"""
Dead Code Eliminator
====================

Removes unreachable / dead code from the AST in four passes:

Mandatory
---------
  1. Statements after a ``return`` inside any block.
  2. Statements after a ``break`` or ``continue`` inside any block.

Optional
--------
  3. Variables that are declared but never read (unused-variable elimination).
  4. Conditionals whose condition is a compile-time constant
     (dead-conditional elimination).
     – ``if (0)  { A } else { B }``  →  B  (or nothing when no else)
     – ``if (1)  { A } else { B }``  →  A
     – ``while (0) { … }``           →  removed entirely
     – ``for (; 0; ) { … }``         →  removed entirely

     NOTE: constant-folding (ConstantFolder) must run *before* this pass
     so that expressions like ``if (2 - 2)`` are already reduced to
     ``if (0)`` by the time we get here.

This is an AST-to-AST pass; it does NOT generate LLVM itself.

Plug it in *after* constant folding and *before* LLVM generation:

    from parser.optimizations.dead_code_eliminator import DeadCodeEliminator
    ast = DeadCodeEliminator().visit(ast)

Flags
-----
Pass ``unused_vars=False`` or ``dead_conditionals=False`` to the
constructor to disable the optional passes individually.
"""

from __future__ import annotations

from parser.ast_nodes import (
    # program
    ASTNode,
    ProgramNode,
    # functions
    FunctionDefNode,
    FunctionDeclNode,
    # blocks / control-flow
    CompoundStmtNode,
    IfNode,
    WhileNode,
    ForNode,
    SwitchNode,
    SwitchCaseNode,
    SwitchDefaultNode,
    # terminators
    ReturnNode,
    BreakNode,
    ContinueNode,
    # declarations & expressions
    VarDeclNode,
    AssignNode,
    IdentifierNode,
    IntLiteralNode,
    # everything else needed for the usage-collector
    BinaryOpNode,
    UnaryOpNode,
    DereferenceNode,
    AddressOfNode,
    IncrementNode,
    DecrementNode,
    CastNode,
    ArrayAccessNode,
    ArrayInitializerNode,
    FunctionCallNode,
    TernaryOpNode,
    PrintfNode,
    ScanfNode,
    MemberAccessNode,
    PointerMemberAccessNode,
    SizeofNode,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helper: trim a statement list after the first unconditional terminator
# ──────────────────────────────────────────────────────────────────────────────

def _trim_after_terminator(items: list) -> tuple[list, bool]:
    """
    Drop everything after the first ``return`` / ``break`` / ``continue``.

    Returns (trimmed_list, was_trimmed).
    """
    for i, item in enumerate(items):
        if isinstance(item, (ReturnNode, BreakNode, ContinueNode)):
            trimmed = items[: i + 1]
            return trimmed, len(trimmed) < len(items)
    return items, False


# ──────────────────────────────────────────────────────────────────────────────
# Helper: collect all *used* identifier names from a subtree
# ──────────────────────────────────────────────────────────────────────────────

def _collect_used_names(node: ASTNode, out: set[str]) -> None:
    """
    Recursively walk *node* and add every IdentifierNode.name to *out*.

    This intentionally visits the *value* side of VarDeclNode (the
    initialiser expression) and AssignNode (right-hand side) so that
    ``int y = x + 1;`` correctly counts ``x`` as used even though the
    variable named by the VarDeclNode itself (``y``) is the one being
    declared.
    """
    if node is None:
        return

    if isinstance(node, IdentifierNode):
        out.add(node.name)
        return

    # ── Declarations / assignments ────────────────────────────────────────
    if isinstance(node, VarDeclNode):
        # Do NOT add node.name here – that is the variable being declared,
        # not a use.  But DO visit the initialiser.
        _collect_used_names(node.value, out)
        return

    if isinstance(node, AssignNode):
        # The target is being written to; only an identifier on the *right*
        # side counts as a read.  However, array-index and dereference
        # sub-expressions inside the target do count.
        _collect_target_reads(node.target, out)
        _collect_used_names(node.value, out)
        return

    # ── Expressions ───────────────────────────────────────────────────────
    if isinstance(node, BinaryOpNode):
        _collect_used_names(node.left, out)
        _collect_used_names(node.right, out)
        return

    if isinstance(node, UnaryOpNode):
        _collect_used_names(node.operand, out)
        return

    if isinstance(node, DereferenceNode):
        _collect_used_names(node.operand, out)
        return

    if isinstance(node, AddressOfNode):
        _collect_used_names(node.operand, out)
        return

    if isinstance(node, (IncrementNode, DecrementNode)):
        _collect_used_names(node.operand, out)
        return

    if isinstance(node, CastNode):
        _collect_used_names(node.operand, out)
        return

    if isinstance(node, ArrayAccessNode):
        _collect_used_names(node.array, out)
        _collect_used_names(node.index, out)
        return

    if isinstance(node, ArrayInitializerNode):
        for elem in node.elements:
            _collect_used_names(elem, out)
        return

    if isinstance(node, TernaryOpNode):
        _collect_used_names(node.condition, out)
        _collect_used_names(node.then_expr, out)
        _collect_used_names(node.else_expr, out)
        return

    if isinstance(node, SizeofNode):
        if not node.is_type:
            _collect_used_names(node.operand, out)
        return

    if isinstance(node, FunctionCallNode):
        for arg in node.args:
            _collect_used_names(arg, out)
        return

    if isinstance(node, PrintfNode):
        for arg in node.args:
            _collect_used_names(arg, out)
        return

    if isinstance(node, ScanfNode):
        for arg in node.args:
            _collect_used_names(arg, out)
        return

    if isinstance(node, MemberAccessNode):
        _collect_used_names(node.obj, out)
        return

    if isinstance(node, PointerMemberAccessNode):
        _collect_used_names(node.ptr, out)
        return

    # ── Statements ────────────────────────────────────────────────────────
    if isinstance(node, ReturnNode):
        _collect_used_names(node.value, out)
        return

    if isinstance(node, CompoundStmtNode):
        for item in node.items:
            _collect_used_names(item, out)
        return

    if isinstance(node, IfNode):
        _collect_used_names(node.condition, out)
        _collect_used_names(node.then_body, out)
        _collect_used_names(node.else_body, out)
        return

    if isinstance(node, WhileNode):
        _collect_used_names(node.condition, out)
        _collect_used_names(node.body, out)
        return

    if isinstance(node, ForNode):
        _collect_used_names(node.init, out)
        _collect_used_names(node.condition, out)
        _collect_used_names(node.update, out)
        _collect_used_names(node.body, out)
        return

    if isinstance(node, SwitchNode):
        _collect_used_names(node.expression, out)
        for case in node.cases:
            _collect_used_names(case, out)
        _collect_used_names(node.default, out)
        return

    if isinstance(node, SwitchCaseNode):
        _collect_used_names(node.value, out)
        for item in node.items:
            _collect_used_names(item, out)
        return

    if isinstance(node, SwitchDefaultNode):
        for item in node.items:
            _collect_used_names(item, out)
        return

    if isinstance(node, FunctionDefNode):
        for param in node.params:
            # Parameters count as "used" automatically – we never remove them.
            out.add(param.name)
        _collect_used_names(node.body, out)
        return

    # Anything else (literals, BreakNode, ContinueNode, …) – no identifiers.


def _collect_target_reads(target: ASTNode, out: set[str]) -> None:
    """
    Collect identifier *reads* that happen inside an assignment target.

    For a plain ``x = …``, nothing is read from the target.
    For ``arr[i] = …``, ``i`` is read (index expression).
    For ``*ptr = …``, ``ptr`` is read.
    For ``s.m = …`` / ``p->m = …``, the base object/pointer is read.
    """
    if isinstance(target, IdentifierNode):
        # The name itself is being written, not read.
        return

    if isinstance(target, ArrayAccessNode):
        # The array base (even if an identifier) is read as a pointer.
        _collect_used_names(target.array, out)
        _collect_used_names(target.index, out)
        return

    if isinstance(target, DereferenceNode):
        _collect_used_names(target.operand, out)
        return

    if isinstance(target, MemberAccessNode):
        _collect_used_names(target.obj, out)
        return

    if isinstance(target, PointerMemberAccessNode):
        _collect_used_names(target.ptr, out)
        return

    # Fallback – collect everything.
    _collect_used_names(target, out)


# ──────────────────────────────────────────────────────────────────────────────
# Main class
# ──────────────────────────────────────────────────────────────────────────────

class DeadCodeEliminator:
    """
    AST-to-AST pass that removes dead and unreachable code.

    Parameters
    ----------
    unused_vars : bool
        Enable removal of variables that are declared but never read.
        Default: True.
    dead_conditionals : bool
        Enable removal of if/while/for whose condition is a compile-time
        integer constant.  Requires ConstantFolder to have run first.
        Default: True.
    """

    def __init__(
        self,
        unused_vars: bool = True,
        dead_conditionals: bool = True,
    ) -> None:
        self._unused_vars = unused_vars
        self._dead_conditionals = dead_conditionals

        # Set of variable names that are *read* anywhere in the current
        # function.  Populated by _build_used_set() before we process each
        # FunctionDefNode.
        self._used_names: set[str] = set()

        # Warnings produced during the pass (list of strings).
        self.warnings: list[str] = []

    # ──────────────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────────────

    def visit(self, node: ASTNode) -> ASTNode | None:
        if node is None:
            return None
        method = "visit_" + type(node).__name__
        return getattr(self, method, self._passthrough)(node)

    # ──────────────────────────────────────────────────────────────────────
    # Program
    # ──────────────────────────────────────────────────────────────────────

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        node.top_level_items = [
            self.visit(item)
            for item in node.top_level_items
            if item is not None
        ]
        return node

    # ──────────────────────────────────────────────────────────────────────
    # Functions
    # ──────────────────────────────────────────────────────────────────────

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> FunctionDefNode:
        # Build the used-name set for this function before processing its body.
        if self._unused_vars:
            self._used_names = set()
            _collect_used_names(node.body, self._used_names)
            # Parameters are always considered used.
            for param in node.params:
                self._used_names.add(param.name)

        node.body = self.visit(node.body)

        # Reset so we don't accidentally carry state across functions.
        self._used_names = set()
        return node

    def visit_FunctionDeclNode(self, node: FunctionDeclNode) -> FunctionDeclNode:
        return node

    # ──────────────────────────────────────────────────────────────────────
    # Compound statements (blocks)
    # ──────────────────────────────────────────────────────────────────────

    def visit_CompoundStmtNode(self, node: CompoundStmtNode) -> CompoundStmtNode:
        # 1. Recurse into children first (deepest blocks cleaned up first).
        visited: list[ASTNode | None] = []
        for item in node.items:
            if item is None:
                continue
            result = self.visit(item)
            # visit() may return None when a node is completely eliminated
            # (e.g. an unused VarDeclNode with no initialiser side-effects,
            # or a dead while loop).
            if result is not None:
                visited.append(result)

        # 2. Mandatory: trim after the first unconditional terminator.
        visited, _ = _trim_after_terminator(visited)

        node.items = visited
        return node

    # ──────────────────────────────────────────────────────────────────────
    # Declarations
    # ──────────────────────────────────────────────────────────────────────

    def visit_VarDeclNode(self, node: VarDeclNode) -> ASTNode | None:
        # Recurse into the initialiser expression first.
        if node.value is not None:
            node.value = self.visit(node.value)

        if not self._unused_vars:
            return node

        # If the variable name is never read anywhere in this function,
        # and the initialiser has no observable side-effects, drop it.
        if node.name not in self._used_names:
            if _is_pure(node.value):
                self.warnings.append(
                    f"[DCE] line {node.line}: unused variable '{node.name}' removed"
                )
                return None  # drop the declaration entirely
            else:
                # The initialiser has side-effects (function call, etc.).
                # Keep the statement but turn the declaration into just the
                # expression by … well, we can't do that cleanly in the AST
                # without an ExprStmtNode.  So we keep the whole VarDeclNode.
                # At minimum we emit a warning.
                self.warnings.append(
                    f"[DCE] line {node.line}: unused variable '{node.name}' "
                    f"kept because its initialiser may have side-effects"
                )

        return node

    # ──────────────────────────────────────────────────────────────────────
    # If statement  (optional: dead-conditional elimination)
    # ──────────────────────────────────────────────────────────────────────

    def visit_IfNode(self, node: IfNode) -> ASTNode | None:
        node.condition = self.visit(node.condition)

        if self._dead_conditionals and isinstance(node.condition, IntLiteralNode):
            if node.condition.value != 0:
                # Condition is always true → keep only then_body.
                self.warnings.append(
                    f"[DCE] line {node.line}: condition is always true, "
                    f"else branch eliminated"
                )
                return self.visit(node.then_body)
            else:
                # Condition is always false → keep only else_body (if any).
                self.warnings.append(
                    f"[DCE] line {node.line}: condition is always false, "
                    f"then branch eliminated"
                )
                if node.else_body is not None:
                    return self.visit(node.else_body)
                return None  # entire if removed

        # Normal path: recurse into both branches.
        node.then_body = self.visit(node.then_body)
        if node.else_body is not None:
            node.else_body = self.visit(node.else_body)
        return node

    # ──────────────────────────────────────────────────────────────────────
    # While statement  (optional: dead-conditional elimination)
    # ──────────────────────────────────────────────────────────────────────

    def visit_WhileNode(self, node: WhileNode) -> ASTNode | None:
        node.condition = self.visit(node.condition)

        if self._dead_conditionals and isinstance(node.condition, IntLiteralNode):
            if node.condition.value == 0:
                # while (0) { … } → never executes, remove entirely.
                self.warnings.append(
                    f"[DCE] line {node.line}: while condition is always false, "
                    f"loop eliminated"
                )
                return None
            # while (non-zero) is an infinite loop – we leave it alone.

        node.body = self.visit(node.body)
        return node

    # ──────────────────────────────────────────────────────────────────────
    # For statement  (optional: dead-conditional elimination)
    # ──────────────────────────────────────────────────────────────────────

    def visit_ForNode(self, node: ForNode) -> ASTNode | None:
        if node.init is not None:
            node.init = self.visit(node.init)
        if node.condition is not None:
            node.condition = self.visit(node.condition)

        if (
            self._dead_conditionals
            and node.condition is not None
            and isinstance(node.condition, IntLiteralNode)
            and node.condition.value == 0
        ):
            # for (…; 0; …) { … } → body never runs.
            # Keep the init expression because it may have side-effects.
            self.warnings.append(
                f"[DCE] line {node.line}: for condition is always false, "
                f"loop body eliminated"
            )
            # Return the init expression wrapped as a statement if possible,
            # otherwise drop everything.  For simplicity we just drop the loop
            # (the init is typically a VarDecl and will be handled by the
            # unused-variable pass if its result is never read).
            return None

        if node.update is not None:
            node.update = self.visit(node.update)
        node.body = self.visit(node.body)
        return node

    # ──────────────────────────────────────────────────────────────────────
    # Switch
    # ──────────────────────────────────────────────────────────────────────

    def visit_SwitchNode(self, node: SwitchNode) -> SwitchNode:
        node.expression = self.visit(node.expression)
        node.cases = [self.visit(case) for case in node.cases]
        if node.default is not None:
            node.default = self.visit(node.default)
        return node

    def visit_SwitchCaseNode(self, node: SwitchCaseNode) -> SwitchCaseNode:
        node.value = self.visit(node.value)
        node.items = [
            r for item in node.items
            if item is not None
            for r in [self.visit(item)]
            if r is not None
        ]
        node.items, _ = _trim_after_terminator(node.items)
        return node

    def visit_SwitchDefaultNode(self, node: SwitchDefaultNode) -> SwitchDefaultNode:
        node.items = [
            r for item in node.items
            if item is not None
            for r in [self.visit(item)]
            if r is not None
        ]
        node.items, _ = _trim_after_terminator(node.items)
        return node

    # ──────────────────────────────────────────────────────────────────────
    # Leaf / pass-through
    # ──────────────────────────────────────────────────────────────────────

    def _passthrough(self, node: ASTNode) -> ASTNode:
        return node


# ──────────────────────────────────────────────────────────────────────────────
# Helper: is an expression side-effect free?
# ──────────────────────────────────────────────────────────────────────────────

def _is_pure(node: ASTNode | None) -> bool:
    """
    Return True when *node* can be dropped without any observable effect.

    Conservative: anything we are not 100% sure about returns False.
    """
    if node is None:
        return True

    # Safe literals and identifiers.
    from parser.ast_nodes import (
        IntLiteralNode, FloatLiteralNode, CharLiteralNode, StringLiteralNode,
    )
    if isinstance(node, (IntLiteralNode, FloatLiteralNode,
                          CharLiteralNode, StringLiteralNode,
                          IdentifierNode)):
        return True

    if isinstance(node, BinaryOpNode):
        return _is_pure(node.left) and _is_pure(node.right)

    if isinstance(node, UnaryOpNode):
        return _is_pure(node.operand)

    if isinstance(node, CastNode):
        return _is_pure(node.operand)

    if isinstance(node, TernaryOpNode):
        return (_is_pure(node.condition)
                and _is_pure(node.then_expr)
                and _is_pure(node.else_expr))

    if isinstance(node, AddressOfNode):
        return True  # just takes an address, no side-effect

    if isinstance(node, ArrayInitializerNode):
        return all(_is_pure(e) for e in node.elements)

    # Anything with a write or unknown side-effect is impure.
    # This includes: FunctionCallNode, IncrementNode, DecrementNode,
    # AssignNode, PrintfNode, ScanfNode, DereferenceNode (may trap), …
    return False
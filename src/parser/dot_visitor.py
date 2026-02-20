from parser.ast_nodes import (
    ASTNode,
    ProgramNode,
    MainFunctionNode,
    VarDeclNode,
    AssignNode,
    IntLiteralNode,
    FloatLiteralNode,
    CharLiteralNode,
    IdentifierNode,
    UnaryOpNode,
    BinaryOpNode,
    DereferenceNode,
    AddressOfNode,
    IncrementNode,
    DecrementNode,
    CastNode,
)


class DotVisitor:
    """
    Walks the AST and produces a Graphviz dot file.

    Usage:
        visitor = DotVisitor()
        dot_string = visitor.visit(ast)

        # Write to file
        with open("ast.dot", "w") as f:
            f.write(dot_string)

    Then on Ubuntu visualise with:
        xdot ast.dot
    Or generate a PNG with:
        dot -Tpng ast.dot -o ast.png
    """

    def __init__(self):
        self._lines = []   # the edges and node definitions we build up
        self._counter = 0  # each node needs a unique ID

    def _new_id(self) -> str:
        """Return a fresh unique node ID."""
        self._counter += 1
        return f"node{self._counter}"

    def _add_node(self, node_id: str, label: str, shape: str = "ellipse"):
        label = label.replace('"', '\\"').replace('\\', '\\\\')
        self._lines.append(f'    {node_id} [label="{label}", shape={shape}];')

    def _add_edge(self, parent_id: str, child_id: str):
        self._lines.append(f'    {parent_id} -> {child_id};')

    # ── Public entry point ────────────────────────────────────

    def visit(self, node: ASTNode) -> str:
        """Visit the root node and return the full dot string."""
        self._lines = []
        self._counter = 0

        self._lines.append('digraph AST {')
        self._lines.append('    node [fontname="Helvetica"];')

        self._visit(node)

        self._lines.append('}')
        return '\n'.join(self._lines)

    # ── Internal dispatch ─────────────────────────────────────

    def _visit(self, node: ASTNode) -> str:
        """Recursively visit a node, return its dot ID."""
        method_name = '_visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: ASTNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, type(node).__name__)
        return node_id

    # ── Program structure ─────────────────────────────────────

    def _visit_ProgramNode(self, node: ProgramNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "Program", shape="rectangle")
        child_id = self._visit(node.main_function)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_MainFunctionNode(self, node: MainFunctionNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "main()", shape="rectangle")
        for stmt in node.statements:
            child_id = self._visit(stmt)
            self._add_edge(node_id, child_id)
        return node_id

    # ── Statements ────────────────────────────────────────────

    def _visit_VarDeclNode(self, node: VarDeclNode) -> str:
        node_id = self._new_id()
        const = "const " if node.is_const else ""
        stars = '*' * node.pointer_depth
        self._add_node(node_id, f"VarDecl\\n{const}{node.type_name}{stars} {node.name}", shape="rectangle")
        if node.value is not None:
            child_id = self._visit(node.value)
            self._add_edge(node_id, child_id)
        return node_id

    def _visit_AssignNode(self, node: AssignNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "=", shape="ellipse")
        target_id = self._visit(node.target)
        value_id  = self._visit(node.value)
        self._add_edge(node_id, target_id)
        self._add_edge(node_id, value_id)
        return node_id

    # ── Literals ──────────────────────────────────────────────

    def _visit_IntLiteralNode(self, node: IntLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, str(node.value), shape="rectangle")
        return node_id

    def _visit_FloatLiteralNode(self, node: FloatLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, str(node.value), shape="rectangle")
        return node_id

    def _visit_CharLiteralNode(self, node: CharLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"'{node.value}'", shape="rectangle")
        return node_id

    def _visit_IdentifierNode(self, node: IdentifierNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.name, shape="ellipse")
        return node_id

    # ── Unary operations ──────────────────────────────────────

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.op, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_DereferenceNode(self, node: DereferenceNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "deref (*)", shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_AddressOfNode(self, node: AddressOfNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "addr (&)", shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_IncrementNode(self, node: IncrementNode) -> str:
        node_id = self._new_id()
        label = "++ (prefix)" if node.prefix else "++ (postfix)"
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_DecrementNode(self, node: DecrementNode) -> str:
        node_id = self._new_id()
        label = "-- (prefix)" if node.prefix else "-- (postfix)"
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_CastNode(self, node: CastNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.pointer_depth
        self._add_node(node_id, f"cast ({node.type_name}{stars})", shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    # ── Binary operations ─────────────────────────────────────

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.op, shape="ellipse")
        left_id  = self._visit(node.left)
        right_id = self._visit(node.right)
        self._add_edge(node_id, left_id)
        self._add_edge(node_id, right_id)
        return node_id
from parser.ast_nodes import (
    ProgramNode, IncludeNode, DefineNode, TypedefNode,
    EnumConstantNode, EnumDeclNode, StructMemberNode, StructDeclNode,
    ParameterNode, FunctionDeclNode, FunctionDefNode, FunctionCallNode,
    CompoundStmtNode, IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    SwitchNode, SwitchCaseNode, SwitchDefaultNode, VarDeclNode, ReturnNode,
    AssignNode, IntLiteralNode, FloatLiteralNode, CharLiteralNode,
    StringLiteralNode, IdentifierNode, ArrayAccessNode, ArrayInitializerNode,
    MemberAccessNode, PointerMemberAccessNode, UnaryOpNode, DereferenceNode,
    AddressOfNode, IncrementNode, DecrementNode, CastNode, SizeofNode,
    BinaryOpNode, TernaryOpNode, PrintfNode, ScanfNode,
)


class DotVisitor:
    """
    Loopt door de AST en maakt een Graphviz dot bestand.

    Gebruik:
        visitor = DotVisitor()
        dot_string = visitor.visit(ast)
        with open("ast.dot", "w") as f:
            f.write(dot_string)

    Visualiseren:  xdot ast.dot
    PNG:           dot -Tpng ast.dot -o ast.png

    Kleurcode:
        Blauw  (#cce5ff) = programma structuur en functies
        Geel   (#fff3cd) = control flow
        Groen  (#d4edda) = literals, struct, enum
        Paars  (#e2d9f3) = typedef
        Cyaan  (#d1ecf1) = enum
        Oranje (#ffeeba) = I/O en functie calls
        Grijs  (#f8f9fa) = blokken { }
        Rood   (#f8d7da) = break/continue
    """

    def __init__(self):
        self._lines = []
        self._counter = 0

    # ── Hulpfuncties ──────────────────────────────────────────

    def _new_id(self) -> str:
        self._counter += 1
        return f"node{self._counter}"

    def _add_node(self, node_id: str, label: str, shape: str = "ellipse",
                  color: str = None):
        label = label.replace('\\', '\\\\').replace('"', '\\"')
        if color:
            self._lines.append(
                f'    {node_id} [label="{label}", shape={shape}, '
                f'style=filled, fillcolor="{color}"];'
            )
        else:
            self._lines.append(
                f'    {node_id} [label="{label}", shape={shape}];'
            )

    def _add_edge(self, parent_id: str, child_id: str, label: str = None):
        if label:
            self._lines.append(
                f'    {parent_id} -> {child_id} [label="{label}"];'
            )
        else:
            self._lines.append(f'    {parent_id} -> {child_id};')

    def _with_comments(self, label: str, node) -> str:
        """Voegt comments toe aan een label als die aanwezig zijn."""
        parts = []
        if hasattr(node, 'leading_comments') and node.leading_comments:
            for c in node.leading_comments:
                parts.append(f"// {c}")
        parts.append(label)
        if hasattr(node, 'inline_comment') and node.inline_comment:
            parts.append(f"// {node.inline_comment}")
        return "\n---\n".join(parts) if len(parts) > 1 else label

    # ── Publiek startpunt ─────────────────────────────────────

    def visit(self, node) -> str:
        self._lines = []
        self._counter = 0
        self._lines.append('digraph AST {')
        self._lines.append('    node [fontname="Helvetica"];')
        self._lines.append('    edge [fontname="Helvetica", fontsize=10];')
        self._visit(node)
        self._lines.append('}')
        return '\n'.join(self._lines)

    # ── Interne dispatch ──────────────────────────────────────

    def _visit(self, node) -> str:
        if node is None:
            node_id = self._new_id()
            self._add_node(node_id, "None", color="#eeeeee")
            return node_id
        method_name = '_visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node) -> str:
        """Fallback — rood zodat je meteen ziet wat er ontbreekt."""
        node_id = self._new_id()
        self._add_node(node_id, type(node).__name__, color="#ffcccc")
        return node_id

    # ── Program ───────────────────────────────────────────────

    def _visit_ProgramNode(self, node: ProgramNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "Program", shape="rectangle", color="#cce5ff")
        for item in node.top_level_items:
            child_id = self._visit(item)
            self._add_edge(node_id, child_id)
        return node_id

    # ── Preprocessor ──────────────────────────────────────────

    def _visit_IncludeNode(self, node: IncludeNode) -> str:
        node_id = self._new_id()
        label = f"#include <{node.header}>" if node.is_system else f'#include "{node.header}"'
        self._add_node(node_id, label, shape="rectangle", color="#fff3cd")
        return node_id

    def _visit_DefineNode(self, node: DefineNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"#define\n{node.name} = {node.value}",
                       shape="rectangle", color="#fff3cd")
        return node_id

    # ── Typedef ───────────────────────────────────────────────

    def _visit_TypedefNode(self, node: TypedefNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.pointer_depth
        self._add_node(node_id,
                       f"typedef\n{node.existing_type}{stars} -> {node.new_name}",
                       shape="rectangle", color="#e2d9f3")
        return node_id

    # ── Enum ──────────────────────────────────────────────────

    def _visit_EnumDeclNode(self, node: EnumDeclNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"enum\n{node.name}",
                       shape="rectangle", color="#d1ecf1")
        for const in node.constants:
            child_id = self._visit(const)
            self._add_edge(node_id, child_id)
        return node_id

    def _visit_EnumConstantNode(self, node: EnumConstantNode) -> str:
        node_id = self._new_id()
        label = f"{node.name} = {node.value}" if node.value is not None else node.name
        self._add_node(node_id, label, shape="ellipse", color="#d1ecf1")
        return node_id

    # ── Struct ────────────────────────────────────────────────

    def _visit_StructDeclNode(self, node: StructDeclNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"struct\n{node.name}",
                       shape="rectangle", color="#d4edda")
        for member in node.members:
            child_id = self._visit(member)
            self._add_edge(node_id, child_id)
        return node_id

    def _visit_StructMemberNode(self, node: StructMemberNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.pointer_depth
        dims = ''.join(f'[{d}]' for d in node.array_dimensions)
        self._add_node(node_id, f"{node.type_name}{stars} {node.name}{dims}",
                       shape="ellipse", color="#d4edda")
        return node_id

    # ── Functions ─────────────────────────────────────────────

    def _visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.return_ptr
        label = self._with_comments(
            f"FunctionDef\n{node.return_type}{stars} {node.name}()", node)
        self._add_node(node_id, label, shape="rectangle", color="#cce5ff")
        for param in node.params:
            child_id = self._visit(param)
            self._add_edge(node_id, child_id, label="param")
        body_id = self._visit(node.body)
        self._add_edge(node_id, body_id, label="body")
        return node_id

    def _visit_FunctionDeclNode(self, node: FunctionDeclNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.return_ptr
        label = f"FunctionDecl\n{node.return_type}{stars} {node.name}()"
        self._add_node(node_id, label, shape="rectangle", color="#cce5ff")
        for param in node.params:
            child_id = self._visit(param)
            self._add_edge(node_id, child_id, label="param")
        return node_id

    def _visit_ParameterNode(self, node: ParameterNode) -> str:
        node_id = self._new_id()
        const = "const " if node.is_const else ""
        stars = '*' * node.pointer_depth
        dims = ''.join(f'[{d}]' for d in node.array_dimensions)
        self._add_node(node_id,
                       f"Param\n{const}{node.type_name}{stars} {node.name}{dims}",
                       shape="ellipse", color="#cce5ff")
        return node_id

    def _visit_FunctionCallNode(self, node: FunctionCallNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"Call\n{node.name}()",
                       shape="ellipse", color="#ffeeba")
        for arg in node.args:
            child_id = self._visit(arg)
            self._add_edge(node_id, child_id)
        return node_id

    # ── Compound statement ────────────────────────────────────

    def _visit_CompoundStmtNode(self, node: CompoundStmtNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "{ }", shape="rectangle", color="#f8f9fa")
        for item in node.items:
            if item is not None:
                child_id = self._visit(item)
                self._add_edge(node_id, child_id)
        return node_id

    # ── Control flow ──────────────────────────────────────────

    def _visit_IfNode(self, node: IfNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, self._with_comments("if", node),
                       shape="diamond", color="#fff3cd")
        self._add_edge(node_id, self._visit(node.condition), label="cond")
        self._add_edge(node_id, self._visit(node.then_body), label="then")
        if node.else_body is not None:
            self._add_edge(node_id, self._visit(node.else_body), label="else")
        return node_id

    def _visit_WhileNode(self, node: WhileNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, self._with_comments("while", node),
                       shape="diamond", color="#fff3cd")
        self._add_edge(node_id, self._visit(node.condition), label="cond")
        self._add_edge(node_id, self._visit(node.body), label="body")
        return node_id

    def _visit_ForNode(self, node: ForNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, self._with_comments("for", node),
                       shape="diamond", color="#fff3cd")
        if node.init is not None:
            self._add_edge(node_id, self._visit(node.init), label="init")
        if node.condition is not None:
            self._add_edge(node_id, self._visit(node.condition), label="cond")
        if node.update is not None:
            self._add_edge(node_id, self._visit(node.update), label="update")
        self._add_edge(node_id, self._visit(node.body), label="body")
        return node_id

    def _visit_BreakNode(self, node: BreakNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "break", shape="rectangle", color="#f8d7da")
        return node_id

    def _visit_ContinueNode(self, node: ContinueNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "continue", shape="rectangle", color="#f8d7da")
        return node_id

    def _visit_SwitchNode(self, node: SwitchNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "switch", shape="diamond", color="#fff3cd")
        self._add_edge(node_id, self._visit(node.expression), label="expr")
        for case in node.cases:
            self._add_edge(node_id, self._visit(case))
        if node.default is not None:
            self._add_edge(node_id, self._visit(node.default))
        return node_id

    def _visit_SwitchCaseNode(self, node: SwitchCaseNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "case", shape="rectangle", color="#fff3cd")
        self._add_edge(node_id, self._visit(node.value), label="value")
        for item in node.items:
            if item is not None:
                self._add_edge(node_id, self._visit(item))
        return node_id

    def _visit_SwitchDefaultNode(self, node: SwitchDefaultNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "default", shape="rectangle", color="#fff3cd")
        for item in node.items:
            if item is not None:
                self._add_edge(node_id, self._visit(item))
        return node_id

    # ── Statements ────────────────────────────────────────────

    def _visit_VarDeclNode(self, node: VarDeclNode) -> str:
        node_id = self._new_id()
        const = "const " if node.is_const else ""
        stars = '*' * node.pointer_depth
        dims = ''.join(f'[{d}]' for d in node.array_dimensions)
        label = self._with_comments(
            f"VarDecl\n{const}{node.type_name}{stars} {node.name}{dims}", node)
        self._add_node(node_id, label, shape="rectangle")
        if node.value is not None:
            self._add_edge(node_id, self._visit(node.value))
        return node_id

    def _visit_ReturnNode(self, node: ReturnNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, self._with_comments("return", node),
                       shape="rectangle")
        if node.value is not None:
            self._add_edge(node_id, self._visit(node.value))
        return node_id

    def _visit_AssignNode(self, node: AssignNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, self._with_comments(node.op, node),
                       shape="ellipse")
        self._add_edge(node_id, self._visit(node.target), label="target")
        self._add_edge(node_id, self._visit(node.value), label="value")
        return node_id

    # ── Literals ──────────────────────────────────────────────

    def _visit_IntLiteralNode(self, node: IntLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, str(node.value), shape="rectangle",
                       color="#d4edda")
        return node_id

    def _visit_FloatLiteralNode(self, node: FloatLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, str(node.value), shape="rectangle",
                       color="#d4edda")
        return node_id

    def _visit_CharLiteralNode(self, node: CharLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"'{node.value}'", shape="rectangle",
                       color="#d4edda")
        return node_id

    def _visit_StringLiteralNode(self, node: StringLiteralNode) -> str:
        node_id = self._new_id()
        display = node.value[:20].replace('\n', '\\n')
        if len(node.value) > 20:
            display += "..."
        self._add_node(node_id, f'"{display}"', shape="rectangle",
                       color="#d4edda")
        return node_id

    # ── Identifiers & access ──────────────────────────────────

    def _visit_IdentifierNode(self, node: IdentifierNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.name, shape="ellipse")
        return node_id

    def _visit_ArrayAccessNode(self, node: ArrayAccessNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "[ ]", shape="ellipse")
        self._add_edge(node_id, self._visit(node.array), label="array")
        self._add_edge(node_id, self._visit(node.index), label="index")
        return node_id

    def _visit_ArrayInitializerNode(self, node: ArrayInitializerNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "{...}", shape="rectangle")
        for elem in node.elements:
            self._add_edge(node_id, self._visit(elem))
        return node_id

    def _visit_MemberAccessNode(self, node: MemberAccessNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f".{node.member}", shape="ellipse",
                       color="#d4edda")
        self._add_edge(node_id, self._visit(node.obj))
        return node_id

    def _visit_PointerMemberAccessNode(self, node: PointerMemberAccessNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, f"->{node.member}", shape="ellipse",
                       color="#d4edda")
        self._add_edge(node_id, self._visit(node.ptr))
        return node_id

    # ── Unary operaties ───────────────────────────────────────

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.op, shape="ellipse")
        self._add_edge(node_id, self._visit(node.operand))
        return node_id

    def _visit_DereferenceNode(self, node: DereferenceNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "deref (*)", shape="ellipse")
        self._add_edge(node_id, self._visit(node.operand))
        return node_id

    def _visit_AddressOfNode(self, node: AddressOfNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "addr (&)", shape="ellipse")
        self._add_edge(node_id, self._visit(node.operand))
        return node_id

    def _visit_IncrementNode(self, node: IncrementNode) -> str:
        node_id = self._new_id()
        label = "++ (prefix)" if node.prefix else "++ (postfix)"
        self._add_node(node_id, label, shape="ellipse")
        self._add_edge(node_id, self._visit(node.operand))
        return node_id

    def _visit_DecrementNode(self, node: DecrementNode) -> str:
        node_id = self._new_id()
        label = "-- (prefix)" if node.prefix else "-- (postfix)"
        self._add_node(node_id, label, shape="ellipse")
        self._add_edge(node_id, self._visit(node.operand))
        return node_id

    def _visit_CastNode(self, node: CastNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.pointer_depth
        self._add_node(node_id, f"cast\n({node.type_name}{stars})",
                       shape="ellipse")
        self._add_edge(node_id, self._visit(node.operand))
        return node_id

    def _visit_SizeofNode(self, node: SizeofNode) -> str:
        node_id = self._new_id()
        if node.is_type:
            stars = '*' * node.pointer_depth
            self._add_node(node_id, f"sizeof\n({node.type_name}{stars})",
                           shape="ellipse")
        else:
            self._add_node(node_id, "sizeof", shape="ellipse")
            self._add_edge(node_id, self._visit(node.operand))
        return node_id

    # ── Binary operaties ──────────────────────────────────────

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.op, shape="ellipse")
        self._add_edge(node_id, self._visit(node.left), label="L")
        self._add_edge(node_id, self._visit(node.right), label="R")
        return node_id

    def _visit_TernaryOpNode(self, node: TernaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "? :", shape="diamond", color="#fff3cd")
        self._add_edge(node_id, self._visit(node.condition), label="cond")
        self._add_edge(node_id, self._visit(node.then_expr), label="then")
        self._add_edge(node_id, self._visit(node.else_expr), label="else")
        return node_id

    # ── I/O ───────────────────────────────────────────────────

    def _visit_PrintfNode(self, node: PrintfNode) -> str:
        node_id = self._new_id()
        display = node.format_string[:20].replace('\n', '\\n')
        if len(node.format_string) > 20:
            display += "..."
        label = self._with_comments(f'printf\n"{display}"', node)
        self._add_node(node_id, label, shape="rectangle", color="#ffeeba")
        for arg in node.args:
            self._add_edge(node_id, self._visit(arg))
        return node_id

    def _visit_ScanfNode(self, node: ScanfNode) -> str:
        node_id = self._new_id()
        display = node.format_string[:20]
        if len(node.format_string) > 20:
            display += "..."
        label = self._with_comments(f'scanf\n"{display}"', node)
        self._add_node(node_id, label, shape="rectangle", color="#ffeeba")
        for arg in node.args:
            self._add_edge(node_id, self._visit(arg))
        return node_id
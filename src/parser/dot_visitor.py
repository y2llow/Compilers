from parser.ast_nodes import (
    ASTNode,
    ProgramNode,
    MainFunctionNode,
    VarDeclNode,
    AssignNode,
    ReturnNode,
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
    ArrayAccessNode,
    ArrayInitializerNode,
    StringLiteralNode,
    IncludeNode,
    PrintfNode,
    ScanfNode,
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
        self._lines = []  # the edges and node definitions we build up
        self._counter = 0  # each node needs a unique ID

    def _new_id(self) -> str:
        """Return a fresh unique node ID."""
        self._counter += 1
        return f"node{self._counter}"

    def _add_node(self, node_id: str, label: str, shape: str = "ellipse"):
        # Escape backslashes first, then quotes
        label = label.replace('\\', '\\\\').replace('"', '\\"')
        self._lines.append(f'    {node_id} [label="{label}", shape={shape}];')

    def _add_edge(self, parent_id: str, child_id: str):
        self._lines.append(f'    {parent_id} -> {child_id};')

    def _format_label_with_comments(self, label: str, ast_node) -> str:
        """Format a label with comments if the AST node has any."""
        parts = []

        # Leading comments
        if ast_node and hasattr(ast_node, 'leading_comments') and ast_node.leading_comments:
            for comment in ast_node.leading_comments:
                parts.append(f"💬 {comment}")

        # Label
        parts.append(label)

        # Inline comment
        if ast_node and hasattr(ast_node, 'inline_comment') and ast_node.inline_comment:
            parts.append(f"💬 {ast_node.inline_comment}")

        # Use real \n — _add_node handles escaping
        return "\n---\n".join(parts) if len(parts) > 1 else label

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

    def _visit_ProgramNode(self, node):
        node_id = self._new_id()
        self._add_node(node_id, "Program", shape="rectangle")
        for inc in node.includes:
            child_id = self._visit(inc)
            self._add_edge(node_id, child_id)
        child_id = self._visit(node.main_function)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_MainFunctionNode(self, node: MainFunctionNode) -> str:
        node_id = self._new_id()
        label = "main()"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")
        for stmt in node.statements:
            child_id = self._visit(stmt)
            self._add_edge(node_id, child_id)
        return node_id

    # ── Statements ────────────────────────────────────────────

    def _visit_VarDeclNode(self, node: VarDeclNode) -> str:
        node_id = self._new_id()
        const = "const " if node.is_const else ""
        stars = '*' * node.pointer_depth
        dims = ''.join([f'[{d}]' for d in node.array_dimensions])
        # Use real \n — _add_node handles escaping
        label = f"VarDecl\n{const}{node.type_name}{stars} {node.name}{dims}"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")

        if node.value is not None:
            child_id = self._visit(node.value)
            self._add_edge(node_id, child_id)
        return node_id

    def _visit_AssignNode(self, node: AssignNode) -> str:
        node_id = self._new_id()
        label = "="
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        target_id = self._visit(node.target)
        value_id = self._visit(node.value)
        self._add_edge(node_id, target_id)
        self._add_edge(node_id, value_id)
        return node_id

    def _visit_ReturnNode(self, node: ReturnNode) -> str:
        node_id = self._new_id()
        label = "return"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")

        if node.value is not None:
            child_id = self._visit(node.value)
            self._add_edge(node_id, child_id)

        return node_id

    # ── Literals ──────────────────────────────────────────────

    def _visit_IntLiteralNode(self, node: IntLiteralNode) -> str:
        node_id = self._new_id()
        label = str(node.value)
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")
        return node_id

    def _visit_FloatLiteralNode(self, node: FloatLiteralNode) -> str:
        node_id = self._new_id()
        label = str(node.value)
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")
        return node_id

    def _visit_CharLiteralNode(self, node: CharLiteralNode) -> str:
        node_id = self._new_id()
        label = f"'{node.value}'"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")
        return node_id

    def _visit_StringLiteralNode(self, node: StringLiteralNode) -> str:
        node_id = self._new_id()
        # Show first 20 chars of string to avoid huge labels
        display = node.value[:20]
        if len(node.value) > 20:
            display += "..."
        label = f'"{display}"'
        self._add_node(node_id, label, shape="rectangle")
        return node_id

    def _visit_IdentifierNode(self, node: IdentifierNode) -> str:
        node_id = self._new_id()
        label = node.name
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        return node_id

    # ── Array operations ──────────────────────────────────────

    def _visit_ArrayAccessNode(self, node: ArrayAccessNode) -> str:
        node_id = self._new_id()
        label = "[]"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")

        array_id = self._visit(node.array)
        index_id = self._visit(node.index)

        self._add_edge(node_id, array_id)
        self._add_edge(node_id, index_id)
        return node_id

    def _visit_ArrayInitializerNode(self, node: ArrayInitializerNode) -> str:
        node_id = self._new_id()
        label = "{...}"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="rectangle")

        for elem in node.elements:
            elem_id = self._visit(elem)
            self._add_edge(node_id, elem_id)

        return node_id

    # ── Unary operations ──────────────────────────────────────

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        node_id = self._new_id()
        label = node.op
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_DereferenceNode(self, node: DereferenceNode) -> str:
        node_id = self._new_id()
        label = "deref (*)"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_AddressOfNode(self, node: AddressOfNode) -> str:
        node_id = self._new_id()
        label = "addr (&)"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_IncrementNode(self, node: IncrementNode) -> str:
        node_id = self._new_id()
        label = "++ (prefix)" if node.prefix else "++ (postfix)"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_DecrementNode(self, node: DecrementNode) -> str:
        node_id = self._new_id()
        label = "-- (prefix)" if node.prefix else "-- (postfix)"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_CastNode(self, node: CastNode) -> str:
        node_id = self._new_id()
        stars = '*' * node.pointer_depth
        label = f"cast ({node.type_name}{stars})"
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)
        return node_id

    # ── Binary operations ─────────────────────────────────────

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        node_id = self._new_id()
        label = node.op
        label = self._format_label_with_comments(label, node)
        self._add_node(node_id, label, shape="ellipse")
        left_id = self._visit(node.left)
        right_id = self._visit(node.right)
        self._add_edge(node_id, left_id)
        self._add_edge(node_id, right_id)
        return node_id

    # ── Include operations ─────────────────────────────────────

    def _visit_IncludeNode(self, node):
        node_id = self._new_id()
        self._add_node(node_id, f"#include <{node.header}>", shape="rectangle")
        return node_id

    def _visit_PrintfNode(self, node):
        node_id = self._new_id()
        display = node.format_string[:20].replace('\n', '\\n')
        if len(node.format_string) > 20:
            display += "..."
        label = f'printf("{display}")'
        self._add_node(node_id, label, shape="rectangle")
        for arg in node.args:
            child_id = self._visit(arg)
            self._add_edge(node_id, child_id)
        return node_id

    def _visit_ScanfNode(self, node):
        node_id = self._new_id()
        display = node.format_string[:20]
        if len(node.format_string) > 20:
            display += "..."
        label = f'scanf("{display}")'
        self._add_node(node_id, label, shape="rectangle")
        for arg in node.args:
            child_id = self._visit(arg)
            self._add_edge(node_id, child_id)
        return node_id
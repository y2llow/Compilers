from parser.ast_nodes import (
    ASTNode,
    ProgramNode,
    IntLiteralNode,
    UnaryOpNode,
    BinaryOpNode,
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
        # Escape special graphviz characters in the label
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

    # ── Per-node visitors ─────────────────────────────────────

    def _visit_ProgramNode(self, node: ProgramNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, "Program", shape="rectangle")

        for expr in node.expressions:
            child_id = self._visit(expr)
            self._add_edge(node_id, child_id)

        return node_id

    def _visit_IntLiteralNode(self, node: IntLiteralNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, str(node.value), shape="rectangle")
        return node_id

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.op, shape="ellipse")

        child_id = self._visit(node.operand)
        self._add_edge(node_id, child_id)

        return node_id

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        node_id = self._new_id()
        self._add_node(node_id, node.op, shape="ellipse")

        left_id  = self._visit(node.left)
        right_id = self._visit(node.right)
        self._add_edge(node_id, left_id)
        self._add_edge(node_id, right_id)

        return node_id
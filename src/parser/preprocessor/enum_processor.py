from parser.ast_nodes import *


class EnumProcessor:
    """
    Vervangt enum constants door IntLiteralNode.

    Voorbeeld:
        enum Color { RED, BLUE };
        int x = BLUE;

    wordt:
        int x = 1;
    """

    def __init__(self):
        self.enum_values = {}

    def process(self, node: ProgramNode) -> ProgramNode:
        self._collect_enums(node)
        return self.visit(node)

    def _collect_enums(self, node: ProgramNode):
        for item in node.top_level_items:
            if isinstance(item, EnumDeclNode):
                current_value = 0

                for const in item.constants:
                    if const.value is not None:
                        current_value = const.value

                    self.enum_values[const.name] = current_value
                    current_value += 1

    def visit(self, node):
        if node is None:
            return None

        method = "visit_" + type(node).__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return node

    def visit_ProgramNode(self, node):
        node.top_level_items = [
            self.visit(item)
            for item in node.top_level_items
            if item is not None
        ]
        return node

    def visit_FunctionDefNode(self, node):
        node.body = self.visit(node.body)
        return node

    def visit_FunctionDeclNode(self, node):
        return node

    def visit_CompoundStmtNode(self, node):
        node.items = [
            self.visit(item)
            for item in node.items
            if item is not None
        ]
        return node

    def visit_VarDeclNode(self, node):
        if node.value is not None:
            node.value = self.visit(node.value)
        return node

    def visit_AssignNode(self, node):
        node.target = self.visit(node.target)
        node.value = self.visit(node.value)
        return node

    def visit_ReturnNode(self, node):
        if node.value is not None:
            node.value = self.visit(node.value)
        return node

    def visit_IfNode(self, node):
        node.condition = self.visit(node.condition)
        node.then_body = self.visit(node.then_body)
        if node.else_body is not None:
            node.else_body = self.visit(node.else_body)
        return node

    def visit_WhileNode(self, node):
        node.condition = self.visit(node.condition)
        node.body = self.visit(node.body)
        return node

    def visit_ForNode(self, node):
        if node.init is not None:
            node.init = self.visit(node.init)
        if node.condition is not None:
            node.condition = self.visit(node.condition)
        if node.update is not None:
            node.update = self.visit(node.update)
        node.body = self.visit(node.body)
        return node

    def visit_SwitchNode(self, node):
        node.expression = self.visit(node.expression)
        node.cases = [self.visit(case) for case in node.cases]
        if node.default is not None:
            node.default = self.visit(node.default)
        return node

    def visit_SwitchCaseNode(self, node):
        node.value = self.visit(node.value)
        node.items = [
            self.visit(item)
            for item in node.items
            if item is not None
        ]
        return node

    def visit_SwitchDefaultNode(self, node):
        node.items = [
            self.visit(item)
            for item in node.items
            if item is not None
        ]
        return node

    def visit_IdentifierNode(self, node):
        if node.name in self.enum_values:
            replacement = IntLiteralNode(self.enum_values[node.name])
            replacement.line = node.line
            replacement.column = node.column
            replacement.source_line = node.source_line
            replacement.leading_comments = getattr(node, "leading_comments", [])
            replacement.inline_comment = getattr(node, "inline_comment", None)
            return replacement

        return node

    def visit_BinaryOpNode(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return node

    def visit_UnaryOpNode(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_DereferenceNode(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_AddressOfNode(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_IncrementNode(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_DecrementNode(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_CastNode(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_ArrayAccessNode(self, node):
        node.array = self.visit(node.array)
        node.index = self.visit(node.index)
        return node

    def visit_ArrayInitializerNode(self, node):
        node.elements = [self.visit(elem) for elem in node.elements]
        return node

    def visit_TernaryOpNode(self, node):
        node.condition = self.visit(node.condition)
        node.then_expr = self.visit(node.then_expr)
        node.else_expr = self.visit(node.else_expr)
        return node

    def visit_FunctionCallNode(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_PrintfNode(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_ScanfNode(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_MemberAccessNode(self, node):
        node.obj = self.visit(node.obj)
        return node

    def visit_PointerMemberAccessNode(self, node):
        node.ptr = self.visit(node.ptr)
        return node

    def visit_SizeofNode(self, node):
        if not node.is_type and node.operand is not None:
            node.operand = self.visit(node.operand)
        return node
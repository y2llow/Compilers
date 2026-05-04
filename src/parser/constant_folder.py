from parser.ast_nodes import (
    ASTNode,
    ProgramNode,
    FunctionDefNode,
    FunctionDeclNode,
    CompoundStmtNode,
    IfNode,
    WhileNode,
    ForNode,
    BreakNode,
    ContinueNode,
    SwitchNode,
    SwitchCaseNode,
    SwitchDefaultNode,
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
    PrintfNode,
    ScanfNode,
    FunctionCallNode,
    TernaryOpNode,
    SizeofNode,
)


class ConstantFolder:
    """
    Constant folding + simpele constant propagation.

    Voorbeeld:
        int x = 2 + 3 * 4;

    wordt:
        int x = 14;

    Deze visitor is aangepast aan de nieuwe AST-structuur:
        ProgramNode.top_level_items
        FunctionDefNode.body
        CompoundStmtNode.items
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._known: dict[str, ASTNode] = {}

    # ------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------

    def visit(self, node: ASTNode) -> ASTNode:
        if node is None:
            return None

        if not self.enabled:
            return node

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        return node

    # ------------------------------------------------------------
    # Program / functions / blocks
    # ------------------------------------------------------------

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        node.top_level_items = [
            self.visit(item)
            for item in node.top_level_items
            if item is not None
        ]
        return node

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> FunctionDefNode:
        # Elke functie heeft zijn eigen context.
        old_known = self._known.copy()
        self._known.clear()

        node.body = self.visit(node.body)

        self._known = old_known
        return node

    def visit_FunctionDeclNode(self, node: FunctionDeclNode) -> FunctionDeclNode:
        return node

    def visit_CompoundStmtNode(self, node: CompoundStmtNode) -> CompoundStmtNode:
        node.items = [
            self.visit(item)
            for item in node.items
            if item is not None
        ]
        return node

    # ------------------------------------------------------------
    # Control flow
    # ------------------------------------------------------------

    def visit_IfNode(self, node: IfNode) -> IfNode:
        node.condition = self.visit(node.condition)

        # Branches zijn onzeker: na een if weten we niet zeker welke branch uitgevoerd werd.
        old_known = self._known.copy()

        self._known = old_known.copy()
        node.then_body = self.visit(node.then_body)

        self._known = old_known.copy()
        if node.else_body is not None:
            node.else_body = self.visit(node.else_body)

        self._known = old_known
        return node

    def visit_WhileNode(self, node: WhileNode) -> WhileNode:
        node.condition = self.visit(node.condition)

        # Een loop kan 0, 1 of veel keer uitvoeren.
        # Daarom laten we bekende waarden niet uit de loop lekken.
        old_known = self._known.copy()
        node.body = self.visit(node.body)
        self._known = old_known

        return node

    def visit_ForNode(self, node: ForNode) -> ForNode:
        old_known = self._known.copy()

        if node.init is not None:
            node.init = self.visit(node.init)

        if node.condition is not None:
            node.condition = self.visit(node.condition)

        if node.update is not None:
            node.update = self.visit(node.update)

        node.body = self.visit(node.body)

        self._known = old_known
        return node

    def visit_BreakNode(self, node: BreakNode) -> BreakNode:
        return node

    def visit_ContinueNode(self, node: ContinueNode) -> ContinueNode:
        return node

    def visit_SwitchNode(self, node: SwitchNode) -> SwitchNode:
        node.expression = self.visit(node.expression)

        old_known = self._known.copy()

        node.cases = [self.visit(case) for case in node.cases]
        if node.default is not None:
            node.default = self.visit(node.default)

        self._known = old_known
        return node

    def visit_SwitchCaseNode(self, node: SwitchCaseNode) -> SwitchCaseNode:
        node.value = self.visit(node.value)
        node.items = [
            self.visit(item)
            for item in node.items
            if item is not None
        ]
        return node

    def visit_SwitchDefaultNode(self, node: SwitchDefaultNode) -> SwitchDefaultNode:
        node.items = [
            self.visit(item)
            for item in node.items
            if item is not None
        ]
        return node

    # ------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------

    def visit_VarDeclNode(self, node: VarDeclNode) -> VarDeclNode:
        if node.value is not None:
            node.value = self.visit(node.value)

            # Simpele casts bij initialisatie.
            if node.type_name == 'int' and node.pointer_depth == 0:
                if isinstance(node.value, FloatLiteralNode):
                    node.value = IntLiteralNode(int(node.value.value))
                elif isinstance(node.value, CharLiteralNode):
                    node.value = IntLiteralNode(ord(node.value.value[0]))

            elif node.type_name == 'char' and node.pointer_depth == 0:
                if isinstance(node.value, FloatLiteralNode):
                    node.value = IntLiteralNode(int(node.value.value))

            elif node.type_name == 'float' and node.pointer_depth == 0:
                if isinstance(node.value, IntLiteralNode):
                    node.value = FloatLiteralNode(float(node.value.value))

            if isinstance(node.value, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                self._known[node.name] = node.value
            else:
                self._known.pop(node.name, None)
        else:
            self._known.pop(node.name, None)

        return node

    def visit_AssignNode(self, node: AssignNode) -> AssignNode:
        node.value = self.visit(node.value)

        if isinstance(node.target, IdentifierNode):
            name = node.target.name

            # Bij compound assignments zoals x += 2 is het veiliger
            # om x niet zomaar te vervangen alsof het een gewone '=' was.
            if node.op != '=':
                self._known.pop(name, None)
                return node

            if isinstance(node.value, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                self._known[name] = node.value
            else:
                self._known.pop(name, None)

        elif isinstance(node.target, DereferenceNode):
            # *ptr = value kan indirect iets wijzigen.
            self._known.clear()

        elif isinstance(node.target, ArrayAccessNode):
            # arr[i] = value kan array-inhoud wijzigen.
            self._known.clear()

        return node

    def visit_ReturnNode(self, node: ReturnNode) -> ReturnNode:
        if node.value is not None:
            node.value = self.visit(node.value)
        return node

    # ------------------------------------------------------------
    # Constant propagation
    # ------------------------------------------------------------

    def visit_IdentifierNode(self, node: IdentifierNode) -> ASTNode:
        return node

    # ------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> ASTNode:
        node.operand = self.visit(node.operand)

        if isinstance(node.operand, IntLiteralNode):
            return IntLiteralNode(self._eval_unary(node.op, node.operand.value))

        if isinstance(node.operand, FloatLiteralNode):
            if node.op == '-':
                return FloatLiteralNode(-node.operand.value)
            if node.op == '+':
                return FloatLiteralNode(node.operand.value)

        return node

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> ASTNode:
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        escape_map = {
            '\\n': 10,
            '\\t': 9,
            '\\r': 13,
            '\\0': 0,
            '\\\\': 92,
            "\\'": 39,
            '\\"': 34,
        }

        def get_value(n):
            if isinstance(n, IntLiteralNode):
                return n.value, 'int'
            if isinstance(n, FloatLiteralNode):
                return n.value, 'float'
            if isinstance(n, CharLiteralNode):
                v = n.value
                char_val = escape_map.get(v, ord(v[0]) if v else 0)
                return char_val, 'char'
            return None, None

        left_val, left_type = get_value(node.left)
        right_val, right_type = get_value(node.right)

        if left_val is None or right_val is None:
            return node

        # Niet folden bij deling door nul.
        if node.op in ('/', '%') and right_val == 0:
            return node

        # Niet folden bij bitwise/shift op floats.
        if node.op in ('<<', '>>', '&', '|', '^') and (
            left_type == 'float' or right_type == 'float'
        ):
            return node

        result = self._eval_binary(node.op, left_val, right_val)

        if node.op in ('&&', '||', '==', '!=', '<', '>', '<=', '>='):
            return IntLiteralNode(int(result))

        if left_type == 'float' or right_type == 'float':
            return FloatLiteralNode(float(result))

        return IntLiteralNode(int(result))

    def visit_TernaryOpNode(self, node: TernaryOpNode) -> ASTNode:
        node.condition = self.visit(node.condition)

        # Alleen branch kiezen als conditie compile-time bekend is.
        if isinstance(node.condition, IntLiteralNode):
            if node.condition.value != 0:
                return self.visit(node.then_expr)
            return self.visit(node.else_expr)

        old_known = self._known.copy()

        self._known = old_known.copy()
        node.then_expr = self.visit(node.then_expr)

        self._known = old_known.copy()
        node.else_expr = self.visit(node.else_expr)

        self._known = old_known
        return node

    def visit_DereferenceNode(self, node: DereferenceNode) -> DereferenceNode:
        # Niet folden: *ptr moet zijn operand behouden.
        return node

    def visit_AddressOfNode(self, node: AddressOfNode) -> AddressOfNode:
        # Niet folden: &x moet x behouden, niet de waarde van x.
        return node

    def visit_IncrementNode(self, node: IncrementNode) -> IncrementNode:
        if isinstance(node.operand, IdentifierNode):
            self._known.pop(node.operand.name, None)
        return node

    def visit_DecrementNode(self, node: DecrementNode) -> DecrementNode:
        if isinstance(node.operand, IdentifierNode):
            self._known.pop(node.operand.name, None)
        return node

    def visit_CastNode(self, node: CastNode) -> CastNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> ArrayAccessNode:
        # Array name zelf niet vervangen door een literal.
        node.index = self.visit(node.index)
        return node

    def visit_ArrayInitializerNode(self, node: ArrayInitializerNode) -> ArrayInitializerNode:
        node.elements = [self.visit(elem) for elem in node.elements]
        return node

    def visit_FunctionCallNode(self, node: FunctionCallNode) -> FunctionCallNode:
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_SizeofNode(self, node: SizeofNode) -> SizeofNode:
        if not node.is_type and node.operand is not None:
            node.operand = self.visit(node.operand)
        return node

    def visit_PrintfNode(self, node: PrintfNode) -> PrintfNode:
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_ScanfNode(self, node: ScanfNode) -> ScanfNode:
        # Bij scanf moeten arguments meestal address-of expressions blijven.
        return node

    # ------------------------------------------------------------
    # Evaluation helpers
    # ------------------------------------------------------------

    def _eval_unary(self, op: str, val: int) -> int:
        match op:
            case '+':
                return +val
            case '-':
                return -val
            case '!':
                return int(not val)
            case '~':
                return ~val
            case _:
                raise ValueError(f"Unknown unary operator: {op}")

    def _eval_binary(self, op: str, left, right):
        match op:
            case '+':
                return left + right
            case '-':
                return left - right
            case '*':
                return left * right
            case '/':
                return int(left / right)
            case '%':
                return left % right
            case '==':
                return int(left == right)
            case '!=':
                return int(left != right)
            case '<':
                return int(left < right)
            case '>':
                return int(left > right)
            case '<=':
                return int(left <= right)
            case '>=':
                return int(left >= right)
            case '&&':
                return int(bool(left) and bool(right))
            case '||':
                return int(bool(left) or bool(right))
            case '&':
                return int(left) & int(right)
            case '|':
                return int(left) | int(right)
            case '^':
                return int(left) ^ int(right)
            case '<<':
                if right < 0:
                    return left
                return int(left) << int(right)
            case '>>':
                if right < 0:
                    return left
                return int(left) >> int(right)
            case _:
                raise ValueError(f"Unknown binary operator: {op}")

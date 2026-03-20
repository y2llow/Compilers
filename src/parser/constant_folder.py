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
    IncludeNode,
    PrintfNode,
    ScanfNode,
)


class ConstantFolder:
    """
    Walks our AST and:
      1. Folds constant expressions at compile time (constant folding)
      2. Replaces identifiers with their known value (constant propagation)

    Rules:
      - BinaryOpNode where both children are literals  → replaced with literal
      - UnaryOpNode  where the child is a literal      → replaced with literal
      - IdentifierNode where value is known            → replaced with literal
      - const variables always have a known value
      - non-const variables have a known value only until they are reassigned

    Usage:
        folder = ConstantFolder()
        optimised_ast = folder.visit(ast)

    To disable folding, pass enabled=False to the constructor.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        # Maps variable name -> literal node for all variables whose value is known
        self._known: dict[str, ASTNode] = {}

    # ── Dispatch ──────────────────────────────────────────────

    def visit(self, node: ASTNode) -> ASTNode:
        if not self.enabled:
            return node

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        """Fallback: return the node unchanged."""
        return node

    # ── Program structure ─────────────────────────────────────

    def visit_ProgramNode(self, node):
        # includes have no foldable expressions — leave them alone
        node.main_function = self.visit(node.main_function)
        return node

    def visit_MainFunctionNode(self, node: MainFunctionNode) -> MainFunctionNode:
        node.statements = [self.visit(stmt) for stmt in node.statements]
        return node

    # ── Statements ────────────────────────────────────────────

    def visit_VarDeclNode(self, node: VarDeclNode) -> VarDeclNode:
        if node.value is not None:
            node.value = self.visit(node.value)

            if node.type_name == 'int' and node.pointer_depth == 0:
                if isinstance(node.value, FloatLiteralNode):
                    node.value = IntLiteralNode(int(node.value.value))
                elif isinstance(node.value, CharLiteralNode):
                    node.value = IntLiteralNode(ord(node.value.value[0]))
            elif node.type_name == 'char' and node.pointer_depth == 0:
                if isinstance(node.value, FloatLiteralNode):
                    node.value = IntLiteralNode(int(node.value.value))
                elif isinstance(node.value, IntLiteralNode):
                    pass  # blijft IntLiteralNode
            elif node.type_name == 'float' and node.pointer_depth == 0:
                if isinstance(node.value, IntLiteralNode):
                    node.value = FloatLiteralNode(float(node.value.value))

            # If the result is a literal, remember it for propagation
            if isinstance(node.value, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                self._known[node.name] = node.value
            else:
                self._known.pop(node.name, None)
        else:
            self._known.pop(node.name, None)

        return node

    def visit_AssignNode(self, node: AssignNode) -> AssignNode:
        # Fold the right hand side first
        node.value = self.visit(node.value)

        # Update known values
        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            if isinstance(node.value, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                # Value is now known
                self._known[name] = node.value
            else:
                # Value is no longer known (e.g. x = x + y)
                self._known.pop(name, None)

        elif isinstance(node.target, DereferenceNode):
            # NIEUW: *ptr = value — we weten niet welke variabele verandert
            # Gooi ALLE bekende waarden weg die via een pointer bereikbaar zijn
            self._known.clear()

        return node

    def visit_ReturnNode(self, node: ReturnNode) -> ReturnNode:
        """Fold return expression"""
        if node.value is not None:
            node.value = self.visit(node.value)
        return node

    # ── Constant propagation ──────────────────────────────────

    def visit_IdentifierNode(self, node: IdentifierNode) -> ASTNode:
        # If we know the value of this variable, replace it with the literal
        if node.name in self._known:
            return self._known[node.name]
        return node

    # ── Expressions ───────────────────────────────────────────

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> ASTNode:
        node.operand = self.visit(node.operand)

        if isinstance(node.operand, IntLiteralNode):
            return IntLiteralNode(self._eval_unary(node.op, node.operand.value))

        elif isinstance(node.operand, FloatLiteralNode):
            if node.op == '-':
                return FloatLiteralNode(-node.operand.value)
            elif node.op == '+':
                return FloatLiteralNode(node.operand.value)

        return node

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> ASTNode:
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        escape_map = {
            '\\n': 10, '\\t': 9, '\\r': 13,
            '\\0': 0, '\\\\': 92, "\\'": 39, '\\"': 34,
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

        if left_val is not None and right_val is not None:
            # Niet folden bij deling door nul
            if node.op in ('/', '%') and right_val == 0:
                return node
            # Niet folden bij bitwise/shift op floats
            if node.op in ('<<', '>>', '&', '|', '^') and (left_type == 'float' or right_type == 'float'):
                return node
            result = self._eval_binary(node.op, left_val, right_val)
            if node.op in ('&&', '||', '==', '!=', '<', '>', '<=', '>='):
                return IntLiteralNode(int(result))
            if left_type == 'float' or right_type == 'float':
                return FloatLiteralNode(float(result))
            return IntLiteralNode(int(result))

        return node

    def visit_DereferenceNode(self, node: DereferenceNode) -> DereferenceNode:
        # Niet folden! De operand moet een variabele blijven,
        # want *x = dereference van x, niet *54
        return node

    def visit_AddressOfNode(self, node: AddressOfNode) -> AddressOfNode:
        return node

    def visit_IncrementNode(self, node: IncrementNode) -> IncrementNode:
        # Niet folden — operand moet variabele blijven
        if isinstance(node.operand, IdentifierNode):
            self._known.pop(node.operand.name, None)
        return node

    def visit_DecrementNode(self, node: DecrementNode) -> DecrementNode:
        # Niet folden — operand moet variabele blijven
        if isinstance(node.operand, IdentifierNode):
            self._known.pop(node.operand.name, None)
        return node

    def visit_CastNode(self, node: CastNode) -> CastNode:
        node.operand = self.visit(node.operand)
        return node

    # ── Evaluation helpers ────────────────────────────────────

    def _eval_unary(self, op: str, val: int) -> int:
        match op:
            case '+':  return +val
            case '-':  return -val
            case '!':  return int(not val)
            case '~':  return ~val
            case _:    raise ValueError(f"Unknown unary operator: {op}")

    def _eval_binary(self, op: str, left: int, right: int) -> int:
        match op:
            case '+':  return left + right
            case '-':  return left - right
            case '*':  return left * right
            case '/':  return int(left / right)
            case '%':  return left % right
            case '==': return int(left == right)
            case '!=': return int(left != right)
            case '<':  return int(left <  right)
            case '>':  return int(left >  right)
            case '<=': return int(left <= right)
            case '>=': return int(left >= right)
            case '&&': return int(bool(left) and bool(right))
            case '||': return int(bool(left) or  bool(right))
            case '&':  return left &  right
            case '|':  return left |  right
            case '^':  return left ^  right
            case '<<':
                if right < 0:
                    return left  # niet folden bij negatieve shift
                return left << right
            case '>>':
                if right < 0:
                    return left  # niet folden bij negatieve shift
                return left >> right

    # ── Evaluation helpers ────────────────────────────────────

    def visit_PrintfNode(self, node):
        node.args = [self.visit(a) for a in node.args]
        return node

    def visit_ScanfNode(self, node):
        node.args = [self.visit(a) for a in node.args]
        return node
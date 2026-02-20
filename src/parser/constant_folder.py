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

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        node.main_function = self.visit(node.main_function)
        return node

    def visit_MainFunctionNode(self, node: MainFunctionNode) -> MainFunctionNode:
        node.statements = [self.visit(stmt) for stmt in node.statements]
        return node

    # ── Statements ────────────────────────────────────────────

    def visit_VarDeclNode(self, node: VarDeclNode) -> VarDeclNode:
        # First fold the initializer expression
        if node.value is not None:
            node.value = self.visit(node.value)

            # If the result is a literal, remember it for propagation
            if isinstance(node.value, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                self._known[node.name] = node.value
            else:
                # Value is not fully known (e.g. depends on another variable)
                self._known.pop(node.name, None)
        else:
            # No initializer — value is unknown
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

        return node

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> ASTNode:
        node.left  = self.visit(node.left)
        node.right = self.visit(node.right)

        if isinstance(node.left, IntLiteralNode) and isinstance(node.right, IntLiteralNode):
            result = self._eval_binary(node.op, node.left.value, node.right.value)
            return IntLiteralNode(result)

        return node

    def visit_DereferenceNode(self, node: DereferenceNode) -> DereferenceNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_AddressOfNode(self, node: AddressOfNode) -> AddressOfNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_IncrementNode(self, node: IncrementNode) -> IncrementNode:
        node.operand = self.visit(node.operand)
        # After increment the value of the variable is no longer known
        if isinstance(node.operand, IdentifierNode):
            self._known.pop(node.operand.name, None)
        return node

    def visit_DecrementNode(self, node: DecrementNode) -> DecrementNode:
        node.operand = self.visit(node.operand)
        # After decrement the value of the variable is no longer known
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
            case '<<': return left << right
            case '>>': return left >> right
            case _:    raise ValueError(f"Unknown binary operator: {op}")
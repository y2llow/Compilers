from parser.ast_nodes import (
    ASTNode,
    ProgramNode,
    IntLiteralNode,
    UnaryOpNode,
    BinaryOpNode,
)


class ConstantFolder:
    """
    Walks our AST and folds constant expressions at compile time.

    Rules:
      - BinaryOpNode where both children are IntLiteralNode  → replaced with IntLiteralNode
      - UnaryOpNode  where the child is an IntLiteralNode    → replaced with IntLiteralNode
      - Everything else is left untouched

    Usage:
        folder = ConstantFolder()
        optimised_ast = folder.visit(ast)

    To disable folding (e.g. for testing), just don't call this pass at all,
    or pass enabled=False to the constructor.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    # ── Dispatch ─────────────────────────────────────────────

    def visit(self, node: ASTNode) -> ASTNode:
        if not self.enabled:
            return node                         # folding is turned off, pass through

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        """Fallback: return the node unchanged."""
        return node

    # ── Visitors ─────────────────────────────────────────────

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        node.expressions = [self.visit(expr) for expr in node.expressions]
        return node

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> ASTNode:
        # First recurse so inner expressions are folded before we look at this node
        node.operand = self.visit(node.operand)

        if isinstance(node.operand, IntLiteralNode):
            return IntLiteralNode(self._eval_unary(node.op, node.operand.value))

        return node  # can't fold (operand isn't a literal)

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> ASTNode:
        # Recurse first
        node.left  = self.visit(node.left)
        node.right = self.visit(node.right)

        if isinstance(node.left, IntLiteralNode) and isinstance(node.right, IntLiteralNode):
            result = self._eval_binary(node.op, node.left.value, node.right.value)
            return IntLiteralNode(result)

        return node  # can't fold

    # ── Evaluation helpers ───────────────────────────────────

    def _eval_unary(self, op: str, val: int) -> int:
        match op:
            case '+':  return +val
            case '-':  return -val
            case '!':  return int(not val)
            case '~':  return ~val
            case _:    raise ValueError(f"Unknown unary operator: {op}")

    def _eval_binary(self, op: str, left: int, right: int) -> int:
        match op:
            # Arithmetic
            case '+':  return left + right
            case '-':  return left - right
            case '*':  return left * right
            case '/':  return int(left / right)   # integer division, C-style (truncates toward zero)
            case '%':  return left % right
            # Comparison  (C returns 0 or 1)
            case '==': return int(left == right)
            case '!=': return int(left != right)
            case '<':  return int(left <  right)
            case '>':  return int(left >  right)
            case '<=': return int(left <= right)
            case '>=': return int(left >= right)
            # Logical
            case '&&': return int(bool(left) and bool(right))
            case '||': return int(bool(left) or  bool(right))
            # Bitwise
            case '&':  return left &  right
            case '|':  return left |  right
            case '^':  return left ^  right
            case '<<': return left << right
            case '>>': return left >> right
            case _:    raise ValueError(f"Unknown binary operator: {op}")
# ============================================================
# AST Node classes for the expression compiler
# ============================================================
# Design notes:
#   - All nodes inherit from ASTNode (easy isinstance checks later)
#   - No ANTLR types are used here — the AST is fully independent
#   - Adding new node types = just add a new class below
# ============================================================


class ASTNode:
    """Base class for all AST nodes."""
    pass


# ── Program ──────────────────────────────────────────────────

class ProgramNode(ASTNode):
    """Root node: holds a list of top-level expressions (one per semicolon)."""
    def __init__(self, expressions: list):
        self.expressions = expressions  # [ASTNode, ...]

    def __repr__(self):
        return f"Program({self.expressions})"


# ── Literals ─────────────────────────────────────────────────

class IntLiteralNode(ASTNode):
    """An integer literal, e.g. 42."""
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Int({self.value})"


# Easy to add later:
#   class FloatLiteralNode(ASTNode): ...
#   class CharLiteralNode(ASTNode):  ...


# ── Unary operations ─────────────────────────────────────────

class UnaryOpNode(ASTNode):
    """
    A unary operation.
    op    : string, one of: '+', '-', '!', '~'
    operand: ASTNode
    """
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


# ── Binary operations ─────────────────────────────────────────

class BinaryOpNode(ASTNode):
    """
    A binary operation.
    op   : string, e.g. '+', '-', '*', '/', '%',
                        '&&', '||', '==', '!=',
                        '<', '>', '<=', '>=',
                        '<<', '>>', '&', '|', '^'
    left : ASTNode
    right: ASTNode
    """
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"
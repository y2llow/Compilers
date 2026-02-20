from src.antlr_files.grammers.Operation_grammer.Operations_grammerVisitor import Operations_grammerVisitor
from src.parser.ast_nodes import (
    ProgramNode,
    IntLiteralNode,
    UnaryOpNode,
    BinaryOpNode,
)


class ASTBuilder(Operations_grammerVisitor):
    """
    Walks the ANTLR Concrete Syntax Tree (CST) and builds our own AST.

    One visit method per labelled alternative in the grammar (the # labels).
    Each method returns an ASTNode — no ANTLR objects leak past this class.
    """

    # ── Top level ────────────────────────────────────────────

    def visitTranslation_unit(self, ctx):
        # Each child pair is: expression ';'
        # ctx.expression() returns the list of all expression sub-trees
        expressions = [self.visit(expr) for expr in ctx.expression()]
        return ProgramNode(expressions)

    # ── Literals ─────────────────────────────────────────────

    def visitIntLiteral(self, ctx):
        return IntLiteralNode(int(ctx.INTEGER().getText()))

    def visitLiteralExpr(self, ctx):
        # expression : literal  ->  just pass through to visitIntLiteral etc.
        return self.visit(ctx.literal())

    # ── Parentheses (just unwrap them — they don't appear in the AST) ────

    def visitParens(self, ctx):
        return self.visit(ctx.expression())

    # ── Unary operators ──────────────────────────────────────

    def visitUnary(self, ctx):
        op = ctx.getChild(0).getText()        # '+' or '-'
        operand = self.visit(ctx.expression())
        return UnaryOpNode(op, operand)

    def visitLogicalNot(self, ctx):
        operand = self.visit(ctx.expression())
        return UnaryOpNode('!', operand)

    def visitBitwiseNot(self, ctx):
        operand = self.visit(ctx.expression())
        return UnaryOpNode('~', operand)

    # ── Binary operators ─────────────────────────────────────
    # All binary rules have the same shape:
    #   expression OP expression
    # so we can use a small helper.

    def _binary(self, ctx):
        """Build a BinaryOpNode from any binary expression context."""
        left  = self.visit(ctx.expression(0))
        op    = ctx.getChild(1).getText()   # the operator token is always child index 1
        right = self.visit(ctx.expression(1))
        return BinaryOpNode(op, left, right)

    def visitLogicalOr(self, ctx):   return self._binary(ctx)
    def visitLogicalAnd(self, ctx):  return self._binary(ctx)
    def visitBitwiseOr(self, ctx):   return self._binary(ctx)
    def visitBitwiseXor(self, ctx):  return self._binary(ctx)
    def visitBitwiseAnd(self, ctx):  return self._binary(ctx)
    def visitEquality(self, ctx):    return self._binary(ctx)
    def visitRelational(self, ctx):  return self._binary(ctx)
    def visitShift(self, ctx):       return self._binary(ctx)
    def visitAddSub(self, ctx):      return self._binary(ctx)
    def visitMulDivMod(self, ctx):   return self._binary(ctx)
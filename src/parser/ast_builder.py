from antlr_files.grammers.CParser.CParserVisitor import CParserVisitor
from parser.ast_nodes import (
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


class ASTBuilder(CParserVisitor):
    """
    Walks the ANTLR Concrete Syntax Tree (CST) and builds our own AST.
    One visit method per labelled alternative in the grammar (the # labels).
    Each method returns an ASTNode — no ANTLR objects leak past this class.
    """

    # ── Top level ─────────────────────────────────────────────

    def visitTranslation_unit(self, ctx):
        return ProgramNode(self.visit(ctx.main_function()))

    def visitMain_function(self, ctx):
        # ctx.statement() returns the list of all statements inside main
        statements = [self.visit(stmt) for stmt in ctx.statement()]
        return MainFunctionNode(statements)

    # ── Statements ────────────────────────────────────────────

    def visitStatement(self, ctx):
        # A statement is one of: var_decl, assignment, expression
        # Just pass through to the correct child
        return self.visit(ctx.getChild(0))

    # ── Variable declaration ───────────────────────────────────

    def visitVar_decl(self, ctx):
        # CONST? type_spec '*'* IDENTIFIER ('=' expression)?
        is_const = ctx.CONST() is not None
        type_name = ctx.type_spec().getText()

        # Count the number of '*' tokens for pointer depth
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        name = ctx.IDENTIFIER().getText()

        # Check if there is an initializer (the '=' expression part)
        value = self.visit(ctx.expression()) if ctx.expression() else None

        return VarDeclNode(is_const, type_name, pointer_depth, name, value)

    # ── Assignment ────────────────────────────────────────────

    def visitAssignment(self, ctx):
        # unary_expr '=' expression
        target = self.visit(ctx.unary_expr())
        value  = self.visit(ctx.expression())
        return AssignNode(target, value)

    # ── Expressions ───────────────────────────────────────────

    def _binary(self, ctx):
        """Build a BinaryOpNode from any binary expression context."""
        left  = self.visit(ctx.expression(0))
        op    = ctx.getChild(1).getText()
        right = self.visit(ctx.expression(1))
        return BinaryOpNode(op, left, right)

    def visitMulDivMod(self, ctx):  return self._binary(ctx)
    def visitAddSub(self, ctx):     return self._binary(ctx)
    def visitShift(self, ctx):      return self._binary(ctx)
    def visitRelational(self, ctx): return self._binary(ctx)
    def visitEquality(self, ctx):   return self._binary(ctx)
    def visitBitwiseAnd(self, ctx): return self._binary(ctx)
    def visitBitwiseXor(self, ctx): return self._binary(ctx)
    def visitBitwiseOr(self, ctx):  return self._binary(ctx)
    def visitLogicalAnd(self, ctx): return self._binary(ctx)
    def visitLogicalOr(self, ctx):  return self._binary(ctx)

    def visitUnaryExpr(self, ctx):
        # Just pass through to the unary_expr rule
        return self.visit(ctx.unary_expr())

    # ── Unary expressions ─────────────────────────────────────

    def visitLogicalNot(self, ctx):
        return UnaryOpNode('!', self.visit(ctx.unary_expr()))

    def visitBitwiseNot(self, ctx):
        return UnaryOpNode('~', self.visit(ctx.unary_expr()))

    def visitUnaryPlusMinus(self, ctx):
        op      = ctx.getChild(0).getText()  # '+' or '-'
        operand = self.visit(ctx.unary_expr())
        return UnaryOpNode(op, operand)

    def visitDereference(self, ctx):
        return DereferenceNode(self.visit(ctx.unary_expr()))

    def visitAddressOf(self, ctx):
        return AddressOfNode(self.visit(ctx.unary_expr()))

    def visitPrefixIncrement(self, ctx):
        return IncrementNode(self.visit(ctx.unary_expr()), prefix=True)

    def visitPrefixDecrement(self, ctx):
        return DecrementNode(self.visit(ctx.unary_expr()), prefix=True)

    def visitCast(self, ctx):
        type_name     = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        operand = self.visit(ctx.unary_expr())
        return CastNode(type_name, pointer_depth, operand)

    def visitPostfixExprRule(self, ctx):
        # Just pass through to postfix_expr
        return self.visit(ctx.postfix_expr())

    # ── Postfix expressions ───────────────────────────────────

    def visitPostfixIncrement(self, ctx):
        return IncrementNode(self.visit(ctx.primary_expr()), prefix=False)

    def visitPostfixDecrement(self, ctx):
        return DecrementNode(self.visit(ctx.primary_expr()), prefix=False)

    def visitPrimaryExprRule(self, ctx):
        # Just pass through to primary_expr
        return self.visit(ctx.primary_expr())

    # ── Primary expressions ───────────────────────────────────

    def visitParens(self, ctx):
        # '(' expression ')' — just unwrap, no node needed
        return self.visit(ctx.expression())

    def visitLiteralExpr(self, ctx):
        return self.visit(ctx.literal())

    def visitIdentifierExpr(self, ctx):
        return IdentifierNode(ctx.IDENTIFIER().getText())

    # ── Literals ──────────────────────────────────────────────

    def visitIntLiteral(self, ctx):
        return IntLiteralNode(int(ctx.INTEGER().getText()))

    def visitFloatLiteral(self, ctx):
        return FloatLiteralNode(float(ctx.FLOAT_LIT().getText()))

    def visitCharLiteral(self, ctx):
        # Strip the surrounding quotes: 'a' -> a
        raw = ctx.CHAR_LIT().getText()
        return CharLiteralNode(raw[1:-1])
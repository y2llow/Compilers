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

    Now also includes line and column information for error reporting.
    """

    def _get_line_col(self, ctx):
        """Extract line and column from ANTLR context"""
        if hasattr(ctx, 'start'):
            return ctx.start.line, ctx.start.column
        return 0, 0

    def _attach_position(self, node, ctx):
        """Attach line and column to AST node"""
        if node is not None:
            line, col = self._get_line_col(ctx)
            node.line = line
            node.column = col
        return node

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

        node = VarDeclNode(is_const, type_name, pointer_depth, name, value)
        return self._attach_position(node, ctx)

    # ── Assignment ────────────────────────────────────────────

    def visitAssignment(self, ctx):
        # unary_expr '=' expression
        target = self.visit(ctx.unary_expr())
        value = self.visit(ctx.expression())
        node = AssignNode(target, value)
        return self._attach_position(node, ctx)

    # ── Expressions ───────────────────────────────────────────

    def _binary(self, ctx):
        """Build a BinaryOpNode from any binary expression context."""
        left = self.visit(ctx.expression(0))
        op = ctx.getChild(1).getText()
        right = self.visit(ctx.expression(1))
        node = BinaryOpNode(op, left, right)
        return self._attach_position(node, ctx)

    def visitMulDivMod(self, ctx):
        return self._binary(ctx)

    def visitAddSub(self, ctx):
        return self._binary(ctx)

    def visitShift(self, ctx):
        return self._binary(ctx)

    def visitRelational(self, ctx):
        return self._binary(ctx)

    def visitEquality(self, ctx):
        return self._binary(ctx)

    def visitBitwiseAnd(self, ctx):
        return self._binary(ctx)

    def visitBitwiseXor(self, ctx):
        return self._binary(ctx)

    def visitBitwiseOr(self, ctx):
        return self._binary(ctx)

    def visitLogicalAnd(self, ctx):
        return self._binary(ctx)

    def visitLogicalOr(self, ctx):
        return self._binary(ctx)

    def visitUnaryExpr(self, ctx):
        # Just pass through to the unary_expr rule
        return self.visit(ctx.unary_expr())

    # ── Unary expressions ─────────────────────────────────────

    def visitLogicalNot(self, ctx):
        node = UnaryOpNode('!', self.visit(ctx.unary_expr()))
        return self._attach_position(node, ctx)

    def visitBitwiseNot(self, ctx):
        node = UnaryOpNode('~', self.visit(ctx.unary_expr()))
        return self._attach_position(node, ctx)

    def visitUnaryPlusMinus(self, ctx):
        op = ctx.getChild(0).getText()  # '+' or '-'
        operand = self.visit(ctx.unary_expr())
        node = UnaryOpNode(op, operand)
        return self._attach_position(node, ctx)

    def visitDereference(self, ctx):
        node = DereferenceNode(self.visit(ctx.unary_expr()))
        return self._attach_position(node, ctx)

    def visitAddressOf(self, ctx):
        node = AddressOfNode(self.visit(ctx.unary_expr()))
        return self._attach_position(node, ctx)

    def visitPrefixIncrement(self, ctx):
        node = IncrementNode(self.visit(ctx.unary_expr()), prefix=True)
        return self._attach_position(node, ctx)

    def visitPrefixDecrement(self, ctx):
        node = DecrementNode(self.visit(ctx.unary_expr()), prefix=True)
        return self._attach_position(node, ctx)

    def visitCast(self, ctx):
        type_name = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        operand = self.visit(ctx.unary_expr())
        node = CastNode(type_name, pointer_depth, operand)
        return self._attach_position(node, ctx)

    def visitPostfixExprRule(self, ctx):
        # Just pass through to postfix_expr
        return self.visit(ctx.postfix_expr())

    # ── Postfix expressions ───────────────────────────────────

    def visitPostfixIncrement(self, ctx):
        node = IncrementNode(self.visit(ctx.primary_expr()), prefix=False)
        return self._attach_position(node, ctx)

    def visitPostfixDecrement(self, ctx):
        node = DecrementNode(self.visit(ctx.primary_expr()), prefix=False)
        return self._attach_position(node, ctx)

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
        node = IdentifierNode(ctx.IDENTIFIER().getText())
        return self._attach_position(node, ctx)

    # ── Literals ──────────────────────────────────────────────

    def visitIntLiteral(self, ctx):
        node = IntLiteralNode(int(ctx.INTEGER().getText()))
        return self._attach_position(node, ctx)

    def visitFloatLiteral(self, ctx):
        node = FloatLiteralNode(float(ctx.FLOAT_LIT().getText()))
        return self._attach_position(node, ctx)

    def visitCharLiteral(self, ctx):
        # Strip the surrounding quotes: 'a' -> a
        raw = ctx.CHAR_LIT().getText()
        node = CharLiteralNode(raw[1:-1])
        return self._attach_position(node, ctx)
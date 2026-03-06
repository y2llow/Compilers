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
    ArrayAccessNode,
    ArrayInitializerNode,
)


class ASTBuilder(CParserVisitor):
    """
    Walks the ANTLR Concrete Syntax Tree (CST) and builds our own AST.
    Updated to handle the new grammar with var_initializer.
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
        statements = [self.visit(stmt) for stmt in ctx.statement()]
        return MainFunctionNode(statements)

    # ── Statements ────────────────────────────────────────────

    def visitStatement(self, ctx):
        # A statement can be var_decl, assignment, return_statement, or expression
        # Just pass through to the correct child
        return self.visit(ctx.getChild(0))

    def visitReturn_statement(self, ctx):
        # return_statement: 'return' expression? ';'
        expr = None
        if ctx.expression():
            expr = self.visit(ctx.expression())
        # For now, we'll just return the expression (or None)
        # You might want to create a ReturnNode later
        return expr

    # ── Variable declaration ───────────────────────────────────

    def visitVar_decl(self, ctx):
        # CONST? type_spec '*'* IDENTIFIER array_dimension* ('=' var_initializer)?
        is_const = ctx.CONST() is not None
        type_name = ctx.type_spec().getText()

        # Count the number of '*' tokens for pointer depth
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        name = ctx.IDENTIFIER().getText()

        # Get array dimensions
        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                # array_dimension: '[' INTEGER ']'
                dim_size = int(dim_ctx.INTEGER().getText())
                array_dimensions.append(dim_size)

        # Check if there is an initializer (the '=' var_initializer part)
        value = None
        if ctx.var_initializer():
            value = self.visit(ctx.var_initializer())

        node = VarDeclNode(is_const, type_name, pointer_depth, name, array_dimensions, value)
        return self._attach_position(node, ctx)

    # ── Variable initializer ──────────────────────────────────

    def visitVar_initializer(self, ctx):
        # var_initializer: array_initializer | expression
        if ctx.array_initializer():
            return self.visit(ctx.array_initializer())
        else:
            return self.visit(ctx.expression())

    # ── Array initialization ───────────────────────────────────

    def visitArray_initializer(self, ctx):
        # array_initializer: '{' initializer_list? '}'
        initializer_list = []
        if ctx.initializer_list():
            initializer_list = self.visit(ctx.initializer_list())
        node = ArrayInitializerNode(initializer_list)
        return self._attach_position(node, ctx)

    def visitInitializer_list(self, ctx):
        # initializer_list: initializer (',' initializer)*
        initializers = [self.visit(init) for init in ctx.initializer()]
        return initializers

    def visitInitializer(self, ctx):
        # initializer: expression | array_initializer
        if ctx.expression():
            return self.visit(ctx.expression())
        else:
            return self.visit(ctx.array_initializer())

    # ── Assignment ────────────────────────────────────────────

    def visitAssignment(self, ctx):
        # assignment: postfix_expr '=' expression
        target = self.visit(ctx.postfix_expr())
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

    def visitPostfixExpr(self, ctx):
        # Just pass through to postfix_expr rule
        return self.visit(ctx.postfix_expr())

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

    def visitPostfix_expr(self, ctx):
        # postfix_expr: primary_expr postfix_op*
        result = self.visit(ctx.primary_expr())

        # Apply postfix operations left to right
        if ctx.postfix_op():
            for op_ctx in ctx.postfix_op():
                result = self._visit_postfix_op(op_ctx, result)

        return result

    def _visit_postfix_op(self, ctx, expr):
        """Visit a postfix operator with the given expression as operand"""
        # postfix_op can be: [expression], ++, or --
        first_child = ctx.getChild(0).getText()

        if first_child == '[':
            # Array access: [expression]
            index = self.visit(ctx.expression())
            node = ArrayAccessNode(expr, index)
            return self._attach_position(node, ctx)
        elif first_child == '++':
            node = IncrementNode(expr, prefix=False)
            return self._attach_position(node, ctx)
        elif first_child == '--':
            node = DecrementNode(expr, prefix=False)
            return self._attach_position(node, ctx)

        return expr

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
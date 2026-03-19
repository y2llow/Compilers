from antlr_files.grammers.CParser.CParserVisitor import CParserVisitor
from parser.ast_nodes import (
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
    ArrayAccessNode,
    ArrayInitializerNode,
    StringLiteralNode,
    IncludeNode,
    PrintfNode,
    ScanfNode,
)

def _unescape(s: str) -> str:
    return (s
        .replace('\\n', '\n')
        .replace('\\t', '\t')
        .replace('\\r', '\r')
        .replace('\\"', '"')
        .replace('\\\\', '\\')
    )

class ASTBuilder(CParserVisitor):
    """
    Walks the ANTLR Concrete Syntax Tree (CST) and builds our own AST.
    Updated to handle the new grammar with var_initializer.
    """

    def __init__(self, comment_collector=None, source_lines=None):
        self.comment_collector = comment_collector
        self.source_lines = source_lines or []

    def _should_attach_comments(self, node):
        """
        Bepaal of deze node comments mag krijgen.
        Alleen top-level statement nodes, niet sub-expressions.
        """
        from parser.ast_nodes import (
            VarDeclNode,
            AssignNode,
            ReturnNode,
            MainFunctionNode,
            ProgramNode,
            IncrementNode,
            DecrementNode,
        )

        statement_types = (
            VarDeclNode,
            AssignNode,
            ReturnNode,
            MainFunctionNode,
            ProgramNode,
            IncrementNode,
            DecrementNode,
        )

        return isinstance(node, statement_types)

    def _get_line_col(self, ctx):
        """Extract line and column from ANTLR context"""
        if hasattr(ctx, 'start'):
            return ctx.start.line, ctx.start.column
        return 0, 0

    def _attach_position(self, node, ctx):
        """Attach line, column, source code, and comments to AST node"""
        if node is not None:
            line, col = self._get_line_col(ctx)
            node.line = line
            node.column = col

            # Get source line
            if 0 < line <= len(self.source_lines):
                node.source_line = self.source_lines[line - 1].rstrip('\n')

            # Get comments - ALLEEN voor statement-level nodes
            if self.comment_collector and self._should_attach_comments(node):
                leading, inline = self.comment_collector.get_for_line(line)
                node.leading_comments = leading
                node.inline_comment = inline

        return node

    # ── Top level ─────────────────────────────────────────────
    def visitTranslation_unit(self, ctx):
        includes = []
        main_fn = None
        statements = []
        has_real_main = False  # NIEUW

        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)

            if hasattr(child, 'getText') and child.getText() == '<EOF>':
                continue

            child_type = type(child).__name__

            if 'Include_directiveContext' in child_type:
                inc = self.visit(child)
                if inc is not None:
                    includes.append(inc)
            elif 'Main_functionContext' in child_type:
                main_fn = self.visit(child)
                has_real_main = True  # NIEUW
            else:
                result = self.visit(child)
                if result is not None:
                    statements.append(result)

        if has_real_main:
            program = ProgramNode(includes, main_fn)
        else:
            # Geen echte main — zet has_real_main=False op het program node
            fake_main = MainFunctionNode(statements)
            program = ProgramNode(includes, fake_main)
            program.has_real_main = False  # NIEUW: markeer als fake

        return self._attach_position(program, ctx)

    def visitInclude_directive(self, ctx):
        """
        Visit #include <stdio.h>
        """
        node = IncludeNode('stdio.h')
        return self._attach_position(node, ctx)

    def visitMain_function(self, ctx):
        statements = [self.visit(stmt) for stmt in ctx.statement()]
        node = MainFunctionNode(statements)
        return self._attach_position(node, ctx)

    # ── Statements ────────────────────────────────────────────

    def visitStatement(self, ctx):
        # A statement can be var_decl, assignment, return_statement, or expression
        # Just pass through to the correct child
        return self.visit(ctx.getChild(0))

    def visitReturn_statement(self, ctx):
        """
        Creates a proper ReturnNode instead of just returning the expression.
        return_statement: 'return' expression? ';'
        """
        expr = None
        if ctx.expression():
            expr = self.visit(ctx.expression())

        # Maak ReturnNode
        node = ReturnNode(expr)
        return self._attach_position(node, ctx)

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

    def visitStringLiteral(self, ctx):
        # Handle string literals
        raw = ctx.STRING_LIT().getText()
        # Remove surrounding quotes: "hello" -> hello
        string_value = raw[1:-1]
        # Unescape common escape sequences
        string_value = string_value.replace('\\n', '\n')
        string_value = string_value.replace('\\t', '\t')
        string_value = string_value.replace('\\r', '\r')
        string_value = string_value.replace('\\"', '"')
        string_value = string_value.replace('\\\\', '\\')
        node = StringLiteralNode(string_value)
        return self._attach_position(node, ctx)

    # ── Includes ──────────────────────────────────────────────
    def visitInclude_directive(self, ctx):
        # include_directive: HASH INCLUDE LT_STDIO_H GT
        node = IncludeNode('stdio.h')
        return self._attach_position(node, ctx)

    def visitPrintf_statement(self, ctx):
        # printf_statement: PRINTF '(' STRING_LIT (',' printf_arg)* ')'
        raw = ctx.STRING_LIT().getText()  # e.g. "\"Hello\\n\""
        format_string = _unescape(raw[1:-1])  # strip quotes, unescape
        args = [self.visit(a) for a in ctx.printf_arg()]
        node = PrintfNode(format_string, args)
        return self._attach_position(node, ctx)

    def visitPrintf_arg(self, ctx):
        return self.visit(ctx.unary_expr())

    def visitScanf_statement(self, ctx):
        # scanf_statement: SCANF '(' STRING_LIT (',' scanf_arg)* ')'
        raw = ctx.STRING_LIT().getText()
        format_string = _unescape(raw[1:-1])
        args = [self.visit(a) for a in ctx.scanf_arg()]
        node = ScanfNode(format_string, args)
        return self._attach_position(node, ctx)

    def visitScanf_arg(self, ctx):
        return self.visit(ctx.unary_expr())

    # Helper (can be a module-level function or reuse the existing logic
    # from visitStringLiteral):
    def _unescape(s: str) -> str:
        return (s
                .replace('\\n', '\n')
                .replace('\\t', '\t')
                .replace('\\r', '\r')
                .replace('\\"', '"')
                .replace('\\\\', '\\')
                )
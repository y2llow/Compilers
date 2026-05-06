from antlr_files.grammers.CParser.CParserVisitor import CParserVisitor
from parser.ast_nodes import (
    ProgramNode,
    IncludeNode,
    DefineNode,
    TypedefNode,
    EnumConstantNode,
    EnumDeclNode,
    StructMemberNode,
    StructDeclNode,
    ParameterNode,
    FunctionDeclNode,
    FunctionDefNode,
    FunctionCallNode,
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
    ReturnNode,
    AssignNode,
    IntLiteralNode,
    FloatLiteralNode,
    CharLiteralNode,
    StringLiteralNode,
    IdentifierNode,
    ArrayAccessNode,
    ArrayInitializerNode,
    MemberAccessNode,
    PointerMemberAccessNode,
    UnaryOpNode,
    DereferenceNode,
    AddressOfNode,
    IncrementNode,
    DecrementNode,
    CastNode,
    SizeofNode,
    BinaryOpNode,
    TernaryOpNode,
    PrintfNode,
    ScanfNode,
)


def _unescape(s: str) -> str:
    """Vervang escape sequences in een string."""
    return (s
        .replace('\\n', '\n')
        .replace('\\t', '\t')
        .replace('\\r', '\r')
        .replace('\\"', '"')
        .replace('\\\\', '\\')
    )


class ASTBuilder(CParserVisitor):
    """
    Loopt door de ANTLR Parse Tree en bouwt een AST.
    """

    def __init__(self, comment_collector=None, source_lines=None):
        self.comment_collector = comment_collector
        self.source_lines = source_lines or []
        self.syntax_errors = []  # errors found during AST building

        # Track typedef/struct/enum names so we can resolve the
        # "someType* x" ambiguity (decl vs multiplication) in visitVar_decl.
        self.known_type_names = set()
        self.typedef_map = {}  # name -> (base_type, pointer_depth)

    # ?? Hulpfuncties ??????????????????????????????????????????

    def _get_line_col(self, ctx):
        if hasattr(ctx, 'start') and ctx.start is not None:
            return ctx.start.line, ctx.start.column
        return 0, 0

    def _attach_position(self, node, ctx):
        if node is None:
            return None

        line, col = self._get_line_col(ctx)
        node.line = line
        node.column = col

        if 0 < line <= len(self.source_lines):
            node.source_line = self.source_lines[line - 1].rstrip('\n')

        if self.comment_collector and self._should_attach_comments(node):
            leading, inline = self.comment_collector.get_for_line(line)
            node.leading_comments = leading
            node.inline_comment = inline

        return node

    def _should_attach_comments(self, node):
        return isinstance(node, (
            VarDeclNode, AssignNode, ReturnNode,
            IfNode, WhileNode, ForNode, SwitchNode,
            BreakNode, ContinueNode,
            FunctionDefNode, FunctionDeclNode,
            PrintfNode, ScanfNode,
            IncrementNode, DecrementNode,
        ))

    # ?? Top level ?????????????????????????????????????????????

    def visitTranslation_unit(self, ctx):
        items = []
        for child in ctx.top_level_item():
            result = self.visit(child)
            if result is not None:
                items.append(result)

        node = ProgramNode(items)
        return self._attach_position(node, ctx)

    def visitTop_level_item(self, ctx):
        return self.visit(ctx.getChild(0))

    # ?? Preprocessor ??????????????????????????????????????????

    def visitInclude_directive(self, ctx):
        if ctx.LT_STDIO_H():
            node = IncludeNode('stdio.h', is_system=True)
        else:
            raw = ctx.STRING_LIT().getText()
            header = raw[1:-1]
            node = IncludeNode(header, is_system=False)

        return self._attach_position(node, ctx)

    def visitDefine_directive(self, ctx):
        name = ctx.IDENTIFIER().getText()
        value = ctx.define_value().getText()
        node = DefineNode(name, value)
        return self._attach_position(node, ctx)

    def visitDefine_value(self, ctx):
        return ctx.getText()

    # ?? Typedef ???????????????????????????????????????????????

    def visitTypedef_decl(self, ctx):
        new_name = ctx.IDENTIFIER().getText()

        if ctx.type_spec():
            existing_type = ctx.type_spec().getText()
            pointer_depth = sum(
                1 for i in range(ctx.getChildCount())
                if ctx.getChild(i).getText() == '*'
            )
        elif ctx.struct_specifier():
            existing_type = ctx.struct_specifier().IDENTIFIER().getText()
            pointer_depth = 0
        elif ctx.enum_specifier():
            existing_type = ctx.enum_specifier().IDENTIFIER().getText()
            pointer_depth = 0
        else:
            existing_type = 'int'
            pointer_depth = 0

        # Register so visitVar_decl can resolve the pointer ambiguity
        self.known_type_names.add(new_name)
        self.typedef_map[new_name] = (existing_type, pointer_depth)  # ← ADD THIS LINE
        node = TypedefNode(existing_type, pointer_depth, new_name)
        return self._attach_position(node, ctx)

    # ?? Enum ??????????????????????????????????????????????????

    def visitEnum_decl(self, ctx):
        return self.visit(ctx.enum_specifier())

    def visitEnum_specifier(self, ctx):
        name = ctx.IDENTIFIER().getText()

        constants = []
        if ctx.enum_body():
            constants = self.visit(ctx.enum_body())

        self.known_type_names.add(name)

        node = EnumDeclNode(name, constants)
        return self._attach_position(node, ctx)

    def visitEnum_body(self, ctx):
        return [self.visit(c) for c in ctx.enum_constant()]

    def visitEnum_constant(self, ctx):
        name = ctx.IDENTIFIER().getText()
        value = None
        if ctx.INTEGER():
            value = int(ctx.INTEGER().getText())

        node = EnumConstantNode(name, value)
        return self._attach_position(node, ctx)

    # ?? Struct ????????????????????????????????????????????????

    def visitStruct_decl(self, ctx):
        return self.visit(ctx.struct_specifier())

    def visitStruct_specifier(self, ctx):
        name = ctx.IDENTIFIER().getText()
        members = []
        if ctx.struct_member():
            members = [self.visit(m) for m in ctx.struct_member()]

        # Register so pointer-to-struct vars can be recognised
        self.known_type_names.add(name)

        node = StructDeclNode(name, members)
        return self._attach_position(node, ctx)

    def visitStruct_member(self, ctx):
        name = ctx.IDENTIFIER().getText()

        if ctx.type_spec():
            type_name = ctx.type_spec().getText()
        elif ctx.enum_specifier():
            type_name = ctx.enum_specifier().IDENTIFIER().getText()
        elif ctx.struct_specifier():
            type_name = ctx.struct_specifier().IDENTIFIER().getText()
        else:
            type_name = 'int'

        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                integer_token = dim_ctx.INTEGER()
                if integer_token is not None:
                    array_dimensions.append(int(integer_token.getText()))

        node = StructMemberNode(type_name, pointer_depth, name, array_dimensions)
        return self._attach_position(node, ctx)

    # ?? Functions ?????????????????????????????????????????????

    def visitFunction_definition(self, ctx):
        return_type, return_ptr = self._visit_return_type(ctx.return_type_spec())
        name = ctx.IDENTIFIER().getText()

        params = []
        if ctx.parameter_list():
            params = self.visit(ctx.parameter_list())

        body = self.visit(ctx.compound_statement())

        node = FunctionDefNode(return_type, return_ptr, name, params, body)
        return self._attach_position(node, ctx)

    def visitFunction_declaration(self, ctx):
        return_type, return_ptr = self._visit_return_type(ctx.return_type_spec())
        name = ctx.IDENTIFIER().getText()

        params = []
        if ctx.parameter_list():
            params = self.visit(ctx.parameter_list())

        node = FunctionDeclNode(return_type, return_ptr, name, params)
        return self._attach_position(node, ctx)

    def _visit_return_type(self, ctx):
        if ctx.VOID():
            return 'void', 0

        type_name = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        return type_name, pointer_depth

    def visitParameter_list(self, ctx):
        if ctx.VOID():
            return []

        return [self.visit(p) for p in ctx.parameter()]

    def visitParameter(self, ctx):
        is_const = ctx.CONST() is not None and len(ctx.CONST()) > 0

        type_name = ctx.type_spec().getText()

        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        name = ctx.IDENTIFIER().getText()

        # Parameters allow int arr[] (no size) so we allow None here
        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                integer_token = dim_ctx.INTEGER()
                if integer_token is not None:
                    array_dimensions.append(int(integer_token.getText()))

        node = ParameterNode(is_const, type_name, pointer_depth, name, array_dimensions)
        return self._attach_position(node, ctx)

    # ?? Compound statement ????????????????????????????????????

    def visitCompound_statement(self, ctx):
        items = []
        for item_ctx in ctx.block_item():
            result = self.visit(item_ctx)
            if result is not None:
                items.append(result)

        node = CompoundStmtNode(items)
        return self._attach_position(node, ctx)

    def _as_compound_body(self, node):
        if isinstance(node, CompoundStmtNode):
            return node
        if node is None:
            return CompoundStmtNode([])
        return CompoundStmtNode([node])

    def visitBlock_item(self, ctx):
        if ctx.var_decl():
            return self.visit(ctx.var_decl())
        else:
            return self.visit(ctx.statement())

    # ?? Statements ????????????????????????????????????????????

    def visitStatement(self, ctx):
        if ctx.getChildCount() == 1 and ctx.getChild(0).getText() == ';':
            return None

        return self.visit(ctx.getChild(0))

    def visitIf_statement(self, ctx):
        condition = self.visit(ctx.expression())

        then_body = self._as_compound_body(self.visit(ctx.control_body(0)))

        else_body = None
        if len(ctx.control_body()) > 1:
            else_body = self._as_compound_body(self.visit(ctx.control_body(1)))

        node = IfNode(condition, then_body, else_body)
        return self._attach_position(node, ctx)

    def visitControl_body(self, ctx):
        return self.visit(ctx.getChild(0))

    def visitWhile_statement(self, ctx):
        condition = self.visit(ctx.expression())
        body = self._as_compound_body(self.visit(ctx.control_body()))

        node = WhileNode(condition, body)
        return self._attach_position(node, ctx)

    def visitFor_statement(self, ctx):
        init = None
        if ctx.for_init():
            init = self.visit(ctx.for_init())

        condition = None
        if ctx.expression():
            condition = self.visit(ctx.expression())

        update = None
        if ctx.for_update():
            update = self.visit(ctx.for_update())

        body = self._as_compound_body(self.visit(ctx.control_body()))

        node = ForNode(init, condition, update, body)
        return self._attach_position(node, ctx)

    def visitFor_init(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        return self.visit(ctx.getChild(0))

    def visitFor_update(self, ctx):
        return self.visit(ctx.getChild(0))

    def visitSwitch_statement(self, ctx):
        expression = self.visit(ctx.expression())

        cases = [self.visit(c) for c in ctx.switch_case()]

        default = None
        if ctx.switch_default():
            default = self.visit(ctx.switch_default())

        node = SwitchNode(expression, cases, default)
        return self._attach_position(node, ctx)

    def visitSwitch_case(self, ctx):
        value = self.visit(ctx.expression())
        items = [self.visit(i) for i in ctx.block_item() if self.visit(i) is not None]

        node = SwitchCaseNode(value, items)
        return self._attach_position(node, ctx)

    def visitSwitch_default(self, ctx):
        items = [self.visit(i) for i in ctx.block_item() if self.visit(i) is not None]

        node = SwitchDefaultNode(items)
        return self._attach_position(node, ctx)

    def visitReturn_statement(self, ctx):
        value = None
        if ctx.expression():
            value = self.visit(ctx.expression())

        node = ReturnNode(value)
        return self._attach_position(node, ctx)

    def visitBreak_statement(self, ctx):
        node = BreakNode()
        return self._attach_position(node, ctx)

    def visitContinue_statement(self, ctx):
        node = ContinueNode()
        return self._attach_position(node, ctx)

    # ?? printf / scanf ????????????????????????????????????????

    def visitPrintf_statement(self, ctx):
        fmt_expr = self.visit(ctx.expression())
        args = [self.visit(a) for a in ctx.printf_arg()]

        if isinstance(fmt_expr, StringLiteralNode):
            node = PrintfNode(fmt_expr.value, args)
        elif isinstance(fmt_expr, IdentifierNode):
            node = FunctionCallNode("printf", [fmt_expr] + args)
        else:
            node = FunctionCallNode("printf", [fmt_expr] + args)

        return self._attach_position(node, ctx)

    def visitPrintf_arg(self, ctx):
        return self.visit(ctx.expression())

    def visitScanf_statement(self, ctx):
        raw = ctx.STRING_LIT().getText()
        format_string = _unescape(raw[1:-1])
        args = [self.visit(a) for a in ctx.scanf_arg()]

        node = ScanfNode(format_string, args)
        return self._attach_position(node, ctx)

    def visitScanf_arg(self, ctx):
        return self.visit(ctx.expression())

    # ?? Variable declaration ??????????????????????????????????

    def visitVar_decl(self, ctx):
        is_const = ctx.CONST() is not None and len(ctx.CONST()) > 0

        type_name = ctx.type_spec().getText()

        # Strip 'enum'/'struct' prefix added by ANTLR getText() concatenation
        for prefix in ('enum', 'struct'):
            if type_name.startswith(prefix) and len(type_name) > len(prefix):
                type_name = type_name[len(prefix):]
                break

        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        name = ctx.IDENTIFIER().getText()

        # Ambiguity resolution: "someType * x" could be multiplication.
        # If the type name is not a known type AND there are stars, this is
        # likely a multiplication expression that the grammar mis-routed.
        # We emit a syntax error so the user gets a clear message.
        builtin_types = {'int', 'float', 'char', 'void'}
        if (pointer_depth > 0
                and type_name not in builtin_types
                and type_name not in self.known_type_names):
            line, col = self._get_line_col(ctx)
            self.syntax_errors.append({
                'line': line,
                'column': col,
                'message': f"Unknown type '{type_name}' — did you mean a multiplication? "
                           f"Declare typedef/struct before using it as a pointer type."
            })
            return None

        # Array dimensions
        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                integer_token = dim_ctx.INTEGER()
                if integer_token is None:
                    # int arr[] without a size is not valid in a variable
                    # declaration (only allowed in function parameters).
                    line = dim_ctx.start.line if dim_ctx.start else 0
                    col = dim_ctx.start.column if dim_ctx.start else 0
                    self.syntax_errors.append({
                        'line': line,
                        'column': col,
                        'message': "Array declaration must specify a constant size (e.g. int arr[3])"
                    })
                    return None
                array_dimensions.append(int(integer_token.getText()))

        # Initialisatie waarde
        value = None
        if ctx.var_initializer():
            value = self.visit(ctx.var_initializer())

        node = VarDeclNode(is_const, type_name, pointer_depth, name,
                           array_dimensions, value)
        return self._attach_position(node, ctx)

    def visitVar_initializer(self, ctx):
        if ctx.array_initializer():
            return self.visit(ctx.array_initializer())
        return self.visit(ctx.expression())

    def visitArray_initializer(self, ctx):
        elements = []
        if ctx.initializer_list():
            elements = self.visit(ctx.initializer_list())

        node = ArrayInitializerNode(elements)
        return self._attach_position(node, ctx)

    def visitInitializer_list(self, ctx):
        return [self.visit(i) for i in ctx.initializer()]

    def visitInitializer(self, ctx):
        if ctx.expression():
            return self.visit(ctx.expression())
        return self.visit(ctx.array_initializer())

    # ?? Assignment ????????????????????????????????????????????

    def visitAssignment(self, ctx):
        target = self.visit(ctx.unary_expr())
        op = ctx.assign_op().getText()
        value = self.visit(ctx.expression())

        node = AssignNode(target, op, value)
        return self._attach_position(node, ctx)

    def visitAssign_op(self, ctx):
        return ctx.getText()

    # ?? Expressions ???????????????????????????????????????????

    def _binary(self, ctx):
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

    def visitTernary(self, ctx):
        condition = self.visit(ctx.expression(0))
        then_expr = self.visit(ctx.expression(1))
        else_expr = self.visit(ctx.expression(2))

        node = TernaryOpNode(condition, then_expr, else_expr)
        return self._attach_position(node, ctx)

    def visitUnaryExpr(self, ctx):
        return self.visit(ctx.unary_expr())

    # ?? Unary expressions ?????????????????????????????????????

    def visitLogicalNot(self, ctx):
        node = UnaryOpNode('!', self.visit(ctx.unary_expr()))
        return self._attach_position(node, ctx)

    def visitBitwiseNot(self, ctx):
        node = UnaryOpNode('~', self.visit(ctx.unary_expr()))
        return self._attach_position(node, ctx)

    def visitUnaryPlusMinus(self, ctx):
        op = ctx.getChild(0).getText()
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

    def visitSizeofType(self, ctx):
        type_name = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        node = SizeofNode(type_name=type_name, pointer_depth=pointer_depth,
                          is_type=True)
        return self._attach_position(node, ctx)

    def visitSizeofExpr(self, ctx):
        operand = self.visit(ctx.unary_expr())
        node = SizeofNode(operand=operand, is_type=False)
        return self._attach_position(node, ctx)

    def visitPostfixExprRule(self, ctx):
        return self.visit(ctx.postfix_expr())

    # ?? Postfix expressions ???????????????????????????????????

    def visitPostfix_expr(self, ctx):
        result = self.visit(ctx.primary_expr())

        for op_ctx in ctx.postfix_op():
            result = self._visit_postfix_op(op_ctx, result)

        return result

    def _visit_postfix_op(self, ctx, expr):
        first = ctx.getChild(0).getText()

        if first == '[':
            index = self.visit(ctx.expression())
            node = ArrayAccessNode(expr, index)
            return self._attach_position(node, ctx)

        elif first == '(':
            name = expr.name if isinstance(expr, IdentifierNode) else str(expr)
            args = []
            if ctx.argument_list():
                args = self.visit(ctx.argument_list())
            node = FunctionCallNode(name, args)
            return self._attach_position(node, ctx)

        elif first == '.':
            member = ctx.IDENTIFIER().getText()
            node = MemberAccessNode(expr, member)
            return self._attach_position(node, ctx)

        elif first == '->':
            member = ctx.IDENTIFIER().getText()
            node = PointerMemberAccessNode(expr, member)
            return self._attach_position(node, ctx)

        elif first == '++':
            node = IncrementNode(expr, prefix=False)
            return self._attach_position(node, ctx)

        elif first == '--':
            node = DecrementNode(expr, prefix=False)
            return self._attach_position(node, ctx)

        return expr

    def visitArgument_list(self, ctx):
        return [self.visit(e) for e in ctx.expression()]

    # ?? Primary expressions ???????????????????????????????????

    def visitParens(self, ctx):
        return self.visit(ctx.expression())

    def visitLiteralExpr(self, ctx):
        return self.visit(ctx.literal())

    def visitIdentifierExpr(self, ctx):
        node = IdentifierNode(ctx.IDENTIFIER().getText())
        return self._attach_position(node, ctx)

    # ?? Literals ??????????????????????????????????????????????

    def visitIntLiteral(self, ctx):
        node = IntLiteralNode(int(ctx.INTEGER().getText()))
        return self._attach_position(node, ctx)

    def visitFloatLiteral(self, ctx):
        node = FloatLiteralNode(float(ctx.FLOAT_LIT().getText()))
        return self._attach_position(node, ctx)

    def visitCharLiteral(self, ctx):
        raw = ctx.CHAR_LIT().getText()
        node = CharLiteralNode(raw[1:-1])
        return self._attach_position(node, ctx)

    def visitStringLiteral(self, ctx):
        raw = ctx.STRING_LIT().getText()
        value = _unescape(raw[1:-1])
        node = StringLiteralNode(value)
        return self._attach_position(node, ctx)
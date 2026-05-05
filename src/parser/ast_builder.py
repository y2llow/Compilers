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

    Voor elke grammar regel is er een visit methode.
    Elke methode pakt de relevante info uit de parse tree
    en maakt de juiste AST node aan.
    """

    def __init__(self, comment_collector=None, source_lines=None):
        self.comment_collector = comment_collector
        self.source_lines = source_lines or []

    # ── Hulpfuncties ──────────────────────────────────────────

    def _get_line_col(self, ctx):
        """Haal regel- en kolomnummer op uit ANTLR context."""
        if hasattr(ctx, 'start') and ctx.start is not None:
            return ctx.start.line, ctx.start.column
        return 0, 0

    def _attach_position(self, node, ctx):
        """Voeg positie-info en comments toe aan een AST node."""
        if node is None:
            return None

        line, col = self._get_line_col(ctx)
        node.line = line
        node.column = col

        # Broncode regel opslaan
        if 0 < line <= len(self.source_lines):
            node.source_line = self.source_lines[line - 1].rstrip('\n')

        # Comments ophalen voor statement-level nodes
        if self.comment_collector and self._should_attach_comments(node):
            leading, inline = self.comment_collector.get_for_line(line)
            node.leading_comments = leading
            node.inline_comment = inline

        return node

    def _should_attach_comments(self, node):
        """Alleen statement-level nodes krijgen comments."""
        return isinstance(node, (
            VarDeclNode, AssignNode, ReturnNode,
            IfNode, WhileNode, ForNode, SwitchNode,
            BreakNode, ContinueNode,
            FunctionDefNode, FunctionDeclNode,
            PrintfNode, ScanfNode,
            IncrementNode, DecrementNode,
        ))

    # ── Top level ─────────────────────────────────────────────

    def visitTranslation_unit(self, ctx):
        """
        translation_unit: top_level_item* EOF
        Maakt een ProgramNode met alle top-level items.
        """
        items = []
        for child in ctx.top_level_item():
            result = self.visit(child)
            if result is not None:
                items.append(result)

        node = ProgramNode(items)
        return self._attach_position(node, ctx)

    def visitTop_level_item(self, ctx):
        """
        top_level_item: include_directive | define_directive | ...
        Geeft gewoon door naar het juiste child.
        """
        return self.visit(ctx.getChild(0))

    # ── Preprocessor ──────────────────────────────────────────

    def visitInclude_directive(self, ctx):
        """
        include_directive: HASH INCLUDE (LT_STDIO_H | STRING_LIT)
        Twee vormen:
          #include <stdio.h>   → is_system=True
          #include "file.h"    → is_system=False
        """
        # Kijk of het LT_STDIO_H is of een STRING_LIT
        if ctx.LT_STDIO_H():
            # <stdio.h>
            node = IncludeNode('stdio.h', is_system=True)
        else:
            # "some/file.h" — strip aanhalingstekens
            raw = ctx.STRING_LIT().getText()
            header = raw[1:-1]  # verwijder " en "
            node = IncludeNode(header, is_system=False)

        return self._attach_position(node, ctx)

    def visitDefine_directive(self, ctx):
        """
        define_directive: HASH DEFINE IDENTIFIER define_value
        Voorbeeld: #define bool int
        """
        name = ctx.IDENTIFIER().getText()
        value = ctx.define_value().getText()  # raw tekst
        node = DefineNode(name, value)
        return self._attach_position(node, ctx)

    def visitDefine_value(self, ctx):
        """Geeft de ruwe tekst terug — wordt gebruikt door visitDefine_directive."""
        return ctx.getText()

    # ── Typedef ───────────────────────────────────────────────

    def visitTypedef_decl(self, ctx):
        """
        typedef_decl:
            TYPEDEF type_spec '*'* IDENTIFIER ';'
          | TYPEDEF struct_specifier IDENTIFIER ';'
          | TYPEDEF enum_specifier IDENTIFIER ';'

        Voorbeeld: typedef int bool;
                   typedef struct Point Point;
        """
        # De nieuwe naam is altijd het laatste IDENTIFIER
        new_name = ctx.IDENTIFIER().getText()

        # Bepaal het bestaande type
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

        node = TypedefNode(existing_type, pointer_depth, new_name)
        return self._attach_position(node, ctx)

    # ── Enum ──────────────────────────────────────────────────

    def visitEnum_decl(self, ctx):
        """
        enum_decl: enum_specifier
        Geeft gewoon door naar enum_specifier.
        """
        return self.visit(ctx.enum_specifier())

    def visitEnum_specifier(self, ctx):
        """
        enum_specifier:
            ENUM IDENTIFIER '{' enum_body '}'
          | ENUM IDENTIFIER

        Voorbeeld: enum Color { RED, GREEN, BLUE }
        """
        name = ctx.IDENTIFIER().getText()

        constants = []
        if ctx.enum_body():
            constants = self.visit(ctx.enum_body())

        node = EnumDeclNode(name, constants)
        return self._attach_position(node, ctx)

    def visitEnum_body(self, ctx):
        """
        enum_body: enum_constant (',' enum_constant)* ','?
        Geeft een lijst van EnumConstantNode terug.
        """
        return [self.visit(c) for c in ctx.enum_constant()]

    def visitEnum_constant(self, ctx):
        """
        enum_constant: IDENTIFIER ('=' INTEGER)?
        Voorbeeld: RED of RED = 5
        """
        name = ctx.IDENTIFIER().getText()
        value = None
        if ctx.INTEGER():
            value = int(ctx.INTEGER().getText())

        node = EnumConstantNode(name, value)
        return self._attach_position(node, ctx)

    # ── Struct ────────────────────────────────────────────────

    def visitStruct_decl(self, ctx):
        """
        struct_decl: struct_specifier
        Geeft gewoon door.
        """
        return self.visit(ctx.struct_specifier())

    def visitStruct_specifier(self, ctx):
        """
        struct_specifier: STRUCT IDENTIFIER ('{' struct_member* '}')?
        Voorbeeld: struct Point { int x; int y; }
        """
        name = ctx.IDENTIFIER().getText()
        members = []
        if ctx.struct_member():
            members = [self.visit(m) for m in ctx.struct_member()]

        node = StructDeclNode(name, members)
        return self._attach_position(node, ctx)

    def visitStruct_member(self, ctx):
        """
        struct_member:
            type_spec '*'* IDENTIFIER array_dimension* ';'
          | enum_specifier IDENTIFIER ';'
          | struct_specifier IDENTIFIER ';'

        Voorbeeld: int x;  of  int* ptr;  of  int arr[5];
        """
        # Haal de naam op (altijd het laatste IDENTIFIER vóór ';')
        name = ctx.IDENTIFIER().getText()

        # Bepaal het type
        if ctx.type_spec():
            type_name = ctx.type_spec().getText()
        elif ctx.enum_specifier():
            type_name = ctx.enum_specifier().IDENTIFIER().getText()
        elif ctx.struct_specifier():
            type_name = ctx.struct_specifier().IDENTIFIER().getText()
        else:
            type_name = 'int'

        # Pointer diepte
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        # Array dimensies
        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                array_dimensions.append(int(dim_ctx.INTEGER().getText()))

        node = StructMemberNode(type_name, pointer_depth, name, array_dimensions)
        return self._attach_position(node, ctx)

    # ── Functions ─────────────────────────────────────────────

    def visitFunction_definition(self, ctx):
        """
        function_definition:
            return_type_spec IDENTIFIER '(' parameter_list? ')' compound_statement

        Voorbeeld: int add(int x, int y) { return x + y; }
        """
        return_type, return_ptr = self._visit_return_type(ctx.return_type_spec())
        name = ctx.IDENTIFIER().getText()

        params = []
        if ctx.parameter_list():
            params = self.visit(ctx.parameter_list())

        body = self.visit(ctx.compound_statement())

        node = FunctionDefNode(return_type, return_ptr, name, params, body)
        return self._attach_position(node, ctx)

    def visitFunction_declaration(self, ctx):
        """
        function_declaration:
            return_type_spec IDENTIFIER '(' parameter_list? ')'

        Voorbeeld: int add(int x, int y);  ← forward declaration
        """
        return_type, return_ptr = self._visit_return_type(ctx.return_type_spec())
        name = ctx.IDENTIFIER().getText()

        params = []
        if ctx.parameter_list():
            params = self.visit(ctx.parameter_list())

        node = FunctionDeclNode(return_type, return_ptr, name, params)
        return self._attach_position(node, ctx)

    def _visit_return_type(self, ctx):
        """
        return_type_spec: VOID | type_spec '*'*
        Geeft (type_naam, pointer_diepte) terug.
        """
        if ctx.VOID():
            return 'void', 0

        type_name = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        return type_name, pointer_depth

    def visitParameter_list(self, ctx):
        """
        parameter_list: parameter (',' parameter)* | VOID
        Geeft een lijst van ParameterNode terug.
        Als het VOID is (lege parameterlijst), geef lege lijst terug.
        """
        # VOID als enige parameter betekent geen parameters
        if ctx.VOID():
            return []

        return [self.visit(p) for p in ctx.parameter()]

    def visitParameter(self, ctx):
        """
        parameter: CONST? type_spec CONST? '*'* IDENTIFIER array_dimension*
        Voorbeeld: int x  of  const float* ptr
        """
        is_const = ctx.CONST() is not None and len(ctx.CONST()) > 0

        type_name = ctx.type_spec().getText()

        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        name = ctx.IDENTIFIER().getText()

        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                array_dimensions.append(int(dim_ctx.INTEGER().getText()))

        node = ParameterNode(is_const, type_name, pointer_depth, name, array_dimensions)
        return self._attach_position(node, ctx)

    # ── Compound statement ────────────────────────────────────

    def visitCompound_statement(self, ctx):
        """
        compound_statement: '{' block_item* '}'
        Maakt een CompoundStmtNode met alle items in het blok.
        """
        items = []
        for item_ctx in ctx.block_item():
            result = self.visit(item_ctx)
            if result is not None:
                items.append(result)

        node = CompoundStmtNode(items)
        return self._attach_position(node, ctx)

    def visitBlock_item(self, ctx):
        """
        block_item: statement | var_decl ';'
        Geeft gewoon door naar het juiste child.
        """
        if ctx.var_decl():
            return self.visit(ctx.var_decl())
        else:
            return self.visit(ctx.statement())

    # ── Statements ────────────────────────────────────────────

    def visitStatement(self, ctx):
        """
        statement: compound_statement | if_statement | while_statement | ...
        Geeft door naar het juiste child.
        """
        # Lege statement (alleen ';')
        if ctx.getChildCount() == 1 and ctx.getChild(0).getText() == ';':
            return None

        return self.visit(ctx.getChild(0))

    def visitIf_statement(self, ctx):
        """
        if_statement:
            IF '(' expression ')' compound_statement
            (ELSE compound_statement)?

        Voorbeeld: if (x > 0) { ... } else { ... }
        """
        condition = self.visit(ctx.expression())
        then_body = self.visit(ctx.compound_statement(0))

        else_body = None
        if len(ctx.compound_statement()) > 1:
            else_body = self.visit(ctx.compound_statement(1))

        node = IfNode(condition, then_body, else_body)
        return self._attach_position(node, ctx)

    def visitWhile_statement(self, ctx):
        """
        while_statement: WHILE '(' expression ')' compound_statement

        Voorbeeld: while (x < 10) { ... }
        """
        condition = self.visit(ctx.expression())
        body = self.visit(ctx.compound_statement())

        node = WhileNode(condition, body)
        return self._attach_position(node, ctx)

    def visitFor_statement(self, ctx):
        """
        for_statement:
            FOR '(' for_init ';' expression? ';' for_update? ')'
            compound_statement

        Voorbeeld: for (int i = 0; i < 10; i++) { ... }
        """
        # Init (mag leeg zijn)
        init = None
        if ctx.for_init():
            init = self.visit(ctx.for_init())

        # Conditie (mag leeg zijn → oneindige lus)
        condition = None
        if ctx.expression():
            condition = self.visit(ctx.expression())

        # Update (mag leeg zijn)
        update = None
        if ctx.for_update():
            update = self.visit(ctx.for_update())

        body = self.visit(ctx.compound_statement())

        node = ForNode(init, condition, update, body)
        return self._attach_position(node, ctx)

    def visitFor_init(self, ctx):
        """
        for_init: var_decl | assignment | expression |
        Mag leeg zijn.
        """
        if ctx.getChildCount() == 0:
            return None
        return self.visit(ctx.getChild(0))

    def visitFor_update(self, ctx):
        """
        for_update: assignment | unary_expr | expression
        """
        return self.visit(ctx.getChild(0))

    def visitSwitch_statement(self, ctx):
        """
        switch_statement:
            SWITCH '(' expression ')' '{' switch_case* switch_default? '}'

        Voorbeeld:
            switch (x) {
                case 1: ...
                case 2: ...
                default: ...
            }
        """
        expression = self.visit(ctx.expression())

        cases = [self.visit(c) for c in ctx.switch_case()]

        default = None
        if ctx.switch_default():
            default = self.visit(ctx.switch_default())

        node = SwitchNode(expression, cases, default)
        return self._attach_position(node, ctx)

    def visitSwitch_case(self, ctx):
        """
        switch_case: CASE expression ':' block_item*
        """
        value = self.visit(ctx.expression())
        items = [self.visit(i) for i in ctx.block_item() if self.visit(i) is not None]

        node = SwitchCaseNode(value, items)
        return self._attach_position(node, ctx)

    def visitSwitch_default(self, ctx):
        """
        switch_default: DEFAULT ':' block_item*
        """
        items = [self.visit(i) for i in ctx.block_item() if self.visit(i) is not None]

        node = SwitchDefaultNode(items)
        return self._attach_position(node, ctx)

    def visitReturn_statement(self, ctx):
        """
        return_statement: RETURN expression? ';'
        """
        value = None
        if ctx.expression():
            value = self.visit(ctx.expression())

        node = ReturnNode(value)
        return self._attach_position(node, ctx)

    def visitBreak_statement(self, ctx):
        """break_statement: BREAK ';'"""
        node = BreakNode()
        return self._attach_position(node, ctx)

    def visitContinue_statement(self, ctx):
        """continue_statement: CONTINUE ';'"""
        node = ContinueNode()
        return self._attach_position(node, ctx)

    # ── printf / scanf ────────────────────────────────────────

    def visitPrintf_statement(self, ctx):
        """
        printf_statement: PRINTF '(' expression (',' printf_arg)* ')'
        Eerste argument kan nu STRING_LIT of een macro identifier zijn.
        """
        fmt_expr = self.visit(ctx.expression())

        args = [self.visit(a) for a in ctx.printf_arg()]

        if isinstance(fmt_expr, StringLiteralNode):
            node = PrintfNode(fmt_expr.value, args)
        elif isinstance(fmt_expr, IdentifierNode):
            # Wordt later door de Preprocessor opgelost.
            node = FunctionCallNode("printf", [fmt_expr] + args)
        else:
            node = FunctionCallNode("printf", [fmt_expr] + args)

        return self._attach_position(node, ctx)

    def visitPrintf_arg(self, ctx):
        return self.visit(ctx.expression())

    def visitScanf_statement(self, ctx):
        """
        scanf_statement: SCANF '(' STRING_LIT (',' scanf_arg)* ')'
        """
        raw = ctx.STRING_LIT().getText()
        format_string = _unescape(raw[1:-1])
        args = [self.visit(a) for a in ctx.scanf_arg()]

        node = ScanfNode(format_string, args)
        return self._attach_position(node, ctx)

    def visitScanf_arg(self, ctx):
        return self.visit(ctx.expression())

    # ── Variable declaration ──────────────────────────────────

    def visitVar_decl(self, ctx):
        """
        var_decl:
            CONST? type_spec CONST? '*'* IDENTIFIER
            array_dimension* ('=' var_initializer)?

        Voorbeeld: const int* ptr = &x;
                   int arr[5] = {1,2,3,4,5};
        """
        # const aanwezig?
        is_const = ctx.CONST() is not None and len(ctx.CONST()) > 0

        type_name = ctx.type_spec().getText()

        # Pointer diepte = aantal '*' tokens
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )

        name = ctx.IDENTIFIER().getText()

        # Array dimensies
        array_dimensions = []
        if ctx.array_dimension():
            for dim_ctx in ctx.array_dimension():
                array_dimensions.append(int(dim_ctx.INTEGER().getText()))

        # Initialisatie waarde
        value = None
        if ctx.var_initializer():
            value = self.visit(ctx.var_initializer())

        node = VarDeclNode(is_const, type_name, pointer_depth, name,
                           array_dimensions, value)
        return self._attach_position(node, ctx)

    def visitVar_initializer(self, ctx):
        """
        var_initializer: array_initializer | expression
        """
        if ctx.array_initializer():
            return self.visit(ctx.array_initializer())
        return self.visit(ctx.expression())

    def visitArray_initializer(self, ctx):
        """
        array_initializer: '{' initializer_list? '}'
        """
        elements = []
        if ctx.initializer_list():
            elements = self.visit(ctx.initializer_list())

        node = ArrayInitializerNode(elements)
        return self._attach_position(node, ctx)

    def visitInitializer_list(self, ctx):
        """
        initializer_list: initializer (',' initializer)*
        """
        return [self.visit(i) for i in ctx.initializer()]

    def visitInitializer(self, ctx):
        """
        initializer: expression | array_initializer
        """
        if ctx.expression():
            return self.visit(ctx.expression())
        return self.visit(ctx.array_initializer())

    # ── Assignment ────────────────────────────────────────────

    def visitAssignment(self, ctx):
        """
        assignment: unary_expr assign_op expression

        Voorbeeld: x = 5;  of  x += 3;
        """
        target = self.visit(ctx.unary_expr())
        op = ctx.assign_op().getText()
        value = self.visit(ctx.expression())

        node = AssignNode(target, op, value)
        return self._attach_position(node, ctx)

    def visitAssign_op(self, ctx):
        """Geeft de operator terug als string."""
        return ctx.getText()

    # ── Expressions ───────────────────────────────────────────

    def _binary(self, ctx):
        """Hulpfunctie voor alle binaire expressies."""
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
        """
        expression '?' expression ':' expression
        Voorbeeld: a > b ? a : b
        """
        condition = self.visit(ctx.expression(0))
        then_expr = self.visit(ctx.expression(1))
        else_expr = self.visit(ctx.expression(2))

        node = TernaryOpNode(condition, then_expr, else_expr)
        return self._attach_position(node, ctx)

    def visitUnaryExpr(self, ctx):
        """Geeft door naar unary_expr."""
        return self.visit(ctx.unary_expr())

    # ── Unary expressions ─────────────────────────────────────

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
        """
        '(' CONST? type_spec '*'* ')' unary_expr
        Voorbeeld: (int) 3.14  of  (float*) ptr
        """
        type_name = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        operand = self.visit(ctx.unary_expr())
        node = CastNode(type_name, pointer_depth, operand)
        return self._attach_position(node, ctx)

    def visitSizeofType(self, ctx):
        """
        SIZEOF '(' type_spec '*'* ')'
        Voorbeeld: sizeof(int)  of  sizeof(int*)
        """
        type_name = ctx.type_spec().getText()
        pointer_depth = sum(
            1 for i in range(ctx.getChildCount())
            if ctx.getChild(i).getText() == '*'
        )
        node = SizeofNode(type_name=type_name, pointer_depth=pointer_depth,
                          is_type=True)
        return self._attach_position(node, ctx)

    def visitSizeofExpr(self, ctx):
        """
        SIZEOF '(' unary_expr ')'
        Voorbeeld: sizeof(x)
        """
        operand = self.visit(ctx.unary_expr())
        node = SizeofNode(operand=operand, is_type=False)
        return self._attach_position(node, ctx)

    def visitPostfixExprRule(self, ctx):
        """Geeft door naar postfix_expr."""
        return self.visit(ctx.postfix_expr())

    # ── Postfix expressions ───────────────────────────────────

    def visitPostfix_expr(self, ctx):
        """
        postfix_expr: primary_expr postfix_op*

        Verwerkt alle postfix operaties van links naar rechts.
        Voorbeeld: arr[i]++  of  obj.member  of  func(args)
        """
        result = self.visit(ctx.primary_expr())

        for op_ctx in ctx.postfix_op():
            result = self._visit_postfix_op(op_ctx, result)

        return result

    def _visit_postfix_op(self, ctx, expr):
        """
        Verwerkt één postfix operatie met de expressie als operand.
        postfix_op kan zijn: [expr], (args), .member, ->member, ++, --
        """
        first = ctx.getChild(0).getText()

        if first == '[':
            # Array toegang: arr[i]
            index = self.visit(ctx.expression())
            node = ArrayAccessNode(expr, index)
            return self._attach_position(node, ctx)

        elif first == '(':
            # Functie aanroep: func(arg1, arg2)
            # De naam van de functie zit in expr (een IdentifierNode)
            name = expr.name if isinstance(expr, IdentifierNode) else str(expr)
            args = []
            if ctx.argument_list():
                args = self.visit(ctx.argument_list())
            node = FunctionCallNode(name, args)
            return self._attach_position(node, ctx)

        elif first == '.':
            # Struct member toegang: obj.member
            member = ctx.IDENTIFIER().getText()
            node = MemberAccessNode(expr, member)
            return self._attach_position(node, ctx)

        elif first == '->':
            # Pointer member toegang: ptr->member
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
        """
        argument_list: expression (',' expression)*
        Geeft een lijst van expressies terug.
        """
        return [self.visit(e) for e in ctx.expression()]

    # ── Primary expressions ───────────────────────────────────

    def visitParens(self, ctx):
        """'(' expression ')' — haakjes weggooien, alleen inhoud bewaren."""
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
        raw = ctx.CHAR_LIT().getText()
        node = CharLiteralNode(raw[1:-1])  # strip ' en '
        return self._attach_position(node, ctx)

    def visitStringLiteral(self, ctx):
        raw = ctx.STRING_LIT().getText()
        value = _unescape(raw[1:-1])  # strip " en " en unescape
        node = StringLiteralNode(value)
        return self._attach_position(node, ctx)
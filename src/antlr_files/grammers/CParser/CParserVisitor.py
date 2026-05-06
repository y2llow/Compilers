# Generated from CParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CParserParser import CParserParser
else:
    from CParserParser import CParserParser

# This class defines a complete generic visitor for a parse tree produced by CParserParser.

class CParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CParserParser#translation_unit.
    def visitTranslation_unit(self, ctx:CParserParser.Translation_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#top_level_item.
    def visitTop_level_item(self, ctx:CParserParser.Top_level_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#include_directive.
    def visitInclude_directive(self, ctx:CParserParser.Include_directiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#define_directive.
    def visitDefine_directive(self, ctx:CParserParser.Define_directiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#define_value.
    def visitDefine_value(self, ctx:CParserParser.Define_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#typedef_decl.
    def visitTypedef_decl(self, ctx:CParserParser.Typedef_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#typedef_name.
    def visitTypedef_name(self, ctx:CParserParser.Typedef_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#enum_decl.
    def visitEnum_decl(self, ctx:CParserParser.Enum_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#enum_specifier.
    def visitEnum_specifier(self, ctx:CParserParser.Enum_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#enum_body.
    def visitEnum_body(self, ctx:CParserParser.Enum_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#enum_constant.
    def visitEnum_constant(self, ctx:CParserParser.Enum_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#struct_decl.
    def visitStruct_decl(self, ctx:CParserParser.Struct_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#struct_specifier.
    def visitStruct_specifier(self, ctx:CParserParser.Struct_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#struct_member.
    def visitStruct_member(self, ctx:CParserParser.Struct_memberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#function_definition.
    def visitFunction_definition(self, ctx:CParserParser.Function_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#function_declaration.
    def visitFunction_declaration(self, ctx:CParserParser.Function_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#return_type_spec.
    def visitReturn_type_spec(self, ctx:CParserParser.Return_type_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#parameter_list.
    def visitParameter_list(self, ctx:CParserParser.Parameter_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#parameter.
    def visitParameter(self, ctx:CParserParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#compound_statement.
    def visitCompound_statement(self, ctx:CParserParser.Compound_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#block_item.
    def visitBlock_item(self, ctx:CParserParser.Block_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#statement.
    def visitStatement(self, ctx:CParserParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#if_statement.
    def visitIf_statement(self, ctx:CParserParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#while_statement.
    def visitWhile_statement(self, ctx:CParserParser.While_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#for_statement.
    def visitFor_statement(self, ctx:CParserParser.For_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#control_body.
    def visitControl_body(self, ctx:CParserParser.Control_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#for_init.
    def visitFor_init(self, ctx:CParserParser.For_initContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#for_update.
    def visitFor_update(self, ctx:CParserParser.For_updateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#switch_statement.
    def visitSwitch_statement(self, ctx:CParserParser.Switch_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#switch_case.
    def visitSwitch_case(self, ctx:CParserParser.Switch_caseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#switch_default.
    def visitSwitch_default(self, ctx:CParserParser.Switch_defaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#return_statement.
    def visitReturn_statement(self, ctx:CParserParser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#break_statement.
    def visitBreak_statement(self, ctx:CParserParser.Break_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#continue_statement.
    def visitContinue_statement(self, ctx:CParserParser.Continue_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#printf_statement.
    def visitPrintf_statement(self, ctx:CParserParser.Printf_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#printf_arg.
    def visitPrintf_arg(self, ctx:CParserParser.Printf_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#scanf_statement.
    def visitScanf_statement(self, ctx:CParserParser.Scanf_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#scanf_arg.
    def visitScanf_arg(self, ctx:CParserParser.Scanf_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#var_decl.
    def visitVar_decl(self, ctx:CParserParser.Var_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#array_dimension.
    def visitArray_dimension(self, ctx:CParserParser.Array_dimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#var_initializer.
    def visitVar_initializer(self, ctx:CParserParser.Var_initializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#array_initializer.
    def visitArray_initializer(self, ctx:CParserParser.Array_initializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#initializer_list.
    def visitInitializer_list(self, ctx:CParserParser.Initializer_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#initializer.
    def visitInitializer(self, ctx:CParserParser.InitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#type_spec.
    def visitType_spec(self, ctx:CParserParser.Type_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#assignment.
    def visitAssignment(self, ctx:CParserParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#assign_op.
    def visitAssign_op(self, ctx:CParserParser.Assign_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#mulDivMod.
    def visitMulDivMod(self, ctx:CParserParser.MulDivModContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#unaryExpr.
    def visitUnaryExpr(self, ctx:CParserParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#shift.
    def visitShift(self, ctx:CParserParser.ShiftContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#bitwiseXor.
    def visitBitwiseXor(self, ctx:CParserParser.BitwiseXorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#logicalAnd.
    def visitLogicalAnd(self, ctx:CParserParser.LogicalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#addSub.
    def visitAddSub(self, ctx:CParserParser.AddSubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#relational.
    def visitRelational(self, ctx:CParserParser.RelationalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#bitwiseOr.
    def visitBitwiseOr(self, ctx:CParserParser.BitwiseOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#bitwiseAnd.
    def visitBitwiseAnd(self, ctx:CParserParser.BitwiseAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#logicalOr.
    def visitLogicalOr(self, ctx:CParserParser.LogicalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#equality.
    def visitEquality(self, ctx:CParserParser.EqualityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#ternary.
    def visitTernary(self, ctx:CParserParser.TernaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#logicalNot.
    def visitLogicalNot(self, ctx:CParserParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#bitwiseNot.
    def visitBitwiseNot(self, ctx:CParserParser.BitwiseNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#unaryPlusMinus.
    def visitUnaryPlusMinus(self, ctx:CParserParser.UnaryPlusMinusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#dereference.
    def visitDereference(self, ctx:CParserParser.DereferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#addressOf.
    def visitAddressOf(self, ctx:CParserParser.AddressOfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#prefixIncrement.
    def visitPrefixIncrement(self, ctx:CParserParser.PrefixIncrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#prefixDecrement.
    def visitPrefixDecrement(self, ctx:CParserParser.PrefixDecrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#cast.
    def visitCast(self, ctx:CParserParser.CastContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#sizeofType.
    def visitSizeofType(self, ctx:CParserParser.SizeofTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#sizeofExpr.
    def visitSizeofExpr(self, ctx:CParserParser.SizeofExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#postfixExprRule.
    def visitPostfixExprRule(self, ctx:CParserParser.PostfixExprRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#postfix_expr.
    def visitPostfix_expr(self, ctx:CParserParser.Postfix_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#arrayAccess.
    def visitArrayAccess(self, ctx:CParserParser.ArrayAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#functionCall.
    def visitFunctionCall(self, ctx:CParserParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#memberAccess.
    def visitMemberAccess(self, ctx:CParserParser.MemberAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#pointerMemberAccess.
    def visitPointerMemberAccess(self, ctx:CParserParser.PointerMemberAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#postfixIncrement.
    def visitPostfixIncrement(self, ctx:CParserParser.PostfixIncrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#postfixDecrement.
    def visitPostfixDecrement(self, ctx:CParserParser.PostfixDecrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#argument_list.
    def visitArgument_list(self, ctx:CParserParser.Argument_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#parens.
    def visitParens(self, ctx:CParserParser.ParensContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#literalExpr.
    def visitLiteralExpr(self, ctx:CParserParser.LiteralExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#identifierExpr.
    def visitIdentifierExpr(self, ctx:CParserParser.IdentifierExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#intLiteral.
    def visitIntLiteral(self, ctx:CParserParser.IntLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#floatLiteral.
    def visitFloatLiteral(self, ctx:CParserParser.FloatLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#charLiteral.
    def visitCharLiteral(self, ctx:CParserParser.CharLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParserParser#stringLiteral.
    def visitStringLiteral(self, ctx:CParserParser.StringLiteralContext):
        return self.visitChildren(ctx)



del CParserParser
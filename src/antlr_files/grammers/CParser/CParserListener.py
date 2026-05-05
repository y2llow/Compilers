# Generated from CParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CParserParser import CParserParser
else:
    from CParserParser import CParserParser

# This class defines a complete listener for a parse tree produced by CParserParser.
class CParserListener(ParseTreeListener):

    # Enter a parse tree produced by CParserParser#translation_unit.
    def enterTranslation_unit(self, ctx:CParserParser.Translation_unitContext):
        pass

    # Exit a parse tree produced by CParserParser#translation_unit.
    def exitTranslation_unit(self, ctx:CParserParser.Translation_unitContext):
        pass


    # Enter a parse tree produced by CParserParser#top_level_item.
    def enterTop_level_item(self, ctx:CParserParser.Top_level_itemContext):
        pass

    # Exit a parse tree produced by CParserParser#top_level_item.
    def exitTop_level_item(self, ctx:CParserParser.Top_level_itemContext):
        pass


    # Enter a parse tree produced by CParserParser#include_directive.
    def enterInclude_directive(self, ctx:CParserParser.Include_directiveContext):
        pass

    # Exit a parse tree produced by CParserParser#include_directive.
    def exitInclude_directive(self, ctx:CParserParser.Include_directiveContext):
        pass


    # Enter a parse tree produced by CParserParser#define_directive.
    def enterDefine_directive(self, ctx:CParserParser.Define_directiveContext):
        pass

    # Exit a parse tree produced by CParserParser#define_directive.
    def exitDefine_directive(self, ctx:CParserParser.Define_directiveContext):
        pass


    # Enter a parse tree produced by CParserParser#define_value.
    def enterDefine_value(self, ctx:CParserParser.Define_valueContext):
        pass

    # Exit a parse tree produced by CParserParser#define_value.
    def exitDefine_value(self, ctx:CParserParser.Define_valueContext):
        pass


    # Enter a parse tree produced by CParserParser#typedef_decl.
    def enterTypedef_decl(self, ctx:CParserParser.Typedef_declContext):
        pass

    # Exit a parse tree produced by CParserParser#typedef_decl.
    def exitTypedef_decl(self, ctx:CParserParser.Typedef_declContext):
        pass


    # Enter a parse tree produced by CParserParser#enum_decl.
    def enterEnum_decl(self, ctx:CParserParser.Enum_declContext):
        pass

    # Exit a parse tree produced by CParserParser#enum_decl.
    def exitEnum_decl(self, ctx:CParserParser.Enum_declContext):
        pass


    # Enter a parse tree produced by CParserParser#enum_specifier.
    def enterEnum_specifier(self, ctx:CParserParser.Enum_specifierContext):
        pass

    # Exit a parse tree produced by CParserParser#enum_specifier.
    def exitEnum_specifier(self, ctx:CParserParser.Enum_specifierContext):
        pass


    # Enter a parse tree produced by CParserParser#enum_body.
    def enterEnum_body(self, ctx:CParserParser.Enum_bodyContext):
        pass

    # Exit a parse tree produced by CParserParser#enum_body.
    def exitEnum_body(self, ctx:CParserParser.Enum_bodyContext):
        pass


    # Enter a parse tree produced by CParserParser#enum_constant.
    def enterEnum_constant(self, ctx:CParserParser.Enum_constantContext):
        pass

    # Exit a parse tree produced by CParserParser#enum_constant.
    def exitEnum_constant(self, ctx:CParserParser.Enum_constantContext):
        pass


    # Enter a parse tree produced by CParserParser#struct_decl.
    def enterStruct_decl(self, ctx:CParserParser.Struct_declContext):
        pass

    # Exit a parse tree produced by CParserParser#struct_decl.
    def exitStruct_decl(self, ctx:CParserParser.Struct_declContext):
        pass


    # Enter a parse tree produced by CParserParser#struct_specifier.
    def enterStruct_specifier(self, ctx:CParserParser.Struct_specifierContext):
        pass

    # Exit a parse tree produced by CParserParser#struct_specifier.
    def exitStruct_specifier(self, ctx:CParserParser.Struct_specifierContext):
        pass


    # Enter a parse tree produced by CParserParser#struct_member.
    def enterStruct_member(self, ctx:CParserParser.Struct_memberContext):
        pass

    # Exit a parse tree produced by CParserParser#struct_member.
    def exitStruct_member(self, ctx:CParserParser.Struct_memberContext):
        pass


    # Enter a parse tree produced by CParserParser#function_definition.
    def enterFunction_definition(self, ctx:CParserParser.Function_definitionContext):
        pass

    # Exit a parse tree produced by CParserParser#function_definition.
    def exitFunction_definition(self, ctx:CParserParser.Function_definitionContext):
        pass


    # Enter a parse tree produced by CParserParser#function_declaration.
    def enterFunction_declaration(self, ctx:CParserParser.Function_declarationContext):
        pass

    # Exit a parse tree produced by CParserParser#function_declaration.
    def exitFunction_declaration(self, ctx:CParserParser.Function_declarationContext):
        pass


    # Enter a parse tree produced by CParserParser#return_type_spec.
    def enterReturn_type_spec(self, ctx:CParserParser.Return_type_specContext):
        pass

    # Exit a parse tree produced by CParserParser#return_type_spec.
    def exitReturn_type_spec(self, ctx:CParserParser.Return_type_specContext):
        pass


    # Enter a parse tree produced by CParserParser#parameter_list.
    def enterParameter_list(self, ctx:CParserParser.Parameter_listContext):
        pass

    # Exit a parse tree produced by CParserParser#parameter_list.
    def exitParameter_list(self, ctx:CParserParser.Parameter_listContext):
        pass


    # Enter a parse tree produced by CParserParser#parameter.
    def enterParameter(self, ctx:CParserParser.ParameterContext):
        pass

    # Exit a parse tree produced by CParserParser#parameter.
    def exitParameter(self, ctx:CParserParser.ParameterContext):
        pass


    # Enter a parse tree produced by CParserParser#compound_statement.
    def enterCompound_statement(self, ctx:CParserParser.Compound_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#compound_statement.
    def exitCompound_statement(self, ctx:CParserParser.Compound_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#block_item.
    def enterBlock_item(self, ctx:CParserParser.Block_itemContext):
        pass

    # Exit a parse tree produced by CParserParser#block_item.
    def exitBlock_item(self, ctx:CParserParser.Block_itemContext):
        pass


    # Enter a parse tree produced by CParserParser#statement.
    def enterStatement(self, ctx:CParserParser.StatementContext):
        pass

    # Exit a parse tree produced by CParserParser#statement.
    def exitStatement(self, ctx:CParserParser.StatementContext):
        pass


    # Enter a parse tree produced by CParserParser#if_statement.
    def enterIf_statement(self, ctx:CParserParser.If_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#if_statement.
    def exitIf_statement(self, ctx:CParserParser.If_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#while_statement.
    def enterWhile_statement(self, ctx:CParserParser.While_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#while_statement.
    def exitWhile_statement(self, ctx:CParserParser.While_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#for_statement.
    def enterFor_statement(self, ctx:CParserParser.For_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#for_statement.
    def exitFor_statement(self, ctx:CParserParser.For_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#control_body.
    def enterControl_body(self, ctx:CParserParser.Control_bodyContext):
        pass

    # Exit a parse tree produced by CParserParser#control_body.
    def exitControl_body(self, ctx:CParserParser.Control_bodyContext):
        pass


    # Enter a parse tree produced by CParserParser#for_init.
    def enterFor_init(self, ctx:CParserParser.For_initContext):
        pass

    # Exit a parse tree produced by CParserParser#for_init.
    def exitFor_init(self, ctx:CParserParser.For_initContext):
        pass


    # Enter a parse tree produced by CParserParser#for_update.
    def enterFor_update(self, ctx:CParserParser.For_updateContext):
        pass

    # Exit a parse tree produced by CParserParser#for_update.
    def exitFor_update(self, ctx:CParserParser.For_updateContext):
        pass


    # Enter a parse tree produced by CParserParser#switch_statement.
    def enterSwitch_statement(self, ctx:CParserParser.Switch_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#switch_statement.
    def exitSwitch_statement(self, ctx:CParserParser.Switch_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#switch_case.
    def enterSwitch_case(self, ctx:CParserParser.Switch_caseContext):
        pass

    # Exit a parse tree produced by CParserParser#switch_case.
    def exitSwitch_case(self, ctx:CParserParser.Switch_caseContext):
        pass


    # Enter a parse tree produced by CParserParser#switch_default.
    def enterSwitch_default(self, ctx:CParserParser.Switch_defaultContext):
        pass

    # Exit a parse tree produced by CParserParser#switch_default.
    def exitSwitch_default(self, ctx:CParserParser.Switch_defaultContext):
        pass


    # Enter a parse tree produced by CParserParser#return_statement.
    def enterReturn_statement(self, ctx:CParserParser.Return_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#return_statement.
    def exitReturn_statement(self, ctx:CParserParser.Return_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#break_statement.
    def enterBreak_statement(self, ctx:CParserParser.Break_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#break_statement.
    def exitBreak_statement(self, ctx:CParserParser.Break_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#continue_statement.
    def enterContinue_statement(self, ctx:CParserParser.Continue_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#continue_statement.
    def exitContinue_statement(self, ctx:CParserParser.Continue_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#printf_statement.
    def enterPrintf_statement(self, ctx:CParserParser.Printf_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#printf_statement.
    def exitPrintf_statement(self, ctx:CParserParser.Printf_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#printf_arg.
    def enterPrintf_arg(self, ctx:CParserParser.Printf_argContext):
        pass

    # Exit a parse tree produced by CParserParser#printf_arg.
    def exitPrintf_arg(self, ctx:CParserParser.Printf_argContext):
        pass


    # Enter a parse tree produced by CParserParser#scanf_statement.
    def enterScanf_statement(self, ctx:CParserParser.Scanf_statementContext):
        pass

    # Exit a parse tree produced by CParserParser#scanf_statement.
    def exitScanf_statement(self, ctx:CParserParser.Scanf_statementContext):
        pass


    # Enter a parse tree produced by CParserParser#scanf_arg.
    def enterScanf_arg(self, ctx:CParserParser.Scanf_argContext):
        pass

    # Exit a parse tree produced by CParserParser#scanf_arg.
    def exitScanf_arg(self, ctx:CParserParser.Scanf_argContext):
        pass


    # Enter a parse tree produced by CParserParser#var_decl.
    def enterVar_decl(self, ctx:CParserParser.Var_declContext):
        pass

    # Exit a parse tree produced by CParserParser#var_decl.
    def exitVar_decl(self, ctx:CParserParser.Var_declContext):
        pass


    # Enter a parse tree produced by CParserParser#array_dimension.
    def enterArray_dimension(self, ctx:CParserParser.Array_dimensionContext):
        pass

    # Exit a parse tree produced by CParserParser#array_dimension.
    def exitArray_dimension(self, ctx:CParserParser.Array_dimensionContext):
        pass


    # Enter a parse tree produced by CParserParser#var_initializer.
    def enterVar_initializer(self, ctx:CParserParser.Var_initializerContext):
        pass

    # Exit a parse tree produced by CParserParser#var_initializer.
    def exitVar_initializer(self, ctx:CParserParser.Var_initializerContext):
        pass


    # Enter a parse tree produced by CParserParser#array_initializer.
    def enterArray_initializer(self, ctx:CParserParser.Array_initializerContext):
        pass

    # Exit a parse tree produced by CParserParser#array_initializer.
    def exitArray_initializer(self, ctx:CParserParser.Array_initializerContext):
        pass


    # Enter a parse tree produced by CParserParser#initializer_list.
    def enterInitializer_list(self, ctx:CParserParser.Initializer_listContext):
        pass

    # Exit a parse tree produced by CParserParser#initializer_list.
    def exitInitializer_list(self, ctx:CParserParser.Initializer_listContext):
        pass


    # Enter a parse tree produced by CParserParser#initializer.
    def enterInitializer(self, ctx:CParserParser.InitializerContext):
        pass

    # Exit a parse tree produced by CParserParser#initializer.
    def exitInitializer(self, ctx:CParserParser.InitializerContext):
        pass


    # Enter a parse tree produced by CParserParser#type_spec.
    def enterType_spec(self, ctx:CParserParser.Type_specContext):
        pass

    # Exit a parse tree produced by CParserParser#type_spec.
    def exitType_spec(self, ctx:CParserParser.Type_specContext):
        pass


    # Enter a parse tree produced by CParserParser#assignment.
    def enterAssignment(self, ctx:CParserParser.AssignmentContext):
        pass

    # Exit a parse tree produced by CParserParser#assignment.
    def exitAssignment(self, ctx:CParserParser.AssignmentContext):
        pass


    # Enter a parse tree produced by CParserParser#assign_op.
    def enterAssign_op(self, ctx:CParserParser.Assign_opContext):
        pass

    # Exit a parse tree produced by CParserParser#assign_op.
    def exitAssign_op(self, ctx:CParserParser.Assign_opContext):
        pass


    # Enter a parse tree produced by CParserParser#mulDivMod.
    def enterMulDivMod(self, ctx:CParserParser.MulDivModContext):
        pass

    # Exit a parse tree produced by CParserParser#mulDivMod.
    def exitMulDivMod(self, ctx:CParserParser.MulDivModContext):
        pass


    # Enter a parse tree produced by CParserParser#unaryExpr.
    def enterUnaryExpr(self, ctx:CParserParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by CParserParser#unaryExpr.
    def exitUnaryExpr(self, ctx:CParserParser.UnaryExprContext):
        pass


    # Enter a parse tree produced by CParserParser#shift.
    def enterShift(self, ctx:CParserParser.ShiftContext):
        pass

    # Exit a parse tree produced by CParserParser#shift.
    def exitShift(self, ctx:CParserParser.ShiftContext):
        pass


    # Enter a parse tree produced by CParserParser#bitwiseXor.
    def enterBitwiseXor(self, ctx:CParserParser.BitwiseXorContext):
        pass

    # Exit a parse tree produced by CParserParser#bitwiseXor.
    def exitBitwiseXor(self, ctx:CParserParser.BitwiseXorContext):
        pass


    # Enter a parse tree produced by CParserParser#logicalAnd.
    def enterLogicalAnd(self, ctx:CParserParser.LogicalAndContext):
        pass

    # Exit a parse tree produced by CParserParser#logicalAnd.
    def exitLogicalAnd(self, ctx:CParserParser.LogicalAndContext):
        pass


    # Enter a parse tree produced by CParserParser#addSub.
    def enterAddSub(self, ctx:CParserParser.AddSubContext):
        pass

    # Exit a parse tree produced by CParserParser#addSub.
    def exitAddSub(self, ctx:CParserParser.AddSubContext):
        pass


    # Enter a parse tree produced by CParserParser#relational.
    def enterRelational(self, ctx:CParserParser.RelationalContext):
        pass

    # Exit a parse tree produced by CParserParser#relational.
    def exitRelational(self, ctx:CParserParser.RelationalContext):
        pass


    # Enter a parse tree produced by CParserParser#bitwiseOr.
    def enterBitwiseOr(self, ctx:CParserParser.BitwiseOrContext):
        pass

    # Exit a parse tree produced by CParserParser#bitwiseOr.
    def exitBitwiseOr(self, ctx:CParserParser.BitwiseOrContext):
        pass


    # Enter a parse tree produced by CParserParser#bitwiseAnd.
    def enterBitwiseAnd(self, ctx:CParserParser.BitwiseAndContext):
        pass

    # Exit a parse tree produced by CParserParser#bitwiseAnd.
    def exitBitwiseAnd(self, ctx:CParserParser.BitwiseAndContext):
        pass


    # Enter a parse tree produced by CParserParser#logicalOr.
    def enterLogicalOr(self, ctx:CParserParser.LogicalOrContext):
        pass

    # Exit a parse tree produced by CParserParser#logicalOr.
    def exitLogicalOr(self, ctx:CParserParser.LogicalOrContext):
        pass


    # Enter a parse tree produced by CParserParser#equality.
    def enterEquality(self, ctx:CParserParser.EqualityContext):
        pass

    # Exit a parse tree produced by CParserParser#equality.
    def exitEquality(self, ctx:CParserParser.EqualityContext):
        pass


    # Enter a parse tree produced by CParserParser#ternary.
    def enterTernary(self, ctx:CParserParser.TernaryContext):
        pass

    # Exit a parse tree produced by CParserParser#ternary.
    def exitTernary(self, ctx:CParserParser.TernaryContext):
        pass


    # Enter a parse tree produced by CParserParser#logicalNot.
    def enterLogicalNot(self, ctx:CParserParser.LogicalNotContext):
        pass

    # Exit a parse tree produced by CParserParser#logicalNot.
    def exitLogicalNot(self, ctx:CParserParser.LogicalNotContext):
        pass


    # Enter a parse tree produced by CParserParser#bitwiseNot.
    def enterBitwiseNot(self, ctx:CParserParser.BitwiseNotContext):
        pass

    # Exit a parse tree produced by CParserParser#bitwiseNot.
    def exitBitwiseNot(self, ctx:CParserParser.BitwiseNotContext):
        pass


    # Enter a parse tree produced by CParserParser#unaryPlusMinus.
    def enterUnaryPlusMinus(self, ctx:CParserParser.UnaryPlusMinusContext):
        pass

    # Exit a parse tree produced by CParserParser#unaryPlusMinus.
    def exitUnaryPlusMinus(self, ctx:CParserParser.UnaryPlusMinusContext):
        pass


    # Enter a parse tree produced by CParserParser#dereference.
    def enterDereference(self, ctx:CParserParser.DereferenceContext):
        pass

    # Exit a parse tree produced by CParserParser#dereference.
    def exitDereference(self, ctx:CParserParser.DereferenceContext):
        pass


    # Enter a parse tree produced by CParserParser#addressOf.
    def enterAddressOf(self, ctx:CParserParser.AddressOfContext):
        pass

    # Exit a parse tree produced by CParserParser#addressOf.
    def exitAddressOf(self, ctx:CParserParser.AddressOfContext):
        pass


    # Enter a parse tree produced by CParserParser#prefixIncrement.
    def enterPrefixIncrement(self, ctx:CParserParser.PrefixIncrementContext):
        pass

    # Exit a parse tree produced by CParserParser#prefixIncrement.
    def exitPrefixIncrement(self, ctx:CParserParser.PrefixIncrementContext):
        pass


    # Enter a parse tree produced by CParserParser#prefixDecrement.
    def enterPrefixDecrement(self, ctx:CParserParser.PrefixDecrementContext):
        pass

    # Exit a parse tree produced by CParserParser#prefixDecrement.
    def exitPrefixDecrement(self, ctx:CParserParser.PrefixDecrementContext):
        pass


    # Enter a parse tree produced by CParserParser#cast.
    def enterCast(self, ctx:CParserParser.CastContext):
        pass

    # Exit a parse tree produced by CParserParser#cast.
    def exitCast(self, ctx:CParserParser.CastContext):
        pass


    # Enter a parse tree produced by CParserParser#sizeofType.
    def enterSizeofType(self, ctx:CParserParser.SizeofTypeContext):
        pass

    # Exit a parse tree produced by CParserParser#sizeofType.
    def exitSizeofType(self, ctx:CParserParser.SizeofTypeContext):
        pass


    # Enter a parse tree produced by CParserParser#sizeofExpr.
    def enterSizeofExpr(self, ctx:CParserParser.SizeofExprContext):
        pass

    # Exit a parse tree produced by CParserParser#sizeofExpr.
    def exitSizeofExpr(self, ctx:CParserParser.SizeofExprContext):
        pass


    # Enter a parse tree produced by CParserParser#postfixExprRule.
    def enterPostfixExprRule(self, ctx:CParserParser.PostfixExprRuleContext):
        pass

    # Exit a parse tree produced by CParserParser#postfixExprRule.
    def exitPostfixExprRule(self, ctx:CParserParser.PostfixExprRuleContext):
        pass


    # Enter a parse tree produced by CParserParser#postfix_expr.
    def enterPostfix_expr(self, ctx:CParserParser.Postfix_exprContext):
        pass

    # Exit a parse tree produced by CParserParser#postfix_expr.
    def exitPostfix_expr(self, ctx:CParserParser.Postfix_exprContext):
        pass


    # Enter a parse tree produced by CParserParser#arrayAccess.
    def enterArrayAccess(self, ctx:CParserParser.ArrayAccessContext):
        pass

    # Exit a parse tree produced by CParserParser#arrayAccess.
    def exitArrayAccess(self, ctx:CParserParser.ArrayAccessContext):
        pass


    # Enter a parse tree produced by CParserParser#functionCall.
    def enterFunctionCall(self, ctx:CParserParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by CParserParser#functionCall.
    def exitFunctionCall(self, ctx:CParserParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by CParserParser#memberAccess.
    def enterMemberAccess(self, ctx:CParserParser.MemberAccessContext):
        pass

    # Exit a parse tree produced by CParserParser#memberAccess.
    def exitMemberAccess(self, ctx:CParserParser.MemberAccessContext):
        pass


    # Enter a parse tree produced by CParserParser#pointerMemberAccess.
    def enterPointerMemberAccess(self, ctx:CParserParser.PointerMemberAccessContext):
        pass

    # Exit a parse tree produced by CParserParser#pointerMemberAccess.
    def exitPointerMemberAccess(self, ctx:CParserParser.PointerMemberAccessContext):
        pass


    # Enter a parse tree produced by CParserParser#postfixIncrement.
    def enterPostfixIncrement(self, ctx:CParserParser.PostfixIncrementContext):
        pass

    # Exit a parse tree produced by CParserParser#postfixIncrement.
    def exitPostfixIncrement(self, ctx:CParserParser.PostfixIncrementContext):
        pass


    # Enter a parse tree produced by CParserParser#postfixDecrement.
    def enterPostfixDecrement(self, ctx:CParserParser.PostfixDecrementContext):
        pass

    # Exit a parse tree produced by CParserParser#postfixDecrement.
    def exitPostfixDecrement(self, ctx:CParserParser.PostfixDecrementContext):
        pass


    # Enter a parse tree produced by CParserParser#argument_list.
    def enterArgument_list(self, ctx:CParserParser.Argument_listContext):
        pass

    # Exit a parse tree produced by CParserParser#argument_list.
    def exitArgument_list(self, ctx:CParserParser.Argument_listContext):
        pass


    # Enter a parse tree produced by CParserParser#parens.
    def enterParens(self, ctx:CParserParser.ParensContext):
        pass

    # Exit a parse tree produced by CParserParser#parens.
    def exitParens(self, ctx:CParserParser.ParensContext):
        pass


    # Enter a parse tree produced by CParserParser#literalExpr.
    def enterLiteralExpr(self, ctx:CParserParser.LiteralExprContext):
        pass

    # Exit a parse tree produced by CParserParser#literalExpr.
    def exitLiteralExpr(self, ctx:CParserParser.LiteralExprContext):
        pass


    # Enter a parse tree produced by CParserParser#identifierExpr.
    def enterIdentifierExpr(self, ctx:CParserParser.IdentifierExprContext):
        pass

    # Exit a parse tree produced by CParserParser#identifierExpr.
    def exitIdentifierExpr(self, ctx:CParserParser.IdentifierExprContext):
        pass


    # Enter a parse tree produced by CParserParser#intLiteral.
    def enterIntLiteral(self, ctx:CParserParser.IntLiteralContext):
        pass

    # Exit a parse tree produced by CParserParser#intLiteral.
    def exitIntLiteral(self, ctx:CParserParser.IntLiteralContext):
        pass


    # Enter a parse tree produced by CParserParser#floatLiteral.
    def enterFloatLiteral(self, ctx:CParserParser.FloatLiteralContext):
        pass

    # Exit a parse tree produced by CParserParser#floatLiteral.
    def exitFloatLiteral(self, ctx:CParserParser.FloatLiteralContext):
        pass


    # Enter a parse tree produced by CParserParser#charLiteral.
    def enterCharLiteral(self, ctx:CParserParser.CharLiteralContext):
        pass

    # Exit a parse tree produced by CParserParser#charLiteral.
    def exitCharLiteral(self, ctx:CParserParser.CharLiteralContext):
        pass


    # Enter a parse tree produced by CParserParser#stringLiteral.
    def enterStringLiteral(self, ctx:CParserParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by CParserParser#stringLiteral.
    def exitStringLiteral(self, ctx:CParserParser.StringLiteralContext):
        pass



del CParserParser
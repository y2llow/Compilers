# Generated from MyGrammar.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MyGrammarParser import MyGrammarParser
else:
    from MyGrammarParser import MyGrammarParser

# This class defines a complete listener for a parse tree produced by MyGrammarParser.
class MyGrammarListener(ParseTreeListener):

    # Enter a parse tree produced by MyGrammarParser#translation_unit.
    def enterTranslation_unit(self, ctx:MyGrammarParser.Translation_unitContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#translation_unit.
    def exitTranslation_unit(self, ctx:MyGrammarParser.Translation_unitContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#function_definition.
    def enterFunction_definition(self, ctx:MyGrammarParser.Function_definitionContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#function_definition.
    def exitFunction_definition(self, ctx:MyGrammarParser.Function_definitionContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#type_specifier.
    def enterType_specifier(self, ctx:MyGrammarParser.Type_specifierContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#type_specifier.
    def exitType_specifier(self, ctx:MyGrammarParser.Type_specifierContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#compound_statement.
    def enterCompound_statement(self, ctx:MyGrammarParser.Compound_statementContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#compound_statement.
    def exitCompound_statement(self, ctx:MyGrammarParser.Compound_statementContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#statement.
    def enterStatement(self, ctx:MyGrammarParser.StatementContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#statement.
    def exitStatement(self, ctx:MyGrammarParser.StatementContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#return_statement.
    def enterReturn_statement(self, ctx:MyGrammarParser.Return_statementContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#return_statement.
    def exitReturn_statement(self, ctx:MyGrammarParser.Return_statementContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#declaration_statement.
    def enterDeclaration_statement(self, ctx:MyGrammarParser.Declaration_statementContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#declaration_statement.
    def exitDeclaration_statement(self, ctx:MyGrammarParser.Declaration_statementContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#expression_statement.
    def enterExpression_statement(self, ctx:MyGrammarParser.Expression_statementContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#expression_statement.
    def exitExpression_statement(self, ctx:MyGrammarParser.Expression_statementContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#expression.
    def enterExpression(self, ctx:MyGrammarParser.ExpressionContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#expression.
    def exitExpression(self, ctx:MyGrammarParser.ExpressionContext):
        pass



del MyGrammarParser
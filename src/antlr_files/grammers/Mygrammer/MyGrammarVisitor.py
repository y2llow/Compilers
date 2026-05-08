# Generated from MyGrammar.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MyGrammarParser import MyGrammarParser
else:
    from MyGrammarParser import MyGrammarParser

# This class defines a complete generic visitor for a parse tree produced by MyGrammarParser.

class MyGrammarVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MyGrammarParser#translation_unit.
    def visitTranslation_unit(self, ctx:MyGrammarParser.Translation_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#function_definition.
    def visitFunction_definition(self, ctx:MyGrammarParser.Function_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#type_specifier.
    def visitType_specifier(self, ctx:MyGrammarParser.Type_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#compound_statement.
    def visitCompound_statement(self, ctx:MyGrammarParser.Compound_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#statement.
    def visitStatement(self, ctx:MyGrammarParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#return_statement.
    def visitReturn_statement(self, ctx:MyGrammarParser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#declaration_statement.
    def visitDeclaration_statement(self, ctx:MyGrammarParser.Declaration_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#expression_statement.
    def visitExpression_statement(self, ctx:MyGrammarParser.Expression_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#expression.
    def visitExpression(self, ctx:MyGrammarParser.ExpressionContext):
        return self.visitChildren(ctx)



del MyGrammarParser
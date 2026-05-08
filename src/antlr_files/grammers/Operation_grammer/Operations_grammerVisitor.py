# Generated from Operations_grammer.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .Operations_grammerParser import Operations_grammerParser
else:
    from Operations_grammerParser import Operations_grammerParser

# This class defines a complete generic visitor for a parse tree produced by Operations_grammerParser.

class Operations_grammerVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by Operations_grammerParser#translation_unit.
    def visitTranslation_unit(self, ctx:Operations_grammerParser.Translation_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#mulDivMod.
    def visitMulDivMod(self, ctx:Operations_grammerParser.MulDivModContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#logicalNot.
    def visitLogicalNot(self, ctx:Operations_grammerParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#parens.
    def visitParens(self, ctx:Operations_grammerParser.ParensContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#shift.
    def visitShift(self, ctx:Operations_grammerParser.ShiftContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#bitwiseXor.
    def visitBitwiseXor(self, ctx:Operations_grammerParser.BitwiseXorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#logicalAnd.
    def visitLogicalAnd(self, ctx:Operations_grammerParser.LogicalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#addSub.
    def visitAddSub(self, ctx:Operations_grammerParser.AddSubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#unary.
    def visitUnary(self, ctx:Operations_grammerParser.UnaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#bitwiseAnd.
    def visitBitwiseAnd(self, ctx:Operations_grammerParser.BitwiseAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#bitwiseNot.
    def visitBitwiseNot(self, ctx:Operations_grammerParser.BitwiseNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#literalExpr.
    def visitLiteralExpr(self, ctx:Operations_grammerParser.LiteralExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#relational.
    def visitRelational(self, ctx:Operations_grammerParser.RelationalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#bitwiseOr.
    def visitBitwiseOr(self, ctx:Operations_grammerParser.BitwiseOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#logicalOr.
    def visitLogicalOr(self, ctx:Operations_grammerParser.LogicalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#equality.
    def visitEquality(self, ctx:Operations_grammerParser.EqualityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Operations_grammerParser#intLiteral.
    def visitIntLiteral(self, ctx:Operations_grammerParser.IntLiteralContext):
        return self.visitChildren(ctx)



del Operations_grammerParser
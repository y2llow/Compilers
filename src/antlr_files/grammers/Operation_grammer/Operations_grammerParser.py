# Generated from Operations_grammer.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,27,67,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,0,4,0,10,8,0,11,0,12,
        0,11,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,
        28,8,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,5,
        1,60,8,1,10,1,12,1,63,9,1,1,2,1,2,1,2,0,1,2,3,0,2,4,0,5,1,0,5,6,
        1,0,2,4,1,0,7,8,1,0,9,12,1,0,13,14,78,0,9,1,0,0,0,2,27,1,0,0,0,4,
        64,1,0,0,0,6,7,3,2,1,0,7,8,5,1,0,0,8,10,1,0,0,0,9,6,1,0,0,0,10,11,
        1,0,0,0,11,9,1,0,0,0,11,12,1,0,0,0,12,13,1,0,0,0,13,14,5,0,0,1,14,
        1,1,0,0,0,15,16,6,1,-1,0,16,17,5,20,0,0,17,28,3,2,1,5,18,19,5,21,
        0,0,19,28,3,2,1,4,20,21,7,0,0,0,21,28,3,2,1,3,22,23,5,22,0,0,23,
        24,3,2,1,0,24,25,5,23,0,0,25,28,1,0,0,0,26,28,3,4,2,0,27,15,1,0,
        0,0,27,18,1,0,0,0,27,20,1,0,0,0,27,22,1,0,0,0,27,26,1,0,0,0,28,61,
        1,0,0,0,29,30,10,15,0,0,30,31,7,1,0,0,31,60,3,2,1,16,32,33,10,14,
        0,0,33,34,7,0,0,0,34,60,3,2,1,15,35,36,10,13,0,0,36,37,7,2,0,0,37,
        60,3,2,1,14,38,39,10,12,0,0,39,40,7,3,0,0,40,60,3,2,1,13,41,42,10,
        11,0,0,42,43,7,4,0,0,43,60,3,2,1,12,44,45,10,10,0,0,45,46,5,15,0,
        0,46,60,3,2,1,11,47,48,10,9,0,0,48,49,5,16,0,0,49,60,3,2,1,10,50,
        51,10,8,0,0,51,52,5,17,0,0,52,60,3,2,1,9,53,54,10,7,0,0,54,55,5,
        18,0,0,55,60,3,2,1,8,56,57,10,6,0,0,57,58,5,19,0,0,58,60,3,2,1,7,
        59,29,1,0,0,0,59,32,1,0,0,0,59,35,1,0,0,0,59,38,1,0,0,0,59,41,1,
        0,0,0,59,44,1,0,0,0,59,47,1,0,0,0,59,50,1,0,0,0,59,53,1,0,0,0,59,
        56,1,0,0,0,60,63,1,0,0,0,61,59,1,0,0,0,61,62,1,0,0,0,62,3,1,0,0,
        0,63,61,1,0,0,0,64,65,5,24,0,0,65,5,1,0,0,0,4,11,27,59,61
    ]

class Operations_grammerParser ( Parser ):

    grammarFileName = "Operations_grammer.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "';'", "'*'", "'/'", "'%'", "'+'", "'-'", 
                     "'<<'", "'>>'", "'<'", "'>'", "'<='", "'>='", "'=='", 
                     "'!='", "'&'", "'^'", "'|'", "'&&'", "'||'", "'!'", 
                     "'~'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "INTEGER", "WS", "COMMENT", "BLOCK_COMMENT" ]

    RULE_translation_unit = 0
    RULE_expression = 1
    RULE_literal = 2

    ruleNames =  [ "translation_unit", "expression", "literal" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    INTEGER=24
    WS=25
    COMMENT=26
    BLOCK_COMMENT=27

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Translation_unitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(Operations_grammerParser.EOF, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def getRuleIndex(self):
            return Operations_grammerParser.RULE_translation_unit

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTranslation_unit" ):
                listener.enterTranslation_unit(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTranslation_unit" ):
                listener.exitTranslation_unit(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTranslation_unit" ):
                return visitor.visitTranslation_unit(self)
            else:
                return visitor.visitChildren(self)




    def translation_unit(self):

        localctx = Operations_grammerParser.Translation_unitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_translation_unit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 6
                self.expression(0)
                self.state = 7
                self.match(Operations_grammerParser.T__0)
                self.state = 11 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 24117344) != 0)):
                    break

            self.state = 13
            self.match(Operations_grammerParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return Operations_grammerParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class MulDivModContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMulDivMod" ):
                listener.enterMulDivMod(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMulDivMod" ):
                listener.exitMulDivMod(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulDivMod" ):
                return visitor.visitMulDivMod(self)
            else:
                return visitor.visitChildren(self)


    class LogicalNotContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalNot" ):
                listener.enterLogicalNot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalNot" ):
                listener.exitLogicalNot(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalNot" ):
                return visitor.visitLogicalNot(self)
            else:
                return visitor.visitChildren(self)


    class ParensContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParens" ):
                listener.enterParens(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParens" ):
                listener.exitParens(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParens" ):
                return visitor.visitParens(self)
            else:
                return visitor.visitChildren(self)


    class ShiftContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterShift" ):
                listener.enterShift(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitShift" ):
                listener.exitShift(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitShift" ):
                return visitor.visitShift(self)
            else:
                return visitor.visitChildren(self)


    class BitwiseXorContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBitwiseXor" ):
                listener.enterBitwiseXor(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBitwiseXor" ):
                listener.exitBitwiseXor(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBitwiseXor" ):
                return visitor.visitBitwiseXor(self)
            else:
                return visitor.visitChildren(self)


    class LogicalAndContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalAnd" ):
                listener.enterLogicalAnd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalAnd" ):
                listener.exitLogicalAnd(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalAnd" ):
                return visitor.visitLogicalAnd(self)
            else:
                return visitor.visitChildren(self)


    class AddSubContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddSub" ):
                listener.enterAddSub(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddSub" ):
                listener.exitAddSub(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddSub" ):
                return visitor.visitAddSub(self)
            else:
                return visitor.visitChildren(self)


    class UnaryContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnary" ):
                listener.enterUnary(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnary" ):
                listener.exitUnary(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnary" ):
                return visitor.visitUnary(self)
            else:
                return visitor.visitChildren(self)


    class BitwiseAndContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBitwiseAnd" ):
                listener.enterBitwiseAnd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBitwiseAnd" ):
                listener.exitBitwiseAnd(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBitwiseAnd" ):
                return visitor.visitBitwiseAnd(self)
            else:
                return visitor.visitChildren(self)


    class BitwiseNotContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBitwiseNot" ):
                listener.enterBitwiseNot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBitwiseNot" ):
                listener.exitBitwiseNot(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBitwiseNot" ):
                return visitor.visitBitwiseNot(self)
            else:
                return visitor.visitChildren(self)


    class LiteralExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def literal(self):
            return self.getTypedRuleContext(Operations_grammerParser.LiteralContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteralExpr" ):
                listener.enterLiteralExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteralExpr" ):
                listener.exitLiteralExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteralExpr" ):
                return visitor.visitLiteralExpr(self)
            else:
                return visitor.visitChildren(self)


    class RelationalContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelational" ):
                listener.enterRelational(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelational" ):
                listener.exitRelational(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelational" ):
                return visitor.visitRelational(self)
            else:
                return visitor.visitChildren(self)


    class BitwiseOrContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBitwiseOr" ):
                listener.enterBitwiseOr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBitwiseOr" ):
                listener.exitBitwiseOr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBitwiseOr" ):
                return visitor.visitBitwiseOr(self)
            else:
                return visitor.visitChildren(self)


    class LogicalOrContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalOr" ):
                listener.enterLogicalOr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalOr" ):
                listener.exitLogicalOr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalOr" ):
                return visitor.visitLogicalOr(self)
            else:
                return visitor.visitChildren(self)


    class EqualityContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Operations_grammerParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(Operations_grammerParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEquality" ):
                listener.enterEquality(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEquality" ):
                listener.exitEquality(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEquality" ):
                return visitor.visitEquality(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = Operations_grammerParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [20]:
                localctx = Operations_grammerParser.LogicalNotContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 16
                self.match(Operations_grammerParser.T__19)
                self.state = 17
                self.expression(5)
                pass
            elif token in [21]:
                localctx = Operations_grammerParser.BitwiseNotContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 18
                self.match(Operations_grammerParser.T__20)
                self.state = 19
                self.expression(4)
                pass
            elif token in [5, 6]:
                localctx = Operations_grammerParser.UnaryContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 20
                _la = self._input.LA(1)
                if not(_la==5 or _la==6):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 21
                self.expression(3)
                pass
            elif token in [22]:
                localctx = Operations_grammerParser.ParensContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 22
                self.match(Operations_grammerParser.T__21)
                self.state = 23
                self.expression(0)
                self.state = 24
                self.match(Operations_grammerParser.T__22)
                pass
            elif token in [24]:
                localctx = Operations_grammerParser.LiteralExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 26
                self.literal()
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 61
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 59
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
                    if la_ == 1:
                        localctx = Operations_grammerParser.MulDivModContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 29
                        if not self.precpred(self._ctx, 15):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 15)")
                        self.state = 30
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 28) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 31
                        self.expression(16)
                        pass

                    elif la_ == 2:
                        localctx = Operations_grammerParser.AddSubContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 32
                        if not self.precpred(self._ctx, 14):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 14)")
                        self.state = 33
                        _la = self._input.LA(1)
                        if not(_la==5 or _la==6):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 34
                        self.expression(15)
                        pass

                    elif la_ == 3:
                        localctx = Operations_grammerParser.ShiftContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 35
                        if not self.precpred(self._ctx, 13):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 13)")
                        self.state = 36
                        _la = self._input.LA(1)
                        if not(_la==7 or _la==8):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 37
                        self.expression(14)
                        pass

                    elif la_ == 4:
                        localctx = Operations_grammerParser.RelationalContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 38
                        if not self.precpred(self._ctx, 12):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 12)")
                        self.state = 39
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 7680) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 40
                        self.expression(13)
                        pass

                    elif la_ == 5:
                        localctx = Operations_grammerParser.EqualityContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 41
                        if not self.precpred(self._ctx, 11):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 11)")
                        self.state = 42
                        _la = self._input.LA(1)
                        if not(_la==13 or _la==14):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 43
                        self.expression(12)
                        pass

                    elif la_ == 6:
                        localctx = Operations_grammerParser.BitwiseAndContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 44
                        if not self.precpred(self._ctx, 10):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 10)")
                        self.state = 45
                        self.match(Operations_grammerParser.T__14)
                        self.state = 46
                        self.expression(11)
                        pass

                    elif la_ == 7:
                        localctx = Operations_grammerParser.BitwiseXorContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 47
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 48
                        self.match(Operations_grammerParser.T__15)
                        self.state = 49
                        self.expression(10)
                        pass

                    elif la_ == 8:
                        localctx = Operations_grammerParser.BitwiseOrContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 50
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 51
                        self.match(Operations_grammerParser.T__16)
                        self.state = 52
                        self.expression(9)
                        pass

                    elif la_ == 9:
                        localctx = Operations_grammerParser.LogicalAndContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 53
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 54
                        self.match(Operations_grammerParser.T__17)
                        self.state = 55
                        self.expression(8)
                        pass

                    elif la_ == 10:
                        localctx = Operations_grammerParser.LogicalOrContext(self, Operations_grammerParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 56
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 57
                        self.match(Operations_grammerParser.T__18)
                        self.state = 58
                        self.expression(7)
                        pass

             
                self.state = 63
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return Operations_grammerParser.RULE_literal

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class IntLiteralContext(LiteralContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a Operations_grammerParser.LiteralContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INTEGER(self):
            return self.getToken(Operations_grammerParser.INTEGER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIntLiteral" ):
                listener.enterIntLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIntLiteral" ):
                listener.exitIntLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIntLiteral" ):
                return visitor.visitIntLiteral(self)
            else:
                return visitor.visitChildren(self)



    def literal(self):

        localctx = Operations_grammerParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_literal)
        try:
            localctx = Operations_grammerParser.IntLiteralContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.match(Operations_grammerParser.INTEGER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 15)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 14)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 13)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 12)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 11)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 10)
         

            if predIndex == 6:
                return self.precpred(self._ctx, 9)
         

            if predIndex == 7:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 8:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 9:
                return self.precpred(self._ctx, 6)
         





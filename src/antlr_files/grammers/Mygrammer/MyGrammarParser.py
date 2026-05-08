# Generated from MyGrammar.g4 by ANTLR 4.13.2
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
        4,1,14,67,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,1,0,4,0,20,8,0,11,0,12,0,21,1,1,1,1,1,1,1,1,1,
        1,1,1,1,2,1,2,1,3,1,3,5,3,34,8,3,10,3,12,3,37,9,3,1,3,1,3,1,4,1,
        4,1,4,3,4,44,8,4,1,5,1,5,3,5,48,8,5,1,5,1,5,1,6,1,6,1,6,1,6,3,6,
        56,8,6,1,6,1,6,1,7,3,7,61,8,7,1,7,1,7,1,8,1,8,1,8,0,0,9,0,2,4,6,
        8,10,12,14,16,0,2,1,0,3,4,1,0,10,11,64,0,19,1,0,0,0,2,23,1,0,0,0,
        4,29,1,0,0,0,6,31,1,0,0,0,8,43,1,0,0,0,10,45,1,0,0,0,12,51,1,0,0,
        0,14,60,1,0,0,0,16,64,1,0,0,0,18,20,3,2,1,0,19,18,1,0,0,0,20,21,
        1,0,0,0,21,19,1,0,0,0,21,22,1,0,0,0,22,1,1,0,0,0,23,24,3,4,2,0,24,
        25,5,10,0,0,25,26,5,1,0,0,26,27,5,2,0,0,27,28,3,6,3,0,28,3,1,0,0,
        0,29,30,7,0,0,0,30,5,1,0,0,0,31,35,5,5,0,0,32,34,3,8,4,0,33,32,1,
        0,0,0,34,37,1,0,0,0,35,33,1,0,0,0,35,36,1,0,0,0,36,38,1,0,0,0,37,
        35,1,0,0,0,38,39,5,6,0,0,39,7,1,0,0,0,40,44,3,10,5,0,41,44,3,12,
        6,0,42,44,3,14,7,0,43,40,1,0,0,0,43,41,1,0,0,0,43,42,1,0,0,0,44,
        9,1,0,0,0,45,47,5,7,0,0,46,48,3,16,8,0,47,46,1,0,0,0,47,48,1,0,0,
        0,48,49,1,0,0,0,49,50,5,8,0,0,50,11,1,0,0,0,51,52,3,4,2,0,52,55,
        5,10,0,0,53,54,5,9,0,0,54,56,3,16,8,0,55,53,1,0,0,0,55,56,1,0,0,
        0,56,57,1,0,0,0,57,58,5,8,0,0,58,13,1,0,0,0,59,61,3,16,8,0,60,59,
        1,0,0,0,60,61,1,0,0,0,61,62,1,0,0,0,62,63,5,8,0,0,63,15,1,0,0,0,
        64,65,7,1,0,0,65,17,1,0,0,0,6,21,35,43,47,55,60
    ]

class MyGrammarParser ( Parser ):

    grammarFileName = "MyGrammar.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "'int'", "'void'", "'{'", 
                     "'}'", "'return'", "';'", "'='" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "IDENTIFIER", "NUMBER", 
                      "WS", "COMMENT", "BLOCK_COMMENT" ]

    RULE_translation_unit = 0
    RULE_function_definition = 1
    RULE_type_specifier = 2
    RULE_compound_statement = 3
    RULE_statement = 4
    RULE_return_statement = 5
    RULE_declaration_statement = 6
    RULE_expression_statement = 7
    RULE_expression = 8

    ruleNames =  [ "translation_unit", "function_definition", "type_specifier", 
                   "compound_statement", "statement", "return_statement", 
                   "declaration_statement", "expression_statement", "expression" ]

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
    IDENTIFIER=10
    NUMBER=11
    WS=12
    COMMENT=13
    BLOCK_COMMENT=14

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

        def function_definition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.Function_definitionContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.Function_definitionContext,i)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_translation_unit

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

        localctx = MyGrammarParser.Translation_unitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_translation_unit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 18
                self.function_definition()
                self.state = 21 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==3 or _la==4):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_definitionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def type_specifier(self):
            return self.getTypedRuleContext(MyGrammarParser.Type_specifierContext,0)


        def IDENTIFIER(self):
            return self.getToken(MyGrammarParser.IDENTIFIER, 0)

        def compound_statement(self):
            return self.getTypedRuleContext(MyGrammarParser.Compound_statementContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_function_definition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_definition" ):
                listener.enterFunction_definition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_definition" ):
                listener.exitFunction_definition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunction_definition" ):
                return visitor.visitFunction_definition(self)
            else:
                return visitor.visitChildren(self)




    def function_definition(self):

        localctx = MyGrammarParser.Function_definitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_function_definition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 23
            self.type_specifier()
            self.state = 24
            self.match(MyGrammarParser.IDENTIFIER)
            self.state = 25
            self.match(MyGrammarParser.T__0)
            self.state = 26
            self.match(MyGrammarParser.T__1)
            self.state = 27
            self.compound_statement()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_specifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return MyGrammarParser.RULE_type_specifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterType_specifier" ):
                listener.enterType_specifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitType_specifier" ):
                listener.exitType_specifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitType_specifier" ):
                return visitor.visitType_specifier(self)
            else:
                return visitor.visitChildren(self)




    def type_specifier(self):

        localctx = MyGrammarParser.Type_specifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_type_specifier)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            _la = self._input.LA(1)
            if not(_la==3 or _la==4):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compound_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.StatementContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.StatementContext,i)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_compound_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompound_statement" ):
                listener.enterCompound_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompound_statement" ):
                listener.exitCompound_statement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompound_statement" ):
                return visitor.visitCompound_statement(self)
            else:
                return visitor.visitChildren(self)




    def compound_statement(self):

        localctx = MyGrammarParser.Compound_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_compound_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            self.match(MyGrammarParser.T__4)
            self.state = 35
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3480) != 0):
                self.state = 32
                self.statement()
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 38
            self.match(MyGrammarParser.T__5)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def return_statement(self):
            return self.getTypedRuleContext(MyGrammarParser.Return_statementContext,0)


        def declaration_statement(self):
            return self.getTypedRuleContext(MyGrammarParser.Declaration_statementContext,0)


        def expression_statement(self):
            return self.getTypedRuleContext(MyGrammarParser.Expression_statementContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = MyGrammarParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_statement)
        try:
            self.state = 43
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [7]:
                self.enterOuterAlt(localctx, 1)
                self.state = 40
                self.return_statement()
                pass
            elif token in [3, 4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 41
                self.declaration_statement()
                pass
            elif token in [8, 10, 11]:
                self.enterOuterAlt(localctx, 3)
                self.state = 42
                self.expression_statement()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Return_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(MyGrammarParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_return_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturn_statement" ):
                listener.enterReturn_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturn_statement" ):
                listener.exitReturn_statement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReturn_statement" ):
                return visitor.visitReturn_statement(self)
            else:
                return visitor.visitChildren(self)




    def return_statement(self):

        localctx = MyGrammarParser.Return_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_return_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            self.match(MyGrammarParser.T__6)
            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==10 or _la==11:
                self.state = 46
                self.expression()


            self.state = 49
            self.match(MyGrammarParser.T__7)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Declaration_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def type_specifier(self):
            return self.getTypedRuleContext(MyGrammarParser.Type_specifierContext,0)


        def IDENTIFIER(self):
            return self.getToken(MyGrammarParser.IDENTIFIER, 0)

        def expression(self):
            return self.getTypedRuleContext(MyGrammarParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_declaration_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclaration_statement" ):
                listener.enterDeclaration_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclaration_statement" ):
                listener.exitDeclaration_statement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeclaration_statement" ):
                return visitor.visitDeclaration_statement(self)
            else:
                return visitor.visitChildren(self)




    def declaration_statement(self):

        localctx = MyGrammarParser.Declaration_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_declaration_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.type_specifier()
            self.state = 52
            self.match(MyGrammarParser.IDENTIFIER)
            self.state = 55
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==9:
                self.state = 53
                self.match(MyGrammarParser.T__8)
                self.state = 54
                self.expression()


            self.state = 57
            self.match(MyGrammarParser.T__7)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Expression_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(MyGrammarParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_expression_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_statement" ):
                listener.enterExpression_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_statement" ):
                listener.exitExpression_statement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression_statement" ):
                return visitor.visitExpression_statement(self)
            else:
                return visitor.visitChildren(self)




    def expression_statement(self):

        localctx = MyGrammarParser.Expression_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_expression_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 60
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==10 or _la==11:
                self.state = 59
                self.expression()


            self.state = 62
            self.match(MyGrammarParser.T__7)
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

        def NUMBER(self):
            return self.getToken(MyGrammarParser.NUMBER, 0)

        def IDENTIFIER(self):
            return self.getToken(MyGrammarParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = MyGrammarParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            _la = self._input.LA(1)
            if not(_la==10 or _la==11):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






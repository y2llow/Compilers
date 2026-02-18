from antlr_files.MyGrammarVisitor import MyGrammarVisitor
from parser.ast_nodes import (
    ProgramNode, FunctionNode, CompoundStatementNode,
    ReturnStatementNode, DeclarationStatementNode,
    NumberNode, IdentifierNode
)

class ASTBuilder(MyGrammarVisitor):
    """
    Visits the ANTLR parse tree and builds our AST.
    Each visit method returns an AST node.
    """

    def visitTranslation_unit(self, ctx):
        # Collect all function definitions
        functions = [self.visit(f) for f in ctx.function_definition()]
        return ProgramNode(functions)

    def visitFunction_definition(self, ctx):
        return_type = ctx.type_specifier().getText()
        name = ctx.IDENTIFIER().getText()
        body = self.visit(ctx.compound_statement())
        return FunctionNode(return_type, name, body)

    def visitCompound_statement(self, ctx):
        statements = [self.visit(s) for s in ctx.statement()]
        return CompoundStatementNode(statements)

    def visitStatement(self, ctx):
        # A statement is one of three options, visit whichever child is present
        if ctx.return_statement():
            return self.visit(ctx.return_statement())
        elif ctx.declaration_statement():
            return self.visit(ctx.declaration_statement())
        elif ctx.expression_statement():
            return self.visit(ctx.expression_statement())

    def visitReturn_statement(self, ctx):
        # expression is optional (e.g. 'return;' in void functions)
        expr = self.visit(ctx.expression()) if ctx.expression() else None
        return ReturnStatementNode(expr)

    def visitDeclaration_statement(self, ctx):
        var_type = ctx.type_specifier().getText()
        name = ctx.IDENTIFIER().getText()
        value = self.visit(ctx.expression()) if ctx.expression() else None
        return DeclarationStatementNode(var_type, name, value)

    def visitExpression_statement(self, ctx):
        # For now just visit the expression if there is one
        if ctx.expression():
            return self.visit(ctx.expression())
        return None

    def visitExpression(self, ctx):
        if ctx.NUMBER():
            return NumberNode(ctx.NUMBER().getText())
        elif ctx.IDENTIFIER():
            return IdentifierNode(ctx.IDENTIFIER().getText())
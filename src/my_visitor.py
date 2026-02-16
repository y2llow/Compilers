# my_visitor.py
from antlr_files.MyGrammarVisitor import MyGrammarVisitor

class MyCustomVisitor(MyGrammarVisitor):
    """
    Custom visitor to analyse the parse tree.
    Override only the methods you need.
    """

    def visitTranslation_unit(self, ctx):
        print("Visiting a translation unit")
        return self.visitChildren(ctx)

    def visitDeclaration(self, ctx):
        # Example: print declared identifiers
        decl_list = ctx.init_declarator_list()
        if decl_list:
            for init_decl in decl_list.init_declarator():
                name = init_decl.IDENTIFIER().getText()
                print(f"Declared variable: {name}")
        return self.visitChildren(ctx)

    def visitExpression(self, ctx):
        # Example: print simple assignments
        target = ctx.IDENTIFIER()
        value = ctx.CONSTANT()
        if target and value:
            print(f"{target.getText()} = {value.getText()}")
        return self.visitChildren(ctx)

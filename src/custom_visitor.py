from antlr_files.MyGrammarVisitor import MyGrammarVisitor
from antlr_files.MyGrammarParser import MyGrammarParser


class MyCustomVisitor(MyGrammarVisitor):
    def visitStartRule(self, ctx: MyGrammarParser.StartRuleContext):
        # Your custom logic here
        return self.visitChildren(ctx)

    # Override other visit methods as needed
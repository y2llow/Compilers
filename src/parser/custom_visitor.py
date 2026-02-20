from src.antlr_files.grammers.Operation_grammer.Operations_grammerVisitor import Operations_grammerVisitor
from src.antlr_files.grammers.Operation_grammer.Operations_grammerParser import Operations_grammerParser


class MyCustomVisitor(Operations_grammerVisitor):
    def visitStartRule(self, ctx: Operations_grammerParser.StartRuleContext):
        # Your custom logic here
        return self.visitChildren(ctx)

    # Override other visit methods as needed
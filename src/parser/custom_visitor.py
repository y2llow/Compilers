from antlr_files.grammers.CParser.CParserVisitor import CParserVisitor
from antlr_files.grammers.CParser.CParserParser import CParserParser


class MyCustomVisitor(CParserVisitor):
    def visitStartRule(self, ctx: CParserParser.StartRuleContext):
        # Your custom logic here
        return self.visitChildren(ctx)

    # Override other visit methods as needed
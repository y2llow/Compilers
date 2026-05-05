"""
Include processor - replaces IncludeNode with parsed file contents
Respects include guards to prevent double inclusion
IMPORTANT: Preserves system includes (#include <...>) and #define statements!
"""

import antlr4
from antlr_files.grammers.CParser.CParserLexer import CParserLexer
from antlr_files.grammers.CParser.CParserParser import CParserParser
from parser.ast_builder import ASTBuilder
from parser.ast_nodes import ProgramNode, IncludeNode, DefineNode
from parser.comment_collector import CommentCollector


class IncludeProcessor:
    """Processes #include directives in the AST, respecting include guards."""

    def __init__(self, include_handler, source_lines=None):
        self.include_handler = include_handler
        self.source_lines = source_lines or []

    def process(self, node: ProgramNode) -> ProgramNode:
        """
        Process all #include in the AST, recursively.

        IMPORTANT:
        - System includes (<stdio.h>) are KEPT (not removed)
        - #define statements are KEPT (not removed)
        - Only LOCAL includes ("file.h") are replaced with file contents
        - Includes found inside included files are also processed (recursive)
        """
        node.top_level_items = self._process_items(node.top_level_items)
        return node

    def _process_items(self, items: list) -> list:
        """
        Expand all local IncludeNodes in a list of AST items.
        Recursively expands any includes found inside included files.
        """
        new_items = []

        for item in items:
            if isinstance(item, IncludeNode):
                if item.is_system:
                    new_items.append(item)
                    continue
                # Parse the included file into AST items ...
                included_items = self._process_include(item)
                # ... then recursively expand any includes inside those items
                expanded = self._process_items(included_items)
                new_items.extend(expanded)
            elif isinstance(item, DefineNode):
                new_items.append(item)
            else:
                new_items.append(item)

        return new_items

    def _process_include(self, include_node: IncludeNode) -> list:
        """Read and parse a LOCAL (non-system) included file."""
        file_contents = self.include_handler.read_include(
            include_node.header,
            include_node.is_system
        )

        if not file_contents:
            return []

        return self._parse_contents(file_contents)

    def _parse_contents(self, contents: str) -> list:
        """Parse file contents and return AST nodes."""

        contents_lines = contents.split('\n')

        # Step 1: parse with a dedicated stream.
        # Do NOT share this stream with CommentCollector — the parser fills
        # ctx.children as it consumes tokens, so any prior read of the same
        # stream leaves it exhausted and produces ctx.children == None.
        parse_input = antlr4.InputStream(contents)
        parse_lexer = CParserLexer(parse_input)
        parse_lexer.removeErrorListeners()
        parse_stream = antlr4.CommonTokenStream(parse_lexer)

        parse_parser = CParserParser(parse_stream)
        parse_parser.removeErrorListeners()

        try:
            tree = parse_parser.translation_unit()
        except Exception:
            return []

        # Step 2: separate stream for CommentCollector.
        # ASTBuilder walks the parse tree (built above) for structure and uses
        # the comment collector only for comment attachment, so the two streams
        # don't interfere.
        cc_input = antlr4.InputStream(contents)
        cc_lexer = CParserLexer(cc_input)
        cc_lexer.removeErrorListeners()
        cc_stream = antlr4.CommonTokenStream(cc_lexer)
        cc_stream.fill()

        comment_collector = CommentCollector(cc_stream, contents_lines)
        try:
            comment_collector.collect()
        except Exception:
            pass

        # Step 3: build AST from the already-complete parse tree.
        try:
            ast = ASTBuilder(comment_collector, contents_lines).visit(tree)
        except Exception:
            return []

        if isinstance(ast, ProgramNode):
            return ast.top_level_items

        return []
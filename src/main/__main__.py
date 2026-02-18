import sys
import antlr4

from antlr_files.MyGrammarLexer import MyGrammarLexer
from antlr_files.MyGrammarParser import MyGrammarParser
from parser.ast_builder import ASTBuilder

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m main <source_file.c>")
        sys.exit(1)

    input_stream = antlr4.FileStream(sys.argv[1])

    # Step 1: Lex
    lexer = MyGrammarLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)

    # Step 2: Parse
    parser = MyGrammarParser(token_stream)
    tree = parser.translation_unit()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors found, stopping.")
        sys.exit(1)

    # Step 3: Build AST
    builder = ASTBuilder()
    ast = builder.visit(tree)

    # Print the AST for debugging
    print(ast)

if __name__ == '__main__':
    main()
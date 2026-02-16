# main.py
import sys
from antlr4 import *
from antlr_files.MyGrammarLexer import MyGrammarLexer
from antlr_files.MyGrammarParser import MyGrammarParser
from my_visitor import MyCustomVisitor  # import your subclass

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source.c>")
        return

    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        code = f.read()

    input_stream = InputStream(code)
    lexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = MyGrammarParser(stream)

    tree = parser.translation_unit()

    visitor = MyCustomVisitor()
    visitor.visit(tree)

    print("Parsing completed successfully.")

if __name__ == "__main__":
    main()

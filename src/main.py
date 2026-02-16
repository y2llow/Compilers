import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from antlr4 import *
from src.antlr_files.MyGrammarLexer import MyGrammarLexer
from src.antlr_files.MyGrammarParser import MyGrammarParser
from src.antlr_files.MyGrammarVisitor import MyGrammarVisitor


class SimpleVisitor(MyGrammarVisitor):
    """Simple visitor to demonstrate parsing"""

    def __init__(self):
        self.indent = 0

    def print_indent(self, text):
        print("  " * self.indent + text)

    def visitFunction_definition(self, ctx):
        return_type = ctx.type_specifier().getText()
        func_name = ctx.IDENTIFIER().getText()
        self.print_indent(f"Function: {return_type} {func_name}()")
        self.indent += 1
        self.visit(ctx.compound_statement())
        self.indent -= 1
        return None

    def visitDeclaration_statement(self, ctx):
        var_type = ctx.type_specifier().getText()
        var_name = ctx.IDENTIFIER().getText()
        if ctx.expression():
            value = ctx.expression().getText()
            self.print_indent(f"Declaration: {var_type} {var_name} = {value}")
        else:
            self.print_indent(f"Declaration: {var_type} {var_name}")
        return None

    def visitReturn_statement(self, ctx):
        if ctx.expression():
            value = ctx.expression().getText()
            self.print_indent(f"Return: {value}")
        else:
            self.print_indent(f"Return: (void)")
        return None


def main():
    parser = argparse.ArgumentParser(description='Simple C Compiler')
    parser.add_argument('--input', required=True, help='Input C file')
    parser.add_argument('--render_ast', help='Output AST (not implemented yet)')
    parser.add_argument('--target_llvm', help='Output LLVM IR (not implemented yet)')

    args = parser.parse_args()

    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: File '{args.input}' not found")
        return 1

    with open(input_path, 'r') as f:
        source_code = f.read()

    print(f"📄 Compiling: {args.input}")
    print("=" * 50)
    print(source_code)
    print("=" * 50)

    # Parse the code
    input_stream = InputStream(source_code)
    lexer = MyGrammarLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser_obj = MyGrammarParser(token_stream)

    # Get parse tree
    try:
        parse_tree = parser_obj.translation_unit()
    except Exception as e:
        print(f"❌ Parse Error: {e}")
        return 1

    print("\n✅ Parsing successful!")
    print("\n📊 Parse Tree Analysis:")
    print("-" * 50)

    # Visit the tree
    visitor = SimpleVisitor()
    visitor.visit(parse_tree)

    print("-" * 50)
    print("\n✅ Compilation completed successfully!")

    if args.render_ast:
        print(f"\n⚠️  AST rendering not yet implemented")
    if args.target_llvm:
        print(f"\n⚠️  LLVM generation not yet implemented")

    return 0


if __name__ == '__main__':
    sys.exit(main())
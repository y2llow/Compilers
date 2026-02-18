import sys
import argparse
import antlr4

from antlr_files.grammers.Operation_grammer.Operations_grammerLexer import Operations_grammerLexer
from antlr_files.grammers.Operation_grammer.Operations_grammerParser import Operations_grammerParser
from parser.ast_builder import ASTBuilder
from parser.constant_folder import ConstantFolder
from parser.dot_visitor import DotVisitor


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("source_file")
    arg_parser.add_argument(
        "--no-fold",
        action="store_true",
        help="Disable constant folding (useful for testing/debugging)"
    )
    arg_parser.add_argument(
        "--dot",
        metavar="OUTPUT.dot",
        help="Write the AST in Graphviz dot format to this file"
    )
    args = arg_parser.parse_args()

    input_stream = antlr4.FileStream(args.source_file)

    # Step 1: Lex
    lexer = Operations_grammerLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)

    # Step 2: Parse
    parser = Operations_grammerParser(token_stream)
    tree = parser.translation_unit()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors found, stopping.")
        sys.exit(1)

    # Step 3: Build AST
    ast = ASTBuilder().visit(tree)
    print("=== AST before folding ===")
    print(ast)

    # Step 4: Constant folding (pass --no-fold to skip)
    ast = ConstantFolder(enabled=not args.no_fold).visit(ast)
    print("\n=== AST after folding ===")
    print(ast)

    # Step 5: Graphviz dot output (pass --dot output.dot to enable)
    if args.dot:
        dot_string = DotVisitor().visit(ast)
        with open(args.dot, "w") as f:
            f.write(dot_string)
        print(f"\nDot file written to: {args.dot}")
        print(f"Visualise with:      xdot {args.dot}")
        print(f"Export PNG with:     dot -Tpng {args.dot} -o ast.png")


if __name__ == '__main__':
    main()
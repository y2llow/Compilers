import sys
import argparse
import antlr4

from antlr_files.grammers.CParser.CParserLexer import CParserLexer
from antlr_files.grammers.CParser.CParserParser import CParserParser
from parser.ast_builder import ASTBuilder
from parser.constant_folder import ConstantFolder
from parser.dot_visitor import DotVisitor
from parser.error_handler import SyntaxErrorListener, RED, RESET
from parser.semantics.semantic_analyser import SemanticAnalyzer
from parser.comment_collector import CommentCollector



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
    arg_parser.add_argument(
        "--target_llvm",
        metavar="OUTPUT.ll",
        help="Generate LLVM IR code to this file"
    )
    args = arg_parser.parse_args()

    # Read source file for error reporting
    with open(args.source_file, 'r') as f:
        source_lines = f.readlines()

    input_stream = antlr4.FileStream(args.source_file)

    # Step 1: Lex
    lexer = CParserLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    # Step 1.5: Collect comments
    comment_collector = CommentCollector(token_stream, source_lines)
    comment_collector.collect()

    # Step 2: Parse
    parser = CParserParser(token_stream)

    # Setup error listener for nice error messages
    error_listener = SyntaxErrorListener(source_lines)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.translation_unit()

    # Check for syntax errors
    if error_listener.has_errors():
        formatted_output, error_count = error_listener.format_errors()
        print(formatted_output)
        print(f"{RED}Compilation failed with {error_count} syntax error(s).{RESET}")
        sys.exit(1)

    # Step 3: Build AST
    ast = ASTBuilder(comment_collector, source_lines).visit(tree)
    print("=== AST before semantic analysis ===")
    print(ast)
    print()

    # Step 3.5: Semantic Analysis
    print("=== Semantic Analysis ===")
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    # Print semantic errors
    if analyzer.errors:
        error_output, error_count = analyzer.format_errors()
        print(error_output)
        print(f"{RED}Compilation failed with {error_count} semantic error(s).{RESET}")
        sys.exit(1)

    # Print semantic warnings
    if analyzer.warnings:
        warning_output, warning_count = analyzer.format_warnings()
        print(warning_output)

    if not analyzer.errors:
        print(f"Semantic analysis passed ✓")
    print()

    # Step 4: Constant folding (pass --no-fold to skip)
    ast = ConstantFolder(enabled=not args.no_fold).visit(ast)
    print("=== AST after folding ===")
    print(ast)
    print()

    # Step 5: LLVM IR Generation (if requested)
    if args.target_llvm:
        from llvm_target.llvm_generator import LLVMGenerator

        print("=== LLVM IR Generation ===")
        llvm_gen = LLVMGenerator()
        llvm_ir = llvm_gen.generate(ast)

        with open(args.target_llvm, 'w') as f:
            f.write(llvm_ir)

        print(f"✅ LLVM IR written to: {args.target_llvm}")
        print(f"Test with: lli {args.target_llvm}")
        print(f"           echo $?")
        print()

    # Step 6: Graphviz dot output (pass --dot output.dot to enable)
    if args.dot:
        dot_string = DotVisitor().visit(ast)
        with open(args.dot, "w") as f:
            f.write(dot_string)
        print(f"Dot file written to: {args.dot}")
        print(f"Visualise with:      xdot {args.dot}")
        print(f"Export PNG with:     dot -Tpng {args.dot} -o ast.png")


if __name__ == '__main__':
    main()
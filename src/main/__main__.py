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
    arg_parser.add_argument("--no-fold", action="store_true")
    arg_parser.add_argument("--dot", metavar="OUTPUT.dot")
    arg_parser.add_argument("--target_llvm", metavar="OUTPUT.ll")
    args = arg_parser.parse_args()

    with open(args.source_file, 'r') as f:
        source_lines = f.readlines()

    input_stream = antlr4.FileStream(args.source_file)

    lexer = CParserLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)

    error_listener = SyntaxErrorListener(source_lines)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    parser = CParserParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    comment_input = antlr4.FileStream(args.source_file)
    comment_lexer = CParserLexer(comment_input)
    comment_lexer.removeErrorListeners()
    comment_token_stream = antlr4.CommonTokenStream(comment_lexer)
    comment_collector = CommentCollector(comment_token_stream, source_lines)
    try:
        comment_collector.collect()
    except Exception:
        pass

    tree = None
    try:
        tree = parser.translation_unit()
    except Exception:
        pass

    if error_listener.has_errors():
        formatted_output, error_count = error_listener.format_errors()
        print(formatted_output)
        print(f"{RED}Compilation failed with {error_count} syntax error(s).{RESET}")
        sys.exit(1)

    ast = ASTBuilder(comment_collector, source_lines).visit(tree)
    print("=== AST before semantic analysis ===")
    print(ast)
    print()

    print("=== Semantic Analysis ===")
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if analyzer.errors:
        error_output, error_count = analyzer.format_errors()
        print(error_output)
        print(f"{RED}Compilation failed with {error_count} semantic error(s).{RESET}")
        sys.exit(1)

    if analyzer.warnings:
        warning_output, warning_count = analyzer.format_warnings()
        print(warning_output)

    if not analyzer.errors:
        print(f"Semantic analysis passed ✓")
    print()

    ast = ConstantFolder(enabled=not args.no_fold).visit(ast)
    print("=== AST after folding ===")
    print(ast)
    print()

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

    if args.dot:
        dot_string = DotVisitor().visit(ast)
        with open(args.dot, "w") as f:
            f.write(dot_string)
        print(f"Dot file written to: {args.dot}")
        print(f"Visualise with:      xdot {args.dot}")
        print(f"Export PNG with:     dot -Tpng {args.dot} -o ast.png")


if __name__ == '__main__':
    main()
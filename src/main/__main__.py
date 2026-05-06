import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
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
    arg_parser.add_argument("--input", required=True, metavar="INPUT.c",
                            help="Path to the C source file")
    arg_parser.add_argument("--no-fold", action="store_true",
                            help="Disable constant folding")
    arg_parser.add_argument("--no-dce", action="store_true",
                            help="Disable dead code elimination")
    arg_parser.add_argument("--no-dce-unused-vars", action="store_true",
                            help="Disable unused-variable elimination (part of DCE)")
    arg_parser.add_argument("--no-dce-dead-cond", action="store_true",
                            help="Disable dead-conditional elimination (part of DCE)")
    arg_parser.add_argument("--render_ast", metavar="OUTPUT.dot",
                            help="Render AST to a Graphviz dot file")
    arg_parser.add_argument("--render_symb", metavar="OUTPUT.dot",
                            help="Render symbol table to a Graphviz dot file")
    arg_parser.add_argument("--target_llvm", metavar="OUTPUT.ll",
                            help="Compile to LLVM IR")
    arg_parser.add_argument("--target_mips", metavar="OUTPUT.mips",
                            help="Compile to MIPS assembly")
    arg_parser.add_argument("--target_bin", metavar="OUTPUT",
                            help="Compile to native binary")
    args = arg_parser.parse_args()

    # ── Bronbestand lezen ─────────────────────────────────────
    with open(args.input, 'r') as f:
        source_lines = f.readlines()

    # ── Lexer en parser opzetten ──────────────────────────────
    input_stream = antlr4.FileStream(args.input)

    lexer = CParserLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)

    error_listener = SyntaxErrorListener(source_lines)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    parser = CParserParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    # ── Comment collector opzetten ────────────────────────────
    comment_input = antlr4.FileStream(args.input)
    comment_lexer = CParserLexer(comment_input)
    comment_lexer.removeErrorListeners()
    comment_token_stream = antlr4.CommonTokenStream(comment_lexer)
    comment_collector = CommentCollector(comment_token_stream, source_lines)
    try:
        comment_collector.collect()
    except Exception:
        pass

    # ── Parsen ────────────────────────────────────────────────
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

    # ── AST bouwen ────────────────────────────────────────────
    builder = ASTBuilder(comment_collector, source_lines)
    ast = builder.visit(tree)

    if builder.syntax_errors:
        for err in builder.syntax_errors:
            print(f"{RED}[Syntax Error] line {err['line']}, column {err['column']}: {err['message']}{RESET}")
        print(f"{RED}Compilation failed with {len(builder.syntax_errors)} syntax error(s).{RESET}")
        sys.exit(1)

    print("=== AST before include processing ===")
    print(ast)
    print()

    # ── Include processing (mandatory) ────────────────────────
    print("=== Processing #include directives ===")
    try:
        from parser.preprocessor.include_handler import IncludeHandler
        from parser.preprocessor.include_processor import IncludeProcessor

        include_handler = IncludeHandler(args.input)

        # Create a shared typedef registry
        typedef_registry = {}

        # Pass it to IncludeProcessor
        include_processor = IncludeProcessor(
            include_handler,
            source_lines,
            typedef_registry
        )
        ast = include_processor.process(ast)

        if typedef_registry:
            print(f"  Found {len(typedef_registry)} typedef(s) in includes")

    except Exception as e:
        print(f"⚠ Include processing skipped: {e}")
    print()

    print("=== AST after include processing ===")
    print(ast)
    print()

    # ── #define preprocessing ──────────────────────────────────
    print("=== Processing #define statements ===")
    try:
        try:
            from parser.preprocessor.preprocessor import Preprocessor
        except ImportError:
            from parser.preprocessor import Preprocessor

        ast = Preprocessor().preprocess(ast)
        print("✓ Define processing completed")
    except Exception as e:
        import traceback
        print(f"⚠ Preprocessor failed: {e}")
        traceback.print_exc()
    print()

    print("=== AST after define processing ===")
    print(ast)
    print()

    # ── num preprocessing ───────────────────────────────────
    print("=== Processing enum constants ===")
    try:
        from parser.preprocessor.enum_processor import EnumProcessor

        ast = EnumProcessor().process(ast)
        print("? Enum processing completed")
    except Exception as e:
        import traceback
        print(f"? Enum processing failed: {e}")
        traceback.print_exc()
    print()

    print("=== AST after enum processing ===")
    print(ast)
    print()

    # ── Semantische analyse ───────────────────────────────────
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

    print("Semantic analysis passed ✓")
    print()

    # ── Constant folding ──────────────────────────────────────
    # Must run BEFORE dead-code elimination so that constant conditions
    # (e.g. `if (2 - 2)`) are already reduced to integer literals by the
    # time the DCE sees them.
    ast = ConstantFolder(enabled=not args.no_fold).visit(ast)

    print("=== AST after constant folding ===")
    print(ast)
    print()

    # ── Dead code elimination ─────────────────────────────────
    if not args.no_dce:
        from parser.optimizations.dead_code_eliminator import DeadCodeEliminator

        dce = DeadCodeEliminator(
            unused_vars=not args.no_dce_unused_vars,
            dead_conditionals=not args.no_dce_dead_cond,
        )
        ast = dce.visit(ast)

        if dce.warnings:
            print("=== Dead Code Elimination warnings ===")
            for w in dce.warnings:
                print(f"  {w}")
            print()

    print("=== AST after dead code elimination ===")
    print(ast)
    print()

    # ── LLVM IR generatie ─────────────────────────────────────
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

    # ── AST dot visualisatie ──────────────────────────────────
    if args.render_ast:
        dot_string = DotVisitor().visit(ast)
        with open(args.render_ast, "w") as f:
            f.write(dot_string)
        print(f"AST dot file written to: {args.render_ast}")
        print(f"Visualise with:          xdot {args.render_ast}")
        print(f"Export PNG with:         dot -Tpng {args.render_ast} -o ast.png")

    # ── Symbol table dot visualisatie ─────────────────────────
    if args.render_symb:
        dot_lines = ['digraph SymbolTable {', '    node [fontname="Helvetica"];']
        for i, scope in enumerate(analyzer.symbol_table.scopes):
            scope_id = f"scope{i}"
            dot_lines.append(f'    {scope_id} [label="Scope {i}", shape=rectangle];')
            for name, sym in scope.items():
                sym_id = f"sym_{i}_{name}"
                const = "const " if sym.is_const else ""
                stars = '*' * sym.pointer_depth
                dims = ''.join([f'[{d}]' for d in sym.array_dimensions])
                label = f"{const}{sym.type_name}{stars} {sym.name}{dims}"
                dot_lines.append(f'    {sym_id} [label="{label}", shape=ellipse];')
                dot_lines.append(f'    {scope_id} -> {sym_id};')
        dot_lines.append('}')
        with open(args.render_symb, "w") as f:
            f.write('\n'.join(dot_lines))
        print(f"Symbol table dot file written to: {args.render_symb}")

    # ── MIPS ──────────────────────────────────────────────────
    if args.target_mips:
        print("⚠️  MIPS target not yet implemented.")

    # ── Binary ────────────────────────────────────────────────
    if args.target_bin:
        print("⚠️  Binary target not yet implemented.")


if __name__ == '__main__':
    main()
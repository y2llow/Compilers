#!/usr/bin/env python3
"""
Compiler Test Runner
====================
For every .c file in src/antlr_files/example_source_files/ this script runs:

    python -m main <file.c> --dot ast.dot
    python -m main <file.c> --target_llvm output.ll

And optionally renders the .dot file to PNG if Graphviz is installed.

Output layout
-------------
test_output/
  <stem>/
    ast.dot              – AST in Graphviz dot format
    ast.png              – PNG render  (if `dot` binary is available)
    output.ll            – LLVM IR     (only when compilation succeeds)
    compiler_ast.txt     – stdout/stderr from the --dot run
    compiler_llvm.txt    – stdout/stderr from the --target_llvm run
  summary.txt            – CSV: file,ast_status,llvm_status

Usage
-----
    python run_tests.py                        # default paths
    python run_tests.py --out my_output_dir    # custom output dir
    python run_tests.py --src path/to/c/files  # custom source dir
"""

import argparse
import subprocess
import sys
from pathlib import Path


# ── ANSI colours ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✔{RESET}  {msg}")
def fail(msg): print(f"  {RED}✘{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}⚠{RESET}  {msg}")
def info(msg): print(f"  {CYAN}→{RESET}  {msg}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def dot_available() -> bool:
    return subprocess.run(["dot", "-V"], capture_output=True).returncode == 0


def render_png(dot_file: Path, png_file: Path) -> bool:
    result = subprocess.run(
        ["dot", "-Tpng", str(dot_file), "-o", str(png_file)],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def run_compiler(args: list, cwd: Path, log_file: Path) -> tuple:
    """
    Run: python -m main <args>
    Saves combined stdout+stderr to log_file.
    Returns (success: bool, stdout: str, stderr: str).
    """
    cmd = [sys.executable, "-m", "main"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    log_file.write_text(
        "=== COMMAND ===\n" + " ".join(cmd) + "\n\n"
        "=== STDOUT ===\n" + result.stdout + "\n"
        "=== STDERR ===\n" + result.stderr
    )
    return result.returncode == 0, result.stdout, result.stderr


def print_compiler_errors(stdout: str, stderr: str):
    """
    Print syntax errors, semantic errors and warnings directly from the
    compiler's stdout/stderr, indented so they sit under the fail line.
    The compiler already formats these with ANSI colours so we print as-is.
    """
    combined = stdout + stderr
    if not combined.strip():
        return
    # Print every non-empty line, indented by 6 spaces so it reads as a
    # sub-block under the ✘ line.
    for line in combined.splitlines():
        if line.strip():
            print(f"      {line}")


# ── Per-file processing ───────────────────────────────────────────────────────

def process_file(c_file: Path, out_root: Path,
                 compiler_src: Path, has_dot: bool):
    """
    Run both compiler passes for one .c file.
    Returns (ast_ok, llvm_ok).
    """
    stem    = c_file.stem
    out_dir = out_root / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{BOLD}{CYAN}━━━  {c_file.name}  ━━━{RESET}")

    # ── Pass 1: AST dot ───────────────────────────────────────
    ast_dot = out_dir / "ast.dot"
    ast_log = out_dir / "compiler_ast.txt"

    info("Generating AST dot…")
    ast_ok, ast_out, ast_err = run_compiler(
        [str(c_file), "--dot", str(ast_dot)],
        cwd=compiler_src,
        log_file=ast_log,
    )

    if ast_ok and ast_dot.exists():
        ok(f"ast.dot  →  {ast_dot.relative_to(out_root.parent)}")
        if has_dot:
            png = out_dir / "ast.png"
            if render_png(ast_dot, png):
                ok(f"ast.png  →  {png.relative_to(out_root.parent)}")
            else:
                warn("Graphviz render failed for ast.dot")
        else:
            warn("Graphviz `dot` not on PATH – skipping PNG")
    else:
        fail(f"AST generation failed:")
        print_compiler_errors(ast_out, ast_err)

    # ── Pass 2: LLVM IR ───────────────────────────────────────
    ll_file  = out_dir / "output.ll"
    llvm_log = out_dir / "compiler_llvm.txt"

    info("Generating LLVM IR…")
    llvm_ok, llvm_out, llvm_err = run_compiler(
        [str(c_file), "--target_llvm", str(ll_file)],
        cwd=compiler_src,
        log_file=llvm_log,
    )

    if llvm_ok and ll_file.exists():
        ok(f"output.ll  →  {ll_file.relative_to(out_root.parent)}")
    else:
        fail(f"LLVM IR generation failed:")
        print_compiler_errors(llvm_out, llvm_err)

    return ast_ok, llvm_ok


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(results):
    total     = len(results)
    ast_pass  = sum(1 for _, a, _ in results if a)
    llvm_pass = sum(1 for _, _, l in results if l)

    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{BOLD}  {'File':<35} {'AST':^7} {'LLVM':^7}{RESET}")
    print(f"{BOLD}{'─' * 60}{RESET}")
    for name, ast_ok, llvm_ok in results:
        a = f"{GREEN}ok{RESET}"  if ast_ok  else f"{RED}FAIL{RESET}"
        l = f"{GREEN}ok{RESET}"  if llvm_ok else f"{RED}FAIL{RESET}"
        print(f"  {name:<35} {a:^18} {l:^18}")
    print(f"{BOLD}{'─' * 60}{RESET}")
    print(f"  Totals: AST {ast_pass}/{total}   LLVM {llvm_pass}/{total}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Run the compiler (AST + LLVM) on all example .c files."
    )
    ap.add_argument(
        "--src",
        default="src/tests/test_set_1",
        help="Directory containing the .c source files",
    )
    ap.add_argument(
        "--out",
        default="test_output",
        help="Root directory for generated artefacts",
    )
    ap.add_argument(
        "--compiler-src",
        default="src",
        help="Directory passed as cwd when running `python -m main` (must contain main/)",
    )
    args = ap.parse_args()

    src_dir      = Path(args.src).resolve()
    out_root     = Path(args.out).resolve()
    compiler_src = Path(args.compiler_src).resolve()

    if not src_dir.exists():
        print(f"{RED}Error: source directory not found: {src_dir}{RESET}")
        sys.exit(1)

    c_files = sorted(src_dir.glob("*.c"))
    if not c_files:
        print(f"{YELLOW}No .c files found in {src_dir}{RESET}")
        sys.exit(0)

    out_root.mkdir(parents=True, exist_ok=True)
    has_dot = dot_available()

    print(f"\n{BOLD}Compiler Test Runner{RESET}")
    print(f"  Source files  : {src_dir}")
    print(f"  Output root   : {out_root}")
    print(f"  Compiler cwd  : {compiler_src}")
    print(f"  Graphviz dot  : {'available' if has_dot else 'not found – PNGs skipped'}")
    print(f"  Files found   : {len(c_files)}")

    results = []
    for c_file in c_files:
        ast_ok, llvm_ok = process_file(c_file, out_root, compiler_src, has_dot)
        results.append((c_file.name, ast_ok, llvm_ok))

    print_summary(results)

    # Write CSV summary
    summary_file = out_root / "summary.txt"
    with summary_file.open("w") as fh:
        fh.write("file,ast,llvm\n")
        for name, ast_ok, llvm_ok in results:
            fh.write(f"{name},{'ok' if ast_ok else 'fail'},{'ok' if llvm_ok else 'fail'}\n")
    print(f"  Summary  →  {summary_file}\n")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "src/tests/ci/tests_manifest.json"
OUT_DIR = ROOT / ".ci_out"


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def run_command(cmd, cwd=ROOT, timeout=20):
    """
    Run een command en geef returncode, stdout, stderr terug.
    """
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def combined_output(stdout, stderr):
    return (stdout or "") + (stderr or "")


def check_contains(output, expected_parts):
    missing = []

    for part in expected_parts:
        if part not in output:
            missing.append(part)

    return missing


def run_compiler_for_ast(test, test_out_dir):
    """
    Run:
        python -m src.main --input file.c --render_ast ast.dot
    """
    ast_file = test_out_dir / "ast.dot"

    cmd = [
        sys.executable,
        "-m",
        "src.main",
        "--input",
        test["file"],
        "--render_ast",
        str(ast_file),
    ]

    returncode, stdout, stderr = run_command(cmd)

    return {
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "output": combined_output(stdout, stderr),
        "ast_file": ast_file,
        "cmd": cmd,
    }


def run_compiler_for_llvm(test, test_out_dir):
    """
    Run:
        python -m src.main --input file.c --target_llvm output.ll
    """
    ll_file = test_out_dir / "output.ll"

    cmd = [
        sys.executable,
        "-m",
        "src.main",
        "--input",
        test["file"],
        "--target_llvm",
        str(ll_file),
    ]

    returncode, stdout, stderr = run_command(cmd)

    return {
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "output": combined_output(stdout, stderr),
        "ll_file": ll_file,
        "cmd": cmd,
    }


def run_lli(ll_file):
    """
    Run:
        lli output.ll
    """
    cmd = ["lli", str(ll_file)]
    returncode, stdout, stderr = run_command(cmd)

    return {
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "output": combined_output(stdout, stderr),
        "cmd": cmd,
    }


def fail_result(test, reason, details=None):
    return {
        "name": test["name"],
        "ok": False,
        "reason": reason,
        "details": details or "",
    }


def pass_result(test):
    return {
        "name": test["name"],
        "ok": True,
        "reason": "",
        "details": "",
    }


def check_valid_ast(test, test_out_dir):
    result = run_compiler_for_ast(test, test_out_dir)
    output = result["output"]

    if result["returncode"] != 0:
        return fail_result(
            test,
            "Expected compiler success, but it failed.",
            output,
        )

    missing = check_contains(output, test.get("contains", []))
    if missing:
        return fail_result(
            test,
            "Compiler output missed expected text.",
            f"Missing: {missing}\n\nOutput:\n{output}",
        )

    ast_file = result["ast_file"]
    if not ast_file.exists():
        return fail_result(
            test,
            "Expected ast.dot to be created, but it does not exist.",
            output,
        )

    ast_content = ast_file.read_text(errors="replace")
    if "digraph AST" not in ast_content:
        return fail_result(
            test,
            "ast.dot exists, but does not look like an AST dot file.",
            ast_content[:500],
        )

    return pass_result(test)


def check_syntax_error(test, test_out_dir):
    result = run_compiler_for_ast(test, test_out_dir)
    output = result["output"]

    if result["returncode"] == 0:
        return fail_result(
            test,
            "Expected syntax error, but compiler succeeded.",
            output,
        )

    missing = check_contains(output, test.get("contains", ["[Syntax Error]"]))
    if missing:
        return fail_result(
            test,
            "Syntax error output missed expected text.",
            f"Missing: {missing}\n\nOutput:\n{output}",
        )

    return pass_result(test)


def check_semantic_error(test, test_out_dir):
    result = run_compiler_for_ast(test, test_out_dir)
    output = result["output"]

    if result["returncode"] == 0:
        return fail_result(
            test,
            "Expected semantic error, but compiler succeeded.",
            output,
        )

    missing = check_contains(output, test.get("contains", ["[Semantic Error]"]))
    if missing:
        return fail_result(
            test,
            "Semantic error output missed expected text.",
            f"Missing: {missing}\n\nOutput:\n{output}",
        )

    return pass_result(test)


def check_runtime(test, test_out_dir, skip_runtime=False):
    """
    Runtime test:
    1. Compile naar LLVM
    2. Run met lli
    3. Vergelijk stdout en exit code
    """
    if skip_runtime:
        return {
            "name": test["name"],
            "ok": True,
            "reason": "",
            "details": "Skipped runtime test.",
            "skipped": True,
        }

    if shutil.which("lli") is None:
        return fail_result(
            test,
            "Runtime test needs 'lli', but lli was not found on PATH.",
            "Install LLVM or run with --skip-runtime for now.",
        )

    compile_result = run_compiler_for_llvm(test, test_out_dir)
    compile_output = compile_result["output"]

    if compile_result["returncode"] != 0:
        return fail_result(
            test,
            "Expected LLVM generation success, but compiler failed.",
            compile_output,
        )

    missing = check_contains(compile_output, test.get("contains", []))
    if missing:
        return fail_result(
            test,
            "LLVM compiler output missed expected text.",
            f"Missing: {missing}\n\nOutput:\n{compile_output}",
        )

    ll_file = compile_result["ll_file"]
    if not ll_file.exists():
        return fail_result(
            test,
            "Expected output.ll to be created, but it does not exist.",
            compile_output,
        )

    runtime_result = run_lli(ll_file)

    expected_stdout = test.get("expected_stdout", "")
    expected_exit_code = test.get("expected_exit_code", 0)

    actual_stdout = runtime_result["stdout"]
    actual_exit_code = runtime_result["returncode"]

    if actual_stdout != expected_stdout:
        return fail_result(
            test,
            "Runtime stdout mismatch.",
            (
                f"Expected stdout: {expected_stdout!r}\n"
                f"Actual stdout:   {actual_stdout!r}\n"
                f"Runtime stderr:\n{runtime_result['stderr']}"
            ),
        )

    if actual_exit_code != expected_exit_code:
        return fail_result(
            test,
            "Runtime exit code mismatch.",
            (
                f"Expected exit code: {expected_exit_code}\n"
                f"Actual exit code:   {actual_exit_code}\n"
                f"Runtime stdout: {actual_stdout!r}\n"
                f"Runtime stderr:\n{runtime_result['stderr']}"
            ),
        )

    return pass_result(test)


def run_one_test(test, skip_runtime=False):
    test_out_dir = OUT_DIR / test["name"]
    test_out_dir.mkdir(parents=True, exist_ok=True)

    expect = test["expect"]

    if expect == "valid_ast":
        return check_valid_ast(test, test_out_dir)

    if expect == "syntax_error":
        return check_syntax_error(test, test_out_dir)

    if expect == "semantic_error":
        return check_semantic_error(test, test_out_dir)

    if expect == "runtime":
        return check_runtime(test, test_out_dir, skip_runtime=skip_runtime)

    return fail_result(
        test,
        f"Unknown expect type: {expect}",
        "Valid expect types: valid_ast, syntax_error, semantic_error, runtime",
    )


def load_manifest():
    if not MANIFEST_PATH.exists():
        print(f"{RED}Manifest not found: {MANIFEST_PATH}{RESET}")
        sys.exit(1)

    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Run compiler CI tests.")
    parser.add_argument(
        "--skip-runtime",
        action="store_true",
        help="Skip runtime tests that need LLVM lli.",
    )
    parser.add_argument(
        "--assignment",
        type=int,
        choices=[1, 2, 3],
        help="Only run tests for one assignment.",
    )
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Keep .ci_out instead of deleting it before running.",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    tests = manifest.get("tests", [])

    if args.assignment is not None:
        tests = [t for t in tests if t.get("assignment") == args.assignment]

    if not args.keep_output and OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"{CYAN}Running {len(tests)} CI test(s)...{RESET}")
    print(f"{CYAN}Output directory: {OUT_DIR}{RESET}")
    if args.skip_runtime:
        print(f"{YELLOW}Runtime tests will be skipped.{RESET}")
    print()

    results = []

    for test in tests:
        result = run_one_test(test, skip_runtime=args.skip_runtime)
        results.append(result)

        if result.get("skipped"):
            print(f"{YELLOW}SKIP{RESET} {test['name']}")
        elif result["ok"]:
            print(f"{GREEN}PASS{RESET} {test['name']}")
        else:
            print(f"{RED}FAIL{RESET} {test['name']}")
            print(f"  Reason: {result['reason']}")
            if result["details"]:
                print("  Details:")
                for line in result["details"].splitlines():
                    print(f"    {line}")

    passed = sum(1 for r in results if r["ok"] and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    failed = sum(1 for r in results if not r["ok"])
    total = len(results)

    print()
    print("=" * 60)
    print(f"Total:   {total}")
    print(f"Passed:  {passed}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

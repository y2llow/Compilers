Ja, sorry. Hieronder een **kortere README** met enkel de nuttige delen. Sections **7, 8, 9 en 11** blijven erin; de rest is compact.

````markdown
# C Compiler — Compilers Project 2025–2026

This project implements a compiler for a subset of C.  
It is written in Python, uses ANTLR for lexing/parsing, builds a custom AST, performs semantic analysis and optimisations, and generates LLVM IR.

## 1. Pipeline

```text
C source
  -> ANTLR lexer/parser
  -> AST builder
  -> include / define / enum processing
  -> semantic analysis + symbol table
  -> constant folding / propagation
  -> dead code elimination
  -> LLVM IR generation
````

## 2. Requirements

```bash
pip install -r requirements.txt
sudo apt-get install -y llvm clang graphviz
```

Optional for visualisation:

```bash
sudo apt-get install -y xdot
```

## 3. Running the compiler

Generate AST:

```bash
python -m src.main --input path/to/file.c --render_ast ast.dot
xdot ast.dot
```

Generate symbol table:

```bash
python -m src.main --input path/to/file.c --render_symb symbol_table.dot
xdot symbol_table.dot
```

Generate LLVM IR and run it:

```bash
python -m src.main --input path/to/file.c --target_llvm output.ll
lli output.ll
echo $?
```

## 4. Running tests

Normal CI tests:

```bash
python scripts/ci_tests.py
```

Only one assignment:

```bash
python scripts/ci_tests.py --assignment 6
```

Functionality tests:

```bash
python scripts/ci_functionality_tests.py
```

Only one assignment:

```bash
python scripts/ci_functionality_tests.py --assignment 5
```

Generated outputs are written to:

```text
.ci_out/
.ci_out_functionality/
```

## 5. Implemented feature status

### Assignment 1 — Expressions

| Feature                                                      | Status |
| ------------------------------------------------------------ | -----: |
| Arithmetic, comparison, logical, bitwise and shift operators |      ✅ |
| Unary operators                                              |      ✅ |
| Parentheses and precedence                                   |      ✅ |
| AST construction and visualisation                           |      ✅ |
| Constant folding                                             |      ✅ |

### Assignment 2 — Types and Variables

| Feature                                                                                             | Status |
| --------------------------------------------------------------------------------------------------- | -----: |
| `int`, `float`, `char`, `const`                                                                     |      ✅ |
| Variables, assignments and identifiers                                                              |      ✅ |
| Pointers, address-of and dereference                                                                |      ✅ |
| Pointer arithmetic and comparisons                                                                  |      ✅ |
| Explicit casts and implicit conversion warnings                                                     |      ✅ |
| Prefix/postfix `++` and `--`                                                                        |      ✅ |
| Constant propagation                                                                                |      ✅ |
| Semantic checks for undeclared variables, redeclarations, const assignment, rvalues and type errors |      ✅ |
| Symbol table visualisation                                                                          |      ✅ |
| Optional const casting                                                                              |      ❌ |

### Assignment 3 — Comments, Arrays, I/O and LLVM

| Feature                                                      | Status |
| ------------------------------------------------------------ | -----: |
| Comments stored in AST / emitted in LLVM                     |      ✅ |
| 1D and multidimensional arrays                               |      ✅ |
| Array initialisers and array element operations              |      ✅ |
| Strings / `char*`                                            |      ✅ |
| `printf` and `scanf` with `%d`, `%x`, `%s`, `%f`, `%c`, `%%` |      ✅ |
| Array semantic checks                                        |      ✅ |
| LLVM IR generation                                           |      ✅ |
| Optional dynamic heap arrays                                 |      ❌ |

### Assignment 4 — Control Flow and Scopes

| Feature                                   | Status |
| ----------------------------------------- | -----: |
| `if`, `else`, `while`, `for`              |      ✅ |
| `break`, `continue`                       |      ✅ |
| Anonymous scopes                          |      ✅ |
| `switch`, `case`, `default`, fallthrough  |      ✅ |
| Enums                                     |      ✅ |
| Scoped semantic analysis and symbol table |      ✅ |
| Optional `else if`                        |      ✅ |

### Assignment 5 — Functions and Headers

| Feature                                                           | Status |
| ----------------------------------------------------------------- | -----: |
| Functions, declarations and calls                                 |      ✅ |
| Forward declarations                                              |      ✅ |
| Recursion                                                         |      ✅ |
| Local and global variables                                        |      ✅ |
| Parameters and return values                                      |      ✅ |
| `void` functions                                                  |      ✅ |
| `#define` and `#include`                                          |      ✅ |
| Function semantic checks                                          |      ✅ |
| No code after `return`, `break`, `continue`                       |      ✅ |
| Optional function overloading                                     |      ✅ |
| Optional include guards                                           |      ✅ |
| Optional all-paths-return check                                   |      ✅ |
| Optional DCE for unused variables and constant-false conditionals |      ✅ |

### Assignment 6 — Advanced Features

| Feature                                                | Status |
| ------------------------------------------------------ | -----: |
| Typedefs                                               |      ✅ |
| Typedefs for built-ins, structs and unions             |      ✅ |
| Structs with primitive, array, enum and pointer fields |      ✅ |
| Struct member access `.` and `->`                      |      ✅ |
| Struct/union member type checking                      |      ✅ |
| Optional structs containing structs by value           |      ✅ |
| Optional arrays containing structs                     |      ✅ |
| Optional unions                                        |      ✅ |
| Optional dynamic struct allocation with `malloc/free`  |      ❌ |
| Optional function pointers                             |      ❌ |
| Optional file I/O with `fgets` / `fputs`               |      ❌ |
| Optional dynamic strings / character buffers           |      ❌ |

## 6. Optimisations

Implemented:

| Optimisation                       | Status |
| ---------------------------------- | -----: |
| Constant folding                   |      ✅ |
| Constant propagation               |      ✅ |
| Remove code after `return`         |      ✅ |
| Remove code after `break`          |      ✅ |
| Remove code after `continue`       |      ✅ |
| Remove unused variables            |      ✅ |
| Remove constant-false conditionals |      ✅ |

Useful flags:

```bash
--no-fold
--no-dce
--no-dce-unused-vars
--no-dce-dead-cond
```

## 7. Optional Functionality Tests

| Assignment | Optional feature                       | Test                                                                                                                       |
| ---------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| A4         | `else if` statements                   | `src/tests/functionality/assignment_4_control_flow/valid/11_else_if_chain.c`                                               |
| A5         | Function overloading by argument count | `src/tests/functionality/assignment_5_functions_headers/optional/01_optional_overload_by_argument_count.c`                 |
| A5         | Function overloading by argument type  | `src/tests/functionality/assignment_5_functions_headers/optional/02_optional_overload_by_argument_type_int_float.c`        |
| A5         | Include guards                         | `src/tests/functionality/assignment_5_functions_headers/optional/03_optional_include_guard_prevents_double_include.c`      |
| A5         | All paths return check                 | `src/tests/functionality/assignment_5_functions_headers/optional/05_optional_all_paths_return_detection.c`                 |
| A5         | No code after `break`                  | `src/tests/functionality/assignment_5_functions_headers/optional/06_optional_unreachable_after_break_runtime.c`            |
| A5         | No code after `continue`               | `src/tests/functionality/assignment_5_functions_headers/optional/07_optional_unreachable_after_continue_runtime.c`         |
| A5         | Constant-false conditional elimination | `src/tests/functionality/assignment_5_functions_headers/optional/08_optional_constant_false_conditional_removed_runtime.c` |
| A5         | Large DCE showcase                     | `src/tests/functionality/assignment_5_functions_headers/optional/09_optional_big_dead_code_showcase.c`                     |
| A6         | Structs containing structs as value    | `src/tests/functionality/assignment_6_advanced_features/runtime/11_runtime_array_of_structs_nested.c`                      |
| A6         | Arrays containing structs              | `src/tests/functionality/assignment_6_advanced_features/runtime/10_runtime_array_of_structs.c`                             |
| A6         | Unions                                 | `src/tests/functionality/assignment_6_advanced_features/optional/01_optional_union_basic_int.c`                            |
| A6         | Union pointer access                   | `src/tests/functionality/assignment_6_advanced_features/optional/02_optional_union_pointer_arrow.c`                        |
| A6         | Big union integration test             | `src/tests/functionality/assignment_6_advanced_features/optional/03_optional_union_big_combined.c`                         |
| A6         | Union member type checking             | `src/tests/functionality/assignment_6_advanced_features/optional/04_optional_union_member_type_checking_runtime.c`         |
| A6         | Typedef union alias                    | `src/tests/functionality/assignment_6_advanced_features/optional/05_optional_union_typedef_alias.c`                        |
| A6         | Inline typedef union alias             | `src/tests/functionality/assignment_6_advanced_features/optional/06_optional_typedef_union_inline_alias.c`                 |
| A6         | Unknown union member error             | `src/tests/functionality/assignment_6_advanced_features/optional/07_optional_union_missing_member.c`                       |
| A6         | Union member type mismatch             | `src/tests/functionality/assignment_6_advanced_features/optional/08_optional_union_member_type_mismatch.c`                 |
| A6         | `->` on non-pointer union              | `src/tests/functionality/assignment_6_advanced_features/optional/09_optional_union_arrow_on_non_pointer.c`                 |

## 8. Recommended Showcase Tests

### Header include + function call

```text
src/tests/functionality/assignment_5_functions_headers/runtime/07_runtime_header_function_call.c
```

Shows local `#include`, function definitions in headers, function calls, LLVM generation and runtime execution.

```bash
python -m src.main --input src/tests/functionality/assignment_5_functions_headers/runtime/07_runtime_header_function_call.c --target_llvm output.ll
lli output.ll
echo $?
```

### Pointer arithmetic

```text
src/tests/functionality/assignment_2_types_variables/runtime/06_runtime_pointer_arithmetic.c
```

Shows arrays, pointer arithmetic, pointer difference, `p++`, `q--`, and LLVM pointer operations.

```bash
python -m src.main --input src/tests/functionality/assignment_2_types_variables/runtime/06_runtime_pointer_arithmetic.c --target_llvm output.ll
lli output.ll
echo $?
```

### Large DCE showcase

```text
src/tests/functionality/assignment_5_functions_headers/optional/09_optional_big_dead_code_showcase.c
```

Shows unused-variable elimination, code after `return`, code after `break`, code after `continue`, `if(0)`, `while(0)` and `for(;0;)`.

```bash
python -m src.main --input src/tests/functionality/assignment_5_functions_headers/optional/09_optional_big_dead_code_showcase.c --render_ast ast.dot
xdot ast.dot
```

### Switch fallthrough

```text
src/tests/functionality/assignment_4_control_flow/runtime/12_runtime_switch_fallthrough.c
```

Shows C-style fallthrough when a `case` has no `break`.

```bash
python -m src.main --input src/tests/functionality/assignment_4_control_flow/runtime/12_runtime_switch_fallthrough.c --target_llvm output.ll
lli output.ll
echo $?
```

## 9. Error Handling

The compiler reports syntax errors as:

```text
[Syntax Error] line X, column Y
```

Semantic errors include:

* undeclared variables
* redeclarations
* assignment to const
* assignment to rvalue
* invalid pointer dereference
* invalid array indexing
* wrong function arguments
* invalid struct/union member access
* `->` on non-pointer types

Example:

```bash
python -m src.main --input src/tests/functionality/assignment_6_advanced_features/invalid_semantic/06_mandatory_arrow_on_non_pointer.c --render_ast ast.dot
```

## 10. Reference

Compare C behaviour with GCC:

```bash
gcc -ansi -pedantic path/to/file.c
```

## 11. Notes and Known Limitations

Implemented:

* LLVM IR output
* AST visualisation
* Symbol table visualisation
* Semantic analysis
* Function overloading
* Include guards
* Structs
* Unions
* Typedefs
* Arrays of structs
* Structs containing structs by value

Not implemented / not claimed:

* Native binary output
* MIPS output
* Dynamic arrays on heap
* Dynamic allocation of structs with `malloc/free`
* Function pointers
* File reading with `fgets`
* File writing with `fputs`
* Dynamically allocated strings / character buffers
* Optional const casting

```
```

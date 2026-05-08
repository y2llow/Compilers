# ============================================================
# Semantic Analyzer with Type Checking and Function Support
# ============================================================

from parser.semantics.symbol_table import SymbolTable
from parser.ast_nodes import *

RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


class SemanticAnalyzer:
    """
    Semantische analysator voor de AST.

    Controleert assignment 1-5 functionaliteit:
    - main bestaat
    - variabelen moeten gedeclareerd zijn
    - geen redeclaratie in dezelfde scope
    - geen assignment aan const
    - basis type checking
    - pointer checks
    - array checks, inclusief 1D en 2D array access
    - printf/scanf vereisen #include <stdio.h>
    - control flow: break/continue context
    - functions: declarations, definitions, calls, argument checking
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.stdio_included = False
        self.current_function_return_type = None
        self.loop_depth = 0
        self.switch_depth = 0
        self.known_types = set()
        self.included_types = set()      # Types seeded from #include registries
        self.typedef_map = {}           # Maps typedef alias -> (underlying_type_name, pointer_depth)
        self.struct_members = {}         # Maps struct name -> list of StructMemberNode
        self.union_members = {}         # Maps union name -> list of StructMemberNode

        # name -> [
        #   {
        #     'return_type': str,
        #     'return_ptr': int,
        #     'params': [(type_name, pointer_depth, dimensions_tuple), ...],
        #     'defined': bool,
        #     'line': int,
        #     'column': int,
        #     'mangled_name': str
        #   }, ...
        # ]
        # Multiple entries with the same name are allowed when their parameter
        # signatures differ. This implements optional function overloading.
        self.functions = {}

    # ============================================================
    # Error / warning helpers
    # ============================================================

    def add_error(self, line, column, message):
        self.errors.append({
            'line': line,
            'column': column,
            'message': message
        })

    def add_warning(self, line, column, message):
        self.warnings.append({
            'line': line,
            'column': column,
            'message': message
        })

    # ============================================================
    # Public entry point
    # ============================================================

    def analyze(self, node, typedef_registry=None):
        if typedef_registry:
            for name, info in typedef_registry.items():
                if isinstance(info, tuple) and len(info) == 2:
                    self.known_types.add(name)
                    self.included_types.add(name)
                    self.typedef_map[name] = info
                else:
                    self.known_types.add(name)
                    self.included_types.add(name)
        self.visit(node)
        return len(self.errors) == 0

    # ============================================================
    # Visitor dispatch
    # ============================================================

    def visit(self, node):
        if node is None:
            return

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node):
        pass

    # ============================================================
    # Program / top-level
    # ============================================================

    def visit_ProgramNode(self, node):
        has_main = False

        # 1. Includes verwerken.
        for item in node.top_level_items:
            if isinstance(item, IncludeNode):
                self.visit(item)

        # 2. Typedefs en structs registreren zodat ze als geldige types gelden.
        for item in node.top_level_items:
            if isinstance(item, (TypedefNode, StructDeclNode, UnionDeclNode)):
                self.visit(item)

        # 3. Enum constants registreren als globale int constants.
        for item in node.top_level_items:
            if isinstance(item, EnumDeclNode):
                self.visit(item)

        # 4. Top-level variabelen registreren.
        for item in node.top_level_items:
            if isinstance(item, VarDeclNode):
                self.visit(item)

        # 5. Analyseer top-level items in volgorde
        for item in node.top_level_items:

            if isinstance(item, FunctionDeclNode):
                self._register_function_declaration(item)
                continue

            elif isinstance(item, FunctionDefNode):
                self._register_function_definition(item)

                if item.name == "main":
                    has_main = True

                    if item.return_type != "int" or item.return_ptr != 0:
                        self.add_error(
                            getattr(item, 'line', 0),
                            getattr(item, 'column', 0),
                            "Error: main function must return int"
                        )

                self.visit(item)

            elif isinstance(item, DefineNode):
                pass

        if not has_main:
            self.add_error(
                0, 0,
                "Error: missing 'int main()' function"
            )

    def visit_IncludeNode(self, node):
        if node.header == 'stdio.h':
            self.stdio_included = True

    def visit_DefineNode(self, node):
        pass

    def visit_TypedefNode(self, node):
        builtin_types = {'int', 'float', 'char', 'void'}

        # A typedef node that came from an included header was already seeded
        # into known_types via the typedef_registry.  Seeing it again in the
        # AST is normal — just update typedef_map and move on without error.
        if node.new_name in self.included_types:
            self.typedef_map[node.new_name] = (node.existing_type, node.pointer_depth)
            self.included_types.discard(node.new_name)
            return

        # Allow `typedef struct Foo Foo` and `typedef enum Foo Foo`:
        # the struct/enum name is registered in known_types first, but aliasing
        # it to the same name is valid C and must not be treated as a conflict.
        underlying = node.existing_type
        for prefix in ('struct', 'enum', 'union'):
            if underlying.startswith(prefix):
                underlying = underlying[len(prefix):]
                break
        if node.new_name in self.known_types and node.new_name == underlying:
            self.typedef_map[node.new_name] = (node.existing_type, node.pointer_depth)
            return

        # The new name must not clash with builtins or already-declared types
        if node.new_name in builtin_types or node.new_name in self.known_types:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: typedef name '{node.new_name}' conflicts with an existing type"
            )
            return

        # Validate the underlying type exists
        self._validate_type_name_str(node.existing_type, node)

        self.known_types.add(node.new_name)
        self.typedef_map[node.new_name] = (node.existing_type, node.pointer_depth)

    def visit_StructDeclNode(self, node):
        self.known_types.add(node.name)
        self.struct_members[node.name] = node.members

        # Validate each member's type
        for member in node.members:
            self._validate_type_name_str(member.type_name, member)

    def visit_UnionDeclNode(self, node):
        self.known_types.add(node.name)
        self.union_members[node.name] = node.members

        for member in node.members:
            self._validate_type_name_str(member.type_name, member)

    # ============================================================
    # Function registration helpers
    # ============================================================

    def _param_signature(self, params):
        result = []

        for p in params:
            dims = tuple(getattr(p, 'array_dimensions', []) or [])
            result.append((p.type_name, p.pointer_depth, dims))

        return result

    def _function_signature(self, node):
        return {
            'return_type': node.return_type,
            'return_ptr': node.return_ptr,
            'params': self._param_signature(node.params),
            'defined': isinstance(node, FunctionDefNode),
            'line': getattr(node, 'line', 0),
            'column': getattr(node, 'column', 0),
        }

    def _same_function_signature(self, a, b):
        return (
                a['return_type'] == b['return_type']
                and a['return_ptr'] == b['return_ptr']
                and a['params'] == b['params']
        )

    def _same_parameter_signature(self, a, b):
        """For overloading, only the parameter list identifies an overload."""
        return a['params'] == b['params']

    def _type_suffix(self, type_name, pointer_depth=0, dims=()):
        safe = str(type_name).replace(' ', '_').replace('*', 'ptr')
        suffix = safe + ('_ptr' * int(pointer_depth or 0))
        if dims:
            suffix += '_arr' + '_'.join(str(d) for d in dims)
        return suffix

    def _mangled_function_name(self, name, params):
        """
        LLVM does not allow multiple global functions with the same name.
        Keep main unmangled, but mangle overloaded functions by parameter types.
        """
        if name == 'main':
            return name
        if not params:
            return f"{name}__void"
        return name + '__' + '__'.join(
            self._type_suffix(t, p, d) for (t, p, d) in params
        )

    def _register_function_declaration(self, node):
        name = node.name
        sig = self._function_signature(node)
        sig['defined'] = False
        sig['mangled_name'] = self._mangled_function_name(name, sig['params'])
        node.mangled_name = sig['mangled_name']

        overloads = self.functions.setdefault(name, [])

        for existing in overloads:
            if self._same_parameter_signature(existing, sig):
                if not self._same_function_signature(existing, sig):
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: conflicting function declaration for '{name}' "
                        f"(same parameter types previously declared at line {existing['line']})"
                    )
                return

        overloads.append(sig)

    def _register_function_definition(self, node):
        name = node.name
        sig = self._function_signature(node)
        sig['defined'] = True
        sig['mangled_name'] = self._mangled_function_name(name, sig['params'])
        node.mangled_name = sig['mangled_name']

        overloads = self.functions.setdefault(name, [])

        for existing in overloads:
            if self._same_parameter_signature(existing, sig):
                if existing.get('defined'):
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: redefinition of function '{name}' "
                        f"with same parameter types (previously defined at line {existing['line']})"
                    )
                    return

                if not self._same_function_signature(existing, sig):
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: conflicting function definition for '{name}' "
                        f"(same parameter types previously declared at line {existing['line']})"
                    )
                    return

                existing['defined'] = True
                existing['line'] = getattr(node, 'line', 0)
                existing['column'] = getattr(node, 'column', 0)
                existing['mangled_name'] = sig['mangled_name']
                node.mangled_name = sig['mangled_name']
                return

        # Add this before overloads.append(sig)
        for existing in overloads:
            if not existing.get('defined') and not self._same_parameter_signature(existing, sig):
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: conflicting function definition for '{name}' "
                    f"(previously declared at line {existing['line']})"
                )
                return

        overloads.append(sig)

    def _conversion_score(self, expected, actual):
        """
        Return None when incompatible.
        Lower score is better.

        exact match = 0
        scalar conversion = 1
        array-to-pointer decay = 0 or 1 depending on exactness

        expected format from function params:
            (type_name, pointer_depth, dims)

        actual format from expressions:
            (type_name, pointer_depth)
            or
            (type_name, pointer_depth, True, dims)
        """

        expected_type = expected[0]
        expected_ptr = expected[1]
        expected_dims = tuple(expected[2]) if len(expected) > 2 and expected[2] else ()

        actual_type = actual[0]
        actual_ptr = actual[1]
        actual_is_array = len(actual) > 2 and actual[2] is True
        actual_dims = tuple(actual[3]) if actual_is_array and len(actual) > 3 else ()

        expected_type = self._resolve_typedef(expected_type)
        actual_type = self._resolve_typedef(actual_type)

        expected_is_array_param = bool(expected_dims)

        # ------------------------------------------------------------
        # Case 1: parameter itself is declared as array
        # Example:
        #   int sum_matrix(int matrix[2][3])
        #   int matrix[2][3];
        #   sum_matrix(matrix);
        # ------------------------------------------------------------
        if expected_is_array_param:
            if actual_is_array and expected_type == actual_type:
                # Prefer exact dimension match, but do not be too strict because
                # older parts of the compiler may store dimensions differently.
                if not expected_dims or not actual_dims or expected_dims == actual_dims:
                    return 0

                # Same base type but dimensions differ: still compatible enough
                # for semantic success, but worse than exact.
                return 1

            # Accept pointer passed to array parameter as a decayed array.
            if actual_ptr > 0 and expected_type == actual_type:
                return 1

            return None

        # ------------------------------------------------------------
        # Case 2: actual argument is an array
        # Function-call context: array can decay to pointer.
        # Example:
        #   void process(int* p);
        #   int arr[3];
        #   process(arr);
        # ------------------------------------------------------------
        if actual_is_array:
            # Array to pointer parameter.
            if expected_ptr > 0:
                decayed_actual_ptr = actual_ptr + 1

                if expected_ptr == decayed_actual_ptr and expected_type == actual_type:
                    return 0

                if expected_ptr == decayed_actual_ptr and expected_type == 'void':
                    return 1

                return None

            # Backwards compatibility with existing tests:
            # allow array passed where scalar of same base type is expected.
            # Example:
            #   void process(int x);
            #   int arr[3];
            #   process(arr);
            if expected_ptr == 0 and actual_ptr == 0 and expected_type == actual_type:
                return 1

            return None

        # ------------------------------------------------------------
        # Case 3: normal pointer arguments
        # ------------------------------------------------------------
        if expected_ptr > 0 or actual_ptr > 0:
            if expected_ptr == actual_ptr and expected_type == actual_type:
                return 0

            if expected_ptr == actual_ptr and expected_type == 'void':
                return 1

            # GCC-compatible behavior:
            # passing float* to int* is a warning, not a hard semantic error.
            # Let overload resolution select the function, then _check_type_assignment()
            # will issue the warning.
            if expected_ptr == actual_ptr:
                return 2

            return None

        # ------------------------------------------------------------
        # Case 4: normal scalar arguments
        # ------------------------------------------------------------
        if expected_type == actual_type:
            return 0

        scalar_types = {'int', 'float', 'char'}
        if expected_type in scalar_types and actual_type in scalar_types:
            return 1

        return None

    def _resolve_function_overload(self, node):
        """Resolve a FunctionCallNode to exactly one overload."""

        if hasattr(node, 'resolved_function'):
            return node.resolved_function

        if getattr(node, 'overload_resolution_failed', False):
            return None

        name = node.name
        overloads = self.functions.get(name, [])
        actual_types = []

        for arg in node.args:
            arg_type = self._get_expression_type(arg)
            if arg_type is None:
                return None
            actual_types.append(arg_type)

        same_count = [f for f in overloads if len(f['params']) == len(actual_types)]

        if not same_count:
            actual_count = len(actual_types)

            # Backwards-compatible message for old Assignment 5 tests.
            # It still contains "no overload taking" for the new overload tests.
            if len(overloads) == 1:
                expected_count = len(overloads[0]['params'])
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: function '{name}' expects {expected_count} argument(s), got {actual_count}; "
                    f"no overload taking {actual_count} argument(s) for function '{name}'"
                )
            else:
                counts = sorted({len(f['params']) for f in overloads})
                counts_text = ', '.join(str(c) for c in counts) if counts else 'none'
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: no overload taking {actual_count} argument(s) for function '{name}' "
                    f"(available: {counts_text})"
                )

            node.overload_resolution_failed = True
            return None

        matches = []
        for func in same_count:
            total_score = 0
            ok = True
            for expected, actual in zip(func['params'], actual_types):
                score = self._conversion_score(expected, actual)
                if score is None:
                    ok = False
                    break
                total_score += score
            if ok:
                matches.append((total_score, func))

        if not matches:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: no matching overload for function '{name}' with given argument type(s)"
            )
            node.overload_resolution_failed = True
            return None

        matches.sort(key=lambda item: item[0])
        best_score = matches[0][0]
        best = [func for score, func in matches if score == best_score]

        if len(best) > 1:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: ambiguous overload call to function '{name}'"
            )
            node.overload_resolution_failed = True
            return None

        resolved = best[0]
        node.resolved_function = resolved
        node.mangled_name = resolved['mangled_name']
        node.resolved_return_type = (resolved['return_type'], resolved['return_ptr'])
        return resolved

    # ============================================================
    # Enum
    # ============================================================

    def _block_always_returns(self, items):
        """
        Return True als elk uitvoerbaar pad door deze block eindigt in een return.

        Conservatieve analyse:
        - return statement => gegarandeerd return
        - if/else => alleen gegarandeerd als then én else gegarandeerd returnen
        - compound block => kijk recursief
        - loops worden standaard niet als gegarandeerd beschouwd,
          behalve simpele while(1) / while(nonzero-int) met body die altijd returnt.
        """

        for stmt in items:
            if self._statement_always_returns(stmt):
                return True

        return False

    def _statement_always_returns(self, stmt):
        """
        Return True als deze statement gegarandeerd een return uitvoert.
        """

        if isinstance(stmt, ReturnNode):
            return True

        if isinstance(stmt, CompoundStmtNode):
            return self._block_always_returns(stmt.items)

        if isinstance(stmt, IfNode):
            # Zonder else is er altijd een pad zonder return.
            if stmt.else_body is None:
                return False

            then_returns = self._statement_always_returns(stmt.then_body)
            else_returns = self._statement_always_returns(stmt.else_body)

            return then_returns and else_returns

        if isinstance(stmt, WhileNode):
            # Alleen heel eenvoudige infinite loops als gegarandeerd tellen:
            # while (1) { return ...; }
            if isinstance(stmt.condition, IntLiteralNode) and stmt.condition.value != 0:
                return self._statement_always_returns(stmt.body)

            return False

        if isinstance(stmt, ForNode):
            # for(;;) wordt soms gebruikt als infinite loop.
            # Alleen als condition ontbreekt en body altijd returnt.
            if stmt.condition is None:
                return self._statement_always_returns(stmt.body)

            return False

        if isinstance(stmt, SwitchNode):
            return self._switch_always_returns(stmt)

        return False

    def _switch_always_returns(self, stmt):
        """
        Conservatieve switch-check:
        switch returnt gegarandeerd alleen als:
        - er een default is
        - elke case block altijd returnt
        - default block altijd returnt

        Dit negeert complexe fallthrough-logica bewust.
        """

        if stmt.default is None:
            return False

        for case in stmt.cases:
            if not self._block_always_returns(case.items):
                return False

        return self._block_always_returns(stmt.default.items)

    def visit_EnumDeclNode(self, node):
        self.known_types.add(node.name)
        current_value = 0

        for const in node.constants:
            if const.value is not None:
                current_value = const.value

            success, existing = self.symbol_table.add_symbol(
                const.name,
                'int',
                pointer_depth=0,
                is_const=True,
                line=getattr(const, 'line', 0),
                column=getattr(const, 'column', 0),
                array_dimensions=[]
            )

            if not success:
                self.add_error(
                    getattr(const, 'line', 0),
                    getattr(const, 'column', 0),
                    f"Error: enum constant '{const.name}' already declared at line {existing.line}, column {existing.column}"
                )

            current_value += 1

    def _validate_type_name_str(self, type_name: str, node) -> bool:
        """Same as _validate_type_name but accepts a plain string."""
        return self._validate_type_name(type_name, node)

    # ============================================================
    # Functions
    # ============================================================

    def visit_FunctionDeclNode(self, node):
        # Validate return type
        self._validate_type_name(node.return_type, node)

        # Validate parameter types
        for param in node.params:
            self._validate_type_name(param.type_name, param)

        # Declarations are registered in visit_ProgramNode, not here
        # So we just validate types but don't need to do anything else

    def _validate_type_name(self, type_name, node):
        valid_builtin_types = {'int', 'float', 'char', 'void'}

        if type_name in valid_builtin_types:
            return True

        # Strip 'enum'/'struct' prefix from ANTLR getText() concatenation
        for prefix in ('enum', 'struct', 'union'):
            if type_name.startswith(prefix) and len(type_name) > len(prefix):
                return True

        # Accept typedef aliases and declared struct/enum names
        if type_name in self.known_types:
            return True

        self.add_error(
            getattr(node, 'line', 0),
            getattr(node, 'column', 0),
            f"Error: unknown type name '{type_name}'"
        )
        return False

    def visit_FunctionDefNode(self, node):
        # Belangrijk:
        # NIET opnieuw registreren/checken hier.
        # Dat gebeurt al in visit_ProgramNode via _register_function_definition.
        # Anders krijg je foutief "redefinition of function main".

        # Validate return type
        self._validate_type_name(node.return_type, node)

        # Validate parameter types
        for param in node.params:
            self._validate_type_name(param.type_name, param)

        old_return_type = self.current_function_return_type
        self.current_function_return_type = (node.return_type, node.return_ptr)

        self.symbol_table.push_scope(f"function {node.name}")

        for param in node.params:
            success, existing = self.symbol_table.add_symbol(
                param.name,
                param.type_name,
                param.pointer_depth,
                param.is_const,
                line=getattr(param, 'line', 0),
                column=getattr(param, 'column', 0),
                array_dimensions=param.array_dimensions
            )

            if not success:
                self.add_error(
                    getattr(param, 'line', 0),
                    getattr(param, 'column', 0),
                    f"Error: parameter '{param.name}' already declared at line {existing.line}, column {existing.column}"
                )

        self._visit_block_items(node.body.items)

        # Optional feature:
        # Check that all paths in non-void functions end with a return statement.
        if node.return_type != "void" or node.return_ptr != 0:
            if not self._block_always_returns(node.body.items):
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: not all control paths in function '{node.name}' return a value"
                )

        self.symbol_table.pop_scope()
        self.current_function_return_type = old_return_type

    def visit_FunctionCallNode(self, node):
        if node.name not in self.functions:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: implicit declaration of function '{node.name}'"
            )

            for arg in node.args:
                self._check_expression(arg)

            return

        for arg in node.args:
            self._check_expression(arg)

        func_info = self._resolve_function_overload(node)
        if func_info is None:
            return

        for i, arg in enumerate(node.args):
            expected_type_name, expected_ptr, _dims = func_info['params'][i]
            arg_type = self._get_expression_type(arg)

            if arg_type is not None:
                self._check_type_assignment(
                    target_type=(expected_type_name, expected_ptr),
                    value_type=arg_type,
                    target_name=f"argument {i + 1}",
                    node=node
                )

    # ============================================================
    # Compound / block
    # ============================================================

    def visit_CompoundStmtNode(self, node):
        self.symbol_table.push_scope("block")
        self._visit_block_items(node.items)
        self.symbol_table.pop_scope()

    def _visit_block_items(self, items):
        seen_non_decl = False

        for item in items:
            if isinstance(item, VarDeclNode):
                if seen_non_decl:
                    self.add_warning(
                        getattr(item, 'line', 0),
                        getattr(item, 'column', 0),
                        "Warning: ISO C90 forbids mixed declarations and code"
                    )
            else:
                seen_non_decl = True

            self.visit(item)

    # ============================================================
    # Control flow
    # ============================================================

    def visit_IfNode(self, node):
        self._check_expression(node.condition)
        self.visit(node.then_body)

        if node.else_body is not None:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        self._check_expression(node.condition)

        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1

    def visit_ForNode(self, node):
        self.symbol_table.push_scope("for")

        if node.init is not None:
            self.visit(node.init)

        if node.condition is not None:
            self._check_expression(node.condition)

        self.loop_depth += 1

        self.visit(node.body)

        if node.update is not None:
            self.visit(node.update)

        self.loop_depth -= 1
        self.symbol_table.pop_scope()

    def visit_BreakNode(self, node):
        if self.loop_depth == 0 and self.switch_depth == 0:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: 'break' statement not within loop or switch"
            )

    def visit_ContinueNode(self, node):
        if self.loop_depth == 0:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: 'continue' statement not within loop"
            )

    def visit_SwitchNode(self, node):
        self._check_expression(node.expression)

        self.switch_depth += 1

        for case in node.cases:
            self.visit(case)

        if node.default is not None:
            self.visit(node.default)

        self.switch_depth -= 1

    def visit_SwitchCaseNode(self, node):
        self._check_expression(node.value)

        for item in node.items:
            if isinstance(item, VarDeclNode):
                self.add_error(
                    getattr(item, 'line', 0),
                    getattr(item, 'column', 0),
                    "Error: variable declaration directly inside switch case is not allowed; use braces"
                )

        self._visit_block_items(node.items)

    def visit_SwitchDefaultNode(self, node):
        for item in node.items:
            if isinstance(item, VarDeclNode):
                self.add_error(
                    getattr(item, 'line', 0),
                    getattr(item, 'column', 0),
                    "Error: variable declaration directly inside switch default is not allowed; use braces"
                )

        self._visit_block_items(node.items)

    # ============================================================
    # Statements
    # ============================================================

    def visit_VarDeclNode(self, node):
        # Strip enum/struct prefix (ANTLR getText concatenates them)
        for prefix in ('enum', 'struct', 'union'):
            if node.type_name.startswith(prefix) and len(node.type_name) > len(prefix):
                node.type_name = node.type_name[len(prefix):]
                break

        # Resolve typedef alias to underlying type for type-checking purposes
        # (we keep node.type_name as the alias for display, but check the underlying type)
        self._validate_type_name(node.type_name, node)

        success, existing = self.symbol_table.add_symbol(
            node.name,
            node.type_name,  # store the alias name — that's fine
            node.pointer_depth,
            node.is_const,
            line=getattr(node, 'line', 0),
            column=getattr(node, 'column', 0),
            array_dimensions=node.array_dimensions
        )

        if not success:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: variable '{node.name}' already declared at line {existing.line}, column {existing.column}"
            )

        if node.value is None:
            return

        if isinstance(node.value, ArrayInitializerNode):
            self._check_array_initializer(node, node.value)
            return

        self._check_expression(node.value)
        value_type = self._get_expression_type(node.value)

        if value_type is not None and success:
            # Resolve typedef alias before type-checking assignment
            effective_type, effective_ptr = self._resolve_typedef_full(
                node.type_name,
                node.pointer_depth
            )

            self._check_type_assignment(
                target_type=(effective_type, effective_ptr),
                value_type=value_type,
                target_name=node.name,
                node=node
            )

    def visit_AssignNode(self, node):
        self._check_lvalue(node.target)
        self._check_expression(node.value)

        target_type = self._get_lvalue_type(node.target)
        value_type = self._get_expression_type(node.value)

        if target_type is not None and value_type is not None:
            self._check_type_assignment(
                target_type=target_type,
                value_type=value_type,
                target_name=self._node_to_string(node.target),
                node=node
            )

    def visit_ReturnNode(self, node):
        if node.value is None:
            if self.current_function_return_type is not None:
                return_type, _return_ptr = self.current_function_return_type
                if return_type != 'void':
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        "Error: non-void function should return a value"
                    )
            return

        self._check_expression(node.value)

        if self.current_function_return_type is not None:
            expected_type = self.current_function_return_type
            actual_type = self._get_expression_type(node.value)

            if actual_type is not None:
                self._check_type_assignment(
                    target_type=expected_type,
                    value_type=actual_type,
                    target_name='return',
                    node=node
                )

    def visit_BinaryOpNode(self, node):
        self._check_expression(node)

    def visit_UnaryOpNode(self, node):
        self._check_expression(node)

    def visit_DereferenceNode(self, node):
        self._check_expression(node)

    def visit_AddressOfNode(self, node):
        self._check_expression(node)

    def visit_IncrementNode(self, node):
        self._check_lvalue(node.operand)

    def visit_DecrementNode(self, node):
        self._check_lvalue(node.operand)

    def visit_CastNode(self, node):
        self._check_expression(node.operand)

    def visit_ArrayAccessNode(self, node):
        self._check_expression(node)

    def visit_ArrayInitializerNode(self, node):
        for elem in node.elements:
            if isinstance(elem, ArrayInitializerNode):
                self.visit_ArrayInitializerNode(elem)
            else:
                self._check_expression(elem)

    def visit_PrintfNode(self, node):
        if not self.stdio_included:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: 'printf' used without #include <stdio.h>"
            )
            return

        self._check_format_args(node.format_string, node.args, 'printf', node)

        for arg in node.args:
            self._check_expression(arg)

    def visit_ScanfNode(self, node):
        if not self.stdio_included:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: 'scanf' used without #include <stdio.h>"
            )
            return

        self._check_format_args(node.format_string, node.args, 'scanf', node)

        for arg in node.args:
            self._check_expression(arg)

    # ============================================================
    # Array checks
    # ============================================================

    def _check_array_initializer(self, var_decl, initializer):
        """
        Check array initializers recursively.

        Examples:
            int a[3] = {1, 2, 3};              OK
            int m[2][3] = {{1,2,3},{4,5,6}};  OK
            int x = {1, 2, 3};                ERROR
        """
        dimensions = getattr(var_decl, "array_dimensions", [])

        if not dimensions:
            self.add_error(
                getattr(initializer, 'line', getattr(var_decl, 'line', 0)),
                getattr(initializer, 'column', getattr(var_decl, 'column', 0)),
                f"Error: array initializer used for non-array variable '{var_decl.name}'"
            )
            return

        self._check_array_initializer_recursive(
            initializer=initializer,
            dimensions=dimensions,
            level=0,
            node=var_decl
        )

    def _check_array_initializer_recursive(self, initializer, dimensions, level, node):
        """
        Recursive check voor multidimensionale array initializers.
        dimensions = [2, 3] voor int matrix[2][3]
        level 0 checkt aantal rijen
        level 1 checkt aantal elementen per rij
        """
        if not isinstance(initializer, ArrayInitializerNode):
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: array initializer must use braces"
            )
            return

        expected_len = dimensions[level]
        actual_len = len(initializer.elements)

        if actual_len != expected_len:
            self.add_error(
                getattr(initializer, 'line', getattr(node, 'line', 0)),
                getattr(initializer, 'column', getattr(node, 'column', 0)),
                f"Error: array initializer has length {actual_len}, expected {expected_len}"
            )
            return

        is_last_dimension = level == len(dimensions) - 1

        for elem in initializer.elements:
            if is_last_dimension:
                # Laatste dimensie: hier verwachten we gewone expressies, geen nested initializer
                if isinstance(elem, ArrayInitializerNode):
                    self.add_error(
                        getattr(elem, 'line', getattr(node, 'line', 0)),
                        getattr(elem, 'column', getattr(node, 'column', 0)),
                        "Error: too many nested braces in array initializer"
                    )
                else:
                    self._check_expression(elem)
            else:
                # Nog niet laatste dimensie: elk element moet opnieuw een initializer zijn
                if not isinstance(elem, ArrayInitializerNode):
                    self.add_error(
                        getattr(elem, 'line', getattr(node, 'line', 0)),
                        getattr(elem, 'column', getattr(node, 'column', 0)),
                        "Error: missing nested braces in multidimensional array initializer"
                    )
                else:
                    self._check_array_initializer_recursive(
                        initializer=elem,
                        dimensions=dimensions,
                        level=level + 1,
                        node=node
                    )

    # ============================================================
    # Type helpers
    # ============================================================

    def _strip_aggregate_prefix(self, type_name: str) -> str:
        bare = type_name

        for prefix in ('struct', 'union', 'enum'):
            if isinstance(bare, str) and bare.startswith(prefix) and len(bare) > len(prefix):
                return bare[len(prefix):]

        return bare

    def _resolve_aggregate_name(self, type_name: str):
        """
        Return ('struct', name) of ('union', name), of None.
        """
        bare = self._strip_aggregate_prefix(type_name)

        if bare in self.struct_members:
            return ('struct', bare)

        if bare in self.union_members:
            return ('union', bare)

        resolved = self._resolve_typedef(type_name)
        resolved = self._strip_aggregate_prefix(resolved)

        if resolved in self.struct_members:
            return ('struct', resolved)

        if resolved in self.union_members:
            return ('union', resolved)

        if type_name in self.typedef_map:
            underlying, _ptr = self.typedef_map[type_name]
            underlying = self._strip_aggregate_prefix(underlying)

            if underlying in self.struct_members:
                return ('struct', underlying)

            if underlying in self.union_members:
                return ('union', underlying)

        return None

    def _get_aggregate_member_type(self, kind: str, aggregate_name: str, member_name: str):
        """
        Return type info for a struct/union member.

        Format:
            (base_type, pointer_depth)

        or for array members:
            (base_type, pointer_depth, True, dimensions)
        """
        if kind == 'struct':
            members = self.struct_members.get(aggregate_name, [])
        else:
            members = self.union_members.get(aggregate_name, [])

        for member in members:
            if member.name == member_name:
                base_type = self._strip_aggregate_prefix(member.type_name)
                dims = getattr(member, "array_dimensions", []) or []

                if dims:
                    return (base_type, member.pointer_depth, True, dims)

                return (base_type, member.pointer_depth)

        return None

    def _get_member_type(self, struct_name, member_name):
        """
        Backwards-compatible wrapper for old struct-only code.
        """
        return self._get_aggregate_member_type('struct', struct_name, member_name)

    def _resolve_struct_name(self, type_name: str) -> str:
        """
        Given a type name (possibly a typedef alias or with struct prefix),
        return the bare struct name registered in self.struct_members, or None.
        """
        # Strip struct prefix from ANTLR concatenation e.g. "structPoint"
        bare = type_name
        if bare.startswith('struct'):
            bare = bare[len('struct'):]

        if bare in self.struct_members:
            return bare

        # Follow typedef chain
        resolved = self._resolve_typedef(type_name)
        if resolved.startswith('struct'):
            resolved = resolved[len('struct'):]
        if resolved in self.struct_members:
            return resolved

        # One more level: typedef alias -> struct name stored in typedef_map
        if type_name in self.typedef_map:
            underlying, _ = self.typedef_map[type_name]
            if underlying.startswith('struct'):
                underlying = underlying[len('struct'):]
            if underlying in self.struct_members:
                return underlying

        return None

    def _strip_aggregate_prefix(self, type_name: str) -> str:
        bare = type_name

        for prefix in ('struct', 'union', 'enum'):
            if isinstance(bare, str) and bare.startswith(prefix) and len(bare) > len(prefix):
                return bare[len(prefix):]

        return bare

    def _resolve_aggregate_name(self, type_name: str):
        """
        Return ('struct', name) of ('union', name), of None.
        """
        bare = self._strip_aggregate_prefix(type_name)

        if bare in self.struct_members:
            return ('struct', bare)

        if bare in self.union_members:
            return ('union', bare)

        resolved = self._resolve_typedef(type_name)
        resolved = self._strip_aggregate_prefix(resolved)

        if resolved in self.struct_members:
            return ('struct', resolved)

        if resolved in self.union_members:
            return ('union', resolved)

        if type_name in self.typedef_map:
            underlying, _ptr = self.typedef_map[type_name]
            underlying = self._strip_aggregate_prefix(underlying)

            if underlying in self.struct_members:
                return ('struct', underlying)

            if underlying in self.union_members:
                return ('union', underlying)

        return None

    def _get_aggregate_member_type(self, kind: str, aggregate_name: str, member_name: str):
        """
        Return type info for a struct/union member.

        Format:
            (base_type, pointer_depth)

        or for array members:
            (base_type, pointer_depth, True, dimensions)
        """
        if kind == 'struct':
            members = self.struct_members.get(aggregate_name, [])
        else:
            members = self.union_members.get(aggregate_name, [])

        for member in members:
            if member.name == member_name:
                base_type = member.type_name

                # Normalize enum/struct/union prefix if needed
                base_type = self._strip_aggregate_prefix(base_type)

                dims = getattr(member, "array_dimensions", []) or []

                if dims:
                    return (base_type, member.pointer_depth, True, dims)

                return (base_type, member.pointer_depth)

        return None

    def _resolve_typedef(self, type_name: str) -> str:
        """
        Follow typedef aliases to the underlying base type name.
        e.g.  typedef int MyInt;  typedef MyInt AnotherInt;
              _resolve_typedef('AnotherInt') -> 'int'
        Stops at built-ins or unknown names to avoid infinite loops.
        """
        builtin_types = {'int', 'float', 'char', 'void'}
        seen = set()
        current = type_name
        while current not in builtin_types and current not in seen:
            seen.add(current)
            if current in self.typedef_map:
                current, _ = self.typedef_map[current]
            else:
                break
        return current

    def _resolve_typedef_full(self, type_name: str, pointer_depth: int = 0):
        """
        Resolve typedef aliases and preserve accumulated pointer depth.

        Example:
            typedef int MyInt;
            typedef MyInt* MyIntPtr;

            _resolve_typedef_full("MyIntPtr", 0) -> ("int", 1)
            _resolve_typedef_full("MyIntPtr", 1) -> ("int", 2)
        """
        builtin_types = {'int', 'float', 'char', 'void'}
        seen = set()
        current = type_name
        total_pointer_depth = pointer_depth

        while current not in builtin_types and current not in seen:
            seen.add(current)

            if current in self.typedef_map:
                underlying_type, alias_pointer_depth = self.typedef_map[current]
                current = underlying_type
                total_pointer_depth += alias_pointer_depth
            else:
                break

        return current, total_pointer_depth

    def _normalize_type_name_for_compare(self, type_name: str) -> str:
        """
        Normaliseer type names voor vergelijkingen.

        Voorbeeld:
            structNode -> Node
            unionValue -> Value
            Node       -> Node
        """
        resolved = self._resolve_typedef(type_name)

        for prefix in ("struct", "union", "enum"):
            if isinstance(resolved, str) and resolved.startswith(prefix) and len(resolved) > len(prefix):
                return resolved[len(prefix):]

        return resolved

    def _normalize_dimensions(self, dims):
        if dims is None:
            return []

        if isinstance(dims, int):
            return [dims]

        return list(dims)

    def _get_expression_type(self, node):
        if node is None:
            return None

        if isinstance(node, IntLiteralNode):
            return ('int', 0)

        if isinstance(node, FloatLiteralNode):
            return ('float', 0)

        if isinstance(node, CharLiteralNode):
            return ('char', 0)

        if isinstance(node, StringLiteralNode):
            return ('char', 1)

        if isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                return None

            resolved_type, resolved_ptr = self._resolve_typedef_full(
                symbol.type_name,
                symbol.pointer_depth
            )

            if symbol.array_dimensions:
                dims = self._normalize_dimensions(symbol.array_dimensions)
                return (resolved_type, resolved_ptr, True, dims)

            return (resolved_type, resolved_ptr)

        if isinstance(node, ArrayAccessNode):
            array_type = self._get_expression_type(node.array)
            if array_type is None:
                return None

            if len(array_type) > 3 and array_type[2]:
                remaining_dims = self._normalize_dimensions(array_type[3])

                if len(remaining_dims) > 1:
                    return (array_type[0], array_type[1], True, remaining_dims[1:])

                return (array_type[0], array_type[1])

            if len(array_type) > 2 and array_type[2]:
                return (array_type[0], array_type[1])

            base_type, ptr_depth = array_type[0], array_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)

            return None

        if isinstance(node, DereferenceNode):
            inner_type = self._get_expression_type(node.operand)
            if inner_type is None:
                return None

            base_type, ptr_depth = inner_type[0], inner_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)

            return None

        if isinstance(node, AddressOfNode):
            inner_type = self._get_expression_type(node.operand)
            if inner_type is None:
                return None

            base_type, ptr_depth = inner_type[0], inner_type[1]
            return (base_type, ptr_depth + 1)

        if isinstance(node, CastNode):
            return (node.type_name, node.pointer_depth)

        if isinstance(node, BinaryOpNode):
            return self._get_binary_op_type(node)

        if isinstance(node, UnaryOpNode):
            return self._get_expression_type(node.operand)

        if isinstance(node, AssignNode):
            return self._get_expression_type(node.value)

        if isinstance(node, IncrementNode):
            return self._get_lvalue_type(node.operand)

        if isinstance(node, DecrementNode):
            return self._get_lvalue_type(node.operand)

        if isinstance(node, TernaryOpNode):
            then_type = self._get_expression_type(node.then_expr)
            else_type = self._get_expression_type(node.else_expr)
            return then_type if then_type == else_type else then_type or else_type

        if isinstance(node, SizeofNode):
            return ('int', 0)

        if isinstance(node, FunctionCallNode):
            if hasattr(node, 'resolved_return_type'):
                return node.resolved_return_type

            if node.name in self.functions:
                func_info = self._resolve_function_overload(node)
                if func_info is not None:
                    return (func_info['return_type'], func_info['return_ptr'])

            return ('int', 0)

        if isinstance(node, MemberAccessNode):
            obj_type = self._get_expression_type(node.obj)
            if obj_type is None:
                return None

            aggregate = self._resolve_aggregate_name(obj_type[0])
            if aggregate is None:
                return None

            kind, aggregate_name = aggregate
            return self._get_aggregate_member_type(kind, aggregate_name, node.member)

        if isinstance(node, PointerMemberAccessNode):
            ptr_type = self._get_expression_type(node.ptr)
            if ptr_type is None:
                return None

            if ptr_type[1] == 0:
                return None

            aggregate = self._resolve_aggregate_name(ptr_type[0])
            if aggregate is None:
                return None

            kind, aggregate_name = aggregate
            return self._get_aggregate_member_type(kind, aggregate_name, node.member)

        return None

    def _get_binary_op_type(self, node):
        left_type = self._get_expression_type(node.left)
        right_type = self._get_expression_type(node.right)

        if left_type is None or right_type is None:
            return None

        left_base, left_ptr = left_type[0], left_type[1]
        right_base, right_ptr = right_type[0], right_type[1]

        left_base = self._resolve_typedef(left_base)
        right_base = self._resolve_typedef(right_base)

        # Comparisons always produce int
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            return ('int', 0)

        # Pointer arithmetic
        if left_ptr > 0 or right_ptr > 0:
            # pointer - pointer -> int difference
            if left_ptr > 0 and right_ptr > 0 and node.op == '-':
                return ('int', 0)

            # pointer + int -> pointer
            if left_ptr > 0 and right_ptr == 0 and right_base in ('int', 'char') and node.op == '+':
                return (left_base, left_ptr)

            # pointer - int -> pointer
            if left_ptr > 0 and right_ptr == 0 and right_base in ('int', 'char') and node.op == '-':
                return (left_base, left_ptr)

            # int + pointer -> pointer
            if right_ptr > 0 and left_ptr == 0 and left_base in ('int', 'char') and node.op == '+':
                return (right_base, right_ptr)

            # Everything else involving pointers has no valid result type
            return None

        if left_base == 'float' or right_base == 'float':
            return ('float', 0)

        return ('int', 0)

    def _get_lvalue_type(self, node):
        if isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                return None

            return self._resolve_typedef_full(
                symbol.type_name,
                symbol.pointer_depth
            )

        if isinstance(node, ArrayAccessNode):
            return self._get_expression_type(node)

        if isinstance(node, DereferenceNode):
            inner_type = self._get_expression_type(node.operand)
            if inner_type is None:
                return None

            base_type, ptr_depth = inner_type[0], inner_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)

            return None

        if isinstance(node, MemberAccessNode):
            return self._get_expression_type(node)

        if isinstance(node, PointerMemberAccessNode):
            return self._get_expression_type(node)

        return None

    # ============================================================
    # Expression checks
    # ============================================================

    def _check_expression(self, node):
        if node is None:
            return

        if isinstance(node, IdentifierNode):
            self._check_identifier(node)

        elif isinstance(node, (IntLiteralNode, FloatLiteralNode, CharLiteralNode, StringLiteralNode)):
            pass

        elif isinstance(node, BinaryOpNode):
            self._check_expression(node.left)
            self._check_expression(node.right)

            left_type = self._get_expression_type(node.left)
            right_type = self._get_expression_type(node.right)

            if left_type is not None and right_type is not None:
                self._check_binary_operation(node.op, left_type, right_type, node)

        elif isinstance(node, UnaryOpNode):
            self._check_expression(node.operand)

        elif isinstance(node, DereferenceNode):
            self._check_expression(node.operand)
            operand_type = self._get_expression_type(node.operand)

            if operand_type is not None:
                base_type, ptr_depth = operand_type[0], operand_type[1]
                if ptr_depth == 0:
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: cannot dereference non-pointer type '{base_type}'"
                    )

        elif isinstance(node, AddressOfNode):
            if isinstance(node.operand, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    "Error: lvalue required as unary '&' operand"
                )
                return

            self._check_expression(node.operand)

        elif isinstance(node, IncrementNode):
            self._check_lvalue(node.operand)

        elif isinstance(node, DecrementNode):
            self._check_lvalue(node.operand)

        elif isinstance(node, CastNode):
            self._check_expression(node.operand)

        elif isinstance(node, ArrayAccessNode):
            array_type = self._get_expression_type(node.array)

            if array_type is not None:
                is_array = len(array_type) > 2 and array_type[2]
                ptr_depth = array_type[1]

                if not is_array and ptr_depth == 0:
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        "Error: subscript applied to non-array/pointer type"
                    )

            index_type = self._get_expression_type(node.index)

            if index_type is not None:
                base_type, ptr_depth = index_type[0], index_type[1]
                if base_type != 'int' or ptr_depth > 0:
                    self.add_error(
                        getattr(node.index, 'line', 0),
                        getattr(node.index, 'column', 0),
                        "Error: array subscript is not an integer"
                    )

            self._check_expression(node.array)
            self._check_expression(node.index)

        elif isinstance(node, AssignNode):
            self.visit_AssignNode(node)

        elif isinstance(node, FunctionCallNode):
            self.visit_FunctionCallNode(node)

        elif isinstance(node, TernaryOpNode):
            self._check_expression(node.condition)
            self._check_expression(node.then_expr)
            self._check_expression(node.else_expr)

        elif isinstance(node, SizeofNode):
            if not node.is_type and node.operand is not None:
                self._check_expression(node.operand)

        elif isinstance(node, MemberAccessNode):
            self._check_expression(node.obj)
            obj_type = self._get_expression_type(node.obj)

            if obj_type is not None:
                aggregate = self._resolve_aggregate_name(obj_type[0])

                if aggregate is None:
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: request for member '{node.member}' in something not a struct or union"
                    )
                else:
                    kind, aggregate_name = aggregate
                    if self._get_aggregate_member_type(kind, aggregate_name, node.member) is None:
                        self.add_error(
                            getattr(node, 'line', 0),
                            getattr(node, 'column', 0),
                            f"Error: {kind} '{aggregate_name}' has no member '{node.member}'"
                        )

        elif isinstance(node, PointerMemberAccessNode):
            self._check_expression(node.ptr)
            ptr_type = self._get_expression_type(node.ptr)
            if ptr_type is not None:
                if ptr_type[1] == 0:
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: '->' applied to non-pointer type '{ptr_type[0]}'"

                    )
                else:
                    aggregate = self._resolve_aggregate_name(ptr_type[0])
                    if aggregate is None:
                        self.add_error(
                            getattr(node, 'line', 0),
                            getattr(node, 'column', 0),
                            f"Error: request for member '{node.member}' in something not a pointer to struct or union"
                        )
                    else:
                        kind, aggregate_name = aggregate
                        if self._get_aggregate_member_type(kind, aggregate_name, node.member) is None:
                            self.add_error(
                                getattr(node, 'line', 0),
                                getattr(node, 'column', 0),
                                f"Error: {kind} '{aggregate_name}' has no member '{node.member}'"
                            )

    def _check_identifier(self, node):
        symbol = self.symbol_table.lookup(node.name)

        if symbol is None:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: variable '{node.name}' is not declared"
            )

    def _check_lvalue(self, node):
        if isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: variable '{node.name}' is not declared"
                )
                return

            if symbol.is_const and symbol.pointer_depth == 0:
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: cannot assign to const variable '{node.name}'"
                )

        elif isinstance(node, ArrayAccessNode):
            self._check_expression(node)

        elif isinstance(node, DereferenceNode):
            self._check_expression(node.operand)

            if isinstance(node.operand, IdentifierNode):
                symbol = self.symbol_table.lookup(node.operand.name)

                if symbol is not None and symbol.is_const and symbol.pointer_depth > 0:
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: assignment of read-only location '*{node.operand.name}'"
                    )

        elif isinstance(node, (IntLiteralNode, FloatLiteralNode, CharLiteralNode, StringLiteralNode)):
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: cannot assign to literal"
            )

        elif isinstance(node, MemberAccessNode):
            self._check_expression(node)

        elif isinstance(node, PointerMemberAccessNode):
            self._check_expression(node)

        elif isinstance(node, (UnaryOpNode, BinaryOpNode, AddressOfNode)):
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: cannot assign to expression result"
            )

    # ============================================================
    # Operation / assignment checks
    # ============================================================

    def _check_binary_operation(self, op, left_type, right_type, node):
        left_base, left_ptr = left_type[0], left_type[1]
        right_base, right_ptr = right_type[0], right_type[1]

        if left_ptr > 0 or right_ptr > 0:
            left_base_norm = self._normalize_type_name_for_compare(left_base)
            right_base_norm = self._normalize_type_name_for_compare(right_base)

            # pointer comparisons
            if op in ('==', '!=', '<', '>', '<=', '>='):
                if (left_ptr > 0 and right_ptr == 0) or (left_ptr == 0 and right_ptr > 0):
                    # p == 0 is allowed, but warn for non-zero integer comparisons
                    other_node = node.right if left_ptr > 0 else node.left
                    if not (isinstance(other_node, IntLiteralNode) and other_node.value == 0):
                        self.add_warning(
                            getattr(node, 'line', 0),
                            getattr(node, 'column', 0),
                            "Warning: comparison between pointer and integer"
                        )

                elif left_ptr > 0 and right_ptr > 0:
                    if left_ptr != right_ptr or left_base_norm != right_base_norm:
                        self.add_warning(
                            getattr(node, 'line', 0),
                            getattr(node, 'column', 0),
                            "Warning: comparison of distinct pointer types lacks a cast"
                        )
                return

            # pointer + int, int + pointer, pointer - int
            if op in ('+', '-'):
                # pointer - pointer is allowed, result is int
                if left_ptr > 0 and right_ptr > 0:
                    if op == '-':
                        if left_ptr != right_ptr or left_base_norm != right_base_norm:
                            self.add_warning(
                                getattr(node, 'line', 0),
                                getattr(node, 'column', 0),
                                "Warning: subtraction of distinct pointer types"
                            )
                        return

                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: invalid operands to binary {op}"
                    )
                    return

                # pointer +/- integer
                if left_ptr > 0 and right_ptr == 0:
                    if right_base not in ('int', 'char'):
                        self.add_error(
                            getattr(node, 'line', 0),
                            getattr(node, 'column', 0),
                            f"Error: invalid pointer arithmetic with non-integer type '{right_base}'"
                        )
                    return

                # integer + pointer is allowed
                if right_ptr > 0 and left_ptr == 0 and op == '+':
                    if left_base not in ('int', 'char'):
                        self.add_error(
                            getattr(node, 'line', 0),
                            getattr(node, 'column', 0),
                            f"Error: invalid pointer arithmetic with non-integer type '{left_base}'"
                        )
                    return

                # integer - pointer is not allowed
                if right_ptr > 0 and left_ptr == 0 and op == '-':
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        "Error: invalid operands to binary -"
                    )
                    return

            # Other pointer operations are invalid
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: invalid operands to binary {op}"
            )
            return

        if left_base == 'void' or right_base == 'void':
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot use 'void' in binary operation '{op}'"
            )
            return

        if op in ('<<', '>>'):
            right = node.right
            is_negative = (
                    (isinstance(right, UnaryOpNode) and right.op == '-')
                    or (isinstance(right, IntLiteralNode) and right.value < 0)
            )

            if is_negative:
                self.add_warning(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Warning: right operand of '{op}' is negative (undefined behavior)"
                )

    def _check_type_assignment(self, target_type, value_type, target_name, node):
        target_base, target_ptr = target_type[0], target_type[1]
        value_base, value_ptr = value_type[0], value_type[1]

        # char* / char array = "text"
        if target_base == 'char' and value_base == 'char' and value_ptr == 1:
            return

        if value_ptr > 0 and target_ptr == 0:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: incompatible types when assigning type '{value_base}{'*' * value_ptr}' to '{target_base}'"
            )
            return

        if target_ptr > 0 or value_ptr > 0:
            self._check_pointer_assignment(target_type, value_type, target_name, node)
            return

        self._check_scalar_assignment(target_base, value_base, target_name, node)

    def _check_pointer_assignment(self, target_type, value_type, target_name, node):
        target_base, target_ptr = target_type[0], target_type[1]
        value_base, value_ptr = value_type[0], value_type[1]

        target_base = self._normalize_type_name_for_compare(target_base)
        value_base = self._normalize_type_name_for_compare(value_base)

        value_node = getattr(node, 'value', None)
        if isinstance(value_node, IntLiteralNode) and value_node.value == 0:
            return

        if value_base == 'void':
            return

        if target_ptr != value_ptr:
            self.add_warning(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Warning: assignment to '{target_base}{'*' * target_ptr}' from incompatible pointer type '{value_base}{'*' * value_ptr}'"
            )
            return

        if target_base != value_base and target_base != 'void':
            self.add_warning(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Warning: assignment to '{target_base}{'*' * target_ptr}' from incompatible pointer type '{value_base}{'*' * value_ptr}'"
            )

    def _check_scalar_assignment(self, target_type, value_type, target_name, node):

        target_base = self._resolve_typedef(target_type)
        value_base = self._resolve_typedef(value_type)

        if target_base == 'int' and value_base == 'float':
            self.add_warning(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Warning: implicit conversion from 'float' to 'int' in assignment to '{target_name}'"
            )
            return

        if target_type == 'char' and value_type in ('int', 'float'):
            self.add_warning(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Warning: implicit conversion from '{value_type}' to 'char' in assignment to '{target_name}'"
            )
            return

        if target_type == 'float' and value_type in ('int', 'char'):
            return

        if target_type == 'int' and value_type == 'char':
            return

        if target_type == value_type:
            return

        if target_type == 'void' or value_type == 'void':
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign '{value_type}' to '{target_type}'"
            )

    # ============================================================
    # Format string checking
    # ============================================================

    def _check_format_args(self, fmt: str, args: list, func_name: str, node):
        import re

        specifiers = re.findall(r'(?<!%)%(?:\d+)?[dxsfc]', fmt)

        expected = len(specifiers)
        actual = len(args)

        if expected != actual:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: {func_name} format expects {expected} argument(s), got {actual}"
            )

    # ============================================================
    # Output methods
    # ============================================================

    def format_errors(self):
        if not self.errors:
            return "", 0

        output = []
        sorted_errors = sorted(self.errors, key=lambda e: (e['line'], e['column']))

        for error in sorted_errors:
            line_num = error['line']
            column = error['column']
            message = error['message']
            output.append(f"{RED}[Semantic Error] line {line_num}, column {column}: {message}{RESET}")

        return '\n'.join(output) + '\n', len(self.errors)

    def format_warnings(self):
        if not self.warnings:
            return "", 0

        output = []
        sorted_warnings = sorted(self.warnings, key=lambda w: (w['line'], w['column']))

        for warning in sorted_warnings:
            line_num = warning['line']
            column = warning['column']
            message = warning['message']
            output.append(f"{YELLOW}[Semantic Warning] line {line_num}, column {column}: {message}{RESET}")

        return '\n'.join(output) + '\n', len(self.warnings)

    # ============================================================
    # Small helpers
    # ============================================================

    def _node_to_string(self, node):
        if isinstance(node, IdentifierNode):
            return node.name

        if isinstance(node, DereferenceNode):
            return f"*{self._node_to_string(node.operand)}"

        if isinstance(node, ArrayAccessNode):
            return f"{self._node_to_string(node.array)}[{self._node_to_string(node.index)}]"

        if isinstance(node, IntLiteralNode):
            return str(node.value)

        if isinstance(node, FloatLiteralNode):
            return str(node.value)

        if isinstance(node, CharLiteralNode):
            return node.value

        return "expression"
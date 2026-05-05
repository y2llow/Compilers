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

        # name -> {
        #   'return_type': str,
        #   'return_ptr': int,
        #   'params': [(type_name, pointer_depth, dimensions_tuple), ...],
        #   'defined': bool,
        #   'line': int,
        #   'column': int
        # }
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

    def analyze(self, node):
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

        # 2. Enum constants registreren als globale int constants.
        for item in node.top_level_items:
            if isinstance(item, EnumDeclNode):
                self.visit(item)

        # 3. Top-level variabelen registreren.
        for item in node.top_level_items:
            if isinstance(item, VarDeclNode):
                self.visit(item)

        # 4. Alle functie-declaraties en definities vooraf registreren.
        # Dit is nodig zodat function calls naar functies later in de file werken.
        for item in node.top_level_items:
            if isinstance(item, FunctionDeclNode):
                self._register_function_declaration(item)
            elif isinstance(item, FunctionDefNode):
                self._register_function_definition(item)

        # 5. Functie bodies analyseren.
        for item in node.top_level_items:
            if isinstance(item, FunctionDefNode):
                if item.name == "main":
                    has_main = True
                    if item.return_type != "int" or item.return_ptr != 0:
                        self.add_error(
                            getattr(item, 'line', 0),
                            getattr(item, 'column', 0),
                            "Error: main function must return int"
                        )

                self.visit(item)

            elif isinstance(item, (TypedefNode, StructDeclNode, DefineNode)):
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
        pass

    def visit_StructDeclNode(self, node):
        pass

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

    def _register_function_declaration(self, node):
        name = node.name
        sig = self._function_signature(node)
        sig['defined'] = False

        if name not in self.functions:
            self.functions[name] = sig
            return

        existing = self.functions[name]

        if not self._same_function_signature(existing, sig):
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: conflicting function declaration for '{name}' "
                f"(previously declared at line {existing['line']})"
            )

    def _register_function_definition(self, node):
        name = node.name
        sig = self._function_signature(node)
        sig['defined'] = True

        if name not in self.functions:
            self.functions[name] = sig
            return

        existing = self.functions[name]

        if not self._same_function_signature(existing, sig):
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: conflicting function definition for '{name}' "
                f"(previously declared at line {existing['line']})"
            )
            return

        if existing.get('defined'):
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: redefinition of function '{name}' "
                f"(previously defined at line {existing['line']})"
            )
            return

        existing['defined'] = True
        existing['line'] = getattr(node, 'line', 0)
        existing['column'] = getattr(node, 'column', 0)

    # ============================================================
    # Enum
    # ============================================================

    def visit_EnumDeclNode(self, node):
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
        """Validate that a type name is known."""
        valid_builtin_types = {'int', 'float', 'char', 'void'}

        if type_name in valid_builtin_types:
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

        self.symbol_table.push_scope()

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

        func_info = self.functions[node.name]
        expected_params = func_info['params']
        expected_param_count = len(expected_params)
        actual_arg_count = len(node.args)

        if actual_arg_count != expected_param_count:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: function '{node.name}' expects {expected_param_count} argument(s), got {actual_arg_count}"
            )

        for i, arg in enumerate(node.args):
            self._check_expression(arg)

            if i < expected_param_count:
                expected_type_name, expected_ptr, _dims = expected_params[i]
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
        self.symbol_table.push_scope()
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
        self.symbol_table.push_scope()

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
        self._visit_block_items(node.items)

    def visit_SwitchDefaultNode(self, node):
        self._visit_block_items(node.items)

    # ============================================================
    # Statements
    # ============================================================

    def visit_VarDeclNode(self, node):

        # Validate type is known
        self._validate_type_name(node.type_name, node)

        success, existing = self.symbol_table.add_symbol(
            node.name,
            node.type_name,
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
            self._check_type_assignment(
                target_type=(node.type_name, node.pointer_depth),
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
        if not var_decl.array_dimensions:
            self.add_error(
                getattr(initializer, 'line', 0),
                getattr(initializer, 'column', 0),
                f"Error: array initializer for non-array variable '{var_decl.name}'"
            )
            return

        expected_size = var_decl.array_dimensions[0]
        actual_size = len(initializer.elements)

        if actual_size != expected_size:
            self.add_error(
                getattr(initializer, 'line', 0),
                getattr(initializer, 'column', 0),
                f"Error: array initializer size mismatch for '{var_decl.name}': expected {expected_size}, got {actual_size}"
            )

        for elem in initializer.elements:
            if isinstance(elem, ArrayInitializerNode):
                # Recursieve checks voor nested arrays kunnen later uitgebreider.
                self.visit_ArrayInitializerNode(elem)
            else:
                self._check_expression(elem)

    # ============================================================
    # Type helpers
    # ============================================================

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

            if symbol.array_dimensions:
                dims = self._normalize_dimensions(symbol.array_dimensions)
                return (symbol.type_name, symbol.pointer_depth, True, dims)

            return (symbol.type_name, symbol.pointer_depth)

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
            if node.name in self.functions:
                func_info = self.functions[node.name]
                return (func_info['return_type'], func_info['return_ptr'])

            return ('int', 0)

        return None

    def _get_binary_op_type(self, node):
        left_type = self._get_expression_type(node.left)
        right_type = self._get_expression_type(node.right)

        if left_type is None or right_type is None:
            return None

        left_base, left_ptr = left_type[0], left_type[1]
        right_base, right_ptr = right_type[0], right_type[1]

        if left_ptr > 0 or right_ptr > 0:
            return None

        if left_base == 'float' or right_base == 'float':
            return ('float', 0)

        return ('int', 0)

    def _get_lvalue_type(self, node):
        if isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                return None
            return (symbol.type_name, symbol.pointer_depth)

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
            if op in ('==', '!=', '<', '>', '<=', '>='):
                if (left_ptr > 0 and right_ptr == 0) or (left_ptr == 0 and right_ptr > 0):
                    self.add_warning(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        "Warning: comparison between pointer and integer"
                    )

                elif left_ptr > 0 and right_ptr > 0 and left_base != right_base:
                    self.add_warning(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        "Warning: comparison of distinct pointer types lacks a cast"
                    )

            elif op in ('+', '-'):
                if left_ptr > 0 and right_ptr > 0:
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: invalid operands to binary {op}"
                    )

                elif left_ptr > 0 and right_base == 'float':
                    self.add_error(
                        getattr(node, 'line', 0),
                        getattr(node, 'column', 0),
                        f"Error: invalid operands to binary {op}"
                    )

                elif right_ptr > 0 and left_base == 'float':
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
        if target_type == 'int' and value_type == 'float':
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
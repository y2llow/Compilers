# ============================================================
# Semantic Analyzer with Complete Type Checking
# ============================================================
from parser.semantics.symbol_table import SymbolTable
from parser.ast_nodes import *
# ANSI color codes
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


class SemanticAnalyzer:
    """
    Semantische analysator voor de AST met VOLLEDIG type checking.

    Controleert:
    1. Gebruik van niet-gedeclareerde variabelen
    2. Redeclaratie van bestaande variabelen (in dezelfde scope)
    3. Incompatibele type operaties/toewijzingen
    4. Toewijzing aan rvalue
    5. Toewijzing aan const variabelen
    6. Array index type (moet int zijn)
    7. Array initializer length matching
    """

    # Type compatibility table
    # Welke types kunnen naar welke types converteren?
    TYPE_COMPATIBILITY = {
        'int': {'int', 'float', 'char'},  # int kan naar int, float, char
        'float': {'float', 'int'},  # float kan naar float, int
        'char': {'char', 'int'},  # char kan naar char, int
        'void': set(),  # void is incompatibel
    }

    # Pointer-to-type compatibility
    # int* kan NIET automatisch naar float* gaan
    POINTER_COMPATIBILITY = {
        'int': {'int'},  # int* kan alleen naar int*
        'float': {'float'},  # float* kan alleen naar float*
        'char': {'char'},  # char* kan alleen naar char*
        'void': {'int', 'float', 'char'},  # void* kan naar alles
    }

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.stdio_included = False

    def add_error(self, line, column, message):
        """Voeg semantische fout toe"""
        self.errors.append({
            'line': line,
            'column': column,
            'message': message
        })

    def add_warning(self, line, column, message):
        """Voeg waarschuwing toe"""
        self.warnings.append({
            'line': line,
            'column': column,
            'message': message
        })

    # ── Public entry point ────────────────────────────────────

    def analyze(self, node):
        """
        Voer semantische analyse uit op de AST.
        Retourneert True als geen fouten, False anders.
        """
        self.visit(node)
        return len(self.errors) == 0

    # ── Internal dispatch ─────────────────────────────────────

    def visit(self, node):
        """Visit een AST node"""
        if node is None:
            return

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node):
        """Fallback als er geen specifieke visitor is"""
        pass

    # ── Program structure ─────────────────────────────────────


    def visit_MainFunctionNode(self, node):
        """Bezoek main functie - maak nieuwe scope"""
        # Push scope voor main function
        self.symbol_table.push_scope()

        # Visit alle statements
        for stmt in node.statements:
            self.visit(stmt)

        # Pop scope
        self.symbol_table.pop_scope()

    def visit_ReturnNode(self, node):
        """Bezoek return statement"""
        # Check de return expressie (als aanwezig)
        if node.value is not None:
            self._check_expression(node.value)

    # ── Statements ────────────────────────────────────────────

    def visit_VarDeclNode(self, node):
        """Bezoek variabele declaratie"""
        # Probeer variabele toe te voegen aan symbol table
        success, existing = self.symbol_table.add_symbol(
            node.name,
            node.type_name,
            node.pointer_depth,
            node.is_const,
            line=getattr(node, 'line', 0),
            column=getattr(node, 'column', 0),
            array_dimensions=node.array_dimensions  # NEW: pass array dims
        )

        if not success:
            # Redeclaratie error
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: variable '{node.name}' already declared at line {existing.line}, column {existing.column}"
            )

        # Check de initializer expressie (als aanwezig)
        if node.value is not None:
            # Handle array initializers
            if isinstance(node.value, ArrayInitializerNode):
                self._check_array_initializer(node, node.value)
            else:
                value_type = self._get_expression_type(node.value)

                # Check type compatibiliteit
                if value_type is not None and success:  # Alleen als geen redeclaratie
                    self._check_type_assignment(
                        target_type=(node.type_name, node.pointer_depth),
                        value_type=value_type,
                        target_name=node.name,
                        node=node
                    )

    def _check_array_initializer(self, var_decl, initializer):
        """
        Check array initializer:
        - Size moet matchen met array declaration
        - Elements moeten correct type zijn
        """
        if not var_decl.array_dimensions:
            self.add_error(
                getattr(initializer, 'line', 0),
                getattr(initializer, 'column', 0),
                f"Error: array initializer for non-array variable '{var_decl.name}'"
            )
            return

        # Check eerste dimensie
        expected_size = var_decl.array_dimensions[0]
        actual_size = len(initializer.elements)

        if actual_size != expected_size:
            self.add_error(
                getattr(initializer, 'line', 0),
                getattr(initializer, 'column', 0),
                f"Error: array initializer size mismatch for '{var_decl.name}': expected {expected_size}, got {actual_size}"
            )

        # TODO: Check multidimensional array initializers
        # For now, just check that all elements are literals
        for elem in initializer.elements:
            if isinstance(elem, ArrayInitializerNode):
                # Nested initializer for multidimensional arrays
                pass
            elif not isinstance(elem, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
                self.add_warning(
                    getattr(elem, 'line', 0),
                    getattr(elem, 'column', 0),
                    f"Warning: array initializer contains non-literal element"
                )

    def visit_AssignNode(self, node):
        """Bezoek toewijzing"""
        # Check linker kant (target) - moet lvalue zijn
        self._check_lvalue(node.target)

        # Get target type
        target_type = self._get_lvalue_type(node.target)

        # Get value type
        value_type = self._get_expression_type(node.value)

        # Check type compatibiliteit
        if target_type is not None and value_type is not None:
            self._check_type_assignment(
                target_type=target_type,
                value_type=value_type,
                target_name=self._node_to_string(node.target),
                node=node
            )

    def visit_BinaryOpNode(self, node):
        """Bezoek binaire operatie"""
        left_type = self._get_expression_type(node.left)
        right_type = self._get_expression_type(node.right)

        # Check of beide operanden dezelfde (compatibele) types hebben
        if left_type is not None and right_type is not None:
            self._check_binary_operation(
                op=node.op,
                left_type=left_type,
                right_type=right_type,
                node=node
            )

    def visit_UnaryOpNode(self, node):
        """Bezoek unaire operatie"""
        self._check_expression(node.operand)

    def visit_DereferenceNode(self, node):
        """Bezoek dereference operatie"""
        expr_type = self._get_expression_type(node.operand)

        # Dereference vereist een pointer
        if expr_type is not None:
            base_type, ptr_depth = expr_type
            if ptr_depth == 0:
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: cannot dereference non-pointer type '{base_type}'"
                )

    def visit_AddressOfNode(self, node):
        """Bezoek address-of operatie"""
        self._check_expression(node.operand)

    def visit_IncrementNode(self, node):
        """Bezoek increment operatie"""
        self._check_lvalue(node.operand)

    def visit_DecrementNode(self, node):
        """Bezoek decrement operatie"""
        self._check_lvalue(node.operand)

    def visit_CastNode(self, node):
        """Bezoek cast operatie"""
        expr_type = self._get_expression_type(node.operand)
        # Casts zijn altijd toegestaan (C philosophy)
        # Maar we kunnen een warning geven
        self._check_expression(node.operand)

    def visit_ArrayAccessNode(self, node):
        """Bezoek array access: arr[index]"""
        # Check dat het array is
        array_type = self._get_expression_type(node.array)
        if array_type is not None:
            base_type, ptr_depth, is_array = array_type if len(array_type) > 2 else (*array_type, False)
            if not is_array and ptr_depth == 0:
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: subscript applied to non-array/pointer type"
                )

        # Check dat index int is
        index_type = self._get_expression_type(node.index)
        if index_type is not None:
            base_type, ptr_depth = index_type
            if base_type != 'int' or ptr_depth > 0:
                self.add_error(
                    getattr(node.index, 'line', 0),
                    getattr(node.index, 'column', 0),
                    f"Error: array subscript is not an integer"
                )

        self._check_expression(node.array)
        self._check_expression(node.index)

    def visit_ArrayInitializerNode(self, node):
        """Bezoek array initializer"""
        for elem in node.elements:
            self._check_expression(elem)

    # ── Type Checking Methods ─────────────────────────────────

    def _get_expression_type(self, node):
        """
        Bepaal het type van een expressie.
        Retourneert: (type_name, pointer_depth) of None

        Voorbeelden:
            IntLiteralNode(5) → ('int', 0)
            FloatLiteralNode(3.14) → ('float', 0)
            IdentifierNode('x') → ('int', 1) als x is int*
        """
        if node is None:
            return None

        if isinstance(node, IntLiteralNode):
            return ('int', 0)

        elif isinstance(node, FloatLiteralNode):
            return ('float', 0)

        elif isinstance(node, CharLiteralNode):
            return ('char', 0)

        elif isinstance(node, StringLiteralNode):
            return ('char', 1)

        elif isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                return None
            # Return array info if applicable
            if symbol.array_dimensions:
                return (symbol.type_name, symbol.pointer_depth, True)
            return (symbol.type_name, symbol.pointer_depth)

        elif isinstance(node, ArrayAccessNode):
            # arr[i] has type of base array element
            array_type = self._get_expression_type(node.array)
            if array_type is None:
                return None
            if len(array_type) > 2 and array_type[2]:  # is_array
                # Strip one dimension
                return (array_type[0], array_type[1])
            # If it's a pointer, dereference it
            base_type, ptr_depth = array_type[0], array_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)
            return None

        elif isinstance(node, DereferenceNode):
            # *ptr: als ptr is int*, dan type is int
            inner_type = self._get_expression_type(node.operand)
            if inner_type is None:
                return None
            base_type, ptr_depth = inner_type[0], inner_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)
            return None

        elif isinstance(node, AddressOfNode):
            # &x: als x is int, dan type is int*
            inner_type = self._get_expression_type(node.operand)
            if inner_type is None:
                return None
            base_type, ptr_depth = inner_type[0], inner_type[1]
            return (base_type, ptr_depth + 1)

        elif isinstance(node, CastNode):
            # (int) x: type is int
            return (node.type_name, node.pointer_depth)

        elif isinstance(node, BinaryOpNode):
            # Type van binaire operatie
            return self._get_binary_op_type(node)

        elif isinstance(node, UnaryOpNode):
            # Type van unaire operatie
            return self._get_expression_type(node.operand)

        elif isinstance(node, AssignNode):
            # Type van assignment is type van value
            return self._get_expression_type(node.value)

        return None

    def _get_binary_op_type(self, node):
        """Bepaal type van binaire operatie"""
        left_type = self._get_expression_type(node.left)
        right_type = self._get_expression_type(node.right)

        if left_type is None or right_type is None:
            return None

        left_base, left_ptr = left_type[0], left_type[1]
        right_base, right_ptr = right_type[0], right_type[1]

        # Pointers kunnen niet gearithmetiseerd worden
        if left_ptr > 0 or right_ptr > 0:
            return None

        # float OP float → float
        if left_base == 'float' or right_base == 'float':
            return ('float', 0)

        # int OP int → int (ook char)
        return ('int', 0)

    def _get_lvalue_type(self, node):
        """Bepaal type van een lvalue (assignment target)"""
        if isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                return None
            return (symbol.type_name, symbol.pointer_depth)

        elif isinstance(node, ArrayAccessNode):
            # arr[i] = value; — type is base element type
            array_type = self._get_expression_type(node.array)
            if array_type is None:
                return None
            if len(array_type) > 2 and array_type[2]:  # is_array
                return (array_type[0], array_type[1])
            base_type, ptr_depth = array_type[0], array_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)
            return None

        elif isinstance(node, DereferenceNode):
            inner_type = self._get_expression_type(node.operand)
            if inner_type is None:
                return None
            base_type, ptr_depth = inner_type[0], inner_type[1]
            if ptr_depth > 0:
                return (base_type, ptr_depth - 1)
            return None

        return None

    def _check_type_assignment(self, target_type, value_type, target_name, node):
        """
        Check of assignment type-compatibel is.

        target_type: (type_name, pointer_depth) waar we naar toewijzen
        value_type: (type_name, pointer_depth) wat we toewijzen
        """
        target_base, target_ptr = target_type[0], target_type[1]
        value_base, value_ptr = value_type[0], value_type[1]

        # Allow string assignment to char array: char buf[50] = "test"
        if target_base == 'char' and target_ptr == 0 and value_base == 'char' and value_ptr == 1:
            return

        # Pointer assignments
        if target_ptr > 0 or value_ptr > 0:
            self._check_pointer_assignment(
                target_type, value_type, target_name, node
            )
            return

        # Non-pointer assignments
        self._check_scalar_assignment(
            target_base, value_base, target_name, node
        )

    def _check_pointer_assignment(self, target_type, value_type, target_name, node):
        """Check pointer-to-pointer assignments"""
        target_base, target_ptr = target_type[0], target_type[1]
        value_base, value_ptr = value_type[0], value_type[1]

        # void* kan naar alles
        if value_base == 'void':
            return

        # Moet exact hetzelfde aantal sterren hebben
        if target_ptr != value_ptr:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign pointer depth {value_ptr} to pointer depth {target_ptr}"
            )
            return

        # Types moeten compatibel zijn
        if target_base != value_base and target_base != 'void':
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign '{value_base}{'*' * value_ptr}' to '{target_base}{'*' * target_ptr}'"
            )

    def _check_scalar_assignment(self, target_type, value_type, target_name, node):
        """Check scalar (non-pointer) assignments"""
        # int = float: warning
        if target_type == 'int' and value_type == 'float':
            self.add_warning(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Warning: implicit conversion from 'float' to 'int' in assignment to '{target_name}'"
            )
            return

        # float = int: OK (implicit conversion)
        if target_type == 'float' and value_type == 'int':
            return

        # int/char/float = int/char/float: OK (implicit conversion)
        if target_type in ('int', 'char', 'float') and value_type in ('int', 'char', 'float'):
            return

        # void type: error
        if target_type == 'void' or value_type == 'void':
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign '{value_type}' to '{target_type}'"
            )

    def _check_binary_operation(self, op, left_type, right_type, node):
        """Check binary operatie type compatibiliteit"""
        left_base, left_ptr = left_type[0], left_type[1]
        right_base, right_ptr = right_type[0], right_type[1]

        # Pointers kunnen niet gearithmetiseerd worden (behalve somige operaties)
        if left_ptr > 0 or right_ptr > 0:
            # Pointer arithmetic is complex, skip voor nu
            return

        # Beide operanden moeten scalaire types zijn
        if left_base == 'void' or right_base == 'void':
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot use 'void' in binary operation '{op}'"
            )
            return

    # ── Expression checking ───────────────────────────────────

    def _check_expression(self, node):
        """Controleer of expressie geldig is"""
        if node is None:
            return

        if isinstance(node, IdentifierNode):
            self._check_identifier(node)
        elif isinstance(node, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
            # Literals zijn altijd OK
            pass
        elif isinstance(node, BinaryOpNode):
            self._check_expression(node.left)
            self._check_expression(node.right)
        elif isinstance(node, UnaryOpNode):
            self._check_expression(node.operand)
        elif isinstance(node, DereferenceNode):
            self._check_expression(node.operand)
        elif isinstance(node, AddressOfNode):
            self._check_expression(node.operand)
        elif isinstance(node, IncrementNode):
            self._check_expression(node.operand)
        elif isinstance(node, DecrementNode):
            self._check_expression(node.operand)
        elif isinstance(node, CastNode):
            self._check_expression(node.operand)
        elif isinstance(node, ArrayAccessNode):
            self._check_expression(node.array)
            self._check_expression(node.index)
        elif isinstance(node, AssignNode):
            # Toewijzing als expressie (zoals in C mogelijk)
            self._check_lvalue(node.target)
            self._check_expression(node.value)

    def _check_identifier(self, node):
        """
        Controleer of identifier geldig is (gedeclareerd).
        Errors:
        - Variabele niet gedeclareerd
        """
        symbol = self.symbol_table.lookup(node.name)

        if symbol is None:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: variable '{node.name}' is not declared"
            )

    def _check_lvalue(self, node):
        """
        Controleer of een node een geldig lvalue is.
        Errors:
        - Niet-gedeclareerde variabele
        - Toewijzing aan const variabele
        - Toewijzing aan literal/rvalue
        """
        if isinstance(node, IdentifierNode):
            # Check of variabele gedeclareerd is
            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: variable '{node.name}' is not declared"
                )
                return

            # Check of variabele const is
            if symbol.is_const:
                self.add_error(
                    getattr(node, 'line', 0),
                    getattr(node, 'column', 0),
                    f"Error: cannot assign to const variable '{node.name}'"
                )

        elif isinstance(node, ArrayAccessNode):
            # arr[i] is an lvalue, but we need to check both parts
            self._check_expression(node.array)
            self._check_expression(node.index)

        elif isinstance(node, DereferenceNode):
            # Dereference kann lvalue sein, aber we moeten the operand checken
            self._check_expression(node.operand)

        elif isinstance(node, (IntLiteralNode, FloatLiteralNode, CharLiteralNode)):
            # Kan niet toewijzen aan literal
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign to literal"
            )

        elif isinstance(node, UnaryOpNode):
            # Unaire operaties kunnen rvalue zijn
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign to expression result"
            )

        elif isinstance(node, BinaryOpNode):
            # Binaire operaties kunnen rvalue zijn
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign to expression result"
            )

        elif isinstance(node, AddressOfNode):
            # & gives rvalue
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: cannot assign to expression result"
            )

    # ── Helper methods ────────────────────────────────────────

    def _node_to_string(self, node):
        """Convert AST node to string representation"""
        if isinstance(node, IdentifierNode):
            return node.name
        elif isinstance(node, DereferenceNode):
            return f"*{self._node_to_string(node.operand)}"
        elif isinstance(node, ArrayAccessNode):
            return f"{self._node_to_string(node.array)}[{self._node_to_string(node.index)}]"
        elif isinstance(node, IntLiteralNode):
            return str(node.value)
        elif isinstance(node, FloatLiteralNode):
            return str(node.value)
        else:
            return "expression"

    # ── Output methods ────────────────────────────────────────

    def format_errors(self):
        """
        Format alle fouten voor output.
        Retourneert (output_string, error_count)
        """
        if not self.errors:
            return "", 0

        output = []

        # Sort errors by line number
        sorted_errors = sorted(self.errors, key=lambda e: (e['line'], e['column']))

        for error in sorted_errors:
            line_num = error['line']
            column = error['column']
            message = error['message']

            output.append(f"{RED}[Semantic Error] line {line_num}, column {column}: {message}{RESET}")

        return '\n'.join(output) + '\n', len(self.errors)

    def format_warnings(self):
        """
        Format alle waarschuwingen voor output.
        Retourneert (output_string, warning_count)
        """
        if not self.warnings:
            return "", 0

        output = []

        # Sort warnings by line number
        sorted_warnings = sorted(self.warnings, key=lambda w: (w['line'], w['column']))

        for warning in sorted_warnings:
            line_num = warning['line']
            column = warning['column']
            message = warning['message']

            output.append(f"{YELLOW}[Semantic Warning] line {line_num}, column {column}: {message}{RESET}")

        return '\n'.join(output) + '\n', len(self.warnings)

    # ── include methods ────────────────────────────────────────

    def visit_ProgramNode(self, node):
        # Check includes first
        for inc in node.includes:
            self.visit(inc)
        # Then analyse main
        self.visit(node.main_function)

    def visit_IncludeNode(self, node):
        if node.header == 'stdio.h':
            self.stdio_included = True

    def visit_PrintfNode(self, node):
        if not self.stdio_included:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                "Error: 'printf' used without #include <stdio.h>"
            )
            return
        # Validate format string vs argument count
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

    def _check_format_args(self, fmt: str, args: list, func_name: str, node):
        """Count format specifiers (%d, %f, %s, %c, %x) and compare to arg count."""
        import re
        # Match %[width][code] but not %%
        specifiers = re.findall(r'(?<!%)%(?:\d+)?[dxsfc]', fmt)
        expected = len(specifiers)
        actual = len(args)
        if expected != actual:
            self.add_error(
                getattr(node, 'line', 0),
                getattr(node, 'column', 0),
                f"Error: {func_name} format expects {expected} argument(s), got {actual}"
            )
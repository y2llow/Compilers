"""
LLVM IR Code Generator - WITH COMMENT SUPPORT
======================

Vertaalt AST naar LLVM IR code.

"""

from llvmlite import ir
import llvmlite.binding as llvm
from parser.ast_nodes import (
    ProgramNode,
    IncludeNode,
    FunctionDeclNode,
    FunctionDefNode,
    ReturnNode,
    IntLiteralNode,
    FloatLiteralNode,
    VarDeclNode,
    AssignNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
    IncrementNode,
    DecrementNode,
    AddressOfNode,
    DereferenceNode,
    CastNode,
    ArrayAccessNode,
    ArrayInitializerNode,
    CharLiteralNode,
    IfNode,
    WhileNode,
    ForNode,
    BreakNode,
    ContinueNode,
    SwitchNode,
    TernaryOpNode,
    SwitchCaseNode,
    SwitchDefaultNode,
    CompoundStmtNode,
)


class LLVMGenerator:
    """
    Genereert LLVM IR code uit een AST.

    Gebruik:
        generator = LLVMGenerator()
        llvm_ir = generator.generate(ast)

        # Schrijf naar bestand
        with open('output.ll', 'w') as f:
            f.write(llvm_ir)
    """

    def __init__(self):
        # Maak een nieuwe LLVM module (= een bestand)
        self.module = ir.Module(name="main_module")
        self.module.triple = llvm.get_default_triple()

        # Builder wordt gebruikt om instructies toe te voegen
        self.builder = None

        # Symbol table: variabele naam -> LLVM waarde
        self.variables = {}

        # Maps: line_number -> {'source': str, 'leading': list, 'inline': str}
        self.line_to_comment = {}
        self.comment_order = []  # Track order of statements

        self.string_counter = 0

        self.loop_stack = []

        self.printf_func = None
        self.scanf_func = None

    # ═══════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════

    def generate(self, ast: ProgramNode) -> str:
        """
        Genereer LLVM IR code uit de AST.

        Returns:
            String met LLVM IR code
        """
        # Bezoek de AST
        self.visit(ast)

        # Return de gegenereerde LLVM IR als string
        raw_llvm = str(self.module)

        llvm_with_comments = self._add_comments_to_llvm(raw_llvm)

        return llvm_with_comments

    # ═══════════════════════════════════════════════════════════
    # COMMENT HANDLING
    # ═══════════════════════════════════════════════════════════

    def _collect_comments(self, node):
        """Collect all comment info from AST node."""
        if not hasattr(node, 'line') or node.line == 0:
            return

        if node.line in self.line_to_comment:
            return

        source_line = getattr(node, 'source_line', '').strip()
        leading = getattr(node, 'leading_comments', [])
        inline = getattr(node, 'inline_comment', None)

        # Store all info
        self.line_to_comment[node.line] = {
            'source': source_line,
            'leading': leading,
            'inline': inline
        }
        self.comment_order.append(node.line)

    def _add_comments_to_llvm(self, llvm_ir):
        """Add source code comments to LLVM IR output."""
        if not self.line_to_comment:
            return llvm_ir

        lines = llvm_ir.split('\n')
        result = []

        in_main = False
        comment_idx = 0
        last_was_alloca = False  # Track if last instruction was alloca

        for line in lines:
            # Detect main function start
            if 'define i32 @main()' in line or 'define i32 @"main"()' in line:
                in_main = True
                # Add ALL comments (leading + source) to the right of define
                if comment_idx < len(self.comment_order):
                    stmt_line = self.comment_order[comment_idx]
                    info = self.line_to_comment[stmt_line]

                    # Build complete comment
                    comment_parts = [info["source"]]
                    for lead in info['leading']:
                        comment_parts.append(f'// {lead}')

                    result.append(f'{line}  ; {" ".join(comment_parts)}')
                    comment_idx += 1
                else:
                    result.append(line)
                continue

            # Detect main function end
            if in_main and line.strip() == '}':
                in_main = False
                result.append(line)
                continue

            # Skip non-instruction lines
            if not in_main or not line.strip() or line.strip() == '{' or line.strip() == 'entry:':
                result.append(line)
                continue

            # Check if this is a store instruction (skip comment if previous was alloca)
            is_store = 'store' in line

            if is_store and last_was_alloca:
                # This store belongs to previous alloca, no comment
                result.append(line)
                last_was_alloca = False
                continue

            # This is a "first" instruction for a statement - add comment
            if comment_idx < len(self.comment_order):
                stmt_line = self.comment_order[comment_idx]
                info = self.line_to_comment[stmt_line]

                # Build complete comment: source + all leading comments
                # NOTE: source_line already contains inline comments!
                comment_parts = [info['source']]
                for lead in info['leading']:
                    comment_parts.append(f'// {lead}')

                result.append(f'{line}  ; {" ".join(comment_parts)}')
                comment_idx += 1

                # Track if this was alloca
                last_was_alloca = 'alloca' in line
            else:
                result.append(line)
                last_was_alloca = False

        return '\n'.join(result)

    # ═══════════════════════════════════════════════════════════
    # VISITOR PATTERN
    # ═══════════════════════════════════════════════════════════

    def visit(self, node):
        """Dispatch naar de juiste visit methode."""
        if node is None:
            return None

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Fallback voor onbekende nodes."""
        raise NotImplementedError(
            f"LLVM generator heeft nog geen visit_{type(node).__name__} methode"
        )

    # ═══════════════════════════════════════════════════════════
    # PROGRAM & MAIN FUNCTION
    # ═══════════════════════════════════════════════════════════

    def visit_ProgramNode(self, node: ProgramNode):
        """
        Eerst alle functies declareren, daarna bodies genereren.
        Nodig voor forward declarations en recursive calls.
        """

        # Pass 1: includes skippen, alle function declarations/definitions registreren
        for item in node.top_level_items:
            if isinstance(item, IncludeNode):
                self._collect_comments(item)
                continue

            if isinstance(item, (FunctionDeclNode, FunctionDefNode)):
                self._declare_function(item)

        # Pass 2: alleen function definitions genereren
        for item in node.top_level_items:
            if isinstance(item, FunctionDefNode):
                self.visit(item)


    def visit_FunctionDefNode(self, node: FunctionDefNode):
        self._collect_comments(node)

        if node.return_type == "int" and node.return_ptr == 0:
            return_type = ir.IntType(32)
        elif node.return_type == "float" and node.return_ptr == 0:
            return_type = ir.FloatType()
        elif node.return_type == "char" and node.return_ptr == 0:
            return_type = ir.IntType(8)
        elif node.return_type == "void" and node.return_ptr == 0:
            return_type = ir.VoidType()
        else:
            return_type = self._get_llvm_type(node.return_type, node.return_ptr)

        # Bouw parameter types
        param_types = []
        for param in node.params:
            llvm_param_type = self._get_llvm_type(
                param.type_name,
                param.pointer_depth
            )
            param_types.append(llvm_param_type)

        func = self.module.globals.get(node.name)
        if func is None:
            func = self._declare_function(node)

        entry_block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)

        # Reset lokale variabelen per functie
        self.variables = {}

        # Parameters opslaan als lokale variabelen
        for i, arg in enumerate(func.args):
            param = node.params[i]
            arg.name = param.name

            param_ptr = self.builder.alloca(arg.type, name=param.name)
            self.builder.store(arg, param_ptr)

            self.variables[param.name] = param_ptr

        # Body genereren
        for stmt in node.body.items:
            self.visit(stmt)

        # Default return als er geen expliciete return was
        if not entry_block.is_terminated:
            if isinstance(return_type, ir.VoidType):
                self.builder.ret_void()
            elif isinstance(return_type, ir.IntType):
                self.builder.ret(ir.Constant(return_type, 0))
            elif isinstance(return_type, ir.FloatType):
                self.builder.ret(ir.Constant(return_type, 0.0))
            else:
                self.builder.ret(ir.Constant(return_type, None))
    # ═══════════════════════════════════════════════════════════
    # STATEMENTS
    # ═══════════════════════════════════════════════════════════

    def visit_ReturnNode(self, node: ReturnNode):
        self._collect_comments(node)

        # Guard: don't emit into an already-terminated block
        if self.builder.block.is_terminated:
            return

        if node.value is None:
            self.builder.ret_void()
        else:
            value = self.visit(node.value)
            self.builder.ret(value)

    def visit_VarDeclNode(self, node: VarDeclNode):
        self._collect_comments(node)

        if node.array_dimensions:
            base_type = self._get_llvm_type(node.type_name, node.pointer_depth)
            array_type = base_type
            for dim in reversed(node.array_dimensions):
                array_type = ir.ArrayType(array_type, dim)

            var_ptr = self.builder.alloca(array_type, name=node.name)
            self.variables[node.name] = var_ptr

            if node.value is not None:
                self._init_array(var_ptr, array_type, node.value, node.array_dimensions)

        else:
            llvm_type = self._get_llvm_type(node.type_name, node.pointer_depth)
            var_ptr = self.builder.alloca(llvm_type, name=node.name)
            self.variables[node.name] = var_ptr

            if node.value is not None:
                value = self.visit(node.value)

                value = self._cast_value(value, llvm_type)

                self.builder.store(value, var_ptr)

    def _init_array(self, var_ptr, array_type, initializer, dimensions):
        """
        Initialiseer een array met een ArrayInitializerNode.
        Werkt recursief voor multi-dimensionale arrays.
        """
        for i, elem in enumerate(initializer.elements):
            # Bereken het adres van element i
            idx = ir.Constant(ir.IntType(32), i)
            zero = ir.Constant(ir.IntType(32), 0)
            elem_ptr = self.builder.gep(var_ptr, [zero, idx], inbounds=True)

            if isinstance(elem, ArrayInitializerNode):
                # Multi-dimensionaal: recursief initialiseren
                inner_type = array_type.element
                self._init_array(elem_ptr, inner_type, elem, dimensions[1:])
            else:
                # Gewone waarde opslaan
                value = self.visit(elem)
                self.builder.store(value, elem_ptr)

    def visit_ArrayAccessNode(self, node: ArrayAccessNode):
        """
        arr[i] of matrix[i][j]

        LLVM:
            %ptr = getelementptr [5 x i32], [5 x i32]* %arr, i32 0, i32 i
            %val = load i32, i32* %ptr
        """
        # Haal de pointer op naar het array
        # Kan genest zijn: matrix[i][j] → ArrayAccess(ArrayAccess(matrix, i), j)
        if isinstance(node.array, IdentifierNode):
            arr_ptr = self.variables[node.array.name]
        else:
            # Geneste array access: eerst de binnenste pointer berekenen
            arr_ptr = self._get_array_ptr(node.array)

        index = self.visit(node.index)
        zero = ir.Constant(ir.IntType(32), 0)
        elem_ptr = self.builder.gep(arr_ptr, [zero, index], inbounds=True)

        return self.builder.load(elem_ptr)

    def _get_array_ptr(self, node):
        """
        Geeft de pointer naar een array element terug zonder te laden.
        Gebruikt voor geneste array access (multi-dim).
        """
        if isinstance(node, IdentifierNode):
            return self.variables[node.name]

        # ArrayAccessNode: bereken de pointer naar dit element
        arr_ptr = self._get_array_ptr(node.array)
        index = self.visit(node.index)
        zero = ir.Constant(ir.IntType(32), 0)
        return self.builder.gep(arr_ptr, [zero, index], inbounds=True)

    def visit_AssignNode(self, node: AssignNode):
        self._collect_comments(node)

        if isinstance(node.target, IdentifierNode):
            var_ptr = self.variables[node.target.name]
            value = self.visit(node.value)

            # Automatische type conversie als types niet matchen
            target_llvm_type = var_ptr.type.pointee
            if isinstance(target_llvm_type, ir.FloatType) and isinstance(value.type, ir.IntType):
                value = self.builder.sitofp(value, ir.FloatType())
            elif isinstance(target_llvm_type, ir.IntType) and isinstance(value.type, ir.FloatType):
                value = self.builder.fptosi(value, target_llvm_type)
            elif isinstance(target_llvm_type, ir.IntType) and isinstance(value.type, ir.IntType):
                if target_llvm_type.width != value.type.width:
                    if target_llvm_type.width > value.type.width:
                        value = self.builder.sext(value, target_llvm_type)
                    else:
                        value = self.builder.trunc(value, target_llvm_type)
            elif value.type != target_llvm_type:
                # Incompatibele pointer types: bitcast om door te gaan (zoals GCC)
                value = self.builder.bitcast(value, target_llvm_type)

            self.builder.store(value, var_ptr)

        elif isinstance(node.target, DereferenceNode):
            # Pointer assignment: *ptr = 10
            ptr_value = self.variables[node.target.operand.name]
            ptr_loaded = self.builder.load(ptr_value)
            value = self.visit(node.value)
            self.builder.store(value, ptr_loaded)

        elif isinstance(node.target, ArrayAccessNode):
            # Array assignment: arr[i] = 10
            elem_ptr = self._get_array_ptr(node.target)
            index = self.visit(node.target.index)
            zero = ir.Constant(ir.IntType(32), 0)
            if isinstance(node.target.array, IdentifierNode):
                arr_ptr = self.variables[node.target.array.name]
            else:
                arr_ptr = self._get_array_ptr(node.target.array)
            elem_ptr = self.builder.gep(arr_ptr, [zero, index], inbounds=True)
            value = self.visit(node.value)
            self.builder.store(value, elem_ptr)

        else:
            raise NotImplementedError("Assignment naar dit type nog niet ondersteund")

    def visit_IfNode(self, node: IfNode):
        self._collect_comments(node)

        # Guard: don't emit into an already-terminated block
        if self.builder.block.is_terminated:
            return

        cond = self.visit(node.condition)
        cond_bool = self.builder.icmp_signed('!=', cond, ir.Constant(ir.IntType(32), 0))

        then_block = self.builder.block.parent.append_basic_block(name="if.then")
        else_block = self.builder.block.parent.append_basic_block(name="if.else")
        end_block = self.builder.block.parent.append_basic_block(name="if.end")

        self.builder.cbranch(cond_bool, then_block, else_block)

        # Then branch
        self.builder.position_at_end(then_block)
        self._visit_block_items(node.then_body.items)
        if not then_block.is_terminated:
            self.builder.branch(end_block)

        # Else branch
        self.builder.position_at_end(else_block)
        if node.else_body is not None:
            self._visit_block_items(node.else_body.items)
        if not else_block.is_terminated:
            self.builder.branch(end_block)

        # End block — only position here if it's reachable
        self.builder.position_at_end(end_block)

    def _visit_block_items(self, items):
        """Helper: bezoek alle items in een blok"""
        for item in items:
            self.visit(item)

    def visit_CompoundStmtNode(self, node: CompoundStmtNode):
        """
        Handle a CompoundStmtNode that appears directly as a statement.
        This happens when DCE inlines an if/while branch as its replacement.
        """
        self._visit_block_items(node.items)

    def visit_WhileNode(self, node: WhileNode):
        """While loop met break/continue support."""
        self._collect_comments(node)

        cond_block = self.builder.block.parent.append_basic_block(name="while.cond")
        body_block = self.builder.block.parent.append_basic_block(name="while.body")
        end_block = self.builder.block.parent.append_basic_block(name="while.end")

        self.builder.branch(cond_block)

        # Push naar stack VOOR body
        self.loop_stack.append((body_block, cond_block, end_block))

        self.builder.position_at_end(cond_block)
        cond = self.visit(node.condition)
        cond_bool = self.builder.icmp_signed('!=', cond, ir.Constant(ir.IntType(32), 0))
        self.builder.cbranch(cond_bool, body_block, end_block)

        self.builder.position_at_end(body_block)
        self._visit_block_items(node.body.items)
        if not body_block.is_terminated:
            self.builder.branch(cond_block)

        # Pop van loop stack
        self.loop_stack.pop()

        # End block
        self.builder.position_at_end(end_block)

    def visit_ForNode(self, node: ForNode):
        """For loop met break/continue support."""
        self._collect_comments(node)

        if node.init is not None:
            self.visit(node.init)

        cond_block = self.builder.block.parent.append_basic_block(name="for.cond")
        body_block = self.builder.block.parent.append_basic_block(name="for.body")
        update_block = self.builder.block.parent.append_basic_block(name="for.update")
        end_block = self.builder.block.parent.append_basic_block(name="for.end")

        self.builder.branch(cond_block)

        # Push naar stack VOOR body
        self.loop_stack.append((body_block, update_block, end_block))

        self.builder.position_at_end(cond_block)
        if node.condition is not None:
            cond = self.visit(node.condition)
            cond_bool = self.builder.icmp_signed('!=', cond, ir.Constant(ir.IntType(32), 0))
            self.builder.cbranch(cond_bool, body_block, end_block)
        else:
            self.builder.branch(body_block)

        self.builder.position_at_end(body_block)
        self._visit_block_items(node.body.items)
        if not body_block.is_terminated:
            self.builder.branch(update_block)

        self.builder.position_at_end(update_block)
        if node.update is not None:
            self.visit(node.update)
        self.builder.branch(cond_block)

        # Pop van stack NA body
        self.loop_stack.pop()

        self.builder.position_at_end(end_block)

    def visit_BreakNode(self, node: BreakNode):
        """
        Break statement - jump naar end van loop.
        """
        self._collect_comments(node)

        if self.loop_stack:
            _, _, end_block = self.loop_stack[-1]
            self.builder.branch(end_block)
        else:
            raise RuntimeError("Break outside loop")

    def visit_ContinueNode(self, node: ContinueNode):
        """
        Continue statement - jump naar update (for) of cond (while).
        """
        self._collect_comments(node)

        if self.loop_stack:
            _, update_or_cond_block, _ = self.loop_stack[-1]
            self.builder.branch(update_or_cond_block)
        else:
            raise RuntimeError("Continue outside loop")

    def visit_SwitchNode(self, node: SwitchNode):
        """
        Switch statement met cases.

        C code:
            switch (x) {
                case 1: ...
                case 2: ...
                default: ...
            }
        """
        self._collect_comments(node)

        # Evalueer expression
        expr_val = self.visit(node.expression)

        # Maak end block aan
        end_block = self.builder.block.parent.append_basic_block(name="switch.end")

        # Push naar loop stack zodat break werkt
        self.loop_stack.append((None, None, end_block))

        # Maak blocks voor elke case
        case_blocks = []
        for case in node.cases:
            case_block = self.builder.block.parent.append_basic_block(name="case")
            case_blocks.append(case_block)

        default_block = None
        if node.default is not None:
            default_block = self.builder.block.parent.append_basic_block(name="default")
        else:
            default_block = end_block

        # Switch instruction
        switch_instr = self.builder.switch(expr_val, default_block)

        # Voeg cases toe aan switch
        for i, case in enumerate(node.cases):
            case_value = self.visit(case.value)
            # Extract de integer waarde
            if isinstance(case_value, ir.Constant):
                case_int = case_value.constant
            else:
                case_int = 0
            switch_instr.add_case(ir.Constant(ir.IntType(32), case_int), case_blocks[i])

        # Generate code voor elke case
        for i, case in enumerate(node.cases):
            self.builder.position_at_end(case_blocks[i])
            self._visit_block_items(case.items)
            if not case_blocks[i].is_terminated:
                self.builder.branch(end_block)

        # Default block
        if node.default is not None:
            self.builder.position_at_end(default_block)
            self._visit_block_items(node.default.items)
            if not default_block.is_terminated:
                self.builder.branch(end_block)

        # Pop van loop stack
        self.loop_stack.pop()

        # End block
        self.builder.position_at_end(end_block)

    def visit_TernaryOpNode(self, node: TernaryOpNode):
        """
        Ternary operator: cond ? then_expr : else_expr

        C code:
            x > 0 ? 1 : 2

        LLVM IR:
            %cond = icmp ...
            br i1 %cond, label %then, label %else
            then:
                %then_val = ...
                br label %end
            else:
                %else_val = ...
                br label %end
            end:
                %result = phi i32 [%then_val, %then], [%else_val, %else]
        """
        cond = self.visit(node.condition)
        cond_bool = self.builder.icmp_signed('!=', cond, ir.Constant(ir.IntType(32), 0))

        then_block = self.builder.block.parent.append_basic_block(name="ternary.then")
        else_block = self.builder.block.parent.append_basic_block(name="ternary.else")
        end_block = self.builder.block.parent.append_basic_block(name="ternary.end")

        self.builder.cbranch(cond_bool, then_block, else_block)

        # Then
        self.builder.position_at_end(then_block)
        then_val = self.visit(node.then_expr)
        self.builder.branch(end_block)
        then_block = self.builder.block

        # Else
        self.builder.position_at_end(else_block)
        else_val = self.visit(node.else_expr)
        self.builder.branch(end_block)
        else_block = self.builder.block

        # End - phi node
        self.builder.position_at_end(end_block)
        phi = self.builder.phi(then_val.type)
        phi.add_incoming(then_val, then_block)
        phi.add_incoming(else_val, else_block)

        return phi

    # ═══════════════════════════════════════════════════════════
    # EXPRESSIONS
    # ═══════════════════════════════════════════════════════════

    def visit_IntLiteralNode(self, node: IntLiteralNode):
        """
        Genereer een integer literal.

        C code:
            42

        LLVM IR:
            i32 42
        """
        return ir.Constant(ir.IntType(32), node.value)

    def visit_FloatLiteralNode(self, node: FloatLiteralNode):
        """
        Genereer een float literal.

        C code:
            3.14

        LLVM IR:
            float 3.14
        """
        return ir.Constant(ir.FloatType(), node.value)

    def visit_CharLiteralNode(self, node):
        value = node.value
        # Zet escape sequences om naar hun ASCII waarde
        escape_map = {
            '\\n': 10,  # newline
            '\\t': 9,  # tab
            '\\r': 13,  # carriage return
            '\\0': 0,  # null
            '\\\\': 92,  # backslash
            "\\'": 39,  # single quote
            '\\"': 34,  # double quote
        }
        if value in escape_map:
            char_val = escape_map[value]
        else:
            char_val = ord(value)
        return ir.Constant(ir.IntType(8), char_val)

    def visit_IdentifierNode(self, node: IdentifierNode):
        """
        Laad de waarde van een variabele.

        C code:
            x

        LLVM IR:
            %1 = load i32, i32* %x
        """
        var_ptr = self.variables[node.name]
        # Als het een array is, geef pointer naar eerste element (geen load)
        if isinstance(var_ptr.type.pointee, ir.ArrayType):
            zero = ir.Constant(ir.IntType(32), 0)
            return self.builder.gep(var_ptr, [zero, zero], inbounds=True)
        return self.builder.load(var_ptr, name=node.name)

    def visit_BinaryOpNode(self, node: BinaryOpNode):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Pointer arithmetic
        if isinstance(left.type, ir.PointerType) and node.op == '+':
            return self.builder.gep(left, [right], inbounds=True)
        if isinstance(left.type, ir.PointerType) and node.op == '-':
            neg = self.builder.neg(right)
            return self.builder.gep(left, [neg], inbounds=True)

        if isinstance(right.type, ir.PointerType) and node.op == '+':
            return self.builder.gep(right, [left], inbounds=True)

        # Pointer vergelijkingen
        if isinstance(left.type, ir.PointerType) or isinstance(right.type, ir.PointerType):
            if node.op in ('==', '!=', '<', '>', '<=', '>='):
                if isinstance(left.type, ir.IntType):
                    left = self.builder.inttoptr(left, right.type)
                if isinstance(right.type, ir.IntType):
                    right = self.builder.inttoptr(right, left.type)
                cmp_map = {
                    '==': '==', '!=': '!=',
                    '<': '<', '>': '>',
                    '<=': '<=', '>=': '>=',
                }
                cmp_result = self.builder.icmp_unsigned(cmp_map[node.op], left, right)
                return self.builder.zext(cmp_result, ir.IntType(32))

        if isinstance(left.type, ir.IntType) and left.type.width < 32:
            left = self.builder.sext(left, ir.IntType(32))
        if isinstance(right.type, ir.IntType) and right.type.width < 32:
            right = self.builder.sext(right, ir.IntType(32))

        # Bepaal of we met floats werken
        is_float = isinstance(left.type, ir.FloatType) or isinstance(right.type, ir.FloatType)

        # Als één kant float is, zet de andere ook om naar float
        if is_float:
            if isinstance(left.type, ir.IntType):
                left = self.builder.sitofp(left, ir.FloatType())
            if isinstance(right.type, ir.IntType):
                right = self.builder.sitofp(right, ir.FloatType())

        # ── Arithmetic ──────────────────────────────────────────
        if node.op == '+':
            return self.builder.fadd(left, right) if is_float else self.builder.add(left, right)
        elif node.op == '-':
            return self.builder.fsub(left, right) if is_float else self.builder.sub(left, right)
        elif node.op == '*':
            return self.builder.fmul(left, right) if is_float else self.builder.mul(left, right)
        elif node.op == '/':
            return self.builder.fdiv(left, right) if is_float else self.builder.sdiv(left, right)
        elif node.op == '%':
            return self.builder.srem(left, right)

        # ── Comparison ──────────────────────────────────────────
        elif node.op in ('==', '!=', '<', '>', '<=', '>='):
            if is_float:
                cmp_map = {
                    '==': 'oeq', '!=': 'one',
                    '<': 'olt', '>': 'ogt',
                    '<=': 'ole', '>=': 'oge',
                }
                cmp_result = self.builder.fcmp_ordered(cmp_map[node.op], left, right)
            else:
                cmp_map = {
                    '==': '==', '!=': '!=',
                    '<': '<', '>': '>',
                    '<=': '<=', '>=': '>=',
                }
                cmp_result = self.builder.icmp_signed(cmp_map[node.op], left, right)
            return self.builder.zext(cmp_result, ir.IntType(32))

        # ── Logical ─────────────────────────────────────────────
        elif node.op == '&&':
            left_bool = self.builder.icmp_signed('!=', left, ir.Constant(ir.IntType(32), 0))
            right_bool = self.builder.icmp_signed('!=', right, ir.Constant(ir.IntType(32), 0))
            result = self.builder.and_(left_bool, right_bool)
            return self.builder.zext(result, ir.IntType(32))
        elif node.op == '||':
            left_bool = self.builder.icmp_signed('!=', left, ir.Constant(ir.IntType(32), 0))
            right_bool = self.builder.icmp_signed('!=', right, ir.Constant(ir.IntType(32), 0))
            result = self.builder.or_(left_bool, right_bool)
            return self.builder.zext(result, ir.IntType(32))

        # ── Bitwise ─────────────────────────────────────────────
        elif node.op == '&':
            return self.builder.and_(left, right)
        elif node.op == '|':
            return self.builder.or_(left, right)
        elif node.op == '^':
            return self.builder.xor(left, right)

        # ── Shift ───────────────────────────────────────────────
        elif node.op == '<<':
            return self.builder.shl(left, right)
        elif node.op == '>>':
            return self.builder.ashr(left, right)

        else:
            raise NotImplementedError(f"Operator {node.op} nog niet ondersteund")

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        """
        Genereer een unaire operatie.

        -x  → neg (int) of fneg (float)
        +x  → noop, gewoon x teruggeven
        !x  → icmp eq x, 0  dan zext naar i32
        ~x  → xor x, -1
        """
        operand = self.visit(node.operand)
        is_float = isinstance(operand.type, ir.FloatType)

        if node.op == '-':
            if is_float:
                return self.builder.fneg(operand)
            else:
                # neg = 0 - x
                zero = ir.Constant(ir.IntType(32), 0)
                return self.builder.sub(zero, operand)

        elif node.op == '+':
            # Unaire + doet niets
            return operand

        elif node.op == '!':
            # !x  →  (x == 0) ? 1 : 0
            zero = ir.Constant(ir.IntType(32), 0)
            cmp_result = self.builder.icmp_signed('==', operand, zero)
            return self.builder.zext(cmp_result, ir.IntType(32))

        elif node.op == '~':
            # ~x  →  x XOR -1 (bitwise NOT)
            minus_one = ir.Constant(ir.IntType(32), -1)
            return self.builder.xor(operand, minus_one)

        else:
            raise NotImplementedError(f"Unaire operator {node.op} nog niet ondersteund")

    # ═══════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════

    def _get_llvm_type(self, type_name: str, pointer_depth: int):
        """
        Converteer C type naar LLVM type.

        Examples:
            'int', 0 -> i32
            'float', 0 -> float
            'int', 1 -> i32*
            'int', 2 -> i32**
        """
        # Base types
        if type_name == 'int':
            base_type = ir.IntType(32)
        elif type_name == 'float':
            base_type = ir.FloatType()
        elif type_name == 'char':
            base_type = ir.IntType(8)
        elif type_name == 'void':
            base_type = ir.VoidType()
        else:
            raise ValueError(f"Onbekend type: {type_name}")

        # Voeg pointers toe
        for _ in range(pointer_depth):
            base_type = base_type.as_pointer()

        return base_type

    def visit_IncrementNode(self, node: IncrementNode):
        if isinstance(node.operand, IdentifierNode):
            var_ptr = self.variables[node.operand.name]
            old_value = self.builder.load(var_ptr, name=node.operand.name)
        elif isinstance(node.operand, DereferenceNode):
            # (*ptr)++ — laad de pointer, gebruik die als var_ptr
            ptr = self.variables[node.operand.operand.name]
            var_ptr = self.builder.load(ptr)
            old_value = self.builder.load(var_ptr)
        elif isinstance(node.operand, ArrayAccessNode):
            # a[i]++ — bereken de pointer naar het element
            zero = ir.Constant(ir.IntType(32), 0)
            arr_ptr = self.variables[node.operand.array.name]
            index = self.visit(node.operand.index)
            var_ptr = self.builder.gep(arr_ptr, [zero, index], inbounds=True)
            old_value = self.builder.load(var_ptr)
        else:
            raise NotImplementedError(f"Increment op {type(node.operand)} niet ondersteund")

        # Check of het een pointer is
        if isinstance(old_value.type, ir.PointerType):
            one = ir.Constant(ir.IntType(32), 1)
            new_value = self.builder.gep(old_value, [one], inbounds=True)
        else:
            one = ir.Constant(ir.IntType(32), 1)
            new_value = self.builder.add(old_value, one)

        self.builder.store(new_value, var_ptr)
        return new_value if node.prefix else old_value

    def visit_DecrementNode(self, node: DecrementNode):
        if isinstance(node.operand, IdentifierNode):
            var_ptr = self.variables[node.operand.name]
            old_value = self.builder.load(var_ptr, name=node.operand.name)
        elif isinstance(node.operand, DereferenceNode):
            # (*ptr)-- — laad de pointer, gebruik die als var_ptr
            ptr = self.variables[node.operand.operand.name]
            var_ptr = self.builder.load(ptr)
            old_value = self.builder.load(var_ptr)
        elif isinstance(node.operand, ArrayAccessNode):
            # a[i]-- — bereken de pointer naar het element
            zero = ir.Constant(ir.IntType(32), 0)
            arr_ptr = self.variables[node.operand.array.name]
            index = self.visit(node.operand.index)
            var_ptr = self.builder.gep(arr_ptr, [zero, index], inbounds=True)
            old_value = self.builder.load(var_ptr)
        else:
            raise NotImplementedError(f"Decrement op {type(node.operand)} niet ondersteund")

        # Check of het een pointer is
        if isinstance(old_value.type, ir.PointerType):
            minus_one = ir.Constant(ir.IntType(32), -1)
            new_value = self.builder.gep(old_value, [minus_one], inbounds=True)
        else:
            one = ir.Constant(ir.IntType(32), 1)
            new_value = self.builder.sub(old_value, one)

        self.builder.store(new_value, var_ptr)
        return new_value if node.prefix else old_value

    def visit_AddressOfNode(self, node: AddressOfNode):
        """
        &x → geeft het adres (pointer) van x terug

        C code:
            int* ptr = &x;

        LLVM:
            %ptr = alloca i32*
            store i32* %x, i32** %ptr
        """
        # De pointer naar x zit al in onze symbol table
        # Dat IS al het adres van x
        return self.variables[node.operand.name]

    def visit_DereferenceNode(self, node: DereferenceNode):
        """
        *ptr → laad de waarde waar ptr naar wijst

        C code:
            int y = *ptr;

        LLVM:
            %1 = load i32*, i32** %ptr   ; laad de pointer zelf
            %2 = load i32, i32* %1       ; laad de waarde via de pointer
        """
        # Laad eerst de pointer zelf
        ptr_value = self.visit(node.operand)

        # Laad dan de waarde waar de pointer naar wijst
        return self.builder.load(ptr_value)

    def visit_CastNode(self, node: CastNode):
        """
        Expliciete type cast.

        C code:
            (int)3.14    → fptosi
            (float)5     → sitofp
            (char)300    → trunc naar i8
        """
        value = self.visit(node.operand)
        target_type = self._get_llvm_type(node.type_name, node.pointer_depth)

        # Float → Int
        if isinstance(value.type, ir.FloatType) and isinstance(target_type, ir.IntType):
            return self.builder.fptosi(value, target_type)

        # Int → Float
        elif isinstance(value.type, ir.IntType) and isinstance(target_type, ir.FloatType):
            return self.builder.sitofp(value, target_type)

        # Int → Int (bijv. int naar char = trunc, char naar int = sext)
        elif isinstance(value.type, ir.IntType) and isinstance(target_type, ir.IntType):
            if value.type.width > target_type.width:
                return self.builder.trunc(value, target_type)
            elif value.type.width < target_type.width:
                return self.builder.sext(value, target_type)
            else:
                return value  # zelfde grootte, niets te doen

        # Zelfde type, niets te doen
        else:
            return value

    def _create_global_string(self, value: str) -> ir.GlobalVariable:
        """
        Maak een globale string constante aan.

        C code:
            "Hello"

        LLVM:
            @.str.0 = private unnamed_addr constant [6 x i8] c"Hello\00"
        """
        # Voeg null-terminator toe
        encoded = (value + '\00').encode('utf-8')
        string_type = ir.ArrayType(ir.IntType(8), len(encoded))

        # Unieke naam: @.str.0, @.str.1, etc.
        name = f".str.{self.string_counter}"
        self.string_counter += 1

        # Maak globale variabele aan
        global_str = ir.GlobalVariable(self.module, string_type, name=name)
        global_str.global_constant = True
        global_str.linkage = 'private'
        global_str.unnamed_addr = True
        global_str.initializer = ir.Constant(string_type, bytearray(encoded))

        return global_str

    def visit_StringLiteralNode(self, node):
        """
        Genereer een string literal.

        C code:
            "Hello"

        LLVM:
            @.str.0 = private unnamed_addr constant [6 x i8] c"Hello\00"
            %ptr = getelementptr [6 x i8], [6 x i8]* @.str.0, i32 0, i32 0
        """
        global_str = self._create_global_string(node.value)

        # Geef pointer naar het eerste karakter terug
        zero = ir.Constant(ir.IntType(32), 0)
        return self.builder.gep(global_str, [zero, zero], inbounds=True)

    def _get_printf(self):
        """
        Declareer printf als die nog niet gedeclareerd is.

        LLVM:
            declare i32 @printf(i8*, ...)
        """
        if self.printf_func is None:
            printf_type = ir.FunctionType(
                ir.IntType(32),  # return type: int
                [ir.IntType(8).as_pointer()],  # eerste argument: char*
                var_arg=True  # varargs: ...
            )
            self.printf_func = ir.Function(self.module, printf_type, name="printf")
        return self.printf_func

    def visit_PrintfNode(self, node):
        """
        Genereer een printf aanroep.

        C code:
            printf("Hello %d\n", x);

        LLVM:
            %fmt = getelementptr [10 x i8], [10 x i8]* @.str.0, i32 0, i32 0
            call i32 (i8*, ...) @printf(i8* %fmt, i32 %x)
        """
        self._collect_comments(node)

        # Maak de format string aan als globale constante
        fmt_ptr = self._create_global_string(node.format_string)
        zero = ir.Constant(ir.IntType(32), 0)
        fmt_arg = self.builder.gep(fmt_ptr, [zero, zero], inbounds=True)

        # Verwerk de argumenten
        args = [fmt_arg]
        for arg in node.args:
            value = self.visit(arg)
            # Array: geef pointer naar eerste element ipv de array zelf
            if isinstance(value.type, ir.ArrayType):
                ptr = self.variables[arg.name] if isinstance(arg, IdentifierNode) else None
                if ptr is not None:
                    value = self.builder.gep(ptr, [zero, zero], inbounds=True)
            # Float moet gepromoveerd worden naar double voor printf varargs
            elif isinstance(value.type, ir.FloatType):
                value = self.builder.fpext(value, ir.DoubleType())
            # Char (i8) moet gepromoveerd worden naar i32 voor printf varargs
            elif isinstance(value.type, ir.IntType) and value.type.width < 32:
                value = self.builder.sext(value, ir.IntType(32))
            args.append(value)

        # Roep printf aan
        printf = self._get_printf()
        self.builder.call(printf, args)

    def _get_scanf(self):
        """
        Declareer scanf als die nog niet gedeclareerd is.

        LLVM:
            declare i32 @scanf(i8*, ...)
        """
        if self.scanf_func is None:
            scanf_type = ir.FunctionType(
                ir.IntType(32),
                [ir.IntType(8).as_pointer()],
                var_arg=True
            )
            self.scanf_func = ir.Function(self.module, scanf_type, name="scanf")
        return self.scanf_func

    def visit_ScanfNode(self, node):
        """
        Genereer een scanf aanroep.

        C code:
            scanf("%d", &x);

        LLVM:
            %fmt = getelementptr [3 x i8], [3 x i8]* @.str.0, i32 0, i32 0
            call i32 (i8*, ...) @scanf(i8* %fmt, i32* %x)
        """
        self._collect_comments(node)

        # Format string
        fmt_ptr = self._create_global_string(node.format_string)
        zero = ir.Constant(ir.IntType(32), 0)
        fmt_arg = self.builder.gep(fmt_ptr, [zero, zero], inbounds=True)

        # Argumenten — scanf verwacht pointers (&x)
        args = [fmt_arg]
        for arg in node.args:
            if isinstance(arg, AddressOfNode):
                # &x → geef de pointer naar x direct mee
                ptr = self.variables[arg.operand.name]
                # Als het een array is, geef pointer naar eerste element
                if isinstance(ptr.type.pointee, ir.ArrayType):
                    ptr = self.builder.gep(ptr, [zero, zero], inbounds=True)
                args.append(ptr)
            else:
                value = self.visit(arg)
                args.append(value)

        # Roep scanf aan
        scanf = self._get_scanf()
        self.builder.call(scanf, args)

    def visit_FunctionCallNode(self, node):
        func = self.module.globals.get(node.name)

        if func is None:
            raise RuntimeError(f"Function '{node.name}' not found in LLVM module")

        args = []

        expected_arg_types = list(func.function_type.args)

        for i, arg in enumerate(node.args):
            value = self.visit(arg)

            if i < len(expected_arg_types):
                value = self._cast_value(value, expected_arg_types[i])

            args.append(value)

        return self.builder.call(func, args)

    def _get_function_return_type(self, node):
        if node.return_type == "int" and node.return_ptr == 0:
            return ir.IntType(32)
        elif node.return_type == "float" and node.return_ptr == 0:
            return ir.FloatType()
        elif node.return_type == "char" and node.return_ptr == 0:
            return ir.IntType(8)
        elif node.return_type == "void" and node.return_ptr == 0:
            return ir.VoidType()
        else:
            return self._get_llvm_type(node.return_type, node.return_ptr)

    def _get_function_param_types(self, node):
        param_types = []

        for param in node.params:
            llvm_param_type = self._get_llvm_type(
                param.type_name,
                param.pointer_depth
            )
            param_types.append(llvm_param_type)

        return param_types

    def _declare_function(self, node):
        """
        Maakt alleen de LLVM function header aan.
        Als de functie al bestaat, hergebruiken we die.
        """

        existing = self.module.globals.get(node.name)
        if existing is not None:
            return existing

        return_type = self._get_function_return_type(node)
        param_types = self._get_function_param_types(node)

        func_type = ir.FunctionType(return_type, param_types)
        return ir.Function(self.module, func_type, name=node.name)

    def _cast_value(self, value, target_type):
        """
        Cast een LLVM value naar target_type wanneer dat nodig is.
        Gebruikt voor assignments, variable initializers, returns en function arguments.
        """

        if value.type == target_type:
            return value

        # int -> float
        if isinstance(value.type, ir.IntType) and isinstance(target_type, ir.FloatType):
            return self.builder.sitofp(value, target_type)

        # float -> int
        if isinstance(value.type, ir.FloatType) and isinstance(target_type, ir.IntType):
            return self.builder.fptosi(value, target_type)

        # int -> int, bv i8 -> i32 of i32 -> i8
        if isinstance(value.type, ir.IntType) and isinstance(target_type, ir.IntType):
            if value.type.width < target_type.width:
                return self.builder.sext(value, target_type)
            if value.type.width > target_type.width:
                return self.builder.trunc(value, target_type)
            return value

        # int -> pointer, bv int 0 naar null pointer of GCC-achtige int-to-pointer
        if isinstance(value.type, ir.IntType) and isinstance(target_type, ir.PointerType):
            if isinstance(value, ir.Constant) and value.constant == 0:
                return ir.Constant(target_type, None)
            return self.builder.inttoptr(value, target_type)

        # pointer -> int
        if isinstance(value.type, ir.PointerType) and isinstance(target_type, ir.IntType):
            return self.builder.ptrtoint(value, target_type)

        # pointer -> pointer
        if isinstance(value.type, ir.PointerType) and isinstance(target_type, ir.PointerType):
            return self.builder.bitcast(value, target_type)

        raise TypeError(f"Cannot cast {value.type} to {target_type}")
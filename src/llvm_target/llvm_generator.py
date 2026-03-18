"""
LLVM IR Code Generator - WITH COMMENT SUPPORT
======================

Vertaalt AST naar LLVM IR code.

NIEUW: Comments from source code are now embedded in LLVM output
"""

from llvmlite import ir
import llvmlite.binding as llvm
from parser.ast_nodes import (
    ProgramNode,
    MainFunctionNode,
    ReturnNode,
    IntLiteralNode,
    FloatLiteralNode,
    VarDeclNode,
    AssignNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
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

        # NIEUW: Comment tracking
        # Maps: line_number -> {'source': str, 'leading': list, 'inline': str}
        self.line_to_comment = {}
        self.comment_order = []  # Track order of statements

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

        # NIEUW: Add comments to LLVM output
        llvm_with_comments = self._add_comments_to_llvm(raw_llvm)

        return llvm_with_comments

    # ═══════════════════════════════════════════════════════════
    # NIEUW: COMMENT HANDLING
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
        """Bezoek het programma (bevat main function)."""
        # AANGEPAST: collect comments from includes (but don't process them)
        for inc in node.includes:
            self._collect_comments(inc)

        self.visit(node.main_function)

    def visit_MainFunctionNode(self, node: MainFunctionNode):
        """
        Genereer de main functie.

        C code:
            int main() { ... }

        LLVM IR:
            define i32 @main() {
            entry:
              ...
            }
        """
        # NIEUW: Collect comments
        self._collect_comments(node)

        # Definieer de main functie: int main()
        # i32 = 32-bit integer (return type)
        # [] = geen argumenten
        func_type = ir.FunctionType(ir.IntType(32), [])
        func = ir.Function(self.module, func_type, name="main")

        # Maak een "basic block" (een blok code zonder jumps)
        entry_block = func.append_basic_block(name="entry")

        # Maak een builder om instructies toe te voegen
        self.builder = ir.IRBuilder(entry_block)

        # Bezoek alle statements in main
        for stmt in node.statements:
            self.visit(stmt)

        # Als de laatste statement geen return was, voeg default return 0 toe
        if not entry_block.is_terminated:
            self.builder.ret(ir.Constant(ir.IntType(32), 0))

    # ═══════════════════════════════════════════════════════════
    # STATEMENTS
    # ═══════════════════════════════════════════════════════════

    def visit_ReturnNode(self, node: ReturnNode):
        """
        Genereer een return statement.

        C code:
            return 42;

        LLVM IR:
            ret i32 42
        """
        # NIEUW: Collect comments
        self._collect_comments(node)

        if node.value is None:
            # return; (zonder waarde)
            self.builder.ret_void()
        else:
            # return <expressie>;
            value = self.visit(node.value)
            self.builder.ret(value)

    def visit_VarDeclNode(self, node: VarDeclNode):
        """
        Genereer een variabele declaratie.

        C code:
            int x = 5;

        LLVM IR:
            %x = alloca i32        ; int x = 5
            store i32 5, i32* %x   ;
        """
        # NIEUW: Collect comments
        self._collect_comments(node)

        # Bepaal LLVM type
        llvm_type = self._get_llvm_type(node.type_name, node.pointer_depth)

        # Alloceer ruimte voor de variabele
        var_ptr = self.builder.alloca(llvm_type, name=node.name)

        # Sla op in symbol table
        self.variables[node.name] = var_ptr

        # Als er een initiele waarde is, sla die op
        if node.value is not None:
            value = self.visit(node.value)

            # Automatische type conversie als types niet matchen
            if isinstance(llvm_type, ir.FloatType) and isinstance(value.type, ir.IntType):
                # int → float
                value = self.builder.sitofp(value, ir.FloatType())
            elif isinstance(llvm_type, ir.IntType) and isinstance(value.type, ir.FloatType):
                # float → int (verlies van informatie, maar grammar laat het toe)
                value = self.builder.fptosi(value, ir.IntType(32))

            self.builder.store(value, var_ptr)

    def visit_AssignNode(self, node: AssignNode):
        """
        Genereer een assignment.

        C code:
            x = 10;

        LLVM IR:
            store i32 10, i32* %x
        """
        # NIEUW: Collect comments
        self._collect_comments(node)

        # Haal de pointer naar de variabele op
        if isinstance(node.target, IdentifierNode):
            var_ptr = self.variables[node.target.name]
            value = self.visit(node.value)
            self.builder.store(value, var_ptr)
        else:
            raise NotImplementedError("Assignment naar niet-identifier nog niet ondersteund")

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

    def visit_IdentifierNode(self, node: IdentifierNode):
        """
        Laad de waarde van een variabele.

        C code:
            x

        LLVM IR:
            %1 = load i32, i32* %x
        """
        var_ptr = self.variables[node.name]
        return self.builder.load(var_ptr, name=node.name)

    def visit_BinaryOpNode(self, node: BinaryOpNode):
        """
        Genereer een binaire operatie.

        Integer arithmetic:  add, sub, mul, sdiv, srem
        Float arithmetic:    fadd, fsub, fmul, fdiv
        Comparison (int):    icmp → zext naar i32
        Comparison (float):  fcmp → zext naar i32
        Logical:             and, or (na bool-conversie)
        Bitwise:             and, or, xor
        Shift:               shl, ashr
        """
        left = self.visit(node.left)
        right = self.visit(node.right)

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
            # % niet geldig voor floats in C
            return self.builder.srem(left, right)

        # ── Comparison ──────────────────────────────────────────
        # icmp/fcmp geeft i1 terug → zext naar i32 voor C-compatibiliteit
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
            # i1 → i32
            return self.builder.zext(cmp_result, ir.IntType(32))

        # ── Logical ─────────────────────────────────────────────
        # && en || werken op bools: zet operanden eerst naar i1
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
            return self.builder.ashr(left, right)  # arithmetic shift right (signed)

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
        else:
            raise ValueError(f"Onbekend type: {type_name}")

        # Voeg pointers toe
        for _ in range(pointer_depth):
            base_type = base_type.as_pointer()

        return base_type
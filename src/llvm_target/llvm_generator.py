"""
LLVM IR Code Generator
======================

Vertaalt AST naar LLVM IR code.

Stap 1 (NU): Alleen int main() { return 0; } ondersteunen
Stap 2 (LATER): Variables, expressions, etc.
"""

from llvmlite import ir
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

        # Builder wordt gebruikt om instructies toe te voegen
        self.builder = None

        # Symbol table: variabele naam -> LLVM waarde
        self.variables = {}

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
        return str(self.module)

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
            %x = alloca i32        ; reserveer ruimte
            store i32 5, i32* %x   ; sla waarde op
        """
        # Bepaal LLVM type
        llvm_type = self._get_llvm_type(node.type_name, node.pointer_depth)

        # Alloceer ruimte voor de variabele
        var_ptr = self.builder.alloca(llvm_type, name=node.name)

        # Sla op in symbol table
        self.variables[node.name] = var_ptr

        # Als er een initiele waarde is, sla die op
        if node.value is not None:
            value = self.visit(node.value)
            self.builder.store(value, var_ptr)

    def visit_AssignNode(self, node: AssignNode):
        """
        Genereer een assignment.

        C code:
            x = 10;

        LLVM IR:
            store i32 10, i32* %x
        """
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

        C code:
            x + y

        LLVM IR:
            %1 = add i32 %x, %y
        """
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Integer operaties
        if node.op == '+':
            return self.builder.add(left, right)
        elif node.op == '-':
            return self.builder.sub(left, right)
        elif node.op == '*':
            return self.builder.mul(left, right)
        elif node.op == '/':
            return self.builder.sdiv(left, right)  # signed division
        elif node.op == '%':
            return self.builder.srem(left, right)  # signed remainder
        else:
            raise NotImplementedError(f"Operator {node.op} nog niet ondersteund")

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
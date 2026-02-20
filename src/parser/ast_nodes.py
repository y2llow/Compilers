# ============================================================
# AST Node classes for the C compiler
# ============================================================
# Design notes:
#   - All nodes inherit from ASTNode (easy isinstance checks later)
#   - No ANTLR types are used here — the AST is fully independent
#   - Adding new node types = just add a new class below
# ============================================================

class ASTNode:
    """Base class for all AST nodes."""
    pass

# ── Program ──────────────────────────────────────────────────

class ProgramNode(ASTNode):
    """Root node: holds the main function."""
    def __init__(self, main_function):
        self.main_function = main_function

    def __repr__(self):
        return f"Program({self.main_function})"

# ── Main function ─────────────────────────────────────────────

class MainFunctionNode(ASTNode):
    """The int main() { ... } function. Holds a list of statements."""
    def __init__(self, statements: list):
        self.statements = statements  # [ASTNode, ...]

    def __repr__(self):
        return f"MainFunction({self.statements})"

# ── Statements ────────────────────────────────────────────────

class VarDeclNode(ASTNode):
    """
    A variable declaration/definition.
    Examples:
        int x;
        const float y = 3.14;
        int* ptr = &x;

    is_const     : bool
    type_name    : str, e.g. 'int', 'float', 'char'
    pointer_depth: int, number of pointer stars (0 = not a pointer)
    name         : str, the variable name
    value        : ASTNode or None (None if no initializer)
    """
    def __init__(self, is_const: bool, type_name: str, pointer_depth: int, name: str, value):
        self.is_const = is_const
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.name = name
        self.value = value  # ASTNode or None

    def __repr__(self):
        const = "const " if self.is_const else ""
        stars = '*' * self.pointer_depth
        val = f" = {self.value}" if self.value is not None else ""
        return f"VarDecl({const}{self.type_name}{stars} {self.name}{val})"

class AssignNode(ASTNode):
    """
    An assignment statement.
    Examples:
        x = 5;
        *ptr = 3;

    target: ASTNode (IdentifierNode or DereferenceNode)
    value : ASTNode
    """
    def __init__(self, target: ASTNode, value: ASTNode):
        self.target = target
        self.value = value

    def __repr__(self):
        return f"Assign({self.target} = {self.value})"

# ── Literals ──────────────────────────────────────────────────

class IntLiteralNode(ASTNode):
    """An integer literal, e.g. 42."""
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Int({self.value})"

class FloatLiteralNode(ASTNode):
    """A floating point literal, e.g. 3.14."""
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"

class CharLiteralNode(ASTNode):
    """A character literal, e.g. 'a'."""
    def __init__(self, value: str):
        self.value = value  # single character string

    def __repr__(self):
        return f"Char('{self.value}')"

# ── Identifier ────────────────────────────────────────────────

class IdentifierNode(ASTNode):
    """A variable name used in an expression, e.g. x."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"

# ── Unary operations ──────────────────────────────────────────

class UnaryOpNode(ASTNode):
    """
    A unary operation.
    op     : str, one of: '+', '-', '!', '~'
    operand: ASTNode
    """
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"

class DereferenceNode(ASTNode):
    """
    Pointer dereference: *ptr
    operand: ASTNode
    """
    def __init__(self, operand: ASTNode):
        self.operand = operand

    def __repr__(self):
        return f"Deref({self.operand})"

class AddressOfNode(ASTNode):
    """
    Address-of operator: &x
    operand: ASTNode
    """
    def __init__(self, operand: ASTNode):
        self.operand = operand

    def __repr__(self):
        return f"AddressOf({self.operand})"

class IncrementNode(ASTNode):
    """
    Increment operator: ++x (prefix) or x++ (postfix)
    operand: ASTNode
    prefix : bool (True = prefix, False = postfix)
    """
    def __init__(self, operand: ASTNode, prefix: bool):
        self.operand = operand
        self.prefix = prefix

    def __repr__(self):
        if self.prefix:
            return f"Increment(++{self.operand})"
        return f"Increment({self.operand}++)"

class DecrementNode(ASTNode):
    """
    Decrement operator: --x (prefix) or x-- (postfix)
    operand: ASTNode
    prefix : bool (True = prefix, False = postfix)
    """
    def __init__(self, operand: ASTNode, prefix: bool):
        self.operand = operand
        self.prefix = prefix

    def __repr__(self):
        if self.prefix:
            return f"Decrement(--{self.operand})"
        return f"Decrement({self.operand}--)"

class CastNode(ASTNode):
    """
    An explicit type cast: (int) x, (float*) ptr
    type_name    : str, e.g. 'int', 'float', 'char'
    pointer_depth: int, number of pointer stars
    operand      : ASTNode
    """
    def __init__(self, type_name: str, pointer_depth: int, operand: ASTNode):
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.operand = operand

    def __repr__(self):
        stars = '*' * self.pointer_depth
        return f"Cast(({self.type_name}{stars}) {self.operand})"

# ── Binary operations ─────────────────────────────────────────

class BinaryOpNode(ASTNode):
    """
    A binary operation.
    op   : str, e.g. '+', '-', '*', '/', '%',
                     '&&', '||', '==', '!=',
                     '<', '>', '<=', '>=',
                     '<<', '>>', '&', '|', '^'
    left : ASTNode
    right: ASTNode
    """
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"
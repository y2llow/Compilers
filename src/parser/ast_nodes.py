# ============================================================
# AST Node classes for the C compiler
# ============================================================
# Design notes:
#   - All nodes inherit from ASTNode (easy isinstance checks later)
#   - No ANTLR types are used here — the AST is fully independent
#   - Adding new node types = just add a new class below
#   - Comments are now stored for code readability
# ============================================================

class ASTNode:
    """Base class for all AST nodes."""

    def __init__(self):
        self.line = 0
        self.column = 0
        self.source_line = ""  # Original source code line for comments
        self.leading_comments = []  # Comments before this node
        self.inline_comment = None  # Comment on same line as code

# ── Program ──────────────────────────────────────────────────

class ProgramNode(ASTNode):
    """Root node: holds the main function."""

    def __init__(self, main_function):
        super().__init__()
        self.main_function = main_function

    def __repr__(self):
        return f"Program({self.main_function})"


# ── Main function ─────────────────────────────────────────────

class MainFunctionNode(ASTNode):
    """The int main() { ... } function. Holds a list of statements."""

    def __init__(self, statements: list):
        super().__init__()
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
        int arr[10];
        int matrix[3][4];
        int values[3] = {1, 2, 3};

    is_const     : bool
    type_name    : str, e.g. 'int', 'float', 'char'
    pointer_depth: int, number of pointer stars (0 = not a pointer)
    name         : str, the variable name
    array_dimensions: list of int, e.g. [10] or [3, 4]
    value        : ASTNode or ArrayInitializerNode or None
    """

    def __init__(self, is_const: bool, type_name: str, pointer_depth: int, name: str,
                 array_dimensions: list = None, value=None):
        super().__init__()
        self.is_const = is_const
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.name = name
        self.array_dimensions = array_dimensions if array_dimensions else []
        self.value = value  # ASTNode or ArrayInitializerNode or None

    def __repr__(self):
        const = "const " if self.is_const else ""
        stars = '*' * self.pointer_depth
        dims = ''.join([f'[{d}]' for d in self.array_dimensions])
        val = f" = {self.value}" if self.value is not None else ""
        return f"VarDecl({const}{self.type_name}{stars} {self.name}{dims}{val})"


class AssignNode(ASTNode):
    """
    An assignment statement.
    Examples:
        x = 5;
        *ptr = 3;
        arr[5] = 10;

    target: ASTNode (IdentifierNode, DereferenceNode, or ArrayAccessNode)
    value : ASTNode
    """

    def __init__(self, target: ASTNode, value: ASTNode):
        super().__init__()
        self.target = target
        self.value = value

    def __repr__(self):
        return f"Assign({self.target} = {self.value})"


# ── Literals ──────────────────────────────────────────────────

class IntLiteralNode(ASTNode):
    """An integer literal, e.g. 42."""

    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Int({self.value})"


class FloatLiteralNode(ASTNode):
    """A floating point literal, e.g. 3.14."""

    def __init__(self, value: float):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"


class CharLiteralNode(ASTNode):
    """A character literal, e.g. 'a'."""

    def __init__(self, value: str):
        super().__init__()
        self.value = value  # single character string

    def __repr__(self):
        return f"Char('{self.value}')"


# ── Identifier ────────────────────────────────────────────────

class IdentifierNode(ASTNode):
    """A variable name used in an expression, e.g. x."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


# ── Array Access ──────────────────────────────────────────────

class ArrayAccessNode(ASTNode):
    """
    Array element access: arr[index] or matrix[i][j]

    array: ASTNode (usually IdentifierNode, but can be another ArrayAccessNode for multi-dim)
    index: ASTNode (the index expression)
    """

    def __init__(self, array: ASTNode, index: ASTNode):
        super().__init__()
        self.array = array
        self.index = index

    def __repr__(self):
        return f"ArrayAccess({self.array}[{self.index}])"


# ── Array Initializer ─────────────────────────────────────────

class ArrayInitializerNode(ASTNode):
    """
    Array initializer: {1, 2, 3} or {{1,2},{3,4}}

    elements: list of ASTNode (each element can be a literal or another ArrayInitializerNode)
    """

    def __init__(self, elements: list):
        super().__init__()
        self.elements = elements

    def __repr__(self):
        elems = ", ".join(str(e) for e in self.elements)
        return f"ArrayInit({{{elems}}})"


# ── Unary operations ──────────────────────────────────────────

class UnaryOpNode(ASTNode):
    """
    A unary operation.
    op     : str, one of: '+', '-', '!', '~'
    operand: ASTNode
    """

    def __init__(self, op: str, operand: ASTNode):
        super().__init__()
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
        super().__init__()
        self.operand = operand

    def __repr__(self):
        return f"Deref({self.operand})"


class AddressOfNode(ASTNode):
    """
    Address-of operator: &x
    operand: ASTNode
    """

    def __init__(self, operand: ASTNode):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
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
        super().__init__()
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
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"
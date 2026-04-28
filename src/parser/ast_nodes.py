# ============================================================
# AST Node classes for the C compiler — COMPLETE VERSION
# Assignments 1-7: types, operators, control flow, functions,
#                  enums, structs, typedef
# ============================================================
# Design notes:
#   - All nodes inherit from ASTNode
#   - No ANTLR types used here — the AST is fully independent
#   - Comments stored for LLVM IR output
# ============================================================


class ASTNode:
    """Base class for all AST nodes."""

    def __init__(self):
        self.line = 0
        self.column = 0
        self.source_line = ""
        self.leading_comments = []
        self.inline_comment = None


# ══════════════════════════════════════════════════════════════
# PROGRAM
# ══════════════════════════════════════════════════════════════

class ProgramNode(ASTNode):
    """
    Root node.
    top_level_items: list of top-level items in order:
        IncludeNode, DefineNode, TypedefNode, EnumDeclNode,
        StructDeclNode, FunctionDefNode, FunctionDeclNode, VarDeclNode
    """

    def __init__(self, top_level_items: list):
        super().__init__()
        self.top_level_items = top_level_items

    def __repr__(self):
        return f"Program({self.top_level_items})"


# ══════════════════════════════════════════════════════════════
# PREPROCESSOR
# ══════════════════════════════════════════════════════════════

class IncludeNode(ASTNode):
    """
    #include <stdio.h>  or  #include "file.h"
    header   : str, e.g. 'stdio.h' or 'some/path/file.h'
    is_system: bool, True for <...>, False for "..."
    """

    def __init__(self, header: str, is_system: bool = True):
        super().__init__()
        self.header = header
        self.is_system = is_system

    def __repr__(self):
        if self.is_system:
            return f"Include(<{self.header}>)"
        return f'Include("{self.header}")'


class DefineNode(ASTNode):
    """
    #define OLD_NAME new_value
    name : str  — the macro name
    value: str  — the replacement text (kept as string; substitution
                  happens in the pre-processor pass, not here)
    """

    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value  # raw string; pre-processor replaces before parsing

    def __repr__(self):
        return f"Define({self.name} = {self.value})"


# ══════════════════════════════════════════════════════════════
# TYPEDEF
# ══════════════════════════════════════════════════════════════

class TypedefNode(ASTNode):
    """
    typedef <existing_type> <new_name>;
    e.g.  typedef int bool;
          typedef struct Point Point;

    existing_type: str  — the source type name
    pointer_depth: int  — number of pointer stars on the source type
    new_name     : str  — the alias being created
    """

    def __init__(self, existing_type: str, pointer_depth: int, new_name: str):
        super().__init__()
        self.existing_type = existing_type
        self.pointer_depth = pointer_depth
        self.new_name = new_name

    def __repr__(self):
        stars = '*' * self.pointer_depth
        return f"Typedef({self.existing_type}{stars} → {self.new_name})"


# ══════════════════════════════════════════════════════════════
# ENUM
# ══════════════════════════════════════════════════════════════

class EnumConstantNode(ASTNode):
    """
    One constant inside an enum body.
    name : str
    value: int or None  (None = auto-assigned: previous + 1, starting at 0)
    """

    def __init__(self, name: str, value=None):
        super().__init__()
        self.name = name
        self.value = value  # explicit int value, or None for auto

    def __repr__(self):
        if self.value is not None:
            return f"EnumConst({self.name} = {self.value})"
        return f"EnumConst({self.name})"


class EnumDeclNode(ASTNode):
    """
    enum <name> { A, B, C };
    name     : str
    constants: list[EnumConstantNode]

    Note: in C an enum is an int. The semantic analyser resolves
    enum constant names and replaces them with their integer values.
    """

    def __init__(self, name: str, constants: list):
        super().__init__()
        self.name = name
        self.constants = constants  # list[EnumConstantNode]

    def __repr__(self):
        consts = ', '.join(repr(c) for c in self.constants)
        return f"EnumDecl({self.name}: [{consts}])"


# ══════════════════════════════════════════════════════════════
# STRUCT
# ══════════════════════════════════════════════════════════════

class StructMemberNode(ASTNode):
    """
    One member declaration inside a struct body.
    type_name    : str
    pointer_depth: int
    name         : str
    array_dimensions: list[int]
    """

    def __init__(self, type_name: str, pointer_depth: int, name: str,
                 array_dimensions: list = None):
        super().__init__()
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.name = name
        self.array_dimensions = array_dimensions if array_dimensions else []

    def __repr__(self):
        stars = '*' * self.pointer_depth
        dims = ''.join(f'[{d}]' for d in self.array_dimensions)
        return f"StructMember({self.type_name}{stars} {self.name}{dims})"


class StructDeclNode(ASTNode):
    """
    struct <name> { <members> };
    name   : str
    members: list[StructMemberNode]  (empty list = forward declaration)
    """

    def __init__(self, name: str, members: list):
        super().__init__()
        self.name = name
        self.members = members  # list[StructMemberNode]

    def __repr__(self):
        members = ', '.join(repr(m) for m in self.members)
        return f"StructDecl({self.name}: [{members}])"


# ══════════════════════════════════════════════════════════════
# FUNCTIONS
# ══════════════════════════════════════════════════════════════

class ParameterNode(ASTNode):
    """
    One parameter in a function signature.
    is_const     : bool
    type_name    : str
    pointer_depth: int
    name         : str
    array_dimensions: list[int]  (for array parameters like int arr[])
    """

    def __init__(self, is_const: bool, type_name: str, pointer_depth: int,
                 name: str, array_dimensions: list = None):
        super().__init__()
        self.is_const = is_const
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.name = name
        self.array_dimensions = array_dimensions if array_dimensions else []

    def __repr__(self):
        const = "const " if self.is_const else ""
        stars = '*' * self.pointer_depth
        dims = ''.join(f'[{d}]' for d in self.array_dimensions)
        return f"Param({const}{self.type_name}{stars} {self.name}{dims})"


class FunctionDeclNode(ASTNode):
    """
    Forward declaration: return_type name(params);
    return_type  : str, e.g. 'int', 'void', 'float'
    return_ptr   : int, pointer depth of return type
    name         : str
    params       : list[ParameterNode]
    """

    def __init__(self, return_type: str, return_ptr: int, name: str, params: list):
        super().__init__()
        self.return_type = return_type
        self.return_ptr = return_ptr
        self.name = name
        self.params = params  # list[ParameterNode]

    def __repr__(self):
        stars = '*' * self.return_ptr
        params = ', '.join(repr(p) for p in self.params)
        return f"FunctionDecl({self.return_type}{stars} {self.name}({params}))"


class FunctionDefNode(ASTNode):
    """
    Full function definition: return_type name(params) { body }
    return_type: str
    return_ptr : int
    name       : str
    params     : list[ParameterNode]
    body       : CompoundStmtNode
    """

    def __init__(self, return_type: str, return_ptr: int, name: str,
                 params: list, body):
        super().__init__()
        self.return_type = return_type
        self.return_ptr = return_ptr
        self.name = name
        self.params = params
        self.body = body  # CompoundStmtNode

    def __repr__(self):
        stars = '*' * self.return_ptr
        params = ', '.join(repr(p) for p in self.params)
        return f"FunctionDef({self.return_type}{stars} {self.name}({params}))"


class FunctionCallNode(ASTNode):
    """
    A function call used as an expression: name(arg1, arg2, ...)
    name: str
    args: list[ASTNode]
    """

    def __init__(self, name: str, args: list):
        super().__init__()
        self.name = name
        self.args = args

    def __repr__(self):
        args = ', '.join(repr(a) for a in self.args)
        return f"FunctionCall({self.name}({args}))"


# ══════════════════════════════════════════════════════════════
# COMPOUND STATEMENT (block)
# ══════════════════════════════════════════════════════════════

class CompoundStmtNode(ASTNode):
    """
    A block: { stmt1; stmt2; ... }
    Used for: function bodies, if/else branches, loop bodies,
              anonymous scopes.
    items: list[ASTNode]  — mix of VarDeclNode and statements
    """

    def __init__(self, items: list):
        super().__init__()
        self.items = items

    def __repr__(self):
        return f"CompoundStmt({self.items})"


# ══════════════════════════════════════════════════════════════
# CONTROL FLOW
# ══════════════════════════════════════════════════════════════

class IfNode(ASTNode):
    """
    if (condition) { then } else { else_ }
    condition: ASTNode
    then_body: CompoundStmtNode
    else_body: CompoundStmtNode or None
    """

    def __init__(self, condition: ASTNode, then_body, else_body=None):
        super().__init__()
        self.condition = condition
        self.then_body = then_body    # CompoundStmtNode
        self.else_body = else_body    # CompoundStmtNode or None

    def __repr__(self):
        if self.else_body:
            return f"If({self.condition}, then={self.then_body}, else={self.else_body})"
        return f"If({self.condition}, then={self.then_body})"


class WhileNode(ASTNode):
    """
    while (condition) { body }
    condition: ASTNode
    body     : CompoundStmtNode
    """

    def __init__(self, condition: ASTNode, body):
        super().__init__()
        self.condition = condition
        self.body = body  # CompoundStmtNode

    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class ForNode(ASTNode):
    """
    for (init; condition; update) { body }

    Design decision: ForNode is kept as-is in the AST.
    We do NOT desugar it to a while loop here — that can be
    done in the LLVM generator if desired, but keeping it
    explicit makes semantic analysis and dot visualisation cleaner.

    init     : VarDeclNode or AssignNode or ASTNode or None
    condition: ASTNode or None  (None = infinite loop, i.e. for(;;))
    update   : AssignNode or UnaryOpNode or ASTNode or None
    body     : CompoundStmtNode
    """

    def __init__(self, init, condition, update, body):
        super().__init__()
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body  # CompoundStmtNode

    def __repr__(self):
        return f"For(init={self.init}, cond={self.condition}, update={self.update})"


class BreakNode(ASTNode):
    """break;"""

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "Break()"


class ContinueNode(ASTNode):
    """continue;"""

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "Continue()"


class SwitchNode(ASTNode):
    """
    switch (expression) { cases... default? }
    expression: ASTNode
    cases     : list[SwitchCaseNode]
    default   : SwitchDefaultNode or None

    Design decision: kept as SwitchNode in the AST (not desugared
    to if-else here). The LLVM generator handles it properly with
    basic blocks.
    """

    def __init__(self, expression: ASTNode, cases: list, default=None):
        super().__init__()
        self.expression = expression
        self.cases = cases      # list[SwitchCaseNode]
        self.default = default  # SwitchDefaultNode or None

    def __repr__(self):
        return f"Switch({self.expression}, cases={len(self.cases)})"


class SwitchCaseNode(ASTNode):
    """
    case <value>: <items>
    value: ASTNode  (usually IntLiteralNode or IdentifierNode for enum)
    items: list[ASTNode]
    """

    def __init__(self, value: ASTNode, items: list):
        super().__init__()
        self.value = value
        self.items = items

    def __repr__(self):
        return f"Case({self.value}, {len(self.items)} items)"


class SwitchDefaultNode(ASTNode):
    """
    default: <items>
    items: list[ASTNode]
    """

    def __init__(self, items: list):
        super().__init__()
        self.items = items

    def __repr__(self):
        return f"Default({len(self.items)} items)"


# ══════════════════════════════════════════════════════════════
# STATEMENTS (carried over + updated)
# ══════════════════════════════════════════════════════════════

class VarDeclNode(ASTNode):
    """
    Variable declaration/definition.
    Examples:
        int x;
        const float y = 3.14;
        int* ptr = &x;
        int arr[10];
        int matrix[3][4];
        int values[3] = {1, 2, 3};
        enum Color c = RED;      (type_name = 'Color')
        struct Point p;          (type_name = 'Point')

    is_const        : bool
    type_name       : str — 'int', 'float', 'char', 'void',
                            or a typedef/enum/struct name
    pointer_depth   : int
    name            : str
    array_dimensions: list[int]
    value           : ASTNode or ArrayInitializerNode or None
    """

    def __init__(self, is_const: bool, type_name: str, pointer_depth: int,
                 name: str, array_dimensions: list = None, value=None):
        super().__init__()
        self.is_const = is_const
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.name = name
        self.array_dimensions = array_dimensions if array_dimensions else []
        self.value = value

    def __repr__(self):
        const = "const " if self.is_const else ""
        stars = '*' * self.pointer_depth
        dims = ''.join(f'[{d}]' for d in self.array_dimensions)
        val = f" = {self.value}" if self.value is not None else ""
        return f"VarDecl({const}{self.type_name}{stars} {self.name}{dims}{val})"


class ReturnNode(ASTNode):
    """
    return <value>?;
    value: ASTNode or None
    """

    def __init__(self, value=None):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Return({self.value})" if self.value else "Return()"


class AssignNode(ASTNode):
    """
    Assignment: target <op> value
    target: ASTNode (IdentifierNode, DereferenceNode, ArrayAccessNode,
                     MemberAccessNode, PointerMemberAccessNode)
    op    : str, one of '=', '+=', '-=', '*=', '/=', '%=',
                         '&=', '|=', '^=', '<<=', '>>='
    value : ASTNode
    """

    def __init__(self, target: ASTNode, op: str, value: ASTNode):
        super().__init__()
        self.target = target
        self.op = op      # '=' for simple assignment, '+=' etc. for compound
        self.value = value

    def __repr__(self):
        return f"Assign({self.target} {self.op} {self.value})"


# ══════════════════════════════════════════════════════════════
# LITERALS
# ══════════════════════════════════════════════════════════════

class IntLiteralNode(ASTNode):
    """Integer literal, e.g. 42."""

    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Int({self.value})"


class FloatLiteralNode(ASTNode):
    """Float literal, e.g. 3.14."""

    def __init__(self, value: float):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"


class CharLiteralNode(ASTNode):
    """Character literal, e.g. 'a'."""

    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Char('{self.value}')"


class StringLiteralNode(ASTNode):
    """String literal, e.g. "hello"."""

    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def __repr__(self):
        escaped = self.value.replace('"', '\\"')
        return f'String("{escaped}")'


# ══════════════════════════════════════════════════════════════
# IDENTIFIERS & ACCESS
# ══════════════════════════════════════════════════════════════

class IdentifierNode(ASTNode):
    """A variable or enum constant name used in an expression."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


class ArrayAccessNode(ASTNode):
    """
    arr[index] or matrix[i][j]
    array: ASTNode
    index: ASTNode
    """

    def __init__(self, array: ASTNode, index: ASTNode):
        super().__init__()
        self.array = array
        self.index = index

    def __repr__(self):
        return f"ArrayAccess({self.array}[{self.index}])"


class ArrayInitializerNode(ASTNode):
    """
    {1, 2, 3} or {{1,2},{3,4}}
    elements: list[ASTNode]
    """

    def __init__(self, elements: list):
        super().__init__()
        self.elements = elements

    def __repr__(self):
        elems = ", ".join(str(e) for e in self.elements)
        return f"ArrayInit({{{elems}}})"


class MemberAccessNode(ASTNode):
    """
    struct_var.member
    object: ASTNode
    member: str
    """

    def __init__(self, obj: ASTNode, member: str):
        super().__init__()
        self.obj = obj
        self.member = member

    def __repr__(self):
        return f"MemberAccess({self.obj}.{self.member})"


class PointerMemberAccessNode(ASTNode):
    """
    ptr->member  (equivalent to (*ptr).member)
    ptr   : ASTNode
    member: str
    """

    def __init__(self, ptr: ASTNode, member: str):
        super().__init__()
        self.ptr = ptr
        self.member = member

    def __repr__(self):
        return f"PtrMemberAccess({self.ptr}->{self.member})"


# ══════════════════════════════════════════════════════════════
# UNARY OPERATIONS
# ══════════════════════════════════════════════════════════════

class UnaryOpNode(ASTNode):
    """
    Unary operation.
    op     : str, one of '+', '-', '!', '~'
    operand: ASTNode
    """

    def __init__(self, op: str, operand: ASTNode):
        super().__init__()
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


class DereferenceNode(ASTNode):
    """*ptr"""

    def __init__(self, operand: ASTNode):
        super().__init__()
        self.operand = operand

    def __repr__(self):
        return f"Deref({self.operand})"


class AddressOfNode(ASTNode):
    """&x"""

    def __init__(self, operand: ASTNode):
        super().__init__()
        self.operand = operand

    def __repr__(self):
        return f"AddressOf({self.operand})"


class IncrementNode(ASTNode):
    """
    ++x (prefix=True) or x++ (prefix=False)
    """

    def __init__(self, operand: ASTNode, prefix: bool):
        super().__init__()
        self.operand = operand
        self.prefix = prefix

    def __repr__(self):
        return f"Increment(++{self.operand})" if self.prefix else f"Increment({self.operand}++)"


class DecrementNode(ASTNode):
    """
    --x (prefix=True) or x-- (prefix=False)
    """

    def __init__(self, operand: ASTNode, prefix: bool):
        super().__init__()
        self.operand = operand
        self.prefix = prefix

    def __repr__(self):
        return f"Decrement(--{self.operand})" if self.prefix else f"Decrement({self.operand}--)"


class CastNode(ASTNode):
    """
    (int) x, (float*) ptr
    type_name    : str
    pointer_depth: int
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


class SizeofNode(ASTNode):
    """
    sizeof(type) or sizeof(expr)
    If is_type is True:  type_name + pointer_depth are set, operand is None
    If is_type is False: operand is set, type_name is None

    This distinction matters for LLVM: sizeof a type uses
    llvmlite's gep trick, sizeof an expression uses the type
    of the expression.
    """

    def __init__(self, type_name: str = None, pointer_depth: int = 0,
                 operand: ASTNode = None, is_type: bool = True):
        super().__init__()
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.operand = operand
        self.is_type = is_type

    def __repr__(self):
        if self.is_type:
            stars = '*' * self.pointer_depth
            return f"Sizeof({self.type_name}{stars})"
        return f"Sizeof({self.operand})"


# ══════════════════════════════════════════════════════════════
# BINARY OPERATIONS
# ══════════════════════════════════════════════════════════════

class BinaryOpNode(ASTNode):
    """
    Binary operation.
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


class TernaryOpNode(ASTNode):
    """
    condition ? then_expr : else_expr
    condition: ASTNode
    then_expr: ASTNode
    else_expr: ASTNode
    """

    def __init__(self, condition: ASTNode, then_expr: ASTNode, else_expr: ASTNode):
        super().__init__()
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __repr__(self):
        return f"Ternary({self.condition} ? {self.then_expr} : {self.else_expr})"


# ══════════════════════════════════════════════════════════════
# I/O (stdio.h)
# ══════════════════════════════════════════════════════════════

class PrintfNode(ASTNode):
    """
    printf("format", arg1, arg2, ...)
    format_string: str
    args         : list[ASTNode]
    """

    def __init__(self, format_string: str, args: list):
        super().__init__()
        self.format_string = format_string
        self.args = args

    def __repr__(self):
        args_repr = ', '.join(repr(a) for a in self.args)
        return f'Printf("{self.format_string}", [{args_repr}])'


class ScanfNode(ASTNode):
    """
    scanf("format", &var1, ...)
    format_string: str
    args         : list[ASTNode]
    """

    def __init__(self, format_string: str, args: list):
        super().__init__()
        self.format_string = format_string
        self.args = args

    def __repr__(self):
        args_repr = ', '.join(repr(a) for a in self.args)
        return f'Scanf("{self.format_string}", [{args_repr}])'
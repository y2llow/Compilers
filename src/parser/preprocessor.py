"""
Preprocessor for #define substitution.
Processes the AST to replace all identifier occurrences with their #define values.
"""

from parser.ast_nodes import *
import re


class Preprocessor:
    """
    Verwerkt #define statements en vervangt alle voorkomens van de macro's.

    Voorbeeld:
        #define FIVE 5
        int x = FIVE;  -> int x = 5;

    Ook ondersteunt:
        #define true 1
        #define false 0
        #define bool int
    """

    def __init__(self):
        self.defines = {}  # name -> value_string

    def preprocess(self, node: ProgramNode) -> ProgramNode:
        """
        Verzamel alle #define statements en vervang alle voorkomens.
        """
        # Stap 1: verzamel alle defines
        self._collect_defines(node)

        # Stap 2: vervang alle voorkomens in de AST
        node.top_level_items = [
            self.visit(item)
            for item in node.top_level_items
            if item is not None
        ]

        return node

    def _collect_defines(self, node: ProgramNode):
        """Verzamel alle #define statements."""
        for item in node.top_level_items:
            if isinstance(item, DefineNode):
                self.defines[item.name] = item.value

    # ============================================================
    # Visitor dispatch
    # ============================================================

    def visit(self, node):
        """Dispatch naar juiste visitor methode."""
        if node is None:
            return None

        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Fallback: return node ongewijzigd."""
        return node

    # ============================================================
    # Program & functions
    # ============================================================

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        # DefineNode zelf NIET vervangen, maar alles erna wel
        new_items = []
        for item in node.top_level_items:
            if isinstance(item, DefineNode):
                # Define nodes zelf weghalen (ze zijn al verwerkt)
                continue
            new_items.append(self.visit(item))

        node.top_level_items = new_items
        return node

    def visit_IncludeNode(self, node: IncludeNode) -> IncludeNode:
        return node

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> FunctionDefNode:
        node.body = self.visit(node.body)
        return node

    def visit_FunctionDeclNode(self, node: FunctionDeclNode) -> FunctionDeclNode:
        node.return_type = self._resolve_type_name(node.return_type)
        node.params = [self.visit(param) for param in node.params]
        return node

    def visit_CompoundStmtNode(self, node: CompoundStmtNode) -> CompoundStmtNode:
        node.items = [self.visit(item) for item in node.items if item is not None]
        return node

    # ============================================================
    # Statements
    # ============================================================

    def _resolve_type_name(self, type_name: str) -> str:
        """
        Vervang type aliases via #define.
        Voorbeeld:
            #define bool int
            bool x = 1; -> int x = 1;
        """
        if type_name in self.defines:
            replacement = self.defines[type_name].strip()
            if replacement in ("int", "float", "char", "void"):
                return replacement

        return type_name

    def visit_VarDeclNode(self, node: VarDeclNode) -> VarDeclNode:
        node.type_name = self._resolve_type_name(node.type_name)

        if node.value is not None:
            node.value = self.visit(node.value)

        return node

    def visit_AssignNode(self, node: AssignNode) -> AssignNode:
        node.target = self.visit(node.target)
        node.value = self.visit(node.value)
        return node

    def visit_ReturnNode(self, node: ReturnNode) -> ReturnNode:
        if node.value is not None:
            node.value = self.visit(node.value)
        return node

    def visit_IfNode(self, node: IfNode) -> IfNode:
        node.condition = self.visit(node.condition)
        node.then_body = self.visit(node.then_body)
        if node.else_body is not None:
            node.else_body = self.visit(node.else_body)
        return node

    def visit_WhileNode(self, node: WhileNode) -> WhileNode:
        node.condition = self.visit(node.condition)
        node.body = self.visit(node.body)
        return node

    def visit_ForNode(self, node: ForNode) -> ForNode:
        if node.init is not None:
            node.init = self.visit(node.init)
        if node.condition is not None:
            node.condition = self.visit(node.condition)
        if node.update is not None:
            node.update = self.visit(node.update)
        node.body = self.visit(node.body)
        return node

    def visit_SwitchNode(self, node: SwitchNode) -> SwitchNode:
        node.expression = self.visit(node.expression)
        node.cases = [self.visit(case) for case in node.cases]
        if node.default is not None:
            node.default = self.visit(node.default)
        return node

    def visit_SwitchCaseNode(self, node: SwitchCaseNode) -> SwitchCaseNode:
        node.value = self.visit(node.value)
        node.items = [self.visit(item) for item in node.items if item is not None]
        return node

    def visit_SwitchDefaultNode(self, node: SwitchDefaultNode) -> SwitchDefaultNode:
        node.items = [self.visit(item) for item in node.items if item is not None]
        return node

    def visit_BreakNode(self, node: BreakNode) -> BreakNode:
        return node

    def visit_ContinueNode(self, node: ContinueNode) -> ContinueNode:
        return node

    # ============================================================
    # Expressions
    # ============================================================

    def visit_IdentifierNode(self, node: IdentifierNode) -> ASTNode:
        """
        Als dit een #define is, vervang het door de waarde.
        """
        if node.name in self.defines:
            # Parse de waarde als een literal
            define_value = self.defines[node.name]
            replacement = self._parse_define_value(define_value)
            if replacement is not None:
                # Copy line/column info
                replacement.line = node.line
                replacement.column = node.column
                replacement.source_line = node.source_line
                if hasattr(node, 'leading_comments'):
                    replacement.leading_comments = node.leading_comments
                if hasattr(node, 'inline_comment'):
                    replacement.inline_comment = node.inline_comment
                return replacement
        return node

    def _parse_define_value(self, value_str: str, seen=None) -> ASTNode:
        """
        Parse een #define waarde naar een ASTNode.
        Ondersteunt:
        - int
        - float
        - string
        - char
        - identifier
        - nested defines
        """
        if seen is None:
            seen = set()

        value_str = value_str.strip()

        if value_str in seen:
            return IdentifierNode(value_str)
        seen.add(value_str)

        # Integer
        if re.match(r'^-?\d+$', value_str):
            return IntLiteralNode(int(value_str))

        # Float
        if re.match(r'^-?\d+\.\d+([eE][+-]?\d+)?$', value_str):
            return FloatLiteralNode(float(value_str))

        # String literal
        if value_str.startswith('"') and value_str.endswith('"'):
            inner = value_str[1:-1]
            inner = inner.replace('\\n', '\n')
            inner = inner.replace('\\t', '\t')
            inner = inner.replace('\\r', '\r')
            inner = inner.replace('\\"', '"')
            inner = inner.replace('\\\\', '\\')
            return StringLiteralNode(inner)

        # Character literal
        if value_str.startswith("'") and value_str.endswith("'"):
            return CharLiteralNode(value_str[1:-1])

        # Identifier / nested define
        if re.match(r'^[a-zA-Z_]\w*$', value_str):
            if value_str in self.defines:
                return self._parse_define_value(self.defines[value_str], seen)
            return IdentifierNode(value_str)

        return IdentifierNode(value_str)
    def visit_IntLiteralNode(self, node: IntLiteralNode) -> IntLiteralNode:
        return node

    def visit_FloatLiteralNode(self, node: FloatLiteralNode) -> FloatLiteralNode:
        return node

    def visit_CharLiteralNode(self, node: CharLiteralNode) -> CharLiteralNode:
        return node

    def visit_StringLiteralNode(self, node: StringLiteralNode) -> StringLiteralNode:
        return node

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> BinaryOpNode:
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return node

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> UnaryOpNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_DereferenceNode(self, node: DereferenceNode) -> DereferenceNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_AddressOfNode(self, node: AddressOfNode) -> AddressOfNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_IncrementNode(self, node: IncrementNode) -> IncrementNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_DecrementNode(self, node: DecrementNode) -> DecrementNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_CastNode(self, node: CastNode) -> CastNode:
        node.operand = self.visit(node.operand)
        return node

    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> ArrayAccessNode:
        node.array = self.visit(node.array)
        node.index = self.visit(node.index)
        return node

    def visit_ArrayInitializerNode(self, node: ArrayInitializerNode) -> ArrayInitializerNode:
        node.elements = [self.visit(elem) for elem in node.elements]
        return node

    def visit_TernaryOpNode(self, node: TernaryOpNode) -> TernaryOpNode:
        node.condition = self.visit(node.condition)
        node.then_expr = self.visit(node.then_expr)
        node.else_expr = self.visit(node.else_expr)
        return node

    def visit_SizeofNode(self, node: SizeofNode) -> SizeofNode:
        if node.operand is not None:
            node.operand = self.visit(node.operand)
        return node

    def visit_PrintfNode(self, node: PrintfNode) -> PrintfNode:
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_ScanfNode(self, node: ScanfNode) -> ScanfNode:
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_FunctionCallNode(self, node: FunctionCallNode) -> FunctionCallNode:
        node.args = [self.visit(arg) for arg in node.args]

        if node.name == "printf" and node.args:
            fmt = node.args[0]
            rest = node.args[1:]

            if isinstance(fmt, StringLiteralNode):
                return PrintfNode(fmt.value, rest)

        return node

    def visit_MemberAccessNode(self, node: MemberAccessNode) -> MemberAccessNode:
        node.obj = self.visit(node.obj)
        return node

    def visit_PointerMemberAccessNode(self, node: PointerMemberAccessNode) -> PointerMemberAccessNode:
        node.ptr = self.visit(node.ptr)
        return node

    def visit_EnumDeclNode(self, node: EnumDeclNode) -> EnumDeclNode:
        return node

    def visit_StructDeclNode(self, node: StructDeclNode) -> StructDeclNode:
        return node

    def visit_TypedefNode(self, node: TypedefNode) -> TypedefNode:
        return node

    def visit_ParameterNode(self, node: ParameterNode) -> ParameterNode:
        node.type_name = self._resolve_type_name(node.type_name)
        return node
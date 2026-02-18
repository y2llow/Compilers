# AST Node classes for our compiler

class ASTNode:
    """Base class for all AST nodes"""
    pass

class ProgramNode(ASTNode):
    """Represents the whole program (translation_unit)"""
    def __init__(self, functions):
        self.functions = functions  # list of FunctionNode

    def __repr__(self):
        return f"Program({self.functions})"

class FunctionNode(ASTNode):
    """Represents a function definition"""
    def __init__(self, return_type, name, body):
        self.return_type = return_type  # string: 'int' or 'void'
        self.name = name                # string: function name
        self.body = body                # CompoundStatementNode

    def __repr__(self):
        return f"Function({self.return_type} {self.name}, {self.body})"

class CompoundStatementNode(ASTNode):
    """Represents a block of statements { ... }"""
    def __init__(self, statements):
        self.statements = statements  # list of statement nodes

    def __repr__(self):
        return f"Block({self.statements})"

class ReturnStatementNode(ASTNode):
    """Represents a return statement"""
    def __init__(self, expression):
        self.expression = expression  # can be None if 'return;'

    def __repr__(self):
        return f"Return({self.expression})"

class DeclarationStatementNode(ASTNode):
    """Represents a variable declaration: int x; or int x = 5;"""
    def __init__(self, var_type, name, value):
        self.var_type = var_type  # string: 'int'
        self.name = name          # string: variable name
        self.value = value        # expression node or None

    def __repr__(self):
        return f"Declaration({self.var_type} {self.name} = {self.value})"

class NumberNode(ASTNode):
    """Represents a number literal"""
    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return f"Number({self.value})"

class IdentifierNode(ASTNode):
    """Represents a variable reference"""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"
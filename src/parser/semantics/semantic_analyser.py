from parser.semantics.symbol_table import SymbolTable
from parser.ast_nodes import *

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def visit(self, node):
        """Bezoek een AST node"""
        if isinstance(node, VarDeclNode):
            # Voeg variabele toe aan symbol table
            success = self.symbol_table.add_symbol(
                node.name,
                node.type_name,
                node.pointer_depth,
                node.is_const
            )
            if not success:
                self.errors.append(f"Error: variable {node.name} already declared")

        elif isinstance(node, IdentifierNode):
            # Check of variabele bestaat
            symbol = self.symbol_table.lookup(node.name)
            if not symbol:
                self.errors.append(f"Error: variable {node.name} not declared")

        # Blijf recursief door AST gaan
        for attr_name in dir(node):
            attr = getattr(node, attr_name)
            if isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ASTNode):
                        self.visit(item)
            elif isinstance(attr, ASTNode):
                self.visit(attr)
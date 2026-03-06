# ============================================================
# Symbol Table with Scope Support
# ============================================================

class Symbol:
    """Eén symbool in de tabel"""

    def __init__(self, name, type_name, pointer_depth=0, is_const=False, line=0, column=0, array_dimensions=None):
        self.name = name
        self.type_name = type_name  # 'int', 'float', 'char'
        self.pointer_depth = pointer_depth  # 0, 1, 2, ...
        self.is_const = is_const
        self.line = line  # For error reporting: waar is dit gedeclareerd
        self.column = column
        self.array_dimensions = array_dimensions if array_dimensions else []  # array dimensions

    def __repr__(self):
        const = "const " if self.is_const else ""
        stars = '*' * self.pointer_depth
        dims = ''.join([f'[{d}]' for d in self.array_dimensions])
        return f"Symbol({const}{self.type_name}{stars} {self.name}{dims})"


class SymbolTable:
    """Symbol table met scope support"""

    def __init__(self):
        # Stack van scopes. Elk scope is een dictionary: naam -> Symbol
        self.scopes = [{}]  # Start met global scope
        self.current_scope_level = 0

    def push_scope(self):
        """Maak een nieuwe (nested) scope aan"""
        self.scopes.append({})
        self.current_scope_level += 1

    def pop_scope(self):
        """Verlaat huidige scope"""
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1

    def add_symbol(self, name, type_name, pointer_depth=0, is_const=False, line=0, column=0, array_dimensions=None):
        """
        Voeg een nieuwe variabele toe aan de huidige scope.
        Retourneert (True, None) als succes.
        Retourneert (False, existing_symbol) als de variabele al bestaat in deze scope.
        """
        current_scope = self.scopes[self.current_scope_level]

        # Check of variabele al bestaat in huidige scope (NOT in parent scopes!)
        if name in current_scope:
            return False, current_scope[name]

        # Voeg toe aan huidge scope
        symbol = Symbol(name, type_name, pointer_depth, is_const, line, column, array_dimensions)
        current_scope[name] = symbol
        return True, None

    def lookup(self, name):
        """
        Zoek een variabele op, startend van huidge scope en omhoog.
        Retourneert Symbol object of None.
        """
        # Search from innermost (current) scope to outermost (global)
        for scope_level in range(self.current_scope_level, -1, -1):
            if name in self.scopes[scope_level]:
                return self.scopes[scope_level][name]
        return None

    def lookup_in_current_scope_only(self, name):
        """
        Zoek een variabele op alleen in de huidge scope (niet in parent scopes).
        Gebruikt voor het detecteren van redeclaratie.
        """
        return self.scopes[self.current_scope_level].get(name)

    def __repr__(self):
        result = []
        for level, scope in enumerate(self.scopes):
            result.append(f"Scope level {level}:")
            for name, symbol in scope.items():
                result.append(f"  {symbol}")
        return '\n'.join(result)
# ============================================================
# Symbol Table with Scope Support + Visualization History
# ============================================================

class Symbol:
    """Eén symbool in de tabel"""

    def __init__(self, name, type_name, pointer_depth=0, is_const=False, line=0, column=0, array_dimensions=None):
        self.name = name
        self.type_name = type_name
        self.pointer_depth = pointer_depth
        self.is_const = is_const
        self.line = line
        self.column = column
        self.array_dimensions = array_dimensions if array_dimensions else []

    def __repr__(self):
        const = "const " if self.is_const else ""
        stars = "*" * self.pointer_depth
        dims = "".join([f"[{d}]" for d in self.array_dimensions])
        return f"Symbol({const}{self.type_name}{stars} {self.name}{dims})"


class Scope:
    """Scope node voor visualisatie"""

    def __init__(self, scope_id, level, name="scope", parent=None):
        self.scope_id = scope_id
        self.level = level
        self.name = name
        self.parent = parent
        self.children = []
        self.symbols = {}

    def add_child(self, child):
        self.children.append(child)


class SymbolTable:
    """Symbol table met scope support + alle oude scopes bewaren"""

    def __init__(self):
        self.scope_counter = 0

        self.global_scope = Scope(
            scope_id=0,
            level=0,
            name="global",
            parent=None
        )

        self.current_scope = self.global_scope
        self.current_scope_level = 0

        # Belangrijk voor visualisatie:
        # hierin blijven scopes bestaan, ook na pop_scope().
        self.all_scopes = [self.global_scope]

        # Backwards compatibility:
        # oude code die self.scopes gebruikt blijft werken.
        self.scopes = [self.global_scope.symbols]

    def push_scope(self, name="scope"):
        """Maak een nieuwe nested scope aan"""
        self.scope_counter += 1

        new_scope = Scope(
            scope_id=self.scope_counter,
            level=self.current_scope.level + 1,
            name=name,
            parent=self.current_scope
        )

        self.current_scope.add_child(new_scope)
        self.all_scopes.append(new_scope)

        self.current_scope = new_scope
        self.current_scope_level = new_scope.level

        # Backwards compatibility met oude renderer/code
        self.scopes.append(new_scope.symbols)

    def pop_scope(self):
        """Verlaat huidige scope zonder hem te verwijderen uit all_scopes"""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent
            self.current_scope_level = self.current_scope.level

            # Stack-view mag poppen, visualisatie gebruikt all_scopes.
            if len(self.scopes) > 1:
                self.scopes.pop()

    def add_symbol(self, name, type_name, pointer_depth=0, is_const=False, line=0, column=0, array_dimensions=None):
        """
        Voeg een nieuwe variabele toe aan de huidige scope.
        Retourneert (True, None) als succes.
        Retourneert (False, existing_symbol) als de variabele al bestaat in deze scope.
        """
        current_symbols = self.current_scope.symbols

        if name in current_symbols:
            return False, current_symbols[name]

        symbol = Symbol(
            name,
            type_name,
            pointer_depth,
            is_const,
            line,
            column,
            array_dimensions
        )

        current_symbols[name] = symbol
        return True, None

    def lookup(self, name):
        """
        Zoek een variabele op, startend van huidige scope en omhoog.
        Retourneert Symbol object of None.
        """
        scope = self.current_scope

        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent

        return None

    def lookup_in_current_scope_only(self, name):
        """
        Zoek een variabele op alleen in de huidige scope.
        """
        return self.current_scope.symbols.get(name)

    def __repr__(self):
        result = []

        for scope in self.all_scopes:
            result.append(f"Scope {scope.scope_id} ({scope.name}, level {scope.level}):")
            for name, symbol in scope.symbols.items():
                result.append(f"  {symbol}")

        return "\n".join(result)
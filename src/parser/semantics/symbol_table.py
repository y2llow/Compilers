# Begin heel eenvoudig - dit is een skeleton om te starten
class Symbol:
    """Eén symbool in de tabel"""

    def __init__(self, name, type_name, pointer_depth=0, is_const=False):
        self.name = name
        self.type_name = type_name  # 'int', 'float', 'char'
        self.pointer_depth = pointer_depth  # 0, 1, 2, ...
        self.is_const = is_const
        self.initialized = False


class SymbolTable:
    """De symbol table zelf"""

    def __init__(self):
        self.symbols = {}  # Dictionary: naam -> Symbol object

    def add_symbol(self, name, type_name, pointer_depth=0, is_const=False):
        """Voeg een nieuwe variabele toe"""
        if name in self.symbols:
            return False  # Variabele bestaat al
        self.symbols[name] = Symbol(name, type_name, pointer_depth, is_const)
        return True

    def lookup(self, name):
        """Zoek een variabele op"""
        return self.symbols.get(name)
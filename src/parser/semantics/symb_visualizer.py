# ============================================================
# Symbol Table Visualizer
# ============================================================

def _safe_dot_id(value):
    text = str(value)
    result = []

    for ch in text:
        if ch.isalnum() or ch == "_":
            result.append(ch)
        else:
            result.append("_")

    return "".join(result)


def _symbol_label(sym):
    const = "const " if getattr(sym, "is_const", False) else ""
    stars = "*" * getattr(sym, "pointer_depth", 0)

    dims = ""
    for dim in getattr(sym, "array_dimensions", []) or []:
        dims += f"[{dim}]"

    type_name = getattr(sym, "type_name", "?")
    name = getattr(sym, "name", "?")

    label = f"{const}{type_name}{stars} {name}{dims}"
    return label.replace('"', '\\"')


def render_symbol_table_dot(symbol_table):
    """
    Render symbol table naar Graphviz DOT.

    Werkt met:
    - nieuwe SymbolTable met all_scopes
    - oude fallback met scopes
    """

    dot_lines = [
        "digraph SymbolTable {",
        "    rankdir=TB;",
        '    node [fontname="Helvetica"];',
        ""
    ]

    # Nieuwe symbol table met bewaarde scopes
    if hasattr(symbol_table, "all_scopes"):
        for scope in symbol_table.all_scopes:
            scope_id_num = getattr(scope, "scope_id", 0)
            scope_name = getattr(scope, "name", "scope")
            symbols = getattr(scope, "symbols", {})

            scope_id = f"scope_{scope_id_num}"

            label = f"Scope {scope_id_num}: {scope_name}"
            label = label.replace('"', '\\"')

            dot_lines.append(
                f'    {scope_id} [label="{label}", shape=rectangle];'
            )

            for name, sym in symbols.items():
                safe_name = _safe_dot_id(name)
                sym_id = f"sym_{scope_id_num}_{safe_name}"

                dot_lines.append(
                    f'    {sym_id} [label="{_symbol_label(sym)}", shape=ellipse];'
                )
                dot_lines.append(f"    {scope_id} -> {sym_id};")

            dot_lines.append("")

        # Scope hierarchy tekenen
        for scope in symbol_table.all_scopes:
            parent_id = getattr(scope, "scope_id", 0)

            for child in getattr(scope, "children", []):
                child_id = getattr(child, "scope_id", 0)
                dot_lines.append(f"    scope_{parent_id} -> scope_{child_id};")

    # Fallback oude symbol table
    else:
        for i, scope in enumerate(symbol_table.scopes):
            scope_id = f"scope_{i}"

            dot_lines.append(
                f'    {scope_id} [label="Scope {i}", shape=rectangle];'
            )

            for name, sym in scope.items():
                safe_name = _safe_dot_id(name)
                sym_id = f"sym_{i}_{safe_name}"

                dot_lines.append(
                    f'    {sym_id} [label="{_symbol_label(sym)}", shape=ellipse];'
                )
                dot_lines.append(f"    {scope_id} -> {sym_id};")

    dot_lines.append("}")

    return "\n".join(dot_lines)
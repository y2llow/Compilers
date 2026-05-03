# Compiler CI Testing — concrete stappen en commands

Deze gids legt uit hoe je nieuwe tests aanmaakt, hoe je ze toevoegt aan `tests_manifest.json`, en hoe je de tests lokaal en via GitHub Actions runt.

---

## 1. Huidige teststructuur

De CI-tests staan onder:

```text
src/tests/ci/
  assignment_1_expressions/
    valid/
    invalid/

  assignment_2_types_variables/
    valid/
    invalid_semantic/
    invalid_syntax/

  assignment_3_arrays_io_llvm/
    valid/
    invalid_semantic/
    invalid_syntax/
    runtime/

  tests_manifest.json
```

De lokale test runner staat hier:

```text
scripts/ci_tests.py
```

---

## 2. Soorten tests

Er zijn vier hoofdtypes in het manifest.

### `valid_ast`

Gebruik dit voor geldige C-files waarvoor je wil checken dat:

- de compiler succesvol runt;
- semantic analysis slaagt;
- `ast.dot` wordt aangemaakt;
- `ast.dot` een Graphviz AST-file is.

Voorbeeld in `tests_manifest.json`:

```json
{
  "name": "a1_valid_precedence",
  "assignment": 1,
  "file": "src/tests/ci/assignment_1_expressions/valid/02_precedence.c",
  "expect": "valid_ast",
  "contains": ["Semantic analysis passed"]
}
```

### `syntax_error`

Gebruik dit voor files die syntactisch fout zijn.

De runner checkt:

- compiler exit code is niet `0`;
- output bevat `[Syntax Error]`;
- eventuele extra keywords uit `contains` zitten in de output.

Voorbeeld:

```json
{
  "name": "a1_invalid_missing_semicolon",
  "assignment": 1,
  "file": "src/tests/ci/assignment_1_expressions/invalid/02_missing_semicolon.c",
  "expect": "syntax_error",
  "contains": ["[Syntax Error]"]
}
```

### `semantic_error`

Gebruik dit voor files die syntactisch geldig zijn, maar semantisch fout.

De runner checkt:

- compiler exit code is niet `0`;
- output bevat `[Semantic Error]`;
- eventuele extra keywords uit `contains` zitten in de output.

Voorbeeld:

```json
{
  "name": "a2_invalid_undeclared_variable",
  "assignment": 2,
  "file": "src/tests/ci/assignment_2_types_variables/invalid_semantic/01_undeclared_variable.c",
  "expect": "semantic_error",
  "contains": ["[Semantic Error]", "not declared"]
}
```

### `runtime`

Gebruik dit voor files waarvoor LLVM gegenereerd én uitgevoerd moet worden met `lli`.

De runner checkt:

- compiler kan LLVM genereren;
- `output.ll` bestaat;
- `lli output.ll` kan draaien;
- stdout is exact gelijk aan `expected_stdout`;
- exit code is exact gelijk aan `expected_exit_code`.

Voorbeeld:

```json
{
  "name": "a3_runtime_printf_int",
  "assignment": 3,
  "file": "src/tests/ci/assignment_3_arrays_io_llvm/runtime/02_runtime_printf_int.c",
  "expect": "runtime",
  "contains": ["Semantic analysis passed"],
  "expected_stdout": "5",
  "expected_exit_code": 0
}
```

---

## 3. Nieuwe test aanmaken

### Stap 1 — Kies de juiste map

Gebruik deze regels:

```text
Geldige compiler/AST-test        -> valid/
Syntax error                     -> invalid_syntax/ of invalid/ bij assignment 1
Semantic error                   -> invalid_semantic/
LLVM + runtime-output check      -> runtime/
```

Voor assignment 4 zou je bijvoorbeeld eerst deze structuur kunnen maken:

```bash
mkdir -p src/tests/ci/assignment_4_control_flow/valid
mkdir -p src/tests/ci/assignment_4_control_flow/invalid_semantic
mkdir -p src/tests/ci/assignment_4_control_flow/invalid_syntax
mkdir -p src/tests/ci/assignment_4_control_flow/runtime
```

### Stap 2 — Maak een kleine C-testfile

Voorbeeld: geldige while-loop runtime test.

```bash
cat > src/tests/ci/assignment_4_control_flow/runtime/01_while_loop.c <<'TESTEOF'
int main() {
    int x = 0;
    while (x < 3) {
        x++;
    }
    return x;
}
TESTEOF
```

Voorbeeld: semantic error test.

```bash
cat > src/tests/ci/assignment_4_control_flow/invalid_semantic/01_undeclared_in_if.c <<'TESTEOF'
int main() {
    if (x) {
        return 1;
    }
    return 0;
}
TESTEOF
```

### Stap 3 — Test de file eerst manueel

Voor een valid/syntax/semantic test:

```bash
python -m src.main --input src/tests/ci/assignment_4_control_flow/invalid_semantic/01_undeclared_in_if.c --render_ast ast.dot
```

Voor een runtime test:

```bash
python -m src.main --input src/tests/ci/assignment_4_control_flow/runtime/01_while_loop.c --target_llvm output.ll
lli output.ll
echo $?
```

Bij de while-loop hierboven verwacht je:

```text
stdout: leeg
exit code: 3
```

### Stap 4 — Voeg de test toe aan `tests_manifest.json`

Open:

```text
src/tests/ci/tests_manifest.json
```

Voeg een nieuw object toe in de `tests` array.

Voor de runtime while-loop:

```json
{
  "name": "a4_runtime_while_loop",
  "assignment": 4,
  "file": "src/tests/ci/assignment_4_control_flow/runtime/01_while_loop.c",
  "expect": "runtime",
  "contains": ["Semantic analysis passed"],
  "expected_stdout": "",
  "expected_exit_code": 3
}
```

Voor de semantic error:

```json
{
  "name": "a4_invalid_undeclared_in_if",
  "assignment": 4,
  "file": "src/tests/ci/assignment_4_control_flow/invalid_semantic/01_undeclared_in_if.c",
  "expect": "semantic_error",
  "contains": ["[Semantic Error]", "not declared"]
}
```

### Stap 5 — Check of de JSON nog geldig is

```bash
python -m json.tool src/tests/ci/tests_manifest.json > /tmp/manifest_check.json
```

Als dit niets print, is de JSON geldig.

---

## 4. Tests lokaal runnen

### Alle tests runnen

```bash
python scripts/ci_tests.py
```

### Alle tests runnen zonder runtime

Handig als LLVM/`lli` even niet beschikbaar is:

```bash
python scripts/ci_tests.py --skip-runtime
```

### Alleen assignment 1 runnen

```bash
python scripts/ci_tests.py --assignment 1 --skip-runtime
```

### Alleen assignment 2 runnen

```bash
python scripts/ci_tests.py --assignment 2 --skip-runtime
```

### Alleen assignment 3 runnen zonder runtime

```bash
python scripts/ci_tests.py --assignment 3 --skip-runtime
```

### Alleen assignment 3 runnen inclusief runtime

```bash
python scripts/ci_tests.py --assignment 3
```

### Output bewaren tussen runs

Standaard verwijdert de runner `.ci_out/` bij elke run. Wil je de vorige output bewaren:

```bash
python scripts/ci_tests.py --keep-output
```

De gegenereerde files staan in:

```text
.ci_out/
```

---

## 5. Wat vergelijkt de CI precies?

### Wel vergelijken

```text
Valid tests:
- exit code is 0
- output bevat expected keywords
- ast.dot bestaat
- ast.dot bevat "digraph AST"

Syntax error tests:
- exit code is niet 0
- output bevat "[Syntax Error]"
- output bevat extra keywords uit contains

Semantic error tests:
- exit code is niet 0
- output bevat "[Semantic Error]"
- output bevat extra keywords uit contains

Runtime tests:
- LLVM generatie lukt
- output.ll bestaat
- lli kan output.ll uitvoeren
- stdout exact gelijk
- exit code exact gelijk
```

### Niet vergelijken

```text
- Volledige GCC-output
- Volledige compiler stdout
- Volledige ast.dot snapshots
- Volledige output.ll snapshots
```

Waarom niet?

- GCC geeft andere foutteksten dan onze compiler.
- AST dot output kan veranderen door node IDs of formatting.
- LLVM IR kan veranderen terwijl het programma nog correct werkt.
- Runtime stdout en exit code zijn wel stabiel en belangrijk, dus die vergelijken we exact.

---

## 6. GitHub Actions runnen

De workflow staat hier:

```text
.github/workflows/ci.yml
```

Die draait automatisch bij push en pull request.

Lokaal kan je dezelfde test draaien met:

```bash
python scripts/ci_tests.py
```

Als GitHub Actions faalt, kijk dan in:

```text
GitHub repository -> Actions -> Compiler CI -> failed job
```

Veel voorkomende oorzaken:

```text
ImportError:
- gegenereerde ANTLR Python files staan mogelijk niet in Git

lli not found:
- LLVM is niet goed geïnstalleerd in de workflow

Test faalt op GitHub maar lokaal niet:
- padverschil
- Python-versieverschil
- ontbrekende dependency
- output bevat net andere tekst dan verwacht
```

---

## 7. Committen na nieuwe tests

Als alles lokaal slaagt:

```bash
git status
git add src/tests/ci scripts/ci_tests.py .github/workflows/ci.yml .gitignore
git commit -m "Add CI tests for <feature>"
git push
```

Voor alleen een nieuwe testfile + manifest:

```bash
git add src/tests/ci/<pad-naar-test>.c src/tests/ci/tests_manifest.json
git commit -m "Add test for <feature>"
git push
```

---

## 8. Belangrijke regels voor goede tests

```text
1. Eén test = één duidelijk doel.
2. Hou testfiles klein.
3. Test manueel vóór je de test in het manifest zet.
4. Gebruik valid_ast voor features die nog geen LLVM hebben.
5. Gebruik runtime alleen als LLVM die feature ondersteunt.
6. Gebruik keywords voor syntax/semantic errors, geen volledige output.
7. Runtime stdout en exit code worden wel exact vergeleken.
8. Commit pas als scripts/ci_tests.py lokaal groen is.
```

---

## 9. Snelle checklist voor een nieuwe test

```text
[ ] C-file gemaakt in juiste map
[ ] Manueel getest met --render_ast of --target_llvm
[ ] Expected gedrag bepaald
[ ] Entry toegevoegd aan tests_manifest.json
[ ] JSON gevalideerd met python -m json.tool
[ ] Runner lokaal uitgevoerd
[ ] Alles groen
[ ] Gecommit en gepusht
``` 
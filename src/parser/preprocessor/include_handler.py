"""
Include handler - finds and reads files for #include directives
Supports include guards: #ifndef, #define, #endif
"""

from pathlib import Path
import re


class IncludeHandler:
    """Handles finding and reading #include files with include guard support."""

    def __init__(self, source_file_path: str):
        self.source_file_path = Path(source_file_path).resolve()
        self.source_dir = self.source_file_path.parent
        self.included_files = set()
        self.defined_guards = set()

    def read_include(self, header: str, is_system: bool) -> str:
        if is_system:
            return ""

        # Try source file's directory first, then cwd for project-root-relative paths
        candidate = self.source_dir / header
        if not candidate.exists():
            candidate = Path.cwd() / header
        file_path = candidate

        if not file_path.exists():
            return ""

        file_abs = str(file_path.resolve())
        if file_abs in self.included_files:
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents = f.read()
        except (IOError, OSError):
            return ""

        # Check for include guard
        guard_name = self._extract_include_guard(contents)
        if guard_name:
            if guard_name in self.defined_guards:
                return ""
            self.defined_guards.add(guard_name)

        self.included_files.add(file_abs)

        # Strip #ifndef / #define GUARD / #endif wrapper so the parser
        # never sees directives it doesn't understand.
        # The guard logic above already handles double-inclusion prevention,
        # so stripping is safe here.
        contents = self._strip_include_guard(contents, guard_name)

        return contents

    def _strip_include_guard(self, contents: str, guard_name: str) -> str:
        """
        Remove the include guard wrapper lines from the file contents so that
        the parser only sees valid grammar tokens.

        Strips:
            #ifndef GUARD_NAME      <- removed
            #define GUARD_NAME      <- removed
            ... body ...            <- kept
            #endif                  <- removed (last one)
        """
        if not guard_name:
            return contents

        lines = contents.split('\n')
        result = []
        i = 0
        stripped_ifndef = False
        stripped_define = False

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped_ifndef and re.match(
                    rf'#ifndef\s+{re.escape(guard_name)}\s*$', stripped):
                stripped_ifndef = True
                i += 1
                continue

            if stripped_ifndef and not stripped_define and re.match(
                    rf'#define\s+{re.escape(guard_name)}\s*$', stripped):
                stripped_define = True
                i += 1
                continue

            result.append(line)
            i += 1

        # Remove the last #endif in the file (closes the guard)
        for j in range(len(result) - 1, -1, -1):
            if re.match(r'#endif\b', result[j].strip()):
                result.pop(j)
                break

        return '\n'.join(result)

    def _extract_include_guard(self, contents: str) -> str:
        """
        Extract include guard name from file contents.
        Returns guard name or "" if no guard found.
        """
        lines = contents.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            match = re.match(r'#ifndef\s+(\w+)', line)
            if match:
                guard_name = match.group(1)
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith('//'):
                        continue
                    define_match = re.match(r'#define\s+(\w+)', next_line)
                    if define_match and define_match.group(1) == guard_name:
                        return guard_name
                    return ""
                return ""

            if not line.startswith('#'):
                return ""

        return ""
from antlr4.error.ErrorListener import ErrorListener
import antlr4

RED = '\033[91m'
RESET = '\033[0m'


class SyntaxErrorListener(ErrorListener):

    def __init__(self, source_lines):
        super().__init__()
        self.source_lines = source_lines
        self.errors = []

    def _get_previous_code_line(self, line_num):
        for i in range(line_num - 2, -1, -1):
            line = self.source_lines[i].strip()
            if line and not line.startswith('//'):
                actual_line = i + 1
                source_line = self.source_lines[i].rstrip('\n')
                column = len(source_line)
                return (actual_line, source_line, column)
        return None

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append({
            'line': line,
            'column': column,
            'message': msg,
            'symbol': offendingSymbol
        })
        raise antlr4.error.Errors.ParseCancellationException("syntax error")

    def has_errors(self):
        return len(self.errors) > 0

    def format_errors(self):
        output = []

        sorted_errors = sorted(self.errors, key=lambda e: e['line'])

        deduped_errors = []
        seen_lines = set()
        for error in sorted_errors:
            line = error['line']
            if line not in seen_lines:
                deduped_errors.append(error)
                seen_lines.add(line)

        for error in deduped_errors:
            line_num = error['line']
            column = error['column']
            raw_message = error['message']

            if "missing ';'" in raw_message and line_num > 1:
                result = self._get_previous_code_line(line_num)
                if result:
                    actual_line, source_line, pointer_column = result
                else:
                    actual_line = line_num
                    source_line = self.source_lines[line_num - 1].rstrip('\n') if 0 < line_num <= len(self.source_lines) else ""
                    pointer_column = column
            else:
                actual_line = line_num
                source_line = self.source_lines[line_num - 1].rstrip('\n') if 0 < line_num <= len(self.source_lines) else ""
                pointer_column = column

            output.append(f"{RED}[Syntax Error] line {actual_line}, column {pointer_column}{RESET}")

            if 0 < actual_line <= len(self.source_lines):
                line_num_str = str(actual_line)
                padding = ' ' * len(line_num_str)
                output.append(f"{RED}   {line_num_str} | {source_line}{RESET}")
                output.append(RED + '   ' + padding + ' | ' + ' ' * pointer_column + '^' + RESET)

            output.append('')

        return '\n'.join(output), len(deduped_errors)
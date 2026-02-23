from antlr4.error.ErrorListener import ErrorListener

# ANSI color codes
RED = '\033[91m'
RESET = '\033[0m'


class SyntaxErrorListener(ErrorListener):
    """
    Custom error listener for ANTLR syntax errors.
    Collects errors and formats them nicely with source context.
    """

    def __init__(self, source_lines):
        """
        Args:
            source_lines: List of source code lines (from file.readlines())
        """
        super().__init__()
        self.source_lines = source_lines
        self.errors = []

    def _get_previous_code_line(self, line_num):
        """
        Get the previous non-comment, non-empty line before line_num.
        Returns (line_number, line_content, column_at_end) or None if not found.
        """
        for i in range(line_num - 2, -1, -1):  # Start from line before line_num, go backwards
            line = self.source_lines[i].strip()
            # Skip empty lines and comment lines
            if line and not line.startswith('//'):
                actual_line = i + 1  # Convert back to 1-indexed
                source_line = self.source_lines[i].rstrip('\n')
                column = len(source_line)
                return (actual_line, source_line, column)
        return None

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Called by ANTLR when a syntax error is encountered.

        Args:
            recognizer: The parser or lexer
            offendingSymbol: The token that caused the error
            line: Line number (1-indexed)
            column: Column position (0-indexed)
            msg: Error message from ANTLR
            e: Exception (if any)
        """
        self.errors.append({
            'line': line,
            'column': column,
            'message': msg
        })

    def has_errors(self):
        """Check if any syntax errors were found."""
        return len(self.errors) > 0

    def _add_missing_semicolon_check(self):
        """
        Check if the last non-empty line is missing a semicolon.
        If we have an EOF error, this semicolon error might be hidden.
        """
        # Only run if we have an EOF error
        has_eof_error = any('<EOF>' in e['message'] for e in self.errors)
        if not has_eof_error:
            return

        # Find the last non-empty line
        for i in range(len(self.source_lines) - 1, -1, -1):
            line = self.source_lines[i].strip()
            if line and line != '}' and not line.startswith('//'):  # Skip empty lines, closing braces, and comments
                # Check if it ends with semicolon
                if not line.endswith(';') and not line.endswith('{'):
                    # Add a synthetic semicolon error
                    self.errors.insert(0, {  # Insert at beginning so it shows first
                        'line': i + 2,  # Next line is where ANTLR would detect it
                        'column': 4,    # Typical indentation
                        'message': "missing ';'"
                    })
                break

    def format_errors(self):
        """
        Format all collected errors in a nice readable way.

        Returns:
            String with formatted error messages
        """
        output = []

        # Check for hidden semicolon errors when EOF error exists
        self._add_missing_semicolon_check()

        # Sort errors by line number to show them in order
        sorted_errors = sorted(self.errors, key=lambda e: e['line'])

        for error in sorted_errors:
            line_num = error['line']
            column = error['column']
            message = error['message']

            # Clean up EOF errors
            if '<EOF>' in message:
                message = "unexpected end of file, expected '}'"

            # Smart semicolon detection: if missing ';', show the previous line
            # because that's where the semicolon should actually be
            if "missing ';'" in message and line_num > 1:
                result = self._get_previous_code_line(line_num)
                if result:
                    actual_line, source_line, pointer_column = result
                    display_column = column  # But display the original column in message
                    # Clean up the message - remove the "at 'xxx'" part
                    if " at " in message:
                        message = message.split(" at ")[0]
                else:
                    # Fallback to original line if something goes wrong
                    actual_line = line_num
                    pointer_column = column
                    display_column = column
                    source_line = self.source_lines[line_num - 1].rstrip('\n') if 0 < line_num <= len(
                        self.source_lines) else ""
            else:
                # Normal case: show the line where ANTLR detected the error
                actual_line = line_num
                pointer_column = column
                display_column = column
                source_line = self.source_lines[line_num - 1].rstrip('\n') if 0 < line_num <= len(
                    self.source_lines) else ""

            # Error header (in red) - use display_column
            output.append(f"{RED}[Syntax Error] line {actual_line}, column {display_column}: {message}{RESET}")

            # Get the source line
            if 0 < actual_line <= len(self.source_lines):
                # Line number formatting
                line_num_str = str(actual_line)
                padding = ' ' * len(line_num_str)

                # Show the source line with line number (in red)
                output.append(f"{RED}   {line_num_str} | {source_line}{RESET}")

                # Show pointer (^) at error position (in red) - use pointer_column
                pointer_line = RED + '   ' + padding + ' | ' + ' ' * pointer_column + '^' + RESET
                output.append(pointer_line)

            output.append('')  # Empty line between errors

        return '\n'.join(output)
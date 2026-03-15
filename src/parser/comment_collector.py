class CommentCollector:
    """
    Verzamelt comments uit de token stream en wijst ze toe aan code lijnen.

    Simpele regel:
    - Inline comment: op dezelfde lijn als code, rechts van de code
    - Leading comment: max 1 lege regel boven de code, geen code ertussen
    """

    def __init__(self, token_stream, source_lines):
        self.token_stream = token_stream
        self.source_lines = source_lines
        self.comments_by_line = {}  # line -> {'leading': [...], 'inline': '...'}
        self.code_lines = set()

    def collect(self):
        """Verzamel alle comments en track code lijnen."""
        # Fill token stream
        self.token_stream.fill()
        tokens = self.token_stream.tokens

        # Eerst: verzamel alle comments en code lijnen
        all_comments = []

        for token in tokens:
            # Track code lijnen (DEFAULT channel)
            if token.channel == 0:
                self.code_lines.add(token.line)

            # Verzamel comments (HIDDEN channel)
            elif token.channel == 1:
                text = token.text.strip()

                if text.startswith('//'):
                    # Single-line comment
                    all_comments.append({
                        'line': token.line,
                        'column': token.column,
                        'text': text[2:].strip(),
                        'type': 'line'
                    })

                elif text.startswith('/*') and text.endswith('*/'):
                    # Multi-line comment - maak één regel van
                    inner = text[2:-2].strip()
                    # Vervang alle newlines en extra whitespace
                    inner = inner.replace('\n', ' ').replace('\r', '')
                    # Verwijder dubbele spaties
                    inner = ' '.join(inner.split())

                    all_comments.append({
                        'line': token.line,
                        'column': token.column,
                        'text': inner,
                        'type': 'block'
                    })

        # Nu: wijs comments toe aan code lijnen
        self._assign_comments(all_comments)

    def _assign_comments(self, all_comments):
        """Wijs comments toe aan de juiste code lijnen."""
        for code_line in sorted(self.code_lines):
            leading = []
            inline = None

            for comment in all_comments:
                # Inline: zelfde lijn, na de code
                if comment['line'] == code_line:
                    # Inline comment komt NA de code (grotere column)
                    inline = comment['text']

                # Leading: 1 of 2 lijnen ervoor
                elif code_line - 2 <= comment['line'] < code_line:
                    # Check: is er code tussen deze comment en code_line?
                    has_code_between = any(
                        l in self.code_lines and l != code_line
                        for l in range(comment['line'] + 1, code_line)
                    )

                    if not has_code_between:
                        leading.append(comment['text'])

            # Bewaar bij deze code lijn
            if leading or inline:
                self.comments_by_line[code_line] = {
                    'leading': leading,
                    'inline': inline
                }

    def get_for_line(self, line):
        """
        Haal comments op voor een specifieke lijn.

        Returns: (leading_comments, inline_comment)
            leading_comments: list van strings
            inline_comment: string of None
        """
        if line in self.comments_by_line:
            return (
                self.comments_by_line[line]['leading'],
                self.comments_by_line[line]['inline']
            )
        return [], None
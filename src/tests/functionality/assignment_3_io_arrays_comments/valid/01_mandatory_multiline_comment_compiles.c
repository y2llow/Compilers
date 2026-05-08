/*
 * mandatory: multi-line comments must be accepted by the lexer/parser
 * and must not break compilation.
 */
int main() {
    int x = 1;
    /* comment in a block */
    x = x + 2;
    return x;
}

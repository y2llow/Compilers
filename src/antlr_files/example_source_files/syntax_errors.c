int main () {
    // Error 1: Missing semicolon
    const int x = 5*(3/10 + 9/10)

    // Error 2: Invalid character (@ is not allowed)
    float y = x @ 2;

    // Error 3: Missing closing parenthesis
    int z = (5 + 3;

    // Error 4: Misspelled keyword (floot instead of float)
    floot a = 3.14;

    // Error 5: Missing semicolon again
    char ch = 'x'

    // Error 6: Extra closing brace
    }}

    // Error 7: Missing opening brace for an if-statement (but we don't support if yet, so this will give weird error)
    int* ptr = &x;

// Error 8: Missing closing brace at the end (remove one } to test)
// ============================================================
// Pure Syntax Error Test File
// Contains ONLY syntactic errors (no semantic/type errors)
// ============================================================

int main () {
    // -- Category 1: Missing Semicolons --

    // Error: Missing semicolon after variable declaration
    const int x = 5*(3/10 + 9/10)

    // Error: Missing semicolon after assignment
    int a = 10

    // Error: Missing semicolon after expression
    x + a

    // Error: Missing semicolon with complex expression
    int complex_missing = (5 + 3) * (2 - 1) / (4 % 3)


    // -- Category 2: Invalid Characters/Tokens --

    // Error: Invalid character @
    float y = x @ 2;

    // Error: Invalid character $ in expression
    int result = 5 $ 3;

    // Error: Invalid character # (not in preprocessor context)
    int z = x # 5;


    // -- Category 3: Parentheses Errors --

    // Error: Missing closing parenthesis
    int z1 = (5 + 3;

    // Error: Missing opening parenthesis
    int w = 5 + 3);

    // Error: Extra closing parenthesis
    int v = (5 + 3));

    // Error: Mismatched parentheses in complex expression
    int complex = ((5 + 3) * (2 + 1);

    // Error: Multiple unmatched parentheses
    int multi_paren = ((5 + (3 * 2);


    // -- Category 4: Invalid Operators --

    // Error: Invalid operator ===
    int test = (5 === 5);

    // Error: Invalid operator <>
    int compare = (x <> y);


    // -- Category 5: Missing Elements in Declarations --

    // Error: Missing identifier after pointer star
    int* = &x;

    // Error: Missing identifier after type
    int * ;

    // Error: Missing identifier after const
    const int;

    // Error: Missing identifier in double pointer
    int** = &x;


    // -- Category 6: Missing Assignment Values --

    // Error: Missing right-hand side of assignment
    int incomplete = ;

    // Error: Missing assignment value
    const float pi = ;

    // Error: Assignment without value
    float empty = ;


    // -- Category 7: Invalid Literal Formats --

    // Error: Invalid float literal (multiple dots)
    float bad_float = 3.14.159;

    // Error: Unclosed character literal
    char bad_char = 'x;

    // Error: Empty character literal
    char empty_char = '';

    // Error: Multiple character literal without closing
    char multi = 'abc;


    // -- Category 8: Cast Errors --

    // Error: Missing closing parenthesis in cast
    int casted = (int x;

    // Error: Invalid cast syntax (missing type)
    float f = () 3.14;

    // Error: Cast without operand
    int cast_no_operand = (int);


    // -- Category 9: Missing Operands --

    // Error: Missing operator between operands (might be parsed differently)
    int no_op = 5 3;

    // Error: Incomplete binary operation
    int incomplete_op = 5 + ;

    // Error: Missing operand after operator
    int missing_operand = * ;

    // Error: Binary operator without right operand
    int no_right = 10 * ;

    // Error: Binary operator without left operand
    int no_left = * 10;


    // -- Category 10: Increment/Decrement Errors --

    // Error: Increment without operand
    ++;

    // Error: Decrement without operand
    --;

    // Error: Invalid increment syntax (4 minus signs)
    int dec = ----;


    // -- Category 11: Assignment Operator Errors --

    // Error: Double equals instead of single (might parse as comparison)
    int double_assign == 5;

    // Error: Assignment without left side
    = 42;


    // -- Category 12: Expression Errors --

    // Error: Expression starting with binary operator
    int starts_with_mult = * 5;

    // Error: Operator at end of expression
    int ends_with_op = 5 + ;

    // Error: Double operators
    int double_op = 5 ** 3;


    // -- Category 13: Multiple Errors on Same Line --

    // Error: Missing semicolon AND invalid character
    int multi1 = 5 @ 3

    // Error: Missing semicolon and invalid operator
    float combo = x <> y

    // Error: Invalid operator and missing semicolon
    int multi2 = 10 === 10


    // -- Category 14: Brace Errors --

    // Error: Extra closing brace
    }

    // Continue after error
    int after_brace = 10;


    // -- Category 15: Complex Nested Errors --

    // Error: Missing semicolon in nested expression
    int nested = (5 + (3 * 2))

    // Error: Unclosed parentheses with operators
    int unclosed = (5 + 3 * (2 - 1;

    // Error: Multiple missing semicolons in sequence
    char ch = 'x'
    int num = 5
    float flt = 3.14


    // -- Category 16: Pointer Operator Errors --

    // Error: Address-of without target
    int* bad_addr = &;

    // Error: Dereference without target
    int deref_bad = *;


    // Valid statements to end properly
    int valid1 = 42;
    float valid2 = 3.14;
    char valid3 = 'A';

}

// Error: Extra closing brace at end
}

// Error: Statement after main without proper structure
int orphan = 42;
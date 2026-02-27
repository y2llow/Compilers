int main() {
    // ========== BASIS DECLARATIES ==========
    int a;
    int b = 10;
    float c = 3.14;
    char d = 'x';
    const int e = 42;
    int* ptr_i;
    float* ptr_f;
    const int* ptr_const;

    // ========== INITIALISATIES ==========
    a = 5;
    ptr_i = &a;
    ptr_f = &c;
    ptr_const = &e;

    // ========== TEST 1: Undeclared variables ==========
    int x = y;              // ERROR: y is niet gedeclareerd
    z = 42;                 // ERROR: z is niet gedeclareerd
    undeclared = a + b;     // ERROR: undeclared is niet gedeclareerd

    // ========== TEST 2: Redeclaration ==========
    int a = 20;             // ERROR: a is al gedeclareerd
    float b = 3.14;         // ERROR: b is al gedeclareerd
    int ptr_i = 5;          // ERROR: ptr_i is al gedeclareerd

    // ========== TEST 3: Const correctness ==========
    e = 100;                // ERROR: assignment to const variable
    const int local_const = 50;
    local_const = 60;       // ERROR: assignment to const variable

    // ========== TEST 4: Type mismatches in assignment ==========
    a = c;                  // WARNING: float to int loses information
    d = a;                  // WARNING: int to char loses information
    a = 3.14;               // WARNING: float literal to int

    // ========== TEST 5: Pointer type mismatches ==========
    ptr_i = &c;             // ERROR: can't assign float* to int*
    ptr_f = &a;             // ERROR: can't assign int* to float*

    // ========== TEST 6: Dereference operations ==========
    *ptr_i = 42;            // OK
    *ptr_i = c;             // WARNING: float to int through pointer
    *ptr_const = 99;        // ERROR: assignment through pointer-to-const

    // ========== TEST 7: Address-of operations ==========
    int** pptr = &ptr_i;    // OK
    int*** ppptr = &pptr;   // OK
    ptr_i = &(a + b);       // ERROR: can't take address of expression

    // ========== TEST 8: Arithmetic operations ==========
    int r1 = a + b;         // OK: int + int
    int r2 = a + c;         // WARNING: int + float to int
    float r3 = a + c;       // OK: int + float to float
    int r4 = a - b;         // OK
    int r5 = a * b;         // OK
    int r6 = a / b;         // OK
    int r7 = a % b;         // OK

    // ========== TEST 9: Pointer arithmetic ==========
    ptr_i = ptr_i + 5;      // OK: pointer + integer
    ptr_i = ptr_i - 2;      // OK: pointer - integer
    int diff = ptr_i - &a;  // OK: pointer - pointer
    ptr_i = ptr_i + c;      // WARNING: pointer + float (float to int)
    ptr_i = ptr_i + d;      // OK: pointer + char (char promoted to int)

    // ========== TEST 10: Unary operators ==========
    int u1 = +a;            // OK
    int u2 = -a;            // OK
    int u3 = !a;            // OK
    int u4 = ~a;            // OK
    int u5 = -c;            // WARNING: -float to int
    int u6 = !c;            // WARNING: !float to int
    int u7 = ~c;            // ERROR: bitwise not on float
    int u8 = !ptr_i;        // WARNING: logical not on pointer

    // ========== TEST 11: Increment/Decrement ==========
    a++;                    // OK
    b--;                    // OK
    c++;                    // OK: float++ is allowed
    ptr_i++;                // OK: pointer increment
    d++;                    // OK: char increment

    const int const_var = 123;
    const_var++;            // ERROR: increment on const

    5++;                    // ERROR: increment on literal
    (a + b)++;              // ERROR: increment on expression

    // ========== TEST 12: Assignment to rvalue ==========
    5 = a;                  // ERROR: assignment to literal
    (a + b) = 10;           // ERROR: assignment to expression

    // ========== TEST 13: Comparison operators ==========
    int cmp1 = a < b;       // OK: yields int
    int cmp2 = a == c;      // OK: int == float
    int cmp3 = ptr_i == &a; // OK: pointer comparison
    int cmp4 = ptr_i == a;  // WARNING: pointer vs integer
    int cmp5 = ptr_i == ptr_f; // ERROR: different pointer types

    // ========== TEST 14: Logical operators ==========
    int log1 = a && b;      // OK
    int log2 = a || c;      // OK
    int log3 = !a;          // OK
    int log4 = ptr_i && a;  // WARNING: pointer in logical

    // ========== TEST 15: Mixed operations ==========
    int complex = a + b * c - d / a;  // WARNING: multiple conversions

    // ========== TEST 16: Multiple errors in one line ==========
    undecl1 = undecl2 + undecl3;  // ERROR: 3 undeclared variables

    // ========== TEST 17: Nested expressions with undeclared ==========
    int nested = a + (b * (c - unknown));  // ERROR: undeclared 'unknown'

}
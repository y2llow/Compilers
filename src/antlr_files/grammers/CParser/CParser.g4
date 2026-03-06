grammar CParser;

// ========================================
// PARSER RULES (lowercase)
// ========================================

// Top-level: a C file has exactly one main function
translation_unit
    : main_function EOF
    ;

main_function
    : INT MAIN '(' ')' '{' statement* '}'
    ;

// ── Statements ───────────────────────────────────────────────
// A statement is one of the following

statement
    : var_decl ';'       // int x = 5;
    | assignment ';'     // x = 5;
    | expression ';'     // 5 + 3;
    ;

// ── Variable declaration/definition ──────────────────────────
// Examples:
//   int x;
//   const float y = 3.14;
//   int* ptr = &x;
//   const int** ptr2;
//   int arr[10];
//   int matrix[3][4];
//   int values[3] = {1, 2, 3};

var_decl
    : CONST? type_spec '*'* IDENTIFIER array_dimension* ('=' array_initializer)?
    ;

// Array dimensions: [10] or [3][4], etc.
array_dimension
    : '[' INTEGER ']'
    ;

// Array initializer: {1, 2, 3} or {{1,2},{3,4}}, etc.
array_initializer
    : '{' initializer_list '}'
    ;

initializer_list
    : initializer (',' initializer)*
    ;

initializer
    : expression
    | array_initializer
    ;

// The basic types — easy to extend later
type_spec
    : INT
    | FLOAT_KW
    | CHAR_KW
    ;

// ── Assignment ───────────────────────────────────────────────
// Examples:
//   x = 5;
//   *ptr = 3;
//   arr[5] = 10;
//   matrix[1][2] = 42;

assignment
    : unary_expr '=' expression
    ;

// ── Expressions (order of precedence, lowest to highest) ─────

expression
    : expression ('*' | '/' | '%') expression          # mulDivMod
    | expression ('+' | '-') expression                # addSub
    | expression ('<<' | '>>') expression              # shift
    | expression ('<' | '>' | '<=' | '>=') expression  # relational
    | expression ('==' | '!=') expression              # equality
    | expression '&' expression                        # bitwiseAnd
    | expression '^' expression                        # bitwiseXor
    | expression '|' expression                        # bitwiseOr
    | expression '&&' expression                       # logicalAnd
    | expression '||' expression                       # logicalOr
    | unary_expr                                       # unaryExpr
    ;

// ── Unary expressions ─────────────────────────────────────────
// Examples:
//   -x, !x, ~x
//   *ptr (dereference)
//   &x (address-of)
//   ++x, --x (prefix)
//   (int) x (cast)

unary_expr
    : '!' unary_expr                    # logicalNot
    | '~' unary_expr                    # bitwiseNot
    | ('+' | '-') unary_expr            # unaryPlusMinus
    | '*' unary_expr                    # dereference
    | '&' unary_expr                    # addressOf
    | '++' unary_expr                   # prefixIncrement
    | '--' unary_expr                   # prefixDecrement
    | '(' type_spec '*'* ')' unary_expr # cast
    | postfix_expr                      # postfixExprRule
    ;

// ── Postfix expressions ───────────────────────────────────────
// x++, x--, arr[5], matrix[1][2]

postfix_expr
    : primary_expr postfix_op*
    ;

postfix_op
    : '++'                              # postfixIncrement
    | '--'                              # postfixDecrement
    | '[' expression ']'                # arrayAccess
    ;

// ── Primary expressions ───────────────────────────────────────
// The "building blocks": literals, identifiers, parentheses

primary_expr
    : '(' expression ')'               # parens
    | literal                          # literalExpr
    | IDENTIFIER                       # identifierExpr
    ;

// ── Literals ──────────────────────────────────────────────────
// Easy to extend: just add a new alternative

literal
    : INTEGER                          # intLiteral
    | FLOAT_LIT                        # floatLiteral
    | CHAR_LIT                         # charLiteral
    ;

// ========================================
// LEXER RULES (UPPERCASE)
// ========================================

// ── Keywords ──────────────────────────────────────────────────
// Keywords must be defined BEFORE the IDENTIFIER rule,
// otherwise they will be recognized as identifiers!

CONST   : 'const' ;
INT     : 'int' ;
FLOAT_KW: 'float' ;
CHAR_KW : 'char' ;
MAIN    : 'main' ;

// ── Literals ──────────────────────────────────────────────────

// Float must be defined before INTEGER, otherwise "3.14" would be
// tokenized as "3" followed by ".14"
FLOAT_LIT  : [0-9]+ '.' [0-9]+ ;
INTEGER    : [0-9]+ ;

// Character literal: 'a', 'x', '\n', etc.
CHAR_LIT   : '\'' ( ~['\\] | '\\' . ) '\'' ;

// Identifier: starts with a letter or underscore, followed by letters/digits/underscores
IDENTIFIER : [a-zA-Z_][a-zA-Z_0-9]* ;

// ── Whitespace and comments ───────────────────────────────────

WS            : [ \t\r\n]+  -> skip ;

// Single-line comments
LINE_COMMENT  : '//' ~[\r\n]* -> channel(HIDDEN) ;

// Multi-line comments
BLOCK_COMMENT : '/*' .*? '*/' -> channel(HIDDEN) ;
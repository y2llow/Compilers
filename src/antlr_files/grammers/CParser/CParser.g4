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
statement
    : var_decl ';'
    | assignment ';'
    | return_statement
    | expression ';'
    ;

// Return statement
return_statement
    : 'return' expression? ';'
    ;

// ── Variable declaration ──────────────────────────────────────
var_decl
    : CONST? type_spec '*'* IDENTIFIER array_dimension* ('=' var_initializer)?
    ;

// Array dimensions: [10] or [3][4], etc.
array_dimension
    : '[' INTEGER ']'
    ;

// Variable initializer - can be expression OR array initializer
var_initializer
    : array_initializer
    | expression
    ;

// Array initializer: {1, 2, 3} or {{1,2},{3,4}}, etc.
array_initializer
    : '{' initializer_list? '}'
    ;

initializer_list
    : initializer (',' initializer)*
    ;

initializer
    : expression
    | array_initializer
    ;

// The basic types
type_spec
    : INT
    | FLOAT_KW
    | CHAR_KW
    ;

// ── Assignment ───────────────────────────────────────────────
assignment
    : postfix_expr '=' expression
    ;

// ── Expressions ───────────────────────────────────────────────
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
    | postfix_expr                                     # postfixExpr
    ;

// ── Unary expressions ─────────────────────────────────────────
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
// Handles: arr[5], matrix[i][j], arr[5]++, etc.
postfix_expr
    : primary_expr postfix_op*
    ;

postfix_op
    : '[' expression ']'                # arrayAccess
    | '++'                              # postfixIncrement
    | '--'                              # postfixDecrement
    ;

// ── Primary expressions ───────────────────────────────────────
primary_expr
    : '(' expression ')'                # parens
    | literal                           # literalExpr
    | IDENTIFIER                        # identifierExpr
    ;

// ── Literals ──────────────────────────────────────────────────
literal
    : INTEGER                           # intLiteral
    | FLOAT_LIT                         # floatLiteral
    | CHAR_LIT                          # charLiteral
    | STRING_LIT                        # stringLiteral  ← ADD THIS
    ;

// ========================================
// LEXER RULES (UPPERCASE)
// ========================================

CONST    : 'const' ;
INT      : 'int' ;
FLOAT_KW : 'float' ;
CHAR_KW  : 'char' ;
MAIN     : 'main' ;

// Float must be defined before INTEGER
FLOAT_LIT  : [0-9]+ '.' [0-9]+ ;
INTEGER    : [0-9]+ ;

// String literal: "hello", "world\n", etc.
STRING_LIT : '"' ( ~["\\\r\n] | '\\' . )* '"' ;

// Character literal: 'a', 'x', '\n', etc.
CHAR_LIT   : '\'' ( ~['\\] | '\\' . ) '\'' ;

// Identifier
IDENTIFIER : [a-zA-Z_][a-zA-Z_0-9]* ;

// Whitespace and comments
WS            : [ \t\r\n]+  -> skip ;
LINE_COMMENT  : '//' ~[\r\n]* -> channel(HIDDEN) ;
BLOCK_COMMENT : '/*' .*? '*/' -> channel(HIDDEN) ;
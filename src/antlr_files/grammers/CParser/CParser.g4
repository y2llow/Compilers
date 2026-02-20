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

var_decl
    : CONST? type_spec '*'* IDENTIFIER ('=' expression)?
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
// x++, x--

postfix_expr
    : primary_expr '++'                 # postfixIncrement
    | primary_expr '--'                 # postfixDecrement
    | primary_expr                      # primaryExprRule
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
COMMENT       : '//' ~[\r\n]* -> skip ;
BLOCK_COMMENT : '/*' .*? '*/' -> skip ;
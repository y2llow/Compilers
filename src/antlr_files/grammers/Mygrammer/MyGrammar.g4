grammar MyGrammar;

// ========================================
// PARSER RULES (lowercase)
// ========================================

// Top-level: a C program is a list of functions
translation_unit
    : function_definition+
    ;

// A function: return_type name() { statements }
function_definition
    : type_specifier IDENTIFIER '(' ')' compound_statement
    ;

// Types we support
type_specifier
    : 'int'
    | 'void'
    ;

// A block of code: { ... }
compound_statement
    : '{' statement* '}'
    ;

// Different kinds of statements
statement
    : return_statement
    | declaration_statement
    | expression_statement
    ;

// return 0;
return_statement
    : 'return' expression? ';'
    ;

// int x;  or  int x = 5;
declaration_statement
    : type_specifier IDENTIFIER ('=' expression)? ';'
    ;

// Any expression followed by semicolon
expression_statement
    : expression? ';'
    ;

// Simple expressions (just numbers for now)
expression
    : NUMBER
    | IDENTIFIER
    ;

// ========================================
// LEXER RULES (UPPERCASE)
// ========================================

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

NUMBER
    : [0-9]+
    ;

// Skip whitespace, tabs, newlines
WS
    : [ \t\r\n]+ -> skip
    ;

// Skip comments
COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;
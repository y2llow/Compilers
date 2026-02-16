
// ------------------------
// Parser rules
// ------------------------

translation_unit
    : external_declaration+
    ;

external_declaration
    : function_definition
    | declaration
    ;

function_definition
    : type_specifier declarator compound_statement
    ;

type_specifier
    : 'int'
    | 'char'
    | 'float'
    | 'double'
    | 'void'
    ;

declarator
    : IDENTIFIER '(' ')'    // only simple functions with no args
    ;

compound_statement
    : '{' block_item* '}'
    ;

block_item
    : declaration
    | statement
    ;

declaration
    : type_specifier init_declarator_list ';'
    ;

init_declarator_list
    : init_declarator (',' init_declarator)*
    ;

init_declarator
    : IDENTIFIER ('=' CONSTANT)?
    ;

statement
    : expression_statement
    | return_statement
    ;

expression_statement
    : expression? ';'
    ;

return_statement
    : 'return' expression? ';'
    ;

expression
    : IDENTIFIER '=' CONSTANT
    ;

// ------------------------
// Lexer rules
// ------------------------

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

CONSTANT
    : [0-9]+
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

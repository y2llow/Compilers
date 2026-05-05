grammar CParser;

// ========================================
// PARSER RULES
// ========================================

translation_unit
    : top_level_item* EOF
    ;

top_level_item
    : include_directive
    | define_directive
    | typedef_decl
    | enum_decl ';'
    | struct_decl ';'
    | function_definition
    | function_declaration ';'
    | var_decl ';'
    ;

// ── Preprocessor ─────────────────────────────────────────────

include_directive
    : HASH INCLUDE (LT_STDIO_H | STRING_LIT)
    ;

define_directive
    : HASH DEFINE IDENTIFIER define_value
    ;

define_value
    : INTEGER
    | FLOAT_LIT
    | CHAR_LIT
    | STRING_LIT
    | IDENTIFIER
    | INT
    | FLOAT_KW
    | CHAR_KW
    | VOID
    ;

// ── Typedef ───────────────────────────────────────────────────

typedef_decl
    : TYPEDEF type_spec '*'* IDENTIFIER ';'
    | TYPEDEF struct_specifier IDENTIFIER ';'
    | TYPEDEF enum_specifier IDENTIFIER ';'
    ;

// ── Enum ──────────────────────────────────────────────────────

enum_decl
    : enum_specifier
    ;

enum_specifier
    : ENUM IDENTIFIER '{' enum_body '}'
    | ENUM IDENTIFIER
    ;

enum_body
    : enum_constant (',' enum_constant)* ','?
    ;

enum_constant
    : IDENTIFIER ('=' INTEGER)?
    ;

// ── Struct ────────────────────────────────────────────────────

struct_decl
    : struct_specifier
    ;

struct_specifier
    : STRUCT IDENTIFIER ('{' struct_member* '}')?
    ;

struct_member
    : type_spec '*'* IDENTIFIER array_dimension* ';'
    | enum_specifier IDENTIFIER ';'
    | struct_specifier IDENTIFIER ';'
    ;

// ── Functions ─────────────────────────────────────────────────

function_definition
    : return_type_spec IDENTIFIER '(' parameter_list? ')' compound_statement
    ;

// Forward declaration
function_declaration
    : return_type_spec IDENTIFIER '(' parameter_list? ')'
    ;

return_type_spec
    : VOID
    | type_spec '*'*
    ;

parameter_list
    : parameter (',' parameter)*
    | VOID
    ;

parameter
    : CONST? type_spec CONST? '*'* IDENTIFIER array_dimension*
    ;

// ── Compound statement (block) ────────────────────────────────

compound_statement
    : '{' block_item* '}'
    ;

block_item
    : statement
    | var_decl ';'
    ;

// ── Statements ────────────────────────────────────────────────

statement
    : compound_statement
    | if_statement
    | while_statement
    | for_statement
    | switch_statement
    | return_statement
    | break_statement
    | continue_statement
    | printf_statement ';'
    | scanf_statement ';'
    | assignment ';'
    | unary_expr ';'
    | expression ';'
    | ';'
    ;

if_statement
    : IF '(' expression ')' compound_statement (ELSE compound_statement)?
    ;

while_statement
    : WHILE '(' expression ')' compound_statement
    ;

for_statement
    : FOR '(' for_init ';' expression? ';' for_update? ')' compound_statement
    ;

for_init
    : var_decl
    | assignment
    | expression
    |
    ;

for_update
    : assignment
    | unary_expr
    | expression
    ;

switch_statement
    : SWITCH '(' expression ')' '{' switch_case* switch_default? '}'
    ;

switch_case
    : CASE expression ':' block_item*
    ;

switch_default
    : DEFAULT ':' block_item*
    ;

return_statement
    : RETURN expression? ';'
    ;

break_statement
    : BREAK ';'
    ;

continue_statement
    : CONTINUE ';'
    ;

// ── printf / scanf ────────────────────────────────────────────

printf_statement
    : PRINTF '(' expression (',' printf_arg)* ')'
    ;

printf_arg
    : expression
    ;

scanf_statement
    : SCANF '(' STRING_LIT (',' scanf_arg)* ')'
    ;

scanf_arg
    : expression
    ;

// ── Variable declaration ──────────────────────────────────────

var_decl
    : CONST? type_spec CONST? '*'* IDENTIFIER array_dimension* ('=' var_initializer)?
    ;

array_dimension
    : '[' INTEGER ']'
    ;

var_initializer
    : array_initializer
    | expression
    ;

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

// ── Types ─────────────────────────────────────────────────────

type_spec
    : INT
    | FLOAT_KW
    | CHAR_KW
    | IDENTIFIER        // for typedef'd types and enum/struct names
    | enum_specifier
    | struct_specifier
    ;

// ── Assignment ───────────────────────────────────────────────

assignment
    : unary_expr assign_op expression
    ;

assign_op
    : '='
    | '+='
    | '-='
    | '*='
    | '/='
    | '%='
    | '&='
    | '|='
    | '^='
    | '<<='
    | '>>='
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
    | expression '?' expression ':' expression         # ternary
    | unary_expr                                       # unaryExpr
    ;

// ── Unary expressions ─────────────────────────────────────────

unary_expr
    : '!' unary_expr                                    # logicalNot
    | '~' unary_expr                                    # bitwiseNot
    | ('+' | '-') unary_expr                            # unaryPlusMinus
    | '*' unary_expr                                    # dereference
    | '&' unary_expr                                    # addressOf
    | '++' unary_expr                                   # prefixIncrement
    | '--' unary_expr                                   # prefixDecrement
    | '(' CONST? type_spec '*'* ')' unary_expr          # cast
    | SIZEOF '(' type_spec '*'* ')'                     # sizeofType
    | SIZEOF '(' unary_expr ')'                         # sizeofExpr
    | postfix_expr                                      # postfixExprRule
    ;

// ── Postfix expressions ───────────────────────────────────────

postfix_expr
    : primary_expr postfix_op*
    ;

postfix_op
    : '[' expression ']'                # arrayAccess
    | '(' argument_list? ')'           # functionCall
    | '.' IDENTIFIER                   # memberAccess
    | '->' IDENTIFIER                  # pointerMemberAccess
    | '++'                             # postfixIncrement
    | '--'                             # postfixDecrement
    ;

argument_list
    : expression (',' expression)*
    ;

// ── Primary expressions ───────────────────────────────────────

primary_expr
    : '(' expression ')'               # parens
    | literal                          # literalExpr
    | IDENTIFIER                       # identifierExpr
    ;

// ── Literals ──────────────────────────────────────────────────

literal
    : INTEGER                          # intLiteral
    | FLOAT_LIT                        # floatLiteral
    | CHAR_LIT                         # charLiteral
    | STRING_LIT                       # stringLiteral
    ;

// ========================================
// LEXER RULES
// ========================================

// Keywords
CONST    : 'const' ;
INT      : 'int' ;
FLOAT_KW : 'float' ;
CHAR_KW  : 'char' ;
VOID     : 'void' ;
RETURN   : 'return' ;
IF       : 'if' ;
ELSE     : 'else' ;
WHILE    : 'while' ;
FOR      : 'for' ;
BREAK    : 'break' ;
CONTINUE : 'continue' ;
SWITCH   : 'switch' ;
CASE     : 'case' ;
DEFAULT  : 'default' ;
ENUM     : 'enum' ;
STRUCT   : 'struct' ;
UNION    : 'union' ;
TYPEDEF  : 'typedef' ;
SIZEOF   : 'sizeof' ;
PRINTF   : 'printf' ;
SCANF    : 'scanf' ;

// Preprocessor
HASH          : '#' ;
INCLUDE       : 'include' ;
DEFINE        : 'define' ;
LT_STDIO_H    : '<stdio.h>' ;

// Literals (float before int!)
FLOAT_LIT  : [0-9]+ '.' [0-9]* | '.' [0-9]+ ;
INTEGER    : [0-9]+ ;
STRING_LIT : '"' ( '\\' . | ~["\\\r\n] )* '"' ;
CHAR_LIT   : '\'' ( '\\' . | ~['\\\r\n] ) '\'' ;

// Identifier (after all keywords!)
IDENTIFIER : [a-zA-Z_][a-zA-Z_0-9]* ;

// Whitespace and comments
WS            : [ \t\r\n]+ -> skip ;
LINE_COMMENT  : '//' ~[\r\n]* -> channel(HIDDEN) ;
BLOCK_COMMENT : '/*' .*? '*/' -> channel(HIDDEN) ;
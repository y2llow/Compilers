grammar Operations_grammer;

// ========================================
// PARSER RULES (lowercase)
// ========================================

// Top-level: a file is one or more expressions ending with semicolons
translation_unit
    : (expression ';')+ EOF
    ;

// Expressions are defined in ORDER OF PRECEDENCE (lowest to highest).
// ANTLR resolves ambiguity by trying alternatives top-to-bottom,
// so we put the LOOSEST binding operators first.

// Tier 1 (lowest precedence): logical OR
expression
    : expression '||' expression         # logicalOr
    | expression '&&' expression         # logicalAnd
    | expression '|'  expression         # bitwiseOr
    | expression '^'  expression         # bitwiseXor
    | expression '&'  expression         # bitwiseAnd
    | expression ('==' | '!=') expression           # equality
    | expression ('<' | '>' | '<=' | '>=') expression  # relational
    | expression ('<<' | '>>') expression            # shift
    | expression ('+' | '-') expression              # addSub
    | expression ('*' | '/' | '%') expression        # mulDivMod
    | '!' expression                     # logicalNot
    | '~' expression                     # bitwiseNot
    | ('+' | '-') expression             # unary
    | '(' expression ')'                 # parens
    | literal                            # literalExpr
    ;

// A literal (only int for now, easy to add float/char/string later)
literal
    : INTEGER   # intLiteral
    ;

// ========================================
// LEXER RULES (UPPERCASE)
// ========================================

INTEGER : [0-9]+ ;

// Skip whitespace
WS : [ \t\r\n]+ -> skip ;

// Skip single-line and block comments
COMMENT       : '//' ~[\r\n]* -> skip ;
BLOCK_COMMENT : '/*' .*? '*/' -> skip ;
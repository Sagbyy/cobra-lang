# -*- coding: utf-8 -*-
 
from genereTreeGraphviz2 import printTreeGraph
reserved={
        'print':'PRINT',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        }
 
tokens = [ 'NUMBER','MINUS', 'PLUS','TIMES','DIVIDE', 'LPAREN',
          'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
          'EGALEGAL','INFEG', 'LBRACKET', 'RBRACKET', 'BOOLEAN'] + list(reserved.values())
 
t_PLUS = r'\+' 
t_MINUS = r'-' 
t_TIMES = r'\*' 
t_DIVIDE = r'/' 
t_LPAREN = r'\(' 
t_RPAREN = r'\)' 
t_OR = r'\|'
t_AND = r'\&'
t_SEMI = r';'
t_EGAL = r'\='
t_INF = r'\<'
t_SUP = r'>'
t_INFEG = r'\<\='
t_EGALEGAL = r'\=\='
t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
 
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t
 
 
def t_NUMBER(t): 
    r'\d+' 
    t.value = int(t.value) 
    return t

def t_BOOLEAN(t):
    r'true|false'
    if t.value == 'true':
        t.value = True
    else:
        t.value = False
    return t
 
t_ignore = " \t"
 
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
 
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
 
import ply.lex as lex
lex.lex()
 
names={}
precedence = ( 
        ('left','OR' ), 
        ('left','AND'), 
        ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'), 
        ('left','PLUS', 'MINUS' ), 
        ('left','TIMES', 'DIVIDE'), 
        )

def evalInst(p):
    if p == 'empty' : return
    if type(p)==tuple : 
        if p[0]=='print' : print(evalExpr(p[1]))
        if p[0]=='bloc' :
            evalInst(p[1])
            evalInst(p[2])
        if p[0] == 'assign' : 
            names[p[1]] = evalExpr(p[2])
        if p[0] == 'while' :
            while evalExpr(p[1]):
                evalInst(p[2])
        if p[0] == 'for' :
            evalInst(p[1])  # Initialisation
            while evalExpr(p[2]):  # Condition
                evalInst(p[4])  # Corps de la boucle
                evalInst(p[3])  # Incrémentation
        if p[0] == 'incrementation' :
            names[p[1]] += 1
 
 
def evalExpr(t):
    if type(t) == int : return t
    if type(t) == str :
        if t == 'true': return True
        if t == 'false': return False
        if t in names : return names[t]
        return "pas truove"
    if t[0]=='+': return evalExpr(t[1]) + evalExpr(t[2])
    if t[0]=='*': return evalExpr(t[1]) * evalExpr(t[2])
    if t[0]=='/': return evalExpr(t[1]) / evalExpr(t[2])
    if t[0]=='-': return evalExpr(t[1]) - evalExpr(t[2])
    if t[0]=='<': return evalExpr(t[1]) < evalExpr(t[2])
    if t[0]=='<=': return evalExpr(t[1]) <= evalExpr(t[2])
    if t[0]=='>': return evalExpr(t[1]) > evalExpr(t[2])
    if t[0]=='>=': return evalExpr(t[1]) >= evalExpr(t[2])
    if t[0]=='==': return evalExpr(t[1]) == evalExpr(t[2])
    if t[0]=='&': return evalExpr(t[1]) and evalExpr(t[2])
    if t[0]=='|': return evalExpr(t[1]) or evalExpr(t[2])
 
def p_start(p):
    'start : bloc'
    print(p[1])
    printTreeGraph(p[1])
    evalInst(p[1])
 
def p_bloc(p):
    '''bloc : bloc statement SEMI
    | statement SEMI'''
    if len(p)==3 : 
        p[0] = ('bloc',p[1],'empty' )
    else : 
        p[0] = ('bloc',p[1],p[2] )
        
def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACKET bloc RBRACKET'
    p[0] = ('for', p[3], p[5], p[7], p[10])
    
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACKET bloc RBRACKET'
    p[0] = ('while', p[3], p[6])
 
def p_statement_expr(p): 
    'statement : PRINT LPAREN expression RPAREN' 
    p[0] = ('print',p[3] )
 
def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign',p[1],p[3] ) 

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN bloc'
    p[0] = ('if', p[1], p[3], p[5]) 

def p_statement_if_else(p):
    'statement : IF LPAREN expression RPAREN '

def p_expression_binop_inf(p): 
    '''expression : expression INF expression
    | expression INFEG expression
    | expression EGALEGAL expression
    | expression AND expression
    | expression OR expression
    | expression PLUS expression
    | expression TIMES expression
    | expression MINUS expression
    | expression DIVIDE expression
    | expression SUP expression''' 
    p[0] = (p[2],p[1],p[3])
    

def p_expression_group(p): 
    'expression : LPAREN expression RPAREN' 
    p[0] = p[2] 
    
def p_statement_increment(p):
    'statement : NAME PLUS PLUS'
    p[0] = ('incrementation', p[1])
    
def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = p[1]
 
def p_expression_number(p): 
    'expression : NUMBER' 
    p[0] = p[1] 
 
def p_expression_name(p): 
    'expression : NAME' 
    p[0] = p[1]
 
def p_error(p):    print("Syntax error in input!")
 
import ply.yacc as yacc
yacc.yacc()
# s = 'print(1+2);print(7*8+(4-4));a=8+8; print(a);b=8+8; print(a+b);'
# s = 'for(i = 0; i < 10; i++) { print(i); };'
s = 'i = 0; while(i < 5) { print(i); i++; };'
# s = 'a=0; a++; a++; a++; print(a);'
yacc.parse(s)

# -*- coding: utf-8 -*-
 
from genereTreeGraphviz2 import printTreeGraph
reserved={
        'print':'PRINT',
        'if':'IF',
        'else':'ELSE',
        'while':'WHILE', 
        'for':'FOR',
        'function' : 'FUNCTION'
       
        }
 
tokens = [ 'NUMBER','MINUS', 'PLUS','TIMES','DIVIDE', 'LPAREN',
          'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
          'EGALEGAL','INFEG', 'LBRACKET', 'RBRACKET']+ list(reserved.values())
 
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
#t_NAME = r'[a-zA-Z_][a-zA-Z_0-9]*'
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
 
t_ignore = " \t"
 
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
 
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
 
import ply.lex as lex
lex.lex()
 
names={} #tableau pour stocker les variables
fonctions={}#tableau pour stocker les fonctions 
precedence = ( 
        ('left','OR' ), 
        ('left','AND'), 
        ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'), 
        ('left','PLUS', 'MINUS' ), 
        ('left','TIMES', 'DIVIDE'), 
        )

def evalInst(p):
    if p== "empty":
        return
    if type(p)==tuple : 
        if p[0]=='print' : print('CALC>',evalExpr(p[1]))
        elif p[0]=='bloc' : 
            evalInst(p[1])
            evalInst(p[2])
        elif p[0]=='if':
            if(evalExpr(p[1]) == True): # Si la condition est vraie
                evalInst(p[2]) # Exécuter le bloc associé
        elif p[0] == 'if_else':
            if evalExpr(p[1]):  # Si la condition du if est vraie
                evalInst(p[2])  # Exécuter le bloc "then"
            else:
                evalInst(p[3])  # Sinon, exécuter le bloc "else"
        elif p[0]=='assign':
            names[p[1]] = evalExpr(p[2])
        elif p[0] == 'incrementation' :
            names[p[1]] += 1    
        elif p[0] == 'decrementation' :
            names[p[1]] -= 1    
        elif p[0] =='while':
            while evalExpr(p[1]):# tant que la condition (p[1]) est vrai dans le while
                evalInst(p[2])# executer le bloc
        elif p[0] == 'for' :
            evalInst(p[1])  # Initialisation
            while evalExpr(p[2]):  # Condition
                evalInst(p[4])  # Corps de la boucle
                evalInst(p[3])  # Incrémentation
        elif p[0] == 'function':
            fonctions[p[1]]=p[2] # Stocke dans le dictionnaire fonctions la fonction avec son nom comme clé et son bloc comme valeur
        elif p[0] =='function_call':# si c'est un apple à une fonction
            if p[1] in fonctions: #si la fonction est bien dans mon tableau
                evalInst(fonctions[p[1]]) #on evalue celle-ci avec evalInst
                print(f"la fonction`{p[1]}` existe ")
            else:
                raise ValueError(f"la fonction '{p[1]}' n'existe pas") #on leve une exception                

 
 


def evalExpr(t):
    if isinstance(t, int):  # Cas d'un entier
        return t
    if isinstance(t, str):  # Cas d'un nom (variable)
        if t == 'true': return True
        if t == 'false': return False
        if t in names:#si la variable existe dans mon tableau de variables
            return names[t] #je la return
        else:
            raise NameError(f"Variable '{t}' non définie")#on léve une exception    
        #return names.get(t, 0)  # Retourner 0 si le nom n'existe pas
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

def p_statement_function_void(p):
    'statement : FUNCTION NAME LPAREN RPAREN LBRACKET bloc RBRACKET '
    p[0] = ('function', p[2], p[6])        

def p_statement_function_call_void(p):
    'statement : NAME LPAREN RPAREN SEMI'
    p[0]= ('function_call', p[1])    
 
 
def p_statement_expr(p): 
    'statement : PRINT LPAREN expression RPAREN' 
    #print(p[3]) 
    p[0] = ('print',p[3] ) 

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACKET bloc RBRACKET '
    p[0] = ('while', p[3], p[6])    

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACKET bloc RBRACKET'
    p[0] = ('for', p[3], p[5], p[7], p[10])   

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN LBRACKET bloc RBRACKET'
    p[0] = ('if',p[3], p[6] )   

def p_statement_if_else(p):
    'statement : IF LPAREN expression RPAREN LBRACKET bloc RBRACKET ELSE LBRACKET bloc RBRACKET'
    p[0] = ('if_else', p[3], p[6], p[9]) 

 
def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])  # ('assign', variable, expression)

def p_expression_binop_inf(p): 
    """
    expression : expression INF expression
               | expression INFEG expression
               | expression EGALEGAL expression
               | expression AND expression
               | expression OR expression
               | expression PLUS expression
               | expression TIMES expression
               | expression MINUS expression
               | expression DIVIDE expression
               | expression SUP expression
    """
    p[0] = (p[2], p[1], p[3])

 
def p_expression_group(p): 
    'expression : LPAREN expression RPAREN' 
    p[0] = p[2] 

def p_statement_increment(p):
    'statement : NAME PLUS PLUS'
    p[0] = ('incrementation', p[1])

def p_statement_decrement(p):
    'statement : NAME MINUS MINUS'
    p[0] = ('decrementation', p[1])    
 
def p_expression_number(p): 
    'expression : NUMBER' 
    p[0] = p[1] 
 
def p_expression_name(p): 
    'expression : NAME' 
    p[0] =  p[1]

 
#pour l'emplacement des erreurs syntaxique
def p_error(p):
    if p:  # Vérifie si le token en erreur (p) existe.
        # Si un token est disponible et affiche le message d'erreur avec sa valeur et la ligne où il se trouve
        print(f"Erreur syntaxique à '{p.value}' (ligne {p.lineno})")
    else:
        # Si le token est None (en gros le prgm c art) cela signifie que l'erreur est probablement à la fin de l'entrée de l'input user
        print("Erreur syntaxique à la fin de l'entrée !")

    #print("Syntax error in input!")
 
import ply.yacc as yacc
yacc.yacc()
s = 'function test(){print(21 + 10);}; test();;'
#s = 'i = 0; while(i < 5) { print(i); i++; };'
yacc.parse(s)
 

# -*- coding: utf-8 -*-

from genereTreeGraphviz2 import printTreeGraph
from re import search

reserved = {
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "elif": "ELIF",
    "while": "WHILE",
    "for": "FOR",
    "function": "FUNCTION",
    "return": "RETURN",
}

tokens = [
    "NUMBER",
    "MINUS",
    "PLUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN",
    "OR",
    "AND",
    "SEMI",
    "EGAL",
    "NAME",
    "INF",
    "SUP",
    "EGALEGAL",
    "INFEG",
    "LBRACKET",
    "RBRACKET",
    "BOOLEAN",
    "COMMA",
    "RETURN",
] + list(reserved.values())

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_OR = r"\|"
t_AND = r"\&"
t_SEMI = r";"
t_EGAL = r"\="
t_INF = r"\<"
t_SUP = r">"
t_INFEG = r"\<\="
t_EGALEGAL = r"\=\="
t_LBRACKET = r"\{"
t_RBRACKET = r"\}"
t_COMMA = r","

stack = []


def t_NAME(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "NAME")  # Check for reserved words
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_BOOLEAN(t):
    r"true|false"
    if t.value == "true":
        t.value = True
    else:
        t.value = False
    return t


t_ignore = " \t"


def t_newline(t):
    r"\n+"
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def read_cobra_file(file_path: str) -> str:
    if search(r"\.cobra$", file_path) is None:
        raise ValueError("The file is not a .cobra file")

    with open(file_path, "r") as file:
        return file.read()


def add_bloc(left, right):
    while right != "empty":
        add_bloc(left[1], left[2])
        stack.append(right)
        return

    stack.append(left)


import ply.lex as lex

lex.lex()

names = {}
fonctions = {}
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "INF", "INFEG", "EGALEGAL", "SUP"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)


def evalInst(p):
    if p == "empty":
        return
    if type(p) == tuple:
        if p[0] == "print":
            print(evalExpr(p[1]))
        if p[0] == "bloc":
            # s=stack.size
            #add_bloc(p[1], p[2])
            # runandpop(s)
            evalInst(p[1])
            evalInst(p[2])
        if p[0] == "assign":
            names[p[1]] = evalExpr(p[2])
        if p[0] == "while":
            while evalExpr(p[1]):
                evalInst(p[2])
        if p[0] == "for":
            evalInst(p[1])  # Initialisation
            while evalExpr(p[2]):  # Condition
                evalInst(p[4])  # Corps de la boucle
                evalInst(p[3])  # Incrémentation
        if p[0] == "incrementation":
            names[p[1]] += 1
        if p[0] == "decrementation":
            names[p[1]] -= 1
        if p[0] == "if":
            if evalExpr(p[1]):
                evalInst(p[2])
            elif len(p) > 3:
                evalInst(p[3])
        if p[0] == "elif":
            if evalExpr(p[1]):
                evalInst(p[2])
            elif len(p) > 3:
                evalInst(p[3])
        if p[0] == "else":
            evalInst(p[1])
        elif p[0] == 'function_void':
            fonctions[p[1]]=p[2] # Stocke dans le dictionnaire fonctions la fonction avec son nom comme clé et son bloc comme valeur
        elif p[0] =='function_void_call':# si c'est un apple à une fonction
            if p[1] in fonctions: #si la fonction est bien dans mon tableau
                #je verifie qu'il n'attend pas d'agument
                param = fonctions[p[1]]
                if(param==0):
                    print("aucun param attendue")
                    evalInst(fonctions[p[1]]) #on evalue celle-ci avec evalInst
                    print(f"la fonction`{p[1]}` existe ")
                else:
                    print("cette fonction attend des arguments ")    
            else:
                raise ValueError(f"la fonction '{p[1]}' n'existe pas") #on leve une exception                
    
        elif p[0] == 'function_void_param':
            # Stocker la fonction avec son nom et ses paramètres dans ma lst de functions
            fonctions[p[1]] = (p[2], p[3])  # (nom de la func, (liste des paramètres, bloc))
        elif p[0] == 'function_void_param_call':#appelle de la func
            if p[1] in fonctions:
                params, bloc = fonctions[p[1]]

                # Associer les arguments aux paramètres
                for param, arg in zip(params, p[2]):#La fonction zip associe chaque elem de la lst params avec un elem correspondant dans p[2]
                    names[param] = evalExpr(arg)#Stocke ces associations dans la lst names ex : names = {'a': 5, 'b': 10}...
                evalInst(bloc)  # Exécuter le bloc de la fonction
            else:
                raise ValueError(f"la fonction  n'existe pas")

def evalExpr(t):
    if type(t) == int:
        return t
    if type(t) == str:
        if t == "true":
            return True
        if t == "false":
            return False
        if t in names:
            return names[t]
        return "pas trouve"
    if t[0] == "+":
        return evalExpr(t[1]) + evalExpr(t[2])
    if t[0] == "*":
        return evalExpr(t[1]) * evalExpr(t[2])
    if t[0] == "/":
        return evalExpr(t[1]) / evalExpr(t[2])
    if t[0] == "-":
        return evalExpr(t[1]) - evalExpr(t[2])
    if t[0] == "<":
        return evalExpr(t[1]) < evalExpr(t[2])
    if t[0] == "<=":
        return evalExpr(t[1]) <= evalExpr(t[2])
    if t[0] == ">":
        return evalExpr(t[1]) > evalExpr(t[2])
    if t[0] == ">=":
        return evalExpr(t[1]) >= evalExpr(t[2])
    if t[0] == "==":
        return evalExpr(t[1]) == evalExpr(t[2])
    if t[0] == "&":
        return evalExpr(t[1]) and evalExpr(t[2])
    if t[0] == "|":
        return evalExpr(t[1]) or evalExpr(t[2])


def p_start(p):
    "start : bloc"
    print(p[1])
    printTreeGraph(p[1])
    evalInst(p[1])


def p_bloc(p):
    """bloc : bloc statement SEMI
    | statement SEMI"""
    if len(p) == 3:
        p[0] = ("bloc", p[1], "empty")
    else:
        p[0] = ("bloc", p[1], p[2])


# def p_bloc_function(p):
#     """bloc_function: bloc_function statement SEMI
#     | RETURN expression SEMI"""
#     if p[1] == "return":
#         p[0] = ("bloc_function", p[1], p[2])
#     else:
#         p[0] = ("bloc_function", p[1], "empty")


def p_statement_function_void_param(p):
    'statement : FUNCTION NAME LPAREN param_list RPAREN LBRACKET bloc RBRACKET'
    p[0] = ('function_void_param', p[2], p[4], p[7])      

def p_statement_function_void_param_call(p):
    'statement : NAME LPAREN arg_list RPAREN '
    p[0] = ('function_void_param_call', p[1], p[3])      

def p_param_list(p):
    '''param_list : NAME COMMA param_list
                  | NAME
                  '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] != '' else []
    else:
        p[0] = [p[1]] + p[3]

def p_arg_list(p):
    '''arg_list : expression COMMA arg_list
                | expression
                '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] != '' else [] #if ternaire ici 
    else:
        p[0] = [p[1]] + p[3] 

def p_statement_function_void(p):
    'statement : FUNCTION NAME LPAREN RPAREN LBRACKET bloc RBRACKET '
    p[0] = ('function_void', p[2], p[6])        

def p_statement_function_call_void(p):
    'statement : NAME LPAREN RPAREN '
    p[0]= ('function_void_call', p[1])    
 


def p_statement_for(p):
    "statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACKET bloc RBRACKET"
    p[0] = ("for", p[3], p[5], p[7], p[10])


def p_statement_while(p):
    "statement : WHILE LPAREN expression RPAREN LBRACKET bloc RBRACKET"
    p[0] = ("while", p[3], p[6])


def p_statement_if(p):
    """statement : IF LPAREN expression RPAREN LBRACKET bloc RBRACKET
    | IF LPAREN expression RPAREN LBRACKET bloc RBRACKET elif_chain
    | IF LPAREN expression RPAREN LBRACKET bloc RBRACKET ELSE LBRACKET bloc RBRACKET"""
    if len(p) == 8:
        p[0] = ("if", p[3], p[6])
    elif len(p) == 9:
        p[0] = ("if", p[3], p[6], p[8])
    elif len(p) == 12:
        p[0] = ("if", p[3], p[6], ("else", p[10]))


def p_elif_chain(p):
    """elif_chain : ELIF LPAREN expression RPAREN LBRACKET bloc RBRACKET
    | ELIF LPAREN expression RPAREN LBRACKET bloc RBRACKET elif_chain
    | ELIF LPAREN expression RPAREN LBRACKET bloc RBRACKET ELSE LBRACKET bloc RBRACKET
    """
    if len(p) == 8:
        p[0] = ("elif", p[3], p[6])
    elif len(p) == 9:
        p[0] = ("elif", p[3], p[6], p[8])
    elif len(p) == 12:
        p[0] = ("elif", p[3], p[6], ("else", p[10]))


def p_statement_expr(p):
    "statement : PRINT LPAREN expression RPAREN"
    p[0] = ("print", p[3])


def p_statement_assign(p):
    "statement : NAME EGAL expression"
    p[0] = ("assign", p[1], p[3])


def p_expression_binop_inf(p):
    """expression : expression INF expression
    | expression INFEG expression
    | expression EGALEGAL expression
    | expression AND expression
    | expression OR expression
    | expression PLUS expression
    | expression TIMES expression
    | expression MINUS expression
    | expression DIVIDE expression
    | expression SUP expression"""
    p[0] = (p[2], p[1], p[3])


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_statement_increment(p):
    "statement : NAME PLUS PLUS"
    p[0] = ("incrementation", p[1])


def p_statement_decrement(p):
    "statement : NAME MINUS MINUS"
    p[0] = ("decrementation", p[1])


def p_expression_boolean(p):
    "expression : BOOLEAN"
    p[0] = p[1]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
    p[0] = p[1]


def p_error(p):
    if p:  # Vérifie si le token en erreur (p) existe.
        # Si un token est disponible et affiche le message d'erreur avec sa valeur et la ligne où il se trouve
        print(f"Erreur syntaxique à '{p.value}' (ligne {p.lineno})")
    else:
        # Si le token est None (en gros le prgm c art) cela signifie que l'erreur est probablement à la fin de l'entrée de l'input user
        print("Erreur syntaxique à la fin de l'entrée !")


import ply.yacc as yacc

yacc.yacc()
# s = 'print(1+2);print(7*8+(4-4));a=8+8; print(a);b=8+8; print(a+b);'
# s = 'for(i = 0; i < 10; i++) { print(i); };'
# s = 'a = 2; print(a);'
# s = "a = 0; if(a == 0) { print(a); } else { print(5+5); };"
# s = "else { print(5+5); };"
#s = "a = 0; if(a == 2) { print(a); } elif(a == 1) { print(5+5); } elif(a ==5 ) { print(5*5); } else { print(5+5*2); };"
# s = 'i = 0; while(i < 5) { print(i); i++; };'
# s = 'a=0; a++; a++; a++; print(a);'
s = "function test(a, b){print(a + b);}; test();"
#s = "function test(a, b){print(a + b);}; test(5, 5);"
#s = read_cobra_file("main.cobra")
# s = "function test(a, b){print(a + b);}; test(21, 9);"
# s = "function test(a, b){print(a + b);}; test(5, 5);"
# s = "if (1 == 1) { print(1); };"
# s = "print(1); print(2); print(3);"
yacc.parse(s)

#print(stack)

[
    ("assign", "a", 0),
    (
        "if",
        ("==", "a", 2),
        ("bloc", ("print", "a"), "empty"),
        (
            "elif",
            ("==", "a", 1),
            ("bloc", ("print", ("+", 5, 5)), "empty"),
            (
                "elif",
                ("==", "a", 5),
                ("bloc", ("print", ("*", 5, 5)), "empty"),
                ("else", ("bloc", ("print", ("+", 5, ("*", 5, 2))), "empty")),
            ),
        ),
    ),
]

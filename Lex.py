import sys
import ply.lex as lex

reserved = {
    # Palabras reservadas
    "begin" : "TkBegin",
    "with" : "TkWith",
    "end" : "TkEnd",
    "if" : "TkIf",
    "otherwise" : "TkOtherwise",
    "while" : "TkWhile",
    "for" : "TkFor",
    "from" : "TkFrom",
    "to" : "TkTo",
    "step" : "TkStep",
    "read" : "TkRead",
    "print" : "TkPrint",
    "var" : "TkVar",
    "int" : "TkInt",
    "bool": "TkBool",
    "char" : "TkChar",
    "array" : "TkArray",
    "of" : "TkOf",
    # Agregadas por conveniencia
    "not" : "TkNegacion",
    "true" : "TkTrue",
    "false" : "TkFalse"
    }

tokens = list(reserved.values())+[
    # Para las palabras reservadas
    "TkReservada",
    # Identificadores de variables
    "TkId",
    # Literales numericos
    "TkNum",
    # Literales para caracteres
    "TkCaracter",
    # Separadores
    "TkComa",
    "TkPunto",
    "TkDosPuntos",
    "TkPuntoYComa",
    "TkParAbre",
    "TkParCierra",
    "TkCorcheteAbre",
    "TkCorcheteCierra",
    "TkHacer",
    "TkAsignacion",
    # Operadores
    "TkSuma",
    "TkResta",
    "TkMult",
    "TkDiv",
    "TkMod",
    "TkConjuncion",
    "TkDisyuncion",
    "TkDesigual",
    "TkMenor",
    "TkMenorIgual",
    "TkMayor",
    "TkMayorIgual",
    "TkIgual",
    "TkSiguienteCar",
    "TkAnteriorCar",
    "TkValorAscii",
    "TkConcatenacion",
    "TkShift",
    ]

# Recibe un lexer y token y devuelve el numero de columna
def columna(l,t):
    inicio_linea = l.string.rfind('\n', 0, t.lexpos)+1
    return (t.lexpos-inicio_linea)+1

# Para contar el numero de linea
def t_saltolinea(t) :
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.hay_salto = True
    return

def t_eof(t):
    return

# Ignoramos espacios y tabs
t_ignore  = ' \t'

# Manejo de errores
def t_error(t):
    t.lexer.hay_error = True
    print('Error: Caracter inesperado "'+t.value[0]+'" en la fila '+str(t.lexer.lineno))
    t.lexer.skip(1)

def t_TkReservada(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,"TkId")
    return t

# Literales numericos
def t_TkNum(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Literal para caracteres
t_TkCaracter = r"'\\['nt\\]'|'.'"

# Separadores
t_TkComa = r','
t_TkPunto = r'\.'
t_TkDosPuntos = r':'
t_TkPuntoYComa = r';'
t_TkParAbre = r'\('
t_TkParCierra = r'\)'
t_TkCorcheteAbre = r'\['
t_TkCorcheteCierra = r'\]'
t_TkHacer = r'->'
t_TkAsignacion = r'<-'

# Operadores
t_TkSuma = r'\+'
t_TkResta = r'-'
t_TkMult = r'\*'
t_TkDiv = r'/'
t_TkMod = r'%'
t_TkConjuncion = r'/\\'
t_TkDisyuncion = r'\\/'
t_TkMenor = r'<'
t_TkMenorIgual = r'<='
t_TkMayor = r'>'
t_TkMayorIgual = r'>='
t_TkDesigual = r'/='
t_TkIgual = r'='
t_TkSiguienteCar = r'\+\+'
t_TkAnteriorCar = r'--'
t_TkValorAscii = r'\#'
t_TkConcatenacion = r'::'
t_TkShift = r'\$'

# Se crea el lexer
lexer = lex.lex()

# Recibe un lexer y un token y retorna la información del token
# con el formato de string deseado en lugar de el de su metodo __str__
def str_token(l,t) :
    salida = t.type
    if t.type in ["TkId","TkNum","TkCaracter"] :
        valor = str(t.value)
        if t.type == "TkId" :
            valor = '"'+valor+'"'
        salida += "("+valor+")"
    salida += " "+str(t.lineno)+" "+str(columna(l,t))
    # Asumimos que el último caracter siempre es EOF
    if l.lexpos != l.lexlen-1 :
        salida += ", "
    return salida

def main() :
    # Lectura del archivo
    f = open(sys.argv[1])
    s = f.read()
    f.close()
    # Agregamos la string como atributo al lexer para
    # evitar usar variables globales
    lexer.string = s
    lexer.input(lexer.string)
    # Agregamos un booleano como atributo al lexer
    # para indicar si se ha encontrado un error
    lexer.hay_error = False
    # Igual para saltos de linea
    lexer.hay_salto = False
    
    imprimir = ""
    while True:
        tok = lexer.token()
        if not tok: 
            break
        if lexer.hay_salto :
            imprimir += "\n"
            lexer.hay_salto = False
        if not(lexer.hay_error) :
            imprimir += str_token(lexer,tok)
    
    if not(lexer.hay_error) :
        print(imprimir)

if __name__ == "__main__" :
    main()

import ply.yacc as yacc
import sys
from Lex import tokens

def p_bloque(p) :
        '''
	bloque : with TkBegin instruccion TkEnd
                | TkBegin instruccion TkEnd
        '''
        crear_nodo(p)

def p_instruccion(p) :
        '''
        instruccion : instruccion instruccion
                | bloque
                | asignacion
                | loop
                | condicional
                | TkPrint expresion TkPuntoYComa
                | TkRead variable TkPuntoYComa
        '''
        crear_nodo(p)
        if p[1] == "print" :
            p[0].ins = True
            p[0].codigo = "print("+p[2].codigo+")"
            p[0].asr = True
            p[0].asercion = "if "+p[2].codigo+" is None : raise NoInicializada()"
        if p[1] == "read" :
            if p[2].tipo == "variable" :
                #p[0].variables[p[2].nombre_var] = "char"
                p[0].variables[p[2].nombre_var] = p[2].nombre_var

def p_asignacion(p): 
    '''
    asignacion : variable TkAsignacion expresion TkPuntoYComa
                | variable TkPunto exp_num TkPuntoYComa
                | variable TkPunto variable TkPuntoYComa
    '''
    crear_nodo(p)
    p[0].ins = True
    if p[2] == '<-' :
            p[0].codigo = str(p[1].codigo)+"="+str(p[3].codigo)
            if p[3].tipo == "expresion" :
                    p[0].variables[p[1].nombre_var] = p[3].tipo_var
            elif p[3].tipo == "variable" :
                    p[0].variables[p[1].nombre_var] = p[3].tipo_var
                    p[0].asr = True
                    p[0].asercion = "if "+p[3].codigo+" is None : raise NoInicializada()"
    else :
        p[0].variables[p[1].nombre_var] = "int"
        if p[3].tipo == "variable" :
            p[0].variables[p[3].nombre_var] = "int"
        p[0].codigo = str(p[1].codigo)+"-="+str(p[3].codigo)

def p_acc_array(p) :
    '''
    acc_array : TkId TkCorcheteAbre exp_num TkCorcheteCierra
                | TkId TkCorcheteAbre variable TkCorcheteCierra
                | acc_array TkCorcheteAbre exp_num TkCorcheteCierra
                | acc_array TkCorcheteAbre variable TkCorcheteCierra
    '''
    crear_nodo(p)
    if type(p[1]) is Nodo :
            p[0].nombre_var = p[1].nombre_var+"*"
            p[0].tipo_var = p[1].tipo_var+"*"
            if p[3].tipo == "variable" :
                p[0].variables[p[3].nombre_var] = "int"
            p[0].id_var = p[1].id_var
            p[0].codigo_array = p[1].codigo_array+"["+p[3].codigo+"]"
            p[0].codigo = "self.bloque.variables['"+p[1].id_var+"']"+p[0].codigo_array
    elif type(p[1]) is str :
            p[0].nombre_var = p[1]+"*"
            p[0].tipo_var = p[1]+"*"
            p[0].codigo = "self.bloque.variables['"+p[1]+"']["+p[3].codigo+"]"
            p[0].codigo_array = "["+p[3].codigo+"]"
            p[0].id_var = p[1]
    p[0].asr = True
    p[0].asercion = "if "+p[3].codigo+"<0 : raise IndiceNegativo()"
    for i in range(1,len(p)) :
        if type(p[i]) is Nodo :
            if p[i].tipo == "variable" :
                p[0].asr = True
                p[0].asercion += "\nif "+p[i].codigo+" is None : raise NoInicializada()"

def p_loop(p):
    '''
        loop : loopFor
             | loopWhile
    '''
    crear_nodo(p)
    
def p_loopFor(p):
    '''
        loopFor : TkFor TkId TkFrom exp_num TkTo exp_num TkHacer instruccion TkEnd
                | TkFor TkId TkFrom exp_num TkTo variable TkHacer instruccion TkEnd
                | TkFor TkId TkFrom variable TkTo exp_num TkHacer instruccion TkEnd
                | TkFor TkId TkFrom variable TkTo variable TkHacer instruccion TkEnd
                | TkFor TkId TkFrom exp_num TkTo exp_num step TkHacer instruccion TkEnd
                | TkFor TkId TkFrom exp_num TkTo variable step TkHacer instruccion TkEnd
                | TkFor TkId TkFrom variable TkTo exp_num step TkHacer instruccion TkEnd
                | TkFor TkId TkFrom variable TkTo variable step TkHacer instruccion TkEnd
    '''
    crear_nodo(p)

    p[0].variables[p[2]] = "int"
    p[0].variables_for.append(p[2])
    p[0].asercion = ""
    for i in range(1,len(p)) :
        if type(p[i]) is Nodo :
                if p[i].tipo == "variable" :
                        p[0].variables[p[i].nombre_var] = "int"
                        p[0].asr = True
                        p[0].asercion += "\nif "+p[i].codigo+" is None : raise NoInicializada()"

def p_step(p) :
    '''
    step : TkStep exp_num
        | TkStep variable
    '''
    crear_nodo(p)
    p[0].codigo = p[2].codigo
    if p[2].tipo == "variable" :
        p[0].variables[p[2].nombre_var] = "int"
        p[0].asr = True
        p[0].asercion = "if "+p[2].codigo+" is None : raise NoInicializada()"
    
def p_loopWhile(p):
    '''
        loopWhile : TkWhile exp_bool TkHacer instruccion TkEnd
                | TkWhile variable TkHacer instruccion TkEnd
    '''
    crear_nodo(p)
    if type(p[2]) is Nodo :
        if p[2].tipo == "variable" :
                p[0].variables[p[2].nombre_var] = "bool"
                p[0].asr = True
                p[0].asercion = "if "+p[2].codigo+" is None : raise NoInicializada()"

def p_condicional(p) :
        '''
        condicional : TkIf exp_bool TkHacer instruccion TkEnd
                | TkIf variable TkHacer instruccion TkEnd
                | TkIf exp_bool TkHacer instruccion TkOtherwise TkHacer instruccion TkEnd
                | TkIf variable TkHacer instruccion TkOtherwise TkHacer instruccion TkEnd
        '''
        crear_nodo(p)
        if type(p[2]) is Nodo :
                if p[2].tipo == "variable" :
                        p[0].variables[p[2].nombre_var] = "bool"
                        p[0].asr = True
                        p[0].asercion = "if "+p[2].codigo+" is None : raise NoInicializada()"

def p_comparador(p):
        '''
        comparador : TkMenorIgual
                    | TkMayorIgual
                    | TkMenor
                    | TkMayor
        '''
        crear_nodo(p)
        p[0].codigo = p[1]

def p_with(p) :
        'with : TkWith declaracion'
        crear_nodo(p)

def p_declaracion(p) :
        '''
        declaracion : TkVar id TkDosPuntos tipo
               | declaracion declaracion
        '''
        crear_nodo(p)
        if len(p) == 5 :
                x = p[2]
                p[0].codigo = ""
                while type(x) is Nodo :
                        p[0].variables[x.nombre_var] = p[4].tipo_var
                        p[0].ins = True
                        p[0].codigo += "self.bloque.variables['"+x.nombre_var+"']="+p[4].codigo
                        p[0].variables_propias.append(x.nombre_var)
                        hijos = x.hijos
                        x = None
                        for y in hijos :
                                if y.tipo == "id" :
                                        x = y
                                        p[0].codigo += "\n"
                                        break
                        

# uno o mas identificadores separados por coma con o sin asginacion
def p_id(p) :
        '''
        id : TkId
            | TkId TkAsignacion expresion
            | TkId TkComa id
            | TkId TkAsignacion expresion TkComa id
        '''
        crear_nodo(p)
        p[0].nombre_var = p[1]
        if len(p) > 3 :
                if p[3].tipo == "expresion" :
                        p[0].variables[p[1]] = p[3].tipo_var
                        p[0].ins = True
                        p[0].codigo = "self.bloque.variables['"+p[1]+"']="+p[3].codigo

def p_variable(p) :
    '''
    variable : TkId
        | TkParAbre variable TkParCierra
        | acc_array
    '''
    crear_nodo(p)
    if type(p[1]) is Nodo :
            if p[1].tipo == "acc_array" :
                    p[0].nombre_var = p[1].nombre_var
                    p[0].tipo_var = p[1].tipo_var
                    p[0].codigo = p[1].codigo
                    p[0].id_var =p[1].id_var
                    p[0].cola =p[1].codigo_array
    elif p[1] == "(" :
            p[0].nombre_var = p[2].nombre_var
            p[0].tipo_var = p[2].tipo_var
            p[0].codigo = p[2].codigo
    else :
            p[0].nombre_var = p[1]
            p[0].tipo_var = p[1]
            p[0].codigo = p[1]
            p[0].codigo = "self.bloque.variables['"+p[0].codigo+"']"

def p_expresion(p) :
        '''
        expresion : exp_num
               | exp_bool
               | variable
               | exp_char
               | exp_array
        '''
        crear_nodo(p)
        p[0].tipo_var = "idk"
        if type(p[1]) is Nodo :
                p[0].codigo = p[1].codigo
                if p[1].tipo == "exp_num" :
                        p[0].tipo_var = "int"
                elif p[1].tipo == "exp_bool" :
                        p[0].tipo_var = "bool"
                elif p[1].tipo == "exp_char" :
                        p[0].tipo_var = "char"
                elif p[1].tipo == "exp_array" :
                        p[0].tipo_var = p[1].tipo_var
                elif p[1].tipo == "variable" :
                        p[0].tipo_var = p[1].tipo_var
                        p[0].tipo_var = p[1].nombre_var
                        p[0].variables[p[1].nombre_var] = p[1].tipo_var
                        p[0].asr = True
                        p[0].asercion = "if "+p[1].codigo+" is None : raise NoInicializada()"

def p_exp_array(p) :
    """
    exp_array : variable TkConcatenacion variable
            | exp_array TkConcatenacion variable
            | variable TkConcatenacion exp_array
            | exp_array TkConcatenacion exp_array
            | TkShift variable
            | TkShift exp_array
            | TkParAbre exp_array TkParCierra
    """
    crear_nodo(p)
    if p[2] == "::" :
        p[0].concat = True
        p[0].tipo_var = p[1].tipo_var
        p[0].variables[p[1].nombre_var] = p[3].tipo_var
        p[0].variables[p[3].nombre_var] = p[1].tipo_var
        p[0].codigo = p[1].codigo+"+"+p[3].codigo
    if p[1] == "$" :
        try :
            p[0].concat = True
            p[0].nombre_var = p[2].nombre_var
            p[0].tipo_var = p[2].tipo_var
            p[0].variables[p[2].id_var] = p[2].id_var
            p[0].codigo = "shift(self.bloque.variables[\""+p[2].id_var+"\"])"+p[2].cola
            print("shift(self.bloque.variables[\""+p[2].id_var+"\"])"+p[2].cola)
        except :
            p[0].concat = True
            p[0].nombre_var = p[2].nombre_var
            p[0].tipo_var = p[2].tipo_var
            p[0].variables[p[2].nombre_var] = p[2].tipo_var
            p[0].codigo = "shift("+p[2].codigo+")"
    if p[1] == "(" :
        p[0].codigo = p[2].codigo
    p[0].asercion = ""
    for i in range(1,len(p)) :
        if type(p[i]) is Nodo :
            if p[i].tipo == "variable" :
                p[0].asr = True
                p[0].asercion += "\nif "+p[i].codigo+" is None : raise NoInicializada()"

def p_exp_char(p) :
    """
    exp_char :  TkCaracter
               | TkCaracter TkAnteriorCar
               | variable TkAnteriorCar
               | TkCaracter TkSiguienteCar
               | variable TkSiguienteCar
               | TkParAbre exp_char TkParCierra
    """
    crear_nodo(p)
    if len(p) == 2 :
        p[0].codigo = p[1]
    elif p[2] == "++" :
        if type(p[1]) is Nodo :
            p[0].variables[p[1].nombre_var] = "char"
            p[0].asr = True
            p[0].asercion += "\nif "+p[1].codigo+" is None : raise NoInicializada()"
            p[0].codigo = "chr(ord("+p[1].codigo+")+1)"
        else :
            p[0].codigo = "chr(ord("+p[1]+")+1)"
    elif p[2] == "--" :
        if type(p[1]) is Nodo :
            p[0].variables[p[1].nombre_var] = "char"
            p[0].asr = True
            p[0].asercion += "\nif "+p[1].codigo+" is None : raise NoInicializada()"
            p[0].codigo = "chr(ord("+p[1].codigo+")-1)"
        else :
            p[0].codigo = "chr(ord("+p[1]+")-1)"
    elif p[1] == "(" :
        p[0].codigo = p[2].codigo

def p_exp_num(p) :
        '''
        exp_num : exp_num operador exp_num
                | variable operador variable
                | exp_num operador variable
                | variable operador exp_num
                | TkValorAscii exp_char
                | TkValorAscii variable
                | TkResta exp_num
                | TkResta variable
                | TkNum
                | TkParAbre exp_num TkParCierra
        '''

        crear_nodo(p)
        p[0].tipo_var = "int"
        p[0].asercion = ""
        for i in range(1,len(p)) :
                if type(p[i]) is Nodo :
                        if p[i].tipo == "variable" :
                                p[0].asr = True
                                p[0].asercion += "\nif "+p[i].codigo+" is None : raise NoInicializada()"
                                if p[i-1] == "#" :
                                    continue
                                p[0].variables[p[i].nombre_var] = "int"

        if len(p) > 3 :
            if type(p[2]) is Nodo :
                if p[2].tipo == "operador" :
                    p[0].codigo = p[1].codigo+p[2].codigo+p[3].codigo
        elif p[1] == "-" :
            p[0].codigo = "-"+p[2].codigo
        elif p[1] == "#" :
            p[0].codigo = "ord("+p[2].codigo+")"
        else :
            p[0].codigo = str(p[1])
        if p[1] == "(" :
            p[0].codigo = "("+p[2].codigo+")"

"""
def p_literal(p) :
        '''
            literal : TkNum
            | literal_bool
            | TkCaracter
        '''
        crear_nodo(p)
        if type(p[1]) is Nodo :
            p[0].tipo_var = p[1].tipo_var
            p[0].codigo = p[1].codigo
        elif type(p[1]) is int :
            p[0].tipo_var = 'int'
            p[0].codigo = str(p[1])
        elif type(p[1]) is str :
            p[0].tipo_var = 'char'
            p[0].codigo = p[1]
"""

def p_literal_bool(p) :
        '''
        literal_bool : TkTrue
               | TkFalse
        '''
        crear_nodo(p)
        p[0].tipo_var = 'bool'
        if p[1] == "true" :
            p[0].codigo = "True"
        else :
            p[0].codigo = "False"

def p_exp_bool(p) :
        '''
        exp_bool : literal_bool
                | exp_bool operador_bool exp_bool
                | variable operador_bool variable
                | exp_bool operador_bool variable
                | variable operador_bool exp_bool
                | exp_num comparador exp_num
                | variable comparador exp_num
                | exp_num comparador variable
                | variable comparador variable
                | exp_bool TkIgual exp_bool
                | TkNegacion exp_bool
                | TkNegacion variable
                | TkParAbre exp_bool TkParCierra
                | comparacion
        '''
        crear_nodo(p)
        p[0].tipo_var = "bool"
        if len(p) > 2 :
                if type(p[2]) is Nodo :
                        if p[2].tipo == "comparador" or p[2].tipo == "operador_bool" :
                                if p[1].tipo == "variable"  :
                                        p[0].variables[p[1].nombre_var] = p[3].tipo_var
                                if p[3].tipo == "variable"  :
                                        p[0].variables[p[3].nombre_var] = p[1].tipo_var
                                p[0].codigo = p[1].codigo+p[2].codigo+p[3].codigo
        if type(p[1]) is Nodo :
            if p[1].tipo == "comparacion" or p[1].tipo == "literal_bool" :
                p[0].codigo = p[1].codigo
        elif p[1] == "(" :
            p[0].codigo = p[2].codigo
        p[0].asercion = ""
        for i in range(1,len(p)) :
            if type(p[i]) is Nodo :
                if p[i].tipo == "variable" :
                    p[0].asr = True
                    p[0].asercion += "\nif "+p[i].codigo+" is None : raise NoInicializada()"

def p_comparador_univ(p) :
    """
    comparador_univ : TkIgual
                    | TkDesigual
    """
    crear_nodo(p)
    if p[1] == "/=" :
        p[0].codigo = "!="
    else :
        p[0].codigo = "=="

def p_comparacion(p) :
    """
    comparacion : variable comparador_univ variable
                | variable comparador_univ exp_num
                | variable comparador_univ exp_bool
                | variable comparador_univ exp_char
                | variable comparador_univ exp_array
                | exp_num comparador_univ variable
                | exp_bool comparador_univ variable
                | exp_char comparador_univ variable
                | exp_array comparador_univ variable
                | exp_num comparador_univ exp_num
                | exp_bool comparador_univ exp_bool
                | exp_char comparador_univ exp_char
                | exp_array comparador_univ exp_array
    """
    crear_nodo(p)
    if p[2].tipo == "comparador_univ" :
            if p[1].tipo == "variable"  :
                    p[0].variables[p[1].nombre_var] = p[3].tipo_var
            if p[3].tipo == "variable"  :
                    p[0].variables[p[3].nombre_var] = p[1].tipo_var
            p[0].codigo = p[1].codigo+p[2].codigo+p[3].codigo
    p[0].asercion = ""
    for i in range(1,len(p)) :
        if type(p[i]) is Nodo :
            if p[i].tipo == "variable" :
                p[0].asr = True
                p[0].asercion += "\nif "+p[i].codigo+" is None : raise NoInicializada()"


def p_operador_bool(p):
    '''
    operador_bool : TkDisyuncion
                  | TkConjuncion
    '''
    crear_nodo(p)
    if p[1] == "\\/" :
        p[0].codigo = " or "
    else :
        p[0].codigo = " and "


def p_tipo(p) :
        '''
       tipo : TkBool
              | TkInt
              | TkChar
              | array
       '''
        crear_nodo(p)
        if type(p[1]) is str :
                p[0].tipo_var = p[1]
                """
                if p[1] == "bool" :
                    p[0].codigo = "True"
                elif p[1] == "int" :
                    p[0].codigo = "0"
                elif p[1] == "char" :
                    p[0].codigo = "'a'"
                """
                p[0].codigo = "None"
        else :
                p[0].tipo_var = p[1].tipo_var
                p[0].codigo = p[1].codigo
 
def p_array(p) :
        '''
        array : TkArray TkCorcheteAbre exp_num TkCorcheteCierra TkOf tipo
                | TkArray TkCorcheteAbre variable TkCorcheteCierra TkOf tipo
        '''
        crear_nodo(p)
        if p[3].tipo == "variable" :
            p[0].variables[p[3].nombre_var] = "int"
            p[0].asr = True
        p[0].tipo_var = "array of "+p[6].tipo_var
        p[0].codigo = "["+p[6].codigo+" for i in range("+p[3].codigo+")]"
        p[0].asr = True
        p[0].asercion = "if "+p[3].codigo+"is None : raise NoInicializada()"
        p[0].asercion += "\nif "+p[3].codigo+"<= 0 : raise TamanoArreglo()"

def p_operador(p):
    '''
        operador : TkMult
                | TkSuma
                | TkDiv
                | TkResta
                | TkMod
    '''
    crear_nodo(p)
    if p[1] == "/" :
        p[0].codigo = "//"
    else :
        p[0].codigo = p[1]

# Mensaje de error
def p_error(p):
    try :
        print("Error de sintaxis en la linea "+str(p.lineno))
    except :
        print("Error de sintaxis")
    sys.exit()

precedence = (

 ('left', 'TkSuma', 'TkResta'),
 ('left', 'TkMult', 'TkDiv','TkMod'),
 ('left', 'TkDisyuncion'),
 ('left', 'TkConjuncion'),
 ('right', 'TkNegacion'),
 ('left','TkSiguienteCar'),
 ('left', 'TkAnteriorCar'), 
 ('right', 'TkValorAscii'),
 ('left','TkConcatenacion'),
 ('right','TkShift'),
 ('left', 'TkCorcheteAbre', 'TkCorcheteCierra'),
 ('nonassoc', 'TkMenor', 'TkMenorIgual','TkMayor','TkMayorIgual','TkIgual','TkDesigual'),
 ('left', 'TkParAbre','TkParCierra'),
 ('left', 'TkHacer')

)

class IndiceNegativo(Exception) :
    pass
class NoInicializada(Exception) :
    pass
class ErrorLectura(Exception) :
    pass
class ErrorFor(Exception) :
    pass
class TamanoArreglo(Exception) :
    pass

class Nodo:
    def __init__(self,tipo,hijos=None,hojas=None):
         # tipo de la produccion
         self.tipo = tipo
         # numero de linea
         self.linea = None
         # nombre de la variable del nodo (de haberloa
         self.nombre_var = None
         # tipo de dato que guarda (de haberlo)
         self.tipo_var = None
         # bloque que lo contiene
         self.bloque = None
         # tabla de simbolos
         self.variables = {}
         # atributo que indica si es una concatenacion
         self.concat = False
         # lista de simbolos declarados en un bloque for
         # no deben ser modificados
         self.variables_for = []
         # variables declaradas en el bloque
         self.variables_propias = []
         # equivalente en codigo python
         self.codigo = "None"
         # indica que es una instruccion completa para ejecutarse
         self.ins = False
         # similar a codigo e ins pero la instruccion es una asercion
         self.asercion = "None"
         self.asr = False
         # hijos (no terminales)
         if hijos:
              self.hijos = hijos
         else:
              self.hijos = []
        # hojas (terminales)
         if hojas :
              self.hojas = hojas
         else :
              self.hojas = []
              
    # recorre el arbol a partir del nodo dado y le asigna a cada nodo
    # una referencia a su bloque correspondiente
    def set_bloques(self, bloque=None) :
        self.bloque = bloque
        for hijo in self.hijos :
            if hijo :
                # solo los nodos de tipo bloque o for se consideran bloque
                # y sus hijos pasan a referenciarlos
                if self.tipo == "bloque" or  self.tipo == "loopFor" :
                    hijo.set_bloques(bloque=self)
                # de lo contrario el hijo hereda el bloque del padre
                else :
                    hijo.set_bloques(bloque=bloque)

    # recorre el arbol agregando a partir del nodo dado
    # agrega las variables faltantes a las tablas de simbolos anidadas
    def set_simbolos(self) :
        error = False
        # si es una declaracion, se completa la tabla de simbolos del
        # bloque correspondiente
        if self.tipo == "declaracion":
            for i in range(len(self.variables_propias)) :
                if self.variables_propias[i] in self.variables_propias[i+1:] :
                    print('Error: variable redeclarada: "'+self.variables_propias[i]+'" en la linea '+str(self.linea))
                    error = True
            #self.bloque.variables_propias += self.variables_propias
            # se itera sobre la tabla de simbolos
            for key,value in self.variables.items() :
                self.bloque.variables[key] = value
                if not key in self.bloque.variables_propias :
                    self.bloque.variables_propias.append(key)
                else :
                    print('Error: variable redeclarada: "'+key+'" en la linea '+str(self.linea))
                    error = True
                """
                if key in self.bloque.variables.keys() and not key in self.bloque.variables_propias :
                    print('Error: variable redeclarada: "'+key+'" en la linea '+str(self.linea))
                    error = True
                # si no, se agrega
                else :
                    self.bloque.variables[key] = value
                """
        # si el nodo es un bloque se agregan las variables declaradas en
        # bloques externos a su tabla de simbolos
        if self.tipo == "bloque" or self.tipo == "loopFor" :
            if not(self.bloque is None) :
                #self.variables.update(self.bloque.variables)
                for key, value in self.bloque.variables.items() :
                    if not(key in self.variables.keys()) :
                        self.variables[key] = value
                self.variables_for += self.bloque.variables_for
        # se llama recursivamente para cada hijo
        for hijo in self.hijos :
            if hijo :
                error = hijo.set_simbolos() or error
        return error

    def validar_semantica(self) :
        # primero se llaman estos metodos para poder trabajar
        self.set_bloques()
        error = self.set_simbolos()
        # se llama el metodo recursivo
        error = self.validar_semantica_r() or error
        return not error


    def validar_semantica_r(self) :
        error = False
        if self.tipo != "bloque" and  self.tipo != "loopFor" :
            for key,value in self.variables.items() :
                    # los asteriscos sibolizan el numero de accesos a un arreglo
                    count1  = key.count("*")
                    count2  = value.count("*")
                    key = key.replace("*","")
                    value = value.replace("*","")
                    if key in self.bloque.variables.keys() :
                        # manejando casos de acceso a arreglo
                        t1 = self.bloque.variables[key].replace("array of ","*")
                        c = t1.count("*")
                        # si hay mas accesos al arreglo de lo que soporta la variable
                        if count1 > c :
                                t1 = t1[c:]
                                t1 = t1.replace("*","array of ")
                                print('Error de tipo en la linea '+str(self.linea)+' en variable "'+key+'" : el tipo '+value+' no es un arreglo')
                                error = True
                        else :
                                t1 = t1[count1:]
                                t1 = t1.replace("*","array of ")
                        # caso especial
                        if self.concat :
                            if not 'array of ' in t1 :
                                print('Error: en la linea '+str(self.linea)+' la operacion solo admite arreglos, no '+str(t1))
                                error = True
                        # si value es un tipo de dato se procede normalmente
                        if value in ["int","char","bool"] or "array of" in value:
                                if value != t1 and self.tipo != "declaracion" and count1 <= c :
                                    print('Error de tipo en la linea '+str(self.linea)+' en variable "'+key+'" esperaba: '+t1+" se encontró: "+value)
                                    error = True
                        # si value es un identificador de otra variable se obtiene el tipo de esa variable
                        else :  
                                if value in self.bloque.variables.keys() and self.tipo != "declaracion":
                                    # manejando casos de acceso a arreglo
                                    t2 = self.bloque.variables[value].replace("array of ","*")
                                    c = t2.count("*")
                                    # si hay mas accesos al arreglo de lo que soporta la variable
                                    if count2 > c :
                                            t2 = t2[c:]
                                            t2 = t2.replace("*","array of ")
                                            print('Error de tipo en la linea '+str(self.linea)+' en variable "'+value+'" : el tipo '+t2+' no es un arreglo')
                                            error = True
                                    else :
                                            t2 = t2[count2:]
                                            t2 = t2.replace("*","array of ")
                                    if t2 != t1 :
                                            print('Error de tipo en la linea '+str(self.linea)+' en variable "'+key+'" esperaba: '+t1+" se encontró: "+t2)
                                            error = True
                                else :
                                    print('Error: variable no declarada "'+value+'" en la linea '+str(self.linea))
                                    error = True
                    else :
                        print('Error: variable no declarada "'+key+'" en la linea '+str(self.linea))
                        error = True
                    if key in self.bloque.variables_for and self.tipo == "asignacion" :
                            print('Error: en la linea '+str(self.linea)+' se intenta modificar la variable "'+key+'" la cual pertenece a una iteración')
                            error = True
        # se llama recursivamente
        for hijo in self.hijos :
            if hijo :
                error = hijo.validar_semantica_r() or error
        return error

    # recorre el arbol e imprime las tablas de simbolos de los bloques
    def imprimir_tabla(self) :
        if self.tipo == "bloque" or  self.tipo == "loopFor" :
                print(self.tipo)
                print(self.variables)
                #print(self.variables_propias)
                #print(self.variables_for)
        for hijo in self.hijos :
            if hijo :
                hijo.imprimir_tabla()

    # Copia la tabla de simbolos del bloque externo
    def obtener_simbolos(self) :
        if self.tipo == "bloque" or self.tipo == "loopFor" :
            if not(self.bloque is None) :
                for key, value in self.bloque.variables.items() :
                    self.variables[key] = value

    # Copia la tabla de simbolos a los bloque externo
    def recuperar_simbolos(self) :
        if self.tipo == "bloque" or self.tipo == "loopFor" :
            if not(self.bloque is None) :
                for key, value in self.variables.items() :
                    if not(key in self.variables_propias) :
                        self.bloque.variables[key] = value
                #self.bloque.recuperar_simbolos()

    # coloca en None todos los values de las tablas de simbolos de cada bloque
    # y respalda los tipos en el diccionario tipos
    def tabla_none(self) :
        if self.tipo == "bloque" or self.tipo == "loopFor" :
            self.tipos = self.variables
        self.variables = {}
        for hijo in self.hijos :
            if hijo :
                hijo.tabla_none()

    def ejecutar(self) :
        self.tabla_none()
        self.ejecutar_r()

    def ejecutar_r(self) :
        self.obtener_simbolos()

        try :
            if self.asr :
                #print(self.asercion)
                exec(self.asercion)
            if self.ins :
                #print(self.codigo)
                exec(self.codigo)
            if self.tipo == "instruccion" and len(self.hojas) > 0:
                if self.hojas[0] == "read" :
                    a = input()
                    count1 = self.hijos[0].nombre_var.count("*")
                    var = self.hijos[0].nombre_var.replace("*","")
                    count2 = self.bloque.tipos[var].count("array of ")
                    tipo = self.bloque.tipos[var].replace("array of ","")
                    if count1 != count2 :
                        raise ErrorLectura()
                    if tipo == "char" :
                        if len(a) != 1 :
                            raise ErrorLectura()
                        exec(self.hijos[0].codigo+"='"+a[0]+"'")
                    elif tipo == "int" :
                        try :
                            exec(self.hijos[0].codigo+"="+str(int(a)))
                        except ValueError :
                            raise ErrorLectura()
                        except IndexError :
                            raise IndexError()
                    elif tipo == "bool" :
                        if a == "true" :
                            exec(self.hijos[0].codigo+"=True")
                        elif a == "false" :
                            exec(self.hijos[0].codigo+"=False")
                        else :
                            raise ErrorLectura()
                    else :
                        raise ErrorLectura()

            if self.tipo == "condicional" :
                # obteniendo el valor de la guardia
                guardia = False
                locales = locals()
                exec("guardia = "+self.hijos[0].codigo,globals(),locales)
                guardia = locales['guardia']
                if guardia :
                    self.hijos[1].ejecutar()
                elif len(self.hijos) > 2 :
                    self.hijos[2].ejecutar_r()
                return
            elif self.tipo == "loopWhile" :
                while True :
                    # obteniendo el valor de la guardia
                    locales = locals()
                    exec("guardia = "+self.hijos[0].codigo,globals(),locales)
                    guardia = locales['guardia']
                    if not guardia :
                        return
                    self.hijos[1].ejecutar_r()
            elif self.tipo == "loopFor" :
                temp = self.bloque
                self.bloque = self
                # asignando el valor inicial
                exec("self.bloque.variables[self.hojas[1]]="+self.hijos[0].codigo)
                # obteniendo el valor final
                final = 0
                locales = locals()
                exec("final="+self.hijos[1].codigo,globals(),locales)
                final = locales['final']
                exec("inicio="+self.hijos[0].codigo,globals(),locales)
                inicio = locales['inicio']
                # obteniendo el step
                step = 1
                if len(self.hijos) == 4 :
                    exec("step="+self.hijos[2].codigo,globals(),locales)
                    step = locales['step']
                elif inicio <= final :
                    step = 1
                else :
                    step = -1

                if step == 0 :
                    raise ErrorFor()
                elif step > 0 :
                    if inicio > final :
                        raise ErrorFor()
                    signo = 1
                else :
                    if inicio < final :
                        raise ErrorFor()
                    signo = -1

                # iterando
                while self.bloque.variables[self.hojas[1]]*signo <= final*signo:
                    self.hijos[-1].ejecutar_r()
                    self.bloque.variables[self.hojas[1]] += step
                self.bloque = temp
            else :
                for hijo in self.hijos :
                    if hijo :
                        hijo.ejecutar_r()
        except IndiceNegativo :
            print("Error en la linea "+str(self.linea)+": el indice no puede ser negativo")
            sys.exit(1)
        except IndexError :
            print("Error en la linea "+str(self.linea)+": indice fuera de rango")
            sys.exit(1)
        except ZeroDivisionError :
            print("Error en la linea "+str(self.linea)+": division por 0")
            sys.exit(1)
        except NoInicializada :
            print("Error en la linea "+str(self.linea)+": variable no inicializada")
            sys.exit(1)
        except KeyError :
            print("Error en la linea "+str(self.linea)+": variable no inicializada")
            sys.exit(1)
        except TypeError :
            print("Error en la linea "+str(self.linea)+": variable no inicializada")
            sys.exit(1)
        except ErrorLectura :
            print("Error en la linea "+str(self.linea)+": error de lectura")
            sys.exit(1)
        except ErrorFor :
            print("Error en la linea "+str(self.linea)+": for interminable")
            sys.exit(1)
        except TamanoArreglo :
            print("Error en la linea "+str(self.linea)+": el tamaño del arreglo debe ser positivo")
            sys.exit(1)
        finally :
            pass
        self.recuperar_simbolos()


def crear_nodo(p) :
        hojas = []
        hijos = []
        for i in range(1,len(p)) :
            if type(p[i]) is str or type(p[i]) is int :
                    hojas.append(p[i])
            else :
                    hijos.append(p[i])
        p[0] = Nodo(p.slice[0].type,hijos,hojas)
        p[0].linea = p.lineno(0)

# Recibe un nodo n y un entero i que representa el nivel de identacion
# imprime el arbol sintactico recursivamente
def imprimir_arbol(nodo,i=0) :
        if nodo is None :
                return
        tab = "  "
        ident = i
        print(ident*tab+nodo.tipo.upper()+": ",end="")
        ident = i+1
        print(" ".join([str(hoja) for hoja in nodo.hojas]))
        for hijo in nodo.hijos :
                if hijo :
                        imprimir_arbol(hijo,i=ident)

def shift(L) :
    R = [None for i in range(len(L))]
    R[0] = L[-1]
    for i in range(1,len(L)) :
        R[i] = L[i-1]
    return R
    #return L[1:] + L[:1]


def main() :
        # Construyendo el parser
        yacc.yacc(errorlog=yacc.NullLogger())
        parser = yacc.yacc()
        f = open(sys.argv[1])
        s = f.read()
        f.close()
        result = parser.parse(s,tracking=True)
        #result.imprimir_tabla()
        if  result.validar_semantica() :
            #result.imprimir_tabla()
            imprimir_arbol(result)
            result.ejecutar()

if __name__ == "__main__" :
    main()

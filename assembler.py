from sly import Lexer, Parser
import json

# Cargar diccionarios de instrucciones
with open('BType.json') as f:
    BType = json.load(f)
with open('IType.json') as f:
    IType = json.load(f)
with open('JType.json') as f:
    JType = json.load(f)
with open('RType.json') as f:
    RType = json.load(f)
with open('SType.json') as f:
    SType = json.load(f)
with open('UType.json') as f:
    UType = json.load(f)
with open('REGnames.json') as f:
    REGnames = json.load(f)

DICCIONARIOS = set(BType) | set(IType) | set(JType) | set(RType) | set(SType) | set(UType)

class CalcLexer(Lexer):
    tokens = {"INSTRUCCION", "REGISTRO", "INMEDIATO"}

    literals = { ',' }
    ignore = ' \t'
    ignore_newline = r'\n+'


    @_(r'x[0-9]|x[12][0-9]|x3[01]|zero|ra|sp|gp|tp|fp|t[0-6]|s[0-9]|s1[01]|a[0-7]')
    def REGISTRO(self, t):
        try:
            if t.value.startswith('x'):
                t.value = int(t.value[1:]) #elimina la 'x' y deja el resto
            else:
                t.value = REGnames[t.value] #elimina la 'x' y deja el resto
        except ValueError:
            print("Error en registro")
            self.error(t) #si no se pudo cambiar a numero entonces no era un numero y se manda a la mierda
            return None
        return t

    @_(r'-?0x[0-9a-fA-F]+|-?[0-9]+')
    def INMEDIATO(self, t):
        try:
            if t.value.startswith('0x') or t.value.startswith('0X'):
                t.value = int(t.value, 16)#Si esta en hexadecimal 0x entones lo intenta convertir a int hexadecimal
            else:
                t.value = int(t.value)#si no simplemente lo cambia a un numero normal
        except ValueError:
            print("Error en inmediato")
            self.error(t)#si no se pudo cambiar a numero entonces no era un numero y se manda a la mierda
            return None
        return t

    @_(r'[a-zA-Z]+')
    def INSTRUCCION(self, t):
        t.value = t.value.lower() #Normaliza a minúsculas
        #Valida contra los diccionarios
        if t.value not in DICCIONARIOS:
            print("Error en instruccion")
            self.error(t)
            return None
        return t

    

    def error(self, t):
        print(f"Se ha encontrado un error de sintaxis--> '{t.value}' en la posición {self.index}")
        self.index += 1




data = "slli, "

lexer = CalcLexer()
for tok in lexer.tokenize(data):
    print(f"{tok.type}: {tok.value}")
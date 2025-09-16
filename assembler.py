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


class CalcLexer(Lexer):
    tokens = {INSTRUCCION, REGISTRO, NUMERO}
    ignore = ' \t'
    ignore_newline = r'\n+'

    INSTRUCCION = r'[a-zA-Z]+'
    REGISTRO = r'x[0-9]|x1[0-9]|x2[0-9]|x3[0-1]'

    def INSTRUCCION(self, t):
        self.t = t.lower()#pone en minusculas la instruccion

        # Verifica si la instrucción está en alguno de los diccionarios
        if (t.value not in BType) and (t.value not in IType) and 
           (t.value not in JType) and (t.value not in RType) and 
           (t.value not in SType) and (t.value not in UType):
            self.error(t)
            return None
        return t

    def error(self, t):
        print(f"Illegal instruction or character '{t.value}'")
        self.index += 1
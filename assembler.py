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

DICCIONARIOS = set(BType) | set(IType) | set(JType) | set(RType) | set(SType) | set(UType)

class CalcLexer(Lexer):
    tokens = {'INSTRUCCION', 'REGISTRO'}

    literals = { ',' }
    ignore = ' \t'
    ignore_newline = r'\n+'

    INSTRUCCION = r'[a-zA-Z]+'

    # Registros x0..x31
    REGISTRO = r'x(?:[0-9]|[12][0-9]|3[01])'

    def INSTRUCCION(self, t):
        t.value = t.value.lower() #Normaliza a minúsculas
        #Valida contra los diccionarios
        if t.value not in DICCIONARIOS:
            self.error(t)
            return None
        return t

    def error(self, t):
        print(f"Se ha encontrado un error de sintaxis: '{t.value}' en la posición {self.index}")
        self.index += 1

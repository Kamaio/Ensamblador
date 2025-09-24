from sly import Lexer, Parser
import json
import textwrap


def complementoA2(val, bits):
    if val < 0:
        val = (1 << bits) + val
    return format(val & ((1 << bits) - 1), f'0{bits}b')


def pseudo(line, original, labels):
    print(f"Linea entregada a pseudo: {line}")

    if  (line[0] == "nop"): return "addi x0, x0, 0"
    elif(line[0] == "mv"): return f"addi {line[1]} {line[2]}, 0"
    elif(line[0] == "not"): return f"xori {line[1]} {line[2]}, -1"
    elif(line[0] == "neg"): return f"sub {line[1]} x0, {line[2]}"
    elif(line[0] == "seqz"): return f"sltiu {line[1]} {line[2]}, 1"
    elif(line[0] == "snez"): return f"sltu {line[1]} x0, {line[2]}"
    elif(line[0] == "sltz"): return f"slt {line[1]} {line[2]}, x0"
    elif(line[0] == "sgtz"): return f"slt {line[1]} x0, {line[2]}"
    elif(line[0] == "beqz"): return f"beq {line[1]} x0, {line[2]}"
    elif(line[0] == "bnez"): return f"bne {line[1]} x0, {line[2]}"
    elif(line[0] == "blez"): return f"bge x0, {line[1]} {line[2]}"
    elif(line[0] == "bgez"): return f"bge {line[1]} x0, {line[2]}"
    elif(line[0] == "bltz"): return f"blt {line[1]} x0, {line[2]}"
    elif(line[0] == "bgtz"): return f"blt x0, {line[1]} {line[2]}"
    elif(line[0] == "bgt"): return f"blt {line[2]} {line[1]} {line[3]}"
    elif(line[0] == "ble"): return f"bge {line[2]} {line[1]} {line[3]}"
    elif(line[0] == "bgtu"): return f"bltu {line[2]} {line[1]} {line[3]}"
    elif(line[0] == "bleu"): return f"bgeu {line[2]} {line[1]} {line[3]}"
    elif(line[0] == "j"): return f"jal x0, {line[1]}"
    elif(line[0] == "jal" and line[1] in labels): return f"jal x1, {line[1]}"
    elif(line[0] == "jr"): return f"jalr x0, {line[1]}, 0"
    elif(line[0] == "jalr" and len(line) <= 2): return f"jalr x1, {line[1]}, 0"
    elif(line[0] == "ret"): return f"jalr x0, x1, 0"

    else: 
        print("SIGUIO NORMAL")
        return original


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
labels = {}
variables = {}
infoGuardada = []


class CalcLexer(Lexer):
    tokens = {"INSTRUCCION", "REGISTRO", "INMEDIATO", "COMA", "PARENTESIS1", "PARENTESIS2", }

    ignore = ' \t'
    ignore_newline = r'\n+'

    COMA  = r'\,'
    PARENTESIS1 = r'\('
    PARENTESIS2 = r'\)'


    @_(r'x3[01]|x[12][0-9]|x[0-9]|zero|ra|sp|gp|tp|fp|t[0-6]|s1[01]|s[0-9]|a[0-7]')
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
        if t.value not in DICCIONARIOS and t.value not in labels:
            print("Error en instruccion")
            self.error(t)
            return None
        return t


    def error(self, t):
        print(f"Se ha encontrado un error de sintaxis--> '{t.value}' en la posición {self.index}")
        self.index += 1


class ExprParser(Parser):
    tokens = CalcLexer.tokens

    @_('INSTRUCCION REGISTRO COMA REGISTRO COMA REGISTRO')
    def expr(self, p):
        if(p.INSTRUCCION in RType):
            return ("RType", p.INSTRUCCION, p.REGISTRO0, p.REGISTRO1, p.REGISTRO2)
        else: 
            raise SyntaxError(f"Instrucción R no reconocida: {p.INSTRUCCION}")

    @_('INSTRUCCION REGISTRO COMA REGISTRO COMA INMEDIATO')
    def expr(self, p):
        if(p.INSTRUCCION in IType):
            return ("IType", p.INSTRUCCION, p.REGISTRO0, p.REGISTRO1, p.INMEDIATO)
        else: 
            raise SyntaxError(f"Instrucción I no reconocida: {p.INSTRUCCION}")

    @_('INSTRUCCION REGISTRO COMA INMEDIATO PARENTESIS1 REGISTRO PARENTESIS2')
    def expr(self, p):
        if(p.INSTRUCCION in IType):
            return ("IType", p.INSTRUCCION, p.REGISTRO0, p.REGISTRO1, p.INMEDIATO)
        elif(p.INSTRUCCION in SType):
            return ("SType", p.INSTRUCCION, p.REGISTRO0, p.REGISTRO1, p.INMEDIATO)
        else: 
            raise SyntaxError(f"Instrucción I o S no reconocida: {p.INSTRUCCION}")

    @_('INSTRUCCION REGISTRO COMA REGISTRO COMA INSTRUCCION')
    def expr(self, p):
        if(p.INSTRUCCION0 in BType):
            return ("BType", p.INSTRUCCION0, p.REGISTRO0, p.REGISTRO1, p.INSTRUCCION1)
        else: 
            raise SyntaxError(f"Instrucción B no reconocida: {p.INSTRUCCION0}")

    @_('INSTRUCCION REGISTRO COMA INSTRUCCION')
    def expr(self, p):
        if(p.INSTRUCCION0 in JType):
            return ("JType", p.INSTRUCCION0, p.REGISTRO, p.INSTRUCCION1)
        else: 
            raise SyntaxError(f"Instrucción J no reconocida: {p.INSTRUCCION0}")

    @_('INSTRUCCION REGISTRO COMA INMEDIATO')
    def expr(self, p):
        if(p.INSTRUCCION in UType):
            return ("UType", p.INSTRUCCION, p.REGISTRO, p.INMEDIATO)
        else: 
            raise SyntaxError(f"Instrucción U no reconocida: {p.INSTRUCCION0}")


#--------------------------------------------------------------------------#        
with open('input.asm') as f: data = f.read()
PC = 0
outputBinario = open("output.bin", "w")
outputHexadecimal = open("output.hex", "w")



#primera pasada: busca las etiquetas y las guarda en un diccionario con su posición
for line in data.split('\n'):
    
    if(line.strip().endswith(":")): 

        if(" " in line.strip()[:-1]): raise SyntaxError("No se permiten espacios en las etiquetas")

        label = line.strip()[:-1] #elimina los espacios y los dos puntos
        labels[label] = PC
        continue

    if(not line.strip()): continue #salta lineas vacias
    else: PC += 4

print(f"labels: {labels}")



#segunda pasada: organiza y guarda las instrucciones
PC = 0
PCv = 0
status = ".text"
for line in data.split('\n'): 
    if(not line.strip() or line.strip().endswith(":") or line.strip().startswith("#")): continue #salta lineas vacias o labels

    if(line.strip() == ".data" and PC == 0): 
        status = ".data"
        continue
    elif(line.strip() == ".text"):
        status = ".text"
        continue
    elif(line.strip() == ".data"): raise SyntaxError("El .data debe estar en la primera linea")


    if(status == ".text"):
        line = pseudo(line.strip().split(" "), line, labels) #revisa si es pseudo, si si devuelve su equivalente en standar, si no la deja igual

        #parte todo en pedazos
        lexer = CalcLexer()
        tokens = lexer.tokenize(line)
        for tok in tokens: print(f"{tok.type}: {tok.value}")

        #mira la estructura y si coincide con las reglas devuelve la informacion
        parser = ExprParser()
        result = parser.parse(lexer.tokenize(line))
        print(result)

        if(result is None): raise TypeError("Instruccion mal escrita")

        if(result[0] == "RType"):
            instruccion = RType[result[1]]
            rd = result[2]
            rs1 = result[3]
            rs2 = result[4]

            print(f"Instrucción: {instruccion}, rd: {rd}, rs1: {rs1}, rs2: {rs2}")

            #ordena la instrucción en binario
            binario = 0
            binario |= (int(instruccion[2], 2) << 25)
            binario |= (rs2 << 20)
            binario |= (rs1 << 15)
            binario |= (int(instruccion[1], 2) << 12)
            binario |= (rd << 7)
            binario |= (int(instruccion[0], 2))

            outputBinario.write(f"\n{bin(binario)[2:].zfill(32)} + {PC}") #escribe en el archivo el binario de 32 bits
            print(f"Binario: {bin(binario)[2:].zfill(32)}")

            outputHexadecimal.write(f"\n{hex(binario)}") #escribe en el archivo el binario en hexadecimal
            print(f"Hexadecimal: {hex(binario)}")

        if(result[0] == "IType"):
            instruccion = IType[result[1]]
            rd = result[2]
            rs1 = result[3]
            inmediato = int(complementoA2(result[4], 12), 2)

            print(f"Instrucción: {instruccion}, rd: {rd}, rs1: {rs1}, inmediato: {inmediato}")
            

            if(result[1] == "slli" or result[1] == "srli"):
                if(result[4] < 0 or result[4] > 31): raise ValueError(f"El inmediato para {result[1]} debe estar entre 0 y 31")
                inmediato = bin(inmediato)[2:].zfill(12) #toma solo los ultimos 5 bits del inmediato y lo convierte a binario de 12 bits
                inmediato = int(inmediato, 2)

            elif(result[1] == 'srai'):
                if(result[4] < 0 or result[4] > 31): raise ValueError(f"El inmediato para {result[1]} debe estar entre 0 y 31")
                inmediato = bin(inmediato | 0b010000000000)[2:].zfill(12) #toma solo los ultimos 5 bits del inmediato y le pone el bit 10 en 1 para indicar que es srai
                inmediato = int(inmediato, 2)

            else:
                if(result[4] < -2048 or result[4] > 2047): raise ValueError(f"El inmediato para {result[1]} debe estar entre -2048 y 2047")

            #ordena la instrucción en binario
            binario = 0
            binario |= ((inmediato & 0b111111111111) << 20) #toma solo los ultimos 12 bits del inmediato
            binario |= (rs1 << 15)
            binario |= (int(instruccion[1], 2) << 12)
            binario |= (rd << 7)
            binario |= (int(instruccion[0], 2))

            outputBinario.write(f"\n{bin(binario)[2:].zfill(32)} + {PC}") #escribe en el archivo el binario de 32 bits
            print(f"Binario: {bin(binario)[2:].zfill(32)}")

            outputHexadecimal.write(f"\n{hex(binario)}") #escribe en el archivo el binario en hexadecimal
            print(f"Hexadecimal: {hex(binario)}")

        if(result[0] == "SType"):
            instruccion = SType[result[1]]
            rs2 = result[2]
            rs1 = result[3]
            inmediato = result[4]
            print(f"Instrucción: {instruccion}, rs2: {rs2}, rs1: {rs1}, inmediato: {inmediato}")

            if inmediato < -2048 or inmediato > 2047: raise ValueError(f"El inmediato para {instruccion} debe estar entre -2048 y 2047")
            inmediato = int(complementoA2(inmediato, 12), 2)
            print(f"inmediato que estamos procesando: {inmediato}")

            binario = 0
            binario |= ((inmediato >> 5) & 0b1111111) << 25
            binario |= (rs2 << 20)
            binario |= (rs1 << 15)
            binario |= (int(instruccion[1], 2) << 12)
            # bits 4:0 -> pos 11:7
            binario |= (inmediato & 0b11111) << 7
            binario |= int(instruccion[0], 2)

            binario_str = bin(binario)[2:].zfill(32)
            print(f"Binario: {binario_str}\nHexadecimal: {hex(binario)}")
    
        if(result[0] == "BType"):
            instruccion = result[1]
            rs1 = result[2]
            rs2 = result[3]
            label = result[4]

            if label not in labels: raise ValueError(f"Etiqueta no encontrada: {label}")
            inmediato = labels[label] - PC
            print(f"{inmediato} =+ {labels[label]} - {PC}")

            inmediato = int(complementoA2(inmediato, 13), 2)
            #inmediato = inmediato >> 6 #si es negativo se convierte a complemento a 2 de 13 bits
            print(f"inmediato que estamos procesando: {bin(inmediato & 0b1111111111111)}")
            print(f"que hace esto? {bin(inmediato & 0b1000000000000)}")

            print(f"Instrucción: {instruccion}, rs1: {rs1}, rs2: {rs2}, label: {label}, inmediato calculado(nuevo PC): {inmediato}")

            binario = 0
            binario |= ((inmediato >> 12) & 0b1) << 31          # bit 12 -> bit 31
            binario |= ((inmediato >> 5) & 0b111111) << 25      # bits 10:5 -> 30:25
            binario |= (rs2 << 20)
            binario |= (rs1 << 15)
            binario |= (int(BType[instruccion][1], 2) << 12)    # funct3 en binario
            binario |= ((inmediato >> 1) & 0b1111) << 8         # bits 4:1 -> 11:8
            binario |= ((inmediato >> 11) & 0b1) << 7            # bit 11 -> 7
            binario |= int(BType[instruccion][0], 2)             # opcode en binario


            outputBinario.write(f"\n{bin(binario)[2:].zfill(32)} + {PC}") #escribe en el archivo el binario de 32 bits
            print(f"Binario: {bin(binario)[2:].zfill(32)}")

            outputHexadecimal.write(f"\n{hex(binario)}") #escribe en el archivo el binario en hexadecimal
            print(f"Hexadecimal: {hex(binario)}")
            
        if(result[0] == "JType"):
            instruccion = result[1]
            rs1 = result[2]
            label = result[3]

            if label not in labels: raise ValueError(f"Etiqueta no encontrada: {label}")
            inmediato = labels[label] - PC
            print(f"{inmediato} =+ {labels[label]} - {PC}")

            inmediato = int(complementoA2(inmediato, 21), 2)
            print(f"inmediato cambiado: {inmediato}")


            binario = 0
            binario |= ((inmediato >> 31) & 0b1 ) << 31
            binario |= ((inmediato >> 1) & 0b11111111111) << 21
            binario |= ((inmediato >> 11) & 0b1) << 20
            binario |= ((inmediato >> 12) & 0b11111111) << 12
            binario |= (rs1 << 7)
            binario |= int(JType[instruccion][0], 2)


            outputBinario.write(f"\n{bin(binario)[2:].zfill(32)} + {PC}") #escribe en el archivo el binario de 32 bits
            print(f"Binario: {bin(binario)[2:].zfill(32)}")

            outputHexadecimal.write(f"\n{hex(binario)}") #escribe en el archivo el binario en hexadecimal
            print(f"Hexadecimal: {hex(binario)}")

        if(result[0] == "UType"):
            instruccion = result[1]
            rs1 = result[2]
            inmediato = result[3]
                                            #1.048.575 sin signo 20 bits
            if(inmediato < 0 or inmediato > 1048575): raise ValueError(f"El inmediato para {result[1]} debe estar entre 0 y 1.048.575")

            binario = 0
            binario |= (inmediato) << 12
            binario |= (rs1) << 7
            binario |= int(UType[instruccion][0], 2)

            print(f"andamos poniendo a: {bin(inmediato)}")


            outputBinario.write(f"\n{bin(binario)[2:].zfill(32)} + {PC}") #escribe en el archivo el binario de 32 bits
            print(f"Binario: {bin(binario)[2:].zfill(32)}")

            outputHexadecimal.write(f"\n{hex(binario)}") #escribe en el archivo el binario en hexadecimal
            print(f"Hexadecimal: {hex(binario)}")
            

        PC += 4


    else:
        line = line.strip().split(" ", 2)
        if line[2].startswith('0x') or line[2].startswith('0X'): line[2] = int(line[2], 16)
        
        if(line[1] == ".word"):
            try:
                line[2] = complementoA2(int(line[2]), 32)
                print(f"numero: {line[2]}")
                cadena = textwrap.wrap(line[2].zfill(32), 8)

                infoGuardada.append(cadena[3])
                infoGuardada.append(cadena[2])
                infoGuardada.append(cadena[1])
                infoGuardada.append(cadena[0])

                variables[line[0]] = PCv
                PCv += 4
            except ValueError:
                raise SyntaxError(f".word solo acepta int, recibido: {line[2]}")

        elif(line[1] == ".dword"):
            try:
                line[2] = complementoA2(int(line[2]), 64)
                print(f"numero: {line[2]}")
                cadena = textwrap.wrap(line[2].zfill(64), 8)

                infoGuardada.append(cadena[7])
                infoGuardada.append(cadena[6])
                infoGuardada.append(cadena[5])
                infoGuardada.append(cadena[4])
                infoGuardada.append(cadena[3])
                infoGuardada.append(cadena[2])
                infoGuardada.append(cadena[1])
                infoGuardada.append(cadena[0])

                variables[line[0]] = PCv
                PCv += 8
            except ValueError:
                raise SyntaxError(f".dword solo acepta int, recibido: {line[2]}")

        elif(line[1] == ".byte"):
            try:
                line[2] = ord(line[2][1:-1])
                line[2] = complementoA2(int(line[2]), 8)
                print(f"letra en numero: {line[2]}")
                cadena = textwrap.wrap(line[2].zfill(8), 8)

                infoGuardada.append(cadena[0])

                variables[line[0]] = PCv
                PCv += 1         
            
            except TypeError:
                try:
                    line[2] = complementoA2(int(line[2]), 8)
                    print(f"numero: {line[2]}")
                    cadena = textwrap.wrap(line[2].zfill(8), 8)

                    infoGuardada.append(cadena[0])

                    variables[line[0]] = PCv
                    PCv += 1

                except ValueError:
                    if(not line[2].startswith("\"") or not line[2].endswith("\"" )): raise SyntaxError("Los strings deben ir entre comillas")
                    raise SyntaxError(f".byte solo acepta int o un solo caracter, recibido: {line[2]}")

        elif(line[1] == ".half"):
            try:
                line[2] = complementoA2(int(line[2]), 16)
                print(f"numero: {line[2]}")
                cadena = textwrap.wrap(line[2].zfill(16), 8)

                infoGuardada.append(cadena[1])
                infoGuardada.append(cadena[0])

                variables[line[0]] = PCv
                PCv += 2
            except ValueError:
                raise SyntaxError(f".half solo acepta int, recibido: {line[2]}")

        elif(line[1] == ".space"):
            try:
                line[2] = int(line[2])
                print(f"numero: {line[2]}")

                for i in range(line[2]): infoGuardada.append("00000000")

                variables[line[0]] = PCv
                PCv += line[2]
            except ValueError:
                raise SyntaxError(f".word solo acepta int, recibido: {line[2]}")

        elif(line[1] == ".ascii"):
            try:
                if(line[2][0] != "\"" or line[2][-1] != "\""): raise SyntaxError("Los strings deben ir entre comillas")
                line[2] = list(line[2])[1:-1]

                for caracter in line[2]:
                    print(caracter)
                    caracter = ord(caracter)
                    caracter = complementoA2(int(caracter), 8)
                    print(f"letra en numero: {caracter}")
                    cadena = textwrap.wrap(caracter.zfill(8), 8)

                    infoGuardada.append(cadena[0])
            except ValueError:
                raise SyntaxError(f"recibido: {line[2]}")

        elif(line[1] == ".asciz" or line[1] == ".string"):
            try:
                if(line[2][0] != "\"" or line[2][-1] != "\""): raise SyntaxError("Los strings deben ir entre comillas")
                line[2] = list(line[2])[1:-1]
                if(not line[2].startswith("\"") or not line[2].endswith("\"" )): raise SyntaxError("Los strings deben ir entre comillas")

                for caracter in line[2]:
                    caracter = ord(caracter)
                    caracter = complementoA2(int(caracter), 8)
                    print(f"letra en numero: {caracter}")
                    cadena = textwrap.wrap(caracter.zfill(8), 8)

                    infoGuardada.append(cadena[0])

                infoGuardada.append("00000000")
            except ValueError:
                raise SyntaxError(f".word solo acepta int, recibido: {line[2]}")


print(variables)
print(infoGuardada)
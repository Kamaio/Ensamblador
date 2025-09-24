

.data
myvar: .word 12
otraotracosa: .byte "w"
otraotraotracosa: .half 28
otraotraotraotracosa: .space 0
otraotraotraotracosaotracosa: .ascii "hola como vamos"


.text


addi x1, x2, -3
#hola gente estoy doramion
nop
mv x1, x2
not x1, x2
neg x1, x2
seqz x1, x2
snez x1, x2
sltz x1, x2
sgtz x1, x2
beqz x1, cosa
bnez x1, cosa
blez x1, cosa
bgez x1, cosa
bltz x1, cosa
bgtz x1, cosa   
bgt x1, x2, cosa     
ble x1, x2, cosa   
bgtu x1, x2, cosa    
bleu x1, x2, cosa           
j cosa
jal cosa
jr x1
jalr x1
ret


cosa:
nop
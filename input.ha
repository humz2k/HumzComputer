#a 50
#b 51
#c 52
#d 53
#e 54

#current 61

@a UNSIGNED 104
@b UNSIGNED 101
@c UNSIGNED 108
@d UNSIGNED 108
@e UNSIGNED 111

@current UNSIGNED 50

.start
PSH MEMORY_IDIR current
COC e MEMORY_DIR current
INC 1 MEMORY_DIR current
JME end
JMP start
.end
FLP
EOF

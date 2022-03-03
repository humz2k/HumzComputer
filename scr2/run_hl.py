from computer import *
from compiler4 import *

file = "programs/fib.hl"
compiler = Compiler(file)
parser = Parser()
out = parser.parse(compiler.compiled,False)

cpu = CPU(single_program=True)
cpu.load(out)
cpu.loop()
#cpu.ram.print_content(8,20)

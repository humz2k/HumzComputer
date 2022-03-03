from computer import *
from compiler4 import *

file = "programs/test.hl"
compiler = Compiler(file)
parser = Parser()
out = parser.parse(compiler.compiled,False)

cpu = CPU(single_program=True)
cpu.load(out)
cpu.loop()
#cpu.ram.print_content(8,20)
mc_val = cpu.register_memory.mc.get_contents().data
register_val = compiler.malloc_start
alloced = mc_val - register_val

print("\n\nUSED MEMORY:",mc_val,"\nBASE MEMORY:",register_val,"\nMEMORY ALLOCED:",alloced,"\nTOTAL MEMORY:",cpu.ram.mem_len)

from compiler2 import *
from main import *

compiler = Compiler("fib.hl")
cpu = CPU()

parser = Parser()

parsed = parser.parse("out.ha")

#print(parsed)

cpu.load(parsed)



cpu.loop()

#cpu.ram.print()
#cpu.ram.print_content()

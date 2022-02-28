from compiler2 import *
from computer import *
import sys

if __name__ == "__main__":

    compiler = Compiler(sys.argv[1])
    cpu = CPU()

    parser = Parser()

    parsed = parser.parse("out.ha")

    #print(parsed)

    cpu.load(parsed)



    cpu.loop()

#cpu.ram.print()
#cpu.ram.print_content()

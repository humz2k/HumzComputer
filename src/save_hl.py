from file_system import *
from computer import *
from compiler2 import *

files = Files()
compiler = Compiler("fib.hl")
parser = Parser()
parsed = parser.parse("out.ha")

for i in files.data:
    print(i)

'''

store_divide = get_raw(ram_content(DataType.INSTRUCTION,OP.XLM,0,0,0,0,0,0))

stores = parsed[0]

commands_divide = get_raw(ram_content(DataType.INSTRUCTION,OP.XLM,0,0,0,0,0,0))

commands = parsed[1]

files.add(store_divide)
for i in stores:
    files.add(i[0])
    files.add(get_raw(i[1]))
files.add(commands_divide)
for i in commands:
    files.add(get_raw(i))

files.save()
'''

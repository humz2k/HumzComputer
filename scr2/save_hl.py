from file_system import *
from computer import *
from compiler2 import *
import sys

if __name__ == "__main__":
    try:
        file = sys.argv[1]
        overwrite = False
        if len(sys.argv) > 2:
            overwrite = sys.argv[2] == "-o"
    except:
        overwrite = False
        file = "programs/hello_world.hl"

    files = Files()
    compiler = Compiler(file)
    parser = Parser()
    parsed = parser.parse("out.ha")

    if overwrite:
        files.data = []

    store_divide = from_contents(ram_content(DataType.INSTRUCTION,OP.XLM,0,0,0,0,0))

    stores = parsed[0]

    commands_divide = from_contents(ram_content(DataType.INSTRUCTION,OP.XLC,0,0,0,0,0))

    commands = parsed[1]

    files.add(store_divide)
    for i in stores:
        files.add(i[0])
        files.add(from_contents(i[1]))
    files.add(commands_divide)
    for i in commands:
        files.add(from_contents(i))

    print(files.data.count(from_contents(ram_content(DataType.INSTRUCTION,OP.EOF,0,0,0,0,0)))-1)

    files.save()

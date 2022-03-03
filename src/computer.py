from memory import *
from file_system import *
from screen import *

class CPU:
    def __init__(self,single_program=True):
        self.ram = Ram()

        self.single_program = single_program

        self.register_memory = RegisterMemory()
        self.register_memory.generate_enum_registermap()
        self.registers = self.register_memory.get_registers()

        self.files = Files()

        self.op_map = OPMap(self)
        self.op_map.generate_enum_opmap()
        self.ops = self.op_map.get_ops()

        self.screen = screen()

    def print_register(self,register):
        print(str(register) + ":",self.registers[register].get_contents())

    def step(self):
        self.register_memory.ci.set_raw(self.ram.get_raw(self.register_memory.pc.get_raw()))
        command = self.register_memory.ci.get_contents()
        if command.type == DataType.INSTRUCTION:
            self.ops[command.op](command)
        else:
            self.register_memory.pc.increment()

    def resolve_addr(self,addr,mode):
        if mode == AddrModes.MEMORY_DIR:
            return addr
        if mode == AddrModes.MEMORY_IDIR:
            return self.ram.get_contents(addr).data
        if mode == AddrModes.REGISTER_IDIR:
            return self.registers[addr].get_contents().data

    def loop(self):
        if self.single_program:
            while self.register_memory.ci.get_contents().op != OP.EOF:
                self.step()
        else:
            while True:
                self.step()

    def load(self,parsed):
        for i in parsed[0]:
            self.ram.set_contents(i[0],i[1])
        for idx,i in enumerate(parsed[1]):
            self.ram.set_contents(idx,i)
        self.register_memory.pc.set_raw(0)

    def load_file(self,file):
        store_divide = from_contents(ram_content(DataType.INSTRUCTION,OP.XLM,0,0,0,0,0))
        commands_divide = from_contents(ram_content(DataType.INSTRUCTION,OP.XLC,0,0,0,0,0))
        eof_divide = from_contents(ram_content(DataType.INSTRUCTION,OP.EOF,0,0,0,0,0))
        temp = [[]]
        for i in self.files.data:
            temp[-1].append(i)
            if i == eof_divide:
                temp.append([])
        if file > (len(temp) - 2):
            return self.load_file(0)
        to_add = temp[file]
        assigns = []
        commands = []
        is_assign = False
        count = 0
        while count < len(to_add):
            i = to_add[count]
            if i == store_divide:
                is_assign = True
            elif i == commands_divide:
                is_assign = False
            else:
                if is_assign:
                    assigns.append([to_add[count],to_add[count+1]])
                    count += 1
                else:
                    commands.append(i)
            count += 1
        for i in assigns:
            self.ram.set_raw(i[0],i[1])
        for idx,i in enumerate(commands):
            self.ram.set_raw(idx,i)

def py_to_data(i):
    negative = i < 0
    data = abs(i) & Masks.DATA
    if negative:
        return (int("".join([["0","1"][e == "0"] for e in str_binary(data)]),2) + 1) & Masks.DATA
    return data

class Parser:
    def __init__(self):
        self.const_addr = [OP.LDM,OP.INC,OP.DEC,OP.COC]
        self.addr = [OP.CLR,OP.ZER,OP.PSH,OP.PSI,OP.INP,OP.LFM]
        self.const = [OP.JMP,OP.JME,OP.JMG,OP.JML]
        self.none = [OP.FLP,OP.EOF,OP.POP,OP.XLM,OP.XLC]
        self.addr_addr = [OP.CPY, OP.ADD, OP.SUB, OP.MUL, OP.DIV, OP.COM]
        self.jumps = [OP.JMP,OP.JME,OP.JMG,OP.JML]

    def parse(self,file,is_file=True):
        parsed = []
        lines = []
        if is_file:
            with open(file,"r") as f:
                lines = [line for line in f.read().splitlines() if len(line) > 0]
        else:
            lines = file

        consts = {}

        for line in [l for l in lines if l[0] == "#"]:
            temp = line[1:].split(" ")
            consts[temp[0]] = int(temp[1])

        stores = []
        for line in [l for l in lines if l[0] == "@"]:
            temp = line[1:].split(" ")

            location = temp[0]
            if location in consts:
                location = consts[location]
            else:
                location = int(location)

            type = DataType[temp[1]]

            data = temp[2]

            if data in consts:
                data = consts[data]

            data = int(data)

            if type == DataType.SIGNED:
                data = py_to_data(data)

            stores.append([location,ram_content(type,0,0,0,0,0,data)])

        to_replace = {}
        count = 0
        for line in [l for l in lines if (l[0] != '#' and l[0] != '/' and l[0] != '@')]:
            if line[0] == ".":
                to_replace[line[1:]] = count
            else:
                count += 1

        for line in [l for l in lines if (l[0] != '#' and l[0] != '/' and l[0] != '@')]:

            outline = None
            command = line.split()
            type = DataType.INSTRUCTION
            addr1 = 0
            addr1mode = 0
            addr2 = 0
            addr2mode = 0
            longaddr = 0
            if line[0] == ".":
                pass
            else:

                op = OP[command[0]]

                if op in self.jumps:
                    if command[1] in to_replace:
                        command[1] = to_replace[command[1]]



                if op in self.none:
                    outline = ram_content(type,op,0,0,0,0,0)

                if op in self.const:
                    addr1 = abs(int(command[1]))
                    outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0)

                if op in self.const_addr:
                    if command[1] in consts:
                        addr1 = abs(int(consts[command[1]]))
                    else:
                        addr1 = abs(int(command[1]))
                    addr2mode = AddrModes[command[2]]
                    addr2 = command[3]
                    if command[3] in consts:
                        addr2 = consts[command[3]]
                    if addr2mode == AddrModes.MEMORY_DIR or addr2mode == AddrModes.MEMORY_IDIR:
                        addr2 = int(addr2)
                    else:
                        addr2 = REG[addr2]
                    outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0)

                if op in self.addr:
                    addr1mode = AddrModes[command[1]]
                    addr1 = command[2]
                    if command[2] in consts:
                        addr1 = consts[command[2]]
                    if addr1mode == AddrModes.MEMORY_DIR or addr1mode == AddrModes.MEMORY_IDIR:
                        addr1 = int(addr1)
                    else:
                        addr1 = REG[addr1]
                    outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0)

                if op in self.addr_addr:
                    addr1mode = AddrModes[command[1]]
                    addr1 = command[2]
                    if command[2] in consts:
                        addr1 = consts[command[2]]
                    if addr1mode == AddrModes.MEMORY_DIR or addr1mode == AddrModes.MEMORY_IDIR:
                        addr1 = int(addr1)
                    else:
                        addr1 = REG[addr1]
                    addr2mode = AddrModes[command[3]]
                    addr2 = command[4]
                    if command[4] in consts:
                        addr2 = consts[command[4]]
                    if addr2mode == AddrModes.MEMORY_DIR or addr2mode == AddrModes.MEMORY_IDIR:
                        addr2 = int(addr2)
                    else:
                        addr2 = REG[addr2]
                    outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0)

                parsed.append(outline)

        return stores,parsed

if __name__ == "__main__":
    cpu = CPU(single_program=False)

    cpu.load_file(0)

    cpu.loop()

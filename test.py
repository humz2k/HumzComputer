from enum import Enum, IntEnum
from dataclasses import dataclass
import sys

#All DataTypes
class DataType(IntEnum):
    INSTRUCTION = 3
    UNSIGNED = 2
    SIGNED = 1
    EMPTY = 0

#All Masks
class Masks(IntEnum):
    DATA = 1073741823 #00111...
    OP = 1056964608 #0011111100...
    ADDR1 = 4190208 #0000000000111111111100...
    ADDR1MODE = 12582912 #000000001100...
    ADDR2 = 1023
    ADDR2MODE = 3072
    LONGADDR = 16777215

#Addr Modes
class AddrModes(IntEnum):
    REGISTER_DIR = 2
    REGISTER_IDIR = 3
    MEMORY_DIR = 0
    MEMORY_IDIR = 1

#class to hold ram content
@dataclass
class ram_content:
    type: int
    op: int
    addr1: int
    addr1mode: int
    addr2: int
    addr2mode: int
    longaddr: int
    data: int

#string to binary
def str_binary(i):
    return bin(i)[2:].zfill(32)

#to see negatives
def twos_comp(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

#helper to input data to ram
def py_to_data(i):
    negative = i < 0
    data = abs(i) & Masks.DATA
    if negative:
        return (int("".join([["0","1"][e == "0"] for e in str_binary(data)]),2) + 1) & Masks.DATA
    return data

class Ram:
    def __init__(self):
        self.ram = []
        for i in range(1024):
            self.ram.append(0)

    def print(self,start=0,length=256):
        line = 3
        for i in range(start,start+length):
            if (i%line) == 0:
                print()
            print(str_binary(self.ram[i]),end=" ")
        print()

    def print_content(self,start=0,length=256):
        for i in range(start,start+length):
            print(self.get_contents(i))

    def get_raw(self,addr):
        return self.ram[addr]

    def get_type(self,addr):
        t = self.ram[addr]
        t = t >> 30
        return DataType(t)

    def get_data(self,addr):
        t = self.ram[addr]
        return t & Masks.DATA

    def get_addr1(self,addr):
        t = self.ram[addr]
        t = t & Masks.ADDR1
        t = t >> 12
        return t

    def get_addr1mode(self,addr):
        t = self.ram[addr]
        t = t & Masks.ADDR1MODE
        t = t >> 22
        return AddrModes(t)

    def get_addr2(self,addr):
        t = self.ram[addr]
        t = t & Masks.ADDR2
        return t

    def get_addr2mode(self,addr):
        t = self.ram[addr]
        t = t & Masks.ADDR2MODE
        t = t >> 10
        return AddrModes(t)

    def get_long_addr(self,addr):
        t = self.ram[addr]
        t = t & Masks.LONGADDR
        return t

    def get_op(self,addr):
        t = self.ram[addr]
        t = t & Masks.OP
        t = t >> 24
        try:
            return OP(t)
        except:
            return t

    def get_contents(self,addr):
        this_type = self.get_type(addr)
        op = 0
        long_addr = 0
        data = 0
        addr1 = 0
        addr1mode = 0
        addr2 = 0
        addr2mode = 0
        if this_type == DataType.INSTRUCTION:
            op = self.get_op()
            long_addr = self.get_long_addr()
            register_address_modes = [AddrModes.REGISTER_DIR,AddrModes.REGISTER_IDIR]
            addr1 = self.get_addr1(addr)
            addr1mode = self.get_addr1mode(addr)
            if addr1mode in register_address_modes:
                addr1 = REG(addr1)
            addr2 = self.get_addr2(addr)
            addr2mode = self.get_addr2mode(addr)
            if addr2mode in register_address_modes:
                addr2 = REG(addr2)
        else:
            data = self.get_data(addr)
            if this_type == DataType.SIGNED:
                data = twos_comp(data,30)
        return ram_content(this_type,op,addr1,addr1mode,addr2,addr2mode,long_addr,data)

    def clear_contents(self,addr):
        ram.ram[addr] = 0

    def set_contents(self,addr,content):
        if content.type == DataType.INSTRUCTION:
            this_type = content.type << 30
            op = content.op << 24
            addr1mode = content.addr1mode << 22
            addr1 = content.addr1 << 12
            addr2mode = content.addr2mode << 10
            addr2 = content.addr2
            raw = this_type | op | addr1 | addr1mode | addr2 | addr2mode
            self.ram[addr] = raw
        else:
            data = (content.data & Masks.DATA) | (content.type << 30)
            self.ram[addr] = data

class Register:
    def __init__(self,name):
        self.name = name
        self.val = 0

    def increment(self):
        self.val += 1

    def set_raw(self,value):
        self.val = value

    def set_contents(self,content):
        if content.type == DataType.INSTRUCTION:
            this_type = content.type << 30
            op = content.op << 24
            addr1mode = content.addr1mode << 22
            addr1 = content.addr1 << 12
            addr2mode = content.addr2mode << 10
            addr2 = content.addr2
            raw = this_type | op | addr1 | addr1mode | addr2 | addr2mode
            self.val = raw
        else:
            data = (content.data & Masks.DATA) | (content.type << 30)
            self.val = data

    def get_raw(self):
        return self.val

    def get_type(self):
        t = self.val
        t = t >> 30
        return DataType(t)

    def get_data(self):
        t = self.val
        return t & Masks.DATA

    def get_addr1(self):
        t = self.val
        t = t & Masks.ADDR1
        t = t >> 12
        return t

    def get_addr1mode(self):
        t = self.val
        t = t & Masks.ADDR1MODE
        t = t >> 22
        return AddrModes(t)

    def get_addr2(self):
        t = self.val
        t = t & Masks.ADDR2
        return t

    def get_addr2mode(self):
        t = self.val
        t = t & Masks.ADDR2MODE
        t = t >> 10
        return AddrModes(t)

    def get_long_addr(self):
        t = self.val
        t = t & Masks.LONGADDR
        return t

    def get_op(self):
        t = self.val
        t = t & Masks.OP
        t = t >> 24
        try:
            return OP(t)
        except:
            return t

    def get_contents(self):
        this_type = self.get_type()
        data = self.get_data()
        if this_type == DataType.SIGNED:
            data = twos_comp(data,30)

        register_address_modes = [AddrModes.REGISTER_DIR,AddrModes.REGISTER_IDIR]
        addr1 = self.get_addr1()
        addr1mode = self.get_addr1mode()
        if addr1mode in register_address_modes:
            addr1 = REG(addr1)
        addr2 = self.get_addr2()
        addr2mode = self.get_addr2mode()
        if addr2mode in register_address_modes:
            addr2 = REG(addr2)
        return ram_content(this_type,self.get_op(),addr1,addr1mode,addr2,addr2mode,self.get_long_addr(),data)

class CPU:
    def __init__(self):
        self.ram = Ram()

        self.pc = Register("pc")
        self.ci = Register("ci")
        self.mc = Register("mc")

        registers_temp = [self.pc,self.ci,self.mc]

        for i in "abcdefghijklmnop":
            registers_temp.append(Register("g" + i))

        self.registers = {}

        to_enum = ""
        for idx,register in enumerate(registers_temp):
            self.registers[idx+1] = register
            to_enum = to_enum + register.name.upper() + " "

        global REG

        REG = IntEnum('REG', to_enum)

        self.OPMapper = self.OPMap(self)

        self.ops = {}

        to_enum = ""
        #iterates through OPMap and creates an enum/dict of functions
        for idx,op in enumerate([f for f in dir(self.OPMapper) if f[0:2] == "op"]):
            self.ops[idx+1] = getattr(self.OPMapper,op)
            to_enum = to_enum + op[3:] + " "

        global OP

        OP = IntEnum('OP',to_enum)

    def print_register(self,register):
        print(str(register) + ":",self.registers[register].get_contents())

    def step(self):
        self.ci.set_raw(self.ram.get_raw(self.pc.get_raw()))
        command = self.ci.get_contents()

        if command.type == DataType.INSTRUCTION:
            self.ops[command.op](command)
        else:
            self.pc.increment()

    def resolve_addr(self,addr,mode):
        if mode == AddrModes.MEMORY_DIR:
            return addr
        if mode == AddrModes.MEMORY_IDIR:
            return self.ram.get_contents(addr).data
        if mode == AddrModes.REGISTER_IDIR:
            return self.registers[addr].get_contents().data

    def loop(self):
        for i in range(5):
            self.step()

    def load(self,parsed):
        for i in parsed[0]:
            self.ram.set_contents(i[0],i[1])
        for idx,i in enumerate(parsed[1]):
            self.ram.set_contents(idx,i)
        self.pc.set_raw(0)

    class OPMap:
        def __init__(self,cpu):
            self.cpu = cpu

        def op_LDM(self,command):
            if command.addr2mode != AddrModes.REGISTER_DIR:
                addr = self.cpu.resolve_addr(command.addr2,command.addr2mode)
                self.cpu.ram.set_contents(addr,ram_content(DataType.UNSIGNED,0,0,0,0,0,0,command.addr1))
            else:
                addr = command.addr2
                self.cpu.registers[addr].set_contents(ram_content(DataType.UNSIGNED,0,0,0,0,0,0,command.addr1))
            self.cpu.pc.increment()

        def op_INC(self,command):
            if command.addr2mode != AddrModes.REGISTER_DIR:
                addr = self.cpu.resolve_addr(command.addr2,command.addr2mode)
                contents = self.cpu.ram.get_contents(addr)
                contents.data += command.addr1
                self.cpu.ram.set_contents(addr,contents)
            else:
                addr = command.addr2
                contents = self.cpu.registers[addr].get_contents()
                contents.data += command.addr1
                self.cpu.registers[addr].set_contents(contents)
            self.cpu.pc.increment()

        def op_DEC(self,command):
            if command.addr2mode != AddrModes.REGISTER_DIR:
                addr = self.cpu.resolve_addr(command.addr2,command.addr2mode)
                contents = self.cpu.ram.get_contents(addr)
                contents.data -= command.addr1
                self.cpu.ram.set_contents(addr,contents)
            else:
                addr = command.addr2
                contents = self.cpu.registers[addr].get_contents()
                contents.data -= command.addr1
                self.cpu.registers[addr].set_contents(contents)
            self.cpu.pc.increment()

class Parser:
    def __init__(self):
        self.const_addr = [OP.LDM,OP.INC,OP.DEC]

    def parse(self,file):
        parsed = []
        lines = []
        with open(file,"r") as f:
            lines = [line for line in f.read().splitlines() if len(line) > 0]

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

            stores.append([location,ram_content(type,0,0,0,0,0,0,data)])

        for line in [l for l in lines if (l[0] != '#' and l[0] != '/' and l[0] != '@')]:
            print("READING",line)
            outline = None
            command = line.split()
            type = DataType.INSTRUCTION
            op = OP[command[0]]
            addr1 = 0
            addr1mode = 0
            addr2 = 0
            addr2mode = 0
            longaddr = 0

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
                outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0,0)
            parsed.append(outline)

        return stores,parsed

cpu = CPU()

parser = Parser()

parsed = parser.parse("input.ha")

print(parsed[0])
print(parsed[1])

cpu.load(parsed)

cpu.loop()

cpu.ram.print(10,2)
cpu.ram.print_content(10,2)

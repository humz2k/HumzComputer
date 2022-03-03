from enum import IntEnum
from dataclasses import dataclass
from inp_char import *

getch = Getch()

@dataclass
class ram_content:
    type: int
    op: int
    addr1: int
    addr1mode: int
    addr2: int
    addr2mode: int
    data: int

class DataType(IntEnum):
    INSTRUCTION = 3
    UNSIGNED = 2
    SIGNED = 1
    EMPTY = 0

class AddrModes(IntEnum):
    REGISTER_DIR = 2
    REGISTER_IDIR = 3
    MEMORY_DIR = 0
    MEMORY_IDIR = 1

class Masks(IntEnum):
    TYPE_SHIFT = 38
    DATA = int('0b0000000011111111111111111111111111111111', 2)
    OP = int('0b0011111100000000000000000000000000000000', 2)
    OP_SHIFT = 32
    ADDR1 = int('0b0000000000111111111111110000000000000000', 2)
    ADDR1_SHIFT = 16
    ADDR1MODE = int('0b0000000011000000000000000000000000000000', 2)
    ADDR1MODE_SHIFT = 30
    ADDR2 = int('0b0000000000000000000000000011111111111111', 2)
    ADDR2MODE = int('0b0000000000000000000000001100000000000000', 2)
    ADDR2MODE_SHIFT = 14

#string to binary
def str_binary(i,size=40):
    return bin(i)[2:].zfill(size)

#to see negatives
def twos_comp(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

class ram_content_helpers:
    def get_type(val):
        t = val
        t = t >> Masks.TYPE_SHIFT
        return DataType(t)

    def get_data(val):
        t = val
        return t & Masks.DATA

    def get_addr1(val):
        t = val
        t = t & Masks.ADDR1
        t = t >> Masks.ADDR1_SHIFT
        return t

    def get_addr1mode(val):
        t = val
        t = t & Masks.ADDR1MODE
        t = t >> Masks.ADDR1MODE_SHIFT
        return AddrModes(t)

    def get_addr2(val):
        t = val
        t = t & Masks.ADDR2
        return t

    def get_addr2mode(val):
        t = val
        t = t & Masks.ADDR2MODE
        t = t >> Masks.ADDR2MODE_SHIFT
        return AddrModes(t)

    def get_op(val):
        t = val
        t = t & Masks.OP
        t = t >> Masks.OP_SHIFT
        return t

def get_contents(val):
    this_type = ram_content_helpers.get_type(val)
    op = ram_content_helpers.get_op(val)
    try:
        op = OP(op)
    except:
        pass
    data = ram_content_helpers.get_data(val)
    addr1 = ram_content_helpers.get_addr1(val)
    addr1mode = ram_content_helpers.get_addr1mode(val)
    addr2 = ram_content_helpers.get_addr2(val)
    addr2mode = ram_content_helpers.get_addr2mode(val)
    if this_type == DataType.SIGNED:
        data = twos_comp(data,32)
    return ram_content(this_type,op,addr1,addr1mode,addr2,addr2mode,data)

def from_contents(content):
    if content.type == DataType.INSTRUCTION:
        this_type = content.type << Masks.TYPE_SHIFT
        op = content.op << Masks.OP_SHIFT
        addr1mode = content.addr1mode << Masks.ADDR1MODE_SHIFT
        addr1 = content.addr1 << Masks.ADDR1_SHIFT
        addr2mode = content.addr2mode << Masks.ADDR2MODE_SHIFT
        addr2 = content.addr2
        return this_type | op | addr1 | addr1mode | addr2 | addr2mode
    else:
        return (content.data & Masks.DATA) | (content.type << Masks.TYPE_SHIFT)


class Ram:
    def __init__(self,mem_len=16384):
        self.mem_len = mem_len
        self.memory = bytearray(self.mem_len*5)

    def clear(self):
        for i in range(len(self.memory)):
            self.memory[i] = 0

    def get_array(self,idx):
        return self.memory[idx*5:(idx*5)+5]

    def get_raw(self,idx):
        return int.from_bytes(b"".join([self.get_array(idx)]),'big')

    def clear_idx(self,idx):
        zero = 0
        self.memory[idx*5:(idx*5)+5] = zero.to_bytes(5,'big')

    def set_raw(self,idx,val):
        self.memory[idx*5:(idx*5)+5] = val.to_bytes(5,'big')

    def get_contents(self,idx):
        raw = self.get_raw(idx)
        return get_contents(raw)

    def set_contents(self,idx,content):
        self.set_raw(idx,from_contents(content))

    def print(self,start=0,length=256,line = 2):
        for i in range(start,start+length):
            if (i%line) == 0:
                print()
            print(i,str_binary(self.get_raw(i)),end=" ")

    def print_content(self,start=0,length=256):
        for i in range(start,start+length):
            print(i,self.get_contents(i))

class Register:
    def __init__(self,name):
        self.name = name
        self.val = 0

    def increment(self):
        self.val += 1

    def set_raw(self,value):
        self.val = value

    def set_contents(self,content):
        self.val = from_contents(content)

    def get_raw(self):
        return self.val

    def get_contents(self):
        return get_contents(self.val)

class RegisterMemory:
    def __init__(self):
        self.pc = Register("pc")
        self.ci = Register("ci")
        self.mc = Register("mc")
        self.eq = Register("eq")

        self.register_list = [self.pc,self.ci,self.mc,self.eq]

        for i in "abcdefghijklmnop123456789":
            self.register_list.append(Register("g" + i))

    def generate_enum_registermap(self):
        self.registers = {}

        to_enum = ""
        for idx,register in enumerate(self.register_list):
            self.registers[idx+1] = register
            to_enum = to_enum + register.name.upper() + " "
        return IntEnum('REG', to_enum)

    def get_registers(self):
        return self.registers

REG = RegisterMemory().generate_enum_registermap()

class OPMap:
    def __init__(self,cpu = None):
        self.cpu = cpu

    def generate_enum_opmap(self):

        self.ops = {}

        to_enum = ""
        #iterates through OPMap and creates an enum/dict of functions
        for idx,op in enumerate([f for f in dir(self) if f[0:2] == "op"]):
            self.ops[idx+1] = getattr(self,op)
            to_enum = to_enum + op[3:] + " "

        return IntEnum('OP',to_enum)

    def get_ops(self):
        return self.ops

    def op_LDM(self,command):
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            self.cpu.ram.set_contents(addr,ram_content(DataType.UNSIGNED,0,0,0,0,0,command.addr1))
        else:
            addr = command.addr2
            self.cpu.registers[addr].set_contents(ram_content(DataType.UNSIGNED,0,0,0,0,0,command.addr1))
        self.cpu.register_memory.pc.increment()

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
        self.cpu.register_memory.pc.increment()

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
        self.cpu.register_memory.pc.increment()

    def op_CLR(self,command):
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            self.cpu.ram.clear_contents(addr)
        else:
            addr = command.addr1
            self.cpu.registers[addr].set_raw(0)
        self.cpu.register_memory.pc.increment()
    #FINISH
    def op_ZER(self,command):
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr)
            contents.data = 0
            if contents.type == DataType.EMPTY:
                contents.type = DataType.SIGNED
            self.cpu.ram.set_contents(addr,contents)
        else:
            addr = command.addr1
            contents = self.cpu.registers[addr].get_contents()
            contents.data = 0
            if contents.type == DataType.EMPTY:
                contents.type = DataType.SIGNED
            self.cpu.registers[addr].set_contents(contents)
        self.cpu.register_memory.pc.increment()

    def op_CPY(self,command):
        contents = None
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr1 = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr1)
        else:
            addr1 = command.addr1
            contents = self.cpu.registers[addr1].get_contents()
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr2 = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            self.cpu.ram.set_contents(addr2,contents)
        else:
            addr2 = command.addr2
            self.cpu.registers[addr2].set_contents(contents)
        self.cpu.register_memory.pc.increment()

    def op_ADD(self,command):
        contents = None
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr1 = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr1)
        else:
            addr1 = command.addr1
            contents = self.cpu.registers[addr1].get_contents()
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr2 = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            contents2 = self.cpu.ram.get_contents(addr2)
            contents2.data += contents.data
            self.cpu.ram.set_contents(addr2,contents2)
        else:
            addr2 = command.addr2
            contents2 = self.cpu.registers[addr2].get_contents()
            contents2.data += contents.data
            self.cpu.registers[addr2].set_contents(contents2)
        self.cpu.register_memory.pc.increment()

    def op_SUB(self,command):
        contents = None
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr1 = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr1)
        else:
            addr1 = command.addr1
            contents = self.cpu.registers[addr1].get_contents()
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr2 = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            contents2 = self.cpu.ram.get_contents(addr2)
            contents2.data -= contents.data
            self.cpu.ram.set_contents(addr2,contents2)
        else:
            addr2 = command.addr2
            contents2 = self.cpu.registers[addr2].get_contents()
            contents2.data -= contents.data
            self.cpu.registers[addr2].set_contents(contents2)
        self.cpu.register_memory.pc.increment()

    def op_MUL(self,command):
        contents = None
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr1 = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr1)
        else:
            addr1 = command.addr1
            contents = self.cpu.registers[addr1].get_contents()
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr2 = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            contents2 = self.cpu.ram.get_contents(addr2)
            contents2.data *= contents.data
            self.cpu.ram.set_contents(addr2,contents2)
        else:
            addr2 = command.addr2
            contents2 = self.cpu.registers[addr2].get_contents()
            contents2.data *= contents.data
            self.cpu.registers[addr2].set_contents(contents2)
        self.cpu.register_memory.pc.increment()

    def op_DIV(self,command):
        contents = None
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr1 = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr1)
        else:
            addr1 = command.addr1
            contents = self.cpu.registers[addr1].get_contents()
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr2 = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            contents2 = self.cpu.ram.get_contents(addr2)
            contents2.data //= contents.data
            self.cpu.ram.set_contents(addr2,contents2)
        else:
            addr2 = command.addr2
            contents2 = self.cpu.registers[addr2].get_contents()
            contents2.data //= contents.data
            self.cpu.registers[addr2].set_contents(contents2)
        self.cpu.register_memory.pc.increment()

    def op_COM(self,command):
        contents = None
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr1 = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr1)
        else:
            addr1 = command.addr1
            contents = self.cpu.registers[addr1].get_contents()
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr2 = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            contents2 = self.cpu.ram.get_contents(addr2)
            contents2.data -= contents.data
            contents2.type = DataType.SIGNED

            self.cpu.register_memory.eq.set_contents(contents2)
        else:
            addr2 = command.addr2
            contents2 = self.cpu.registers[addr2].get_contents()
            contents2.data -= contents.data
            contents2.type = DataType.SIGNED

            self.cpu.register_memory.eq.set_contents(contents2)
        self.cpu.register_memory.pc.increment()

    def op_COC(self,command):
        if command.addr2mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            contents = self.cpu.ram.get_contents(addr)
            contents.data -= command.addr1
            contents.type = DataType.SIGNED
            self.cpu.register_memory.eq.set_contents(contents)
        else:
            addr = command.addr2
            contents = self.cpu.registers[addr].get_contents()
            contents.data -= command.addr1
            contents.type = DataType.SIGNED
            self.cpu.register_memory.eq.set_contents(contents)
        self.cpu.register_memory.pc.increment()

    def op_PSH(self,command):
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr)
            self.cpu.screen.push(contents.data)
        else:
            addr = command.addr1
            contents = self.cpu.registers[addr].get_contents()
            self.cpu.screen.push(contents.data)
        self.cpu.register_memory.pc.increment()

    def op_PSI(self,command):
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr)
            for i in str(contents.data):
                self.cpu.screen.push(ord(i))
        else:
            addr = command.addr1
            contents = self.cpu.registers[addr].get_contents()
            for i in str(contents.data):
                self.cpu.screen.push(ord(i))
        self.cpu.register_memory.pc.increment()

    def op_FLP(self,command):
        self.cpu.screen.flip()
        self.cpu.register_memory.pc.increment()

    def op_JMP(self,command):
        self.cpu.register_memory.pc.set_raw(command.addr1)

    def op_JME(self,command):
        if self.cpu.register_memory.eq.get_contents().data == 0:
            self.cpu.register_memory.pc.set_raw(command.addr1)
        else:
            self.cpu.register_memory.pc.increment()

    def op_LFM(self,command):

        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            temp = self.cpu.ram.get_contents(addr).data
        else:
            addr = command.addr1
            temp = self.cpu.registers[addr].get_contents().data
        self.cpu.ram.clear()
        self.cpu.register_memory.pc.val = 0
        self.cpu.load_file(temp)

    def op_JMG(self,command):
        if self.cpu.register_memory.eq.get_contents().data < 0:
            self.cpu.register_memory.pc.set_raw(command.addr1)
        else:
            self.cpu.register_memory.pc.increment()

    def op_JML(self,command):
        if self.cpu.register_memory.eq.get_contents().data > 0:
            self.cpu.register_memory.pc.set_raw(command.addr1)
        else:
            self.cpu.register_memory.pc.increment()

    def op_POP(self,command):
        self.cpu.screen.pop()
        self.cpu.register_memory.pc.increment()

    def op_INP(self,command):
        temp = ord(getch())
        if command.addr1mode != AddrModes.REGISTER_DIR:
            addr = self.cpu.resolve_addr(command.addr1,command.addr1mode)
            contents = self.cpu.ram.get_contents(addr)
            contents.data = temp
            self.cpu.ram.set_contents(addr,contents)
        else:
            addr = command.addr1
            contents = self.cpu.registers[addr].get_contents()
            contents.data = temp
            self.cpu.registers[addr].set_contents(contents)
        self.cpu.register_memory.pc.increment()

    def op_EOF(self,command):
        if not self.cpu.single_program:
            self.cpu.ram.clear()
            self.cpu.register_memory.pc.val = 0
            self.cpu.load_file(0)

    def op_XLM(self,command):
        pass

    def op_XLC(self,command):
        pass

OP = OPMap().generate_enum_opmap()

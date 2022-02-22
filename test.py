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

#Addr Modes
class AddrModes(IntEnum):
    REGISTER_DIR = 0
    REGISTER_IDIR = 1
    MEMORY_DIR = 2
    MEMORY_IDIR = 3

#class to hold ram content
@dataclass
class ram_content:
    type: int
    op: int
    addr1: int
    addr1mode: int
    addr2: int
    addr2mode: int
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
        data = self.get_data(addr)
        if this_type == DataType.SIGNED:
            data = twos_comp(data,30)
        return ram_content(this_type,self.get_op(addr),self.get_addr1(addr),self.get_addr1mode(addr),self.get_addr2(addr),self.get_addr2mode(addr),data)

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
        return ram_content(this_type,self.get_op(),self.get_addr1(),self.get_addr1mode(),self.get_addr2(),self.get_addr2mode(),data)

class CPU:
    def __init__(self):
        self.ram = Ram()

        self.pc = Register("pc")
        self.ci = Register("ci")

        self.registers = [self.pc,self.ci]

        self.OPMapper = self.OPMap(self)

        self.ops = {}

        to_enum = ""
        #iterates through OPMap and creates an enum/dict of functions
        for idx,op in enumerate([f for f in dir(self.OPMapper) if f[0:2] == "op"]):
            self.ops[idx+1] = getattr(self.OPMapper,op)
            to_enum = to_enum + op[3:] + " "

        global OP

        OP = IntEnum('OP',to_enum)

    def step(self):
        self.ci.set_raw(self.ram.get_raw(self.pc.get_raw()))
        command = self.ci.get_contents()

        if command.type == DataType.INSTRUCTION:
            self.ops[command.op](command)

        self.pc.increment()

    def resolve_addr(self,addr,mode):
        if mode == AddrModes.MEMORY_DIR:
            return addr

    def loop(self):
        for i in range(5):
            self.step()

    class OPMap:
        def __init__(self,cpu):
            self.cpu = cpu

        def op_LDD(self,command=None):
            if command == None:
                return 0
            addr = self.cpu.resolve_addr(command.addr2,command.addr2mode)
            self.cpu.ram.set_contents(addr,ram_content(DataType.UNSIGNED,0,0,0,0,0,command.addr1))


cpu = CPU()
cpu.ram.set_contents(1,ram_content(DataType.INSTRUCTION,OP.LDD,1,0,0,AddrModes.MEMORY_DIR,0))
cpu.loop()
cpu.ram.print(0,3)
cpu.ram.print_content(0,3)

from enum import Enum, IntEnum
from dataclasses import dataclass
import sys

class DataType(IntEnum):
    INSTRUCTION = 3
    UNSIGNED = 2
    SIGNED = 1
    EMPTY = 0

class Masks(IntEnum):
    DATA = 1073741823
    OP = 1056964608
    ADDR1 = 16773120
    ADDR2 = 4095

@dataclass
class ram_content:
    type: int
    op: int
    addr1: int
    addr2: int
    data: int

def str_binary(i):
    return bin(i)[2:].zfill(32)

def twos_comp(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def py_to_data(i):
    negative = i < 0
    data = abs(i) & Masks.DATA
    if negative:
        return (int("".join([["0","1"][e == "0"] for e in str_binary(data)]),2) + 1) & Masks.DATA
    return data

class Ram:
    def __init__(self):
        self.ram = []
        for i in range(4096):
            self.ram.append(0)

    def print(self,start=0,length=256):
        line = 3
        count = -1
        print_array = []
        for i in range(start,start+length):
            if (i%line) == 0:
                print()
            print(str_binary(self.ram[i]),end=" ")
        print()

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

    def get_addr2(self,addr):
        t = self.ram[addr]
        t = t & Masks.ADDR2
        return t

    def get_op(self,addr):
        t = self.ram[addr]
        t = t & Masks.OP
        t = t >> 24
        return t

    def get_contents(self,addr):
        this_type = self.get_type(addr)
        data = self.get_data(addr)
        if this_type == DataType.SIGNED:
            data = twos_comp(data,30)
        return ram_content(this_type,self.get_op(addr),self.get_addr1(addr),self.get_addr2(addr),data)

    def clear_contents(self,addr):
        ram.ram[addr] = 0

    def set_contents(self,addr,content):
        if content.type == DataType.INSTRUCTION:
            this_type = content.type << 30
            op = content.op << 24
            addr1 = content.addr1 << 12
            addr2 = content.addr2
            raw = this_type | op | addr1 | addr2
            self.ram[addr] = raw
        else:
            data = (content.data & Masks.DATA) | (content.type << 30)
            self.ram[addr] = data

ram = Ram()
ram.ram[0] = 1073745919
ram.ram[1] = 1090514944
ram.ram[2] = 1140846592
ram.ram[3] = 1677717504
ram.set_contents(4,ram_content(DataType.INSTRUCTION,5,5,6,py_to_data(100000000)))
#print(ram.get_contents(4))
ram.print(0,5)


class Register:
    def __init__(self,name):
        self.name = name
        self.val = 0

    def increment(self):
        self.val += 1

    def set_raw(self,value):
        self.val = value

    def set_contents(self,content):
        pass

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

    def get_addr2(self):
        t = self.val
        t = t & Masks.ADDR2
        return t

    def get_op(self):
        t = self.val
        t = t & Masks.OP
        t = t >> 24
        return t

    def get_contents(self):
        this_type = self.get_type()
        data = self.get_data()
        if this_type == DataType.SIGNED:
            data = twos_comp(data,30)
        return ram_content(this_type,self.get_op(),self.get_addr1(),self.get_addr2(),data)

pc = Register("pc")
ci = Register("ci")

for i in range(5):
    ci.set_raw(ram.get_raw(pc.get_raw()))
    print(ci.get_contents())
    pc.increment()

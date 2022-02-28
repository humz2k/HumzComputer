from enum import IntEnum
from definitions import *
from op_map import OP
from ram_helpers import ram_content_helpers
from helpers import *

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

    def get_contents(self):

        this_type = ram_content_helpers.get_type(self.val)
        data = ram_content_helpers.get_data(self.val)

        addr1,addr1mode, addr2, addr2mode = 0,0,0,0

        if this_type == DataType.SIGNED:
            data = twos_comp(data,30)
        if this_type == DataType.INSTRUCTION:
            register_address_modes = [AddrModes.REGISTER_DIR,AddrModes.REGISTER_IDIR]
            addr1 = ram_content_helpers.get_addr1(self.val)
            addr1mode = ram_content_helpers.get_addr1mode(self.val)
            if addr1mode in register_address_modes:
                addr1 = REG(addr1)
            addr2 = ram_content_helpers.get_addr2(self.val)
            addr2mode = ram_content_helpers.get_addr2mode(self.val)
            if addr2mode in register_address_modes:
                addr2 = REG(addr2)
        return ram_content(this_type,ram_content_helpers.get_op(self.val),addr1,addr1mode,addr2,addr2mode,ram_content_helpers.get_long_addr(self.val),data)


class RegisterMemory:
    def __init__(self):
        self.pc = Register("pc")
        self.ci = Register("ci")
        self.mc = Register("mc")
        self.eq = Register("eq")

        self.register_list = [self.pc,self.ci,self.mc,self.eq]

        for i in "abcdefghijklmnop":
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

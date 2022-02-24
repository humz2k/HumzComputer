from definitions import *
from helpers import *
from op_map import OP
from registers import REG
from ram_helpers import ram_content_helpers

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

    def get_contents(self,addr):
        this_type = ram_content_helpers.get_type(self.ram[addr])
        op = 0
        long_addr = 0
        data = 0
        addr1 = 0
        addr1mode = 0
        addr2 = 0
        addr2mode = 0
        if this_type == DataType.INSTRUCTION:
            op = ram_content_helpers.get_op(self.ram[addr])
            long_addr = ram_content_helpers.get_long_addr(self.ram[addr])
            register_address_modes = [AddrModes.REGISTER_DIR,AddrModes.REGISTER_IDIR]
            addr1 = ram_content_helpers.get_addr1(self.ram[addr])
            addr1mode = ram_content_helpers.get_addr1mode(self.ram[addr])
            if addr1mode in register_address_modes:
                addr1 = REG(addr1)
            addr2 = ram_content_helpers.get_addr2(self.ram[addr])
            addr2mode = ram_content_helpers.get_addr2mode(self.ram[addr])
            if addr2mode in register_address_modes:
                addr2 = REG(addr2)
        else:
            data = ram_content_helpers.get_data(self.ram[addr])
            if this_type == DataType.SIGNED:
                data = twos_comp(data,30)
        return ram_content(this_type,op,addr1,addr1mode,addr2,addr2mode,long_addr,data)

    def clear_contents(self,addr):
        self.ram[addr] = 0

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

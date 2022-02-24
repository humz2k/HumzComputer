from enum import IntEnum

from definitions import *

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
            self.cpu.ram.set_contents(addr,ram_content(DataType.UNSIGNED,0,0,0,0,0,0,command.addr1))
        else:
            addr = command.addr2
            self.cpu.registers[addr].set_contents(ram_content(DataType.UNSIGNED,0,0,0,0,0,0,command.addr1))
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
            self.cpu.ram.set_contents(addr,contents)
        else:
            addr = command.addr1
            contents = self.cpu.registers[addr].get_contents()
            contents.data = 0
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

OP = OPMap().generate_enum_opmap()

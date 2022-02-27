from enum import IntEnum

from definitions import *

def _twos_comp(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

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

    def op_EOF(self,command):
        pass

OP = OPMap().generate_enum_opmap()

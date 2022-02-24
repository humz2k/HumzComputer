from enum import Enum, IntEnum
from dataclasses import dataclass
from definitions import *
from op_map import *
from registers import *
from helpers import *
from ram import *
import sys

class CPU:
    def __init__(self):
        self.ram = Ram()

        self.register_memory = RegisterMemory()
        self.register_memory.generate_enum_registermap()
        self.registers = self.register_memory.get_registers()

        self.op_map = OPMap(self)
        self.op_map.generate_enum_opmap()
        self.ops = self.op_map.get_ops()

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
        for i in range(5):
            self.step()

    def load(self,parsed):
        for i in parsed[0]:
            self.ram.set_contents(i[0],i[1])
        for idx,i in enumerate(parsed[1]):
            self.ram.set_contents(idx,i)
        self.register_memory.pc.set_raw(0)

class Parser:
    def __init__(self):
        self.const_addr = [OP.LDM,OP.INC,OP.DEC]
        self.addr = [OP.CLR,OP.ZER]
        self.addr_addr = [OP.CPY]

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

            if op in self.addr:
                addr1mode = AddrModes[command[1]]
                addr1 = command[2]
                if command[2] in consts:
                    addr1 = consts[command[2]]
                if addr1mode == AddrModes.MEMORY_DIR or addr1mode == AddrModes.MEMORY_IDIR:
                    addr1 = int(addr1)
                else:
                    addr1 = REG[addr1]
                outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0,0)

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
                outline = ram_content(type,op,addr1,addr1mode,addr2,addr2mode,0,0)

            parsed.append(outline)

        return stores,parsed

cpu = CPU()

parser = Parser()

parsed = parser.parse("input.ha")

cpu.load(parsed)

cpu.loop()

print(cpu.registers[REG.GA].get_contents())

cpu.ram.print(10,2)
cpu.ram.print_content(10,2)

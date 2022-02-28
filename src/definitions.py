from enum import IntEnum
from dataclasses import dataclass


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

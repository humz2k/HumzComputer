from definitions import *
from op_map import OP

class ram_content_helpers:
    def get_type(val):
        t = val
        t = t >> 30
        return DataType(t)

    def get_data(val):
        t = val
        return t & Masks.DATA

    def get_addr1(val):
        t = val
        t = t & Masks.ADDR1
        t = t >> 12
        return t

    def get_addr1mode(val):
        t = val
        t = t & Masks.ADDR1MODE
        t = t >> 22
        return AddrModes(t)

    def get_addr2(val):
        t = val
        t = t & Masks.ADDR2
        return t

    def get_addr2mode(val):
        t = val
        t = t & Masks.ADDR2MODE
        t = t >> 10
        return AddrModes(t)

    def get_long_addr(val):
        t = val
        t = t & Masks.LONGADDR
        return t

    def get_op(val):
        t = val
        t = t & Masks.OP
        t = t >> 24
        try:
            return OP(t)
        except:
            return t

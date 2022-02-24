from definitions import *
from op_map import OP

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

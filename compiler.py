from dataclasses import dataclass
from shunting import *

@dataclass
class var:
    type: str
    address: int
    val: int

class Compiler:
    def __init__(self,file):
        self.file = file
        with open(file,"r") as f:
            lines = f.read().split(";")
        out = []
        for i in lines:
            if "{" in i:
                out.append("{")
                out.append(i.split("{")[1])
            elif "}" in i:
                out.append(i.split("}")[0])
                out.append("}")

            else:
                out.append(i)
        out = [i.strip() for i in out]
        self.lines = [i for i in out if len(i) > 0]
        self.variables = {}
        self.mem_start = 512
        self.var_start = self.mem_start
        self.consts = 0
        self.compile()
        print(self.var_start - self.mem_start)

    def compile(self):
        self.find_variables()
        out = self.find_consts(self.lines)
        out = self.math(out)
        out = self.resolve_addresses(out)
        inst = self.pass_1(out)
        assigns = self.get_assigns()
        #print(self.variables)

    def add_variable(self,name,type,val,delta=1):
        if not name in self.variables:
            self.variables[name] = [var(type,self.var_start,val)]
            self.var_start += delta
            return
        self.variables[name].append(var(type,self.var_start,val))
        self.var_start += delta

    def find_variables(self):
        for i in [j.split(" ") for j in self.lines if j.split(" ")[0] in ["int","unsigned_int"]]:
            name = i[1]
            type = i[0]
            size = 1
            if "[" in name:
                size = int(i[1].split("[")[1][:-1])
                name = i[1].split("[")[0]
            val = 0
            vals = [0] * size
            if len(i) > 2:
                val = i[3]
                vals = []
                is_int = False
                try:
                    val = int(val)
                    is_int = True
                except:
                    pass
                if is_int:
                    vals = [int(i[3])] * size
                else:
                    if val[0] == '"' and val[-1] == '"':
                        for i in range(size):
                            vals.append(ord(val[1+i]))
                    elif val[0] == "[" and val[-1] == "]":
                        this_list = val[1:-1].split(",")
                        for i in range(size):
                            vals.append(int(this_list[i]))
            for i in range(size):
                self.add_variable(name,type,vals[i])

    def find_consts(self,inp):
        out = []
        for line in [j for j in inp if not j.split(" ")[0] in ["int","unsigned_int"]]:
            command = line.split(" ")
            for idx in range(len(command)):
                i = idx
                try:
                    test = int(command[i])
                    number = True
                except:
                    number = False
                if number:
                    type = "unsigned_int"
                    if int(command[i]) < 0:
                        type = "int"

                    self.add_variable("const"+str(self.consts),type,int(command[i]))
                    command[i] = "const"+str(self.consts)
                    self.consts += 1

            out.append(" ".join(command))

        return out

    def math(self,inp):
        out = []
        for line in inp:
            if len(line.split(" ")) > 2:
                #assignments
                if line.split(" ")[1] == "=":
                    expr = line.split(" ")[2:]
                    for i in range(len(expr)):
                        if "[" in expr[i]:
                            var = expr[i].split("[")[0]
                            offset = int(expr[i].split("[")[1][:-1])
                            expr[i] = str(self.variables[var][0].address + offset)
                    for i in range(len(expr)):
                        if expr[i] in self.variables:
                            expr[i] = str(self.variables[expr[i]][0].address)

                    out.append(" ".join(line.split(" ")[0:2] + expr))
                else:
                    out.append(line)
            else:
                out.append(line)

        return out

    def resolve_addresses(self,inp):
        out = []
        for line in inp:
            command = line.split(" ")
            for i in range(len(command)):
                var = command[i]
                offset = 0
                if "[" in command[i] and not '"' in command[i]:
                    var = command[i].split("[")[0]
                    offset = int(command[i].split("[")[1][:-1])
                if var in self.variables:
                    var = self.variables[var][0].address
                    command[i] = str(var + offset)
            out.append(" ".join(command))
        return out

    def get_assigns(self):
        out = []
        for i in self.variables.keys():
            for j in self.variables[i]:
                temp = "@" + str(j.address) + " " + ["UNSIGNED","SIGNED"][str(j.type) == "int"] + " " + str(j.val)
                out.append(temp)
        return out

    def pass_1(self,inp):
        out = []
        for line in inp:
            command = line.split(" ")
            if command[1] == "=":
                pass

compiler = Compiler("test.hl")

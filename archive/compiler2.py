from dataclasses import dataclass

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
        #print(self.var_start - self.mem_start)

    def compile(self):
        self.find_variables()
        out = self.find_consts(self.lines)
        assigns = self.get_assigns()
        out = self.pass_1(out)
        with open("out.ha", "w") as f:
            for i in assigns:
                f.write(i + "\n")
            for i in out:
                f.write(i + "\n")
            f.write("EOF\n")

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
                    if val[0] == '"':
                        val = " ".join(i[3:])
                        val = val.replace('\\n', '\n')
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
            is_string = False
            out_temp = []
            temp = ""
            for i in range(len(command)):
                if '"' in command[i]:
                    is_string = not is_string
                    if command[i].count('"') > 1:
                        out_temp.append(command[i])
                    else:
                        if is_string:
                            temp = ""
                        else:
                            temp += " " + command[i]
                            out_temp.append(temp[1:])
                if is_string:

                    temp += " " + command[i]
                elif not '"' in command[i]:
                    out_temp.append(command[i])

            command = out_temp

            for idx in range(len(command)):
                if "[" in command[idx]:
                    var = command[idx].split("[")[0]
                    offset = command[idx].split("[")[1][:-1]
                    try:
                        test = int(offset)
                        number = True
                    except:
                        number = False
                    if number:
                        type = "unsigned_int"
                        if int(offset) < 0:
                            type = "int"

                        self.add_variable("const" + str(self.consts), type, int(offset))
                        command[idx] = var + "[" + str("const" + str(self.consts)) + "]"
                        self.consts += 1
                elif '"' in command[idx] and len(command[idx]) == 3:
                    val = ord(command[idx][1:-1])
                    type = "unsigned_int"
                    self.add_variable("const"+str(self.consts),type,val)
                    command[idx] = "const"+str(self.consts)
                    self.consts += 1
                else:
                    try:
                        test = int(command[idx])
                        number = True
                    except:
                        number = False
                    if number:
                        type = "unsigned_int"
                        if int(command[idx]) < 0:
                            type = "int"

                        self.add_variable("const"+str(self.consts),type,int(command[idx]))
                        command[idx] = "const"+str(self.consts)
                        self.consts += 1

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
        ifs = []
        if_no = 0
        for line in inp:
            command = line.split(" ")
            if len(command) > 1:

                if command[0] == "_load":
                    file_to_load = command[1]
                    offset = None
                    if "[" in file_to_load:
                        offset = file_to_load.split("[")[1][:-1]
                        file_to_load = file_to_load.split("[")[0]
                    out.append("LDM " + str(self.variables[file_to_load][0].address) + " REGISTER_DIR GA")
                    if offset != None:
                        out.append("ADD MEMORY_DIR " + str(self.variables[offset][0].address) + " REGISTER_DIR GA")
                    out.append("LFM REGISTER_IDIR GA")

                if command[0] == "while":

                    if_one = "while" + str(if_no)
                    if_no += 1
                    if_two = "while" + str(if_no)
                    if_no += 1
                    if_three = "while" + str(if_no)
                    if_no += 1

                    first = command[1]
                    first_offset = None
                    if "[" in first:
                        first_offset = first.split("[")[1][:-1]
                        first = first.split("[")[0]

                    out.append("." + if_three)

                    out.append("LDM " + str(self.variables[first][0].address) + " REGISTER_DIR GA")
                    if first_offset != None:
                        out.append("ADD MEMORY_DIR " + str(self.variables[first_offset][0].address) + " REGISTER_DIR GA")

                    second = command[3]
                    second_offset = None
                    if "[" in second:
                        second_offset = second.split("[")[1][:-1]
                        second = second.split("[")[0]

                    out.append("LDM " + str(self.variables[second][0].address) + " REGISTER_DIR GB")
                    if second_offset != None:
                        out.append("ADD MEMORY_DIR " + str(self.variables[second_offset][0].address) + " REGISTER_DIR GB")

                    op = command[2]

                    out.append("COM REGISTER_IDIR GA REGISTER_IDIR GB")

                    if op == "==":
                        out.append("JME " + if_one)
                        out.append("JMP " + if_two)
                        out.append("." + if_one)
                        ifs += [["JMP " + if_three,"." + if_two]]

                    if op == "!=":
                        out.append("JME " + if_one)
                        ifs += [["JMP " + if_three,"." + if_one]]

                    if op == ">=":
                        out.append("JML " + if_one)
                        ifs += [["JMP " + if_three,"." + if_one]]

                    if op == "<=":
                        out.append("JMG " + if_one)
                        ifs += [["JMP " + if_three,"." + if_one]]

                    if op == ">":
                        out.append("JMG " + if_one)
                        out.append("JMP " + if_two)
                        out.append("." + if_one)
                        ifs += [["JMP " + if_three,"." + if_two]]

                    if op == "<":
                        out.append("JML " + if_one)
                        out.append("JMP " + if_two)
                        out.append("." + if_one)
                        ifs += [["JMP " + if_three,"." + if_two]]

                if command[0] == "if":
                    first = command[1]
                    first_offset = None
                    if "[" in first:
                        first_offset = first.split("[")[1][:-1]
                        first = first.split("[")[0]

                    out.append("LDM " + str(self.variables[first][0].address) + " REGISTER_DIR GA")
                    if first_offset != None:
                        out.append("ADD MEMORY_DIR " + str(self.variables[first_offset][0].address) + " REGISTER_DIR GA")

                    second = command[3]
                    second_offset = None
                    if "[" in second:
                        second_offset = second.split("[")[1][:-1]
                        second = second.split("[")[0]

                    out.append("LDM " + str(self.variables[second][0].address) + " REGISTER_DIR GB")
                    if second_offset != None:
                        out.append("ADD MEMORY_DIR " + str(self.variables[second_offset][0].address) + " REGISTER_DIR GB")

                    op = command[2]

                    out.append("COM REGISTER_IDIR GA REGISTER_IDIR GB")

                    if_one = "if" + str(if_no)
                    if_no += 1
                    if_two = "if" + str(if_no)
                    if_no += 1

                    if op == "==":
                        out.append("JME " + if_one)
                        out.append("JMP " + if_two)
                        out.append("." + if_one)
                        ifs += [["." + if_two]]

                    if op == "!=":
                        out.append("JME " + if_one)
                        ifs += [["." + if_one]]

                    if op == ">=":
                        out.append("JML " + if_one)
                        ifs += [["." + if_one]]

                    if op == "<=":
                        out.append("JMG " + if_one)
                        ifs += [["." + if_one]]

                    if op == ">":
                        out.append("JMG " + if_one)
                        out.append("JMP " + if_two)
                        out.append("." + if_one)
                        ifs += [["." + if_two]]

                    if op == "<":
                        out.append("JML " + if_one)
                        out.append("JMP " + if_two)
                        out.append("." + if_one)
                        ifs += [["." + if_two]]


                if command[0] == "input":

                    var = command[1]
                    if "[" in var:
                        var = command[1].split("[")[0]
                        offset = command[1].split("[")[1][:-1]
                        out.append("LDM " + str(self.variables[var][0].address) + " REGISTER_DIR GA")
                        out.append("ADD MEMORY_IDIR " + str(self.variables[offset][0].address) + " REGISTER_DIR GA")
                        out.append("INP REGISTER_IDIR GA")
                    else:
                        out.append("INP MEMORY_DIR " + str(self.variables[var][0].address))

                if command[0] == "push":
                    to_push = line.split("push ")[1]
                    if '"' in to_push:
                        to_push = to_push.replace('\\n', '\n')
                        for i in to_push[1:-1]:
                            out.append("LDM " + str(ord(i)) + " REGISTER_DIR GA")
                            out.append("PSH REGISTER_DIR GA")
                    else:
                        if "[" in to_push:
                            var = to_push.split("[")[0]
                            offset = to_push.split("[")[1][:-1]
                            out.append("LDM " + str(self.variables[var][0].address) + " REGISTER_DIR GA")
                            out.append("ADD MEMORY_IDIR " + str(self.variables[offset][0].address) + " REGISTER_DIR GA")
                            out.append("PSH REGISTER_IDIR GA")
                        else:
                            for i in self.variables[to_push]:
                                out.append("PSH MEMORY_DIR " + str(i.address))

                if command[0] == "push_int":
                    to_push = line.split("push_int ")[1]
                    if '"' in to_push:
                        to_push = to_push.replace('\\n', '\n')
                        for i in to_push[1:-1]:
                            out.append("LDM " + str(ord(i)) + " REGISTER_DIR GA")
                            out.append("PSI REGISTER_DIR GA")
                    else:
                        if "[" in to_push:
                            var = to_push.split("[")[0]
                            offset = to_push.split("[")[1][:-1]
                            out.append("LDM " + str(self.variables[var][0].address) + " REGISTER_DIR GA")
                            out.append("ADD MEMORY_IDIR " + str(self.variables[offset][0].address) + " REGISTER_DIR GA")
                            out.append("PSI REGISTER_IDIR GA")
                        else:
                            for i in self.variables[to_push]:
                                out.append("PSI MEMORY_DIR " + str(i.address))

                if command[1] == "=":
                    if len(command) > 3:
                        first = command[0]
                        first_offset = None
                        if "[" in first:
                            first_offset = first.split("[")[1][:-1]
                            first = first.split("[")[0]

                        out.append("LDM " + str(self.variables[first][0].address) + " REGISTER_DIR GA")
                        if first_offset != None:
                            out.append("ADD MEMORY_DIR " + str(self.variables[first_offset][0].address) + " REGISTER_DIR GA")

                        second = command[2]
                        second_offset = None
                        if "[" in second:
                            second_offset = second.split("[")[1][:-1]
                            second = second.split("[")[0]

                        out.append("LDM " + str(self.variables[second][0].address) + " REGISTER_DIR GB")
                        if second_offset != None:
                            out.append("ADD MEMORY_DIR " + str(self.variables[second_offset][0].address) + " REGISTER_DIR GB")

                        third = command[4]
                        third_offset = None
                        if "[" in third:
                            third_offset = third.split("[")[1][:-1]
                            third = third.split("[")[0]

                        out.append("LDM " + str(self.variables[third][0].address) + " REGISTER_DIR GC")
                        if third_offset != None:
                            out.append("ADD MEMORY_DIR " + str(self.variables[third_offset][0].address) + " REGISTER_DIR GC")

                        out.append("CPY REGISTER_IDIR GB REGISTER_DIR GD")
                        out.append("CPY REGISTER_IDIR GC REGISTER_DIR GE")
                        out.append("ZER REGISTER_IDIR GA")
                        out.append("ADD REGISTER_DIR GD REGISTER_IDIR GA")
                        op = command[3]
                        if op == "+":
                            out.append("ADD REGISTER_DIR GE REGISTER_IDIR GA")
                        if op == "-":
                            out.append("SUB REGISTER_DIR GE REGISTER_IDIR GA")
                        if op == "*":
                            out.append("MUL REGISTER_DIR GE REGISTER_IDIR GA")
                        if op == "/":
                            out.append("DIV REGISTER_DIR GE REGISTER_IDIR GA")
                    else:
                        first = command[0]
                        first_offset = None
                        if "[" in first:
                            first_offset = first.split("[")[1][:-1]
                            first = first.split("[")[0]

                        out.append("LDM " + str(self.variables[first][0].address) + " REGISTER_DIR GA")
                        if first_offset != None:
                            out.append("ADD MEMORY_DIR " + str(self.variables[first_offset][0].address) + " REGISTER_DIR GA")

                        second = command[2]
                        second_offset = None
                        if "[" in second:
                            second_offset = second.split("[")[1][:-1]
                            second = second.split("[")[0]

                        out.append("LDM " + str(self.variables[second][0].address) + " REGISTER_DIR GB")
                        if second_offset != None:
                            out.append("ADD MEMORY_DIR " + str(self.variables[second_offset][0].address) + " REGISTER_DIR GB")

                        out.append("ZER REGISTER_IDIR GA")
                        out.append("ADD REGISTER_IDIR GB REGISTER_IDIR GA")
            else:
                if command[0] == "pop":
                    out.append("POP")
                if command[0] == "flip":
                    out.append("FLP")
                if command[0] == "}":
                    for t in ifs.pop(-1):
                        out.append(t)
        return out

if __name__ == "__main__":
    compiler = Compiler("programs/fib.hl")

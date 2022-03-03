from dataclasses import dataclass

@dataclass
class var:
    type: str
    name: str
    addr_offset: int
    val: int

def split_var(var):
    name = var
    offset = None
    pointer = False
    if "[" in var:
        name = var.split("[")[0]
        offset = var.split("[")[1][:-1]
    if "&" in name:
        name = name[1:]
        pointer = True
    return name,offset,pointer

class Compiler:
    def __init__(self,file):
        self.file = file
        self.lines = self.load_file()
        self.variables = {}
        self.current_var = 0
        self.consts = 0
        self.mem_used = 0
        self.malloc_start = 0
        self.compiled = self.compile()


    def compile(self):
        self.find_variables()
        out = self.split_by(self.lines)
        out = self.find_replace_const(out)
        out = self.translate(out)
        translate_length = len(out) + 2
        malloc_start = 0
        if len(self.variables.keys()) > 0:
            malloc_start = self.variables[list(self.variables.keys())[-1]][-1].addr_offset + translate_length + 1
        else:
            malloc_start = translate_length + 1
        self.malloc_start = malloc_start

        out = self.do_offsets(translate_length) + self.do_assigns() + ["LDM " + str(malloc_start) + " REGISTER_DIR MC"] + out + ["EOF"]
        return out

    def load_file(self):
        with open(self.file,"r") as f:
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
        return [i for i in out if len(i) > 0]

    def add_variable(self,name,type,val,delta=1):
        if not name in self.variables:
            self.variables[name] = [var(type,"var"+str(self.current_var),self.current_var,val)]
        else:
            self.variables[name].append(var(type,"var"+str(self.current_var),self.current_var,val))
        self.current_var += delta

    def find_variables(self):
        for i in  [j.split(" ") for j in self.lines if j.split(" ")[0] in ["int","unsigned_int"]]: #only look where variable declaration

            type = i[0] #Get type

            name,size,ignore = split_var(i[1]) #get name and size

            if size == None:
                size = 1

            size = int(size)

            vals = [0] * size #zero if no vals

            if len(i) > 2: #if there are vals

                val = i[3] #get the vals
                vals = []
                is_int = False
                try:
                    val = int(val)
                    is_int = True
                except:
                    pass
                if is_int:
                    vals = [val] * size
                else:
                    if val[0] == '"': #can probably throw errors here
                        val = " ".join(i[3:])
                        val = val.replace('\\n','\n')
                        for i in range(size):
                            vals.append(ord(val[1+i]))

                    elif val[0] == "[" and val[-1] == "]":
                        this_list = val[1:-1].split(",")
                        for i in range(size):
                            vals.append(int(this_list[i]))
            for j in range(size):
                self.add_variable(name,type,vals[j])

    def split_by(self,inp):
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
            for i in range(len(command)):
                command[i] = command[i].replace('\\n','\n')
            out.append(command)
        return out;

    def find_replace_const(self,inp):
        #this like modifies the list in place but idc
        out = []
        for line in range(len(inp)):
            command = inp[line]
            for idx in range(len(command)):
                if "[" in command[idx]:
                    name,offset,malloc = split_var(command[idx])
                    if malloc:
                        name = "&" + name
                    try:
                        test = int(offset)
                        number = True
                    except:
                        number = False
                    if number:
                        type = "unsigned_int"
                        if test < 0:
                            type = "int"
                        self.add_variable("const" + str(self.consts),type,int(offset))
                        command[idx] = name + "[" + str("const" + str(self.consts)) + "]"
                        self.consts += 1
                elif '"' in command[idx] and len(command[idx]) == 3:
                    val = ord(command[idx][1:-1])
                    type = "unsigned_int"
                    self.add_variable("const" + str(self.consts),type,val)
                    command[idx] = "const" + str(self.consts)
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
                        self.add_variable("const" + str(self.consts),type,int(command[idx]))
                        command[idx] = "const" + str(self.consts)
                        self.consts += 1

            out.append(command)
        return out

    def resolve_var(self,var,register_dest):
        out = []
        name,offset,pointer = split_var(var)
        if pointer:
            out.append("CPY MEMORY_DIR " + str(self.variables[name][0].name + " REGISTER_DIR " + register_dest))
        else:
            out.append("LDM " + str(self.variables[name][0].name) + " REGISTER_DIR " + register_dest)

        if offset != None:
            if "&" in offset:
                out.append("ADD MEMORY_IDIR " + str(self.variables[offset][0].name) + " REGISTER_DIR " + register_dest)
            else:
                out.append("ADD MEMORY_DIR " + str(self.variables[offset][0].name) + " REGISTER_DIR " + register_dest)
        return out

    def do_offsets(self,offset):
        out = []
        for i in self.variables.keys():
            for j in self.variables[i]:
                temp = "#" + str(j.name) + " " + str(j.addr_offset + offset)
                out.append(temp)
        return out

    def do_assigns(self):
        out = []
        for i in self.variables.keys():
            for j in self.variables[i]:
                temp = "@" + str(j.name) + " " + ["UNSIGNED","SIGNED"][str(j.type) == "int"] + " " + str(j.val)
                out.append(temp)
        return out

    def translate(self,inp):
        out = []
        jumps = []
        jump_no = 0

        for command in inp:
            if len(command) > 1:

                if command[0] == "malloc":
                    out += self.resolve_var(command[1],"GA")
                    out += self.resolve_var(command[2],"GB")
                    out.append("ZER REGISTER_IDIR GA")
                    out.append("ADD REGISTER_DIR MC REGISTER_IDIR GA")
                    out.append("ADD REGISTER_IDIR GB REGISTER_DIR MC")

                elif command[0] == "_load":
                    out += self.resolve_var(command[1],"GA")
                    out.append("LFM REGISTER_IDIR GA")

                elif command[0] == "while":

                    jump_one = "while" + str(jump_no)
                    jump_no += 1
                    jump_two = "while" + str(jump_no)
                    jump_no += 1
                    jump_three = "while" + str(jump_no)
                    jump_no += 1

                    out.append("." + jump_three)

                    out += self.resolve_var(command[1],"GA")
                    out += self.resolve_var(command[3],"GB")

                    op = command[2]

                    out.append("COM REGISTER_IDIR GA REGISTER_IDIR GB")

                    if op == "==":
                        out.append("JME " + jump_one)
                        out.append("JMP " + jump_two)
                        out.append("." + jump_one)
                        jumps += [["JMP " + jump_three,"." + jump_two]]

                    if op == "!=":
                        out.append("JME " + jump_one)
                        jumps += [["JMP " + jump_three,"." + jump_one]]

                    if op == ">=":
                        out.append("JML " + jump_one)
                        jumps += [["JMP " + jump_three,"." + jump_one]]

                    if op == "<=":
                        out.append("JMG " + jump_one)
                        jumps += [["JMP " + jump_three,"." + jump_one]]

                    if op == ">":
                        out.append("JMG " + jump_one)
                        out.append("JMP " + jump_two)
                        out.append("." + jump_one)
                        jumps += [["JMP " + jump_three,"." + jump_two]]

                    if op == "<":
                        out.append("JML " + jump_one)
                        out.append("JMP " + jump_two)
                        out.append("." + jump_one)
                        jumps += [["JMP " + jump_three,"." + jump_two]]

                elif command[0] == "if":
                    jump_one = "if" + str(jump_no)
                    jump_no += 1
                    jump_two = "if" + str(jump_no)
                    jump_no += 1

                    out += self.resolve_var(command[1],"GA")
                    out += self.resolve_var(command[3],"GB")

                    op = command[2]

                    out.append("COM REGISTER_IDIR GA REGISTER_IDIR GB")

                    if op == "==":
                        out.append("JME " + jump_one)
                        out.append("JMP " + jump_two)
                        out.append("." + jump_one)
                        jumps += [["." + jump_two]]

                    if op == "!=":
                        out.append("JME " + jump_one)
                        jumps += [["." + jump_one]]

                    if op == ">=":
                        out.append("JML " + jump_one)
                        jumps += [["." + jump_one]]

                    if op == "<=":
                        out.append("JMG " + jump_one)
                        jumps += [["." + jump_one]]

                    if op == ">":
                        out.append("JMG " + jump_one)
                        out.append("JMP " + jump_two)
                        out.append("." + jump_one)
                        jumps += [["." + jump_two]]

                    if op == "<":
                        out.append("JML " + jump_one)
                        out.append("JMP " + jump_two)
                        out.append("." + jump_one)
                        jumps += [["." + jump_two]]

                elif command[0] == "input":
                    out += self.resolve_var(command[1],"GA")
                    out.append("INP REGISTER_IDIR GA")

                elif command[0] == "push":
                    if '"' in command[1]:
                        for i in command[1][1:-1]:
                            out.append("LDM " + str(ord(i)) + " REGISTER_DIR GA")
                            out.append("PSH REGISTER_DIR GA")
                    else:
                        if "[" in command[1] or "&" in command[1]:
                            out += self.resolve_var(command[1],"GA")
                            out.append("PSH REGISTER_IDIR GA")
                        else:
                            for i in self.variables[command[1]]:
                                out.append("PSH MEMORY_DIR " + str(i.name))

                elif command[0] == "push_int":
                    if "[" in command[1] or "&" in command[1]:
                        out += self.resolve_var(command[1],"GA")
                        out.append("PSI REGISTER_IDIR GA")
                    else:
                        if len(self.variables[command[1]]) > 1:
                            out.append("LDM " + str(ord("[")) + " REGISTER_DIR GA")
                            out.append("PSH REGISTER_DIR GA")
                            out.append("LDM " + str(ord(",")) + " REGISTER_DIR GA")
                            for i in self.variables[command[1]]:
                                out.append("PSI MEMORY_DIR " + str(i.name))
                                out.append("PSH REGISTER_DIR GA")
                            out.append("POP")
                            out.append("LDM " + str(ord("]")) + " REGISTER_DIR GA")
                            out.append("PSH REGISTER_DIR GA")
                        else:
                            out.append("PSI MEMORY_DIR " + str(self.variables[command[1]][0].name))

                elif command[1] == "=":
                    if len(command) > 3:
                        out += self.resolve_var(command[0],"GA")
                        out += self.resolve_var(command[2],"GB")
                        out += self.resolve_var(command[4],"GC")

                        op = command[3]

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
                        out += self.resolve_var(command[0],"GA")
                        out += self.resolve_var(command[2],"GB")
                        out.append("ZER REGISTER_IDIR GA")
                        out.append("ADD REGISTER_IDIR GB REGISTER_IDIR GA")
            else:
                if command[0] == "pop":
                    out.append("POP")
                if command[0] == "flip":
                    out.append("FLP")
                if command[0] == "}":
                    for t in jumps.pop(-1):
                        out.append(t)

        return out


if __name__ == "__main__":
    compiler = Compiler("programs/line.hl")

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
        print(self.var_start - self.mem_start)

    def compile(self):
        self.find_variables()
        self.find_lists()
        out = self.first_pass()
        print(out)

    def add_variable(self,name,type,val,delta=1):
        self.variables[name] = var(type,self.var_start,val)
        self.var_start += delta

    def find_variables(self):
        for i in [j.split(" ") for j in self.lines if j.split(" ")[0] == "var"]:
            self.add_variable(i[2],i[1],0)

    def find_lists(self):
        for i in [j.split(" ") for j in self.lines if j.split(" ")[0] == "list"]:
            type = i[1]
            name = i[2]
            size = int(i[4])
            self.add_variable(name,type,0,size)

    def first_pass(self):
        out = []
        for line in [j for j in self.lines if not j.split(" ")[0] in ["var","list"]]:
            command = line.split(" ")
            for idx in range(len(command)):
                i = idx + 3
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

compiler = Compiler("test.hl")

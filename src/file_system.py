from memory import *

filename = "files"

class Files:
    def __init__(self,filename = filename,size=250000):
        self.filename = filename
        self.data = []
        self.size = size
        self.read()

    def read(self):
        with open(self.filename, "rb") as f:
            for i in range(self.size):
                piece = f.read(5)
                temp = int.from_bytes(piece,'big')
                if temp == 0:
                    break
                self.data.append(temp)

    def save(self):
        with open(self.filename, "wb") as f:
            for i in self.data:
                bytes = i.to_bytes(5,'big')
                f.write(bytes)

    def add(self,t):
        self.data.append(t)

#print(get_bytes(ram_content(DataType.UNSIGNED,0,0,0,0,0,0,10)))

import os

def clearConsole():
    command = 'clear'
    if os.name in ('nt','dos'):
        command = 'cls'
    os.system(command)

class screen:
    def __init__(self,size=[50,50]):
        self.size=[50,50]
        self.screen = [""]

    def push(self,inp):
        char = chr(inp)
        if char == "\n":
            self.screen.append("")
            return
        self.screen[-1] += char

    def flip(self):
        clearConsole()
        for i in self.screen[-self.size[1]:]:
            if len(i) > self.size[0]:
                print(i[:50])
            else:
                print(i)

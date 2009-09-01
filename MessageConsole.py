from Tkinter import *

class MessageConsole:
    def __init__(self,optimus):
        self.optimus = optimus
        self.root = Tk()
        t = Text(self.root)
        scroll = Scrollbar(self.root,command=t.yview)
        t.configure(yscrollcommand=scroll.set)
        t.tag_configure('debug', font=('Courier New',10))
        t.tag_configure('error', foreground='red')
        self.root.bind('<Destroy>',self.destroy)
        for (m,type) in self.optimus.messages:
            t.insert(END,str(m) + "\n",type)
        t.pack(side=LEFT)
        scroll.pack(side=RIGHT,fill=Y)
        self.t = t
        self.t.see(END)
    def add_message(self,message,type):
        self.t.insert(END,str(message) + "\n")
        self.t.see(END)
    def destroy(self,event):
        self.optimus.console = None


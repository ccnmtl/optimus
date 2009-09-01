from Tkinter import *
from tkSimpleDialog import Dialog
from OptimusEvent import *

fed = None

class FedMenu:
    """a Tk based interface for modifying federate attributes
    at runtime"""

    def __init__(self,optimus):
        self.optimus = optimus
        self.root = Tk()
        f1 = Frame(self.root)

        for f in optimus.federates:
            opener = FedOpener(self,f)
            b = Button(f1,text=f.name,command=opener.open)
            b.pack(fill=X)
        f1.pack()
        self.root.mainloop()
        
class FedOpener:
    def __init__(self,root,federate):
        self.optimus = root
        self.federate = federate
        self.root = root.parent

    def open(self):
        global fed
        fed = self.federate
        AttMenu(self.root)
        
    def add_event_handler(self):
        global fed
        fed = self.federate
        NewHandlerEditor(self.root)

    def open_handlers(self):
        global fed
        fed = self.federate
        HandlerMenu(self.root)

    def unload(self):
        self.optimus.unload_federate(self.federate.name)

class NewHandlerEditor(Dialog):
    def body(self,master):
        self.title("OPTIMUS: Add event handler")
        self.federate = fed

        Label(master, text="Event:").grid(row=0,sticky=NW)
        Label(master, text="Code:").grid(row=1,sticky=NW)

        self.e = Entry(master)
        self.f = Frame(master)
        self.t = Text(self.f)
        self.t.pack(side=LEFT)
        self.t.tag_configure("code",font=("Courier New",10))
        scroll = Scrollbar(self.f,command=self.t.yview)
        self.t.configure(yscrollcommand=scroll.set)
        scroll.pack(side=LEFT,fill=Y)

        self.e.grid(row=0,column=1,sticky=W)
        self.f.grid(row=1,column=1,sticky=W)

        self.event_var = StringVar()
        self.event_var.set("")

        self.e["textvariable"] = self.event_var

    def apply(self):
        code = self.t.get(1.0,END)
        event = self.event_var.get()
        self.federate.add_new_event_handler(event,code)

        self.federate.event_handler_menu.add_command(label=event,command=self.federate.event_handlers[event].edit)


class AttMenu(Dialog):
    """a Tk based interface for modifying federate attributes
    at runtime"""

    def body(self,master):
        self.title("attributes")
        self.vars = []
        row = 0
        def cmpbyorder(x,y):
            if x.order > y.order:
                return 1
            elif x.order < y.order:
                return -1
            else:
                return 0
        attributes = fed.attributes.values()
        attributes.sort(cmpbyorder)
        for att in attributes:
            Label(master, text=att.label).grid(row=row,sticky=NE)
            if att.type == 'boolean':
                v = BooleanVar()
                v.set(att.value)
                self.vars.append(v)
                c = Checkbutton(master,variable=self.vars[row])
                c.grid(row=row,column=1,stick=W)
            elif att.type == 'integer':
                v = IntVar()
                v.set(att.value)
                self.vars.append(v)
                if att.valid_values == []:
                    entry = Entry(master)
                    entry["textvariable"] = self.vars[row]
                    entry.grid(row=row,column=1,stick=W)
                else:
                    f = Frame(master)
                    for value,label in att.valid_values:
                        Radiobutton(f,text=label,value=value,variable=self.vars[row]).pack(anchor=W)
                    f.grid(row=row,column=1,stick=W)

            elif att.type == 'float':
                v = DoubleVar()
                v.set(att.value)
                self.vars.append(v)
                if att.valid_values == []:
                    entry = Entry(master)
                    entry["textvariable"] = self.vars[row]
                    entry.grid(row=row,column=1,stick=W)
                else:
                    f = Frame(master)
                    for value,label in att.valid_values:
                        Radiobutton(f,text=label,value=value,variable=self.vars[row]).pack(anchor=W)
                    f.grid(row=row,column=1,stick=W)
            else:
                v = StringVar()
                v.set(att.value)
                self.vars.append(v)
                if att.valid_values == []:
                    entry = Entry(master)
                    entry.grid(row=row,column=1,stick=W)
                    entry["textvariable"] = self.vars[row]
                else:
                    f = Frame(master)
                    for value,label in att.valid_values:
                        Radiobutton(f,text=label,value=value,variable=self.vars[row]).pack(anchor=W)
                    f.grid(row=row,column=1,sticky=W)
            row = row + 1

    def apply(self):
        i = 0
        for a in fed.attributes:
            att = fed.attributes[a]
            print "updating %s" % fed.attributes[a].varname
            fed.attributes[a].set(self.vars[att.order].get())
            code = "fed.%s = fed.attributes[a].get()"  % fed.attributes[a].varname
            exec code
            i = i + 1

        

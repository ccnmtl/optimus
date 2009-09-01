from Tkinter import *

class EventHandler:
    def __init__(self,federate,event,code,filename=None):
        self.event = event
        self.federate = federate
        self.source_code = code
        self.filename = filename
        try:
            self.code = compile(code,"<string>","exec")
        except SyntaxError, x:
            self.federate.error("Error loading federate %s" % self.federate.name)
            self.federate.error("in %s event handler" % self.event)
            if filename != None:
                self.federate.error("File: %s" % self.filename)
            self.federate.error("line: %d" % x[1][1])
            self.federate.error("Error: %s" % x[0])

    def as_xml(self):
        from xml.sax import saxutils
        xml = """<event type=%s>\n""" % saxutils.quoteattr(self.event)
        xml += saxutils.escape(self.source_code)
        xml += """</event>\n"""
        return xml

    def edit(self):
        self.root = Tk()
        self.root.title("OPTIMUS: Edit event handler for %s" % self.event)
        outer = Frame(self.root)
        Label(outer,text=self.event).pack()
        f = Frame(outer)
        self.t = Text(f)
        self.t.pack(side=LEFT)
        self.t.tag_configure("code",font=("Courier New",10))
        self.t.insert(END,self.source_code,"code")
        scroll = Scrollbar(f,command=self.t.yview)
        self.t.configure(yscrollcommand=scroll.set)
        scroll.pack(side=LEFT,fill=Y)
        f.pack()
        buttons = Frame(outer)
        save_button = Button(buttons,text="save",command=self.save)
        cancel_button = Button(buttons,text="cancel",command=self.quit)
        save_button.pack(side=LEFT)
        cancel_button.pack(side=LEFT)
        buttons.pack()
        outer.pack()
        self.root.mainloop()

    def save(self):
        self.source_code = self.t.get(1.0,END)
        try:
            self.code = compile(self.source_code,'<string>','exec')
            self.root.destroy()
        except:
            self.federate.error("syntax error in %s handler. not saving changes." % self.event)

    def quit(self):
        self.root.destroy()



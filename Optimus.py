#!/usr/bin/python

import re,sys,os

import Image

from Tkinter import *
from tkFileDialog import askopenfilename,asksaveasfilename
from tkSimpleDialog import askstring,askinteger
from Numeric import *

from Organizer import Organizer
from Federate import Federate
from OptimusEvent import OptimusEvent
from FedMenu import FedOpener,AttMenu
from MessageConsole import *
import urllib
from xml.dom.minidom import Document, parseString

WIDTH = 640
HEIGHT = 480

def debug(message):
    if __debug__:
        print message

# -----------------------------------------------------------------------------------
def main():
    root = Tk()
    optimus = Optimus(root)
    optimus.organizer.generate_event(OptimusEvent("display",{}))
    root.mainloop()

def array2image(a):
    if a.typecode() == UnsignedInt8:
        mode = "L"
    elif a.typecode() == Float32:
        mode = "F"
    else:
        raise ValueError, "unsupported image mode"
    return Image.fromstring(mode, (a.shape[1], a.shape[0]), a.tostring())

class Optimus:
    def __init__(self,parent):
        self.parent = parent
        self.parent.title('OPTIMUS')
        self.messages = []
        self.console = None
        self.debug("creating new Optimus object")

        menubar = Menu(self.parent)
        filemenu = Menu(menubar,tearoff=0)

        filemenu.add_command(label="Exit",command=self.parent.quit)
        menubar.add_cascade(label="File",menu=filemenu)

        federatemenu = Menu(menubar,tearoff=0)
        federatemenu.add_command(label="load federate",command=self.load_federate)
        menubar.add_cascade(label="Federates",menu=federatemenu)

        simulationmenu = Menu(menubar,tearoff=0)
        simulationmenu.add_command(label="load simulation",command=self.load_simulation)
        simulationmenu.add_command(label="save as simulation",command=self.save_as_simulation)
        menubar.add_cascade(label="Simulations",menu=simulationmenu)

        scenariomenu = Menu(menubar,tearoff=0)
        scenariomenu.add_command(label="load scenario",command=self.load_scenario)
        scenariomenu.add_command(label="save as scenario",command=self.save_as_scenario)
        menubar.add_cascade(label="Scenarios",menu=scenariomenu)

        self.parent.config(menu=menubar)
        
        outer_frame = Frame(self.parent)
        top_frame   = Frame(outer_frame)
        self.canvas = Canvas(top_frame,
                             width  = WIDTH,
                             height = HEIGHT)

        self.canvas.pack(side=LEFT)
        self.canvas.bind("<Button-1>",       self.canvas_click)
        self.canvas.bind("<ButtonRelease-1>",self.canvas_mouseup)
        self.canvas.bind("<B1-Motion>",      self.canvas_mousemove)
        top_frame.pack()


        buttons = Frame(outer_frame)
        self.n_steps_button = Button(buttons,text="run N steps",command=self.run_n_steps)
        self.start_button   = Button(buttons,text="start",command=self.start)
        self.stop_button    = Button(buttons,text="stop", command=self.stop)
        self.step_button    = Button(buttons,text="step", command=self.step)
        self.reset_button   = Button(buttons,text="reset",command=self.reset)
        self.console_button = Button(buttons,text="console",command=self.launch_console)

        outer_frame.pack()
        self.canvas.pack()
        buttons.pack()
        self.n_steps_button.pack(side=LEFT)
        self.start_button.pack(side=LEFT)
        self.stop_button.pack( side=LEFT)
        self.step_button.pack( side=LEFT)
        self.reset_button.pack(side=LEFT)
        self.console_button.pack(side=LEFT)

        self.organizer = Organizer(self)

        self.federates = []
        self.federatemenu = federatemenu
        
        self.ticking = 0
        self.tickDelay = 10
        self.steps = -1

    def debug(self,message):
        self.add_message(message,"debug")
    def error(self,message):
        self.add_message(message,"error")
        self.set_error_status()
    def warn(self,message):
        self.add_message(message,"warn")
    def add_message(self,message,type):
        self.messages.append((message,type))
        if self.console != None:
            self.console.add_message(message,type)
            
    def step(self):
        """ generates a single tick event"""
        self.debug(" --- tick --- ")
        self.organizer.generate_event(OptimusEvent("tick",{}))
        self.organizer.generate_event(OptimusEvent("display",{}))

    def start(self):
        """ generates tick events until the user hits stop"""
        self.stop()
        self.ticking = 1
        self.step()
        self.tickId = self.parent.after(self.tickDelay, self.start)

    def stop(self):
        """makes it stop generating tick events"""
        if self.ticking:
            self.parent.after_cancel(self.tickId)
            self.ticking = 0

    def run_n_steps(self):
        if self.steps == -1:
            self.steps = askinteger("how many steps?","steps:")
        if self.steps == 0:
            self.stop()
            self.steps = -1
        else:
            self.stop()
            self.step()
            self.steps = self.steps - 1
            self.tickId = self.parent.after(self.tickDelay,
                    self.run_n_steps)


    def reset(self):
        self.organizer.generate_event(OptimusEvent("unload",{}))
        self.organizer.generate_event(OptimusEvent("init",{}))
        self.organizer.generate_event(OptimusEvent("display",{}))
    def launch_console(self):
        self.console = MessageConsole(self)
        self.clear_error_status()
    def clear_error_status(self):
        self.console_button.configure(foreground='black')
    def set_error_status(self):
        self.console_button.configure(foreground='red')

    def canvas_click(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        pos = (x,y)
        self.organizer.generate_event(OptimusEvent("mousedown",{"pos" : pos}))
        self.organizer.generate_event(OptimusEvent("display",{}))

    def canvas_mouseup(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        pos = (x,y)
        self.organizer.generate_event(OptimusEvent("mouseup",{"pos" : pos}))
        self.organizer.generate_event(OptimusEvent("display",{}))

    def canvas_mousemove(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        pos = (x,y)
        self.organizer.generate_event(OptimusEvent("mousemove",{"pos" : pos}))

    def add_federate(self,filename):
        self.debug("loading new federate from %s" % filename)
        f = Federate(self.organizer,self.canvas,filename)
        try:
            self.federates.append(f)
        except:
            self.error("problem loading federate from %s" % filename)
            return
        opener = FedOpener(self,f)
        m = Menu(self.federatemenu,tearoff=0)
        m.add_command(label="edit attributes",command=opener.open)
        m2 = Menu(m,tearoff=0)
        for k in f.event_handlers.keys():
            e = f.event_handlers[k]
            m2.add_command(label=k,command=e.edit)
        m.add_cascade(label="event handlers",menu=m2)
        m.add_command(label="add event handler",command=opener.add_event_handler)
        m.add_command(label="unload federate",command=opener.unload)
        m.add_command(label="save as...",command=f.save_xml)
        f.event_handler_menu = m2
        self.federatemenu.add_cascade(label=f.name,menu=m)

    def load_federate(self):
        filename = askopenfilename(filetypes=[("XML documents","*.xml"),("All files","*")])
        if filename == "":
            return
        try:
            self.add_federate(filename)
        except:
            self.error("couldn't load federate from %s" % filename)
        
    def unload_federate(self,federate):
        self.debug("unloading federate")
        fed_idx = None
        f = None
        for i in range(len(self.federates)):
            fed = self.federates[i]
            if fed.name == federate:
                fed.handle_event(OptimusEvent("unload",{}))
                fed_idx = i
                f = fed
                break
        self.federates.remove(f)
        self.organizer.unregister(f)
        self.federatemenu.delete(fed_idx + 1)

    def unload_all_federates(self):
        i = 1
        for f in self.federates:
            f.handle_event(OptimusEvent("unload",{}))
            self.organizer.unregister(f)
            self.federatemenu.delete(i)
            i += 1
        self.federates = []

    def load_simulation(self):
        # get the filename
        filename = askopenfilename(filetypes=[("XML documents","*.xml"),("All files","*")])
        if filename == "":
            return
        # clear out the old federates
        self.unload_all_federates()
        # load the new ones
        try:
            self.add_simulation("file:" + filename)
        except:
            self.error("couldn't load simulation from %s" % filename)

    def add_simulation(self,filename):
        self.debug("adding simulation from %s" % filename)
        # parse the xml file and set all our attributes
        parts = filename.split("/")
        uri_base = "/".join(parts[:-1])
        try:
            xmlstring = "".join(urllib.urlopen(filename).readlines())
        except:
            self.error("couldn't open simulation file: %s" % filename)
        try:
            doc = parseString(xmlstring)
        except:
            self.error("%s isn't well-formed XML" % filename)

        base_path = uri_base[5:]
        sys.path.append(base_path.encode())
        self.debug(base_path)

        # 'federate' should be the root element of the document
        root           = doc.getElementsByTagName('simulation')[0]
        self.name      = root.getAttribute('name')

        self.parent.title("OPTIMUS simulation: " + self.name)

        federates      = root.getElementsByTagName('federates')[0]
        feds = federates.getElementsByTagName('federate')
        for federate in feds:
            file = federate.getAttribute("file")
            if not re.match("(http:|\/|file:)",file):
                # the uri appears to be relative, so we
                # append it to the base uri
                file = "/".join([uri_base,file])
            self.add_federate(file)

        
    def save_as_simulation(self):
        sim_name = askstring("Simulation Name","enter a name for the simulation:")
        if sim_name == "":
            return
        filename = asksaveasfilename(filetypes=[("XML documents","*.xml"),("All files","*")])

        file = open(filename,'w')
        file.write("""<?xml version="1.0"?>\n""")
        file.write("""<simulation name="%s">\n""" % sim_name)
        file.write("""  <federates>\n""")
        cwd = os.getcwd()
        sep = os.sep
        filename = filename.replace(cwd + sep,'')
        sim_parts = filename.split(sep)
        for f in self.federates:
            (protocol,path) = urllib.splittype(f.file)
            parts = path.split(sep)
            rem = 0
            print parts
            print sim_parts
            for i in range(len(sim_parts)):
                print "comparing %s and %s" % (sim_parts[i],parts[i])
                if sim_parts[i] == parts[i]:
                   rem += 1 
                else:
                    break
            parts = parts[rem:]
            fed_filename = sep.join(parts)
            
            file.write("""   <federate file="%s"/>\n""" % fed_filename)
        file.write("""  </federates>\n""")
        file.write("""</simulation>\n""")
        file.close()
            
    def load_scenario(self):
        askopenfilename(filetypes=[("XML documents","*.xml"),("All files","*")])
    def save_as_scenario(self):
        asksaveasfilename(filetypes=[("XML documents","*.xml"),("All files","*")])
        
if __name__ == "__main__":
    main()

#!/usr/bin/python
from Tkinter import *
from tkFileDialog  import askopenfilename, asksaveasfilename
from tkSimpleDialog import askstring,Dialog
from xml.dom.minidom import Document, parseString
import Image,ImageTk

width  = 640
height = 480

grid_x_step = 10
grid_y_step = 10

node_radius = 2

# define some colors
canvas_bg_color             = '#ffffff'
grid_color                  = '#eeeeff'

node_colors = {
'default' : '#ffffff',
'selected' : '#ff6600',
}
node_outline_colors = {
'default' : '#000000',
'selected' : '#ff0000',
}

segment_colors = {
'default' : '#666666',
'selected' : '#ff0000',
}

# define some constants
ADD_NODE       = 0
ONE_WAY        = 1
TWO_WAY        = 2
DELETE_NODE    = 3
DELETE_SEGMENT = 4
SELECT         = 5
SELECT_SEGMENT = 6

MOUSEDOWN = 0
MOUSEUP   = 1

NODE_COUNTER = 0
SEGMENT_COUNTER = 0

node_attributes = [
("source","boolean",0),
("sink","boolean",0),
("source_rate","int",0),
("sink_weight","int",1)]

segment_attributes = [
("green","int",10),
("red","int",0),
("offset","int",0)]

SHOW_NODE_LABELS = 0

def new_node_id():
    global NODE_COUNTER
    NODE_COUNTER += 1
    return NODE_COUNTER

def new_segment_id():
    global SEGMENT_COUNTER
    SEGMENT_COUNTER += 1
    return SEGMENT_COUNTER

class Node:
    def __init__(self,canvas,id,x,y,args={}):
        self.x = x
        self.y = y
        self.id = id

        self.attributes = {}

        for (name,type,default) in node_attributes:
            if args.has_key(name):
                self.set_attr(name,type,args[name])
            else:
                self.set_attr(name,type,default)
        
        self.drawn = None
        self.drawn_label = None
        self.status = 'default'
        self.canvas = canvas
        self.segments = []
        self.show_label_v = SHOW_NODE_LABELS
        self.draw()

    def set_attr(self,name,type,value):
        if type == "boolean":
            if value == "true" or value == "t":
                value = 1
            elif value == "false" or value == "f":
                value = 0
            value = int(value)
        else:
            typecode = str
            if type == "int":
                typecode = int
            elif type == "float":
                typecode = float
            value = typecode(value)
        self.attributes[name] = value
        
    def draw(self):
        x0 = self.x - node_radius
        x1 = self.x + node_radius
        y0 = self.y - node_radius
        y1 = self.y + node_radius
        if self.drawn == None:
            self.drawn = self.canvas.create_oval(x0, y0, x1, y1, 
                    fill=node_colors[self.status],
                    outline = node_outline_colors[self.status])
        else:
            self.canvas.itemconfigure(self.drawn,fill=node_outline_colors[self.status],
                outline=node_outline_colors[self.status])
            self.canvas.coords(self.drawn,x0,y0,x1,y1)
        if self.show_label_v:
            if self.drawn_label == None:
                self.drawn_label = self.canvas.create_text(self.x,self.y +
                        15,text=str(self.id),fill=node_outline_colors[self.status])
            else:
                self.canvas.itemconfigure(self.drawn_label,fill=node_outline_colors[self.status])
                self.canvas.coords(self.drawn_label,x0,y0 + 15)
        else:
            if self.drawn_label != None:
                self.canvas.delete(self.drawn_label)
                self.drawn_label = None

    def show_label(self,b):
        self.show_label_v = b
        self.draw()

    def select(self):
        self.status = 'selected'
        self.draw()
        
    def deselect(self):
        self.status = 'default'
        self.draw()
        
    def connect(self,segment):
        self.segments.append(segment)
        
    def moveto(self,x,y):
        self.x = x
        self.y = y
        self.draw()
        for s in self.segments:
            s.draw()

    def distance_from(self,x,y):
        dist = (self.x - x) * (self.x - x)
        dist = dist + ((self.y - y) * (self.y - y))
        return dist
    
    def __repr__(self):
        string = "%s,%d,%d" % (str(self.id),self.x,self.y)
        for (name,type,default) in node_attributes:
            string = string + ",%s" % str(self.attributes[name])
        string = string + "\n"
        return string

    def delete_self(self):
        for segment in self.segments:
            segment.delete_self()
        self.segments = []
        if self.drawn != None:
            self.canvas.delete(self.drawn)
        if self.drawn_label != None:
            self.canvas.delete(self.drawn_label)
        
selected_node = None

class NodeEdit(Dialog):
    def body(self,master):
        self.title("Edit node attributes")
        self.node = selected_node
        self.vars = []
        row = 0
        for (name,type,default) in node_attributes:
            Label(master, text=name).grid(row=row,stick=NW)
            if type == "boolean":
                v = BooleanVar()
                v.set(self.node.attributes[name])
                self.vars.append(v)
                c = Checkbutton(master,variable=self.vars[row])
                c.grid(row=row,column=1,stick=W)
            elif type == 'int':
                v = IntVar()
                v.set(self.node.attributes[name])
                self.vars.append(v)
                entry = Entry(master)
                entry["textvariable"] = self.vars[row]
                entry.grid(row=row,column=1,stick=W)
            elif type == 'float':
                v = DoubleVar()
                v.set(self.node.attributes[name])
                self.vars.append(v)
                entry = Entry(master)
                entry["textvariable"] = self.vars[row]
                entry.grid(row=row,column=1,stick=W)
            else:
                v = StringVar()
                v.set(self.node.attributes[name])
                self.vars.append(v)
                entry = Entry(master)
                entry["textvariable"] = self.vars[row]
                entry.grid(row=row,column=1,stick=W)
            row = row + 1

    def apply(self):
        i = 0
        for (name,type,value) in node_attributes:
            self.node.set_attr(name,type,self.vars[i].get())
            i = i + 1

class Segment:
    def __init__(self,canvas,id,start,end,args={}):
        self.start = start
        self.end = end
        self.id = id
        self.status = 'default'
        self.drawn = None
        self.canvas = canvas
        self.attributes = {}
        for (name,type,default) in segment_attributes:
            if args.has_key(name):
                self.set_attr(name,type,args[name])
            else:
                self.set_attr(name,type,default)
        # make sure the nodes know about it
        self.start.connect(self)
        self.end.connect(self)
        self.draw()
        
    def set_attr(self,name,type,value):
        if type == "boolean":
            if value == "true" or value == "t":
                value = 1
            elif value == "false" or value == "f":
                value = 0
            value = int(value)
        else:
            typecode = str
            if type == "int":
                typecode = int
            elif type == "float":
                typecode = float
            value = typecode(value)
        self.attributes[name] = value

    def select(self):
        self.status = 'selected'
        self.draw()

    def deselect(self):
        self.status = 'default'
        self.draw()

    def draw(self):
        (x0,y0) = (self.start.x,self.start.y)
        (x1,y1) = (self.end.x,self.end.y)
        if self.drawn == None:
            self.drawn = self.canvas.create_line(x0,y0,x1,y1,width=1,
                    arrow='last',fill=segment_colors[self.status])
        else:
            self.canvas.itemconfigure(self.drawn,fill=segment_colors[self.status])
            self.canvas.coords(self.drawn,x0,y0,x1,y1)

    def distance_from(self,x,y):
        (x0,y0) = (self.start.x,self.start.y)
        (x1,y1) = (self.end.x,self.end.y)
        import math
        length = ((x1 - x0) * (x1 - x0)) + ((y1 - y0) * (y1 - y0))
        length = math.sqrt(length)

        (ux,uy) = ((x1 - x0)/length, (y1 - y0)/length)

        num_points = 5
        dists = []
        for i in range(num_points):
            out = (float(i + 1)/num_points) * length
            (mx,my) = ((out * ux) + x0, (out * uy) + y0)
            dist = (mx - x) * (mx - x)
            dist = dist + ((my - y) * (my - y))
            dists.append(dist)

        return min(dists)
    
    def __repr__(self):
        string = "%s,%s" % (str(self.start.id),str(self.end.id))
        for (name,type,default) in segment_attributes:
            string = string + ",%s" % str(self.attributes[name])
        string = string + "\n"
        return string
    
    def delete_self(self):
        self.canvas.delete(self.drawn)

    def moveto(self,dx,dy):
        # dx,dy is the amount that it's moved
        # calculate new start position
        (x,y) = (self.start.x + dx,self.start.y + dy)
        self.start.moveto(x,y)
        # calculate new end position
        (x,y) = (self.end.x + dx,self.end.y + dy)
        self.end.moveto(x,y)

selected_segment = None

class SegmentEdit(Dialog):
    def body(self,master):
        self.title("Edit segment attributes")
        self.segment = selected_segment
        self.vars = []
        row = 0
        for (name,type,default) in segment_attributes:
            Label(master, text=name).grid(row=row,stick=NW)
            if type == "boolean":
                v = BooleanVar()
                v.set(self.segment.attributes[name])
                self.vars.append(v)
                c = Checkbutton(master,variable=self.vars[row])
                c.grid(row=row,column=1,stick=W)
            elif type == 'int':
                v = IntVar()
                v.set(self.segment.attributes[name])
                self.vars.append(v)
                entry = Entry(master)
                entry["textvariable"] = self.vars[row]
                entry.grid(row=row,column=1,stick=W)
            elif type == 'float':
                v = DoubleVar()
                v.set(self.segment.attributes[name])
                self.vars.append(v)
                entry = Entry(master)
                entry["textvariable"] = self.vars[row]
                entry.grid(row=row,column=1,stick=W)
            else:
                v = StringVar()
                v.set(self.segment.attributes[name])
                self.vars.append(v)
                entry = Entry(master)
                entry["textvariable"] = self.vars[row]
                entry.grid(row=row,column=1,stick=W)
            row = row + 1

    def apply(self):
        i = 0
        for (name,type,value) in segment_attributes:
            self.segment.set_attr(name,type,self.vars[i].get())
            i = i + 1

class Layout_Tool:
    def __init__(self,parent):
        self.parent = parent
        self.parent.title('network layout tool')
        self.mode = ADD_NODE

        self.nodes                = {}
        self.segments             = {}
        self.start_node           = None
        self.selected_node        = None
        self.selected_segment     = None
        self.intermediate_segment = None

        self.nodes_filename = "nodes.csv"
        self.segments_filename = "segments.csv"
        self.background_image = None

        self.mouseup = MOUSEUP
        self.mousedown_x = 0
        self.mousedown_y = 0

        menubar     = Menu(self.parent)
        filemenu    = Menu(menubar,  tearoff=0)
        nodemenu    = Menu(menubar, tearoff=0)
        segmentmenu = Menu(menubar, tearoff=0)
        profilemenu = Menu(menubar, tearoff=0)
        viewmenu    = Menu(menubar, tearoff=0)

        viewmenu.add_command(label="load background image...",
                command=self.load_background_image)
        self.show_grid_var = BooleanVar()
        self.show_grid_var.set(0)
        self.gridlines = []

        self.show_node_labels_var = BooleanVar()
        self.show_node_labels_var.set(SHOW_NODE_LABELS)

        viewmenu.add_checkbutton(label="show grid",
                variable=self.show_grid_var, command=self.show_grid)
        viewmenu.add_checkbutton(label="show node labels",
                command=self.show_node_labels,
                variable=self.show_node_labels_var)
        nodemenu.add_command(label="load nodes...",command=self.load_nodes)
        segmentmenu.add_command(label="load segments...",command=self.load_segments)
        nodemenu.add_command(label="save nodes as...",command=self.save_nodes_as)
        segmentmenu.add_command(label="save segments as...",command=self.save_segments_as)
        profilemenu.add_command(label="load nodes profile...",command=self.load_nodes_profile)
        profilemenu.add_command(label="load segments profile...",command=self.load_segments_profile)
        filemenu.add_command(label="save",command=self.save_button_pressed)
        filemenu.add_command(label="Exit",command=self.parent.quit)
        menubar.add_cascade(label="File",menu=filemenu)
        menubar.add_cascade(label="View",menu=viewmenu)
        menubar.add_cascade(label="Nodes",menu=nodemenu)
        menubar.add_cascade(label="Segments",menu=segmentmenu)
        menubar.add_cascade(label="Profiles",menu=profilemenu)
        self.parent.config(menu=menubar)

        
        outer_frame = Frame(self.parent)
        self.canvas = Canvas(outer_frame,width=width,height=height,
                             background=canvas_bg_color)
        self.canvas.bind("<Button-1>",self.canvas_click)
        self.canvas.bind("<ButtonRelease-1>",self.canvas_mouseup)
        self.canvas.bind("<B1-Motion>",self.canvas_mousemove)

        mode_buttons = Frame(outer_frame)

        self.mode = IntVar()
        self.mode.set(ADD_NODE)

        
        self.select_button   = Radiobutton(mode_buttons,text="select node",
                                           value = SELECT,
                                           variable=self.mode,
                                           indicatoron=0)
        self.select_segment_button = Radiobutton(mode_buttons,text="select segment",
                value= SELECT_SEGMENT,
                variable = self.mode,
                indicatoron=0)
        self.new_node_button = Radiobutton(mode_buttons,text="add node",
                                           value = ADD_NODE,
                                           variable=self.mode,
                                           indicatoron=0)
        self.one_way_button  = Radiobutton(mode_buttons,text="one way",
                                           value = ONE_WAY,
                                           variable=self.mode,
                                           indicatoron=0)
        self.two_way_button  = Radiobutton(mode_buttons,text="two way",
                                           value = TWO_WAY,
                                           variable=self.mode,
                                           indicatoron=0)
        self.delete_node_button   = Radiobutton(mode_buttons,text="delete node",
                                           value = DELETE_NODE,
                                           variable=self.mode,
                                           indicatoron=0)
        self.delete_segment_button   = Radiobutton(mode_buttons,text="delete segment",
                                           value = DELETE_SEGMENT,
                                           variable=self.mode,
                                           indicatoron=0)

        buttons = Frame(outer_frame)

        self.save_button     = Button(buttons, text="save",command=self.save_button_pressed)
        self.edit_node_button = Button(buttons, text="edit node",
                state='disabled',command=self.edit_node_pressed)
        self.edit_segment_button = Button(buttons, text="edit segment",
                state='disabled',command=self.edit_segment_pressed)

        outer_frame.pack()
        self.canvas.pack()
        mode_buttons.pack()
        buttons.pack()
        self.select_button.pack(side=LEFT)
        self.select_segment_button.pack(side=LEFT)
        self.new_node_button.pack(side=LEFT)
        self.one_way_button.pack(side=LEFT)
        self.two_way_button.pack(side=LEFT)
        self.delete_node_button.pack(side=LEFT)
        self.delete_segment_button.pack(side=LEFT)
        self.save_button.pack(side=LEFT)
        self.edit_node_button.pack(side=LEFT)
        self.edit_segment_button.pack(side=LEFT)

    def load_background_image(self):
        filename = askopenfilename(filetypes=[("PNG graphics","*.png"),("JPEG graphics","*.jpg"),
        ("GIF images","*.gif")])
        self.im = Image.open(filename)
        self.im = self.im.resize((width,height),Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.im)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=NW, image=self.img)
        self.canvas.tag_lower(self.canvas_image)

    def load_nodes(self):
        self.nodes_filename = askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*")])
        file = open(self.nodes_filename,"r")
        header = file.readline()
        header = header.strip()
        fields = header.split(',')
        for node in self.nodes.values():
            node.delete_self()
        self.nodes = {}
        for line in file:
            line = line.strip()
            parts = line.split(',')
            id = parts[0]
            x = parts[1]
            y = parts[2]
            args = {}
            idx = 3
            for f in fields[idx:]:
                args[f] = parts[idx]
                idx = idx + 1
            self.add_node(int(x),int(y),id,args)
        file.close()
        self.unselect_all_nodes()

    def load_segments(self):
        self.segments_filename = askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*")])
        file = open(self.segments_filename,"r")
        header = file.readline()
        header = header.strip()
        fields = header.split(',')
        for segment in self.segments.values():
            segment.delete_self()
        self.segments = {}
        for line in file:
            line = line.strip()
            parts = line.split(',')
            start = parts[0]
            end = parts[1]
            start_node = self.nodes[start]
            end_node = self.nodes[end]
            idx = 2
            args = {}
            for f in fields[idx:]:
                args[f] = parts[idx]
                idx = idx + 1
            self.add_segment(start_node,end_node,None,args)
        file.close()
        self.unselect_all_segments()
            
    def load_nodes_profile(self):
        self.nodes_profile_filename = askopenfilename(filetypes=[("XML Documents","*.xml"),
                ("All files","*")])
        xmlstring = open(self.nodes_profile_filename,"r").read()
        doc = parseString(xmlstring)
        global node_attributes
        node_attributes = []
        for attr in doc.getElementsByTagName('attribute'):
            name = attr.getAttribute('name')
            type = attr.getAttribute('type')
            default = attr.getAttribute('default')
            node_attributes.append((name,type,default))
        doc.unlink()
        
    def load_segments_profile(self):
        self.segments_profile_filename = askopenfilename(filetypes=[("XML Documents","*.xml"),
                ("All files","*")])
        xmlstring = open(self.segments_profile_filename,"r").read()
        doc = parseString(xmlstring)
        global segment_attributes
        segment_attributes = []
        for attr in doc.getElementsByTagName('attribute'):
            name = attr.getAttribute('name')
            type = attr.getAttribute('type')
            default = attr.getAttribute('default')
            segment_attributes.append((name,type,default))
        doc.unlink()

    def draw_grid(self):
        self.gridlines = []
        for x in range(0,width,grid_x_step):
            self.gridlines.append(self.canvas.create_line(x,0,x,height,width=1,fill=grid_color))
        for y in range(0,height,grid_y_step):
            self.gridlines.append(self.canvas.create_line(0,y,width,y,width=1,fill=grid_color))
    def show_grid(self):
        if self.show_grid_var.get():
            self.draw_grid()
        else:
            for l in self.gridlines:
                self.canvas.delete(l)

    def show_node_labels(self):
        global SHOW_NODE_LABELS
        SHOW_NODE_LABELS = self.show_node_labels_var.get()
        for n in self.nodes.values():
            n.show_label(SHOW_NODE_LABELS)
        
    def canvas_click(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.mousedown_x = x
        self.mousedown_y = y
        self.mouseup = MOUSEDOWN
        if self.mode.get() == ADD_NODE:
            self.unselect_all_nodes()
            self.unselect_all_segments()
            self.add_node(x,y)
        if self.mode.get() == ONE_WAY:
            self.unselect_all_nodes()
            self.unselect_all_segments()
            self.add_one_way(x,y)
        if self.mode.get() == TWO_WAY:
            self.unselect_all_nodes()
            self.unselect_all_segments()
            self.add_two_way(x,y)
        if self.mode.get() == DELETE_NODE:
            self.delete_node(x,y)
        if self.mode.get() == DELETE_SEGMENT:
            self.delete_segment(x,y)
        if self.mode.get() == SELECT:
            self.select_node(x,y)
        if self.mode.get() == SELECT_SEGMENT:
            self.select_segment(x,y)

    def select_segment(self,x,y):
        seg = self.closest_segment(x,y)
        self.unselect_all_nodes()
        self.unselect_all_segments()
        seg.select()
        self.selected_segment = seg
        self.edit_segment_button.configure(state='normal')


    def canvas_mouseup(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.mouseup = MOUSEUP
        if self.mode.get() == ONE_WAY:
            self.finish_add_one_way(x,y)
        if self.mode.get() == TWO_WAY:
            self.finish_add_two_way(x,y)

    def canvas_mousemove(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mouseup == MOUSEDOWN:
            if self.mode.get() == SELECT:
                self.selected_node.moveto(x,y)
            if self.mode.get() == ONE_WAY:
                self.intermediate_add_one_way(x,y)
            if self.mode.get() == TWO_WAY:
                self.intermediate_add_two_way(x,y)
            if self.mode.get() == SELECT_SEGMENT:
                dx = x - self.mousedown_x 
                dy = y - self.mousedown_y
                self.selected_segment.moveto(dx,dy)
                self.mousedown_x = x
                self.mousedown_y = y

    def add_node(self,x,y,id=None,args={}):
        global NODE_COUNTER
        if id == None:
            id = new_node_id()
        else:
            if int(id) > NODE_COUNTER:
                NODE_COUNTER = int(id)
        node = Node(self.canvas,id,x,y,args)
        self.nodes[str(id)] = node
        self.selected_node = node
        self.edit_node_button.configure(state='normal')
        node.select()
        
    def select_node(self,x,y):
        n = self.closest_node(x,y)
        self.unselect_all_nodes()
        self.unselect_all_segments()
        self.selected_node = n
        self.selected_node.select()
        self.edit_node_button.configure(state='normal')
        
    def unselect_all_nodes(self):
        for n in self.nodes.values():
            n.deselect()
        self.selected_node = None
        self.edit_node_button.configure(state='disabled')
        
    def unselect_all_segments(self):
        for s in self.segments.values():
            s.deselect()
        self.selected_segment = None
        self.edit_segment_button.configure(state='disabled')
            
    def add_one_way(self,x,y):
        self.start_node = self.closest_node(x,y)

    def intermediate_add_one_way(self,x,y):
        finish_node = self.closest_node(x,y)
        if self.start_node != finish_node:
            (x0,y0) = (self.start_node.x,self.start_node.y)
            (x1,y1) = (finish_node.x,finish_node.y)
            if self.intermediate_segment:
                self.canvas.coords(self.intermediate_segment,x0,y0,x1,y1)
            else:
                self.intermediate_segment = self.canvas.create_line(x0,y0,x1,y1,width=1,arrow='last',
                                                                    fill=segment_colors['selected'])
        
    def finish_add_one_way(self,x,y):
        finish_node = self.closest_node(x,y)
        if self.start_node != finish_node:
            self.add_segment(self.start_node,finish_node)
            self.canvas.delete(self.intermediate_segment)
            self.intermediate_segment = None
            
    def add_two_way(self,x,y):
        self.start_node = self.closest_node(x,y)

    def intermediate_add_two_way(self,x,y):
        finish_node = self.closest_node(x,y)
        if self.start_node != finish_node:
            (x0,y0) = (self.start_node.x,self.start_node.y)
            (x1,y1) = (finish_node.x,finish_node.y)
            if self.intermediate_segment:
                self.canvas.coords(self.intermediate_segment,x0,y0,x1,y1)
            else:
                self.intermediate_segment = self.canvas.create_line(x0,y0,x1,y1,width=1,arrow='both',
                                                                    fill=segment_colors['selected'])

    def finish_add_two_way(self,x,y):
        finish_node = self.closest_node(x,y)
        if self.start_node != finish_node:
            self.add_segment(self.start_node,finish_node)
            self.add_segment(finish_node,self.start_node)
            self.canvas.delete(self.intermediate_segment)
            self.intermediate_segment = 0

    def add_segment(self,start,end,id=None,args={}):
        global SEGMENT_COUNTER
        if id == None:
            id = new_segment_id()
        else:
            if int(id) > SEGMENT_COUNTER:
                SEGMENT_COUNTER = int(id)
        segment = Segment(self.canvas,id,start,end,args)
        self.segments[str(id)] = segment
        self.selected_segment = segment
        self.edit_segment_button.configure(state='normal')
        segment.select()
        
    def delete_node(self,x,y):
        node = self.closest_node(x,y)
        if node != None:
            node.delete_self()
            del self.nodes[str(node.id)]
            self.unselect_all_nodes()
            self.unselect_all_segments()

    def delete_segment(self,x,y):
        segment = self.closest_segment(x,y)
        if segment != None:
            segment.delete_self()
            del self.segments[str(segment.id)]
            self.unselect_all_nodes()
            self.unselect_all_segments()

    def closest_node(self,x,y):
        """ returns id of node closest to (x,y)"""
        closest_dist = 1000000000
        closest = None
        idx = 0
        for n in self.nodes.values():
            dist = n.distance_from(x,y)
            if dist < closest_dist:
                closest_dist = dist
                closest = n
            idx = idx + 1
        return closest

    def closest_segment(self,x,y):
        closest_dist = 1000000000
        closest = None
        idx = 0
        for s in self.segments.values():
            dist = s.distance_from(x,y)
            if dist < closest_dist:
                closest_dist = dist
                closest = s
            idx = idx + 1
        return closest
            

    def save_nodes_as(self):
        self.nodes_filename = asksaveasfilename(filetypes=[("CSV files","*.csv"),("All files","*")])
        self.save_nodes()
                

    def save_segments_as(self):
        self.segments_filename = asksaveasfilename(filetypes=[("CSV files","*.csv"),("All files","*")])
        self.save_segments()

    def save_nodes(self):
        f = file(self.nodes_filename,'w')
        f.write("node,x,y")
        for (name,type,default) in node_attributes:
            f.write(",%s" % name)
        f.write("\n")
        for n in self.nodes.values():
            f.write(str(n))
        f.close()

    def save_segments(self):
        f = file(self.segments_filename,'w')
        f.write("start,end")
        for (name,type,default) in segment_attributes:
            f.write(",%s" % name)
        f.write("\n")
        for s in self.segments.values():
            f.write(str(s))
        f.close()

    def save_button_pressed(self):
        # write nodes file
        self.save_nodes()

        # write segments file
        self.save_segments()

    def edit_node_pressed(self):
        global selected_node
        selected_node = self.selected_node
        dialog = NodeEdit(self.parent)

    def edit_segment_pressed(self):
        global selected_segment
        selected_segment = self.selected_segment
        dialog = SegmentEdit(self.parent)

root = Tk()
lt = Layout_Tool(root)
root.mainloop()

#!/usr/bin/python

from Tkinter import *
import Image,ImageTk
import csv

map_file = "simulations/traffic/pollution/lm_small.png"
nodes_file = "simulations/traffic/streets/manhattan_nodes.csv"
segments_file = "simulations/traffic/streets/manhattan_segments.csv"
width  = 640
height = 480
size = (width,height)

node_radius = 2

# define some colors
canvas_bg_color             = '#ffffff'
grid_color                  = '#eeeeff'
one_way_color               = '#666666'
two_way_color               = '#666666'
node_color                  = '#ffffff'
node_outline_color          = '#000000'
selected_node_color         = '#ff6600'
selected_node_outline_color = '#ff0000'
active_segment_color        = '#ff0000'


class Map:
    def __init__(self,master):
        self.master = master
        self.f1 = Frame(self.master)
        self.canvas = Canvas(self.f1,width=width,height=height,background="#ffffff")
        self.img = Image.open(map_file)
        self.pimg = ImageTk.PhotoImage(self.img)
        self.img = self.canvas.create_image(0,0,anchor=NW,image=self.pimg)

        self.canvas.bind("<Button-1>",self.mousedown)

        self.nodes = {}
        p = csv.parser()
        n_file = open(nodes_file)
        headers = n_file.readline()
        while 1:
            line = n_file.readline()
            if not line:
                break
            (idx,x,y) = p.parse(line)
            x = int(x)
            y = int(y)
            self.nodes[idx] = (x,y)
            node = self.canvas.create_oval(x - node_radius,y-node_radius,x+node_radius,y+node_radius,fill=node_color,outline=node_outline_color)

        self.segments = []
        s_file = open(segments_file)
        headers = s_file.readline()
        while 1:
            line = s_file.readline()
            if not line:
                break
            (start,end) = p.parse(line)
            start = int(start)
            end = int(end)
            self.segments.append((start,end))
            

        self.canvas.pack()

        self.l = Label(self.f1,text="foo")
        self.l.pack()
        
        self.f1.pack()

    def mousedown(self,event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        (idx,nx,ny) = self.closest_node(x,y)

        (incoming,outgoing) = self.node_segments(idx)
        inc_string = "incoming: "
        if len(incoming) > 0:
            inc_string = inc_string + ",".join([str(s) for s in incoming])
        else:
            inc_string = ""
        out_string = "outgoing: "
        if len(outgoing) > 0:
            out_string = out_string + ",".join([str(s) for s in outgoing])
        else:
            out_string = ""

        self.l.configure(text="%d: (%d,%d) %s %s" % (idx,nx,ny,inc_string,out_string))

    def closest_node(self,x,y):
        """ returns id of node closest to (x,y)"""
        closest_dist = 1000000000
        closest = 0
        idx = 0
        nx = 0
        ny = 0
        for idx in self.nodes.keys():
            n = self.nodes[idx]
            dist = (x - n[0]) * (x - n[0])
            dist = dist + ((y - n[1]) * (y - n[1]))
            if dist < closest_dist:
                closest_dist = dist
                closest = idx
                nx = n[0]
                ny = n[1]
        return (int(closest),nx,ny)

    def node_segments(self,node):
        incoming = []
        outgoing = []
        idx = 0
        for (start,end) in self.segments:
            if start == node:
                incoming.append(idx)
            if end == node:
                outgoing.append(idx)
            idx += 1
        return (incoming,outgoing)

if __name__ == "__main__":
    root = Tk()
    map = Map(root)
    root.mainloop()

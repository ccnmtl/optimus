(x,y) = int(event.attrs['pos'][0]/4.0), int(event.attrs['pos'][1]/4.0)
try:
    self.canvas.coords(self.textlabel,x*4,y*4)
    self.canvas.itemconfigure(self.textlabel,text="%.04f" % self.ctplus1[x,y])
except:
    self.textlabel = self.canvas.create_text(x*4, y*4, text="%.04f" % self.ctplus1[x,y])
self.canvas.itemconfigure(self.textlabel,fill="#ff0000")

for i in range(self.num_segments):
    red = "#ff9999"
    green = "#99ff99"
    color = [green,red][self.redlights[i]]
    seg = self.drawn_segments[i]
    self.canvas.itemconfigure(seg,fill=color)


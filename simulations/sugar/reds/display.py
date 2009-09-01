# first clear out the dots from the last tick
c = self.grid
# this is a big slowdown
# it would be better to do it by converting to an image and
# alpha-blending or something, but i'm too lazy to do that
num_dots = len(self.canvas_dots)
cnt = 0
for x in range(160):
    for y in nonzero(c[x,:]):
        xpos = x * 4
        ypos = y * 4
        width = .4 * self.health[x,y]
        h_width = width / 2
        min = 2 - h_width
        max = 2 + h_width
        color = "#ff0000"
        if cnt >= num_dots:
            self.canvas_dots.append(self.canvas.create_rectangle(xpos + min,
                ypos + min, xpos + max, ypos + max,
                fill=color,outline="#ff0000",width=0))
        else:
            self.canvas.coords(self.canvas_dots[cnt],xpos + min,ypos + min,
                    xpos + max,ypos + max)
            pass
        cnt += 1
        
if num_dots >= cnt:
    for d in self.canvas_dots[cnt - 1:]:
        self.canvas.delete(d)
self.canvas_dots = self.canvas_dots[:cnt]

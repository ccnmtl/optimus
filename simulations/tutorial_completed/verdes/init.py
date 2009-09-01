import MLab

# start them at random positions
self.x = MLab.rand(self.number) * 640
self.y = MLab.rand(self.number) * 480

# draw them on the canvas
self.dots = []
for i in range(self.number):
    self.dots.append(self.canvas.create_rectangle(self.x[i] - 1,self.y[i] - 1,self.x[i] + 1,self.y[i] + 1,
                                                  fill="#006600",outline="#006600",width=0))


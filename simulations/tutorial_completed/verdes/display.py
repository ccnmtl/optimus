
# if the user has reduced the number of verdes,
# we need to clear out those dots.
if len(self.dots) > self.number:
    # clear them from the canvas
    for dot in self.dots[self.number:]:
        self.canvas.delete(dot)
    # resize the array
    self.dots = self.dots[:self.number]

# update the position of each verde
for i in range(self.number):
    self.canvas.coords(self.dots[i],self.x[i] - 1,self.y[i] -1,
                       self.x[i] + 1,self.y[i] + 1)

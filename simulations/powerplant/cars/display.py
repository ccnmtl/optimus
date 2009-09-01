# draw the cars on the screen

for i in self.cars:
    car = self.cars[i]
    (x,y) = car.coordinates()
    (x,y) = (x / self.scale, y / self.scale)
    self.canvas.coords(car.representation,x,y,x,y)

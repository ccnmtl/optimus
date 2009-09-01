
# set lights on streets
for i in xrange(len(self.lights)):
    self.streets[i].light = self.lights[i]

seen = {}
vmax = int(self.max_velocity)
slowdown_probability = self.slowdown_probability

# move the cars 
for s in self.streets:
    seen = s.update_ca(seen,vmax,slowdown_probability)

# simple sink

sink = (520,380)
def distance(x1,y1,x2,y2):
    dx = x2 - x1
    dy = y2 - y1
    dx = dx * dx
    dy = dy * dy
    dist = dx + dy
    return sqrt(dist)

to_remove = []
for c in self.cars:
    car = self.cars[c]
    (x,y) = car.coordinates()
    for sink in self.sinks:
        sink_x = self.node_x[sink]
        sink_y = self.node_y[sink]
        dist = distance(x,y,sink_x,sink_y)
        if dist < 6 and car.dest == sink:
            car.delete_self()
            self.canvas.delete(car.representation)
            to_remove.append(c)

for c in to_remove:
    try:
        del self.cars[c]
    except:
        pass


not_lost = {}
for s in self.streets:
    for c in s.cars:
        id = s.cars[c].id
        not_lost[id] = 1
for c in self.cars:
    if not not_lost.has_key(self.cars[c].id):
        print "lost car %d (%d,%d)" % (self.cars[c].id,self.cars[c].street.idx,self.cars[c].pos)

# build some arrays with the info we'll need to calculate pollution later

num_cars = len(self.cars.keys())
self.velocity = zeros(num_cars)
self.old_velocity = zeros(num_cars)
self.x = zeros(num_cars)
self.y = zeros(num_cars)
self.trucks = zeros(num_cars)

i = 0
for c in self.cars:
    car = self.cars[c]
    self.x[i] = car.x
    self.y[i] = car.y
    self.velocity[i] = car.dx
    self.old_velocity[i] = car.old_velocity
    if car.truck:
        self.trucks[i] = 1
    else:
        self.trucks[i] = 0
    i += 1

self.handle_event(OptimusEvent("calculate_pollution",{}))


self.scale = 10

self.max_velocity = int((1600.0 / (3600.0 * .4 * 5.0)) * self.max_velocity_mph)

# weight the destinations
self.dests = []
for i in xrange(len(self.sinks)):
    weight = self.sink_weights[i]
    sink = self.sinks[i]
    for n in xrange(weight):
        self.dests.append(sink)

from car import *

self.streets = []

for s in xrange(self.num_segments):
    self.streets.append(Street(s,self.segment_start_x[s] * self.scale,
        self.segment_start_y[s] * self.scale,
        self.segment_end_x[s] * self.scale,
        self.segment_end_y[s] * self.scale,
        self.segment_start[s],
        self.segment_end[s]))

leaving_edges = self.leaving_edges

for i in xrange(self.num_segments):
    le = []
    for edge in leaving_edges[i]:
        le.append(self.streets[edge])
    self.streets[i].leaving_edges = le

# add some cars
self.cars = {}
r = Random()
taken = {}
for i in xrange(self.numcars):
    street_idx = r.randint(0,self.num_segments - 1)
    street     = self.streets[street_idx]
    pos        = r.randint(0,street.len - 1)

    if not taken.has_key((street_idx,pos)):
        taken[(street_idx,pos)] = 1
        velocity   = r.randint(0,self.max_velocity)

        dest = self.dests[r.randint(0,len(self.dests) - 1)]
        c          = Car(street,pos,velocity,dest,self)
        # if we're heading right to a destination
        # we're probably on a one way road
        # so we have to use that as our destination
        if c.street.end_node_idx in self.dests:
            c.dest = c.street.end_node_idx

        self.cars[c.id] = c

color = self.car_color
truck_color = "#ff0000"
self.lost = {}

for c in self.cars:
    car = self.cars[c]
    (x,y) = car.coordinates()
    (x,y) = (x / self.scale, y / self.scale)
    vehicle_color = color
    if car.truck:
        vehicle_color=truck_color
    car.representation = self.canvas.create_rectangle(x,y,x,y,fill=vehicle_color,outline=vehicle_color,width=0)

from car import Car
from random import Random

node = attrs['node']

segments_starting_at = []
for i in range(self.num_segments):
    if self.segment_start[i] == node:
        segments_starting_at.append(i)

r = Random()
street_idx = segments_starting_at[r.randint(0,len(segments_starting_at) - 1)]
street     = self.streets[street_idx]
pos        = 0
if not street.cars.has_key(pos):
    velocity   = 0

    dest = self.dests[r.randint(0,len(self.dests) - 1)]
    c          = Car(street,pos,velocity,dest,self)
    self.cars[c.id] = c
    (x,y) = c.coordinates()
    color = self.car_color
    c.representation = self.canvas.create_rectangle(x,y,x,y,fill=color,outline=color,width=0)


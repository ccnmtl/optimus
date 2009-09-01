self.segment_start_x = self.organizer.get_var("streets","segment_start_x",zeros(self.num_segments))
self.segment_end_x   = self.organizer.get_var("streets","segment_end_x",zeros(self.num_segments))
self.segment_start_y = self.organizer.get_var("streets","segment_start_y",zeros(self.num_segments))
self.segment_end_y   = self.organizer.get_var("streets","segment_end_y",zeros(self.num_segments))

from car import *

for s in range(len(self.streets)):
    street = self.streets[s]
    street.move(self.segment_start_x[s],self.segment_start_y[s],
                self.segment_end_x[s],self.segment_end_y[s])


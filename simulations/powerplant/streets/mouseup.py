self.debug("mouseup")
x = attrs['pos'][0]
y = attrs['pos'][1]

self.node_x[self.selected_node] = x
self.node_y[self.selected_node] = y

for i in xrange(self.num_segments):
    s = self.segment_start[i]
    e = self.segment_end[i]
    x1 = self.node_x[s]
    y1 = self.node_y[s]
    x2 = self.node_x[e]
    y2 = self.node_y[e]
    self.segment_start_x[i] = x1
    self.segment_start_y[i] = y1
    self.segment_end_x[i] = x2
    self.segment_end_y[i] = y2
    seg = self.drawn_segments[i]
    self.canvas.coords(seg,x1,y1,x2,y2)

self.segment_length = sqrt(power(self.segment_end_x - self.segment_start_x,2) \
                           + power(self.segment_end_y - self.segment_start_y,2))

self.selected_node = -1

data = self.csv2numeric(self.nodes_file,(int,int,int))

self.nodes  = data['node']
self.node_x = data['x']
self.node_y = data['y']

data = self.csv2numeric(self.segments_file,(int,int))
self.segment_start = data['start']
self.segment_end = data['end']


self.num_segments = len(self.segment_start.tolist())
self.segment_start_x = zeros(self.num_segments)
self.segment_start_y = zeros(self.num_segments)
self.segment_end_x = zeros(self.num_segments)
self.segment_end_y = zeros(self.num_segments)

self.segments = arange(self.num_segments)
self.cnt = 0

lights_data = self.csv2numeric(self.lights_file,(int,int,int))
self.lights_red  = lights_data['red']
self.lights_green = lights_data['green']
self.lights_cnt = lights_data['start']

self.lights_period = self.lights_red + self.lights_green
self.lights_cnt    = self.lights_cnt % self.lights_period
self.redlights     = self.lights_cnt > self.lights_green

# build a list of lists of the edges that leave from each node

leaving_node = []
for n in range(len(self.nodes)):
    leaving = []
    for s in range(self.num_segments):
        if self.segment_start[s] == n:
            leaving.append(s)
    leaving_node.append(leaving)

# use that to build a list of the edges that each edge connects to

self.leaving_edge = []
for s in range(self.num_segments):
    self.leaving_edge.append(leaving_node[self.segment_end[s]])

for i in range(self.num_segments):
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

self.segment_length = sqrt(power(self.segment_end_x - self.segment_start_x,2) \
                           + power(self.segment_end_y - self.segment_start_y,2))

self.node_graph = {}

for n in self.nodes:
    self.node_graph[n] = {}

for i in range(len(self.segment_start)):
    start = self.segment_start[i]
    end = self.segment_end[i]
    weight = self.segment_length[i]
    self.node_graph[start][end] = weight

self.nodes_to_streets = {}

for i in range(len(self.segment_start)):
    tuple = (self.segment_start[i],self.segment_end[i])
    self.nodes_to_streets[tuple] = i

source_data = self.csv2numeric(self.sources_file,(int,int))
sink_data = self.csv2numeric(self.sinks_file,(int,int))

self.sources = source_data['node']
self.source_rates = source_data['rate']

self.sinks = sink_data['node']
self.sink_weights = sink_data['weight']

self.selected_node = -1
self.drawn_segments = []
for i in range(self.num_segments):
    red = "#ff9999"
    green = "#99ff99"
    color = [green,red][self.redlights[i]]

    seg = self.canvas.create_line(self.segment_start_x[i],
                                  self.segment_start_y[i],
                                  self.segment_end_x[i],
                                  self.segment_end_y[i],
                                  width=1,
                                  arrow='last',
                                  fill=color)
    self.drawn_segments.append(seg)

data = self.csv2numeric(self.nodes_file,(int,int,int,int,int,int,int))

self.nodes          = data['node']
self.node_x_r       = data['x']
self.node_y_r       = data['y']
self.sources_r      = data['source']
self.sinks_r        = data['sink']
self.source_rates_r = data['source_rate']
self.sink_weights_r = data['sink_weight']

self.node_x = {}
self.node_y = {}
self.sources = []
self.sinks = []
self.source_rates = []
self.sink_weights = []

i = 0
for n in self.nodes:
    self.node_x[n - 1] = self.node_x_r[i]
    self.node_y[n - 1] = self.node_y_r[i]

    if self.sources_r[i] == 1:
        self.sources.append(n - 1)
        self.source_rates.append(self.source_rates_r[i])

    if self.sinks_r[i] == 1:
        self.sinks.append(n - 1)
        self.sink_weights.append(self.sink_weights_r[i])
        
    i = i + 1

data = self.csv2numeric(self.segments_file,(int,int,int,int,int))
self.segment_start = data['start'] - 1
self.segment_end   = data['end'] - 1
self.lights_green  = data['green']
self.lights_red   = data['red']
self.lights_cnt    = data['offset']

self.num_segments    = len(self.segment_start.tolist())
self.segment_start_x = zeros(self.num_segments)
self.segment_start_y = zeros(self.num_segments)
self.segment_end_x   = zeros(self.num_segments)
self.segment_end_y   = zeros(self.num_segments)

self.segments = arange(self.num_segments)
self.cnt = 0

self.lights_period = self.lights_red + self.lights_green
self.lights_cnt    = self.lights_cnt % self.lights_period
self.redlights     = self.lights_cnt > self.lights_green

# build a list of lists of the edges that leave from each node

leaving_node = []
for n in self.nodes:
    leaving = []
    for s in range(self.num_segments):
        if self.segment_start[s] == n - 1:
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
    self.node_graph[n - 1] = {}

for i in range(len(self.segment_start)):
    start = self.segment_start[i]
    end = self.segment_end[i]
    weight = self.segment_length[i]
    self.node_graph[start][end] = weight

self.nodes_to_streets = {}

for i in range(len(self.segment_start)):
    tuple = (self.segment_start[i],self.segment_end[i])
    self.nodes_to_streets[tuple] = i


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

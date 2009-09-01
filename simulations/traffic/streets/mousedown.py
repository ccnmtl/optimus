# figure out which node is closest to where the user clicked.

x = attrs['pos'][0]
y = attrs['pos'][1]

dist = power(self.node_x - x, 2) + power(self.node_y - y, 2)

self.selected_node = 0
shortest_distance = dist[0]
for i in range(len(dist)):
    if dist[i] < shortest_distance:
        self.selected_node = i
        shortest_distance = dist[i]

self.debug(self.selected_node)

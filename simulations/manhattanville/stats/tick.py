from stats_functions import *
(num_cars,min_speed,max_speed,average_speed,
 min_distance,max_distance,average_distance,total_distance,
 min_age,max_age,average_age,total_age) = calculate_cars_statistics(self.cars)
(street_congestion,average_congestion)       = calculate_streets_statistics(self.streets)
self.congestion_node_graph                   = congestion_weighted_graph(self.node_graph,street_congestion,self.nodes_to_streets)
(min_pollution,max_pollution,average_pollution,total_pollution) = calculate_pollution_statistics(self.pollution)

self.num_cars           = num_cars
self.min_speed          = min_speed
self.max_speed          = max_speed
self.average_speed      = average_speed
self.min_distance       = min_distance
self.max_distance       = max_distance
self.average_distance   = average_distance
self.total_distance     = total_distance
self.min_age            = min_age
self.max_age            = max_age
self.average_age        = average_age
self.total_age          = total_age
self.average_congestion = average_congestion
self.min_pollution      = min_pollution
self.max_pollution      = max_pollution
self.average_pollution  = average_pollution
self.total_pollution    = total_pollution

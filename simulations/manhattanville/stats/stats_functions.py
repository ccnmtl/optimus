from Numeric import *
def basic_stats(list):
    """ calculates the min, max, average, and total for a list """
    length = len(list)
    if length == 0:
        return (0,0,0,0)
    min = list[0]
    max = list[0]
    total = 0
    for item in list:
        total += item
        if item < min:
            min = item
        if item > max:
            max = item
    average = total / length
    return (min,max,average,total)

def calculate_cars_statistics(cars):
    """ calculates the number of cars, the minimum speed,
    the maximum speed, and the average speed of the cars"""

    speeds    = [c.dx                 for c in cars.values()]
    distances = [c.distance_travelled for c in cars.values()]
    ages      = [c.age                for c in cars.values()]

    (min_speed,   max_speed,   average_speed,   total_speed)    = basic_stats(speeds)
    (min_distance,max_distance,average_distance,total_distance) = basic_stats(distances)
    (min_age,     max_age,     average_age,     total_age)      = basic_stats(ages)

    num_cars = len(cars)
    return (num_cars,min_speed,max_speed,average_speed,
            min_distance,max_distance,average_distance,total_distance,
            min_age,max_age,average_age,total_age)

def calculate_streets_statistics(streets):
    street_lengths    = array([s.length    for s in streets])
    street_cars_count = array([len(s.cars) for s in streets])

    street_congestion = street_cars_count / street_lengths

    (min,max,average_congestion,total) = basic_stats(street_congestion)
    
    return (street_congestion,average_congestion)


def congestion_weighted_graph(node_graph,street_congestion,nodes_to_streets):
    # make congestion weighted graph
    congestion_by_nodes = {}

    for (start,end) in nodes_to_streets.keys():
        congestion_by_nodes[(start,end)] = street_congestion[nodes_to_streets[(start,end)]]

    congestion_node_graph = {}
    for start in node_graph.keys():
        dict = node_graph[start]
        congestion_node_graph[start] = {}
        for end in dict.keys():
            congestion_node_graph[start][end] = congestion_by_nodes[(start,end)]
    return congestion_node_graph

def calculate_pollution_statistics(pollution):
    return basic_stats(ravel(pollution))

from Numeric import *
from random import random,randint
from pprint import pprint

TRUE = 1
FALSE = 0
GreenLight = "this error is raised if a car is near the end of a segment and may move to the next."
NoRoute = "no route to the sink"

shared_id = 0

class Street:
    def __init__(self,idx,startx,starty,endx,endy,start_node_idx,end_node_idx):
        self.idx    = idx
        self.startx = startx
        self.starty = starty
        self.endx   = endx
        self.endy   = endy
        self.start_node_idx = start_node_idx
        self.end_node_idx = end_node_idx

        self.dx = 0
        self.dy = 0
        self.length = 0.0
        self.len = 0

        self.update_coordinates()

        self.cars = {}

        self.light = 0
        self.leaving_edges = []


    def update_coordinates(self):
        self.dx = self.endx - self.startx
        self.dy = self.endy - self.starty

        self.length = sqrt((self.dx * self.dx) + (self.dy * self.dy))
        self.len = int(self.length)

    def move(self,x1,y1,x2,y2):
        self.startx = x1
        self.starty = y1
        self.endx   = x2
        self.endy   = y2

        self.update_coordinates()

    def dx(self):
        return self.dx
    def dy(self):
        return self.dy

    def occupied_cells(self):
        """ returns a list of which cells have cars in them """
        # should be able to cache this and just
        # recalculate if any cars have moved
        occ = self.cars.keys()
        occ.sort()
        return occ

    def next_occupied(self,occ,cell):
        for c in occ:
            if c > cell:
                return c
        return -1

    def have_green_light(self,velocity,cell):
        if (velocity > (self.len - cell - 1)) and (self.light == 0):
            return TRUE
        else:
            return FALSE

    def empty_from_start(self):
        occ = self.occupied_cells()
        if occ == []:
            return self.len
        else:
            return occ[0]

    def clear_cell(self,idx):
        del self.cars[idx]

    def update_ca(self,seen,vmax,slowdown_probability):
        road_length = self.len
        occ = self.occupied_cells()
        to_delete = []
        for cell in occ:
            car = self.cars[cell]
            assert(cell == car.pos)
            if not seen.has_key(car.id):
                seen[car.id] = 1
                empty = 0
                # set speed to desired speed
                desired_v = car.desired_velocity(vmax,slowdown_probability)
                # check if we're possibly at the end of a segment
                next_occupied_idx = self.next_occupied(occ,cell)

                try:
                    car.move(vmax,slowdown_probability)
                except GreenLight:
                    # we are near the end of the segment and have a
                    # green light to move onto the next segment
                    # this part still needs to be moved down into the Car
                    # class.
                    end_of_segment = road_length - cell - 1
                    # figure out which segment we might move onto
                    try:
                        next_street = car.pick_next_street()
                    except NoRoute:
                        car.delete_self()
                        to_delete.append(cell)
                    else:
                        # figure out how many empty cells there are in
                        # front of us
                        onto_next = FALSE
                        empty_cells_on_current = 0
                        empty_on_next = 0
                        if next_occupied_idx == -1:
                            empty_cells_on_current = end_of_segment
                            if desired_v > empty_cells_on_current:
                                empty_on_next = next_street.empty_from_start() - 1
                                if empty_on_next > 0:
                                    onto_next = TRUE
                                    next_street_idx = min(desired_v - empty_cells_on_current,empty_on_next)
                        else:
                            empty_cells_on_current = next_occupied_idx - cell - 1
                            onto_next = FALSE

                        total_empty = empty_cells_on_current + empty_on_next
                        empty = min(desired_v,total_empty)

                        if empty > 0:
                        ## move the car to its new position
                            if onto_next == TRUE:
                                car.move_to(next_street,next_street_idx,empty)
                            else:
                                new_idx = cell + empty
                                car.move_to(self,new_idx,empty)
                        else:
                            car.move_to(car.street,car.pos,0)
        for c in to_delete:
            del self.cars[c]
        return seen

def is_truck(percentage):
    r = randint(0,100)
    if r < percentage:
        return True
    else:
        return False

class Car:
    """represents a single Car in the simulation"""
    def __init__(self,street,pos,velocity,dest,federate):
        """creates a new Car object. pass in the street that
        it's on, its position on that street, and its velocity"""
        
        global shared_id
        self.id       = shared_id
        shared_id    += 1
        self.street   = street
        self.pos      = pos
        self.velocity = velocity
        self.dest     = dest
        self.federate = federate

        self.truck = is_truck(self.federate.percent_trucks)

        self.dx = velocity * self.federate.cell_length
        self.old_velocity = velocity * self.federate.cell_length

        # tell the street where we are
        self.street.cars[self.pos] = self

        self.distance_travelled = 0.0
        self.age = 0

        self.representation = ""
        # figure out x,y position
        self.x = 0
        self.y = 0

    def pollution(self):
        return self.CO2PerDistance

    def delete_self(self):
        try:
            del self.street.cars[self.pos]
        except:
            pass

    def node_path_to_streets(self,node_path):
        """ converts a path defined as nodes to a path
        defined as streets """
        street_path = []
        start = node_path[0]
        if len(node_path) == 1:
            # return a dummy if there is only one
            # node in the path (ie, the car is very
            # close to its destination node)
            return {start: 0}
        for n in node_path[1:]:
            end = n
            street_idx = self.federate.nodes_to_streets[(start,end)]
            street_path.append(street_idx)
            start = end
        start = street_path[0]
        street_dict = {}
        for s in street_path[1:]:
            street_dict[start] = self.federate.streets[s]
            start = s
        # make sure the current street points to something
        street_dict[self.street.idx] = self.federate.streets[street_path[0]]
        return street_dict

    def pick_next_street(self):
        from dijkstra import shortestPath
        from pprint import pprint
        import copy
        street_graph = copy.deepcopy(self.federate.street_graph)

        if self.federate.path_weight == "distance":
            # don't need to do anything for this one
            pass
        elif self.federate.path_weight == "congestion":
            street_graph = copy.deepcopy(self.federate.congestion_graph)
        else:
            pass

        if self.federate.randomize_graph == 1:
            for start in street_graph.keys():
                dict = street_graph[start]
                for end in dict.keys():
                    weight = dict[end]
                    weight += (random() * .0001)
                    dict[end] = weight
        try:
            path = shortestPath(street_graph,
                                self.street.end_node_idx,
                                self.dest)
        except KeyError:
            print "ERROR"
            print "going from %d" % self.street.end_node_idx
            print "to: %d" % self.dest
            pprint(street_graph)
            raise NoRoute
            self.delete_self()

        try:
            path = self.node_path_to_streets(path)
            return path[self.street.idx]
        except IndexError:
            print "ERROR"
            print "going from %d" % self.street.end_node_idx
            print "to: %d" % self.dest
            pprint(street_graph)
            pprint(path)
            raise NoRoute
        except KeyError:
            return self.street
    
    def coordinates(self):
        """ calculates and returns the x,y coordinates of
        the car """
        street_length = self.street.length
        percentage_pos = self.pos / street_length
        segment_dx = self.street.dx
        segment_dy = self.street.dy

        self.x = self.street.startx + percentage_pos * segment_dx
        self.y = self.street.starty + percentage_pos * segment_dy
        return (self.x,self.y)

    def desired_velocity(self,vmax,slowdown_probability):
        """ returns how fast the car would *like* to go during
        the next timestep. basically, it accelerates by 1 unit
        up to the max. then, with slowdown_probability chance, it will
        slow down one unit"""
        v = min(int(vmax),self.velocity + 1)
        if random() < slowdown_probability:
            v = v - 1
        v = max(v,0)
        return v

    def debug(self):
        if __debug__:
            print "Car(%d): [%d,%d] %d" % (self.id,self.street.idx,self.pos, self.velocity)

    def move_to(self,street,pos,velocity):
        """update's the car's position. arguments are:
        - new street to put the car on
        - new position on that street
        - new velocity
        """
        # clear out old values
        self.street.clear_cell(self.pos)

        # update car's state
        self.street = street
        self.pos = pos
        self.velocity = velocity

        self.old_velocity = self.dx
        self.dx = self.federate.cell_length * self.velocity

        self.distance_travelled += self.dx
        
        # update street's status
        if self.street.cars.has_key(pos):
            print "overwriting position %d" % pos
            print "car being overwritten: "
            self.street.cars[pos].debug()
            print "being overwritten by: "
            self.debug()
        self.street.cars[pos] = self

    def near_end(self,velocity):
        street_length = self.street.len
        if (street_length - self.pos) > velocity:
            return FALSE
        else:
            return TRUE

    def move(self,vmax,slowdown_probability):
        self.age += 1
        desired_velocity = self.desired_velocity(vmax,slowdown_probability)
        if desired_velocity == 0:
            self.move_to(self.street,self.pos,0)
            return
        occ = self.street.occupied_cells()
        next_occupied_idx = self.street.next_occupied(occ,self.pos)
            
        near_end = self.near_end(desired_velocity)
        if near_end == TRUE:
            green_light = self.street.have_green_light(desired_velocity,self.pos)
            if green_light == TRUE:
                raise GreenLight
        else:
            move_to_cell = 0
            if next_occupied_idx == -1:
                move_to_cell = self.pos + desired_velocity
            else:
                move_to_cell = min(self.pos + desired_velocity,next_occupied_idx - 1)
            distance = move_to_cell - self.pos
            self.move_to(self.street,move_to_cell,distance)

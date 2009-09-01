from OPTIMUS import *

class Cars (AgentLayer):
    # an agent layer that implements a collection of
    # cars that travel

    # other layers needed:
    #    - roads
    #    - traffic_lights
    
    def __init__(self,organizer,num_cars = 5):
        self.organizer = organizer
        organizer.register(self,                 # give a reference to ourself
                           layer = "traffic",    # tell the organizer that we implement a traffic layer
                           editable = ["recklessness","pollution"], # specify which attributes can be tweaked through the GUI      
                           # register event handlers
                           event_handlers = ["Tick" : self.tick,
                                             "Earthquake" : self.earthquake_handler],
                           # tell the  organizer what time scale we expect
                           tick = "second",
                           # tell the organizer how big we expect a tile to be
                           tile = "km",
                           # specify which other layers *must* be present
                           requires = ["roads","traffic_lights"],
                           )
        self.cars = []
        # ...


    # event handlers
    def tick(self,event):
        # move cars depending on stuff
        # like where other cars are, state of lights, etc.
        # first it saves its previous state

    def earthquake_handler(self,event):
        # drivers hear about earthquake on radio and all
        # get on their cellphones to make sure if loved
        # ones are ok. since they're talking on their
        # cellphones, their recklessness goes up by 50%
        self.recklessness *= 1.5


    # methods that all Layers must implement
    def get_in_region(self,attribute,x1,y1,x2,y2):
        """ gets some value within a given region """
        if attribute == "car_count":
            cnt = 0
            for c in self.cars:
                if c.x > x1 and c.x < x2 and c.y > y1 and c.y < y2:
                    cnt += 1
            return cnt
        # ...

    def get_at(self,attribute,x,y):
        # ...

    def display(self,tileengine):
        # tell the tile engine
        # what it needs to do to display our layer


# CA based air pollution layer

class Pollution (CALayer):

    def __init__(self,organizer):
        organizer.register(self,
                           layer = "pollution",
                           editable = [], # specify which attributes can be tweaked through the GUI      
                           # register event handlers
                           event_handlers = ["Tick" : self.tick],
                           # tell the  organizer what time scale we expect
                           tick = "second",
                           # tell the organizer how big we expect a tile to be
                           tile = "km",
                           # specify which other layers *must* be present
                           requires = ["traffic"],
                           )
        self.cells = []
        # ...

    # event handlers

    def tick(self,event):
        # loop over the cells, calculating
        # the value based on previous state, neighbor states,
        # cars within the cell, etc.
        # ...

    def get_in_region(self,attribute,x1,y1,x2,y2):

        if attribute == "avg_pollution":
            # get the cells within the specified region
            # and produce a weighted average of their pollution
            # values
    def get_at(self,attribute,x,y):

        if attribute == "pollution":
            # figure out which cell is at location (x,y)
            # and return its pollution value

    def display(self,tileengine):
        # tell the tile engine how to display each
        # cell

class Roads (Layer):
    # ....

class Traffic_Lights (Layer):
    # ....


# main

width = 20  # tiles
height = 20 # tiles
world = new Optimus(width,height)
organizer = world.getOrganizer()

road_layer     = new Roads(organizer)
traffic_lights = new Traffic_Lights(organizer)
cars           = new Cars(organizer)
pollution      = new Pollution(organizer)



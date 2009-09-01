# populate randomly
self.grid = MLab.rand(160,120) * 10
self.grid = self.grid.astype('i')
self.grid = where(self.grid > 8,1,0)
# start everyone with the same health
self.health = self.grid * self.start_health

# start with a blank array of dots
self.canvas_dots = []

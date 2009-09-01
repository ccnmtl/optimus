import Numeric
from Numeric import *
import math

self.x_axis = 12
self.y_axis = 12

self.x = MLab.rand(self.number) * self.x_axis
self.y = MLab.rand(self.number) * self.y_axis

for j in range(self.number):
    self.x[j] = int(self.x[j])
    self.y[j] = int(self.y[j])

self.pos_grid = zeros((self.x_axis,self.y_axis,2))
for i in range(self.x_axis):
    for j in range(self.y_axis):
        for k in range(self.number):
            if self.x[k] == i and self.y[k] == j:
                self.pos_grid[i][j][0] = 0
                self.pos_grid[i][j][1] = self.initial_tokens



				  

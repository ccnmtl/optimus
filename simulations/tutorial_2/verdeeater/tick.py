import Numeric
from Numeric import * 
import MLab

for i in range(self.x_axis):
    for j in range(self.y_axis):
        if self.pos_grid[i][j][1] > 0:
            if self.pos_grid[i][j][0] > self.lifespan or self.pos_grid[i][j][1] <= 1:
                self.pos_grid[i][j] = [0,0]
            else:
                self.pos_grid[i][j][1] -= 1
                self.pos_grid[i][j][0] += 1


self.already_grid = zeros((self.x_axis,self.y_axis))

foodgrid = self.organizer.get_var("verde","desire_grid",[0])                
self.food_pos_grid = self.organizer.get_var("verde","pos_grid",[0])                
             
self.food2_pos_grid = self.organizer.get_var("verdefood","pos_grid",[0])                

import copy    
for x in range(self.x_axis):
        for y in range(self.y_axis):
            e=0
            w=0
            n=0
            s=0
            max = 0
            target = [0,0]
            if self.already_grid[x][y] == 0 and self.pos_grid[x][y][1] != 0:
                if x > 0:
                    e = foodgrid[x-1][y]
                    if e > max:
                        max = e
                        target = [x-1,y]
                if x < self.x_axis - 1:
                    w = foodgrid[x+1][y]
                    if w > max:
                        max = w
                        target = [x+1,y]
                if y > 0:
                    s = foodgrid[x][y-1]
                    if s > max:
                        max = s
                        target = [x,y-1]
                if y < self.y_axis - 1:
                    n = foodgrid[x][y+1]
                    if n > max:
                        max = n
                        target = [x,y+1]
                if max == 0:
                    target = [x,y]
                if self.food_pos_grid[target[0]][target[1]][1] == 0 and self.food2_pos_grid[target[0]][target[1]][1] == 0 :
                    if self.pos_grid[target[0]][target[1]][1] == 0:            
                        self.pos_grid[target[0]][target[1]] = copy.deepcopy(self.pos_grid[x][y])
                        self.pos_grid[x][y] = [0,0]
                        self.already_grid[x][y] = 1
                        self.already_grid[target[0]][target[1]] = 1
                    elif (target[0] != x or target[1] != y) and (target[0] != 0 or target[1] != 0) and self.pos_grid[x][y][0] > self.rep_age and self.pos_grid[target[0]][target[1]][0] > self.rep_age:
                        z1 = MLab.rand(1) * self.x_axis
                        z2 = MLab.rand(1) * self.y_axis
                        z1 = int(z1[0])
                        z2 = int(z2[0])
                        if self.food_pos_grid[z1][z2][1] == 0 and self.food2_pos_grid[z1][z2][1]==0 and self.pos_grid[z1][z2][1]==0:
                            self.pos_grid[z1][z2][0] = 0
                            self.pos_grid[z1][z2][1] = (self.pos_grid[x][y][1] + self.pos_grid[target[0]][target[1]][1])/2
                        
                elif self.food2_pos_grid[target[0]][target[1]][1] == 0:
                        self.pos_grid[x][y][1] += (self.food_pos_grid[target[0]][target[1]][1]/10 + 1)
                        self.pos_grid[target[0]][target[1]] = copy.deepcopy(self.pos_grid[x][y])
                        self.pos_grid[x][y] = [0,0]
                        self.food_pos_grid[target[0]][target[1]] = [0,0]
                       
                else:
                    temp = "temp"
                    
                    
        
        
        

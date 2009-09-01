for i in range(self.x_axis):
    for j in range(self.y_axis):
        if self.pos_grid[i][j][1] != 0:
            self.pos_grid[i][j][0] += 1
            self.pos_grid[i][j][1] += 1

self.desire_grid = MLab.rand(self.x_axis,self.y_axis) * 0
for x in range(self.x_axis):
    for y in range(self.y_axis):
        value = 0
        for x2 in range(self.x_axis):
            for y2 in range(self.y_axis):
                value += self.pos_grid[x2][y2][1] / (1 + math.sqrt(pow(abs(x-x2),2) + pow(abs(y-y2),2)))
        self.desire_grid[x][y] = value    

for i in range(len(self.dots)):
    self.canvas.delete(self.dots[i])


self.dots = []
     
self.x_scaler = 550 / self.x_axis
self.y_scaler = 450 / self.y_axis
for xx in range(0,self.x_axis):
	for yy in range(0,self.y_axis):
		  if self.food_pos_grid[xx][yy][1] != 0: 
                              self.dots.append(self.canvas.create_rectangle(50 + self.x_scaler * (xx-1),50 + self.y_scaler * (yy-1),50 + self.x_scaler * (xx - (self.x_scaler-1.0)/self.x_scaler),50 + self.y_scaler * (yy - (self.y_scaler-1.0)/self.y_scaler),
                                     fill="green", outline = "green", width = self.food_pos_grid[xx][yy][1]/10))
                  elif self.pos_grid[xx][yy][1] != 0:  
                              self.dots.append(self.canvas.create_rectangle(50 + self.x_scaler * (xx-1),50 + self.y_scaler * (yy-1),50 + self.x_scaler * (xx - (self.x_scaler-1.0)/self.x_scaler),50 + self.y_scaler * (yy - (self.y_scaler-1.0)/self.y_scaler),
                                     fill="blue", outline = "blue", width = self.pos_grid[xx][yy][1]/7))
                  elif self.food2_pos_grid[xx][yy][1] != 0:
                              self.dots.append(self.canvas.create_rectangle(50 + self.x_scaler * (xx-1),50 + self.y_scaler * (yy-1),50 + self.x_scaler * (xx - (self.x_scaler-1.0)/self.x_scaler),50 + self.y_scaler * (yy - (self.y_scaler-1.0)/self.y_scaler),
                                     fill="red", outline = "red", width = self.food2_pos_grid[xx][yy][1]/10))
                    
    

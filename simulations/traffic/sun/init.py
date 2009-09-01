self.full = zeros((162,122)).astype('f')

# create an array that matches the screen dimensions
# to put pixels in for display
self.grid = zeros((640,480,3))

# m is an array to store the pollution emitted by the cars
self.m = zeros((160,120)).astype('f')

# diagonal neighbor diffusion percentage
self.diagdiff = 1.0 - self.hvdiff

# the actual percentage of mass that diffuses to a single h/v neighbor
self.hvfactor = self.diffused * self.hvdiff / 4.0 

# the actual percentage of mass that diffuses to a single diagonal neighbor
self.diagfactor = self.diffused * self.diagdiff / 4.0 

self.cnt = 0

ctplus1 = self.full[1:-1,1:-1]
ctplus1 = ctplus1.astype('b')

scaleup = scale2x(ctplus1)
scaleup = scale2x(scaleup)
scaleup = 255 - scaleup

self.debug(scaleup[40,40])
self.grid[:,:,0] = scaleup
self.grid[:,:,1] = scaleup
self.grid[:,:,2] = scaleup

surfarray.blit_array(self.screen,self.grid)

self.grid = zeros((640, 480,3))
self.full = ones((162,122)) * 255
self.full = self.full.astype('b')
self.sugar = self.full[1:-1,1:-1]

self.full[0,] = self.full[-2,]
self.full[-1,] = self.full[1,]
self.full[:,0] = self.full[:,-2]
self.full[:,-1] = self.full[:,1]
# corners
self.full[0,0] = self.full[-2,-2]
self.full[0,-1] = self.full[-2,1]
self.full[-1,0] = self.full[1,-2]
self.full[-1,-1] = self.full[1,1]


self.cnt = 0

size = array(self.sugar.shape)*2
scaleup = zeros(size)
scaleup[::2,::2] = self.sugar
scaleup[1::2,::2] = self.sugar
scaleup[:,1::2] = scaleup[:,::2]

r = scaleup
size = array(r.shape)*2
scaleup = zeros(size)
scaleup[::2,::2] = r
scaleup[1::2,::2] = r
scaleup[:,1::2] = scaleup[:,::2]

self.grid[:,:,0] = scaleup
self.grid[:,:,1] = scaleup
self.grid[:,:,2] = scaleup

surfarray.blit_array(self.background,self.grid)

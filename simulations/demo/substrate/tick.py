self.sugar = self.full[1:-1,1:-1].astype('i')

n = self.full[0:-2,1:-1].astype('i')
s = self.full[2:,1:-1].astype('i')
e = self.full[1:-1,2:].astype('i')
w = self.full[1:-1,0:-2].astype('i')

ave = (self.sugar + n + s + e + w) / 5
delta = (ave - self.sugar) / 50
self.sugar = self.sugar + delta
self.sugar = where(delta < 1,ave,self.sugar)

self.sugar = where(self.sugar > 255, 255, self.sugar)
self.sugar = self.sugar.astype('b')

self.cnt = self.cnt + 1


# update edges
self.full[1:-1,1:-1] = self.sugar
self.full[0,] = self.full[-2,]
self.full[-1,] = self.full[1,]
self.full[:,0] = self.full[:,-2]
self.full[:,-1] = self.full[:,1]
# corners
self.full[0,0] = self.full[-2,-2]
self.full[0,-1] = self.full[-2,1]
self.full[-1,0] = self.full[1,-2]
self.full[-1,-1] = self.full[1,1]


if (self.cnt % self.display_every) == 0:
    r = self.sugar 
    self.debug("displaying")
    size = array(r.shape)*2
    scaleup = zeros(size)
    scaleup[::2,::2] = r
    scaleup[1::2,::2] = r
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

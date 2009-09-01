# variables that are defined in federate.xml
# self.h:  mixing height in m (1000)
# dx: cell width in m (50)
# dy: cell height in m (50)
# vd: deposition velocity (0.1)

seconds_per_tick = 0.2

# wind velocity
wind_x = self.wind_x * (seconds_per_tick) 
wind_y = self.wind_y * (seconds_per_tick)

# define neighborhood
c = self.full[1:-1,1:-1]
n = self.full[0:-2,1:-1]
s = self.full[2:,1:-1]
e = self.full[1:-1,2:]
w = self.full[1:-1,0:-2]


# define constants:
a0 = 1.0 
a1 = wind_x / self.dx
a2 = -1 * wind_x / self.dx
a3 = wind_y / self.dy
a4 = -1 * wind_y / self.dy
a5 = 1 - (self.vd * seconds_per_tick / self.h)

d1 = (w - c) * self.diffusion_rate / (self.dx * self.dx)
d2 = (e - c) * self.diffusion_rate / (self.dx * self.dx)
d3 = (n - c) * self.diffusion_rate / (self.dy * self.dy)
d4 = (s - c) * self.diffusion_rate / (self.dy * self.dy)

# calculate diffusion

lost = self.diffusion_rate
# amount that comes in should be divided evenly between neighbors
gained = self.diffusion_rate / 4.0

# add diffusion to constants
#a1 = a1 + gained
#a2 = a2 + gained
#a3 = a3 + gained
#a4 = a4 + gained
#a5 = a5 - lost

# calculate the new values
ctplus1 = (a0 * self.m) + (a1 * w) + d1 + (a2 * e) + d2 + (a3 * n) + d3 + (a4 * s) + d4 + (a5 * c) 

# basic sanity check to make sure we don't have any cells with
# negative pollution levels
ctplus1 = where(ctplus1 < 0.0, 0.0, ctplus1)

self.ctplus1 = ctplus1

# put it back into the full grid
self.full[1:-1,1:-1] = ctplus1.astype('f')
# clear m out
self.m = zeros((160,120)).astype('f')

# since we have background pollution levels, we need to duplicate the edges
# so we don't get weird banding stuff

#self.full[0,:] = self.full[1,:]
#self.full[-1,:] = self.full[-2,:]
#self.full[:,0] = self.full[:,1]
#self.full[:,-1] = self.full[:,-2]

self.datafile = open(self.data_dir + os.sep + "%04d" % self.cnt + ".csv","w")
for i in xrange(160):
    self.datafile.write(",".join([str(n) for n in self.ctplus1[i]]) + "\n")
self.datafile.close()

self.cnt = self.cnt + 1

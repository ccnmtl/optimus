# variables that are defined in federate.xml
# self.h:  mixing height in m (1000)
# dx: cell width in m (50)
# dy: cell height in m (50)
# vd: deposition velocity (0.1)

# wind velocity
wind_x = self.wind_x
wind_y = self.wind_y

# define neighborhood
c = self.full[1:-1,1:-1]
n = self.full[0:-2,1:-1]
s = self.full[2:,1:-1]
e = self.full[1:-1,2:]
w = self.full[1:-1,0:-2]


# define constants:
a0 = 1.0 / (self.h * self.dx * self.dy)
a1 = wind_x / self.dx
a2 = -1 * wind_x / self.dx
a3 = wind_y / self.dy
a4 = -1 * wind_y / self.dy
a5 = 1 - (self.vd / self.h)

# calculate diffusion

lost = self.diffusion_rate
# amount that comes in should be divided evenly between neighbors
gained = self.diffusion_rate / 4.0

# add diffusion to constants
a1 = a1 + gained
a2 = a2 + gained
a3 = a3 + gained
a4 = a4 + gained
a5 = a5 - lost

# calculate the new values
ctplus1 = (a0 * self.m) + (a1 * w) + (a2 * e) + (a3 * n) + (a4 * s) + (a5 * c) 

sum = 0
for i in range(160):
    for j in range(120):
       sum = sum + ctplus1[i,j] 
ave = sum / (160 * 120)

self.debug(ave)

# basic sanity check to make sure we don't have any cells with
# negative pollution levels
ctplus1 = where(ctplus1 < 0.0, 0.0, ctplus1)

self.ctplus1 = ctplus1
# put it back into the full grid
self.full[1:-1,1:-1] = ctplus1.astype('f')
# clear m out
self.m = zeros((160,120)).astype('f')

self.cnt = self.cnt + 1

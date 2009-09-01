# we need to force the self.x and self.y arrays to the right
# length if the number of verdes has been reduced
if len(self.x) > self.number:
    self.x = self.x[:self.number]
    self.y = self.y[:self.number]

# create new Numeric arrays for each neighbor location
c = zeros(self.number).astype('f')
n = zeros(self.number).astype('f')
s = zeros(self.number).astype('f')
e = zeros(self.number).astype('f')
w = zeros(self.number).astype('f')


# populate the neighbors with pollution data
for i in range(self.number):
    x = self.x[i] / 4
    y = self.y[i] / 4
    x = int(x + 1)
    y = int(y + 1)
    c[i] = self.pollution[x,y]
    n[i] = self.pollution[x,y - 1]
    s[i] = self.pollution[x,y + 1]
    e[i] = self.pollution[x + 1,y]
    w[i] = self.pollution[x - 1,y]

# calculate horizontal component
dx = zeros(self.number)
dx = where(w < c, dx - 1,dx)
dx = where(e < c, dx + 1,dx)
dx = where((dx == 0) and (e != c), where(e < w, dx + 1, dx - 1), dx)

# calculate vertical component
dy = zeros(self.number)
dy = where(n < c, dy - 1,dy)
dy = where(s < c, dy + 1,dy)
dy = where((dy == 0) and (n != c), where(n < s, dy - 1, dy + 1), dy)

# update position
self.x = self.x + dx
self.y = self.y + dy

# ensure that we haven't moved any off the grid
self.x = where(self.x > 639, 639, self.x)
self.x = where(self.x < 1, 1, self.x)
self.y = where(self.y > 479, 479, self.y)
self.y = where(self.y < 1, 1, self.y)


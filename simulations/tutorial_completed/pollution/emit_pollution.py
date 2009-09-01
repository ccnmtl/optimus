# need to scale it properly

xs = attrs['x'].astype('i') / 4
ys = attrs['y'].astype('i') / 4
pollution = attrs['pollution']

n = len(xs)

for i in range(n):
    x = xs[i]
    y = ys[i]

    if x > 159: x = 159
    if y > 119: y = 119
    if x < 0: x = 0
    if y < 0: y = 0
    
    self.m[x,y] = self.m[x,y] + pollution[i]
self.m = where(self.m > 255.0, 255.0, self.m)

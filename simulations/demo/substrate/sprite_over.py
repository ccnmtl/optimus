# need to scale it properly

xs = attrs['x'].tolist()
ys = attrs['y'].tolist()

n = len(xs)
for i in range(n):
    x = xs[i]
    y = ys[i]
    v = self.full[x,y] - 50
    if v < 0:
        v = 0
    self.full[x,y] = v




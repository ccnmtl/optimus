num = self.numsprites

x = MLab.rand(num) * 640
y = MLab.rand(num) * 480
dx = (MLab.rand(num) * 10) - 5
dy = (MLab.rand(num) * 10) - 5

self.x = x.astype('i')
self.y = y.astype('i')
self.dx = dx.astype('i')
self.dy = dy.astype('i')

self.full = MLab.rand(162,122) * 255
self.full = self.full.astype('i')

self.m = zeros((160,120)).astype('i')

self.ctplus1 = self.full[1:-1,1:-1]
self.display_array(self.ctplus1)

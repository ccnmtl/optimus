c = self.full[1:-1,1:-1]

ctplus1 = c + self.growback_rate
ctplus1 = where(ctplus1 > 255, 255, ctplus1)

self.ctplus1 = ctplus1
self.full[1:-1,1:-1] = ctplus1

ctplus1 = self.full[1:-1,1:-1]
eaten = attrs['eaten']
ctplus1 = ctplus1 - eaten
ctplus1 = where(ctplus1 < 0, 0, ctplus1)
self.ctplus1 = ctplus1
self.full[1:-1,1:-1] = ctplus1

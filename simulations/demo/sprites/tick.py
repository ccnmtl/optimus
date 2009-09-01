self.debug("updating sprites")
self.x = self.x + self.dx
self.y = self.y + self.dy

self.dx = where((self.x >= 640) or (self.x < 0), -1 * self.dx, self.dx)
self.dy = where((self.y >= 480) or (self.y < 0), -1 * self.dy, self.dy)


self.organizer.generate_event(OptimusEvent("sprite_over",{'x' : self.x / 4,
                                                          'y' : self.y / 4}))


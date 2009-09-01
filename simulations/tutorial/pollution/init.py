self.full = zeros((162,122)).astype('f')

# create an array that matches the screen dimensions
# to put pixels in for display
self.grid = zeros((640,480,3))

# m is an array to store the pollution emitted by the cars
self.m = zeros((160,120)).astype('f')

self.cnt = 0

self.ctplus1 = self.full[1:-1,1:-1]

# invert it (ie, make high pollution values black and low white)
self.image = 255.0 - self.ctplus1

# convert it to a Tk Image that can be displayed on the canvas
self.im = array2image(self.image.astype('b'))
self.im2 = self.im.resize((640,480))
self.img = ImageTk.PhotoImage(self.im2)

self.canvas_image = self.canvas.create_image(0, 0, anchor=NW, image=self.img)
self.canvas.tag_lower(self.canvas_image)

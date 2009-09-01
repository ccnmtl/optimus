self.full = zeros((162,122)).astype('f') + self.background_pm10


# create an array that matches the screen dimensions
# to put pixels in for display
self.grid = zeros((640,480,3))

# m is an array to store the pollution emitted by the cars
self.m = zeros((160,120)).astype('f')

self.cnt = 0

self.ctplus1 = self.full[1:-1,1:-1]

self.image = 255.0 - self.ctplus1

self.im = array2image(self.image.astype('b'))
self.im2 = self.im.resize((640,480))

self.bg = Image.open(self.load_image('huntspoint_crop2.jpg'))
black = zeros((480,640)).astype('b')
self.black = array2image(black)
self.black = Image.merge('RGB',[self.black,self.black,self.black])
self.merged = Image.composite(self.bg,self.black,self.im2)
self.img = ImageTk.PhotoImage(self.merged)


#self.img = ImageTk.PhotoImage(self.im2)

self.canvas_image = self.canvas.create_image(0, 0, anchor=NW, image=self.img)
self.canvas.tag_lower(self.canvas_image)

# make sure we have a directory to dump our CSV files in
try:
    os.makedirs(self.data_dir)
except OSError:
    pass

# clear out any old ones

for f in os.listdir(self.data_dir):
    if f[-4:] == ".csv":
        os.unlink(self.data_dir + os.sep + f)
        

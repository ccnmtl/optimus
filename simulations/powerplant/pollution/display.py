
if (self.cnt % self.display_every) == 0:
    ctplus1 = self.ctplus1.copy()

    smallest = ctplus1[0,0]
    largest = smallest
    for i in ravel(ctplus1):
        if i > largest:
            largest = i
        if i < smallest:
            smallest = i

    if largest != smallest:
        scale = 255.0 / (largest - smallest)
        ctplus1 = (ctplus1 - smallest) * scale

    # ensure that everything is within a displayable range
    ctplus1 = where(ctplus1 < 0.0, 0.0, ctplus1)
    ctplus1 = where(ctplus1 > 255.0, 255.0, ctplus1)

    ctplus1 = ctplus1.astype('b')

    ctplus1 = 255 - ctplus1

    self.image = transpose(ctplus1)
    self.im = array2image(self.image.astype('b'))
    self.im2 = self.im.resize((640,480))
    self.im2.mode = 'RGBA'
    self.merged = Image.composite(self.bg,self.black,self.im2)
    self.img = ImageTk.PhotoImage(self.merged)

    #self.img = ImageTk.PhotoImage(self.im2)
    self.canvas.itemconfigure(self.canvas_image,image=self.img)



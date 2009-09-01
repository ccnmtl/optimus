#!/usr/bin/env python

import Image, ImageDraw, MLab
from Numeric import *
from types import *

class TileEngineCanvas:
    def __init__(self,r_width,r_height,p_width,p_height):
        self.r_width = r_width
        self.r_height = r_height
        self.p_width = p_width
        self.p_height = p_height
        self.layers = []
        self.image = Image.new("RGBA",(p_width,p_height),"#fff")

    def get_scale(self):
        """ returns the number of pixels / meter """
        return (self.p_width / self.r_width,
                self.p_height / self.r_height)

    def as_image(self):
        """ returns PIL Image of all the layers of the canvas
        combined """
        self.clear()
        for l in self.layers:
            l.draw()
        return self.image

    def clear(self):
        self.image = Image.new("RGBA",(self.p_width,self.p_height),"#fff")

    def default_grid(self):
        """ draws a nice little grid as the default when nothing is loaded
        """
        self.clear()
        w = 10
        h = 10
        x = 0
        draw = ImageDraw.Draw(self.image)
        while x < self.p_width:
            draw.line([(x,0),(x,self.p_height)],fill=128)
            x += w

    def set_layers(self,layers=[]):
        self.layers = layers

    def set_r_size(self,w,h):
        self.r_width = w
        self.r_height = h

    def set_p_size(self,w,h):
        self.p_width = w
        self.p_height = w

class UnknownMapping(Exception):
    pass

import cPickle
ImageCache = {}

def get_image(v,size,map):
    str = cPickle.dumps((v,size,map))
    if not ImageCache.has_key(str):
        colour = map[v]
        img = None
        if type(colour) == TupleType:
            img = Image.new('RGBA',size,colour)
        elif type(colour) == IntType:
            img = Image.new('RGBA',size,(colour,colour,colour))
        elif type(colour) == StringType:
            if colour[0] == "#":
                # hex colour code
                img = Image.new('RGBA',size,colour)
            else:
                # it must be an image filename.
                image = Image.open(colour)
                img = image.resize(size)
        else:
            raise UnknownMapping
        ImageCache[str] = img
    return ImageCache[str]

class Layer:
    
    def draw(self):
        """ should be overridden with a method that draws the layer on
        self.canvas.image """
        pass
        
    def get_alpha(self):
        return self.alpha
    
    def set_alpha(self,alpha):
        self.alpha = alpha

    def get_size(self):
        return (self.width, self.height)
    
    def get_pixel_size(self):
        (xscale, yscale) = self.canvas.get_scale()
        (w,h) = self.get_size()
        return (w * xscale, h * yscale)

    def get_offset(self):
        return (self.x_offset, self.y_offset)

    def get_pixel_offset(self):
        (xscale, yscale) = self.canvas.get_scale()
        (x,y) = self.get_offset()
        return (x * xscale, y * yscale)
        
    def get_mask(self):
        if self.mask == None:
            s = self.get_pixel_size()
            self.mask = Image.new("L",s,self.alpha)
        return self.mask

class TileLayer(Layer):
    def __init__(self, canvas, width, height, data, map, x_offset=0,
            y_offset=0, alpha=256):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.data = data
        self.map = map
        self.alpha = alpha
        self.type = "tile"
        self.mask = None

    def get_cell_size(self):
        """ returns the size of a single cell in meters """
        (w,h) = self.data.shape
        return (self.width / w, self.height / h)

    def get_pixel_cell_size(self):
        """ returns size of cell in pixels on the current canvas """
        (xscale,yscale) = self.canvas.get_scale()
        (w,h) = self.get_cell_size()
        (w,h) = (w * xscale, h * yscale)
        return (w,h)
    
    def get_cell_image(self,i,j):
        """ returns an image object for the specified cell """
        v = int(self.data[i,j])
        s = self.get_pixel_cell_size()
        return get_image(v,s,self.map)
    
    def get_cell_mask(self):
        """ returns an image of the right size that can be used as a
        mask"""
        if self.mask == None:
            s = self.get_pixel_cell_size()
            self.mask = Image.new("L",s,self.get_alpha())            
        return self.mask

    def draw(self):
        a = self.get_cell_mask()
        image = self.canvas.image
        (w,h) = self.data.shape
        (xoff,yoff) = self.get_pixel_offset()
        (cwidth,cheight) = self.get_pixel_cell_size()
        for i in range(w):
            for j in range(h):
                px = (i * cwidth) + xoff
                py = (j * cheight) + yoff
                img = self.get_cell_image(i,j)
                image.paste(img,(px,py),a)

class Sprite:
    def __init__(self,x,y,value,w=1,h=1,layer = None):
        self.x = x
        self.y = y
        self.value = value
        self.layer = layer
        self.w = w
        self.h = h
        self.mask = None
        
    def set_layer(self,layer):
        self.layer = layer
        
    def moveto(self,x,y):
        self.x = x
        self.y = y

    def position(self):
        return (self.x,self.y)

    def pixel_position(self):
        (xscale,yscale) = self.layer.canvas.get_scale()
        (x,y) = self.position()
        return (x * xscale, y * yscale)

    def get_size(self):
        return (self.w, self.h)

    def get_pixel_size(self):
        (xscale,yscale) = self.layer.canvas.get_scale()
        (width,height) = self.get_size()
        return (width * xscale, height * yscale)
    
    def as_image(self):
        img = get_image(self.value,self.get_pixel_size(),self.layer.map)
        return img

    def get_mask(self):
        """ returns an image of the right size that can be used as a
        mask"""
        if self.mask == None:
            s = self.get_pixel_size()
            self.mask = Image.new("L",s,self.layer.alpha)            
        return self.mask

    

    def draw(self):
        pos = self.pixel_position()
        image = self.layer.canvas.image
        a = self.get_mask()
        image.paste(self.as_image(),pos,a)
        

class SpriteLayer(Layer):
    def __init__(self, canvas, width, height, sprites, map, alpha = 0):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.sprites = sprites
        self.map = map
        self.alpha = alpha
        self.type = "sprite"
        self.mask = None
        for s in self.sprites:
            s.set_layer(self)

    def draw(self):
        bg = self.canvas.image
        for s in self.sprites:
            s.draw()
            
class ImageLayer (Layer):
    """ a layer that just has a single image. handy for backgrounds. """
    def __init__(self,canvas,width,height,img,alpha=256,x=0,y=0):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.img = img
        self.alpha = alpha
        self.x_offset = x
        self.y_offset = y
        self.mask = None

    def draw(self):
        a = self.get_mask()
        s = self.get_pixel_size()
        img = Image.open(self.img)
        img = img.resize(s)
        self.canvas.image.paste(img,self.get_pixel_offset(),a)    
  
  
if __name__ == "__main__":
    c = TileEngineCanvas(40,30,400,300)
    
    map = range(256)
    for i in range(0,150):
        map[i] = "red.png"
    for i in range(150,170):
        map[i] = "#f60"
    a = MLab.rand(20,15) * 255
    a = a.astype('b')

    b = MLab.rand(4,3) * 255
    b = b.astype('b')

    map2 = range(256)
    for i in range(128):
        map2[i] = "green.png"
    for i in range(128,200):
        map2[i] = "blue.png"
    for i in range(200,256):
        map2[i] = "red.png"
        
    sprites = []
    import random
    for i in range(30):
        v = random.randint(0,255)
        x = random.randint(0,40)
        y = random.randint(0,30)
        s = Sprite(x,y,v,1,1)
        sprites.append(s)
        
    
    sl = SpriteLayer(c,40,30,sprites,map2,256)

    t = TileLayer(c,40,30,a,map,0,0,128)
    t2 = TileLayer(c,40,30,b,range(256),2,3,128)

    bg = ImageLayer(c,40,30,"bg.png",256,3,2)
    c.set_layers([bg,sl])
    i = c.as_image()
    i.show()
    i.save('output.png')


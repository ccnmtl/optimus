from random import Random
import urllib,urlparse,os
import re, random
from xml.dom.minidom import Document, parseString
from Numeric import *
import MLab
import csv
import sys
from Tkinter import *
from dijkstra import Dijkstra
import traceback
from pathjoin import path_join

import Image
import ImageTk

from Attribute import Attribute
from OptimusEvent import OptimusEvent
from EventHandler import EventHandler

def array2image(a):
    if a.typecode() == UnsignedInt8:
        mode = "L"
    elif a.typecode() == Float32:
        mode = "F"
    else:
        raise ValueError, "unsupported image mode"
    return Image.fromstring(mode, (a.shape[1], a.shape[0]), a.tostring())


def scale2x(a):
    size = array(a.shape)*2
    scaleup = zeros(size)
    scaleup[::2,::2] = a
    scaleup[1::2,::2] = a
    scaleup[:,1::2] = scaleup[:,::2]
    return scaleup

def scale4x(a):
    return scale2x(scale2x(a))

class Federate:
    """represents a Federate in OPTIMUS. a Federate
    is like a 'layer' or 'component' of a simulation.
    it should simulate a discrete system. if it implements
    the interface correctly, it should be able to interoperate
    with other federates"""
    def __init__(self,organizer,canvas,file):
        """creates a new federate object.
        pass in a reference to the organizer, the tile engine,
        and the name (URI actually) of the xml file with the
        federate's specification."""
        base = ""
        if file[0:5] != "file:":
            base = file[file.rfind("/")]
        file = path_join(base,file)
            
        self.organizer = organizer
        self.debug("creating new federate from %s" % file)
        # create local references to the organizer, engine
        
        self.canvas = canvas

        # set some fields to default values
        self.name                  = 'undefined'
        self.system                = 'undefined'
        self.description           = ""
        self.event_handlers        = {}
        self.query_region_handlers = {}
        self.query_point_handlers  = {}
        self.attributes            = {}

        self.graphical = 0 # If this is set to '1', this federate will register with the TileEngine.
        self.gridColors = [] # this will be set up by the TileEngine if this federate registers with it.
        self.file                  = file        
        # parse the xml file and set all our attributes
        uri_base = file
        try:
            xmlstring = "".join(urllib.urlopen(file).readlines())
        except:
            self.error("couldn't open federate file: %s" % file)
            return
        try:
            doc = parseString(xmlstring)
        except:
            self.error("%s is not well-formed xml" % file)
            return

        (scheme,netloc,base_path,query,fragment) = urlparse.urlsplit(uri_base)
        base_path = "/".join(base_path.split("/")[:-1]) + "/"
        uri_base = urlparse.urlunsplit([scheme,netloc,base_path,"",""])
        if scheme == 'file':
            if not base_path[0] == '/':
                cwd = os.getcwd()
                base_path = "%s%s%s" % (cwd,os.sep,base_path)
                uri_base = urlparse.urlunsplit([scheme,netloc,base_path,query,fragment])
                pattern = re.compile(r"C:\\")
                uri_base = pattern.sub("",uri_base)
        if scheme != 'http':
            base_path = base_path.replace("/",os.sep)
            sys.path.append(base_path.encode())
        
        # 'federate' should be the root element of the document
        try:
            root           = doc.getElementsByTagName('federate')[0]
        except:
            self.error("no federate root element in %s" % file)
        self.name      = root.getAttribute('name')
        self.system    = root.getAttribute('system')
        self.graphical = root.getAttribute('graphical')

        try:
            handlers       = root.getElementsByTagName('handlers')[0]
        except:
            self.error("missing handlers element in %s" % file)
        ev_handlers    = handlers.getElementsByTagName('event')
        errorcounter = 40
        # gather up the event handlers
        for evh in ev_handlers:
            self.add_event_handler(evh,uri_base)
            
        # gather up the query-region handlers
        for qrh in handlers.getElementsByTagName('query-region'):
            param = qrh.getAttribute('param')
            file = qrh.getAttribute('file')
            code = ""
            if file == "":
                code = qrh.childNodes[0].data
            else:
                if not re.match("(http:|\/|file:)",file):
                    file = urlparse.urljoin(uri_base,file)
                code = "".join(urllib.urlopen(file).readlines())
            self.query_region_handlers[param] = code

        # gather up the query-point handlers
        for qph in handlers.getElementsByTagName('query-point'):
            param = qph.getAttribute('param')
            file = qph.getAttribute("file")
            code = ""
            if file == "":
                code = qph.childNodes[0].data
            else:
                if not re.match("(http:|\/|file:)",file):
                    file = urlparse.urljoin(uri_base,file)
                code = "".join(urllib.urlopen(file).readlines())
            self.query_point_handlers[param] = code

        # gather up bound variables
        self.bound_variables = []
        try:
            bindings       = root.getElementsByTagName('bindings')[0]

            for var in bindings.getElementsByTagName('variable'):
                binding = {}
                binding["localname"] = var.getAttribute('localname')
                binding["system"]    = var.getAttribute('system')
                binding["variable"]  = var.getAttribute('variable')
                binding["default"]   = var.getAttribute('default')
                self.bound_variables.append(binding)
        except:
            # probably means that there is no <binding/> element
            pass

        # gather up the attributes.
        # attributes are stored as the type you define
        attributes_root = root.getElementsByTagName('attributes')[0]
        self.attr_idx = 0
        for attribute in attributes_root.getElementsByTagName('attribute'):
            self.add_attribute(attribute)

        #unlink the DOM object
        doc.unlink()

        self.uri_base = uri_base
        # then register ourselves
        self.organizer.register(self)

        # give ourselves an 'init' event
        self.handle_event(OptimusEvent('init',{}))
        
    def add_event_handler(self,evh,uri_base):
        type = evh.getAttribute('type')
        file = evh.getAttribute("file")
        code = ""
        if file == "":
            # if no file attribute is specified, it must
            # be inline code
            code = evh.childNodes[0].data
        else:
            # get the code from the specified file
            if not re.match("(http:|\/|file:)",file):
                # the uri appears to be relative, so we
                # append it to the base uri
                file = urlparse.urljoin(uri_base,file)
            try:
                code = "".join(urllib.urlopen(file).readlines())
            except:
                self.error("couldn't open file %s" % file)
        code = code.replace("\r\n", "\n")

        self.event_handlers[type] = EventHandler(self,type,code,file)
       
    def add_new_event_handler(self,type,code):
        self.event_handlers[type] = EventHandler(self,type,code)

    def display_array(self,a):
        a = transpose(a)
        self.im = array2image(a.astype('b'))
        self.im2 = self.im.resize((640,480))
        self.img = ImageTk.PhotoImage(self.im2)
        if hasattr(self,'canvas_image'):
            self.canvas.itemconfigure(self.canvas_image,image = self.img)
        else:
            self.canvas_image = self.canvas.create_image(0,0, anchor=NW, image = self.img)
            self.canvas.tag_lower(self.canvas_image)
        
    def add_attribute(self,attribute):
        attr_varname     = attribute.getAttribute('varname')
        attr_name        = attribute.getAttribute('name')
        attr_type        = attribute.getAttribute('type')
        attr_description = attribute.getAttribute('description')
        attr_label       = attribute.getAttribute('label')
        attr_fixed       = attribute.getAttribute('fixed')

        allowed_values = []
        allowed_default = ""
        if attr_fixed == "choice":
            for allowed in attribute.getElementsByTagName('allowed'):
                allowed_value = allowed.getAttribute("value")
                allowed_label = allowed.getAttribute("label")
                if allowed.getAttribute("default") == "default":
                    allowed_default = allowed_value
                allowed_values.append((allowed_value,allowed_label))
            if allowed_default == "":
                allowed_default = allowed_values[0][0]
        
        typefunc = str
        if (attr_type == "float"):
            typefunc = float
        elif (attr_type == "int" or attr_type == "integer"):
            typefunc = int

        attr_default = typefunc(attribute.getAttribute('default'))
        if attr_fixed == "choice":
            attr_default = allowed_default
            
        attr_min     = typefunc(attribute.getAttribute('min'))
        attr_max     = typefunc(attribute.getAttribute('max'))
        
        attr         = Attribute(attr_name,attr_varname,attr_type,attr_default,
                                 attr_min,attr_max,attr_label,attr_description,
                                 allowed_values)
        attr.order = self.attr_idx
        self.attr_idx += 1
        self.attributes[attr_varname] = attr
        setattr(self,attr_varname,attr.get())

    def unload(self):
        """removes the federate from OPTIMUS"""
        self.organizer.unregister(self)

    def load_image(self, name):
        self.debug("loading %s %s" % (self.uri_base,name))
        base_path = urlparse.urlsplit(self.uri_base)[2]
        path = base_path + name
        return open(path,"rb")

    def bind_variables(self):
        for v in self.bound_variables:
            value = self.organizer.get_var(v["system"],v["variable"],eval(v["default"]))
            setattr(self,v["localname"],value)

    def handle_event(self,event):
        """handles an event.
        Finds the event handler for the appropriate
        type (we should be able to assume that we have one
        since this will usually be called by the organizer
        and the organizer knows who can handle what events)
        and execs the code"""
        if self.event_handlers.has_key(event.type):
            self.debug("%s handling event %s" % (self.name,event.type))
            self.bind_variables()
            self.current_event = event
            attrs = event.attrs # this is available for the code to access
            try:
                exec self.event_handlers[event.type].code
            except (ArithmeticError, AssertionError, AttributeError, EOFError, EnvironmentError, Exception, FloatingPointError, IOError, ImportError, IndentationError, IndexError, KeyError, KeyboardInterrupt, LookupError, MemoryError, NameError, NotImplementedError, OSError, OverflowError, ReferenceError, RuntimeError, StandardError, SyntaxError, SystemError, SystemExit, TabError, TypeError, UnboundLocalError, UnicodeError, ValueError, ZeroDivisionError), x:
                self.error("Error in federate %s" % self.name)
                self.error("in event handler for %s" % event.type)
                self.error("line: %d" % traceback.extract_tb(sys.exc_info()[2])[1][1])
                if hasattr(x,'args'):
                    try:
                        self.error("error: %s" % x[0])
                    except IndexError:
                        self.error(x)
                        
                
            
    def handle_query_region(self,param):
        """passes off a query region request to the appropriate handler"""
        if self.query_region_handlers.has_key(param):
            exec self.query_region_handlers[param]
            
    def handle_query_point(self,param):
        """passes off a query point request to the appropriate handler"""
        if self.query_point_handlers.has_key(param):
            exec self.query_point_handlers[param]

    def get_var(self,var,default_value):
        """returns the value of a variable"""
        code = "returnvar = self.%s" % var
        if hasattr(self,var):
            returnvar = getattr(self,var)
        else:
            returnvar = default_value
        return returnvar

    def set_attribute(self, varname, value):
        """enforces boundary restrictions while setting an attribute of this federate.
        An attempt to go past the boundary results in the attribute being changed
        to the boundary value."""
        self.attributes[varname].set(value)

    def get_attribute(self, varname):
        """returns the requested attribute's value."""
        return self.attributes[varname].get()
        
    def debug(self,message):
        self.organizer.debug(message)
    def error(self,message):
        self.organizer.error(message)
    def warn(self,message):
        self.organizer.warn(message)

    def csv2numeric(self,filename,types):
        """ opens a csv file and reads it in to named
        Numeric arrays. the file must have the names of the
        columns on the first line

        types is an array of types to treat the columns as. eg, for a file like

        a,b
        1,2.3
        2,5.6
        3,7.84

        you would do

        data = self.csv2numeric("file.csv",[int,float])

        and data would look like:

        {'a': array([1 2 3]), 'b': array([2.3 5.6 7.84])}

        it can really only handle numerical datatypes. ie, you can't
        have strings or even alphabetical characters in the file other
        than the first header row. 

        """
        if not re.match("(http:|\/|file:)",filename):
            filename = urlparse.urljoin(self.uri_base,filename)
        file = urllib.urlopen(filename)
        arrays = []
        headers = []
        try:
            p = csv.parser()
            header_line = file.readline()
            fields = p.parse(header_line)
            for f in fields:
                arrays.append([])
                headers.append(f)
            while 1:
                line = file.readline()
                if not line:
                    break
                fields = p.parse(line)
                for i in range(len(fields)):
                    typecode = types[i]
                    try:
                        arrays[i].append(typecode(fields[i]))
                    except:
                        arrays[i].append(fields[i])
        except AttributeError:
            # must be using python 2.3
            reader = csv.reader(file)
            fields = reader.next()
            for f in fields:
                arrays.append([])
                headers.append(f)
            for row in reader:
                fields = row
                for i in range(len(fields)):
                    typecode = types[i]
                    try:
                        arrays[i].append(typecode(fields[i]))
                    except:
                        try:
                            arrays[i].append(fields[i])
                        except:
                            pass
        results = {}
        for i in range(len(headers)):
            results[headers[i]] = array(arrays[i])
        return results

    def readArray(self,filename):
        if not re.match("(http:|\/|file:)",filename):
            filename = urlparse.urljoin(self.uri_base,filename)
        try:
            from Scientific.IO.ArrayIO import readArray
            return readArray(filename)
        except ImportError:
            self.error("Scientific module not installed")

    def as_xml(self):
        from xml.sax import saxutils
        xml = """<?xml version="1.0"?>
        <federate name=%s system=%s>
        <description>
        %s
        </description>
        <attributes>""" % (saxutils.quoteattr(self.name),
                saxutils.quoteattr(self.system),
                saxutils.escape(self.description))
        for a in self.attributes:
            xml += self.attributes[a].as_xml()
        xml += """</attributes>
        <handlers>"""
        for e in self.event_handlers:
            xml += e.as_xml()
        xml += """</handlers>
        <bindings>"""
        for b in self.bound_variables:
            xml += """<variable localname=%s system=%s variable=%s
            default=%s />""" % (saxutils.quoteattr(b['localname']),
                    saxutils.quoteattr(b['system']),
                    saxutils.quoteattr(b['variable']),
                    saxutils.quoteattr(b['default']))
        xml += """</bindings></federate>"""
        return xml
    def save_xml(self):
        from tkFileDialog import asksaveasfilename
        filename = asksaveasfilename(filetypes=[("XML documents","*.xml"),
        ("All files","*")])
        file = open(filename,"w")
        file.write(self.as_xml())
        file.close()


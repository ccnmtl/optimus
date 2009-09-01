from XMLObject import *

class Allowed(XMLObject):
    value = StringAttribute()
    label = StringAttribute()

class Attribute(XMLObject):
    name    = StringAttribute()
    varname = StringAttribute()
    label   = StringAttribute(facultative=1)
    type    = StringAttribute()
    min     = StringAttribute(facultative=1)
    max     = StringAttribute(facultative=1)
    default = StringAttribute(facultative=1)
    allowed = ListNode('Allowed', facultative=1)
    
class Attributes(XMLObject):
    attributes = ListNode('Attribute', facultative=1)

class Event(XMLObject):
    type = StringAttribute()
    file = StringAttribute()

class Handlers(XMLObject):
    events = ListNode('Event', facultative=1)

class Variable(XMLObject):
    localname = StringAttribute()
    system    = StringAttribute()
    variable  = StringAttribute()
    default   = StringAttribute()

class Bindings(XMLObject):
    variables = ListNode('Variable')

class Federate(XMLObject):
    name        = StringAttribute()
    system      = StringAttribute()
    description = TextNode()
    attributes  = ListNode('Attributes', facultative=1)
    handlers    = ListNode('Handlers')
    bindings    = ListNode('Bindings', facultative=1)

    def add_attribute(self,name="",varname="",label="",type="", min="",
            max="", default="", allowed=[]):
        a = Attribute(name=name, varname=varname, label=label, type=type,
                min=min, max=max, default=default)
        self.attributes[0].attributes.append(a)

    def add_event_handler(self, type='', file=''):
        e = Event(type=type, file=file)
        self.handlers[0].events.append(e)

    def add_binding(self, localname='', system='', variable='',
            default=''):
        v = Variable(localname=localname, system=system, variable=variable,
                default=default)
        self.bindings[0].variables.append(v)


if __name__ == "__main__":
    xml = open("simulations/traffic/cars/federate.xml","r").read()
    f = Federate.fromXml(xml)
    f.add_attribute('foo','foo','the foo attribute','float','0.0','1.0','0.5')
    f.add_event_handler(type='foo', file='file.py')
    f.add_binding(localname='foo', system='foo', variable='foo', default='3')
    print f.toXml()

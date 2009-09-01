from XMLObject import *

class Federate(XMLObject):
    system = StringAttribute()
    file   = StringAttribute()

class Federates(XMLObject):
    federates = ListNode('Federate')

class Simulation(XMLObject):
    name = StringAttribute()
    description = TextNode()
    federates = ListNode('Federates')

    def add_federate(self, system='', file=''):
        f = Federate(system=system, file=file)
        self.federates[0].federates.append(f)

if __name__ == "__main__":
    xml = open("simulations/sugar/simulation.xml","r").read()
    s = Simulation.fromXml(xml)
    s.add_federate(system='foo', file='foo/federate.xml')
    print s.toXml()

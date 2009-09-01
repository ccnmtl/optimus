class Organizer:
    def __init__(self,optimus):
        self.optimus = optimus
        self.debug("creating new Organizer object")
        # create empty dictionaries for federates (key is system)
        self.federates = {}
        # and event_handlers (key is event type. contains a list of handler code)
        self.event_handlers = {}

    def debug(self,message):
        self.optimus.debug(message)
    def error(self,message):
        self.optimus.error(message)
    def warn(self,message):
        self.optimus.warn(message)

    def register(self,federate):
        """called by federates when they are first loaded.
        lets the organizer know that a new federate has been loaded.
        adds the federate to the list of known federates
        and adds it to the event handler list for any event that
        the federate is interested in"""
        self.federates[federate.system] = federate
        for event in federate.event_handlers.keys():
            if self.event_handlers.has_key(event):
                self.event_handlers[event].append(federate)
            else:
                self.event_handlers[event] = [federate]
                
    def unregister(self,federate):
        """ called when a federate is unloaded. need to implement.
        should just remove the federate from the list
        and remove its event handlers"""
        del self.federates[federate.system]
        for event in federate.event_handlers.keys():
            self.event_handlers[event].remove(federate)

    def generate_event(self,event):
        """passes the event on to whatever
        federates are interested in events of that type"""
        if self.event_handlers.has_key(event.type):
            list = self.event_handlers[event.type]
            for fed in list:
                fed.handle_event(event)

    def query_region(self,system,param):
        """a federate uses this method to ask (via the organizer)
        another federate for the value of a particular parameter
        within a given region. the organizer makes sure that
        the requestee has registered a handler for the parameter,
        then calls it returning the value. otherwise, nothing is
        returned"""
        if self.federates.has_key(system):
            self.federates[system].handle_query_region(param)
            return self.val
        else:
            return None

    def query_point(self,system,param):
        """ same as query region, but for a point rather than a region"""
        if self.federates.has_key(system):
            self.federates[system].handle_query_point(param)
            return self.val
        else:
            return None

    def query_return(self,val):
        """ exec'd code can't 'return' a value, so instead,
        it calls this method on the organizer to say that a
        return value is ready. normally, it should finish
        the execed code immediately after calling this, then
        the query_region() or query_point() returns self.val"""
        self.val = val

    def get_attribute(self,system,attribute):
        try:
            return self.federates[system].attributes[attribute].get()
        except KeyError:
            return None

    def get_var(self,system,varname,default):
        try:
            return self.federates[system].get_var(varname,default)
        except KeyError:
            return default

if __name__ == "__main__":
    org = Organizer()
    print "done"

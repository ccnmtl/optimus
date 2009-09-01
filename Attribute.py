"""
the Attribute class wraps an attribute of a federate

parameters:
   - name: name of the attribute (how it will be listed in forms)
   - varname: the name of the variable (as it will be referenced in code)
   - type: integer, boolean, float, etc. (currently no strict limits)
   - default: the value to set it to initially
   - min: minimum allowable value
   - max: maximum allowable value
   - description: a long description of the attribute
   - valid_values: a list of values that are valid. ignored if empty
   - validate_code: string containing python code that performs custom
                    validation of a value
   - group: the name of a group that the attribute belongs in (for grouping
            fields in a form)

"""

InvalidValue = "this attribute cannot be set to that value"

class Attribute:
    """
    class to wrap a single attribute of a federate
    """
    def __init__(self,name,varname,type,default,min,max,
                 label="",description="",valid_values=[],validate_code="",group=""):

        self.name         = name
        self.type         = type
        self.varname      = varname
        self.description  = description
        self.label        = label
        self.default      = default
        self.valid_values = valid_values
        self.valid_values_v = []

        for (v,l) in valid_values:
            self.valid_values_v.append(v)
            
        self.min          = min
        self.max          = max
        self.group        = group
        
        # store a copy of the source for serialization 
        self.validate_code_source = validate_code
        if validate_code != "":

            self.validate_code = compile(validate_code,"<string>","exec")
        else:
            self.validate_code = ""

        if self.type == 'boolean':
            if self.default == 'true' or self.default == 't':
                self.default = 1
            if self.default == 'false' or self.default == 'f':
                self.default = 0

        self.value = self.default

    def get(self):
        return self.value

    def validate(self,value):
        try:
            if self.type == "integer" or self.type == "float":
                if value > self.max or value < self.min:
                    raise InvalidValue
            if self.type == "boolean":
                if value == 1 or value == 0:
                    pass
                else:
                    raise InvalidValue
            if len(self.valid_values) > 0:
                if value not in self.valid_values_v:
                    raise InvalidValue
            exec self.validate_code
            return 1
        except:
            return 0

    def set(self,value):
        if self.type == "integer" or self.type == "float":
            typecode = (int,float)[self.type!="integer"]
            try:
                value = typecode(value)
            except:
                raise InvalidValue

        if self.validate(value) == 1:
            self.value = value
        else:
            raise InvalidValue

    def reset(self):
        # we don't bother with validating because we
        # assume that the default value is valid
        self.value = self.default

    def as_xml(self):
        from xml.sax import saxutils
        xml = """<attribute name=%s varname=%s type=%s default=%s
        description=%s label=%s min=%s max=%s validate=%s />""" \
                % (saxutils.quoteattr(str(self.name)),
                   saxutils.quoteattr(str(self.varname)),
                   saxutils.quoteattr(str(self.type)),
                   saxutils.quoteattr(str(self.value)),
                   saxutils.quoteattr(str(self.description)),
                   saxutils.quoteattr(str(self.label)),
                   saxutils.quoteattr(str(self.min)),
                   saxutils.quoteattr(str(self.max)),
                   saxutils.quoteattr(str(self.validate_code_source)))
        return xml
        

    
if __name__ == "__main__":
    att = Attribute(name="not 5",varname="foo",type="integer",
                    description="a test attribute that can't be set to 5",default=4,
                    min=0,max=10,validate_code="if value == 5: raise InvalidValue",
                    group="test")
    print att.get()
    try:
        att.set(5)
    except InvalidValue:
        print "won't let me set it to 5"
    att.set(6)
    print att.get()
    att.reset()
    print att.get()
    try:
        att.set(11)
    except InvalidValue:
        print "won't let me set it to 11"
    try:
        att.set(-1)
    except InvalidValue:
        print "won't let me set it to -1"
    print att.get()
        

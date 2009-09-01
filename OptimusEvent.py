class OptimusEvent:
    """a simple class for Events that Federates generate.
    basically just has a type and a dictionary of attributes"""
    def __init__(self,type,attrs):
        self.type = type
        self.attrs = attrs

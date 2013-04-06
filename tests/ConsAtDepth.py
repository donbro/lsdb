class ConsAtDepth(dict):
    """a stack made out of a dictionary of slots whose indices are small integers.  
    Each slot hold a set or relation (or other object with a length)"""

    # dicts are mutable
    
    # def __new__(cls, arg={}):                          
    #     
    #     # s = [a for a in iterable]                           
    #     print "hi from new %r" % arg
    #     
    #     r =  super(ConsAtDepth, cls).__new__(cls, arg ) 
    #     print "hi from new %r" % r
    #     return r


    def __init__(self, arg=None):
        print "hi from init", arg
        super(ConsAtDepth, self).__init__(arg) # TypeError: "'int' object is not iterable"
        self = arg
        print "self", self
        
    def __str__(self):
        return d_lengths(self)
        
    def __repr__(self):
        print "hi from repr %s"
        return d_lengths(self)
        
# T1 = ConsAtDepth({'a':1})
# print T1 # "ConsAtDepth is: %s %r" %(T1, T1)

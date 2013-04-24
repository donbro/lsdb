class mySubStak(list):
    """subclass of list to hold RS1 and RS2 and do extra stuff on append() and pop()"""
    
    def __init__(self, arg=[]):
        super(mySubStak, self).__init__(arg)
        self.RS1 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))
        self.RS2 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))    
        self.RS3 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))    

    def append(self, arg):
        print "sub stak says *append*",
        super(mySubStak, self).append(arg)
                 
    def pop(self):
        print "sub stack says *pop*!",
        # if a directory simply wasn't stored in RS1 because database was empty, then we just skip it here.
        if len(self) > 0 and self[-1] in self.RS1.keys():

            self.RS3[self[-1]] = self.RS1[self[-1]]
            
            # if len(self.RS1[self[-1]]) > 0:
            #     RS2[self[-1]] = self.RS1[self[-1]]
            #     print "(popped directory %r is not empty (%d))" % (self[-1], len(self.RS1[self[-1]]),)
            #     for rs in (self.RS1[self[-1]]):
            #         print "pop", "delete", rs
            #         # yield rs
            # else:
            #     print "(popped directory %r is empty)" % (self[-1], ) ,
            # 
            del self.RS1[self[-1]]          

            print "len(self.RS3)", len(self.RS3)
        
        res =  super(mySubStak, self).pop()

        return res

    def __repr__(self):
        """repr string looks like: "(2) [(1, 399) * , (2, 448) <13>]" """
 
        # self (ie, the list) can be longer than RS, RS can be longer than self
        # RS can have gaps in sequence of depth of keys, eg, (1,xx), (3, xx) 
        #   though RS shouldn't have two keys at any particular depth value
        
        len_self = len(self)
        len_max_RS = 0 if len(self.RS1.keys())==0 else max(self.RS1.keys())[0]
        mx = max(len_self, len_max_RS)  # ie, highest index we need to display

        s=[]
        for k in self:
            if k in self.RS1.keys():    
                s += [ "%r %d" % (k, len(self.RS1[k])) ]
            else:
                s += [ "%r * " % (k,  ) ]

        # we can have RS entry(s) that are beyond the stak, (at least in the value of depth)
        s += [ ( "%r <%d>" ) % (k, len(self.RS1[k]))  for k in self.RS1.keys() if k[0] > len_self]  
                    
        return "(%d) [%s]" % (mx , ", ".join(s))        


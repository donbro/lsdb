
class ComboAtDepth(dict):
    """implementation of last-in first-out stack-ish object but the entries, while always pushed/popped at end
            of list are also indexed by (depth, folder_id) and may not all be present"""
            
    # depth isn't really needed (depth, folder_id) is no more unique then (folder_id)
    # but depth was seen as an efficient index into the set.  
    
    #   depth is very useful as a display device: showing lists and counts at each level
    
    # A python dictionary hash of the key (folder_id) is sufficient but it could also be (depth, folder_id)
    
    # the whole thing could be a relation on (depth, folder_id, vol_id, ... ) (ie, it would be depth + the whole file record)
    
    # this object will be queried ("has_key"/"is in") by way of the key: (depth, folder_id)

    # elements are like (depth, folder_id): relation([(file_id, file_name, file_mod_date)...])
    
    # depth  is defined as 1 + max of the depth keys present (depths begin at zero); 0 if empty.
    
    def __init__(self, in_list=()):
        super(ComboAtDepth, self).__init__(in_list)
        self.in_list = in_list

    def __repr__(self):
        # print "ComboAtDepth is ", len(self), [(k, v) for (k, v) in self.items() ]
        if len(self) == 0:
            return "[]"
        else:
            s = [(k, self[k]) for k in sorted(self.keys())]            
            return "[%s]" % "-".join(["%d:(%d)" % (d, len(r),) for ((d,fid),r) in s ])     # [1:2-1:2-2:1]
            return "[%s]" % "-".join(["%d" % (len(v),) for k, v in s ])    

    def pr(self):
        s = [(k, self[k]) for k in sorted(self.keys())]
        return [  "%d: %d (%d) %s" % (depth, folder_id, len(r), [b.file_name.encode('utf8') for b in r ] ) for ((depth,folder_id),r) in s  ]
        print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in self.items()  ])        

    def pr2(self):
        return "\n".join(self.pr())

    def display(self):
        """returns tuple (depth (one-based), {depth (index), folder_id}, list of contents at each depth for Contents and Items stacks)"""

        #   tuples returned from this routine are combined into a before/after display:
        #
        #                                    2 ==> 1                               
        #           {0: 40014149, 1: 42755279} ==> {0: 40014149}                   
        #                              [0-0][] ==> [0][]  
        #

        s = [(k, self[k]) for k in sorted(self.keys())]
        t = [  "(%d) %s" % ( len(r), ", ".join([b.file_name.encode('utf8') for b in r ]) ) for ((depth,folder_id),r) in s  ]


        s2 = [(k, RS2[k]) for k in sorted(RS2.keys())]
        t2 = [  "(%d) %s" % ( len(r), ", ".join([b.file_name.encode('utf8') for b in r ]) ) for ((depth,folder_id),r) in s2  ]
        
        return  ( 
                self.max_depth_value(),
                "%r" % [(d,fid) for ((d,fid),r) in s ]   ,
                (t, t2) # self.pr()
                # "[%s][%s]" % (d_lengths(self.folderContentsAtDepth) , d_lengths(self.itemsAtDepth))
                )
        
    def push(self, (in_depth, folder_id), r):
        """RS1.push( depth, folder_id, r ) """
        k = (in_depth, folder_id)
        v = r
        if not isinstance(r, relation):
            raise TypeError, "type of object pushed should be relation"

        objs_at_depth = self.objects_at_depth(in_depth)
        if len(objs_at_depth) > 0:
            print "object relation of length %d already exists at depth (%d).  add items to it?" % (len(objs_at_depth),in_depth)

        # if self.max_depth_value() > in_depth:
        #     raise ValueError , "(max) depth is already %d, object is being pushed at index %d." %  (self.max_depth_value(), in_depth)

        # update() accepts one iterable/list of key/value pairs (or iterables of length two)
        update_list = [   (   k , v  )    ]
        self.update( update_list )
        # print [d for ((d,fid),r) in self.items()]
        print "push:\n", self.pr2(depth)



    def pop(self, called_for_depth_value):
        
        # if len(self.folderIDAtDepth.keys()) == 0:
        #     return
        #     
        # len_s = self.max_folder_id()
        # 
        # assert len_s != None, "pop_item_stack: self.max_folder_id() is %r!" % self.max_folder_id()
    
        # use while because we could have popped more than one level
        #    (eg, end of level 3 is also end of level 2 and so the pop is to level 1)
        
        # use object_at_depth so will raise error if more than one value at this depth
        
        r = self.objects_at_depth(called_for_depth_value)
        
        if r ==  []:
            raise ValueError,  "Pop: Entry for depth value %d: is not present." % (called_for_depth_value,)
            # return
        print "pop", called_for_depth_value, r
        #     
        # if len(r) > 1:
        #     raise ValueError, ("more than one", r)
            
        
        
        # if self.max_depth_value() ==  called_for_depth_value:
        #     print "Current max depth (%d) equals called for pop-to max depth value is (%d).  No action performed." % (self.max_depth_value(),called_for_depth_value)
        #     return
        # elif self.max_depth_value() >  called_for_depth_value:
        #     print "called for pop-to max depth value (%d) is less than current max depth value (%d).  Will pop." % (called_for_depth_value, self.max_depth_value())
        # else:       # self.max_depth_value() < called_for_depth_value:
        #     print "Current max depth (%d) already less than called for pop-to max depth value is (%d).  Is this correct?" % (self.max_depth_value(),called_for_depth_value)
        #     return

        while self.max_depth_value() >=  called_for_depth_value:
            display_before = self.display()

            (fid, r) = self.object_at_depth(self.max_depth_value())
            
            "length of popped relation is", len(r)
            if len(r) > 0:
                print "\nCopy un-accounted for values [%r] to RS2?\n" % (", ".join([b.file_name.encode('utf8') for b in r ] ) ,)
                RS2.push( (self.max_depth_value(), fid), r  )
                
                print 

            del self[(self.max_depth_value(), fid)]

            display_after =  self.display()
            for n, v in enumerate(display_before):
                print "popS  %32s ==> %-32s" % (v, display_after[n])
            print 
            

        
    def max_depth_value(self):
        """returns 0 for empty, 1 for a single level-0 stack, 2 for 0,1, etc."""
        return None if len(self) == 0 else max( [d for ((d,fid),r) in self.items()] )
        return 0 if len(self) == 0 else 1+ max( [d for ((d,fid),r) in self.items()] )
        
    def object_at_depth(self,in_depth):
        s = [(fid,r) for ((d,fid),r) in self.items() if d == in_depth]
        if len(s) == 0:
            return s
        elif len(s) ==1:
            return s[0]
        else:
            raise ValueError, ("more than one", s)
        # return [((d,fid),r) for ((d,fid),r) in self.items() if d == in_depth]

    def objects_at_depth(self,in_depth):
        return [(fid,r) for ((d,fid),r) in self.items() if d == in_depth]
        

    def stack_is_larger_then_depth(self, depth):
        return self.max_depth_value() > depth
            

    #ISS.push( depth, folder_id, r)

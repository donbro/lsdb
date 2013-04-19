class ItemStackStuff(object):
    """docstring for ItemStackStuff"""
    
    def __init__(self , folderIDAtDepth={}, itemsAtDepth=defaultdict(set)):
        super(ItemStackStuff, self).__init__()
        self.folderIDAtDepth = folderIDAtDepth      # dictionary: keys: depth, values: (int) folder_ids 

        self.folderContentsAtDepth = defaultdict(relation)  # almost.  needs to supply a heading at init time!  lambda?
        self.itemsAtDepth = itemsAtDepth
        
        
    def max_folder_id(self):
        """returns None for empty, 0 for a stack holding key 0, 1 for 0,1, etc."""
        return None if len(self.folderIDAtDepth.keys()) == 0 else  max(self.folderIDAtDepth.keys())

    def stack_depth(self):
        """returns 0 for empty, 1 for a single level-0 stack, 2 for 0,1, etc."""
        return 0 if len(self.folderIDAtDepth.keys()) == 0 else 1+ max(self.folderIDAtDepth.keys())


    def display_stack(self):
        """returns tuple (depth (one-based), {depth (index), folder_id}, list of contents at each depth for Contents and Items stacks)"""

        #   tuples returned from this routine are combined into a before/after display:
        #
        #                                    2 ==> 1                               
        #           {0: 40014149, 1: 42755279} ==> {0: 40014149}                   
        #                              [0-0][] ==> [0][]  
        #
        
        return  ( 
                self.stack_depth(),
                "%s" % self.folderIDAtDepth,            
                "[%s][%s]" % (d_lengths(self.folderContentsAtDepth) , d_lengths(self.itemsAtDepth))
                )
                
    def stack_is_larger_then_depth(self, depth):
        """          # ie, if our current stack is larger than our current depth"""
        return self.stack_depth()  > depth

    def pop_item_stack(self, depth, n=3):
        
        if len(self.folderIDAtDepth.keys()) == 0:
            return
    
        len_s = self.max_folder_id()
        
        assert len_s != None, "pop_item_stack: self.max_folder_id() is %r!" % self.max_folder_id()
    
        # use while because we could have popped more than one level
        #    (eg, end of level 3 is also end of level 2 and so the pop is to level 1)
        
        while self.stack_depth() > depth:
        
            if GPR.verbose_level >= n:
                s_before = self.display_stack()
    
            if len(self.folderContentsAtDepth[len_s]) > 0:
                self.itemsAtDepth[len_s] = relation (self.folderContentsAtDepth[len_s].heading)
                self.itemsAtDepth[len_s] |= self.folderContentsAtDepth[len_s]
        
            del self.folderContentsAtDepth[len_s]
            del self.folderIDAtDepth[len_s]

            if GPR.verbose_level >= n:
                s_after = self.display_stack()
                print
                for n, v in enumerate(s_before):
                    print "pop  %32s ==> %-32s" % (v, s_after[n])
                print 

            len_s = self.max_folder_id()


# global container for item stack stuff
# ISS = ItemStackStuff()     



       # TODO this is wrong.  we have two different file_exists able to arrive here (depends on whether is directory)
        
        # if depth-1 in ISS.folderIDAtDepth and folder_id == ISS.folderIDAtDepth[depth-1] \
        #                                                             and (file_exists or  force_folder_scan):
        # 
        #     #   Remove a file item from the list of database contents.
        # 
        #     file_id         = item_dict['NSFileSystemFileNumber']
        #     filename        = item_dict[NSURLNameKey]
        #     file_mod_date   = item_dict[NSURLContentModificationDateKey]
        # 
        #     s = str(file_mod_date)
        #     file_mod_date = s[:-len(" +0000")]
        #     # print file_mod_date
        # 
        #     rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
        # 
        #     if ISS.folderContentsAtDepth.has_key(depth-1):
        #     
        #         if rs in ISS.folderContentsAtDepth[depth-1]:
        #             ISS.folderContentsAtDepth[depth-1].remove(rs)
        #         else:
        #             # print ""
        #             # print "%r not in database list (%d)" % (rs, len(ISS.folderContentsAtDepth[depth-1]))
        #             zs =  ISS.folderContentsAtDepth[depth-1].tuple_d(*rs)
        #             # print
        #     else:
        #         print 'folderContentsAtDepth', ISS.folderContentsAtDepth.keys() , 'has no key', depth-1
        #                 

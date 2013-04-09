#!/usr/bin/env python
# encoding: utf-8
"""
relation_dict.py

Created by donb on 2013-04-01.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from collections import defaultdict
from relation import relation, RelationTupleLengthException


class relation_dict(defaultdict):
    """default dict whose default value is a relation"""
    
    _heading = ("a", "b", "c")

    def __init__(self, update_list=(), heading=None):  # **kwargs):
        
        self.heading = heading if heading else  relation_dict._heading

        # update_list
        # [((1, 234584), relation( ('a', 'b', 'c'), [(1, 2, 3)] ))]

        # super(relation_dict, self).__init__( relation( relation_dict.default_heading ) )
        
        super(relation_dict, self).__init__( relation( self.heading ), update_list ) # , **kwargs)

        #debugging
        if update_list:
            print "relation_dict-"+(hex(id(self))[7:-2])+".init( %r )" % update_list        

    
    def __setitem__(self, key, in_value):
        """values of a relation dict are relations. keys are (depth, folder_id)"""

        if in_value.heading != self.heading:
                    raise RelationTupleLengthException(in_value, 
                        "Attempt to insert relation with heading %r into relation_dict with heading %r" % (in_value.heading, self.heading) )

        # RelationTupleLengthException: Attempt to insert relation with heading 
        # ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date')  
        # into relation_dict with heading ('a', 'b', 'c')  
        # failed on relation( ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date'),  
        #                                           [(1, 2, 7, 2, 7), (1, 2, 8, 2, 8)] )
        
        
        dict.__setitem__(self, key, in_value)

        # make these dependent on verbose_level?
        # if [row for row in in_value] == []:
        #         print "\nDoing the default dictionary thing here:"
        # print "relation_dict-"+(hex(id(self))[-6:-2])+".setitem( %r, %r )" % (key, [row[2] for row in in_value])
        


        # self._dict[key[0]] = key
        

    def update(self, args=None, **kwargs):
        print "relation_dict-"+(hex(id(self))[7:-2])+".update( %r, %r )" % (args, kwargs)
        if args is not None:
            if hasattr(args, 'keys'):
                for key in args.keys():
                    self.__setitem__(key, args[key])
            else:
                for key, value in args:
                    self[key] = value
        if kwargs:
            self.update(kwargs)

    # output of stack
    
    # def pr2(self, depth=None, short=False):
    #     """show contents of , just lengths (depth is assumed via position) if short=True"""
    #     # [0:(10)-1:(0)]
    #     if short:
    #         return  "[%s]" % "-".join(["%d" % (d) for (k,d) in self._lengths_of_contents_at_depth(depth)])
    #     else:
    #         return "[%s]" % "-".join(["%s:(%d)" % (k,d) for (k,d) in self._lengths_of_contents_at_depth(depth)])

            
    # def pr_str(self, short=False):
    #     if not short:
    #         # [1:(1)-2:(1)]
    #         return "[%s]" % "-".join(["%d:(%d)" % (k[0], len(self[k]),) for k in self._sorted_keys() ])
    #     else:
    #         # 1-1
    #         return "-".join(["%d" % (len(self[k]),) for k in self._sorted_keys() ])     
    #         # return "[%s]" % "-".join(["(%d)" % (len(self[k]),) for k in self._sorted_keys() ])  
            


    # def _lengths_of_contents_at_depth(self, depth=None):
    #     """show depth, len(contents at depth) of , down to but not including the key of depth, if provided, all, otherwise."""
    #     if depth:
    #         return [(k, len(self[self._dict[k]])) for  k  in sorted(self._dict.keys()) if k < depth]
    #     else:
    #         return [(k, len(self[self._dict[k]])) for  k  in sorted(self._dict.keys())]
            
    

    #
    #   the fullon repr() of an instance of this object is something like:
    #
    #       defaultdict(relation( ('a', 'b', 'c'), [] ), {(1, 234584): relation( ('a', 'b', 'c'), [(1, 2, 3)] )})
    #
    #   our repr is the repr of the object as a dict:
    #
    #       {(1, 234584): relation( ('a', 'b', 'c'), [(4, 5, 6), (1, 2, 3)] )}
    #
    #   for our basic str() we use just the (sorted) keys and the tuples contained within the relations
    #
    #       (1, 234584):[(4, 5, 6), (1, 2, 3)], (2, 444584):[(24, 25, 26)]
    #
    #   a shorter version pr_str() useful when watching traces is keys, lengths
    #
    #       [1:(2)-2:(1)]
    #
    #   and an even shorter pr_str(short=True) is just lengths, depths are inferred from position
    #
    #       2-1
    #

        
    def _sorted_keys(self):
        return sorted(self.keys())

    def xpr1(self, in_rel):
        # [[('a', 1), ('b', 2), ('c', 3)]]
        return  [ [ (k, row[k])  for k in self.heading ]  for row in in_rel]

    def xpr2(self, in_rel):
        # ['(a=1, b=2, c=3)']
        return  [ "(%s)" %  ", ".join([ "%s=%r"% a for a in row ])  for row in self.xpr1(in_rel)]


    def xpr3(self, in_rel, no_brackets=False):
        #  [(a=4, b=5, c=6), (a=1, b=2, c=3)] or (a=4, b=5, c=6), (a=1, b=2, c=3)
        if no_brackets:
            return  ", ".join( self.xpr2(in_rel) )
        else:
            return  "[%s]" %  ", ".join( self.xpr2(in_rel) )

    def super_repr(self):
        """my super repr"""
        return super(relation_dict, self).__repr__(  )

    def __repr__(self):
        # (1, 234584):[(a=4, b=5, c=6)], (2, 444584):[(a=24, b=25, c=26)]
        return  "[]" if len(self) == 0 else ", ".join( [ "%r:%s" % (k,self.xpr3(r) ) for (k,r) in sorted(self.items())] )
        
        
    def __str__(self):
        return "[]" if len(self) == 0 else ", ".join(["%r:%r" % (k, list(set(self[k]))) for k in self._sorted_keys() ])
        # list() of relation looks like: [relation_c6a5(a=1, b=2, c=3), ...]
        
    def pr_str(self, short=False):
        if not short:
            # [1:(1)-2:(1)]
            return "[%s]" % "-".join(["%d:(%d)" % (k[0], len(self[k]),) for k in self._sorted_keys() ])
        else:
            # 1-1
            return "-".join(["%d" % (len(self[k]),) for k in self._sorted_keys() ])     
            # return "[%s]" % "-".join(["(%d)" % (len(self[k]),) for k in self._sorted_keys() ])  



import unittest


 
class relation_dict_TestCase( unittest.TestCase ):
    """ Class to test relation_dict """
    
    def test_047_relation_dict(self):


        RS2 = relation_dict()   
        #  currently: defaultdict(relation( ('a', 'b', 'c'), [] ), {})
        with self.assertRaises(RelationTupleLengthException):
            RS2[(1,2)] = relation( ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date') , [ (1,2,7,2,7), (1,2,8,2,8) ] ) 
        
        # can't really do this either, because the default factoty is created at init time, this will pass (fool) the
        RS2.heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date')
        #       setitem test, but isn't really the thing
        RS2[(1,2)] = relation( ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date') , [ (1,2,7,2,7), (1,2,8,2,8) ] ) 
        print RS2.super_repr() == "defaultdict(relation( ('a', 'b', 'c'), [] ), {(1, 2): relation( ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date'), [(1, 2, 7, 2, 7), (1, 2, 8, 2, 8)] )})"
        print repr(RS2)



    def test_048_relation_dict(self):
        """default header"""
        
        RS1 = relation_dict()
        k = (5, 123423)
        self.assertEqual(RS1[k] , relation( RS1.heading, [] ))
        self.assertEqual(RS1.super_repr() , 
                "defaultdict(relation( ('a', 'b', 'c'), [] ), {(5, 123423): relation( ('a', 'b', 'c'), [] )})" )

    def test_049_relation_dict(self):
        """default header"""
        
        RS2 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   
        k = (5, 123423)
        self.assertEqual(RS2[k] , relation( ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date'), [] ))
        self.assertEqual(RS2.super_repr() , 
            "defaultdict(relation( ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date'), [] ), "
                "{(5, 123423): relation( ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date'), [] )})"
                 )

        
            
    def test_050_relation_dict(self):
        """properties of empty relation_dict"""
        
        RS1 = relation_dict()
        self.assertEqual( repr(RS1) , '[]' )
        self.assertEqual( str(RS1) , '[]' )
        self.assertEqual(  RS1.pr_str() , '[]' )
        self.assertEqual(  RS1.pr_str(short=True) , '' )
        
        # print "RS1.pr2(short=True)", RS1.pr2(short=True)
        
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [] )
        

    def test_052_relation_dict(self):
        """using the defaultdict functionality to create a relation_dict"""
        
        RS1 = relation_dict()

        k = (5, 123423)

        # referring to non-existant entry creats empty entry at that key
        self.assertEqual( RS1[ k ] ,    relation( RS1.heading, [] ) )
        self.assertEqual( RS1,          { k: relation( RS1.heading, [] ) } )

        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(5, 0)] )  # ie, empty relation at depth 5

        # print "RS1.pr2()", RS1.pr2()
        # print "RS1.pr2(short=True)", RS1.pr2(short=True)

    def test_053_relation_dict(self):
        """additive behavior of empty relation_dict"""
        
        RS1 = relation_dict()

        k = (5, 123423)
        
        RS1[ k ] += (1, 2, 3)  
        
        # simply accessing a non-existant slot creates a new empty relation
        self.assertEqual( RS1[ k ] , relation( RS1.heading, [(1, 2, 3)] ) )
        
        self.assertEqual( RS1, { k: relation( RS1.heading, [(1, 2, 3)] ) } )

        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(5, 1)] ) # ie, relation of length 1 at depth 5


    def test_060_relation_dict(self):
        """init of relation_dict via list"""

        k = (1,234584)
        r = relation( ('a', 'b', 'c'), [(1, 2, 3)] )
        update_list = [   (   k , r  )    ]
        RS1 = relation_dict( update_list )

        self.assertEqual (RS1[k] , r )
        
        self.assertEqual (RS1.default_factory.heading , ('a', 'b', 'c') )

        self.assertEqual( repr(RS1) ,               '(1, 234584):[(a=1, b=2, c=3)]' )
        self.assertEqual( str(RS1) ,                '(1, 234584):[(1, 2, 3)]' )
        self.assertEqual(  RS1.pr_str() ,           '[1:(1)]' )
        self.assertEqual(  RS1.pr_str(short=True) , '1' )

        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(1, 1)] )
        

    def test_070_relation_dict(self):
        """arithmetic behavior of relation_dict"""

        RS1 = relation_dict()

        k1 = (1,234584)
        k2 = (2,444584)

        RS1[k1] += ( 1 ,2 , 3)  
        
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(1, 2, 3)] ) )
        self.assertEqual( RS1, { k1: relation( RS1.heading, [(1, 2, 3)] ) } )
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(1, 1)] )

        RS1[k1] += ( 4 ,5 , 6 ) 
        
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(4, 5, 6), (1, 2, 3)] ) )
        self.assertEqual( RS1, { k1: relation( RS1.heading, [(4, 5, 6), (1, 2, 3)] ) } )
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(1, 2)]  )

        RS1[k2] += ( 24 ,25 , 26 ) 
        
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(4, 5, 6), (1, 2, 3)] ) )
        self.assertEqual( RS1[ k2 ] , relation( RS1.heading, [(24, 25, 26)] ) )
        
        self.assertEqual( RS1, { k1: relation( RS1.heading, [(4, 5, 6), (1, 2, 3)] ),
                                 k2: relation( RS1.heading, [(24, 25, 26)] ) } )
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(1, 2), (2, 1)] )


        RS1[k1] -= ( 1 ,2 , 3)
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(4, 5, 6) ] ) )
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(1, 1), (2, 1)]  )


        # self.failUnlessRaises(tuple_set_exception, tuple_set, ('a', 'b', 'a') )    unittest.main()
        with self.assertRaises(KeyError):
            RS1[k1].subtract( (1, 2, 3) )
            
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(4, 5, 6) ] ) )
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(1, 1), (2, 1)] )


    def test_071_relation_dict(self):
        """test internal stack-of-keys when using update()"""

        RS1 = relation_dict()
        k1 = (1,234584)
        # k2 = (2,444584)

        RS1[k1] += ( 1 ,2 , 3)  
        
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(1, 2, 3)] ) )
        self.assertEqual( RS1, { k1: relation( RS1.heading, [(1, 2, 3)] ) } )
        
        r = relation( ('a', 'b', 'c'), [(4, 5, 6)] )
        update_list = [   (   k1 , r  )    ]

        RS1.update( update_list ) 
        
                
        self.assertEqual( RS1[ k1 ] , relation( RS1.heading, [(4, 5, 6)] ) )
        self.assertEqual( RS1, { k1: relation( RS1.heading, [(4, 5, 6)] ) } )

    def test_075_relation_dict(self):
        """stack replacement"""
        RS1 = relation_dict()

        k11 = (3,234584)
        RS1[k11] = relation( RS1.heading, [(1, 2, 3)] )   
        # self.assertEqual( RS1._lengths_of_contents_at_depth() ,  [(3, 1)]   )
        self.assertEqual( RS1[ k11 ] , relation( RS1.heading, [(1, 2, 3)] ) )

        k12 = (3,37482)
        RS1[k12] = relation( RS1.heading, [(4, 5, 6)] )   
        
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(3, 1)] )      # stack is still an entry of length 1 at depth 3
        
        self.assertEqual( RS1[ k12 ] , relation( RS1.heading, [(4, 5, 6)] ) )
        self.assertEqual( RS1, { k11: relation( RS1.heading, [(1, 2, 3)] ) , 
                                        k12: relation( RS1.heading, [(4, 5, 6)] ) } )


        k13 = (3, 98765 )
        RS1[k12] = relation( RS1.heading, [(9, 7, 5 ), (6, 2 , 8)] )   
        
        # self.assertEqual( RS1._lengths_of_contents_at_depth() , [(3, 2)] )      # now just one entry of length 2 at depth 3
        
        self.assertEqual(  str(RS1) , '(3, 37482):[(6, 2, 8), (9, 7, 5)], (3, 234584):[(1, 2, 3)]' )


    def test_080_relation_dict(self):
        """relation_dict heading attribute"""

        RS2 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   

        self.assertEqual( RS2.heading , ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date') )
        
        RS2[(1,2)] +=  (1,2,7,2,7) # , (1,2,8,2,8) ] ) 
        self.assertEqual( RS2[(1,2)] ,
                    relation( ('vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date'), [(1, 2, 7, 2, 7)] ))

        with self.assertRaises(RelationTupleLengthException):
            RS2[(1,2)] +=  (1,2,7) # , (1,2,8,2,8) ] ) 

        print   RS2[(1,2)]
        print   RS2
        print "%r" % RS2
        
    def test_080_relation_dict(self):

        RS1_dbdel = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   

        k13 = (3, 98765 )
        
        print k13 in RS1_dbdel        
        
        rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
        
        RS1_dbdel[ (depth-1, folder_id) ] -= rs       # present, so no longer a "file to be deleted"
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(relation_dict_TestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)  

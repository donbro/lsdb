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


from relation import relation

# def hix():
#     """docstring for hix"""
#     print "hi from hix"
#     return relation( ("a", "b", "c") )
# 
# a = set([1,2,3])

        # set is:
        # 'add', 'clear', 'copy', 'difference', 'difference_update', 'discard', 
        # 'intersection', 'intersection_update', 'isdisjoint', 'issubset', 
        # 'issuperset', 'pop', 'remove', 'symmetric_difference', 
        # 'symmetric_difference_update', 'union', 'update'
        
# print [k for k in dir(a) if k[0]!="_"]
# sys.exit()


class relation_dict(defaultdict):
    """default dict whose default value is a relation"""

    def __init__(self, *args, **kwargs):
        if args == () and kwargs == {}:
            pass
        else:
            print 'init', 'args:', type(args), args, 'kwargs', kwargs
        super(relation_dict, self).__init__( relation( ("a", "b", "c") ), *args, **kwargs)
        
    def _sorted_keys(self):
        return sorted(self.keys())

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

    def __repr__(self):
        return "%r %s" % (self.default_factory.heading, repr(set(self)))

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
    
    def test_050_relation_dict(self):
        """ tuple_set uniqueness"""
        
        RS2 = relation_dict()
        print "repr(RS2) is: %r" % RS2
        print " str(RS2) is: %s" % RS2
        print


    def test_060_relation_dict(self):
        
                
        #   tuple_set_exception: tuple_set given (3) ('a', 'c', 'a') should be (2) ('a', 'c')
        # self.failUnlessRaises(tuple_set_exception, tuple_set, ('a', 'b', 'a') )  


        k = (1,234584)
        r =   relation( ('a', 'b', 'c'),  [ ( 1 ,2 , 3) ] ) # 
        print "r", r
        update_list = [   (   k , r  )    ]
        RS1 = relation_dict( update_list )
        print RS1.default_factory.heading

        print "repr(RS1) is: %r" % RS1
        print " str(RS1) is: %s" % RS1
        print "pr_str(RS1) is: %s" % RS1.pr_str()
        print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)
        print




        RS1[(1,234584)] += ( 1 ,2 , 3)  
        print "repr(RS1) is: %r" % RS1
        print " str(RS1) is: %s" % RS1
        print

        RS1[(1,234584)] += ( 4 ,5 , 6 ) 
        print "repr(RS1) is: %r" % RS1
        print " str(RS1) is: %s" % RS1
        print "pr_str(RS1) is: %s" % RS1.pr_str()
        print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)
        print

        RS1[(2,444584)] += ( 24 ,25 , 26 ) 
        print "repr(RS1) is: %r" % RS1
        print " str(RS1) is: %s" % RS1
        print "pr_str(RS1) is: %s" % RS1.pr_str()
        print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)


        RS1[(1,234584)].subtract( ( 1 ,2 , 3))
        print "repr(RS1) is: %r" % RS1
        print " str(RS1) is: %s" % RS1
        print "pr_str(RS1) is: %s" % RS1.pr_str()
        print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)
        print

        RS1[(1,234584)] -= ( 1 ,2 , 3)
        print "repr(RS1) is: %r" % RS1
        print " str(RS1) is: %s" % RS1
        print "pr_str(RS1) is: %s" % RS1.pr_str()
        print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)



if __name__ == '__main__':
    unittest.main()

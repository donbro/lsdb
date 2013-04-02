#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-04-01.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os


from collections import defaultdict


from relations.relation import relation

def hix():
    """docstring for hix"""
    print "hi from hix"
    return relation( ("a", "b", "c") )

# a = set([1,2,3])
# b = set([3,4,5])
# 
# print a
# print b
# print a - b

# class RS(defaultdict(relation( ("a", "b", "c") ))):


class RS(defaultdict):

    def __init__(self, *args, **kwargs):
        super(RS, self).__init__( relation( ("a", "b", "c") ), *args, **kwargs)
        
    def _sorted_keys(self):
        return sorted(self.keys())

    # reprs, displays, strs, etc.
    #
    #   the fullon repr() of an instance of this object is something like:
    #
    #       defaultdict(relation( ('a', 'b', 'c'), [] ), {(1, 234584): relation( ('a', 'b', 'c'), [(1, 2, 3)] )})
    #
    #   for our repr we use the repr of the object as a dict:
    #
    #       {(1, 234584): relation( ('a', 'b', 'c'), [(4, 5, 6), (1, 2, 3)] )}
    #
    #   for our basic str() we use just the (sorted) keys and the tuples contained within the relations
    #
    #       (1, 234584): [(1, 2, 3),(4, 5, 6)] 
    #       (1, 234584):[(4, 5, 6), (1, 2, 3)], (2, 444584):[(24, 25, 26)]
    #
    #   a shorter version useful when watching traces is keys, lengths
    #
    #       [1:(2)-2:(1)]
    #
    #   shortest pr_str(short=True) is just lengths, depths are inferred from position
    #

    def __repr__(self):
        return repr(dict(self))

    def __str__(self):
        return ", ".join(["%r:%r" % (k, list(set(self[k]))) for k in self._sorted_keys() ])     # [1:2-1:2-2:1]
        return "[%s]" % "-".join(["%d:(%d)" % (k[0], len(self[k]),) for k in self._sorted_keys() ])     # [1:2-1:2-2:1]

    def pr_str(self, short=False):
        if not short:
            return "[%s]" % "-".join(["%d:(%d)" % (k[0], len(self[k]),) for k in self._sorted_keys() ])     # [1:2-1:2-2:1]
        else:
            return "-".join(["%d" % (len(self[k]),) for k in self._sorted_keys() ])     # [1:2-1:2-2:1]
            return "[%s]" % "-".join(["(%d)" % (len(self[k]),) for k in self._sorted_keys() ])     # [1:2-1:2-2:1]

k = (1,234584)
r =   relation( ('a', 'b', 'c'),  [( 1 ,2 , 3) ] ) # 
print "r", r
update_list = [   (   k , r  )    ]
RS1 = RS( update_list )

print "repr(RS1) is: %r" % RS1
print " str(RS1) is: %s" % RS1

RS2 = RS()

print "RS2", RS2

# RS1 = RS( [ (1,234584) , ( 1 ,2 , 3) ] ) # defaultdict(relation( ("a", "b", "c") ))
print RS1, RS1._sorted_keys(), repr(dict(RS1))
# print dir(RS1)
print "repr(RS1) is: %r" % RS1
print " str(RS1) is: %s" % RS1
print "pr_str(RS1) is: %s" % RS1.pr_str()
print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)



RS1[(1,234584)] += ( 1 ,2 , 3)  
print RS1

RS1[(1,234584)] += ( 4 ,5 , 6 ) 
print "repr(RS1) is: %r" % RS1
print " str(RS1) is: %s" % RS1
print "pr_str(RS1) is: %s" % RS1.pr_str()
print "pr_str(short=True) is: %s" % RS1.pr_str(short=True)

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

sys.exit()

RS1[(1,234584)] += ("hey there2", )
print RS1
RS1[(1,234584)] -= ("hey there", )
print RS1

# 
# def main():
#     pass
# 
# 
# if __name__ == '__main__':
#     main()
# 

#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-02-24.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import unittest

class tuple_set_exception(Exception):
    pass

class tuple_set(tuple):
    """tuple_set maintain order and ensures all elements are unique."""
    
    # to subclass a non-mutable, like tuple, we also need to override __new__().
    # note that we pass set(iterable) to constructor

    def __new__(cls, iterable=()):
        s = [a for a in iterable]
        if len( set(s) ) != len(s):
                raise tuple_set_exception("tuple_set given (%d) %r should be (%d) %r" % (len(s) , tuple(s),  len(set(s)) , tuple(set(s))))
        return super(tuple_set, cls).__new__(cls, set(iterable) )
    
    # as a test of uniqueness we check the length of the iterator against the representation as a set
    def __init__(self, iterable=() ):
        # if iterable: 
        #     if len( self ) != len(iterable):
        #             raise tuple_set_exception("tuple_set given (%d) %r should be (%d) %r" %(len(iterable) , iterable,  len( self ) , self))
        pass
        
    def union(self, other):
        """union of two operands as sets, then made into a tuple_set."""
        return self.__class__( set(self).union(set(other)) )

    __or__ = union

    def intersection(self, other):
        """intersection of two operands as sets, then made into a ordered set."""
        return self.__class__( set(self).intersection(set(other)) )

    __and__ = intersection
    __xor__ = intersection
        
class relation(set):
    def __init__(self, heading, rows=() ):                          # can create empty as: relation(header)  

        self.heading = tuple_set( heading )
        
        super(relation, self).__init__(rows)                        # superclass init is: set.__init__(rows)
        

import unittest


 
class relation_TestCase( unittest.TestCase ):
    """ Class to test relation """

    def test_050_tuple_set(self):
        """ tuple_set.                simple properties of..."""
        
        #    tuple_set
        
        ts1 = tuple_set( ['a', 'b'] )
        
        self.failUnlessEqual( ts1 ,tuple( ('a', 'b' )  ) , "tuple_set not initialized.")
        self.failUnlessEqual( ts1 , ('a', 'b' )          , "tuple_set is a tuple.")
        self.assertNotEqual(  ts1 , ['a', 'b']           , "tuple_set is tuple not list.")

        # iterator over dictionary is keys()
        ts2 = tuple_set( { 'a':1 , 'b':2 }  )
        self.failUnlessEqual( ts1 ,tuple_set( ('a', 'b')  ) , "tuple_set is tuple not dictionary.")
        
        self.assertTrue( ts1 == ('a', 'b') )  # a tuple_set (used internally for heading) is equal to a tuple.
        

    def test_051_tuple_set(self):
        """ tuple_set uniqueness"""
                
        self.failUnlessRaises(tuple_set_exception, tuple_set, ('a', 'b', 'a') )  
        
        # ts2 = tuple_set(        ('a', 'c', 'a')  )
        # error is:
        #   tuple_set_exception: tuple_set given (3) ('a', 'c', 'a') should be (2) ('a', 'c')

        
        
    def test_052_tuple_set(self):
        """ tuple_set set algebra"""
        
        ts1 = tuple_set( ('a', 'b') )
        ts2 = tuple_set( ('b', 'c') )
        ts3 = ts1 & ts2
        self.assertIsInstance(ts3, tuple_set)
        self.failUnlessEqual(ts3, ('b',))

        ts4 = ts1 ^ ts2
        self.assertIsInstance(ts4, tuple_set)
        self.failUnlessEqual(ts4, ('b',))

        ts5 = ts1 | ts2
        self.assertIsInstance(ts5, tuple_set)
        # tuple_set has order, should compare equal to tuple
        self.failUnlessEqual(ts5,  ('a', 'c', 'b'))
  
        

    def test_060_relation(self):
        """ relation heading """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )

        self.assertIsInstance(r1.heading, tuple_set)
        self.failUnlessEqual( r1.heading ,tuple_set( ['a', 'b']  ) , "heading not initialized.")
        self.failUnlessEqual( r1.heading ,tuple_set( ( 'a', 'b' )  ) , "heading not initialized.")
        self.failUnlessEqual( r1.heading ,tuple_set( { 'a':1 , 'b':2 }  ) , "heading not initialized.")



    def test_061_relation(self):
        """ relation rows """
                
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )
        r2 = relation( ('a', 'b'), [(3, 4), (3, 5) , (3, 2), (1, 2) ] )

        #    relation as set of rows
        
        self.assertSetEqual(r1, set( [(1, 2), (3, 2), (3, 4), (3, 5)] ) )
        self.assertSetEqual(r1, set( [(1, 2), (3, 2), (3, 4), (3, 6)] ) )
        # AssertionError: Items in the first set but not the second:
        # (3, 5)
        # Items in the second set but not the first:
        # (3, 6)
        
        self.assertSetEqual(r1, r2 )




        # print dir(relation_TestCase)
    # 'addCleanup',         'addTypeEqualityFunc',  'assertAlmostEqual', 'assertAlmostEquals', 
    # 'assertDictContainsSubset', 'assertDictEqual', 'assertEqual', 'assertEquals', 
    # 'assertFalse',            'assertGreater', 'assertGreaterEqual', 'assertIn', 'assertIs', 
    # 'assertIsInstance',   'assertIsNone', 'assertIsNot', 'assertIsNotNone', 'assertItemsEqual', 
    # 'assertLess',         'assertLessEqual', 'assertListEqual', 'assertMultiLineEqual', 
    # 'assertNotAlmostEqual', 'assertNotAlmostEquals', 'assertNotEqual', 
    # 'assertNotEquals',    'assertNotIn', 'assertNotIsInstance', 'assertNotRegexpMatches', 
    # 'assertRaises',       'assertRaisesRegexp', 'assertRegexpMatches', 'assertSequenceEqual', 
    # 'assertSetEqual',     'assertTrue', 'assertTupleEqual', 'assert_', 
    # 'countTestCases', 'debug',    'defaultTestResult', 'doCleanups', 
    # 'fail', 'failIf', 'failIfAlmostEqual', 'failIfEqual', 'failUnless', 
    # 'failUnlessAlmostEqual', 'failUnlessEqual', 'failUnlessRaises', 
    # 'failureException', 'id', 'longMessage', 'maxDiff', 'run', 
    # 'setUp',  'setUpClass', 'shortDescription', 'skipTest', 
    # 'tearDown', 'tearDownClass' 
    
if __name__ == '__main__':
    unittest.main()
    
    
#!/usr/bin/env python
# encoding: utf-8
"""
relation.py

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
    
    # as a test of uniqueness we check the length of the iterator against its representation as a set
    def __new__(cls, iterable=()):
        s = [a for a in iterable]
        if len( set(s) ) != len(s):
                raise tuple_set_exception("tuple_set given duplicate entries %r uniques are %r" % (  tuple(s),  tuple(set(s))))
                # raise tuple_set_exception("tuple_set given duplicate entries (%d) %r uniques are (%d) %r" % (len(s) , tuple(s),  len(set(s)) , tuple(set(s))))
        return super(tuple_set, cls).__new__(cls, iterable )
    
    def __init__(self, iterable=() ):
        pass
        
    def union(self, other):
        """union of two operands as sets, then made into a tuple_set."""
        return self.__class__( set(self).union(set(other)) )

    __or__ = union

    def intersection(self, other):
        """intersection of two operands as sets, then made into a tuple_set."""
        return self.__class__( set(self).intersection(set(other)) )

    # my first preference is to have both ^ and & operate as intersection.  will this be okay?  
    #   do we need a real xor for these items?
        
    __and__ = intersection
    __xor__ = intersection

from collections import namedtuple        

class relation(set):
    
    tuple_d = None               # class variable holds the extended namedtuple class

    def __init__(self, heading, rows=() ,_name = None):                          # can create empty as: relation(header) 
        if _name is None: 
            _name = 'relation_'+hex(id(self))[5:-2]
        self.name = _name
        self.heading = tuple_set( heading )
        super(relation, self).__init__(rows)                        # superclass init is: set.__init__(rows)
        
        self.rel_tuple = namedtuple(self.name, self.heading)
        
        class tuple_d(self.rel_tuple):
            """extends the namedtuple allowing indexing (getitem) by field name."""
            def __getitem__(self, k):
                if k in self._fields:
                    n =   self._fields.index( k)
                    return super(tuple_d, self).__getitem__(n)
                else:
                    return super(tuple_d, self).__getitem__(k)

            def __repr__(self):
                'Return a nicely formatted representation string'
                return _name + "(" + ", ".join(["%s=%r"% (k, self[k]) for k in self._fields]) +  ")"

        self.tuple_d = tuple_d

    def __repr__(self):
        """relation( ('a', 'b'), [(1, 2), (3, 4), (2, 3), (3, 5)] )"""

        # return '%s( %r, %r )' % (self.__class__.__name__, self.heading, self.dictrepr() ) 
        return '%s( %r, %r )' % (self.__class__.__name__, self.heading, list(set(self)) ) 

    def __iter__(self):
        """ set-based iterator which returns tuple_d's (a dict-like object of attr=value items) """
        for row in set(self):  # don't say "for row in self:" not here, not now
            yield self.tuple_d( *row  )

        
    def equals(self, other):
        """comparison of two operands."""
        if not isinstance(other, self.__class__): # if we don't recognize "other" we let the other decide if we're equal
            return NotImplemented

        # either exact match on content or headings and rows are permutatoins (use output of whole relation to compare)

        if self.heading == other.heading:                       # if headings are the same, equality is equality of sets
            return set.__eq__(self, other)  
        elif set(self.heading) != set(other.heading):           # no chance if headings aren't set equal
            return False
        elif  len(self) != len(other):                          # len(self.rows)
            return False
        else:
            return  set([tuple([r[k] for k in self.heading]) for r in self]) \
                        == set([ tuple ([r[k] for k in self.heading]) for r in other])

    __eq__ = equals

    def not_equals(self, other):
        """comparison of two operands."""
        if not isinstance(other, self.__class__): # if we don't recognize "other" we let the other decide if we're not equal
            return NotImplemented
        return  not self.equals(other) # (set(self) != set(other)) or (self.heading != other.heading)

    __ne__ = not_equals




import unittest


 
class relation_TestCase( unittest.TestCase ):
    """ Class to test relation """
    
    def assertReallyEqual(self, a, b):
        # assertEqual first, because it will have a good message if the
        # assertion fails.
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        # self.assertEqual(0, cmp(a, b)) # TypeError: cannot compare sets using cmp()
        # self.assertEqual(0, cmp(b, a)) # TypeError: cannot compare sets using cmp()


    def assertReallyNotEqual(self, a, b):
        # assertNotEqual first, because it will have a good message if the
        # assertion fails.
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        # self.assertNotEqual(0, cmp(a, b))
        # self.assertNotEqual(0, cmp(b, a))

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

        r1 = relation( ('a', 'b') )
        
        # print type(r1.tuple_d), r1.tuple_d, r1.tuple_d( *(1,2,3) )

        rows = [r for r in r1]
        
        print rows
        
        r2 = relation( ('a', 'b', 'c') , [(1,2,3)], 'rel001')
        print r2, [r for r in r2], r2.tuple_d

        r2 = relation( ('a', 'b', 'c') , [(1,2)], 'rel001')
        
        print r2, [r for r in r2]
        

    def test_0601_relation(self):
        """ relation heading """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )

        self.assertIsInstance(r1.heading, tuple_set)
        self.failUnlessEqual( r1.heading ,tuple_set( ['a', 'b']  ) , "heading not initialized.")
        self.failUnlessEqual( r1.heading ,tuple_set( ( 'a', 'b' )  ) , "heading not initialized.")
        self.failUnlessEqual( r1.heading ,tuple_set( { 'a':1 , 'b':2 }  ) , "heading not initialized.")

        ts1 = tuple_set( ('a', 'b') )

        self.assertNotEqual(r1, ts1)

    def test_061_relation(self):
        """ relation rows """
                
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )
        # row = r1[0]  , TypeError: 'relation' object does not support indexing

        import operator
        self.failUnlessRaises(TypeError, operator.getitem,(r1, 0) )  

        rows = [r for r in r1]
        
        self.assertEqual( set(rows) , set([r1.tuple_d(a=1, b=2), r1.tuple_d(a=3, b=2), r1.tuple_d(a=3, b=4), r1.tuple_d(a=3, b=5)]))

        self.assertSetEqual( set(rows)  , set([r1.tuple_d(a=1, b=2), r1.tuple_d(a=3, b=2), r1.tuple_d(a=3, b=4), r1.tuple_d(a=3, b=5)]) )

        rows = [r for r in r1 if r.a == 1]

        # [tuple_d(a=1, b=2)]

        print rows
        
        r = rows[0] # tuple_d(a=1, b=2)
        
        self.assertEqual( r.a , 1)
        self.assertEqual( r['a'], 1)
        self.assertEqual( r[0] , 1)

        # operator.getitem(r , 2) 
        
        self.assertEqual( r[1] , 2)
        operator.getitem (  r , 1  ) 
        self.assertRaises(IndexError, operator.getitem,  r , 2  )  
        # self.assertRaises(TypeError, operator.getitem,  r , 2  )  

        # self.assertEqual( r[2], 1)

        

    def test_062_relation(self):
        """ relation equality """
                
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )
        r2 = relation( ('a', 'b'), [(3, 4), (3, 5) , (3, 2), (1, 2) ] )    # permutation of two rows from r1
        r3 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 5), (3, 4)] )        #permutation of one row from r1

        # exactly equal, not "set equal"
        
        self.assertEqual( r1 , r3)
        self.assertEqual( r1 , r2)
        self.assertEqual( r2 , r3)
        
        self.assertReallyEqual(r1, r2)
        
        # permutation of header and/or rows
        
        r4 = relation( ('b', 'a'), [(2, 3), (2,1), (4,3), (5,3)] )        #permutation of header and rows
        
        r5 = relation( ('b', 'a'), [(3, 2), (1, 2), (3, 5), (3, 4)] )        #permutation of header but not rows

        self.assertEqual( r1 , r4)
        
        self.assertReallyEqual(r1, r4)

        #    relation as set of rows

        self.assertSetEqual(r1, set( [(1, 2), (3, 2), (3, 4), (3, 5)] ) )

        # self.assertSetEqual(r1, set( [(1, 2), (3, 2), (3, 4), (3, 6)] ) )
        
        # AssertionError: Items in the first set but not the second:
        # (3, 5)
        # Items in the second set but not the first:
        # (3, 6)
        
        
        




    # print dir(relation_TestCase)
        
    # 'addCleanup',                 'addTypeEqualityFunc',  'assertAlmostEqual', 'assertAlmostEquals', 
    # 'assertDictContainsSubset',   'assertDictEqual',      'assertEqual', 'assertEquals', 
    # 'assertFalse',                'assertGreater',        'assertGreaterEqual', 'assertIn', 'assertIs', 
    # 'assertIsInstance',           'assertIsNone',         'assertIsNot', 'assertIsNotNone', 'assertItemsEqual', 
    # 'assertLess',                 'assertLessEqual',      'assertListEqual', 'assertMultiLineEqual', 
    # 'assertNotAlmostEqual',       'assertNotAlmostEquals', 'assertNotEqual', 
    # 'assertNotEquals',            'assertNotIn', 'assertNotIsInstance', 'assertNotRegexpMatches', 
    # 'assertRaises',               'assertRaisesRegexp', 'assertRegexpMatches', 'assertSequenceEqual', 
    # 'assertSetEqual',             'assertTrue', 'assertTupleEqual', 'assert_', 
    # 'countTestCases',             'debug',    'defaultTestResult', 'doCleanups', 
    # 'fail', 'failIf',             'failIfAlmostEqual', 'failIfEqual', 'failUnless', 
    # 'failUnlessAlmostEqual',      'failUnlessEqual', 'failUnlessRaises', 
    # 'failureException',           'id',     'longMessage', 'maxDiff', 'run', 
    # 'setUp',                      'setUpClass', 'shortDescription', 'skipTest', 
    # 'tearDown',                   'tearDownClass' 
    
if __name__ == '__main__':
    unittest.main()
    
    
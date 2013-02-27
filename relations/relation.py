#!/usr/bin/env python
# encoding: utf-8
"""
relation.py -- an implementation of the relational algebra object

Created by donb on 2013-02-24.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

#    A relation contains a heading and a body.  


from collections import namedtuple        

class tuple_set_exception(Exception):
    pass

class tuple_set(tuple):
    """tuple_set maintain order and ensures all elements are unique."""
    
    def __new__(cls, iterable=()):                          # to subclass a non-mutable, like tuple, we use __new__().
        s = [a for a in iterable]                           # s used internally to guard against exhaustion of iterable
        if len( set(s) ) != len(s):                         # uniqueness requires the length of iterator match its length as a set
            raise tuple_set_exception("tuple_set given duplicate entries %r uniques are %r" % (  tuple(s),  tuple(set(s))))
        return super(tuple_set, cls).__new__(cls, s ) 
    
    # def __init__(self, iterable=() ):                     # "there is no __init__ for a tuple (non-mutable)"
        
    def union(self, other):
        """union of two operands as sets, then made into a tuple_set."""
        return self.__class__( set(self).union(set(other)) )

    __or__ = union

    def intersection(self, other):
        """intersection of two operands as sets, then made into a tuple_set."""
        return self.__class__( set(self).intersection(set(other)) )

    # my first preference is to have both ^ and & operate as intersection.  will this be okay?   do we need a real xor
    __and__ = intersection
    __xor__ = intersection


class RelationException(Exception):
    pass
    
class RelationTupleLengthException(RelationException):
    def __init__(self, obj, explanation):
        self.obj = obj
        self.explanation = explanation

    def __str__(self):
        return "%s failed on %r" % (self.explanation, self.obj )

# (r, "Restriction should be a function, e.g. lambda t: t.id == 3 (%s)" % restriction)

class RelationConstraintException(RelationException):
    def __init__(self, obj, constraint_name):
        self.obj = obj
        self.constraint_name = constraint_name

    def __str__(self):
        return "Constraint %s failed on {%s}" % (self.constraint_name, ", ".join(self.obj.heading()))

class RelationInvalidOperationException(RelationException):
    def __init__(self, obj, explanation):
        self.obj = obj
        self.explanation = explanation

    def __str__(self):
        return "%s on column headings {%s}" % (self.explanation, ", ".join(map( repr , self.obj.heading )) )

class RelationUnsupportedOperandTypesException(RelationException):
    def __init__(self, obj, explanation):
        self.obj = obj
        self.explanation = explanation

    def __str__(self):
        return "Unsupported operand type(s) %s on {%s}" % (self.explanation, ", ".join(self.obj.heading()))

#===========================================================================
#   relation
#
#       TODO allow heading to be a dictionary with type info, e.g., {'a':IntType, 'b':StringType}
#               (or more complex type trees from relations database)
#
#    The heading represents an ordering that has been introduced to the attributes
#    and which corresponts to the order of the values in each row. This shared domain of
#    the tuples in T1 is referred to as the heading of table T1. If “T is a table over H” 
#    then H is referred to as the *heading* of T.
#    [Applied Mathematics for Database Professionals—Lex de Haan and Toon Koppelaars]


class relation(set):
    
    def __init__(self, heading, rows=() ,in_name = None):
        if in_name is None: 
            in_name = 'relation_'+hex(id(self))[5:-2]

        self.name = in_name
        self.heading = tuple_set( heading )
        # rows = [r for r in rows]
        # try:
        super(relation, self).__init__([ self._convert_to_row(r) for r in rows])
        # except:
            # pass
            
        # super(relation, self).__init__([ tuple(r) for r in rows])

        # create specific namedtuple and then subclass to extend functionality to include indexing, eg, tuple['k']
        class tuple_d( namedtuple(self.name, self.heading) ):
            """extends the namedtuple allowing indexing (getitem) by field name."""
            __slots__ = ()
            
            @property
            def fields(self):                                        # eg, tuple_d.
                return self._fields

            def __getitem__(self, k):
                if k in self._fields:
                    n =   self._fields.index(k)
                    return super(tuple_d, self).__getitem__(n)
                else:
                    return super(tuple_d, self).__getitem__(k)

            def __repr__(self):
                'Return a nicely formatted representation string'
                return in_name + "(" + ", ".join(["%s=%r"% (k, self[k]) for k in self._fields]) +  ")"

        self.tuple_d = tuple_d                                      # specialized namedtuple class stored as instance variable

        
    def add(self, in_map):
        """ add takes a single element, even if that element is a sequence"""
        new_row = self._convert_to_row(in_map)        # whould we check length?        
        set.add(self, new_row)

    def _convert_to_row(self, in_row):
        if hasattr(in_row, 'get'):                                  # 'get' ==> subscript[ing]
            return tuple( map (in_row.get , self.heading) )
        else:
            if len(in_row) == len(self.heading):
                return tuple(in_row)
            else:
                print "_convert_to_row", len(in_row), len(self.heading)
                raise RelationTupleLengthException(in_row, "Attempt to insert row %r into relation with heading %r" % (in_row, self.heading) )

    def project(self, heading):
        r = self.__class__( heading )        # default empty body eg: relation( ('a',), [] )
        for row in self:
            r.add( r._convert_to_row(row) )   # r._tuple_to_row uses r.heading to project row   
        return r

    def __getitem__(self, attr):
        """ syntactical shorthand: r(['id', 'name']) is r.project( ['id', 'name']) """
        return self.project( attr)

    def __call__(self, restriction = lambda r:True):
        """ syntactical shorthand: r( restrict_fn ) is r.where( restrict_fn ) """
        return RESTRICT(self, restriction)

    def __repr__(self):
        """relation( ('a', 'b'), [(1, 2), (3, 4), (2, 3), (3, 5)] )"""
        return '%s( %r, %r )' % (self.__class__.__name__, self.heading, list(set(self)) ) 


    def __iter__(self):
        """ set-based iterator which returns tuple_d's (a dict-like object of attr=value items) """
        for row in set(self):  # don't say "for row in self:" not here, not now
            yield self.tuple_d._make( row  )
            # yield self.tuple_d( *row  )
        
    def equals(self, other):
        """comparison of two operands."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.heading == other.heading:                       # if headings are the same, equality is equality of sets
            return set.__eq__(self, other)  
        elif set(self.heading) != set(other.heading):           # no chance if headings aren't set equal
            return False
        elif  len(self) != len(other):                          # len(self.rows)
            return False
        else:
            return  set([tuple([r[k] for k in self.heading]) for r in self]) \
                        == set([ tuple ([r[k] for k in self.heading]) for r in other])  # list is not hashable

    __eq__ = equals

    def not_equals(self, other):
        """comparison of two operands."""
        if not isinstance(other, self.__class__): # if we don't recognize "other" we let the other decide if we're not equal
            return NotImplemented
        return  not self.equals(other) # (set(self) != set(other)) or (self.heading != other.heading)

    __ne__ = not_equals


    def where(self, restriction = lambda r:True):
	        """Restrict rows by condition, e.g. r.where(lambda t: t.x==3)"""
	        return RESTRICT(self, restriction)

#  from Dee.py   there is a strategy that creates a pseudo relation for the condition 
#       and then joins i.e. implemented in terms of AND macro.  this would be more general for the future...
#       return AND(r, relation(r.heading, relationFromCondition(restriction)))        
   
def RESTRICT(r, restriction = lambda trx:True):
        """Restrict rows based on condition"""
        if not callable(restriction):
            raise RelationInvalidOperationException(r, "Restriction should be a function, e.g. lambda t: t.id == 3 (%s)" % restriction)
        rows = [row for row in r if restriction(row)]
        return relation ( r.heading , rows) # can create relatin from list of tuple_d's or any getitem'able types


import unittest


 
class relation_TestCase( unittest.TestCase ):
    """ Class to test relation """
    
    def test_050_tuple_set(self):
        """ tuple_set uniqueness"""
                
        #   tuple_set_exception: tuple_set given (3) ('a', 'c', 'a') should be (2) ('a', 'c')
        self.failUnlessRaises(tuple_set_exception, tuple_set, ('a', 'b', 'a') )  


    def test_051_tuple_set(self):
        """ tuple_set.                simple properties of..."""
        
        ts1 = tuple_set(  ( 'a', 'b') )
        ts2 = tuple_set(  ( 'b', 'a') )
        
        # order matters when comparing tuple_sets
        self.assertReallyNotEqual(ts1, ts2)
        
        
        ts1 = tuple_set( ['a', 'b'] )
                
        self.assertReallyEqual( ts1 , ('a', 'b' ) )     # a tuple_set (used internally for heading) is equal to a tuple.

        self.assertNotEqual(  ts1 , ['a', 'b'] ,"tuple_set is not list.")

        ts2 = tuple_set( { 'a':1 , 'b':2 }  )

        self.assertEqual( ts2 ,tuple_set( ('a', 'b')  ) , "tuple_set is tuple not dictionary.")
                
        
        
    def test_052_tuple_set(self):
        """ tuple_set set algebra"""
        
        ts1 = tuple_set( ('a', 'b', 'e') )
        ts2 = tuple_set( ('b', 'c', 'e') )
        ts3 = ts1 & ts2

        # can't know the order of result of tuple_set combinations

        self.assertIsInstance(ts3, tuple_set)
        self.assertEqual(ts3,  tuple_set(('b', 'e')))

        ts4 = ts1 ^ ts2
        self.assertIsInstance(ts4, tuple_set)
        self.assertEqual(ts4, tuple_set(('b', 'e')) )

        ts5 = ts1 | ts2
        self.assertIsInstance(ts5, tuple_set)
        self.assertEqual(ts5,  tuple_set(('a', 'c', 'b', 'e')))
  
        

    def test_0600_relation(self):
        """ relation creation from list of "get"-able objects"""

        #   empty relation
        r1 = relation( ('a', 'b') )
        self.assertEqual( r1 , relation( ('a', 'b'), [] ))
        self.assertEqual( [r for r in r1] , [] )
        self.assertEqual( repr(r1), "relation( ('a', 'b'), [] )" )
        
        # can create relation from iterable of any "getitem-able" type like dict or namedtuple
        r2 = relation( ('a', 'b') , [ { 'a':3, 'b':5 } , {'a':6, 'b':84 } ] )
        self.assertSetEqual (set(r2) , set([(6, 84), (3, 5)]))

        # can have extra keys
        r3 = relation( ('a', 'b') , [ { 'a':6, 'b':5 } , {'a':6, 'b':22 , 'c': 99} ] )
        self.assertSetEqual (set(r3) , set([(6, 22), (6, 5)]))

        # can be missing keys, (filled in with None)
        r4 = relation( ('a', 'b') , [ { 'a':1, 'b':5 } , {'a':36 } ] )
        self.assertSetEqual (set(r4) , set([(36, None), (1, 5)]))
        
        # rows sourced from tuple_d's
        r5 = relation( ('a', 'b') , [r2.tuple_d(a=6, b=7), r2.tuple_d(a=3, b=15)]  )
        self.assertSetEqual (set(r5) , set( [(3, 15), (6, 7)] ))
                
        r6 = relation( ('a', 'b') , [ r2.tuple_d( 1, 2 ), r2.tuple_d( 3, 5 ) ]  )
        self.assertSetEqual( set([r for r in r6]) , set([ r2.tuple_d( 1, 2 ), r2.tuple_d( 3, 5 ) ]) )
        
        t1 = r1.tuple_d( 1, 2 )
        r2 = relation ( ('a', 'b'), [t1])
        self.assertEqual( r2 , relation( ('a', 'b'), [ r1.tuple_d( 1, 2 ) ] ))
        

    def test_0610_relation(self):
        """ relation creation from tuple-like types"""
        
        # can create relation from iterable of any tuple-like types
        
        r1 = relation( ('a', 'b'), [(6, 84), (3, 5)] )
        
        self.assertSetEqual (set(r1) , set( [(6, 84), (3, 5)] ))
        
        # but only if tuples are exactly the length of the heading

        with self.assertRaises(RelationException):
            r1 = relation( ('a', 'b'), [(6, 7), (3, )] )
            
        
    def test_0620_relation(self):
        """ relation creation via generator"""

        heading = ('a','b','c', 'd', 'e' )

        # generator generates x number of dictionaries matching heading
        
        def gen(x):
            for i in range(x):
                yield dict( [ (k , n + i*2)  for n,k in enumerate(heading) ] )                

        # print [n for n in gen(5)] # [{'a': 0, 'c': 2, 'b': 1, 'e': 4, 'd': 3}, {'a': 2, 'c': 4, 'b': 3, 'e': 6, 'd': 5}, ...

        r4 = relation (('a','b','c', 'd', 'e' )  )
        
        rows = gen(5)
        # print [r for r in rows]
        print [ r4._convert_to_row(r) for r in rows] # [(0, 1, 2, 3, 4), (2, 3, 4, 5, 6), 

        g = gen(5)
        r4 = relation (('a','b','c', 'd', 'e' ) , g )
        self.assertEqual (r4 , relation( ('a', 'b', 'c', 'd', 'e'), [(4, 5, 6, 7, 8), (6, 7, 8, 9, 10), (2, 3, 4, 5, 6), (8, 9, 10, 11, 12), (0, 1, 2, 3, 4)] ))

        # test exhaustion of generator
        r5 = relation (('a','b','c', 'd', 'e' ) , g )
        self.assertEqual( r5 , relation( ('a', 'b', 'c', 'd', 'e'), [] ))


    def test_0630_relation(self):
        """ relation creation via generator"""

        #  add

        in_dict = {'a': 5, 'b':6 }

        t2 =  tuple([in_dict[k] for k in r2.heading]) 
        t3 = r2._convert_to_row(in_dict)

        
        self.assertEqual( t2, t3)

        r3 = relation( ('a', 'b', 'd') , [ { 'b':5 , 'a':3 } , {'a':6, 'b':84, 'c':99} ,  ] )
        print r3
        
        r2.add( in_dict )
        self.assertEqual( r2 , relation( ('a', 'b'), [(5, 6), (6, 84), (3, 5)] ) )
        length_before = len(r2)
        
        r2.add( in_dict )
        self.assertEqual( r2 , relation( ('a', 'b'), [(5, 6), (6, 84), (3, 5)] ) )
        self.assertTrue( len(r2) == length_before )

        # r2 = relation( ('a', 'b', 'c') , [(1,2,3)], 'rel001')
        # print r2, [r for r in r2], r2.tuple_d
        # 
        # r2 = relation( ('a', 'b', 'c') , [(1,2)], 'rel001')
        # 
        # print r2, [r for r in r2]
        

    def test_0640_relation(self):
        """ relation and tuple_d """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] , "test")
        
        self.assertEqual( repr(r1), "relation( ('a', 'b'), [(1, 2), (3, 2), (3, 4), (3, 5)] )" )
        
        t1 = r1.tuple_d( *(1,2) )
        t2 = r1.tuple_d( a=1, b=2 )
        t3 = r1.tuple_d( b=2, a=1 )
        
        print "t3.fields:", t3.fields

        self.assertEqual(  t1 , t2 )
        self.assertEqual(  t2 , t3 )
        
        self.assertIn(  t2 , r1 )
        self.assertIn(  t3 , r1 )

        t4 = r1.tuple_d( a=2, b=1 )
        
        self.assertEqual( repr(t4), "test(a=2, b=1)" )

        # test(a=2, b=1) not found in relation( ('a', 'b'), [(1, 2), (3, 2), (3, 4), (3, 5)] )
        self.assertNotIn(  t4 , r1)    
        
        self.assertEqual( t1.a , 1)
        self.assertEqual( t1['a'], 1)
        self.assertEqual( t1[0] , 1)
        

        d1 = {'a':3, 'b':6 }
        t5 =  r1.tuple_d(**d1)
        self.assertEqual( t5, r1.tuple_d(a=3, b=6) )

        d2 = {'a':3, 'b':6, 'c':7 }
        result = map(d2.pop, ('x', 'y', 'z') , t1) # [1, 2, None]

        
        # try:
        #     t6 =  r1.tuple_d(**d2)  # TypeError: __new__() got an unexpected keyword argument 'c'
        # except TypeError:
        #     pass

        s = [d1[k] for k in r1.tuple_d._fields] # [3, 6]
        # print dir(r1.tuple_d)
        # print t5
        # print t1._replace(a=45) # test(a=45, b=2)
        self.assertEqual( t1._replace(a=45), r1.tuple_d(a=45, b=2) )
        
     
    def test_0650_relation(self):
        """ relation and tuple_d """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )

        self.assertIsInstance(r1.heading, tuple_set)
        self.assertEqual( r1.heading ,tuple_set( ['a', 'b']  ) , "heading not initialized.")
        self.assertEqual( r1.heading ,tuple_set( ( 'a', 'b' )  ) , "heading not initialized.")
        self.assertEqual( r1.heading ,tuple_set( { 'a':1 , 'b':2 }  ) , "heading not initialized.")

        ts1 = tuple_set( ('a', 'b') )

        self.assertNotEqual(r1, ts1)

    def test_0660_relation(self):
        """ relation and tuple_d """
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] ,"r1")
        r2 = relation( ('c', 'd', 'e'), [(3, 2), (1, 2), (3, 4), (3, 5)] , "r2" )
        
        print r1.tuple_d(a=1, b=2)
        # print r2.tuple_d(a=1, b=2) # TypeError: __new__() got an unexpected keyword argument 'a'
        print r2.tuple_d(c=1, d=2, e=6) # TypeError: __new__() got an unexpected keyword argument 'a'
        

    def test_0670_relation(self):
        """ relation rows """
                
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )
        # row = r1[0]  , TypeError: 'relation' object does not support indexing

        import operator
        self.failUnlessRaises(TypeError, operator.getitem,(r1, 0) )  

        # operator.getitem (  r1 , 2  ) 
        # # self.assertRaises(IndexError, operator.getitem,  r , 2  )  

        rows = [r for r in r1]
        
        self.assertEqual( set(rows)     , set([r1.tuple_d(a=1, b=2), r1.tuple_d(a=3, b=2), r1.tuple_d(a=3, b=4), r1.tuple_d(a=3, b=5)]))

        self.assertSetEqual( set(rows)  , set([r1.tuple_d(a=1, b=2), r1.tuple_d(a=3, b=2), r1.tuple_d(a=3, b=4), r1.tuple_d(a=3, b=5)]) )

    def test_0680_relation(self):
        """ relational restriction / where() """
                
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] , "restrict_test" )

        # RelationInvalidOperationException: Restriction should be a function, 
        #       e.g. lambda t: t.id == 3 (7) on column headings {'a', 'b'}

        self.failUnlessRaises(RelationInvalidOperationException, r1.where , 7)

        # do a restrict explicitly
        z = lambda r: r.a == 1 or r.b == 2
        rows = [r for r in r1 if z(r)]
        r2 = relation ( ('a', 'b') , rows)
        
        self.assertEqual( r2, relation( ('a', 'b'), [(1, 2), (3, 2)] ))

        # compare to where()
        r3 = r1.where(lambda r: r.a == 1 or r.b == 2)
        self.assertEqual( r3, relation( ('a', 'b'), [(1, 2), (3, 2)] ))

        r3 = r1.where(lambda r: r.a == 3 and r.b == 2)
        self.assertEqual( r3, relation( ('a', 'b'), [(3, 2)]   ))

        r3 = r1.where(lambda r: r == ( 3,5))
        self.assertEqual( r3, relation( ('a', 'b'), [(3, 5)] ) )

        r3 = r1.where(lambda r: r == r1.tuple_d(a=1, b=2) )
        self.assertEqual( r3, relation( ('a', 'b'), [(1, 2)] ) )

        
        # 
        # r = rows[0] # tuple_d(a=1, b=2)
        # 
        # 
        # # operator.getitem(r , 2) 
        # 
        # self.assertEqual( r[1] , 2)
        # operator.getitem (  r , 1  ) 
        # self.assertRaises(IndexError, operator.getitem,  r , 2  )  
        # # self.assertRaises(TypeError, operator.getitem,  r , 2  )  
        # 
        # # self.assertEqual( r[2], 1)

        

    def test_0690_relation(self):
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
        
    def test_0691_relation(self):
        """ project """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )
                          
        self.assertEqual( r1.project(('a',)) , relation( ('a',), [(3,), (1,)] ) )

        self.assertEqual( r1.project(('b',)) , relation( ('b',), [(2,), (5,), (4,)] ) )
        
        self.assertEqual( r1.project(('a', 'b')) , r1 , "project on two columns" )
        

#        a1 = r1['a']        # __getitem__ returns list, not set?

        self.assertEqual( r1['a'], relation( ('a',), [(3,), (1,)] ) )
        
        self.assertEqual( r1(lambda r: r.b == 4) , relation( ('a', 'b'), [(3, 4)] ))
        
        r4 = relation( ('a', 'b'), [(3, 4)] )
        
        self.assertEqual( r4['b'], relation( ('b',), [(4,)] ))

        
    def assertReallyEqual(self, a, b):
        # assertEqual has a good message if the assertion fails.
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        # self.assertEqual(0, cmp(a, b)) # TypeError: cannot compare sets using cmp()
        # self.assertEqual(0, cmp(b, a)) # TypeError: cannot compare sets using cmp()


    def assertReallyNotEqual(self, a, b):
        # assertEqual has a good message if the assertion fails.
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        # self.assertNotEqual(0, cmp(a, b))
        # self.assertNotEqual(0, cmp(b, a))

        




    # print dir(relation_TestCase)
        
    # 'addCleanup',                 'addTypeEqualityFunc',  'assertAlmostEqual', 'assertAlmostEquals', 
    # 'assertDictContainsSubset',   'assertDictEqual',      'assertEqual', 'assertEquals', 
    # 'assertFalse',                'assertGreater',        'assertGreaterEqual', 'assertIn', 'assertIs', 
    # 'assertIsInstance',           'assertIsNone',         'assertIsNot', 'assertIsNotNone', 'assertItemsEqual', 
    # 'assertLess',                 'assertLessEqual',      'assertListEqual', 'assertMultiLineEqual', 
    # 'assertNotAlmostEqual',       'assertNotAlmostEquals', 'assertNotEqual', 
    # 'assertNotEquals',            'assertNotIn',          'assertNotIsInstance', 'assertNotRegexpMatches', 
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
    
    
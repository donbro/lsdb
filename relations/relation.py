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


from collections import namedtuple        

class tuple_set_exception(Exception):
    pass

class tuple_set(tuple):
    """tuple_set maintain order and ensures all elements are unique."""
    
    # to subclass a non-mutable, like tuple, we use __new__().
    def __new__(cls, iterable=()):
        s = [a for a in iterable]
        # as a test of uniqueness we check the length of the iterator against its representation as a set
        if len( set(s) ) != len(s):
                raise tuple_set_exception("tuple_set given duplicate entries %r uniques are %r" % (  tuple(s),  tuple(set(s))))
        return super(tuple_set, cls).__new__(cls, s ) # s used internally in case iterable is exhausted
    
    # "there is no __init__ for a tuple"
    # def __init__(self, iterable=() ):
    #     pass
        
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
        return "%s on column headings {%s}" % (self.explanation, ", ".join([repr(k) for k in self.obj.heading]) )

class RelationUnsupportedOperandTypesException(RelationException):
    def __init__(self, obj, explanation):
        self.obj = obj
        self.explanation = explanation

    def __str__(self):
        return "Unsupported operand type(s) %s on {%s}" % (self.explanation, ", ".join(self.obj.heading()))


class relation(set):
    
    tuple_d = None               # this class variable holds the extended subclass of namedtuple

        # TODO allow heading to be a dictionary with type info, e.g., {'a':IntType, 'b':StringType}
        #       (or more complex type trees from relations database)

    def __init__(self, heading, rows=() ,_name = None):
        if _name is None: 
            _name = 'relation_'+hex(id(self))[5:-2]
        self.name = _name
        self.heading = tuple_set( heading )
        rows = [r for r in rows]
        try:
            return super(relation, self).__init__([ tuple([r[k] for k in heading]) for r in rows])
        except:
            pass
        super(relation, self).__init__([ tuple(r) for r in rows])


        # extend functionality of namedtuple with a subclass
        class tuple_d( namedtuple(self.name, self.heading) ):
            """extends the namedtuple allowing indexing (getitem) by field name."""
            __slots__ = ()
            
            @property
            def hypot(self):
                return (self.x ** 2 + self.y ** 2) ** 0.5

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

def RESTRICT(r, restriction = lambda trx:True):

        """Restrict rows based on condition"""

           # this is from Dee.py where there is a strategy taht creates a pseudo relation for the condition 
           #  and then joins i.e. implemented in terms of AND macro.  this would be more general for the future...
   
        if not callable(restriction):
            raise RelationInvalidOperationException(r, "Restriction should be a function, e.g. lambda t: t.id == 3 (%s)" % restriction)

        # return AND(r, relation(r.heading, relationFromCondition(restriction)))
        # Hs = tuple(r1.heading().union(r2.heading()))

        rows = [row for row in r if restriction(row)] # list of tuple_d
        
        return relation ( r.heading , rows)

        # Bs = []
        # relType = relation(r1.heading, [])
        # for tr1 in r1._scan():
        #     relType.setBody([tr1])
        #     for tr2 in r2._scan(relType):   #returns only matching row(s) = fast
        #         tr1.update(tr2)
        #         Bs.append(dictToTuple(Hs, tr1))    #Note deep copies varying dict
        # 
        # return relation(r.heading, Bs)    #Note: removes duplicate attributes
        

def AND(r1, r2):
        """Natural join
           Ranges from intersection (both relations have same heading)
           through natural join (both relations have one or more common attributes)
           to cartesian (cross) join (neither relation has any attribute in common)
        """
        #Optimise the order
        if callable(r1._body):
            if not callable(r2._body):
                return AND(r2, r1)
            else:
                if not(r1._body.func_code.co_argcount == 0 or (r1._body.func_code.co_argcount == 1 and isinstance(r1._body, types.MethodType))):   #e.g. a view (function which returns a relation, i.e. complete set) #todo unless recursive!
                    if r2._body.func_code.co_argcount == 0 or (r2._body.func_code.co_argcount == 1 and isinstance(r2._body, types.MethodType)):   #e.g. a view (function which returns a relation, i.e. complete set) #todo unless recursive!
                        return AND(r2, r1)
                    else:
                        raise RelationInvalidOperationException(r1, "Cannot AND two functional relations")

        #Can we optimise the hash-join loop? i.e. scan the smallest
        if not callable(r2._body):
            if len(r1._body) > len(r2._body):
                return AND(r2, r1)

        #todo allow a list of relation parameters and call optimiser to order their execution (same for OR, COMPOSE etc)
        Hs = tuple(r1.heading().union(r2.heading()))
        Bs = []
        relType = relation(r1.heading, [])
        for tr1 in r1._scan():
            relType.setBody([tr1])
            for tr2 in r2._scan(relType):   #returns only matching row(s) = fast
                tr1.update(tr2)
                Bs.append(dictToTuple(Hs, tr1))    #Note deep copies varying dict

        #todo infer constraints!
        #todo: need mechanism... based on Darwen's algorithm?
        ##    #Infer constraints  #todo put in one routine?
        ##    #dict([(cname, (_convertToConstraint(kn), p)) for cname, (kn, p) in self.constraint_definitions.items()])
        ##    constraints = {}
        ##    for (rr, prefix) in [(r1, 'L_'), (r2, 'R_')]:
        ##        for cname, (kn, p) in rr.constraint_definitions.items():
        ##            if _convertToShorthand(kn) == 'Key':
        ##                if set(p).issubset(set(Hs)):
        ##                    constraints[prefix+cname] = (_convertToConstraint(kn), p)

        return relation(Hs, Bs)    #Note: removes duplicate attributes
# 
# ##Wrappers: these wrap a lambda expression and make it behave like a relation so the A algebra can be used,
# ## e.g. RESTRICT and EXTEND can be implemented in terms of AND
# def relationFromCondition(f):
#     def wrapper(trx):
#         if f(trx):
#             return [Tuple()]    #DUM
#         else:
#             return []           #DEE
# 
#     return wrapper
# 
# def relationFromExtension(f):
#     def wrapper(trx):
#         return [f(trx)]
# 
#     return wrapper

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
        """ relation creation """

        r1 = relation( ('a', 'b') )
        
        self.assertEqual( [r for r in r1] , [] )

        self.assertEqual( repr(r1), "relation( ('a', 'b'), [] )" )
        
        # can create relation from iterable of any "getitem-able" type
        
        r2 = relation( ('a', 'b') , [ { 'a':3, 'b':5} , {'a':6, 'b':84} ] )
        self.assertEqual( r2 , relation( ('a', 'b'), [(6, 84), (3, 5)] )  )


        r2 = relation( ('a', 'b') , [ { 'b':5 , 'a':3 } , {'a':6, 'b':84, 'c':99} ,  ] )
        self.assertEqual( r2 , relation( ('a', 'b'), [(6, 84), (3, 5)] )  )
        
        # r2 = relation( ('a', 'b', 'c') , [(1,2,3)], 'rel001')
        # print r2, [r for r in r2], r2.tuple_d
        # 
        # r2 = relation( ('a', 'b', 'c') , [(1,2)], 'rel001')
        # 
        # print r2, [r for r in r2]
        

    def test_0601_relation(self):
        """ relation and tuple_d """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] , "test")
        
        self.assertEqual( repr(r1), "relation( ('a', 'b'), [(1, 2), (3, 2), (3, 4), (3, 5)] )" )
        
        t1 = r1.tuple_d( *(1,2) )
        t2 = r1.tuple_d( a=1, b=2 )
        t3 = r1.tuple_d( b=2, a=1 )

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
        
     
    def test_0602_relation(self):
        """ relation and tuple_d """

        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )

        self.assertIsInstance(r1.heading, tuple_set)
        self.assertEqual( r1.heading ,tuple_set( ['a', 'b']  ) , "heading not initialized.")
        self.assertEqual( r1.heading ,tuple_set( ( 'a', 'b' )  ) , "heading not initialized.")
        self.assertEqual( r1.heading ,tuple_set( { 'a':1 , 'b':2 }  ) , "heading not initialized.")

        ts1 = tuple_set( ('a', 'b') )

        self.assertNotEqual(r1, ts1)

    def test_0610_relation(self):
        """ relation rows """
                
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] )
        # row = r1[0]  , TypeError: 'relation' object does not support indexing

        import operator
        self.failUnlessRaises(TypeError, operator.getitem,(r1, 0) )  

        rows = [r for r in r1]
        
        self.assertEqual( set(rows)     , set([r1.tuple_d(a=1, b=2), r1.tuple_d(a=3, b=2), r1.tuple_d(a=3, b=4), r1.tuple_d(a=3, b=5)]))

        self.assertSetEqual( set(rows)  , set([r1.tuple_d(a=1, b=2), r1.tuple_d(a=3, b=2), r1.tuple_d(a=3, b=4), r1.tuple_d(a=3, b=5)]) )

    def test_0611_relation(self):
        """ relational restriction / where() """
                
        
        r1 = relation( ('a', 'b'), [(3, 2), (1, 2), (3, 4), (3, 5)] , "restrict_test" )

        # RelationInvalidOperationException: Restriction should be a function, 
        #       e.g. lambda t: t.id == 3 (7) on column headings {'a', 'b'}

        self.failUnlessRaises(RelationInvalidOperationException, r1.where , 7)

        z = lambda r: r.a == 1 or r.b == 2

        rows = [r for r in r1 if z(r)] # [restrict_test(a=1, b=2), restrict_test(a=3, b=2)]
        
        r2 = relation ( ('a', 'b') , rows)
        
        self.assertEqual( r2, relation( ('a', 'b'), [(1, 2), (3, 2)] ))
        # sys.exit()
        
        r3 = r1.where(lambda r: r.a == 1 or r.b == 2)
        self.assertEqual( r3, relation( ('a', 'b'), [(1, 2), (3, 2)] ))

        
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
    
    
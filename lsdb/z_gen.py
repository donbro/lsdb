#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-04-10.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os


def clean_end( source ):
    for line in source:
        yield line.rstrip()

def split_fields( source ):
    for line in source:
        yield line.split()
        
def compose_gen(*args): # gen_1, gen_2):
    print args
    """
    compose(gen_1, func_2, unpack=False) -> function
    
    The function returned by compose is a composition of gen_1 and func_2.
    That is, compose(gen_1, func_2)(5) == gen_1(func_2(5))
    """
    
    # if not callable(gen_1):
    #     raise TypeError("First argument to compose must be callable")
    # if not callable(func_2):
    #     raise TypeError("Second argument to compose must be callable")
    
    for x in args[1]( args[0]() ):
    # for x in args[1](z for z in args[0]()):
        yield x
    # for x in args[1]( _z ):
    #     yield x
        
    # if unpack:
    #     def composition(*args, **kwargs):
    #         return gen_1(*func_2(*args, **kwargs))
    # else:
    #     def composition(*args, **kwargs):
    #         return gen_1(func_2(*args, **kwargs))
    # return composition
        

def x_gen():
    for x in range(5):
        print "x_gen", x
        yield x
        
def y_gen(s):
    for y in s:
        if y not in [3,5]:
            yield y

def z_gen(s):
    for z in s:
        if z == 4:
            print "z_gen",
            yield 44
        yield z

# a = compose_gen (x_gen, y_gen, z_gen)
# print a
# b = y_gen(a)
# c = z_gen(b)
# for x in a:
for x in z_gen( y_gen( x_gen() ) ):    
    print x
    
# So you are just using generator functions as a convenient notation for iterator decorators. 
# I think the example of Nick D is much better, since it highlights the continuation aspect    
# [http://codepython3.appspot.com/question/5080fb364f1eba38a4d9409e]    
#     
# with open('somefile','r') as source:
# 
#     data= convert_pos( split_fields( discard_blank( clean_end( source ) ) ), 0 )
#     total= 0
#     for l in data:
#         print l
#         total += l[0]
#     print total
#     
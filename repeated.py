#!/usr/bin/env python
# encoding: utf-8
"""
repeated.py

Created by donb on 2013-01-24.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

def square(x):
     print "square(%d)" % x
     return x * x

def repeated(f, n):
     def rfun(p):
         return reduce(lambda x, _: f(x), xrange(n), p)
     return rfun

def main():
    f = square
    n = 5
    p = 3
    
    print reduce(lambda x, _: f(x), xrange(n), p)
    print

    do_it =  repeated(square, 5)
    
    do_it(3)
    print    
    do_it(4)
    print

if __name__ == '__main__':
	main()


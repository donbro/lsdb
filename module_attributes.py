#!env python
# encoding: utf-8

"""
#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""

"""
module_attributes.py

Output a summary of the attributes in a specific module

Created by donb on 2013-01-19.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""


import sys
#import os



# import mysql.connector
# theModule = mysql.connector
# 
# db = mysql.connector.connect(unix_socket='/tmp/mysql.sock', user='root', password='')



import objc
theModule = objc




def keys_from_kvt(s):
	return [ a['k'] for a in s]

def display_kvt(l,s):
	if s == []:
		return "no %s.\n" % (l,)
#		return "no %ss (list empty)(%d).\n" % (l, len(s) )
	
	if list != type(s):
		print "arg to display_kvt must be list ", type(s), "of dicts with keys ('k', 'v', 't')"
	if dict != type(s[0]):
		print "arg to display_kvt must be list of dicts (found ", type(s[0]), ") with keys ('k', 'v', 't')"
	
	ss = [ a['k'] for a in s]
	ss.sort()
	return "%s (%d)\n\n%r\n" % (l, len(s) , ss )

def display_set(l,s):
	ss = list(set(s))
	ss.sort()
	return "%s (%d)\n\n%r\n" % (l, len(s) , ss )

def display_set_count_only(l,s):
	ss = set(s)
	return "%s (%d)\n" % (l, len(s) )


def display_kvt_count_only(l,s):
	if s == []:
		return "no %s.\n" % (l,)
	
	return "%s (%d)\n" % (l, len(s) )

#	kvt is a list of dicts, one dict for each attribute; keys are: ('k', 't', 'v')

def get_kvt(s):
	r = [  ( k , getattr(theModule, k ) ) for k in set(s)]
	return [  dict( k=k , t=type(v) , v=v ) for k ,v in r]

def diff_kvts(s1, s2):
	return	get_kvt(set(keys_from_kvt(s1)).difference(set(keys_from_kvt(s2))))
	

# def set_by_type(s, t):
# 	if isinstance(t,basestring):
# 		return set([ d['k'] for d in s if t  in str(d['t']) ])
# 	if type(t) == type:
# 		return set([ d['k'] for d in s if d['t'] == t ])
# 	print "error in set by type", t
#

def kvt_by_type(s, t):
	if isinstance(t,basestring):
		return [ d for d in s if t  in str(d['t']) ]
	if type(t) == type:
		return [ d for d in s if d['t'] == t ]
	print "error in set by type", t


def diff_dicts(d1, d2):
	return set(d1.keys()).difference(d2.keys())


#
# 		BEGIN
#


print "Module %r\n" % (getattr(theModule, '__name__','no name'), )

if theModule.__doc__ is None:
	print 'no module doc string.\n'
else:
	print "%s\n" % (theModule.__doc__,)


try:
	print "module path is %s\n" % (u'…/'+'/'.join(theModule.__file__.split('/')[-5:]),)
except:
	print "module has no path.\n"


try:
	print 'module package is ', theModule.__package__, "\n"
except:
	print 'no module package.\n'
	

#
# 		attrs in module dir() (54)
#


dir_kvt = get_kvt(dir( theModule ))
print display_kvt_count_only('attrs in module dir()', dir_kvt)

#
# 		builtins
#

# By default, when in the __main__ module, __builtins__
# is the built-in module __builtin__ (note: no 's');
# when in any other module, __builtins__ is an alias
# for the dictionary of the __builtin__ module itself.
#
#	eg,
#
#	__builtins__.__dict__ == mysql.connector.__builtins__
#

#  remove ['__builtins__', '__doc__', '__name__', '__package__'] from builtins

try:
	builtins_set =  set( theModule.__builtins__ ).difference(set(['__builtins__', '__doc__', '__name__', '__package__']))
except AttributeError:
	builtins_set = set([])
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

#
#	module doesn't always have all/any builtins.  we're looking for those that it dows
#  AttributeError: "'module' object has no attribute 'bytearray'"

print display_set_count_only('builtins (140)',  builtins_set)

dir_and_builtins = builtins_set.intersection( set(keys_from_kvt(dir_kvt)))

print display_set_count_only("builtins also in dir()", dir_and_builtins)

s = list(dir_and_builtins)
s.sort()

import __builtin__
for a in s:
#	print repr(a), "\n"
	w1 = getattr(__builtin__, a)
	w2 = getattr(theModule, a)
	print "%24s:\t%s" % ("__builtin__."+a, w1)
	print "%24s:\t%s" % (theModule.__name__+"."+a, w2)
	print

#print
 

#
# 	after displaying overlap between builtins and dir
#		remove builtins and other common module attributes from dir.  (why?)
#

dir_kvt = 	get_kvt(set(keys_from_kvt(dir_kvt)).difference(
			set(list(builtins_set) +
			['__all__', '__builtins__', '__file__', '__path__','__doc__','__name__','__package__'] )) )


print display_kvt_count_only('dir() minus builtins', dir_kvt)


#
# 		attrs in module (__all__) (33)
# 		maybe there is no __all__, then use dir() ??
#

try:
	all_kvt = get_kvt(theModule.__all__)
	print display_kvt_count_only('attrs in module (__all__)',  all_kvt)
except AttributeError:
	print "module has no __all__, using dir()\n"
	all_kvt = dir_kvt
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise



print "----"
print


#
#		just look at those in __all__ from here out.  (okay, but why?)
#

#	types

all_types = kvt_by_type(all_kvt, type )

print display_kvt('types',all_types )

all_leftover = diff_kvts(all_kvt, all_types)

#print display_kvt('all_leftover', all_leftover )

#	instances

all_instance = kvt_by_type(all_leftover, 'instance' )

print display_kvt('instances', all_instance )

# if len(all_instance) > 0:
# 	print "\n".join(["%20s: %r" % (d['k'],d['v'].__class__) for d in all_instance])
# 	print

all_leftover = diff_kvts(all_leftover, all_instance)

#print display_kvt('all_leftover', all_leftover )

#	strings

a = kvt_by_type(all_leftover, str )

print display_kvt_count_only('strings', a )

if len(a) > 0:
	print "\n".join(["%20s: %r" % ( d['k'], (d['v'][:52])
			+ (( "" , "..." ) [len(d['v']) > 52]) ) for d in a])
	print


all_leftover = diff_kvts(all_leftover, a)

#print display_kvt('all_leftover', all_leftover )

#	integers

a = kvt_by_type(all_leftover, int )

print display_kvt_count_only('integers', a )

if len(a) > 0:
	print "\n".join(["%20s: %r" % (d['k'],d['v']) for d in a])
	print

all_leftover = diff_kvts(all_leftover, a)

#print display_kvt('all_leftover', all_leftover )

#	functions

def subtract_by_type(xxx, t):
	a = kvt_by_type(all_leftover, t )

	
	if t in ['bool', bool]:
		t = 'bool'
		if len(a) == 0:
			print display_kvt_count_only(t+'s', a )
		else:
			print display_kvt_count_only(t+'s', a )
			print "\n".join(["%20s: %r" % (d['k'],d['v']) for d in a])
			print
	elif t in ['function']:
		print display_kvt_count_only(t+'s', a )
		print "\n".join(["%20s: %s\n" % (d['k'], d['v'].__doc__ ) for d in a])
		# print "\n".join(["%20s: %s\n" % (d['k'], d['v'].__doc__.split("\n")[0][:56] ) for d in a])
		# print "\n".join(["%20s: %s\n" % (d['k'], d['v'].__doc__[:80]+ ( "" if len(d['v'].__doc__)>80 else u"…" )) for d in a])
	
	else:
		print display_kvt(t+'s', a )
	
	return diff_kvts(all_leftover, a)


all_leftover = subtract_by_type(all_leftover, "function" )

# a = kvt_by_type(all_leftover, "function" )
#
# print display_kvt('functions', a )
#
#
# all_leftover = diff_kvts(all_leftover, a)


#	classobj

a = kvt_by_type(all_leftover, "classobj" )

print display_kvt('classobj', a )

all_leftover = diff_kvts(all_leftover, a)

#	None type (!)

all_leftover = subtract_by_type(all_leftover, 'NoneType')

#	modules

all_leftover = subtract_by_type(all_leftover, 'module')

#	dicts

all_leftover = subtract_by_type(all_leftover, 'dict')

#	float

all_leftover = subtract_by_type(all_leftover, 'float')

#	bool

all_leftover = subtract_by_type(all_leftover, bool)

#	bool

all_leftover = subtract_by_type(all_leftover, 'list')

#	check for leftovers

if len(all_leftover) > 0:
	
	print display_kvt('all_leftover', all_leftover )
	
	print all_leftover[:4]
else:
	print "That's all folks!"

sys.exit()
# 
# 
# if __name__ == '__main__':
#   main()
# 

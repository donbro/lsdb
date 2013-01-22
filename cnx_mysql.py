#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8


"""
untitled.py

Created by donb on 2013-01-22.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os



import mysql.connector
from mysql.connector import errorcode


def main():
    config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'filesx',
    'raise_on_warnings': True
    }

    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Username or password %r and %r?" % (config['user'], config['password']))
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print "Database %r does not exist." % config['database'] 
		else:
			print 'err:', err
    else:
		cnx.close()
	    

if __name__ == '__main__':
    main()


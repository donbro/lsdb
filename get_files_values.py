#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
untitled.py

Created by donb on 2013-01-22.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import objc
import sys
import os

# RIP FSSpec
# Note “FSSpec” is a deprecated type in Apple’s APIs.
# The type is not availble for 64-bit code,
# and shouldn’t be used for new development.
# [http://packages.python.org/pyobjc/core/fsref-fsspec.html]
# FSSpecs are deprecated on Mac OS X and their use is highly discouraged.
# They have trouble with internationalization and cannot support some
# files with more than 31 characters in their name. Avoid them at all costs.
# [http://cocoadev.com/wiki/FSSpec]

from Foundation import NSFileManager, NSURL, NSURLNameKey, NSURLTypeIdentifierKey , \
            NSURLIsDirectoryKey ,\
            NSURLIsVolumeKey, \
            NSURLLocalizedTypeDescriptionKey, CFURLGetFSRef


from datetime import date, datetime, timedelta

import mysql.connector
from mysql.connector import errorcode



props2 =[ 	NSURLNameKey, NSURLTypeIdentifierKey ,
    NSURLIsDirectoryKey , # NSURLFileSizeKey
    "NSURLTotalFileSizeKey" , "NSURLContentAccessDateKey",
    "NSURLFileResourceTypeKey",  # NSURLCreationDateKey,
    NSURLIsVolumeKey, "NSURLVolumeIdentifierKey",
    NSURLLocalizedTypeDescriptionKey
] # "NSURLIsUbiquitousItemKey"]


    


def GetURLResourceValues(url, inProps):
	
	values, error =  url.resourceValuesForKeys_error_(
				inProps ,
				None )
	
	if error is not None:
		print
		print error
    
    # convert key strings from unicode(!) to string
	
	return 	dict( zip(   [str(z) for z in values.allKeys() ] , values.allValues() ) )

#
#   And now some mysql connector stuff…
#

def do_cnx_and_insert_array_of_dict(array_of_dict):
    
    config = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'files',
        'buffered': True
        # 'charset': "utf8",
        # 'use_unicode': True
        # 'raise_on_warnings': True
    }
    
    try:
        cnx = mysql.connector.connect(**config)
        
        vol_id = None
        for d in array_of_dict:
            print d['NSURLNameKey']
            vol_id = insert(cnx, d, vol_id)
        
        cnx.close()
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err


def insert(cnx, values_dict, vol_id):
    cursor = cnx.cursor()
    # now = datetime.now()
    
    if vol_id == None:
        
        add_file = ("insert into files "
                        "(folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s ) ");
    
        
        filename         = values_dict[NSURLNameKey]
        file_id          = values_dict['NSFileSystemFileNumber']
        file_size        = values_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
        file_create_date = values_dict['NSFileCreationDate']
        file_mod_date    = values_dict['NSFileModificationDate']
        folder_id        = values_dict['NSFileSystemFolderNumber']
        
        data_file = (int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )
        
        # Insert file
        print "executing", data_file
        cursor.execute(add_file, data_file)
        
        # # Make sure data is committed to the database
        cnx.commit()
        cursor.close()
        
        cursor2 = cnx.cursor()
        query = "select max(vol_id) from files where vol_id RLIKE 'vol[0-9][0-9][0-9][0-9]' "
        # query = ("SELECT first_name, last_name, hire_date FROM employees "
        #     "WHERE hire_date BETWEEN %s AND %s")
        cursor2.execute(query)
        print "vol_id is none"
        # print "executing", query
        zz = [z for z in cursor2]
        # print "zz", zz[0][0]
        vol_id = zz[0][0]
        print "vol_id is: ", repr(vol_id)
        cursor2.close()

    
    else:  # vol_id != None:
        
        add_file = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s, %s ) ");

        
        filename         = values_dict[NSURLNameKey]
        file_id          = values_dict['NSFileSystemFileNumber']
        file_size        = values_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
        file_create_date = values_dict['NSFileCreationDate']
        file_mod_date    = values_dict['NSFileModificationDate']
        folder_id        = values_dict['NSFileSystemFolderNumber']
        
        data_file = (vol_id, int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )
        
        # Insert file
        print "executing", data_file
        cursor.execute(add_file, data_file)
        
        # # Make sure data is committed to the database
        cnx.commit()
        cursor.close()

    
    return vol_id
    
    # cnx.close()


def GetAttributesOfItem(s):
    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
    	print
    	print error
    # >>> map(  lambda x: x*x  ,   [1,2,3] )
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    
    return dz

def m(in_path):
    
    
    url =  NSURL.fileURLWithPath_(in_path)
    
    v = []
    
    while True: # not d1[NSURLIsVolumeKey]:
        
        d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        d1.update(d2)
        v.insert(0,d1)
        print repr(url.path())
        
        url = url.URLByDeletingLastPathComponent()
        if d1[NSURLIsVolumeKey]: break
        
        # d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        # d1.update(d2)
        # v.insert(0,d1)
        # print repr(url.path())
    
    print
    
    # volume will be item zero in the list
    for n, d in enumerate(v):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
            print "is a volume", 1L
        else:
            d.update({'NSFileSystemFolderNumber': v[n-1]['NSFileSystemFileNumber'] })
            print "is not a volume",  v[n-1]['NSFileSystemFileNumber']
    
    print
    
    do_cnx_and_insert_array_of_dict(v)
    
    sys.exit()
    
    
    #   Finder display:
    #   created:    Tuesday, 2012.10.02 20:52
    #   modified:   Thursday, 2013.01.17 09:06
    
    #   'NSFileCreationDate': 2012-10-03 00:52:17 +0000,
    #   'NSFileModificationDate': 2013-01-17 14:06:08 +0000
    
    #   database (display)
    #       2012-10-03 00:52:17
    #       2013-01-17 14:06:08
    
    
    # {'NSURLIsDirectoryKey': False,
    # 'NSFileOwnerAccountName': u'donb',
    # 'NSFileSystemNumber': 234881026L,
    # 'NSFileHFSTypeCode': 0L,
    # 'NSFileReferenceCount': 1L,
    # 'NSFileExtensionHidden': False,
    # 'NSURLVolumeIdentifierKey': <67456400 00000000>,
    # 'NSFileOwnerAccountID': 501L,
    # 'NSURLContentAccessDateKey': 2013-01-16 09:25:28 +0000,
    # 'NSURLFileResourceTypeKey': u'NSURLFileResourceTypeRegular',
    # 'NSURLLocalizedTypeDescriptionKey': u'Document',
    # 'NSFileSize': 13L,
    # 'NSFileHFSCreatorCode': 0L,
    # 'NSFileType': u'NSFileTypeRegular',
    # 'NSURLNameKey': u'Adobe\xae Pro Fonts',
    # 'NSFileGroupOwnerAccountID': 20L,
    # 'NSURLTypeIdentifierKey': u'public.data',
    # 'NSURLIsVolumeKey': False,
    # 'NSFileCreationDate': 2007-01-02 13:18:08 +0000,
    # 'NSFileGroupOwnerAccountName': u'staff',
    # 'NSURLTotalFileSizeKey': 13L,
    # 'NSFilePosixPermissions': 420L,
    # 'NSFileSystemFileNumber': 22756470L,
    # 'NSFileModificationDate': 2007-01-02 13:18:08 +0000}
    


    
    
    # print values
    # print

def main():
    global sharedFM
    sharedFM = NSFileManager.defaultManager()
    
    s = "/"
    s = "/Volumes/Dunharrow"
    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"
#    s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"
    s = "/Users/donb/projects/files/get_files_values.py"
    
    m(s)

if __name__ == '__main__':
    main()


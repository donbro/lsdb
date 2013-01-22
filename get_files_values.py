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
				
	#print type(values)
	#<objective-c class __NSCFDictionary at 0x7fff7f0ff898>
	

	if error is not None:
		print
		print error

	av =  dict( zip(   [str(z) for z in values.allKeys() ] , values.allValues() ) ) # better way to get items?
	
	return av
	
	return dict(  zip(  [str(z) for z in values.allKeys() ] , 	[  u(m) for m in av  ] ))



def do_cnx_insert(values):
    config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'files'
    # 'buffered': True,
    # 'charset': "utf8",
    # 'use_unicode': True
    # 'raise_on_warnings': True
    }

    try:
        cnx = mysql.connector.connect(**config)
        insert(cnx, values)
    except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Username or password %r and %r?" % (config['user'], config['password']))
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print "Database %r does not exist." % config['database'] 
		else:
			print 'err:', err
    else:
		cnx.close()
	    

def insert(cnx, values_dict):
    cursor = cnx.cursor()
    # now = datetime.now()
                    
    add_file = ("insert into files "
                    "( folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
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
    cursor.execute(add_file, data_file)

    # # Make sure data is committed to the database
    cnx.commit()
    cursor.close()
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
	
    print in_path
    print

    url =  NSURL.fileURLWithPath_(in_path)
    
#    print CFURLGetFSRef(url,None) # <objc.FSRef object at 0x10dc0c270>
#    print objc.FSRef.from_pathname(in_path)
    
    v = []
    
    d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
    d1.update(d2)
    v.insert(0,d1)
    
    while not d1[NSURLIsVolumeKey]:
        print url.path()
        print
        url = url.URLByDeletingLastPathComponent()
        print repr(url.path())
        d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        d1.update(d2)
        v.insert(0,d1)
    
    # volume will be item zero in the list
    for n, d in enumerate(v):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
            print "is a volume"
        else:
            d.update({'NSFileSystemFolderNumber': v[n-1]['NSFileSystemFileNumber'] })
            print "is not a volume",  v[n-1]['NSFileSystemFileNumber']

    for d in v:
        mn(d)
        
    sys.exit()
    
def mn(d1):
    
    print d1['NSURLNameKey']
    print
    
     
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
    

    do_cnx_insert(d1)



    # print values
    # print

def main():
    global sharedFM
    sharedFM = NSFileManager.defaultManager()
    # s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"
    s = "/"
    s = "/Volumes/Dunharrow"
    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"
    s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"
    
    m(s)

if __name__ == '__main__':
    main()


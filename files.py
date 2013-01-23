#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
files.py

Created by donb on 2013-01-22.
Copyright (c) 2013 Don Brotemarkle. All rights reserved.
"""

import objc
import sys
import os

# 
#   FSSpec
# 
#   RIP FSSpec
#   Note “FSSpec” is a deprecated type in Apple’s APIs.
#   The type is not availble for 64-bit code,
#   and shouldn’t be used for new development.
#   [http://packages.python.org/pyobjc/core/fsref-fsspec.html]
#   FSSpecs are deprecated on Mac OS X and their use is highly discouraged.
#   They have trouble with internationalization and cannot support some
#   files with more than 31 characters in their name. Avoid them at all costs.
#   [http://cocoadev.com/wiki/FSSpec]

from Foundation import NSFileManager, NSURL, NSURLNameKey, NSURLTypeIdentifierKey , \
            NSURLIsDirectoryKey ,\
            NSURLIsVolumeKey, \
            NSURLLocalizedTypeDescriptionKey, CFURLGetFSRef


from datetime import date, datetime, timedelta

import mysql.connector
from mysql.connector import errorcode

# global sharedFM

sharedFM = NSFileManager.defaultManager()

props2 =[   NSURLNameKey, NSURLTypeIdentifierKey ,
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
    
    return  dict( zip(   [str(z) for z in values.allKeys() ] , values.allValues() ) )

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


    # have to discover vol_id which will then be valid for all files in this group
    
    try:
        cnx = mysql.connector.connect(**config)
        
        vol_id = None

        vol_id = select_file(cnx, array_of_dict[0], vol_id)        

        for d in array_of_dict:

            vol_id = insert(cnx, d, vol_id)
        
        cnx.close()
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err

def select_file(cnx, values_dict, vol_id):

    print "select_file:", values_dict['NSURLNameKey']

    filename         = values_dict[NSURLNameKey]
    file_id          = values_dict['NSFileSystemFileNumber']
    file_size        = values_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = values_dict['NSFileCreationDate']

    select_query = ( "select vol_id, folder_id, file_name, file_id, file_mod_date from files.files "
                        " where file_name = %r  and file_create_date = %r and folder_id = 1 " )
                        

    select_data = (filename.encode('utf8'), str(file_create_date) )

    # zz = execute_query(cnx, select_query, select_data)

    cursor = cnx.cursor()
    
    # print "executing", select_query % select_data
    cursor.execute( select_query % select_data )
    zz = [z for z in cursor]
    
    # [('vol0003', 1, 'Roma', 2, datetime.datetime(2013, 1, 16, 3, 41, 36))]
    
    cursor.close()
    
    if zz == []:
        print "    vol_id is None\n"
        return None
    else:
        print "    vol_id is %r\n" % ( zz[0][0], )

        return zz[0][0]

def execute_query(cnx, query, data):

    # print "executing", query % data
    
    try:

        cursor = cnx.cursor()        
        cursor.execute(query, data)
        zz = [z for z in cursor]
        cnx.commit()
        
        print "zz", zz

        return zz
        

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            n1 = err.msg.index('Duplicate entry')
            n2 = err.msg.index('for key ')
            msg2 = err.msg[n1:n2]
            print "    "+msg2
            print
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
        return None
        
    finally:
        cursor.close()


        
    
def insert(cnx, values_dict, vol_id):

    print "insert:", values_dict['NSURLNameKey']

    filename         = values_dict[NSURLNameKey]
    file_id          = values_dict['NSFileSystemFileNumber']
    file_size        = values_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = values_dict['NSFileCreationDate']
    file_mod_date    = values_dict['NSFileModificationDate']
    folder_id        = values_dict['NSFileSystemFolderNumber']
        
    if vol_id == None:

        add_file_sql = ("insert into files "
                        "(folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s ) ");
        
        data_file = (int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        execute_query(cnx, add_file_sql, data_file)
                
        cursor2 = cnx.cursor()
        query = "select max(vol_id) from files where vol_id RLIKE 'vol[0-9][0-9][0-9][0-9]' "

        cursor2.execute(query)
        print "    vol_id is none"
        zz = [z for z in cursor2]
        vol_id = zz[0][0]
        print "    vol_id is: ", repr(vol_id)
        cursor2.close()
    
    else:  # vol_id != None:
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s, %s ) ");
        
        data_file = (vol_id, int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        execute_query(cnx, add_file_sql, data_file)

    # end if vol_id is None

    return vol_id
    

def GetAttributesOfItem(s):
    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
        print
        print error
    # >>> map(  lambda x: x*x  ,   [1,2,3] )
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    
    return dz

def run_files(options, in_path):
    
    
    url =  NSURL.fileURLWithPath_(in_path)
    
    v = []
    
    print "arg and superfolders:"
    print
    while True: # not d1[NSURLIsVolumeKey]:
        
        d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        d1.update(d2)
        v.insert(0,d1)
        print "    "+repr(url.path())
        
        url = url.URLByDeletingLastPathComponent()
        if d1[NSURLIsVolumeKey]: break
            
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
    
    return
    
    
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

#===============================================================================
# main
#===============================================================================


def main():

    # hack to have Textmate run with hardwired arguments while command line can be free…

    #
    #   some favorite testing files
    #

    s = "/"
    s = "/Volumes/Dunharrow"
    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"
    #    s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"
    s = "/Users/donb/projects/files/get_files_values.py"

    s = "/Volumes/Taos/TV series/Tron Uprising/Season 01/Tron Uprising - 1x01 - The Renegade (1).mkv"
    s = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s = "/Volumes/Dunharrow"
    s = "/Users/donb/projects"


    s = "/Volumes/Brandywine/erin esurance/"
    
    if os.getenv('TM_LINE_NUMBER' ):
        argv = ["--help"]+[s]
        argv = ["-rd 3"]+[s]
        argv = [s]
    else:
        argv = sys.argv[1:]
    
    #
    #   optparse
    #
    # The optparse module is a modern alternative for command line option parsing 
    # that offers several features not available in getopt, including type conversion, 
    # option callbacks, and automatic help generation. There are many more features to 
    # optparse than can be covered here, but this section will introduce some of 
    # the more commonly used capabilities.
    # [http://www.doughellmann.com/PyMOTW/optparse/]

    
    from optparse import OptionParser, OptionValueError
    
    VERSION = "0.6"    
    parser = OptionParser(usage='usage: %prog [options] [filename(s)] ',
                          version='%%prog %s' % VERSION)

    # --help ==>    Usage: get_files_values.py pathname [options] 
    # --version ==> get_files_values.py 0.6


    parser.add_option("-r", "--recursive",  dest="do_recursion",  action="store_const", const=True, 
        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,default=False )
    
                                                
    parser.add_option("-v", "--verbose", dest="verbose_count", 
        help="increment verbose count by one.  default=%default", action="count" ) 
        
        
    def _depth_callback(option, opt_str, value, parser): # , cls):
        if value == "None" or value == "none":
            setattr(parser.values, option.dest, None)
        else:
            try:
                setattr(parser.values, option.dest, int(value))
            except:
                raise OptionValueError("%s value must be integer or None. %s: %r received."
                                   % (option.dest, str(type(value)), value) )


    parser.add_option("-d", "--depth-limit", "--depth", dest="depth_limit", action="callback" , 
        callback=_depth_callback,
        help="limit recusion DEPTH. using DEPTH = 0 means process the directory only.  DEPTH=None means no depth limit (use with caution). "
        "Recursion is implied when any depth-limit is specified. default is %default.",
         metavar="DEPTH", type="string") 

    parser.add_option("-f", "--force-folder-scan", dest="force_folder_scan", action = "store_true", 
        help="explicitly check contents of directories even if directory timestamp not newer than"
        "database value.  Normal operation does not check the contents of a directory if its timestamp equals"
        "that in the database. default = %default", 
        default=False) 
        
        
    #
    #   set defaults and call parser
    #
                          
                          
    parser.set_defaults( verbose_count=1,  ) # depth_limit=1,    

    (options, args) = parser.parse_args(argv)
    args = [os.path.abspath(a) for a in args]
    
    # print ', '.join([ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])
    # print reduce(lambda i,j:i+', '+j, [ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])

    print "options:"
    print
    print "\n".join([  "%20s: %r " % (k,v)  for k,v in options.__dict__.items() ])
    print
    

    print "args:"
    print
    print "\n".join(["    "+x for x in args])
    print
    
    
    for s in args:
        run_files(options, s)
        
        
#   Calling main() from the interactive prompt (>>>). Really?  
#   This is a commandline utility; i'm never going to do that.

if __name__ == "__main__":
        main()
        
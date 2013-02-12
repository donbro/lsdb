#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
~/projects/lsdb/lsdb/files.py

Created by donb on 2013-01-22.
Copyright (c) 2013 Don Brotemarkle. All rights reserved.
"""

import sys

if sys.version_info < (2, 6):
    print "Sorry, python version is %d.%d.  We require Python %d.%d." %  ( sys.version_info.major , sys.version_info.minor, 2, 6)
    sys.exit(1)


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

import objc
import sys
import os


from Foundation import NSFileManager, NSURL, NSURLNameKey, NSURLTypeIdentifierKey , \
            NSURLIsDirectoryKey ,\
            NSURLIsVolumeKey, \
            NSURLLocalizedTypeDescriptionKey, CFURLGetFSRef,\
            NSFileModificationDate, NSFileTypeDirectory, NSFileType


import datetime

import mysql.connector
from mysql.connector import errorcode

__version__ = "0.5"


# global sharedFM

global options

sharedFM = NSFileManager.defaultManager()

props2 =[   NSURLNameKey, NSURLTypeIdentifierKey ,
    NSURLIsDirectoryKey , # NSURLFileSizeKey
    "NSURLTotalFileSizeKey" , "NSURLContentAccessDateKey",
    "NSURLFileResourceTypeKey",  # NSURLCreationDateKey,
    NSURLIsVolumeKey, "NSURLVolumeIdentifierKey",
    NSURLLocalizedTypeDescriptionKey
] # "NSURLIsUbiquitousItemKey"]

from Foundation import NSTimeZone, NSDateFormatter

from dates.dateutils import pr, tz_pr # , get_datestrings, currentCalendar #  _DATETIME_to_python


# choose some timezones with which to display some dates, they're fun!
    
time_zones = [
    ('Local' , NSTimeZone.localTimeZone()) ,
    ('GMT' ,   NSTimeZone.timeZoneForSecondsFromGMT_(0))
    # ('G' , NSTimeZone.timeZoneWithAbbreviation_(u'GMT'))
]

dx = [ {'name' : n , 'tz' : tz, 'df' : NSDateFormatter.alloc().init() } for n, tz in time_zones ]
map ( lambda y : NSDateFormatter.setTimeZone_(y[0], y[1])  , [ (x['df'], x['tz']) for x in dx] )

format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss z" # ==> 'Fri 2011-07-29 19:46:39 EDT' or 'EST', or 'GMT-04:00'
format_string = "E yyyy.MM.dd HH:mm z"              # ==> Tue 2012.04.03 00:39 EDT

map ( lambda y : NSDateFormatter.setDateFormat_(y, format_string)  , [x['df'] for x in dx] )



from Foundation import NSLog

class MyError(Exception):
    def __init__(self, code, description=""):
        self.code = code
        self.description = description
    def __str__(self):
        return "%s (%d)" %  (self.description,  self.code)


def GetURLResourceValues(url, inProps):
    """raises custom exception MyError when, eg, the file does not exist"""
    values, error =  url.resourceValuesForKeys_error_(
                inProps ,
                None )
    
    if error is not None:
        raise MyError(error.code()  , error.localizedDescription())
    
    # convert unicode key strings to string
    
    return  dict( zip(   [str(z) for z in values.allKeys() ] , values.allValues() ) )


def GetAttributesOfItem(s):

    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
        print
        print error
    
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    return dz


def insertItem(cnx, itemDict, vol_id):
    """returns inserted, created, or existing as well as the new/found/provided vol_id"""

    folder_id        = itemDict['NSFileSystemFolderNumber']
    filename         = itemDict[NSURLNameKey]
    file_id          = itemDict['NSFileSystemFileNumber']
    file_size        = itemDict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = itemDict['NSFileCreationDate']
    file_mod_date    = itemDict[NSFileModificationDate]
        
    if vol_id == None:

        add_file_sql = ("insert into files "
                        "(folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s ) "
                        );
        
        data_file = (int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        (l, zz) = execute_insert_query(cnx, add_file_sql, data_file)
        
        if l == "inserted" : 
            l = "created"       # we create a vol_id by inserting, when there is no vol_id to begin with.
        
        vol_id = zz[0][0]

    
    else:  # vol_id != None:
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s, %s ) ");
        
        data_file = (vol_id, int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        (l, zz) = execute_insert_query(cnx, add_file_sql, data_file)


    sa =  dx[0]['df'].stringFromDate_(file_mod_date)
    pathname = itemDict["NSURLPathKey"]
    pr6(l, vol_id, folder_id, file_id, sa, pathname)        

    #   "existing" is special code for duplicate key (returned from execute_insert_query)
    #       We use this at higher levels!

    return l, vol_id


# Using list as the default_factory, it is easy to group a sequence of key-value pairs into a dictionary of lists:
    
from collections import defaultdict
item_tally = defaultdict(list)
 
def gocnx1(cnx, array_of_dict): 
    
    #
    #   Insert superfolders into the database
    #   (discovering/creating the vol_id with first insert without vol_id)
    #
        
    vol_id = None
    
    for item_dict in array_of_dict:
        l, vol_id = insertItem(cnx, item_dict, vol_id)

    #
    #   begin tallying results with the last entry above, the basepath:
    #
    
    item_tally[l].append(item_dict['NSURLPathKey'])
    
    #
    #   now that we have a vol_id, we can insert/update 
    #       the volume specific data including uuid, capaicy, availalbe capacity
    #
    
    # duplicate key part of the row doesn't need update; collision implies values already matches (duh!)
    
    query = ("insert into volume_uuids "
                    "(vol_id, vol_uuid, vol_total_capacity, vol_available_capacity) "
                    "values ( %s, %s, %s, %s ) " 
                    "on duplicate key update "
                    "vol_total_capacity = values(vol_total_capacity), "
                    "vol_available_capacity = values(vol_available_capacity)"
                    );
    
    data = (vol_id, str(array_of_dict[0]['NSURLVolumeUUIDStringKey']) , 
                    str(array_of_dict[0]['NSURLVolumeTotalCapacityKey']),                                                    
                    str(array_of_dict[0]['NSURLVolumeAvailableCapacityKey']) )
                    
    # 'MySQLConverter' object has no attribute '___nscfnumber_to_mysql'                    
    
    (l, zz) = execute_insert_query(cnx, query, data)
    pr4(l, vol_id, "", data[1], 3)
    return vol_id
    

def xxx(cnx, l, hdl, vol_id, file_id):

    # if basepath_dict2['NSFileType'] == NSFileTypeDirectory:

        sql = "select vol_id, folder_id, file_name, file_id from files where vol_id = %r and folder_id = %d "

        data = (vol_id, file_id )

        # this is gonna be a list of files
        
        listOfItems = execute_select_query(cnx, sql, data)
        listOfItems = [(i[0], i[1], i[2].decode('utf8'), i[3]) for i in listOfItems]

        hdl.extend(listOfItems)
        
        if len(listOfItems) > 0:
            # print hdl
            # if folder_id not in hdd:
            #     hdl =  listOfItems
            # else:
            #     hdl = hdl + listOfItems
            # print d
            # print "listOfItems:", listOfItems[0]
            print "%s. adding file_ids (%d) %r to hdl now (%d) " % ( l, len(listOfItems), [r[3] for r in listOfItems], 
                    len(hdl) )

from Foundation import NSDirectoryEnumerationSkipsSubdirectoryDescendants ,\
                        NSDirectoryEnumerationSkipsPackageDescendants ,\
                            NSDirectoryEnumerationSkipsHiddenFiles


def gocnx2(cnx, basepath, vol_id):
    
    # now enumerate through all files within/below the current file/directory
    # An enumeration is recursive, including the files of all subdirectories, 
    # and crosses device boundaries. An enumeration does not resolve symbolic links, 
    # or attempt to traverse symbolic links that point to directories.


#   this:



    #   Enumerate the given directory, basepath, compile a list of 
    #       directories that are not up to date ("existing") in the database

    # >>>
    # >>> s = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]
    # >>> d = defaultdict(list)
    # >>> for k, v in s:
    # ...     d[k].append(v)
    # ...
    # >>> d.items()
    # [('blue', [2, 4]), ('red', [1]), ('yellow', [1, 3])]

    
    basepath_url =  NSURL.fileURLWithPath_(basepath)
    def x(y,z):
        print "x", y, z
        
    s = []
    s2 = []
    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                    basepath_url, 
                    [ NSURLNameKey, NSURLIsDirectoryKey  ],
                              NSDirectoryEnumerationSkipsPackageDescendants |
                              NSDirectoryEnumerationSkipsHiddenFiles,
                              x
                      
                    )

#                                         NSDirectoryEnumerationSkipsSubdirectoryDescendants |

    for url in enumerator2:
        
        depth = enumerator2.level()
        
        if depth : print "depth: ", depth

        # print type(url), url # NSURL
        # values, error =  url.resourceValuesForKeys_error_(
        #         [ NSURLIsDirectoryKey , NSURLNameKey ] ,
        #         None )        # , 
        # 
        # subpath_dict = dict( zip(   [str(z) for z in values.allKeys() ] , values.allValues() ) )

        subpath_dict = GetAttributesOfItem(url.path())  # also NSFileExtendedAttributes
        # print subpath_dict

        subpath_dict.update(GetURLResourceValues(url, [u'NSURLNameKey']))

        subpath_dict.update(  {  "NSURLPathKey":  url.path() })

        folder_url = url.URLByDeletingLastPathComponent()            
        folder_dict =   GetAttributesOfItem(folder_url.path())         
        folder_id        = folder_dict['NSFileSystemFileNumber']

        subpath_dict.update({'NSFileSystemFolderNumber': folder_id }) 
                

        if subpath_dict[NSFileType] == NSFileTypeDirectory:

            l, vol_id = insertItem(cnx, subpath_dict, vol_id)
            item_tally[l].append(url)

            # if l == "existing":
            #     s.append(url)
            # else:
            #     s2.append((url,l))
            
    # print len(s), s
    # print
    # print len(s2), s2
    # print
    sz = set([k for k, v in item_tally.items() if len(v) > 0])
    if sz == set(['existing']):
        print "all (%d) directories are existing" % len(item_tally['existing'])
    else:
        print [(k, len(v), v ) for k, v in item_tally.items() if len(v) > 0 and k != "existing"]
    
        # this call crashes(!):
        #       i.getResourceValue_forKey_error_(objc.NULL, 'NSURLIsDirectoryKey',objc.NULL) # enumerator2.fileAttributes() # ['NSURLIsDirectoryKey']
        
    sys.exit()

    # NSDirectoryEnumerator *dirEnumerator = [localFileManager enumeratorAtURL:directoryToScan
    #                     includingPropertiesForKeys:[NSArray arrayWithObjects:NSURLNameKey,
    #                                                 NSURLIsDirectoryKey,nil]
    #                     options:NSDirectoryEnumerationSkipsHiddenFiles
    #                     errorHandler:nil];
 
    """    // An array to store the all the enumerated file names in
    NSMutableArray *theArray=[NSMutableArray array];
 
    // Enumerate the dirEnumerator results, each value is stored in allURLs
    for (NSURL *theURL in dirEnumerator) {
 
        // Retrieve the file name. From NSURLNameKey, cached during the enumeration.
        NSString *fileName;
        [theURL getResourceValue:&fileName forKey:NSURLNameKey error:NULL];
 
        // Retrieve whether a directory. From NSURLIsDirectoryKey, also
        // cached during the enumeration.
        NSNumber *isDirectory;
        [theURL getResourceValue:&isDirectory forKey:NSURLIsDirectoryKey error:NULL];
 
        // Ignore files under the _extras directory
        if (([fileName caseInsensitiveCompare:@"_extras"]==NSOrderedSame) &&
            ([isDirectory boolValue]==YES))
        {
            [dirEnumerator skipDescendants];
        }
        else
        {
            // Add full path for non directories
            if ([isDirectory boolValue]==NO)
                [theArray addObject:theURL];
 
        }
    }
    """

# end this    
    
    # basepath  = array_of_dict[-1]["NSURLPathKey"]

    # pr4("basepath:", "", "", basepath , 3)
    
    hdd = {}
    hdl = []    # simply a list of all items contained in database for all directories actually processed
                #   for all subpaths of this basepath.


    
    basepath_dict =   GetURLResourceValues(basepath_url, props2) 
    basepath_dict2 =   GetAttributesOfItem(basepath_url.path() ) 
    
    

    # folder_url = basepath_url.URLByDeletingLastPathComponent()            
    # folder_dict =   GetAttributesOfItem(folder_url.path())         
    # folder_id        = folder_dict['NSFileSystemFileNumber']

    
    
    enumerator = sharedFM.enumeratorAtPath_(basepath)

    #   Once for the beginning

    file_id         = enumerator.directoryAttributes()['NSFileSystemFileNumber']
    if basepath_dict2['NSFileType'] == NSFileTypeDirectory:
        xxx(cnx, "basepath", hdl, vol_id, file_id)

    # print "enumerator.directoryAttributes():", enumerator.directoryAttributes()
    #     NSFileCreationDate = "2011-09-28 04:46:52 +0000";
    #     NSFileExtensionHidden = 0;
    #     NSFileGroupOwnerAccountID = 20;
    #     NSFileGroupOwnerAccountName = staff;
    #     NSFileModificationDate = "2013-01-07 04:11:36 +0000";
    #     NSFileOwnerAccountID = 501;
    #     NSFileOwnerAccountName = donb;
    #     NSFilePosixPermissions = 493;
    #     NSFileReferenceCount = 7;
    #     NSFileSize = 238;
    #     NSFileSystemFileNumber = 832;
    #     NSFileSystemNumber = 234881055;
    #     NSFileType = NSFileTypeDirectory;
    
    
    subpath = enumerator.nextObject()
    
    while subpath:

        fullpath = basepath.stringByAppendingPathComponent_(subpath)
        fullpath_url =  NSURL.fileURLWithPath_(fullpath)
        
        subpath_dict =   GetURLResourceValues(fullpath_url, props2) 

        subpath_dict.update( enumerator.fileAttributes() )
        
        subpath_dict.update(  {  "NSURLPathKey":  fullpath })
        
        if subpath_dict[NSURLNameKey][0] == ".":   
            pr4("skipping:", "", "", subpath, 3)
            if subpath_dict['NSFileType'] == NSFileTypeDirectory :
                enumerator.skipDescendents() # dont need to skip whole directory, just this file
            subpath = enumerator.nextObject()
            continue
        
        depth = subpath.count("/") + 1
        depth2 = enumerator.level()
        
        if depth != depth2: print "depth != depth2", depth , depth2, depth != depth2

        if subpath_dict['NSFileType'] == NSFileTypeDirectory and depth > options.depth_limit-1:
            l =  "directory at depth (%d):" % ( depth,)
            pr4(l, "", "",  subpath+"/" )
            enumerator.skipDescendents()
            subpath = enumerator.nextObject()
            continue
            

        # this case might never happen?  we halt the descent at the directory above?  never get to depth_limit?
        if depth > options.depth_limit:
            print "depth limit: %s (%d > %d)?" % ( subpath, depth , options.depth_limit)
            print "unexpected?"
            enumerator.skipDescendents()
            subpath = enumerator.nextObject()
            continue

        #
        #   If none of the above special cases hold, then we process the current path
        #
        
        #   When we are processing a directory we have to check the current contents
        #   of that directory agiainst the contents of the database.
        #   while dancing withthe enumerator.  so:
        #   when a dir is up:
        #       1. query the database, store the contents
        #       2. as the successive files go by, insert/check them against database, then delete them
        #               from our ongoing complete array of all files that have been
        #               seen (at all?) as contents of directory.
        #       3. at the end(?) of the directory, check to see if any are left not deleted by step (2) above
            

        #   get current path's folder, 
        #   (my folder number is my container's file number)
        
        folder_url = fullpath_url.URLByDeletingLastPathComponent()            
        folder_dict =   GetAttributesOfItem(folder_url.path())         
        folder_id        = folder_dict['NSFileSystemFileNumber']
        subpath_dict.update({'NSFileSystemFolderNumber': folder_id })
        

        filename        = subpath_dict[NSURLNameKey]
        file_id         = subpath_dict['NSFileSystemFileNumber']
        # file_size        = subpath_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
        # file_create_date = subpath_dict['NSFileCreationDate']
        # file_mod_date    = subpath_dict[NSFileModificationDate]
        pathname        = subpath_dict["NSURLPathKey"]

        #
        #   if current item is present in the list of items contained by all our processed directories
        #       then remove that item from the list.

        rs = (vol_id, folder_id, filename, file_id)
        
        if rs in hdl:
            # print "rs:", rs
            hdl.remove(rs)
            print "%s. removing %8d %r from hdl now (%d) " % ( "lineitem",  rs[3],rs[2],  len(hdl) )
        else:
            print "rs not in hdl!", rs, len(hdl)
        


        #
        #   Do the actual file or directory
        #
        
        l, vol_id = insertItem(cnx, subpath_dict, vol_id)
        
        #   "existing" is special code for duplicate key (returned from execute_insert_query)
        #   If a directory is existing (in terms of an index that includes mod date) that means no update is 
        #       necessary
        
        if l == "existing":
            print "existing directory.  no update is necessary"
        

        #
        #   if directory, add contents of database for this directory to tracking dictionary
        #
        
        if subpath_dict['NSFileType'] == NSFileTypeDirectory:
            xxx(cnx, "directory", hdl, vol_id, file_id)
            
        subpath = enumerator.nextObject()
        
          
    print "%10s. hdl now (%d) %r" % ( "final", len(hdl) , hdl)

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
        
        vol_id = gocnx1(cnx, array_of_dict)

        basepath  = array_of_dict[-1]["NSURLPathKey"]

        gocnx2(cnx, basepath, vol_id)

        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    finally:
        cnx.close()


def pr4(l, v, d, p, n=1):
    if options.verbose_level >= n:
        s =    "%-10s %-8s %27s %s" % (l, v , d,  p) 
        s =    "%-10s %-8s %s %s" % (l, v , d,  p)   # not fixed 27 but varies with width of third string.
        print s

def pr5(l, v, fid, d, p, n=1):
    if options.verbose_level >= n:
        s =    "%-10s %-8s %27s %s" % (l, v , d,  p) 
        s =    "%-10s %-8s %8d %s %s" % (l, v , fid, d,  p)   # not fixed 27 but varies with width of third string.
        print s

def pr6(l, v, folder_id, file_id, d, p, n=1):
    if options.verbose_level >= n:
        s =    "%-10s %-8s %7d %7d %s %s" % (l, v , folder_id, file_id, d,  p)   # not fixed 27 but varies with width of third string.
        print s

def print_vsd5(l, sl, n):
    if options.verbose_level >= n:     
        print l + ":\n"
        l = [ (d["NSURLPathKey"], 
                "is a volume" if d[NSURLIsVolumeKey] else "is not a volume", 
                    d['NSFileSystemFolderNumber']) for d in sl]
        s =    [ "    %8d  %-16s %s" % (fid,v ,   p) for ( p, v, fid) in l ]
        print "\n".join(s)
        print
    



def execute_select_query(cnx, select_query, select_data, n=3):

    cursor = cnx.cursor()

    if options.verbose_level >= n:     
        print select_query % select_data
    
    cursor.execute( select_query % select_data )
    
    zz = [z for z in cursor]
    
    cursor.close()

    return zz
    

def execute_insert_query(cnx, query, data):
    """ returns (l,z) where l is a string indicating situation: created, existing, etc., and z is the entire result set """

    try:

        cursor = cnx.cursor() # buffered=True)      
        if options.verbose_level >= 3:     
            print query % data  
        cursor.execute(query, data) ## , multi=True)

        cnx.commit()

        q = "select @vol_id"
        cursor.execute(q)
        zz3 = [z for z in cursor]
        
        cnx.commit()
  
        return ("inserted" , zz3 )

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            
            if options.verbose_level >= 3:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2]
                print "    "+msg2

            cnx.commit()

            q = "select @vol_id"
            cursor.execute(q)
            zz3 = [z for z in cursor]
            # print "    vol_id (found):", zz3[0][0]
            cnx.commit()

            return ("existing" , zz3 )  # "existing" is special code for duplicate key: we use this at higher levels!
            
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
        return None
        
    finally:
        
        cursor.close()



def print_dict_tall(l, in_dict, left_col_width=24, verbose_level_threshold=1):
    if options.verbose_level >= verbose_level_threshold:
        print l + ":"
        print
        s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
        print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
        print


def DoSuperfolders(basepath):

    #
    #   1. Generate Superfolder list, including volume
    #   Work upwards from given path to first path that indicates that it is indeed a volume (eg, "/Volumes/volume_name")
    #   Establish volume credentials
    #   Insert given path through volume path into database
    #   if given path is directory then enumerate through contained files and directories (according to options)
    #
    
    #  path given on command line is "basepath"

    url =  NSURL.fileURLWithPath_(basepath)

    # loop-and-a-half here.  go "upwards" and break (and hold) on first volume (ie, where d1[NSURLIsVolumeKey] is true)
    # breaking before moving "up" from the final directory leaves variable "url" pointing to top (volume) directory.        

    superfolder_list = []
    while True:       
        d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        d1.update(d2)
        d1.update(  {  "NSURLPathKey":  url.path() })
        superfolder_list.insert(0,d1)
        if d1[NSURLIsVolumeKey]:         # break before moving "up"
            break
        url = url.URLByDeletingLastPathComponent()            
        

    #   get volume info and copy to the volume item's dictonary

    values, error =  url.resourceValuesForKeys_error_( ['NSURLVolumeUUIDStringKey',
                                                        'NSURLVolumeTotalCapacityKey',
                                                        'NSURLVolumeAvailableCapacityKey',
                                                        'NSURLVolumeSupportsPersistentIDsKey',
                                                        'NSURLVolumeSupportsVolumeSizesKey'] , None )
    if error is not None:
        print
        print error

    d1.update(dict(values))

    print_dict_tall("volume info", values, 36, 3)
    
    # go forwards (downwards) thorugh the list setting each items "folder number" to the file number of its container

    for n, d in enumerate(superfolder_list):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
        else:
            d.update({'NSFileSystemFolderNumber': superfolder_list[n-1]['NSFileSystemFileNumber'] })
    
    print_vsd5("volume, superfolder(s) and basepath", superfolder_list, 2)    
    
    return superfolder_list
    

#===============================================================================
#   DoBasepath
#===============================================================================

def DoBasepath(basepath):

        try:

            superfolder_list = DoSuperfolders(basepath)

            do_cnx_and_insert_array_of_dict(superfolder_list)

        except MyError as e:
            print "Error: " + "%s (%d)" %  ( e.description, e.code )


#===============================================================================
# main
#===============================================================================


def main():

    #
    #   some favorite testing files
    #

    s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"

    s = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s = "/Volumes/Dunharrow"

    s = "/Users/donb/projects/files/get_files_values.py"

    s = "/Users/donb/projects"
    s = "/Volumes/Brandywine/erin esurance/"

    s = "/Volumes/Taos"
    s = "/Volumes/Dunharrow"
    s = "/Volumes/Brandywine/erin esurance/"
    s1 = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s2 = "/Volumes/Taos/TV series/Tron Uprising/Season 01/Tron Uprising - 1x01 - The Renegade (1).mkv"

    
    
    s = u'/Volumes/Sapporo/TV Show/Winx Club/S01/Winx Club - 1x07 - Grounded (aka Friends in Need).avi'
    
    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/S03/'

    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/'

    s = u'/Volumes/Ulysses/TV Shows/'

    s = "/"
    
    s = u"/Users/donb"
    
    s = u'/Volumes/Sacramento/Movies/The Dark Knight (2008) (720p).mkv'

    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"

    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/'

    s = u'/Users/donb/projects/lsdb'
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        # argv = ["--help"]+[s]
        argv = ["-rd 4"]
        argv += ["-v"]
        argv += [s]
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
    
    parser = OptionParser(usage='usage: %prog [options] [filename(s)] ',
                          version='%%prog %s' % __version__ )

    # --help ==>    Usage: get_files_values.py pathname [options] 
    # --version ==> get_files_values.py 0.6


    parser.add_option("-r", "--recursive",  dest="do_recursion",  action="store_const", const=True, 
        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,default=False )
    
                                                
    parser.add_option("-v", "--verbose", dest="verbose_level", 
        help="increment verbose count by one.  default=%default", action="count" ) 

    parser.add_option("-q", "--quiet", 
        action="store_const", const=0, dest="verbose_level", default=1, 
           help="Normal operation is to output one status line per file, status being \"inserted\", \"existing\", etc."
           " This option will prevent any output to stdout, Significant errors are still output to stderr.") 
        
        
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
                          
    parser.set_defaults( verbose_level=1,  depth_limit=1 )

    global options
    
    (options, args) = parser.parse_args(argv)
    
    # no args means do the current directory
    
    if args == []: args = ["."]
    
    args = [os.path.abspath(a) for a in args]
    
    
    # print ', '.join([ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])
    # print reduce(lambda i,j:i+', '+j, [ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])

    # display list of timezones
    if options.verbose_level >= 3:
        print "time_zones:"
        print
        s = [   "%12s: %s" % (x['name'], "%r (%s) %s%s" % tz_pr(x['tz']) ) for x in dx ]
        print "\n".join(s)
        print

    if options.verbose_level >= 2:
        print "sys.argv:"
        print
        print "\n".join(["    "+x for x in sys.argv])
        print

    if options.verbose_level >= 2 or True:
        print "options (after optparsing):"
        print
        print "\n".join([  "%20s: %r " % (k,v)  for k,v in options.__dict__.items() ])
        print
        
    if options.verbose_level >= 2:
        print "args (after optparsing):"
        print
        if args == []:
            print [None]
        else:
            print "\n".join(["    "+x for x in args])
        print
    
    
    for basepath in args:
        DoBasepath(basepath)
        
        
#   Calling main() from the interactive prompt (>>>). Really?  
#   This is a commandline utility; i'm never going to do that.
#
#   maybe.  for testing.  just sayin'

if __name__ == "__main__":
        main()
        
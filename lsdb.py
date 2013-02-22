#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
    ~/projects/lsdb-master/lsdb.py
    
    Created by donb on 2013-01-22.
    Copyright (c) 2013 Don Brotemarkle. All rights reserved.
    
"""

# this file defines the command "lsdb"

import sys
import os

if sys.version_info < (2, 6):
    print "Sorry, python version %d.%d is required. This is version %d.%d." %  (  2, 6, sys.version_info.major , sys.version_info.minor )
    sys.exit(1)

import logging
import datetime
from collections import defaultdict

from optparse import OptionParser, OptionValueError

import mysql.connector
from mysql.connector import errorcode

import objc

from Foundation import NSFileManager, NSURL
from Foundation import NSLog
from Foundation import NSDirectoryEnumerationSkipsSubdirectoryDescendants ,\
                            NSDirectoryEnumerationSkipsPackageDescendants ,\
                            NSDirectoryEnumerationSkipsHiddenFiles, \
                            NSURLCreationDateKey

from LaunchServices import kUTTypeApplication, kUTTypeData, \
                                    UTGetOSTypeFromString, UTTypeCopyDeclaringBundleURL,\
                                    UTTypeCopyDescription, UTTypeCopyDeclaration, UTTypeConformsTo, \
                                    LSCopyItemInfoForURL, kLSRequestExtension, kLSRequestTypeCreator
                                    # _LSCopyAllApplicationURLs

#   see dates module for list of timezones and formatters
from dates import dateFormatters, print_timezones

from files import sharedFM, MyError #  = NSFileManager.defaultManager()

# some Common File System Resource Keys

from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLAttributeModificationDateKey, \
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey

#
#   This table is pretty much what this module is about.  combined with some directory enumeration…
#                        

databaseAndURLKeys = [  ( 'file_name',            NSURLNameKey), 
                        (  None,                  NSURLIsDirectoryKey), 
                        (  None,                  NSURLVolumeURLKey), 
                        (  None,                  NSURLLocalizedTypeDescriptionKey), 
                        ( 'file_uti',             NSURLTypeIdentifierKey), 
                        ( 'file_create_date',     NSURLCreationDateKey), 
                        ( 'file_mod_date',        NSURLContentModificationDateKey), 
                        (  None,                  NSURLParentDirectoryURLKey), 
                        ( 'file_size',           'NSURLTotalFileSizeKey'),
                        ( 'file_id',             'NSFileSystemFileNumber'),
                        ( 'folder_id',           'NSFileSystemFolderNumber' ),
                        (  None,                  NSURLIsVolumeKey)                        
                    ]


enumeratorURLKeys = [t[1] for t in databaseAndURLKeys]

__version__ = "0.5"

global options  # the command-line argument parser options

from files import GetNSFileAttributesOfItem, GetURLResourceValuesForKeys


# simply a list of all items contained in database for all directories actually processed
#   for all subpaths of this basepath.

itemsToDelete = defaultdict(set)
itemsToDelete2 = defaultdict(set)


def itemsToDelete_repr(d):
    # xxcx = " ".join(["%d-%d" % (k, len(v)) for k, v in d.items() ])
    # xxcx = "-".join(["%2d" % (len(v),) for k, v in d.items() ])
    xxcx = "-".join(["%d" % (len(v),) for k, v in d.items() ])
    return xxcx


def DoDBQueryFolder(cnx, l, vol_id,  item_dict, item_stack, depth):

    #   for modified directories (or if force_folder_scan is True):
    #       (1) get contents from database and 
    #       (2) compare this to the current filesystem (iterator's) results for that directory

    #   Here we do (1): get and store the directory's folder_id at item_stack[depth].  
    #   While iterating through the filesystem, check each new item's folder_id against item_stack[depth - 1]

    #   this marks this folder as one that the incoming items shoudl be compared against.
    
    folder_id         = item_dict['NSFileSystemFileNumber']
    item_stack[depth] = folder_id   # we are always just at one folder for any particular depth

    # the fields returned here are those of the primary key of the table (minus file_mod_date).  
    #   define these somewhere/ retrieve them from the database at start?
    
    sql = "select vol_id, folder_id, file_name, file_id from files "+\
            "where vol_id = %r and folder_id = %d "
    data = (vol_id, folder_id )

    # get list of records contained in this directory
    listOfItems = execute_select_query(cnx, sql, data, 4)

    # coming out of the database we decode utf8 to get unicode strings
    listOfItems = [(i[0], i[1], i[2].decode('utf8'), i[3]) for i in listOfItems]

    # since defaultdict, don't create an empty entry if we don't have to?
    if len(listOfItems) > 0:
        itemsToDelete[depth] |= set(listOfItems)




# error handler for enumeratorAtURL
def errorHandler1(y,error):
    print "enumeratorAtURL error: %s (%d)" % (error.localizedDescription(), error.code())


def DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack):
    
    # now enumerate through all files within/below the current file/directory
    # An enumeration is recursive, including the files of all subdirectories, 
    # and crosses device boundaries. An enumeration does not resolve symbolic links, 
    # or attempt to traverse symbolic links that point to directories.


    #   Enumerate the given directory, basepath, compile a list of 
    #       directories that are not up to date ("existing") in the database
    #       for single directory contents only, NSDirectoryEnumerationSkipsSubdirectoryDescendants


    basepath_url =  NSURL.fileURLWithPath_(basepath)

    # some general directory-oriented housekeeping that was in the superfolder processing:

    basepath_dict = GetURLResourceValuesForKeys(basepath_url, enumeratorURLKeys)
    basepath_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories
    
    print_dict_tall("basepath dict", basepath_dict, 32, 4)

    l, vol_id = insertItem(cnx, basepath_dict, vol_id, 0 , item_tally)  

    depth = 0 

    folder_id         = basepath_dict['NSFileSystemFileNumber']
    item_stack[depth] = 0  # placeholder, not actively searchable list

    if l != "existing" or options.force_folder_scan:
        DoDBQueryFolder(cnx, "basepath", vol_id,  basepath_dict, item_stack, depth)
    
    pr8(l, vol_id, basepath_dict, depth)
    
        
    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                            basepath_url, 
                            enumeratorURLKeys,
                            NSDirectoryEnumerationSkipsPackageDescendants |
                                NSDirectoryEnumerationSkipsHiddenFiles,
                            errorHandler1 
                        )

    for url in enumerator2:
        

        item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

        #  we might do this for some pre-defined directories we don't want to enumerate?
        # if ([[path pathExtension] isEqualToString:@"rtfd"]) {
        #     // Don't enumerate this directory.
        #     [directoryEnumerator skipDescendents];


        print_dict_tall("item dict", item_dict, 32, 4)
        # print item_dict
        
        ts1 = item_dict[NSURLLocalizedTypeDescriptionKey]    # eg, 'Folder'

        # A Uniform Type Identifier (UTI) is a text string that uniquely identifies a given class or type of item.
        
         # conformance hierarchy
         #  A conformance hierarchy says that if type A is "above" type B then
         #   “all instances of type A are also instances of type B.”        
    
        #  UTCreateStringForOSType
        #  UTGetOSTypeFromString
        #  UTTypeConformsTo
        #  UTTypeCopyDeclaration
        #  UTTypeCopyDeclaringBundleURL
        #  UTTypeCopyDescription
        #  UTTypeCopyPreferredTagWithClass
        #  UTTypeCreateAllIdentifiersForTag
        #  UTTypeCreatePreferredIdentifierForTag
        #  UTTypeEqual',

        
        uti = item_dict[NSURLTypeIdentifierKey]     
        
        
        # NSLog(t)   
        # print type(t)
        # print ts1, uti

        uti_declaration =  UTTypeCopyDeclaration(uti)
        
        # print "UTTypeCopyDeclaration:", type(uti_declaration), uti_declaration
        # print "UTTypeCopyDeclaringBundleURL:", UTTypeCopyDeclaringBundleURL(uti)  # Folder, public.folder, 'publ'
        # print "UTTypeCopyDescription:", UTTypeCopyDescription(uti)
        # print "UTTypeConformsTo(uti, kUTTypeData):", UTTypeConformsTo(uti, kUTTypeData)
        

        # declaring bundle is, eg, file://localhost/Users/donb/Downloads/ComicBookLover.app/ or
        #                       file://localhost/System/Library/CoreServices/CoreTypes.bundle/
        
        
        
        depth = enumerator2.level()
        
        # print len(item_stack), max(item_stack.keys())+1
        if max(item_stack.keys())+1 > depth: # len(item_stack) > depth:
            pop_item_stack(depth, item_stack, 3)


        if item_dict[NSURLIsDirectoryKey]:
            
            # is a directory
            
            item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

            l, vol_id = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  

            # if the directory shows as modified, get database contents for the directory

            folder_id         = item_dict['NSFileSystemFileNumber']
            item_stack[depth] = 0  # placeholder, not actively searchable list
            # item_stack[depth] = folder_id   # we are always just at one folder for any particular depth

            if l != "existing" or options.force_folder_scan:
                DoDBQueryFolder(cnx, "directory", vol_id,  item_dict, item_stack, depth)

        else:
        
            # not a directory
            
            l, vol_id = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  


        #
        #       Check each item that passes to see if it is in a list of items that  we are tracking.
        #

        folder_id       = item_dict['NSFileSystemFolderNumber']

        if depth-1 in item_stack and folder_id == item_stack[depth-1] and l != "inserted": # no need to check if we just inserted the item

            #   Remove a file item from the list of database contents.

            file_id         = item_dict['NSFileSystemFileNumber']
            filename        = item_dict[NSURLNameKey]

            # these fields are those of the primary key of the table (minus file_mod_date).  define these somewhere/ retrieve them from the database at start?

            rs = (vol_id, folder_id, filename, file_id)
            
            if rs in itemsToDelete[depth-1]:
                itemsToDelete[depth-1].remove(rs)
            else:
                # if l != "inserted":
                # print "\nrs not in itemsToDelete[%d] %r %r\n" %  (depth-1, rs, itemsToDelete[depth-1])
                print "\n%s not in [%d] %s\n" %  ( "%s (%d)" % (rs[2] , rs[3] ), depth-1, ", ".join([( "%s (%d)" % x[2:] )for x in itemsToDelete[depth-1] ] ))
        

        pr8(l, vol_id, item_dict, depth)
            

            
    #end for url in enumerator2

    #  final pop(s) back up to depth zero
    
    depth = 0  # depth is defined as zero for basepath
    pop_item_stack(depth, item_stack, 3)

def max_item_stack(item_stack):
    if len(item_stack.keys()) == 0:
        return None
    else:
        return max(item_stack.keys()) # +1

def s123(item_stack):
    return  ( max_item_stack(item_stack), "%s" % item_stack, "[%s][%s]" % (itemsToDelete_repr(itemsToDelete) , itemsToDelete_repr(itemsToDelete2)) )

def pop_item_stack(depth, item_stack, n=3):
    
    len_s = max_item_stack(item_stack)
    
    # print "pop_item_stack", depth, len_s , item_stack, item_stack.keys(), len(item_stack.keys())
    
    while len_s is not None and max(item_stack.keys())+1 > depth: # len(item_stack) > depth:

        if options.verbose_level >= n:
            print "\npop (%d)(%d):" % (depth, max(item_stack.keys()))  # to [%d] from %d " % (depth , len(item_stack))

            s_before = s123(item_stack)
            # (len(item_stack), "%s" % item_stack, "[%s][%s]" % (itemsToDelete_repr(itemsToDelete) , itemsToDelete_repr(itemsToDelete2)) )
    
        if len(itemsToDelete[len_s]) > 0:
            itemsToDelete2[len_s] |= itemsToDelete[len_s]

        # print "item_stack:", len(item_stack), item_stack , "len_s:", len_s, "max(item_stack.keys())+1", max(item_stack.keys())+1
        
        del itemsToDelete[len_s]
        del item_stack[len_s]

        len_s = max_item_stack(item_stack)

        # if len(item_stack.keys()) > 0:
        #     len_s = max(item_stack.keys())+1 # len(item_stack) # assert: len_s decremented by one.
    
        if options.verbose_level >= n:
            s_after = s123(item_stack)
            # s_after =  (max(item_stack.keys())+1, "%s" % item_stack, "[%s][%s]" % (itemsToDelete_repr(itemsToDelete) , itemsToDelete_repr(itemsToDelete2)) )

            for n, v in enumerate(s_before):
                print "%32s ==> %-32s" % (v, s_after[n])
                
            print 




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

def pr7(l, v, folder_id, file_id, d, depth, p, n=1):
    if options.verbose_level >= n:
        s =    "%-12s %-7s %8d %8d %s %2d %s" % (l, v , folder_id, file_id, d,  depth, p)   # not fixed 27 but varies with width of third string.
        print s


def pr8(l, vol_id, item_dict, depth, n=1):

    file_mod_date    = item_dict[NSURLContentModificationDateKey]

    sa =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)  # needs a real NSDate here?

    pathname         = item_dict["NSURLPathKey"]
    folder_id        = item_dict['NSFileSystemFolderNumber']
    filename         = item_dict[NSURLNameKey]
    file_id          = item_dict['NSFileSystemFileNumber']
    # depth = i - n + 1

    if options.verbose_level >= n:
        s =    "%-12s %-8s %-7s %8d %8d %s %2d %s" % (l, itemsToDelete_repr(itemsToDelete), vol_id , folder_id, file_id, sa,  depth, filename) 
        print s
        # NSLog(s)

# 2013-02-17 00:14:36.649 python[18887:60b] existing              vol0001        1        2 Wed 2013.01.16 01:51 EST -4 Genie



def print_vsd5(l, sl, n):
    if options.verbose_level >= n:     
        print l + ":\n"
        l = [ (d["NSURLPathKey"], 
                "is a volume" if d[NSURLIsVolumeKey] else "is not a volume", 
                    d['NSFileSystemFolderNumber']) for d in sl]
        s =    [ "    %8d  %-16s %s" % (fid,v ,   p) for ( p, v, fid) in l ]
        print "\n".join(s)
        print
    




def asdf(in_obj, left_col_width=12):
    s = "%%%ss: %%r" % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
    return "\n".join([ s % (a, getattr(in_obj,a)) for a in dir(in_obj) if a[0]!="_" and "URL" in a])

def execute_select_query(cnx, select_query, select_data, n=3):

    cursor = cnx.cursor()

    if options.verbose_level >= n:     
        print select_query % select_data
    
    cursor.execute( select_query % select_data )
    
    zz = [z for z in cursor]
    
    cursor.close()

    return zz
    
def execute_update_query(cnx, update_sql, d, n=3):

    cursor = cnx.cursor()
    
    if options.verbose_level >= n:     
        print update_sql % d
    
    cursor.execute( update_sql % d)
    
    # zz = [z for z in cursor]
    
    cnx.commit()
    
    cursor.close()
    

def execute_insert_query(cnx, query, data, verbose_level=3):
    """ returns (l,z) where l is a string indicating situation: created, existing, etc., and z is the entire result set """

    try:

        cursor = cnx.cursor() # buffered=True)      
        if options.verbose_level >= verbose_level:     
            try:
                print repr(query % data)
            except:
                print "unicode error?"
                
        cursor.execute(query, data) ## , multi=True)

        cnx.commit()

        # q = "select @existing_count"
        # cursor.execute(q)
        # zz = [z for z in cursor]
        # if options.verbose_level >= verbose_level:     
        #     print "@existing_count: ", zz
        # existing_count = zz[0][0]

        q = "select @existing_count3"
        # q = "select @existing_count2, @existing_count3"
        cursor.execute(q)
        zz4 = [z for z in cursor]
        if options.verbose_level >= verbose_level:     
            print "@existing_count3: ", zz4             # [('2013-02-19 06:34:21', 18)]
        current_count = zz4[0][0]


        q = "select @vol_id"
        cursor.execute(q)
        zz = [z for z in cursor]
        
        cnx.commit()
        l = "inserted"
        return (l , zz , current_count, zz4)

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            
            if options.verbose_level >= verbose_level:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2-1]
                print "    "+repr(msg2)

            cnx.commit()

            # q = "select @existing_count"
            # cursor.execute(q)
            # zz = [z for z in cursor]
            # if options.verbose_level >= verbose_level:     
            #     print "@existing_count: ", zz
            # existing_count = zz[0][0]

            q = "select @existing_count3"
            cursor.execute(q)
            zz4 = [z for z in cursor]
            if options.verbose_level >= verbose_level:     
                print "@existing_count3: ", zz4
            current_count = zz4[0][0]

            q = "select @vol_id"
            cursor.execute(q)
            zz = [z for z in cursor]
            # print "    vol_id (found):", zz[0][0]
            cnx.commit()

            # "existing" is special code for duplicate key: we use this at higher levels!
            l = "existing"
            return (l , zz , current_count, zz4)  
        
        elif err.errno == 1644 and err.sqlstate == '22012':
            
            # MySQL connector error:  Unhandled user-defined exception condition
            
            if options.verbose_level >= verbose_level:
                n1 = err.msg.index('): ') + len('): ')
                msg2 = err.msg[n1:]

                print '\n'+"MySQL connector error: " , msg2+": " + "%d (%s)" % (err.errno, err.sqlstate)
                # print "\n".join([ "%8s: %r" % (a, getattr(err,a)) for a in dir(err) if a[0]!="_"])
                print
            
            #   we no longer handle in this process the situation where an earlier record(s) exists.

            l = "updated-dup"
            
            # this is probably not needed; we are *not* in autocommit mode.

            
            cnx.commit()            

            q = "select @existing_count3"
            cursor.execute(q)
            zz = [z for z in cursor]
            if options.verbose_level >= verbose_level:     
                print "@existing_count3: ", zz
            current_count = zz[0][0]

            q = "select @vol_id"
            cursor.execute(q)
            zz = [z for z in cursor]
            # print "    vol_id (found):", zz[0][0]
            cnx.commit()

            current_count = 1  # by defn: unique key
            zz4 = None
            return (l , zz , current_count, zz4)  
            
            
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
        return None
        
    finally:
        
        cursor.close()


def insertItem(cnx, itemDict, vol_id,  depth, item_tally): 
    """returns inserted, created, or existing as well as the new/found/provided vol_id"""

    # Convert from item_dict (Cocoa) forms to something that the database DBI can convert from

    d = {}
    for dk, fk in databaseAndURLKeys:
        if dk:
            if fk in [NSURLNameKey, NSURLTypeIdentifierKey]:
                d[dk] =  itemDict[fk].encode('utf8')
            elif dk in ['file_create_date', 'file_mod_date']:
                d[dk] =  str(itemDict[fk])
            else:
                d[dk] =  itemDict[fk]


    # print_dict_tall("insert data", d, 32, 4)

    if vol_id == None:

        add_file_sql = ("insert into files "
                        "(folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                        "values ( %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, %(file_mod_date)s, %(file_uti)s ) "
                        
                        );

        (l, zz, current_count, zz4) = execute_insert_query(cnx, add_file_sql, d, 3)
        
        #   really, there could be existing, inserted (new record, known vol_id), created (new, unknonw) and updated?
        #   totally new directory record suggests no existing records to have to check to see if we deleted.
        #   totally new directory would return no records from the database anyway, but don't need to check.
        
        if l == "inserted" : 
            l = "created"       # we create a vol_id by inserting, when there is no vol_id to begin with.
        
        vol_id = zz[0][0]

        d['vol_id'] = vol_id
    
    else:  # vol_id != None:
        
        d['vol_id'] = vol_id
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                        "values ( %(vol_id)s, %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, %(file_mod_date)s, %(file_uti)s ) "
                        );
        
        (l, zz, current_count, zz4) = execute_insert_query(cnx, add_file_sql, d, 3)

    # end if vol_id == None

    
    if l == "existing" and current_count > 1:  # zero would mean a created record, 1 means update (one earlier record exists), 2 means multiple records exist (a problem?)
        l = "updated"
        item_tally[l].append(d['file_name'])
        l = "updated(%d)" % current_count
    else:
        item_tally[l].append(d['file_name'])

    #   Do the update "by hand" because we can't modify a target table from within a MySQL trigger?!?

    # don't do this!  we won't do this kind of thing here, lets keep the duplicate record and
    #           use it in a lter pass to "update" any dependents
     
    if False and l == "updated-dup":        
        update_sql = ("update files "
                        " set  "
                            " files.file_size           =  %(file_size)s, "
                            " files.file_create_date    =  %(file_create_date)r,  "
                            " files.file_mod_date       =  %(file_mod_date)r,  "
                            " files.file_uti            =  %(file_uti)r   "
                        " where files.vol_id            =  %(vol_id)r "
                        " and files.folder_id           =  %(folder_id)s "
                        " and files.file_name           =  %(file_name)r " )

        execute_update_query(cnx, update_sql, d, 4)
    


    #  see "Just a little Zero" for more on  scheme to represent deletion.

    
    #     delete_sql = ("delete from files "
    #                     " where files.vol_id = %(vol_id)r "
    #                     " and files.folder_id = %(folder_id)s "
    #                     " and files.file_name = %(file_name)r "
    #                     " and files.file_mod_date <= " + repr(max_file_mod_date) )
    #     # print "(max_file_mod_date, b):", (max_file_mod_date, b)
    #     zz = execute_select_query(cnx, delete_sql, d, n=3)
    #     # print "zz:", zz
        
    #   "existing" is special code for duplicate key
    #       We use this at higher levels!

    return l, vol_id



def print_dict_tall(l, in_dict, left_col_width=24, verbose_level_threshold=1):
    if options.verbose_level >= verbose_level_threshold:
        print l + ":"
        print
        s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
        print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
        print


def GetSuperfolderList(basepath):

    """Generate Superfolder list, including volume """
    
    #  path given on command line is "basepath"

    url =  NSURL.fileURLWithPath_(basepath)

    # loop-and-a-half here.  go "upwards" and break (and hold) on first volume (ie, where d1[NSURLIsVolumeKey] is true)
    #   Work upwards from given path to first path that indicates that it is indeed a volume (eg, "/Volumes/volume_name")
    # breaking before moving "up" from the final directory leaves variable "url" pointing to top (volume) directory.        

    superfolder_list = []

    while True:       
        
        d1 = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

        # d1, d2 = ( GetURLResourceValuesForKeys(url, props2), GetNSFileAttributesOfItem(url.path()) )
        # d1.update(d2)
        # d1.update(  {  "NSURLPathKey":  url.path() })

        d1.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

        superfolder_list.insert(0,d1)
        
        if d1[NSURLIsVolumeKey]:         # break before moving "up"
            break
        url = url.URLByDeletingLastPathComponent()            
    
    # last iteration is the volume
    
    volume_url = url
    
    # go forwards (downwards) thorugh the list setting each items "folder number" to the file number of its container

    for n, d in enumerate(superfolder_list):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
        else:
            d.update({'NSFileSystemFolderNumber': superfolder_list[n-1]['NSFileSystemFileNumber'] })
    
    print_vsd5("volume, superfolder(s) and basepath", superfolder_list, 4)
    
    return superfolder_list, volume_url


#===============================================================================
#       DoDBInsertSuperfolders
#===============================================================================
    
def DoDBInsertSuperfolders(cnx, superfolder_list, item_tally, item_stack): 
    
    #
    #   Insert superfolders into the database
    #   (discovering/creating the vol_id with first insert without vol_id)
    #
    #   we don't do basepath here, makes more sense to do it within the basepath enumeration.
    #
        
    vol_id = None
    n = len(superfolder_list)
    for i, item_dict in enumerate(superfolder_list[0:-1]):

        l, vol_id = insertItem(cnx, item_dict, vol_id, i - n + 1, item_tally)  

        depth = i - n + 1
        
        pr8(l, vol_id, item_dict, depth)

    # basepath is processed in basepath enumerator (duh)
        
    if options.verbose_level >= 4 :
        print
            
    return vol_id, l
    


def  DoDBInsertVolumeData(cnx, vol_id, volume_url):
    """ insert/update volumes table with volume specific data, eg uuid, total capacity, available capacity """    

   #   get volume info

    values, error =  volume_url.resourceValuesForKeys_error_( ['NSURLVolumeUUIDStringKey',
                                                        'NSURLVolumeTotalCapacityKey',
                                                        'NSURLVolumeAvailableCapacityKey',
                                                        'NSURLVolumeSupportsPersistentIDsKey',
                                                        'NSURLVolumeSupportsVolumeSizesKey'] , None )
    if error is not None:
        print
        print error

    # volume_dict.update(dict(values))
    dv = dict(values)

    print_dict_tall("volume info", values, 36, 4)
    
    # note this insert includes "on duplicate key update" of vol_total_capacity and vol_available_capacity.
    
    query = ("insert into volume_uuids "
                    "(vol_id, vol_uuid, vol_total_capacity, vol_available_capacity) "
                    "values ( %s, %s, %s, %s ) " 
                    "on duplicate key update "
                    "vol_total_capacity = values(vol_total_capacity), "
                    "vol_available_capacity = values(vol_available_capacity)"
                    );
    
    data = (vol_id, str(dv['NSURLVolumeUUIDStringKey']) ,
                    int(dv['NSURLVolumeTotalCapacityKey']),
                    int(dv['NSURLVolumeAvailableCapacityKey']) )
                    
    (l, zz, current_count, zz4) = execute_insert_query(cnx, query, data, 3)

    pr4(l, vol_id, "", data[1], 4)

    
#===============================================================================
#       DoDBItems
#===============================================================================

def DoDBItems(superfolder_list, volume_url):
    
    #   And now some mysql connector stuff…

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
        
        #   initialize the item tally here
        #   (Using list as the default_factory, it is easy to group a sequence 
        #           of key-value pairs into a dictionary of lists)

        item_tally = defaultdict(list)
        item_stack = {}
        
        
        try:

            vol_id, l = DoDBInsertSuperfolders(cnx, superfolder_list, item_tally, item_stack)


       
            # update volume info for the volume which is the [0]'th entry

            DoDBInsertVolumeData(cnx, vol_id, volume_url)
            
            # our original path, basepath, is the last entry in the superfolder list

            basepath  = superfolder_list[-1]["NSURLPathKey"]

            if superfolder_list[-1][NSURLIsDirectoryKey]:  
                DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack)
            else:
                print "no enumeration for non-directory."

        except KeyboardInterrupt:
            print "KeyboardInterrupt (hey!)"
            pass
        
        #
        #   wrapup: format and print final tallys
        #

        print "\nfinal tallys:"
        
        item_tally_keys = [k for k, v in item_tally.items() if len(v) > 0 ]
        # print item_tally_keys , ['existing'], item_tally_keys == ['existing']
        if item_tally_keys == ['existing']:  # set(item_tally_keys) == set(['existing']):
            print "\n    All filesystem items are existing (%d)." % len(item_tally['existing'])
        else:
            print
            print "\n".join(["%15s (%d) %r" % (k, len(v), map(str,v) ) for k, v in item_tally.items() if len(v) > 0 ])

        if item_stack == {}:
            print "    item_stack is empty."
        else:
            print "\n    item_stack:", item_stack
    
        # print
        # print "itemsToDelete:\n\n", itemsToDelete_repr(itemsToDelete), itemsToDelete.keys()
        # # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), list(v)) for k, v in itemsToDelete.items()  ])
        # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete.items()  ])
        # # print

        if len(itemsToDelete) == 0:
            print "    itemsToDelete is empty."
        else:
            print "    itemsToDelete:\n\n", itemsToDelete_repr(itemsToDelete), itemsToDelete.keys()
            print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete.items()  ])

        if len(itemsToDelete2) == 0:
            print "    itemsToDelete2 is empty."
        else:
            print "    itemsToDelete2 is [%s]:\n" % itemsToDelete_repr(itemsToDelete2) # , itemsToDelete2.keys()
            # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
            print '\n\n'.join([  "    %d: %s" % (k,  [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])



        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    finally:
        cnx.close()


#===============================================================================
#   DoBasepath
#===============================================================================

def DoBasepath(basepath):

        try:

            superfolder_list, volume_url = GetSuperfolderList(basepath)
 
            DoDBItems(superfolder_list, volume_url)

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
    

    s = u'/Volumes/Ulysses/TV Shows/'

    s = "/"
    
    s = u"/Users/donb"
    
    s = u'/Volumes/Sacramento/Movies/The Dark Knight (2008) (720p).mkv'

    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"

    
    # s = u'/Volumes/Dunharrow/Authors/Karl Popper/Popper - Unended Quest (autobiography).pdf'
    s = u"/Volumes/Dunharrow/iTunes Dunharrow/TV Shows/The No. 1 Ladies' Detective Agency"

    s = "/Volumes/Brandywine/erin esurance/"





    s = u'/Users/donb/projects/lsdb'
    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/'
    
    
    s = '~/dev-mac/sickbeard'
    
    s = "/Users/donb/Downloads/Sick-Beard-master/sickbeard"
    
    s = "/Volumes/Brandywine/TV Series/White Collar/S04"

    s = u'/Users/donb/Downloads/incomplete'

    s = "."
    
    
    # import os
    # retvalue = os.system("touch ~/projects/lsdb")
    # print retvalue
    
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        # argv = ["--help"]+[s]
        argv = ["-rd 4"]
        argv += ["-v"]
        argv += ["-v"]
        argv += ["-f"]
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
    
    args = [os.path.abspath(os.path.expanduser(a)) for a in args]
    
    LOGLEVELS = (logging.FATAL, logging.WARNING, logging.INFO, logging.DEBUG)

    # Create logger
    logger = logging.getLogger('')
    logger.setLevel(logging.WARNING)
    # logger.addHandler(gui_log)

    logger.setLevel(LOGLEVELS[options.verbose_level-1])

    # logging.info('--------------------------------') # INFO:root:-------------------------------- (in red!)
    
    # print ', '.join([ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])
    # print reduce(lambda i,j:i+', '+j, [ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])

    if options.verbose_level >= 4:
        print "sys.argv:"
        print
        print "\n".join(["    "+x for x in sys.argv])
        print

    # display list of timezones
    if options.verbose_level >= 4:
        print_timezones("time_zones")
        
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
#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
    ~/projects/lsdb-master/lsdb.py
    
    Created by donb on 2013-01-22.
    Copyright (c) 2013 Don Brotemarkle. All rights reserved.
    
    This file defines the command "lsdb"
    
"""

#
#   repr of a file record is "vol0007 42884672 42884713 Wed 2013.02.20 18:02 EST  2 __init__.py"
#   with a possibility of outputing the path not just the filenamne

class MyError(Exception):
    def __init__(self, code, description=""):
        self.code = code
        self.description = description
    def __str__(self):
        return "%s (%d)" %  (self.description,  self.code)


# 
# Overwriting __new__() works if you want to modify the string on construction:
# 
# class caps(str):
#    def __new__(self, content):
#       return str.__new__(self, content.upper())
# But if you just want to add new methods, you don't even have to touch the constructor:
# 
# class text(str):
#    def duplicate(self):
#       return text(self + self)
#       
#       

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
from pprint import pprint


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

from files import sharedFM, MyError 

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

from files import databaseAndURLKeys, enumeratorURLKeys, \
                GetNSFileAttributesOfItem, GetURLResourceValuesForKeys, GetURLValues

# databaseAndURLKeys = [  ( 'file_name',            NSURLNameKey), 
#                         (  None,                  NSURLIsDirectoryKey), 
#                         (  None,                  NSURLVolumeURLKey), 
#                         (  None,                  NSURLLocalizedTypeDescriptionKey), 
#                         ( 'file_uti',             NSURLTypeIdentifierKey), 
#                         ( 'file_create_date',     NSURLCreationDateKey), 
#                         ( 'file_mod_date',        NSURLContentModificationDateKey), 
#                         (  None,                  NSURLParentDirectoryURLKey), 
#                         ( 'file_size',           'NSURLTotalFileSizeKey'),
#                         ( 'file_id',             'NSFileSystemFileNumber'),
#                         ( 'folder_id',           'NSFileSystemFolderNumber' ),
#                         (  None,                  NSURLIsVolumeKey)                        
#                     ]
# 

# enumeratorURLKeys = [t[1] for t in databaseAndURLKeys]

__version__ = "0.5"

global options  # the command-line argument parser options



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
    # get list of records contained in this directory
    # coming out of the database we decode utf8 to get unicode strings

    # current_folder_contents = [ dict(zip( ("vol_id", "folder_id", "file_name", "file_id") , rs )) for rs in current_folder_contents] 
    
    # don't need mod date for comparison, but do need it later to avoid modifying current version
    #       in liew of deletable versin.
    
    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "

    data = (vol_id, folder_id )

    current_folder_contents = execute_select_query(cnx, sql, data, 4)
    current_folder_contents = [  (i[0], i[1], i[2].decode('utf8'), i[3], str(i[4]))  for i in current_folder_contents] 

    # here's where we add to itemsToDelete
    
    if len(current_folder_contents) > 0:    # don't create an empty entry in 
        itemsToDelete[depth] |= set(current_folder_contents) 


def DoSomeUTIStuff():

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
        
        
        


# error handler for enumeratorAtURL
def errorHandler1(y,error):
    print "enumeratorAtURL error: %s (%d)" % (error.localizedDescription(), error.code())



def max_item_stack(item_stack):
    if len(item_stack.keys()) == 0:
        return None
    else:
        return max(item_stack.keys()) # +1

def s123(item_stack):
    return  ( max_item_stack(item_stack), "%s" % item_stack, "[%s][%s]" % (itemsToDelete_repr(itemsToDelete) , itemsToDelete_repr(itemsToDelete2)) )

def pop_item_stack(depth, item_stack, n=3):
    
    len_s = max_item_stack(item_stack)
    
    while len_s is not None and max(item_stack.keys())+1 > depth:
        
        if options.verbose_level >= n:
            # pop to [%d] from %d " % (depth , len(item_stack))
            print "\npop (%d)(%d):" % (depth, max(item_stack.keys()))  
            s_before = s123(item_stack)
    
        if len(itemsToDelete[len_s]) > 0:
            itemsToDelete2[len_s] |= itemsToDelete[len_s]
        
        del itemsToDelete[len_s]
        del item_stack[len_s]

        if options.verbose_level >= n:
            s_after = s123(item_stack)
            for n, v in enumerate(s_before):
                print "%32s ==> %-32s" % (v, s_after[n])
            print 

        len_s = max_item_stack(item_stack)



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
        s =    "%-14s %-8s %-7s %8d %8d %s %2d %s" % (l, itemsToDelete_repr(itemsToDelete), vol_id , folder_id, file_id, sa,  depth, filename) 
        print s
        # NSLog(s)

# 2013-02-17 00:14:36.649 python[18887:60b] existing              vol0001        1        2 Wed 2013.01.16 01:51 EST -4 Genie
#   repr() could look like:
# inserted(2,3) 8        vol0010 40014149 41291492 Thu 2013.03.07 11:51 EST  1 lsdb.py



def print_supervolume_list(l, sl, n):
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
    
    try:
        cursor.execute( update_sql % d)
        cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            if True or options.verbose_level >= verbose_level:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2-1]
                print "    "+repr(msg2)
        else:
            print 'execute_update_query:', err, err.errno , err.message , err.msg, err.sqlstate
    finally:
        cursor.close()

#   these codes should become part of the SQL create trigger script

kDuplicateKey = "existing"
kRecordInserted = "inserted"

class FilesInsertResult():

    def __init__(self, count_by_file_name=None, count_by_file_id=None, msg=None, l=None, verbose_level=3):
        
        self.count_by_file_name = count_by_file_name
        self.count_by_file_id = count_by_file_id
        self.msg = msg
        self.l = l

        assert( self.l in [ kDuplicateKey, kRecordInserted ])
        
        if (self.l, self.msg) ==  (kDuplicateKey, u'found existing vol_id'):
            self.m = "existing vol"  
        elif (self.l, self.msg) ==  (kRecordInserted, u'using provided vol_id after insert files'):
            if self.count_by_file_name == 1:
                self.m = "inserted"
            else:
                self.m = "updated"
        elif (self.l, self.msg) ==  (kRecordInserted, u'found existing vol_id after insert files'):
            self.m = "found vol"  
        elif (self.l, self.msg) ==  (kDuplicateKey, u'using provided vol_id'):
            self.m = "existing"
        elif (self.l, self.msg) ==  (kRecordInserted, u'created new vol_id after insert files') :
            self.m = "created vol" #  we created a new vol_id
        else:
            print "unusual! (status, message) after insert with is %r" % ( (self.l, self.msg ), )
            self.m = l

        if options.verbose_level >= verbose_level:     
            print self

    def __str__(self):

        if self.count_by_file_name == None or self.count_by_file_id == None:
            return "<None>"                                                                    
        
        if self.count_by_file_name == 1 and self.count_by_file_id == 1:
            return self.m                                                                    
        elif  self.count_by_file_name == self.count_by_file_id:  
            return "%s(%d)" % (self.m, self.count_by_file_name)                      
        else:                                                                   
            return "%s(%d,%d)" %  ( self.m, self.count_by_file_name, self.count_by_file_id )
        
    def is_existing(self):
        return self.l == kDuplicateKey
        
    def is_inserted(self):
        return self.l == kRecordInserted
    

def execute_insert_into_files(cnx, query, data, verbose_level=3):
    """ returns kDuplicateKey if duplicate key violation, kRecordInserted if not."""

    # the fields in the query argument are marked %s because a magic routine that we con't see is converting our data
    #       into mysql-compatible strings and then inserting them into our %s-es.  I think that
    #       using %s implies that we could've used %r or '%s', etc; so I recommend not using the magic
    #       conversion routine implied by using (query, data) but rather explicity formating the sql using 
    #       (query % data) and passing the resultant string to cursor.execute()

    try:

        cursor = cnx.cursor()      
        if options.verbose_level >= verbose_level:     
            try:
                print query % data
            except:
                print "unicode error?"
                
        cursor.execute(query, data) 

        cnx.commit()

        q = "select @count_by_file_name, @count_by_file_id, @msg" # via insert trigger on table "files"
        cursor.execute(q)
        trigger_vars = dict(zip(("count_by_file_name", "count_by_file_id", "msg"), [z for z in cursor][0]))

        # kRecordInserted means we didn't get a duplicate key error
        insert_result = FilesInsertResult(l=kRecordInserted, verbose_level=verbose_level, **trigger_vars)  

        q = "select @vol_id"
        cursor.execute(q)
        vol_id = [z for z in cursor][0][0]
        cnx.commit()
            
        return (vol_id , insert_result) 

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            
            if options.verbose_level >= verbose_level:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2-1]
                print "    "+repr(msg2)

            cnx.commit()

            #  only insert trigger table "files" sets these variables
 
            q = "select @count_by_file_name, @count_by_file_id , @msg"
            cursor.execute(q)
            trigger_vars = dict(zip(("count_by_file_name", "count_by_file_id", "msg"), [z for z in cursor][0]))

            #   kDuplicateKey means we got a duplicate key error
            insert_result = FilesInsertResult( l = kDuplicateKey, verbose_level=verbose_level, **trigger_vars) 

            q = "select @vol_id"
            cursor.execute(q)
            vol_id = [z for z in cursor][0][0]
            cnx.commit()
 
            return (vol_id , insert_result)

        elif err.errno == 1242 and err.sqlstate == '21000':
            # 
            print "Subquery returns more than 1 row"
            print query % data
            
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
            
        return None
        
    finally:
        
        cursor.close()


def execute_insert_query(cnx, query, data, verbose_level=3):
    """ general insert execute, only returns (l , vol_id). Use insert_into_files for files table inserts """

    # the fields in the query argument are marked %s because a magic routine that we con't see is converting our data
    #       into mysql-compatible strings and then inserting them into our %s-es.  I think that
    #       using %s implies that we could've used %r or '%s', etc; so I recommend not using the magic
    #       conversion routine implied by using (query, data) but rather explicity formating the sql using 
    #       (query % data) and passing the resultant string to cursor.execute()

    try:

        cursor = cnx.cursor() # buffered=True)      
        if options.verbose_level >= verbose_level:     
            try:
                print query % data
            except:
                print "unicode error?"
                
        cursor.execute(query, data)
        cnx.commit()

        q = "select @vol_id"
        cursor.execute(q)
        vol_id = [z for z in cursor][0][0]
        cnx.commit()
            
   
        return (kRecordInserted , vol_id ) 

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            
            if options.verbose_level >= verbose_level:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2-1]
                print "    "+repr(msg2)

            cnx.commit()

 

            q = "select @vol_id"
            cursor.execute(q)
            vol_id = [z for z in cursor][0][0]
            cnx.commit()
            
            return (kDuplicateKey , vol_id ) # duplicate key

        elif err.errno == 1242 and err.sqlstate == '21000':
            # 
            print "Subquery returns more than 1 row"
            print query % data
            
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
        return None
        
    finally:
        
        cursor.close()


def GetD(item_dict):
    """Convert from item_dict (Cocoa) forms to something that the database DBI can convert from"""

    d = {}
    for dk, fk in databaseAndURLKeys:
        if dk:
            if fk in [NSURLNameKey, NSURLTypeIdentifierKey]:
                d[dk] =  item_dict[fk].encode('utf8')
            elif dk in ['file_create_date', 'file_mod_date']:
                d[dk] =  str(item_dict[fk])[:-len(" +0000")] # "2011-07-02 21:02:54 +0000" => "2011-07-02 21:02:54"
            else:
                d[dk] =  item_dict[fk]

    print_dict_tall("insert data", d, 32, 4)

    return d



def insertItem(cnx, item_dict, vol_id,  depth, item_tally): 
    """returns vol_id, insert_result """

    d = GetD(item_dict)
    
    if vol_id == None:
        
        # these fields are marked %s because a magic routine that we con't see is converting our data
        #       into mysql-compatible strings and then inserting them into our %s-es.  I think that
        #       using %s implies that we could've used %r or '%s', etc; so I recommend not using the magic
        #       conversion routine implied by using (query, data) but rather explicity formating the sql using 
        #       (query % data) and passing the resultant string to cursor.execute()

        add_file_sql = ("insert into files "
                        " (folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                        " values ( %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, "
                        " %(file_mod_date)s, %(file_uti)s ) "
                        
                        );
                        
        (vol_id , insert_result) = execute_insert_into_files(cnx, add_file_sql, d, 4)
    
    else:  # vol_id != None:
        
        d['vol_id'] = vol_id
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                        "values ( %(vol_id)s, %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, %(file_mod_date)s, %(file_uti)s ) "
                        );
        
        (vol_id , insert_result) = execute_insert_into_files(cnx, add_file_sql, d, 4)
        
    # end if vol_id == None

    item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
        
    return vol_id, insert_result


def print_dict_tall(l, in_dict, left_col_width=24, verbose_level_threshold=1):
    if options.verbose_level >= verbose_level_threshold:
        print l + ":"
        print
        s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
        print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
        print


def get_superfolders_list(basepath):

    """return list of superfolders from volume down to container of basepath.  could be empty. """

    superfolder_list = []

    url =  NSURL.fileURLWithPath_(basepath)

    d1 = GetURLValues(url, enumeratorURLKeys)
    
    # base path could be a volume, then superfolder list is empty

    while not d1[NSURLIsVolumeKey]:        
        
        url = url.URLByDeletingLastPathComponent()                    # go "upwards"

        d1 = GetURLValues(url, enumeratorURLKeys)

        superfolder_list.insert(0,d1)


    print_supervolume_list("volume, superfolder(s)", superfolder_list, 4)
    
    return superfolder_list



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

        # d1.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

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
    
    print_supervolume_list("volume, superfolder(s) and basepath", superfolder_list, 4)
    
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
    # l = None
    for i, item_dict in enumerate(superfolder_list[0:-1]):

        depth = i - n + 1
        
        vol_id, insert_result = insertItem(cnx, item_dict, vol_id, depth, item_tally)  
        
        pr8(str(insert_result), vol_id, item_dict, depth)

    # basepath is processed in basepath enumerator (duh)
        
    if options.verbose_level >= 4 :
        print
            
    return vol_id
    # return vol_id, l
    
#===============================================================================
#       DoDBEnumerateBasepath
#===============================================================================

def DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack):
    
    # two steps: (1) handle basepath as singleton, and (2) enumerate all items below basepath
    #
    #   unless forced otherwise, each directory is compared to database version for modification date
    #    and if up-do-date then that directory's contents are not checked (assumed also up-to-date)
    #    (this doesn't catch a modification of a file in place: there is not directory modification in this case)


    #   Do the same things here for this directory as we would for any *inside* the enumeration (loop-and-a-half):

    basepath_url =  NSURL.fileURLWithPath_(basepath)
    basepath_dict = GetURLResourceValuesForKeys(basepath_url, enumeratorURLKeys)
    print_dict_tall("basepath dict", basepath_dict, 32, 4)

    depth = 0  # depth is defined as zero for basepath

    vol_id, insert_result = insertItem(cnx, basepath_dict, vol_id, depth, item_tally)  

    pr8(str(insert_result), vol_id, basepath_dict, depth)

    # if we are not a directory, then just exit gracefully
    if not basepath_dict[NSURLIsDirectoryKey]:
        pop_item_stack(depth, item_stack, 4)
        return vol_id
        
    #else (go aheard with enumeratoino f direcory)
    
    folder_id         = basepath_dict['NSFileSystemFileNumber']
    item_stack[depth] = 0  # placeholder, not actively searchable list

    if (not insert_result.is_existing()) or options.force_folder_scan:
        DoDBQueryFolder(cnx, "basepath", vol_id,  basepath_dict, item_stack, depth)
    
    
    enumeratorOptionKeys = 0L
    if not options.scan_packages:
        enumeratorOptionKeys = enumeratorOptionKeys | NSDirectoryEnumerationSkipsPackageDescendants
    if not options.scan_hidden_files:
        enumeratorOptionKeys = enumeratorOptionKeys | NSDirectoryEnumerationSkipsHiddenFiles
        
    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                            basepath_url, 
                            enumeratorURLKeys,
                            enumeratorOptionKeys,
                            errorHandler1 
                        )

    for url in enumerator2:

        item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

        # call enumerator2.skipDescendents() to skip all subdirectories

        print_dict_tall("item dict", item_dict, 32, 4)
        
        depth = enumerator2.level()

        #   pop_item_stack includes copying items to the list ItemsToDelete
        #    and could just to the deletion at "pop time".  currently we wait until the end.
        
        if max(item_stack.keys()) + 1 > depth:          # ie, if our current stack is larger than our current depth
            pop_item_stack(depth, item_stack, 4)

        if item_dict[NSURLIsDirectoryKey]:
            
            # is a directory
            
            # item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

            vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  

            # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))

            print_label = str(insert_result)

            # if the directory shows as modified get database contents for the directory
            #   DoDBQueryFolder marks this directory as "one worth following"

            if options.force_folder_scan or not insert_result.is_existing():
                DoDBQueryFolder(cnx, "directory", vol_id,  item_dict, item_stack, depth)
            else:
                item_stack[depth] = 0  # placeholder, not a real entry, won't ever match an item's folder_id
                
            # if we are looking at an existing directory (and not forced) (1) we don't need to query
            #  database but also (2) do we even need to run the rest of the filesystem enumerator
            #  past the database (they'll all exist, even if attribute data might have changed
            #       without the directory being updated)?

        else:
        
            # not a directory
            
            # don't have to do this if we are "within" an alrady checked existing directory? 
            #       ( or we have another "force" option to scan every file?  or is this force_scan?)
            
            # a file can be *updated* in the filesystem without updating the mod date of the directory?

            folder_id = item_dict['NSFileSystemFolderNumber']
            if not (depth-1 in item_stack and folder_id == item_stack[depth-1] ) :
                # print "skipped. assumed existing because immediate folder is not updated."
                # no insert_item but want to tally "skipped" also
                print_label = "skipped"
                item_tally[print_label].append(item_dict[NSURLNameKey].encode('utf8'))
            else:
                
                vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  
                
                # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
                print_label = str(insert_result)



        folder_id = item_dict['NSFileSystemFolderNumber']

        #
        #   Here's where we:
        #       (1)  check to see if we need to check: check if our current item is from a folder that
        #               we are keeping track of
        #       (2)  if we are even within a tracked folder, then we check if this particular item 
        #               is within the list obtained from the database when we "entered" this folder.
        #
        #       If the current item shows as haveing just been inserted then there is no need to check 
        #           to see if it is already in the database :-)
        #

        if depth-1 in item_stack and folder_id == item_stack[depth-1] \
                        and not insert_result.is_inserted():

            #   Remove a file item from the list of database contents.

            file_id         = item_dict['NSFileSystemFileNumber']
            filename        = item_dict[NSURLNameKey]
            file_mod_date        = item_dict[NSURLContentModificationDateKey]

            s = str(file_mod_date)
            file_mod_date = s[:-len(" +0000")]
            # print file_mod_date


            # these fields are those of the primary key of the table (minus file_mod_date).  define these somewhere/ retrieve them from the database at start?
            # rs = {'file_name': filename, 'vol_id': vol_id, 'folder_id': folder_id, 'file_id': file_id}
            rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
            # print rs , itemsToDelete[depth-1]
            if rs in itemsToDelete[depth-1]:
                itemsToDelete[depth-1].remove(rs)
            else:
                print "not in database list"
                print rs
                # print itemsToDelete[depth-1]
                print [( "%s (%d)" % x[2:4] )for x in itemsToDelete[depth-1] ] 
                # print "filesystem item \n%s not in database list [%d] %s\n" %  ( "%s (%d)" % (rs[2] , rs[3] ), depth-1, ", ".join([( "%s (%d)" % x[2:] )for x in itemsToDelete[depth-1] ] ))
        
        if print_label != "skipped":
            pr8(print_label, vol_id, item_dict, depth)
            

            
    #end for url in enumerator2

    #  final pop(s) back up to depth zero
    
    depth = 0  # depth is defined as zero for basepath
    pop_item_stack(depth, item_stack, 4)
    
    return vol_id

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
    
    # note: "on duplicate key update" of vol_total_capacity and vol_available_capacity.
    
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
                    
    (l , vol_id) = execute_insert_query(cnx, query, data, 3)
    
    pr4(l, vol_id, "", data[1], 3)
    

from relations.relation import relation

class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    # def _row_to_python(self, rowdata, desc=None):
    #     row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
    #     if row:
    #         r = relation( self.column_names , [row] )
    #         rows =  [row for row in r]
    #         return rows[0]
    #         # return dict(zip(self.column_names, row))
    #     return None

    def set_rel_name(self, in_rel_name=None):
        self._rel_name = in_rel_name

    def fetchall(self):
        # print "yea! fetchall", self.column_names
        if not self._have_unread_result():
            raise errors.InterfaceError("No result set to fetch from.")
        rel = relation( self.column_names, [] ,self._rel_name)
        (rows, eof) = self._connection.get_rows()
        self._rowcount = len(rows)

        for i in xrange(0,self.rowcount):
        #     res.append(self._row_to_python(rows[i]))
            rel.add( self._row_to_python(rows[i]) )
        self._handle_eof(eof)
        return rel
    

        
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

        # cur = cnx.cursor(cursor_class=MySQLCursorDict)
        # cur.execute("SELECT * FROM volume_uuids")
        # cur.set_rel_name(in_rel_name="volumes") # need name at relation init time
        # r = cur.fetchall()
        # 
        # # print cur.description
        # for z in r:
        #     print z
        # cur.close()

        # volumes(vol_id=u'vol0008', vol_uuid=u'1186DFD4-A592-3712-BA62-38B0D0FCD16C', vol_total_capacity=379580334080, vol_available_capacity=19091451904)
        
        #   initialize the item tally here
        #   (Using list as the default_factory, it is easy to group a sequence 
        #           of key-value pairs into a dictionary of lists)

        item_tally = defaultdict(list)
        item_stack = {}
        
        
        try:

            vol_id = DoDBInsertSuperfolders(cnx, superfolder_list, item_tally, item_stack)


       
            # our original path, basepath, is the last entry in the superfolder list

            basepath  = superfolder_list[-1]["NSURLPathKey"]

            # if superfolder_list[-1][NSURLIsDirectoryKey]:  
            vol_id = DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack)
            # else:
                # print "no enumeration for non-directory."

            # update volume info for the volume which is the [0]'th entry.
            # could do this just after DoDBInsertSuperfolders but if we are enumerating
            # from the top of a (new) volume then vol_id could still be None at that point.

            DoDBInsertVolumeData(cnx, vol_id, volume_url)
            

        except KeyboardInterrupt:
            print "KeyboardInterrupt (hey!)"
            pass
        
        #
        #   wrapup: format and print final tallys
        #

        print "\nfinal tallys:"
        
        item_tally_keys = [k for k, v in item_tally.items() if len(v) > 0 ]

        if item_tally_keys == ['existing']:  
            print "\n    All filesystem items are existing (%d)." % len(item_tally['existing'])
        else:            
            print
            for k, v in item_tally.items():
                if len(v) > 0:
                    if k in ["skipped", "existing"]:
                        print  "%15s (%2d)" % (k, len(v))  
                        # print  "%15s (%2d) %s" % (k, len(v), (", ".join(map(str,v))).decode('utf8') )  
                    else:
                        print  "%15s (%2d) %s" % (k, len(v), (", ".join(map(str,v))).decode('utf8') )  
                        # print  "%15s (%d) %r" % (k, len(v), map(str,v) )  
                    print
            
                
            # print "\n".join(["%15s (%d) %r" % (k, len(v), map(str,v) ) for k, v in item_tally.items() if len(v) > 0 ])

        if item_stack == {}:
            # print "    item_stack is empty."
            pass
        else:
            print "\n    item_stack is not empty!", item_stack
    
        # print
        # print "itemsToDelete:\n\n", itemsToDelete_repr(itemsToDelete), itemsToDelete.keys()
        # # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), list(v)) for k, v in itemsToDelete.items()  ])
        # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete.items()  ])
        # # print

        if len(itemsToDelete) == 0:
            pass
            # print "    itemsToDelete is empty."
        else:
            print "    itemsToDelete is not empty!:\n\n", itemsToDelete_repr(itemsToDelete), itemsToDelete.keys()
            print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete.items()  ])

        if len(itemsToDelete2) == 0:
            print "    itemsToDelete2 is empty."
        else:
            print "    itemsToDelete2 is [%s]:\n" % itemsToDelete_repr(itemsToDelete2) # , itemsToDelete2.keys()
            # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
            print '\n\n'.join([  "    %d: %s" % (k,  [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
            #  see "Just a little Zero" for more on  scheme to represent deletion.
            for k, v in itemsToDelete2.items(): # zz in itemsToDelete2:
                for rs in v:
                    d =   dict(zip( ("vol_id", "folder_id", "file_name", "file_id", "file_mod_date") , rs ))  
                    d["file_name"] = str(d["file_name"].decode('utf8'))
                    # print d
                    update_sql = ("update files "
                                    " set files.folder_id =  0 "
                                    " where files.vol_id  =  %(vol_id)r "
                                    " and files.folder_id =  %(folder_id)s "
                                    " and files.file_name =  %(file_name)r " 
                                    " and files.file_id =  '%(file_id)s' " 
                                    " and files.file_mod_date =  '%(file_mod_date)s' " 
                                    )  # file_name is already in utf8 form?    
                    print
                    execute_update_query(cnx, update_sql, d, 3)
    


        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    finally:
        cnx.close()
        
def final_tallys(item_tally, item_stack):
    """wrapup: format and print final tallys"""

    print "\nfinal tallys:"
    
    item_tally_keys = [k for k, v in item_tally.items() if len(v) > 0 ]

    if item_tally_keys == ['existing']:  
        print "\n    All filesystem items are existing (%d)." % len(item_tally['existing'])
    else:            
        print
        for k, v in item_tally.items():
            if len(v) > 0:
                if k in ["skipped", "existing"]:
                    print  "%15s (%2d)" % (k, len(v))  
                    # print  "%15s (%2d) %s" % (k, len(v), (", ".join(map(str,v))).decode('utf8') )  
                else:
                    print  "%15s (%2d) %s" % (k, len(v), (", ".join(map(str,v))).decode('utf8') )  
                    # print  "%15s (%d) %r" % (k, len(v), map(str,v) )  
                print
        
            
        # print "\n".join(["%15s (%d) %r" % (k, len(v), map(str,v) ) for k, v in item_tally.items() if len(v) > 0 ])

    if item_stack == {}:
        # print "    item_stack is empty."
        pass
    else:
        print "\n    item_stack is not empty!", item_stack

    # print
    # print "itemsToDelete:\n\n", itemsToDelete_repr(itemsToDelete), itemsToDelete.keys()
    # # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), list(v)) for k, v in itemsToDelete.items()  ])
    # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete.items()  ])
    # # print

    if len(itemsToDelete) == 0:
        pass
        # print "    itemsToDelete is empty."
    else:
        print "    itemsToDelete is not empty!:\n\n", itemsToDelete_repr(itemsToDelete), itemsToDelete.keys()
        print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete.items()  ])

    if len(itemsToDelete2) == 0:
        print "    itemsToDelete2 is empty."
    else:
        print "    itemsToDelete2 is [%s]:\n" % itemsToDelete_repr(itemsToDelete2) # , itemsToDelete2.keys()
        # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
        print '\n\n'.join([  "    %d: %s" % (k,  [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
        #  see "Just a little Zero" for more on  scheme to represent deletion.
        for k, v in itemsToDelete2.items(): # zz in itemsToDelete2:
            for rs in v:
                d =   dict(zip( ("vol_id", "folder_id", "file_name", "file_id", "file_mod_date") , rs ))  
                d["file_name"] = str(d["file_name"].decode('utf8'))
                # print d
                update_sql = ("update files "
                                " set files.folder_id =  0 "
                                " where files.vol_id  =  %(vol_id)r "
                                " and files.folder_id =  %(folder_id)s "
                                " and files.file_name =  %(file_name)r " 
                                " and files.file_id =  '%(file_id)s' " 
                                " and files.file_mod_date =  '%(file_mod_date)s' " 
                                )  # file_name is already in utf8 form?    
                print
                execute_update_query(cnx, update_sql, d, 3)




#===============================================================================
#   DoArgs
#===============================================================================

def DoArgs(options, args):

    #   this database connecting routine could be replaced with a more command-line or config file oriented
    #   And now some mysql connector stuff…
    #   DoStuff(cnx)                            # DoStuff™


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
    
        #   initialize the item tallys here (kind of a per-connection tally?)

        item_tally = defaultdict(list)
        item_stack = {}

        try:

            for basepath in args:
                
                DoDBBasepath(cnx, options, basepath, item_tally, item_stack)
        

            # # vol_id = DoDBInsertSuperfolders(cnx, superfolder_list, item_tally, item_stack)
            # # 
            # # 
            # #        
            # # # our original path, basepath, is the last entry in the superfolder list
            # # 
            # # basepath  = superfolder_list[-1]["NSURLPathKey"]
            # 
            # vol_id = DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack)

            # update volume info for the volume which is the [0]'th entry.
            # could do this just after DoDBInsertSuperfolders but if we are enumerating
            # from the top of a (new) volume then vol_id could still be None at that point.

            

        except KeyboardInterrupt:
            print "KeyboardInterrupt (hey!)"
            pass
        

        print "\nfinal tallys:" # and updates to "deleted" entries
        
        final_tallys(item_tally, item_stack)
        
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
#   DoDBBasepath
#===============================================================================
import pprint
from Foundation import NSDate

def DoDBBasepath(cnx, options, basepath, item_tally, item_stack):
    
        superfolder_list = get_superfolders_list(basepath)
        vol_id = None
        n = len(superfolder_list)
        for i, m in enumerate(superfolder_list):

            # to indicate this is a placeholder directory entry, not a fully listed directory 
            #   (which is what an up-to-date date would indicate)
            #   we are inserting a placeholder while there might also already be an actual one.
            #   will be cleaned up when the placeholder is not found to be in the database?
            
            m[NSURLContentModificationDateKey] = NSDate.distantPast() 

            # print "\n".join([ "%32s = %r" % (k,v ) for k,v in m.items()])
            # print

            depth = i - n + 1
        
            vol_id, insert_result = insertItem(cnx, m, vol_id, depth, item_tally)  
        
            pr8(str(insert_result), vol_id, m, depth)


        basepath_url =  NSURL.fileURLWithPath_(basepath)
        basepath_dict = GetURLResourceValuesForKeys(basepath_url, enumeratorURLKeys)


        depth = 0  # depth is defined as zero for basepath
        vol_id, insert_result = insertItem(cnx, basepath_dict, vol_id, depth, item_tally)  
        pr8(str(insert_result), vol_id, basepath_dict, depth)

        # if we are not a directory, then just skip the enumeration
        if basepath_dict[NSURLIsDirectoryKey]:
            # return vol_id
        
            folder_id         = basepath_dict['NSFileSystemFileNumber']
            item_stack[depth] = 0  # placeholder, not actively searchable list

            if (not insert_result.is_existing()) or options.force_folder_scan:
                DoDBQueryFolder(cnx, "basepath", vol_id,  basepath_dict, item_stack, depth)
    
    
            enumeratorOptionKeys = 0L
            if not options.scan_packages:
                enumeratorOptionKeys = enumeratorOptionKeys | NSDirectoryEnumerationSkipsPackageDescendants
            if not options.scan_hidden_files:
                enumeratorOptionKeys = enumeratorOptionKeys | NSDirectoryEnumerationSkipsHiddenFiles
        
            enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                    basepath_url, 
                                    enumeratorURLKeys,
                                    enumeratorOptionKeys,
                                    errorHandler1 
                                )

            for url in enumerator2:

                item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

                # call enumerator2.skipDescendents() to skip all subdirectories

                print_dict_tall("item dict", item_dict, 32, 4)
        
                depth = enumerator2.level()

                #   pop_item_stack includes copying items to the list ItemsToDelete
                #    and could just to the deletion at "pop time".  currently we wait until the end.
        
                if max(item_stack.keys()) + 1 > depth:          # ie, if our current stack is larger than our current depth
                    pop_item_stack(depth, item_stack, 4)

                if item_dict[NSURLIsDirectoryKey]:
            
                    # is a directory
            
                    # item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

                    vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  

                    # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))

                    print_label = str(insert_result)

                    # if the directory shows as modified get database contents for the directory
                    #   DoDBQueryFolder marks this directory as "one worth following"

                    if options.force_folder_scan or not insert_result.is_existing():
                        DoDBQueryFolder(cnx, "directory", vol_id,  item_dict, item_stack, depth)
                    else:
                        item_stack[depth] = 0  # placeholder, not a real entry, won't ever match an item's folder_id
                
                    # if we are looking at an existing directory (and not forced) (1) we don't need to query
                    #  database but also (2) do we even need to run the rest of the filesystem enumerator
                    #  past the database (they'll all exist, even if attribute data might have changed
                    #       without the directory being updated)?

                else:
        
                    # not a directory
            
                    # don't have to do this if we are "within" an alrady checked existing directory? 
                    #       ( or we have another "force" option to scan every file?  or is this force_scan?)
            
                    # a file can be *updated* in the filesystem without updating the mod date of the directory?

                    folder_id = item_dict['NSFileSystemFolderNumber']
                    if not (depth-1 in item_stack and folder_id == item_stack[depth-1] ) :
                        # print "skipped. assumed existing because immediate folder is not updated."
                        # no insert_item but want to tally "skipped" also
                        print_label = "skipped"
                        item_tally[print_label].append(item_dict[NSURLNameKey].encode('utf8'))
                    else:
                
                        vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  
                
                        # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
                        print_label = str(insert_result)



                folder_id = item_dict['NSFileSystemFolderNumber']

                #
                #   Here's where we:
                #       (1)  check to see if we need to check: check if our current item is from a folder that
                #               we are keeping track of
                #       (2)  if we are even within a tracked folder, then we check if this particular item 
                #               is within the list obtained from the database when we "entered" this folder.
                #
                #       If the current item shows as haveing just been inserted then there is no need to check 
                #           to see if it is already in the database :-)
                #

                if depth-1 in item_stack and folder_id == item_stack[depth-1] \
                                and not insert_result.is_inserted():

                    #   Remove a file item from the list of database contents.

                    file_id         = item_dict['NSFileSystemFileNumber']
                    filename        = item_dict[NSURLNameKey]
                    file_mod_date        = item_dict[NSURLContentModificationDateKey]

                    s = str(file_mod_date)
                    file_mod_date = s[:-len(" +0000")]
                    # print file_mod_date


                    # these fields are those of the primary key of the table (minus file_mod_date).  define these somewhere/ retrieve them from the database at start?
                    # rs = {'file_name': filename, 'vol_id': vol_id, 'folder_id': folder_id, 'file_id': file_id}
                    rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
                    # print rs , itemsToDelete[depth-1]
                    if rs in itemsToDelete[depth-1]:
                        itemsToDelete[depth-1].remove(rs)
                    else:
                        print "not in database list"
                        print rs
                        # print itemsToDelete[depth-1]
                        print [( "%s (%d)" % x[2:4] )for x in itemsToDelete[depth-1] ] 
                        # print "filesystem item \n%s not in database list [%d] %s\n" %  ( "%s (%d)" % (rs[2] , rs[3] ), depth-1, ", ".join([( "%s (%d)" % x[2:] )for x in itemsToDelete[depth-1] ] ))
        
                if print_label != "skipped":
                    pr8(print_label, vol_id, item_dict, depth)
            

            
            #end for url in enumerator2

            #  final pop(s) back up to depth zero
    
            depth = 0  # depth is defined as zero for basepath
            pop_item_stack(depth, item_stack, 4)



        pop_item_stack(depth, item_stack, 4)

        volume_url = basepath_dict[NSURLVolumeURLKey]
        DoDBInsertVolumeData(cnx, vol_id, volume_url)

#===============================================================================
# main
#===============================================================================


def main():

    #
    #   some favorite testing files
    #

    s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"

    s = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s = "/Users/donb/projects/files/get_files_values.py"

    s = "/Users/donb/projects"
    s = "/Volumes/Brandywine/erin esurance/"

    s = "/Volumes/Taos"
    s = "/Volumes/Brandywine/erin esurance/"
    s1 = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s2 = "/Volumes/Taos/TV series/Tron Uprising/Season 01/Tron Uprising - 1x01 - The Renegade (1).mkv"

    
    
    s = u'/Volumes/Sapporo/TV Show/Winx Club/S01/Winx Club - 1x07 - Grounded (aka Friends in Need).avi'
    

    s = u'/Volumes/Ulysses/TV Shows/'

    s = "/"
    
    s = u"/Users/donb"
    
    s = u'/Volumes/Sacramento/Movies/The Dark Knight (2008) (720p).mkv'

    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"


    s = u'/Users/donb/projects/lsdb'
    
    s = '~/dev-mac/sickbeard'
    
    s = "/Users/donb/Downloads/Sick-Beard-master/sickbeard"
    
    s = "/Volumes/Brandywine/TV Series/White Collar/S04"

    s = u'/Users/donb/Downloads/incomplete'

    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/'

    s = "/Volumes/Brandywine/erin esurance/"


    s = "/Volumes/Ulysses/bittorrent/"


    
    
    
    s = "/Volumes/Chronos/TV Show"
    s = u"/Volumes/Dunharrow/iTunes Dunharrow/TV Shows/The No. 1 Ladies' Detective Agency"
    s = u"/Volumes/Romika/Movies/"


    s = "/Volumes/Ulysses/bittorrent"
    s = "."

    s = "/Volumes/Katie"
    s = u"/Volumes/Romika/Movies/Animation | Simulation | Warrior"

    s = "/Volumes/Romika/Aperture Libraries/Aperture Esquire.aplibrary"
    
    s = "/Volumes/Ulysses/TV Shows/Nikita/Nikita.S03E01.1080p.WEB-DL.DD5.1.H.264-KiNGS.mkv"
    s = "."
    
    s = "/Volumes/Romika/Aperture Libraries/Aperture Esquire.aplibrary/"
    
    # import os
    # retvalue = os.system("touch ~/projects/lsdb")
    # print retvalue
    
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        # argv = ["--help"]+[s]
        argv = ["-rd 4"]
        argv += ["-v"]
        argv += ["-v"]
        # argv += ["-v"]
        # argv += ["-a"]
        # argv += ["-p"]
        # argv += ["-f"] 
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
        help="increment verbose count (verbosity) by one. Normal operation is to output one status line per file. One -v option will give you information on what files are being skipped and slightly more information at the end.  default=%default", action="count" ) 

    parser.add_option("-q", "--quiet", 
        action="store_const", const=0, dest="verbose_level", default=1, 
           help="Normal operation is to output one status line per file, status being \"inserted\", \"existing\", etc."
           " This option will prevent any output to stdout, Significant errors are still output to stderr.") 

 # -v, --verbose               increase verbosity
 # -q, --quiet                 suppress non-error messages
# This option increases the amount of information you are given during the transfer. 
# By default, rsync works silently. A single -v will give you information about what 
# files are being transferred and a brief summary at the end. 
# Two -v options will give you information on what files are being skipped and slightly more information at the end. More than two -v options should only be used if you are debugging rsync.        
        
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
        
    parser.add_option("-p", "--scan-packages", dest="scan_packages", action = "store_true", 
        help="scan contents of packages. Normal operation does not check the contents of packages. default = %default", 
        default=False) 
        
    parser.add_option("-a", "--scan-hidden-files", dest="scan_hidden_files", action = "store_true", 
        help="Include directory entries whose names begin with a dot. Normal operation does not include hidden files. default = %default", 
        default=False) 
     # -a      Include directory entries whose names begin with a dot (.).        
        
    #
    #   set defaults and call parser
    #
                          
    parser.set_defaults( verbose_level=1,  depth_limit=1 )

    global options
    
    (options, args) = parser.parse_args(argv)
    
    # no args means do the current directory
    
    if args == []: args = ["."]
    
    args = [os.path.abspath(os.path.expanduser(a)) for a in args]
    # args = [os.path.abspath(os.path.expanduser(a.decode('utf8'))) for a in args]
    
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
        # print type(sys.argv[-1].decode('utf8')), sys.argv[-1].decode('utf8')
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
    
    DoArgs(options, args)

        
        
#   Calling main() from the interactive prompt (>>>). Really?  
#   This is a commandline utility; i'm never going to do that.
#
#   maybe.  for testing.  just sayin'

if __name__ == "__main__":
        main()
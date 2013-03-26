#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
    lsdb.py
    
    This file defines the command "lsdb"
    
    Created by donb on 2013-01-22.
    Copyright (c) 2013 Don Brotemarkle. All rights reserved.
    
"""

#
#   repr of a file record is "vol0007 42884672 42884713 Wed 2013.02.20 18:02 EST  2 __init__.py"
#   with a possibility of outputing the path not just the filenamne



import sys
import os

if sys.version_info < (2, 6):
    print "Sorry, python version %d.%d is required. This is version %d.%d." %  \
                                    (  2, 6, sys.version_info.major , sys.version_info.minor )
    sys.exit(1)

import logging
# import datetime
from collections import defaultdict


import mysql.connector
from mysql.connector import errorcode
# from pprint import pprint


# import objc


#   see dates module for list of timezones and formatters
from dates import dateFormatters, print_timezones

from files import sharedFM, MyError 

from relations.relation import relation

from Foundation import NSURL, NSLog, \
                            NSDirectoryEnumerationSkipsPackageDescendants , \
                            NSDirectoryEnumerationSkipsHiddenFiles, \
                            NSURLIsPackageKey

# some Common File System Resource Keys

from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey
                        
                        # NSURLAttributeModificationDateKey

#
#   This table is pretty much what this module is about.  combined with some directory enumeration…
#                        

from files import   GetURLValues # GetURLResourceValuesForKeys, GetNSFileAttributesOfItem

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


def d_lengths(in_dict):
    """return lengths of items at each depth, eg [17-1-0]  or  [0-17 1-1 2-0]  """
    return "-".join(["%d" % (len(v),) for k, v in in_dict.items() ])    
    

class ItemStackStuff(object):
    """docstring for ItemStackStuff"""
    
    def __init__(self , folderIDAtDepth={}, itemsAtDepth=defaultdict(set)):
        super(ItemStackStuff, self).__init__()
        self.folderIDAtDepth = folderIDAtDepth      # dictionary: keys: depth, values: (int) folder_ids 
        self.itemsAtDepth = itemsAtDepth            # dictionary: keys: depth, values: sets of ?? ; relation??
        self.folderContentsAtDepth = defaultdict(relation)  # almost.  needs to supply a heading at init time!  lambda?

    def max_folder_id(self):
        """returns None for empty, 0 for a stack holding key 0, 1 for 0,1, etc."""
        return None if len(self.folderIDAtDepth.keys()) == 0 else  max(self.folderIDAtDepth.keys())

    def stack_depth(self):
        """returns 0 for empty, 1 for a single level-0 stack, 2 for 0,1, etc."""
        return 0 if len(self.folderIDAtDepth.keys()) == 0 else 1+ max(self.folderIDAtDepth.keys())


    def display_stack(self):
        return  ( 
                # self.max_folder_id()+1,                                 #  1 ==> 0   
                self.stack_depth(),
                "%s" % self.folderIDAtDepth,                            #  {0: 40014149, 1: 41299565} ==> {0: 40014149} 
                "[%s][%s]" % (d_lengths(self.folderContentsAtDepth) , d_lengths(self.itemsAtDepth))  #  [31-0][] ==> [31][] 
                )
    def is_stack_larger_then_depth(self, depth):
        """          # ie, if our current stack is larger than our current depth"""
        return self.stack_depth()  > depth
        


    def pop_item_stack(self, depth, n=3):
    
        len_s = self.max_folder_id()
        
        assert len_s != None, "pop_item_stack: self.max_folder_id() is %r!" % self.max_folder_id()
    
        # use while because we could have popped more than one level
        #    (eg, end of level 3 is also end of level 2 and so the pop is to level 1)
        
        while self.stack_depth() > depth:
        
            if GPR.verbose_level >= n:
                s_before = self.display_stack()
    
            if len(self.folderContentsAtDepth[len_s]) > 0:
                self.itemsAtDepth[len_s] = relation (self.folderContentsAtDepth[len_s].heading)
                self.itemsAtDepth[len_s] |= self.folderContentsAtDepth[len_s]
        
            del self.folderContentsAtDepth[len_s]
            del self.folderIDAtDepth[len_s]

            if GPR.verbose_level >= n:
                s_after = self.display_stack()
                print
                for n, v in enumerate(s_before):
                    print "pop  %32s ==> %-32s" % (v, s_after[n])
                print 

            len_s = self.max_folder_id()


# global container for item stack stuff
ISS = ItemStackStuff()     

# global container for verbose_level, basically.  (soon to be more logging-like)
class PrintStuff(object):
    """docstring for PrintStuff"""
    
    def __init__(self, verbose_level=3):
        super(PrintStuff, self).__init__()
        self.verbose_level = verbose_level

    def print_dict(self, l, in_dict, left_col_width=24, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
            print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
            print
    
    def print_it(self, s, verbose_level_threshold):
        if self.verbose_level >= verbose_level_threshold:     
            try:
                print s
            except UnicodeDecodeError as e:
                print  repr(e[1])
                # print u"UnicodeDecodeError", repr(e[1])

    def print_superfolders_list(self, l, sl, verbose_level_threshold):
        if self.verbose_level >= verbose_level_threshold:     
            print l + ":\n"
            l = [ (d["NSURLPathKey"], 
                    "is a volume" if d[NSURLIsVolumeKey] else "is not a volume", 
                        d['NSFileSystemFolderNumber']) for d in sl]
            s =    [ "    %8d  %-16s %s" % (fid,v ,   p) for ( p, v, fid) in l ]
            print "\n".join(s)
            print
    
    def pr4(self, l, v, d, p, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            print "%-10s %-8s %27s %s" % (l, v , d,  p) 

    def pr5(self, l, v, fid, d, p, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            s =    "%-10s %-8s %27s %s" % (l, v , d,  p) 
            s =    "%-10s %-8s %8d %s %s" % (l, v , fid, d,  p)   # not fixed 27 but varies with width of third string.
            print s


    def pr6(self, l, v, folder_id, file_id, d, p, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            s =    "%-10s %-8s %7d %7d %s %s" % (l, v , folder_id, file_id, d,  p) 
            print s

    def pr8(self, l, vol_id, item_dict, depth, verbose_level_threshold=1):

        file_mod_date    = item_dict[NSURLContentModificationDateKey]

        sa =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)  # needs a real NSDate here?

        # pathname         = item_dict["NSURLPathKey"]
        folder_id        = item_dict['NSFileSystemFolderNumber']
        filename         = item_dict[NSURLNameKey]
        file_id          = item_dict['NSFileSystemFileNumber']

        if self.verbose_level >= verbose_level_threshold:
            s = "%-14s %-8s %-7s %8d %8d %s %2d %s" % \
                    (l, d_lengths(ISS.folderContentsAtDepth), vol_id , folder_id, file_id, sa,  depth, filename) 
            print s
        
    def pr8p(self, l, vol_id, item_dict, depth, verbose_level_threshold=1):
        """longest version prints full pathname"""

        file_mod_date    = item_dict[NSURLContentModificationDateKey]

        sa =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)  # needs a real NSDate here?

        pathname         = item_dict["NSURLPathKey"]
        folder_id        = item_dict['NSFileSystemFolderNumber']
        # filename         = item_dict[NSURLNameKey]
        file_id          = item_dict['NSFileSystemFileNumber']

        if self.verbose_level >= verbose_level_threshold:
            s = "%-14s %-8s %-7s %8d %8d %s %2d %s" % \
                    (l, d_lengths(ISS.folderContentsAtDepth), vol_id , folder_id, file_id, sa,  depth, pathname) 
            print s
        
    def pr7z(self,  item_dict,   verbose_level_threshold=1):
        """0-0      vol0006     5651     6227 Wed 2013.03.20 13:29 EDT  1 <filename>"""
        vol_id          = item_dict['vol_id']
        depth           = item_dict['depth']
        file_mod_date    = item_dict[NSURLContentModificationDateKey]
        sa          =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)  # needs a real NSDate here?
        pathname         = item_dict["NSURLPathKey"]
        folder_id        = item_dict['NSFileSystemFolderNumber']
        filename         = item_dict[NSURLNameKey]

        if item_dict['NSURLIsDirectoryKey']:  filename += "/"

        file_id          = item_dict['NSFileSystemFileNumber']

        if self.verbose_level >= verbose_level_threshold:
            print "%-8s %-7s %8d %8d %s %2d %s" % \
                    (d_lengths(ISS.folderContentsAtDepth), vol_id , folder_id, file_id, sa,  depth, filename) 


    def print_attrs(self, in_obj, type_list=(str, bool, int), without_underscore=True, verbose_level_threshold=2):
        """tall print of attrs of object matching type, without underscore"""

        if self.verbose_level >= verbose_level_threshold:
            r = [ (a, getattr(in_obj,a)) for a in dir(in_obj) if isinstance( getattr(in_obj,a), type_list )  
                                                                and ( (a[0]!="_") or not without_underscore) ]    
            print "\n".join([ "%24s = %r" % s for s in r ])
            

GPR = PrintStuff()     


# def asdf(in_obj, left_col_width=12):
#     s = "%%%ss: %%r" % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
#     return "\n".join([ s % (a, getattr(in_obj,a)) for a in dir(in_obj) if a[0]!="_" and "URL" in a])

def execute_select_query(cnx, select_query, select_data, n=3):

    cursor = cnx.cursor()

    GPR.print_it(select_query % select_data, n)
    
    cursor.execute( select_query % select_data )
    
    zz = [z for z in cursor]
    
    cursor.close()

    return zz
    
def execute_update_query(cnx, update_sql, d, n=3):

    cursor = cnx.cursor()

    GPR.print_it(update_sql % d, n)
    
    try:
        cursor.execute( update_sql , d)
        cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            if True or GPR.verbose_level >= n:
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

        if GPR.verbose_level >= verbose_level:     
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
        
        GPR.print_it(query % data, verbose_level)


        "cursor._connection.charset is: " , cursor._connection.charset                
        
        # Returns an iterator when multi is True, otherwise None.            
        cursor.execute(query, data)         # (…, operation, params=None, multi=False)

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
            
            if GPR.verbose_level >= verbose_level:
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
        if GPR.verbose_level >= verbose_level:     
            try:
                print query % data
            except:
                print repr(query % data)                                # print "unicode error?"
                
                
        cursor.execute(query, data)
        cnx.commit()

        q = "select @vol_id"
        cursor.execute(q)
        vol_id = [z for z in cursor][0][0]
        cnx.commit()
            
   
        return (kRecordInserted , vol_id ) 

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            
            if GPR.verbose_level >= verbose_level:
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

    GPR.print_dict("insert data", d, 32, 4)

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
                        " %(file_mod_date)s, %(file_uti)s ) " )
                        
        (vol_id , insert_result) = execute_insert_into_files(cnx, add_file_sql, d, 4)
    
    else:  # vol_id != None:
        
        d['vol_id'] = vol_id
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                        "values "
                        "( %(vol_id)s, %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, "
                        "%(file_mod_date)s, %(file_uti)s ) "
                        )
        
        (vol_id , insert_result) = execute_insert_into_files(cnx, add_file_sql, d, 4)
        
    # end if vol_id == None

    item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
        
    return vol_id, insert_result




def get_superfolders_list(basepath):
    """return list of superfolders from volume down to container of basepath.  could be empty. """

    superfolders_list = []
    url =  NSURL.fileURLWithPath_(basepath)
    # d1 = GetURLValues(url, enumeratorURLKeys)

    while True: # not d1[NSURLIsVolumeKey]:            # base path could be a volume, then superfolder list is empty
        d1 = GetURLValues(url, enumeratorURLKeys)
        superfolders_list.insert(0,d1)
        if d1[NSURLIsVolumeKey]: 
            break
        url = url.URLByDeletingLastPathComponent()                    # go "upwards" to volume

    GPR.print_superfolders_list("volume, superfolder(s)", superfolders_list, 4)

    return superfolders_list




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

    GPR.print_dict("volume info", values, 36, 4)
    
    # note: "on duplicate key update" of vol_total_capacity and vol_available_capacity.
    
    query = ("insert into volume_uuids "
                    "(vol_id, vol_uuid, vol_total_capacity, vol_available_capacity) "
                    "values ( %s, %s, %s, %s ) " 
                    "on duplicate key update "
                    "vol_total_capacity = values(vol_total_capacity), "
                    "vol_available_capacity = values(vol_available_capacity)"
                    )
    
    data = (vol_id, str(dv['NSURLVolumeUUIDStringKey']) ,
                    int(dv['NSURLVolumeTotalCapacityKey']),
                    int(dv['NSURLVolumeAvailableCapacityKey']) )
                    
    (l , vol_id) = execute_insert_query(cnx, query, data, 4)
    
    GPR.pr4(l, vol_id, "", data[1], 4)
    


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

        desc = self.description

        for i in xrange(0,self.rowcount):
        #     res.append(self._row_to_python(rows[i]))
            r = list(rows[i])
            for idx,v in enumerate(rows[i]):
                if desc[idx][1] in [ 254 , 253]:
                    r[idx] = rows[i][idx].decode('utf8')  
                elif desc[idx][1] in [ 10, 12 ]:
                    # print r[idx] , str(rows[i][idx])  # date
                    r[idx] = str(rows[i][idx])  # date
                elif desc[idx][1] in [ 3 ]:
                    # print r[idx] , int(rows[i][idx])  # longint
                    r[idx] = int(rows[i][idx])  # date
                # else:
                #     print desc[idx][1]
                    
            rel.add( r ) # self._row_to_python(r) )
        self._handle_eof(eof)
        return rel
    

        

def final_tallys(item_tally):
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



    if len(ISS.folderContentsAtDepth) == 0:
        # pass
        print "    folderContentsAtDepth is empty."
    else:
        print "    folderContentsAtDepth is not empty!:\n\n", d_lengths(ISS.folderContentsAtDepth), ISS.folderContentsAtDepth.keys()
        print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in ISS.folderContentsAtDepth.items()  ])

    if len(ISS.itemsAtDepth) == 0:
        print "    itemsAtDepth is empty."
    else:
        print "    itemsAtDepth is [%s]:\n" % d_lengths(ISS.itemsAtDepth)
        # print '\n\n'.join([  "    %d: %s" % (k,  [b.file_name for b in v ] ) for k, v in itemsAtDepth.items()  ])
        print '\n\n'.join([  "    %d: %s" % (k,  [b[2] for b in v ] ) for k, v in ISS.itemsAtDepth.items()  ])

        

def DoDBItemsToDelete(cnx, itemsAtDepth):
    """see "Just a little Zero" for more on  scheme to represent deletion."""

    for k, v in itemsAtDepth.items():
        for rs in v:
            d =   dict(zip( ("vol_id", "folder_id", "file_name", "file_id", "file_mod_date") , rs ))  
            d["file_name"] = str(d["file_name"].encode('utf8'))
            d["vol_id"] = str(d["vol_id"].encode('utf8'))

# UnicodeEncodeError: 'ascii', u'actress\u2014Grace Park.approject', 7, 8, 'ordinal not in range(128)'

            # print d
            update_sql = ("update files "
                            " set files.folder_id =  0 "
                            " where files.vol_id  =  %(vol_id)s "
                            " and files.folder_id =  %(folder_id)s "
                            " and files.file_name =  %(file_name)s " 
                            " and files.file_id =  %(file_id)s " 
                            " and files.file_mod_date =  %(file_mod_date)s " 
                            )  # file_name is already in utf8 form?    

            print
            execute_update_query(cnx, update_sql , d, 3)
    



def select_for_vol_id(cnx, d):
    
    gd = GetD(d) 
    
    select_query = ( "select  vol_id  from files "
                        "where  folder_id = 1 "
                        "and file_name = %(file_name)s and file_create_date = %(file_create_date)s "
                        )

    cursor = cnx.cursor()
    GPR.print_it(select_query % gd, 4)
    cursor.execute( select_query , gd )    
    r = [z for z in cursor] 
    vol_id = r[0][0]
    cursor.close()
    
    return  vol_id

def do_db_file_exists(cnx, d, vol_id):
    
    gd = GetD(d) 
    
    select_query = ( "select 1 from files "
            "where vol_id = %(vol_id)s and folder_id = %(folder_id)s "
            "and file_name = %(file_name)s and file_mod_date = %(file_mod_date)s "
            )

    gd['vol_id'] = vol_id

    cursor = cnx.cursor()
    GPR.print_it(select_query % gd, 4)
    cursor.execute( select_query , gd )
    r = [z for z in cursor] 
    file_exists =  r == [(1,)] 
    cursor.close()
        
    return file_exists
    
def do_db_query_folder(cnx,  vol_id,  item_dict, folderIDAtDepth, depth):
        
    folder_id         = item_dict['NSFileSystemFileNumber']

    ISS.folderIDAtDepth[depth] = folder_id   # we are always just at one folder for any particular depth
    
    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "

    data = (vol_id, folder_id )


    cur = cnx.cursor(cursor_class=MySQLCursorDict)
    cur.execute( sql % data )
    cur.set_rel_name(in_rel_name="folder_contents") # need name at relation init time
    r = cur.fetchall()

    # relation( (u'vol_id',.. u'file_mod_date'), [  (u'vol0010',.. '2013-02-11 07:10:25'),..., 

    cur.close()
    
    # if len(r) > 0:
    ISS.folderContentsAtDepth[depth] = r 

    

def error_handler_for_enumerator(y,error):
    print "enumeratorAtURL error: %s (%d)" % (error.localizedDescription(), error.code())

        
#===============================================================================
#   do_fs_basepath generates filesystem entries
#   (1) begin with basepath
#   (2) isolate as much as possible the databawse access.  currently
#       a)  select_for_vol_id(cnx, volume_dict)
#       b)  is my current item equal to the one in the database, and
#       c)  what are the contents of this directory currently in the database
#===============================================================================

def do_fs_basepath(cnx, basepath, slist, vol_id, item_tally=defaultdict(list), force_folder_scan=False, 
                                                              scan_hidden_files=False, depth_limit=4, 
                                                              scan_packages=False): # , verbose_level=3, do_recursion=True ):
    # yield all but the last one, which is basepath
    
    n = len(slist)
    for i, superfolder_dict in enumerate(slist[:-1]):
        superfolder_dict['vol_id'] = vol_id
        superfolder_dict['depth'] = i+1-n
        yield superfolder_dict 

    #   Begin iteration of all files.  Start with the base path.
    
    basepath_dict = slist[-1]
    depth = 0  # depth is defined as zero for basepath
    # folderIDAtDepth = {}
    # print "ISS.folderIDAtDepth", ISS.folderIDAtDepth
    
    # three cases: (1) directory, not package or we're following packages.  do enumerate
    #              (2) directory and package and we're not following packages.  no enumerate
    #              (3) not directory.  no enumerate. same as case(2)

    basepath_url =  NSURL.fileURLWithPath_(basepath)

    # deep case is directory or follow package; don't need to know if this is a package? (packages are directories)
    p_dict, error =  basepath_url.resourceValuesForKeys_error_( [NSURLIsPackageKey] , None )
    item_is_package = p_dict[NSURLIsPackageKey]
    # print "item_is_package", item_is_package, "not item_is_package", not item_is_package, "scan_packages", scan_packages
    
    if basepath_dict[NSURLIsDirectoryKey] and ( not item_is_package or scan_packages):

        ISS.folderIDAtDepth[depth] = 0 
        file_exists = do_db_file_exists(cnx, basepath_dict, vol_id)

        if (not file_exists) or  force_folder_scan:
            do_db_query_folder(cnx,  vol_id,  basepath_dict, ISS.folderIDAtDepth, depth)

        basepath_dict['vol_id'] = vol_id
        basepath_dict['depth'] = depth
        yield basepath_dict
        
        # begin actual enumeration
        enumeratorOptionKeys = 0L
        if not scan_packages:
            enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
        if not scan_hidden_files:
            enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles

        enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                                                                basepath_url,   enumeratorURLKeys,
                                                                                enumeratorOptionKeys, error_handler_for_enumerator )
        for url in enumerator2:

            item_dict = GetURLValues(url, enumeratorURLKeys)        # GetURLResourceValuesForKeys
            depth = enumerator2.level()
            # print max(ISS.folderIDAtDepth.keys()), max(ISS.folderIDAtDepth.keys()) + 1,  depth, ISS.is_stack_larger_then_depth(depth)
            if ISS.is_stack_larger_then_depth(depth):
                ISS.pop_item_stack(depth, 4)

            # deep case is directory or follow package; don't need to know if this is a package? (packages are directories)
            p_dict, error =  url.resourceValuesForKeys_error_( [NSURLIsPackageKey] , None )
            item_is_package = p_dict[NSURLIsPackageKey]
            # print "item_is_package", item_is_package

            if item_dict[NSURLIsDirectoryKey] or (item_is_package and scan_packages):
                ISS.folderIDAtDepth[depth] = 0 
                file_exists = do_db_file_exists(cnx, item_dict, vol_id)
                if (not file_exists) or  force_folder_scan:
                    do_db_query_folder(cnx,   vol_id,  item_dict, ISS.folderIDAtDepth, depth)
            # else:
            #     pass


            folder_id = item_dict['NSFileSystemFolderNumber']
            if depth-1 in ISS.folderIDAtDepth and folder_id == ISS.folderIDAtDepth[depth-1] and (file_exists or  force_folder_scan):

                #   Remove a file item from the list of database contents.

                file_id         = item_dict['NSFileSystemFileNumber']
                filename        = item_dict[NSURLNameKey]
                file_mod_date   = item_dict[NSURLContentModificationDateKey]

                s = str(file_mod_date)
                file_mod_date = s[:-len(" +0000")]
                # print file_mod_date


                # these fields are those of the primary key of the table (minus file_mod_date).  
                # define these somewhere/ retrieve them from the database at start?
                # rs = {'file_name': filename, 'vol_id': vol_id, 'folder_id': folder_id, 'file_id': file_id}
                rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
                if ISS.folderContentsAtDepth.has_key(depth-1):
                
                    if rs in ISS.folderContentsAtDepth[depth-1]:
                        ISS.folderContentsAtDepth[depth-1].remove(rs)
                    else:
                        print ""
                        print "%r not in database list (%d)" % (rs, len(ISS.folderContentsAtDepth[depth-1]))
                        zs =  ISS.folderContentsAtDepth[depth-1].tuple_d(*rs)
                        # print "zs in ISS.folderContentsAtDepth[depth-1]", zs in ISS.folderContentsAtDepth[depth-1]
                        # print  [ "%s %s"  % (r.file_name.encode('utf8'), r.file_mod_date) for r in ISS.folderContentsAtDepth[depth-1]]
                        print
                else:
                    print 'folderContentsAtDepth', ISS.folderContentsAtDepth.keys() , 'has no key', depth-1
                    

            item_dict['vol_id'] = vol_id
            item_dict['depth'] = depth
            yield item_dict

        # end enumerator
            

            
    else:   
        # didn't enumerate
        basepath_dict['vol_id'] = vol_id
        basepath_dict['depth'] = depth
        # GPR.pr7z( basepath_dict)
        # gd = GetD(basepath_dict)    # the basepath
        #useful friendly reminder
        if basepath_dict[NSURLIsDirectoryKey] and item_is_package and not scan_packages:
            GPR.print_it("\nbasepath is a directory and a package but we're not scanning packages.\n", 2)

        yield basepath_dict            


    return

    
    # sys.exit()    
        


def do_lsdb(args, options):
    """do_lsdb is the high-level, self-contained routine most like the command-line invocation"""

    config = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'files',
        'buffered': True
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
            
    GPR.print_attrs(cnx, verbose_level_threshold=2) # , without_underscore=False

    sys.exit()


    item_tally = defaultdict(list)  # initialize the item tallys here (kind of a per-connection tally?)
  

    try:
        basepath = args[0] # "/Users/donb/projects/lsdb-master"

        print "\nbasepath:", basepath, "\n"

        slist = get_superfolders_list(basepath)

        vol_id = select_for_vol_id(cnx, slist[0])  # slist[0] is volume
    
        # do_fs_basepath is a generator

        for fs_dict in do_fs_basepath(cnx, basepath , slist, vol_id, force_folder_scan=True, 
                                                      scan_packages=options.scan_packages):
            GPR.pr7z( fs_dict )

        # do final stuff at end of generator
        
        depth = 0
        ISS.pop_item_stack(depth, 2)
        if ISS.folderIDAtDepth != {}:
            print "\n    folderIDAtDepth is not empty!", ISS.folderIDAtDepth

    except MyError, err:
        print err.description
    except KeyboardInterrupt:
        print "KeyboardInterrupt (hey!)"

    final_tallys(item_tally) # , folderIDAtDepth)

    if len(ISS.itemsAtDepth) != 0:
        DoDBItemsToDelete(cnx, ISS.itemsAtDepth)
        
    cnx.close()



#===============================================================================
# main
#===============================================================================

def main():

    #   some favorite testing files


    s = "/Users/donb/projects"
    s = "/Volumes/Brandywine/erin esurance/"

    s = "/Volumes/Taos"
    s = "/Volumes/Brandywine/erin esurance/"


    
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
    
    s = u"/Volumes/Romika/Movies/"


    s = "."

    s = "/Volumes/Katie"

    
    

    
    s = u"/Volumes/Dunharrow/iTunes Dunharrow/TV Shows/The No. 1 Ladies' Detective Agency"
    
    s = u"/Volumes/Romika/Movies/Animation | Simulation | Warrior"


    s = "/Volumes/Romika/Aperture Libraries/"

    s = "/Volumes/Ulysses/TV Shows/Nikita/Nikita.S03E01.1080p.WEB-DL.DD5.1.H.264-KiNGS.mkv"

    # s = "/Volumes/Romika/Aperture Libraries/Aperture Esquire.aplibrary"

    # test for "basepath is a directory and a package but we're not scanning packages."
    s = u"/Users/donb/Documents/Delete Imported Items on matahari?.rtfd"

    s = "."
    
    s = "/Volumes/Chronos/TV Show"
    s = "/Volumes/Ulysses/bittorrent"
    
    # s = "/Volumes/Taos/TV series/Tron Uprising/Season 01/Tron Uprising - 1x01 - The Renegade (1).mkv"
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        argv = []
        # argv = ["--help"]+[s]
        # argv = ["-rd 4"]
        argv += ["-v"]
        argv += ["-v"]
        # argv += ["-v"]
        # argv += ["-a"]
        # argv += ["-p"]
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

    # from optparse import OptionParser, OptionValueError

    from argparse import ArgumentParser
    parser = ArgumentParser(description="A very extensible IRC bot written in Python.")
    
    
    parser = OptionParser(usage='usage: %prog [options] [filename(s)] ',
                          version='%%prog %s' % __version__ )

    # --help ==>    Usage: get_files_values.py pathname [options] 
    # --version ==> get_files_values.py 0.6


    parser.add_option("-r", "--recursive",  dest="do_recursion",  action="store_const", const=True, 
        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,default=False )
    
                                                
    parser.add_option("-v", "--verbose", dest="verbose_level", 
        help="increment verbose count (verbosity) by one. "\
                "Normal operation is to output one status line per file. "\
                "One -v option will give you information on what files are being"\
                " skipped and slightly more information at the end.  default=%default", action="count" ) 

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
    
    if args == []: 
        args = ["."]
    
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

    GPR.print_dict("options (after optparsing)", options.__dict__, left_col_width=24, verbose_level_threshold=2)

    if options.verbose_level >= 2:
        print "args (after optparsing):"
        print
        if args == []:
            print [None]
        else:
            print "\n".join(["    "+x for x in args])
        print
        
    do_lsdb(args, options)

#===============================================================================
#   script
#===============================================================================
        
#   Calling main() from the interactive prompt (>>>). Really?  
#   This is a commandline utility; i'm never going to do that.
#
#   maybe.  for testing.  just sayin'

if __name__ == "__main__":
    main()
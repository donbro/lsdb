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
from pprint import pprint


# import objc


#   see dates module for list of timezones and formatters
from dates import dateFormatters, print_timezones

from files import sharedFM, MyError 

from relations.relation import relation

from Foundation import NSURL, NSLog, \
                            NSDirectoryEnumerationSkipsPackageDescendants , \
                            NSDirectoryEnumerationSkipsHiddenFiles
                            # NSURLIsPackageKey

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

from files import   GetURLValues, is_item_a_package

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
    return "[%s]" % "-".join(["%d" % (len(v),) for k, v in in_dict.items() ])    
    

from relations.relation_dict import relation_dict

RS1_db_rels = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   
RS2_ins = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   


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
    
    def print_list(self, l, in_list, left_col_width=24, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s = "    %%%ss" % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
            print "\n".join([  s % x for x in in_list ])
            print

    def print_attrs(self, l, in_obj, type_list=(str, bool, int), without_underscore=True, verbose_level_threshold=2):
        """tall print of attrs of object matching type, without underscore"""

        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            r = [ (a, getattr(in_obj,a)) for a in dir(in_obj) if isinstance( getattr(in_obj,a), type_list )  
                                                                and ( (a[0]!="_") or not without_underscore) ]    
            print "\n".join([ "%24s = %r" % s for s in r ])
    
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
            s0 = dict([(k, RS1_db_rels[k]) for k in RS1_db_rels] )# avoid self-creation
            s1 =  '[%s]' % "-".join([ "%d"%(len(s0[k])) if k in s0 else "*" for k in stak]) # might *create* an entry if RS is a *default* dict (duh)
            
            # s1 =  '[%s]' % "-".join(["%d"%(len(RS1_db_rels[k])) for k in stak]) # might *create* an entry if RS is a *default* dict and k isn't already present in RS

            s2 = '[%s]' % "-".join(["%d"%(len(RS2_ins[k])) for k in RS2_ins])
            print "%-12s %-7s %8d %8d %s %2d %s" % \
                    (s1+'+'+s2, vol_id , folder_id, file_id, sa,  depth, filename) 

            

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
        print "item_tally.items()"
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



    # if len(ISS.folderContentsAtDepth) == 0:
    #     # pass
    #     print "    folderContentsAtDepth is empty."
    # else:
    #     print "    folderContentsAtDepth is not empty!:\n\n", d_lengths(ISS.folderContentsAtDepth), ISS.folderContentsAtDepth.keys()
    #     print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in ISS.folderContentsAtDepth.items()  ])

    nz = [rel for k, rel in RS1_db_rels.items() if len(rel) > 0]
    if nz == []:
        print "RS1_db_rels (No items to be deleted from database)", "\n"
    else:
        print "RS1_db_rels (to be deleted from database)", "\n", [rel for k, rel in RS1_db_rels.items() if len(rel) > 0] , "\n"
    
    # if len(ISS.itemsAtDepth) == 0:
    #     print "    itemsAtDepth is empty."
    # else:
    #     print "    itemsAtDepth is [%s]:\n" % d_lengths(ISS.itemsAtDepth)
    #     # print '\n\n'.join([  "    %d: %s" % (k,  [b.file_name for b in v ] ) for k, v in itemsAtDepth.items()  ])
    #     print '\n\n'.join([  "    %d: %s" % (k,  [b[2] for b in v ] ) for k, v in ISS.itemsAtDepth.items()  ])


    print "RS2 (files to be inserted into database)", "\n"
    nz2 = [rel for k, rel in RS2_ins.items() if len(rel) > 0]
    # print "\n".join(["%s" % t for t in r for r in nz1]) # [rel for k, rel in RS2_ins.items() if len(rel) > 0])
    for rel in nz2:
        for t in rel:
            # print t._asdict()
            print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)s %(file_name)s" % t._asdict()
    print "\n"

# def DoDBItemsToDelete(cnx, itemsAtDepth):
#     """see "Just a little Zero" for more on  scheme to represent deletion."""
#     for k, rel in itemsAtDepth.items():
#         do_db_delete_rel(cnx, rel)
        
def do_db_delete_rel(cnx, in_rel):
        
    for rs in in_rel:
        d =   dict(zip( ("vol_id", "folder_id", "file_name", "file_id", "file_mod_date") , rs ))  
        d["file_name"] = str(d["file_name"].encode('utf8'))
        d["vol_id"] = str(d["vol_id"].encode('utf8'))

        update_sql = ("update files "
                        " set files.folder_id =  0 "
                        " where files.vol_id  =      %(vol_id)s "
                        " and files.folder_id =      %(folder_id)s "
                        " and files.file_name =      %(file_name)s " 
                        " and files.file_id =        %(file_id)s " 
                        " and files.file_mod_date =  %(file_mod_date)s " 
                        ) 

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
    if r == []:
        vol_id = None
        print "vol_id is:", vol_id
    else:
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
    cursor.close()
    # print "do_db_file_exists", r
    
    if r == [(1,)]:
        return True
    elif r == []:
        return False
    else:
        print "do_db_file_exists", r
        return gronk
        
        
    # return file_exists
import copy
def do_db_query_folder(cnx,  vol_id,  item_dict, depth):
        
    folder_id         = item_dict['NSFileSystemFileNumber']

    
    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "
            
    data = (vol_id, folder_id )
    cur = cnx.cursor(cursor_class=MySQLCursorDict)
    cur.execute( sql % data )
    cur.set_rel_name(in_rel_name="files_del") # need name at relation init time
    r = cur.fetchall()
    # relation( (u'vol_id',.. u'file_mod_date'), [  (u'vol0010',.. '2013-02-11 07:10:25'),..., 
    cur.close()
    
    #ISS.push( depth, folder_id, r)
    # ISS.folderIDAtDepth[depth] = folder_id   # we are always just at one folder for any particular depth
    # ISS.folderContentsAtDepth[depth] = r 

    # this should be in relation.copy()(?)
    r2 = relation( r.heading, [row for row in r] ,r.name)
    # for row in r:
    #     r2.add( row )
    
    RS1_db_rels[ (depth, folder_id) ] =  r2
    # print "do_db_query_folder", "RS1_db_rels.keys()", RS1_db_rels.keys()
    

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

stak = []

def do_fs_basepath(cnx, basepath, slist, vol_id, item_tally=defaultdict(list), force_folder_scan=False, 
                                                                                  scan_hidden_files=False, 
                                                                                  depth_limit=4, 
                                                                                  scan_packages=False):
    """do_fs_basepath is a generator yielding an ordered sequence of (status, dictionary) pairs
      
      first yield the sequence of directories above the basepath, from top down.  could be empty.
      then yield basepath, then enumerate contents of basepath if it is a directory 
      or package and we want to scan packages
      """

    n = len(slist)
    for i, superfolder_dict in enumerate(slist[:-1]):   # last one is basepath
        superfolder_dict['vol_id'] = vol_id
        superfolder_dict['depth'] = i+1-n
        yield superfolder_dict 

    #     for url in enumerator2:
    basepath_url =  NSURL.fileURLWithPath_(basepath)
    
    item_dict = slist[-1]
    depth = 0                                                # print "(%d) %s" % (depth, item_dict['NSURLNameKey'])
    
    item_is_package = is_item_a_package(basepath_url)
    if item_dict[NSURLIsDirectoryKey] or (item_is_package and scan_packages):
        
        file_exists = do_db_file_exists(cnx, item_dict, vol_id)
        print "File is new or force_folder_scan." if ((not file_exists) or  force_folder_scan) else "File is up-do-date."
        if (not file_exists) or  force_folder_scan:
            do_db_query_folder(cnx,  vol_id,  item_dict, depth)

        i_am_a_folder_file_id         = item_dict['NSFileSystemFileNumber']            
        stak.append((depth, i_am_a_folder_file_id))

        item_dict['vol_id'] = vol_id
        item_dict['depth'] = depth
        yield item_dict
        
        # fall-through to do enumeration
        
    else:
    
        if item_dict[NSURLIsDirectoryKey] and item_is_package and not scan_packages:
            GPR.print_it("\nbasepath is a directory and a package but we're not scanning packages.\n", 2)
    
        item_dict['vol_id'] = vol_id
        item_dict['depth'] = depth

        yield item_dict
        return


    #   fall-through to do enumeration.
    #    do enumeration if we are a directory or we-are-a-package-and-we-want-package
    
    enumeratorOptionKeys = 0L
    if not scan_packages:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
    if not scan_hidden_files:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles

    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                        basepath_url,   enumeratorURLKeys, enumeratorOptionKeys, error_handler_for_enumerator 
                                        )
    for url in enumerator2:

        item_dict = GetURLValues(url, enumeratorURLKeys)
        depth = enumerator2.level()                             # print "(%d) %s" % (depth, item_dict['NSURLNameKey'])
            
        while len(stak) > depth:
            stak.pop()

        item_is_package = is_item_a_package(basepath_url)
        if item_dict[NSURLIsDirectoryKey] or (item_is_package and scan_packages):

            file_exists = do_db_file_exists(cnx, item_dict, vol_id)
            print "File is new or force_folder_scan." if ((not file_exists) or  force_folder_scan) else "File is up-do-date."
            if (not file_exists) or  force_folder_scan:
                do_db_query_folder(cnx,   vol_id,  item_dict, depth)

            i_am_a_folder_file_id = item_dict['NSFileSystemFileNumber']            
            stak.append((depth, i_am_a_folder_file_id))
                
        # check our folder ID against the stack of folder IDs
        folder_id = item_dict['NSFileSystemFolderNumber']

        print "Current item's folder " + ("*is*" if (depth-1, folder_id) in RS1_db_rels else "is not") + " in the list of database-contents directories to check against."

        if (depth-1, folder_id) in RS1_db_rels:
            file_id         = item_dict['NSFileSystemFileNumber']
            filename        = item_dict[NSURLNameKey]
            file_mod_date   = item_dict[NSURLContentModificationDateKey]
            s = str(file_mod_date)
            file_mod_date = s[:-len(" +0000")]
            rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
            
            try:
                
                RS1_db_rels[ (depth-1, folder_id) ] -= rs       # present, so no longer a "file to be deleted"
                
            except KeyError:
                RS2_ins[ (depth-1, folder_id) ] += rs       # in filesystem but not in database, hence a "file to be inserted"
                
        
 
        item_dict['vol_id'] = vol_id
        item_dict['depth'] = depth
        yield item_dict

    # end enumerator

    return
        


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
            
    GPR.print_attrs("mysql.connector", cnx, verbose_level_threshold=4) 

    # sys.exit()


    item_tally = defaultdict(list)  # initialize the item tallys here (kind of a per-connection tally?)
  

    try:
        
        for basepath in args:

            print "\nbasepath:"
            print
            print "    ", basepath
            print

            slist = get_superfolders_list(basepath)

            vol_id = select_for_vol_id(cnx, slist[0])  # slist[0] is volume
    
            # do_fs_basepath is a generator

            for fs_dict in do_fs_basepath(cnx, basepath , slist, vol_id, force_folder_scan=options.force_folder_scan, 
                                                          scan_packages=options.scan_packages):
                GPR.pr7z( fs_dict )

            # do final stuff at end of generator
        
            depth = 0

            # ISS.pop_item_stack(depth, 2)

            while len(stak) > depth:
                # stak_before = stak[:]
                stak.pop()
                # print "pop", stak_before, "==>", stak
            
            # if ISS.folderIDAtDepth != {}:
            #     print "\n    folderIDAtDepth is not empty!", ISS.folderIDAtDepth

    except MyError, err:
        print err.description
    except KeyboardInterrupt:
        print "KeyboardInterrupt (hey!)"

    final_tallys(item_tally) # , folderIDAtDepth)

    # if len(ISS.itemsAtDepth) != 0:
    #     DoDBItemsToDelete(cnx, ISS.itemsAtDepth)

    for k, rel in RS1_db_rels.items():      # RS1_db_rels is a dict of relations -- {(d,fid): relation(), .. }
        do_db_delete_rel(cnx, rel)
        
    cnx.close()



def do_parse_argv(argv):

    from argparse import ArgumentParser
    parser = ArgumentParser(description="filesystem, library files and database multitool.")

    parser.add_argument("-r", "--recursive",  dest="do_recursion",  
                        action="store_const", const=True, 
                        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,
                        default=False )

    parser.add_argument("-v", "--verbose", 
                        action="count", dest="verbose_level", 
                        help="increment verbose count (verbosity) by one. "\
                        "Normal operation is to output one status line per file. "\
                        "One -v option will give you slightly more information on each file.  Two -v options "\
                        " shows all debugging info available.") 

    parser.add_argument("-q", "--quiet", 
                        action="store_const", 
                        const=0, dest="verbose_level", default=1, 
                        help="Normal operation is to output one status line per file, status being \"inserted\", \"existing\", etc."
                        " This option will prevent any output to stdout, Significant errors are still output to stderr.") 

    # def _depth_callback(option, opt_str, value, parser): # , cls):
    #     if value == "None" or value == "none":
    #         setattr(parser.values, option.dest, None)
    #     else:
    #         try:
    #             setattr(parser.values, option.dest, int(value))
    #         except:
    #             raise OptionValueError("%s value must be integer or None. %s: %r received."
    #                                % (option.dest, str(type(value)), value) )

    # ValueError: 'unknown action "callback"'

    # parser.add_argument("-d", "--depth-limit", "--depth", dest="depth_limit", action="callback" , 
    #     callback=_depth_callback,
    #     help="limit recusion DEPTH. using DEPTH = 0 means process the directory only.  DEPTH=None means no depth limit (use with caution). "
    #     "Recursion is implied when any depth-limit is specified. default is %default.",
    #      metavar="DEPTH", type="string") 


    parser.add_argument("-f", "--force-folder-scan", dest="force_folder_scan", action = "store_true", 
                        help="explicitly check contents of directories even if directory timestamp not newer than"
                        "database value.  Normal operation does not check the contents of a directory if its timestamp equals"
                        "that in the database.", 
                        default=False) 
        
    parser.add_argument("-p", "--scan-packages", dest="scan_packages", action = "store_true", 
        help="scan contents of packages. Normal operation does not check the contents of packages.", 
        default=False) 
        
    parser.add_argument("-a", "--scan-hidden-files", dest="scan_hidden_files", action = "store_true", 
        help="Include directory entries whose names begin with a dot. Normal operation does not include hidden files.", 
        default=False) 
    
    return parser.parse_known_args(argv) # (options, args)

#===============================================================================
# main
#===============================================================================

def main():

    #   some favorite testing files

    u'/Users/donb'
    u'/Users/donb/Documents/Delete Imported Items on matahari?.rtfd'
    u'/Users/donb/Downloads/incomplete'
    '/Users/donb/projects'
    '/Volumes/Brandywine/TV Series/White Collar/S04'
    '/Volumes/Brandywine/erin esurance'
    '/Volumes/Chronos/TV Show'
    u"/Volumes/Dunharrow/iTunes Dunharrow/TV Shows/The No. 1 Ladies' Detective Agency"
    '/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf'
    u'/Volumes/Sacramento/Movies/The Dark Knight (2008) (720p).mkv'
    '/Volumes/Taos'
    u'/Volumes/Ulysses/TV Shows'
    '/Users/donb/dev-mac/sickbeard'

    
    
    s = '/Volumes/Ulysses/TV Shows/Nikita/Nikita.S03E01.1080p.WEB-DL.DD5.1.H.264-KiNGS.mkv'

    # basepath is a directory and a package but we're not scanning packages.
    s = u"/Users/donb/Documents/Installing Evernote v. 4.6.2—Windows Seven.rtfd"
    
    s =     u'/Volumes/Sapporo/TV Show/Winx Club/S01/Winx Club - 1x07 - Grounded (aka Friends in Need).avi'

    
    
    s = u'/Users/donb/Documents/ do JavaScript "var listOfFunctions = [];.rtf'
    s = '/Volumes/Ulysses/bittorrent'
    s =     u'/Volumes/Ulysses/TV Shows/Lost Girl'
    s = '/Volumes/Ulysses/TV Shows/Nikita/'

    s = "."
    s = '/Volumes/Ulysses/TV Shows/Nikita/'

    
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
        # argv += ["-f"] 
        argv += [s]
    else:
        argv = sys.argv[1:]
    

    (options, args) = do_parse_argv(argv)


    
    # no args means do the current directory
    
    if args == []: 
        args = ["."]
    
    args = [os.path.abspath(os.path.expanduser(a)) for a in args]
    # args = [os.path.abspath(os.path.expanduser(a.decode('utf8'))) for a in args]
    
    # LOGLEVELS = (logging.FATAL, logging.WARNING, logging.INFO, logging.DEBUG)
    # 
    # # Create logger
    # logger = logging.getLogger('')
    # logger.setLevel(logging.WARNING)
    # # logger.addHandler(gui_log)
    # 
    # logger.setLevel(LOGLEVELS[options.verbose_level-1])
    # 
    # logging.info('--------------------------------') # INFO:root:-------------------------------- (in red!)
    

    GPR.print_list("sys.argv", sys.argv)

    # display list of timezones
    if options.verbose_level >= 4:
        print_timezones("time_zones")

    GPR.print_dict("options (after optparsing)", options.__dict__, left_col_width=24, verbose_level_threshold=2)

    GPR.print_list("args (after optparsing)", args)
        
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
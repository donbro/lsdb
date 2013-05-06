#!/Users/donb/projects/VENV/lsdb/bin/python
# encoding: utf-8

from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey

import mysql.connector
from mysql.connector import errorcode

from lsdbstuff.keystuff import databaseAndURLKeys, enumeratorURLKeys
from printstuff.printstuff import GPR
from relations.relation import relation

import os
MY_FULLNAME = os.path.normpath(os.path.abspath(__file__))   
PROG_DIR = os.path.dirname(MY_FULLNAME)                       
DATA_DIR = PROG_DIR                                          
CONFIG_FILE = os.path.join(DATA_DIR, "dbstuff.cfg") # /Users/donb/projects/lsdb-master/dbstuff/dbstuff.cfg

# buffered = False
# verbose_level = 2
# ssl_key = None
# passwd = None
# sql_mode = None
# db = None
# raise_on_warnings = False
# raw = False
# host = 127.0.0.1
# user = 
# ssl_ca = None
# collation = None
# connection_timeout = None
# password = 
# port = 3306
# autocommit = False
# ssl_cert = None
# use_unicode = True
# charset = utf8
# time_zone = None
# client_flags = 0
# dsn = None
# unix_socket = None
# get_warnings = False
# connect_timeout = None

import psycopg2
def db_connect_psycopg2():
    
    cnx = psycopg2.connect(database='files',  user='donb', host='localhost' )    
    GPR.print_attrs("psycopg2.connect", cnx, verbose_level_threshold=1)     # 4
    return cnx
    
import ConfigParser
def db_connect():
    """open and return mysql connector object"""
    default_dict = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'files',
        'buffered': True
    }

    config = ConfigParser.ConfigParser()
    config.readfp(open(CONFIG_FILE))
    config_dict = dict(config.items('dbstuff'))
    
    default_dict.update(config_dict)
    
    GPR.print_dict("db_connect(default_dict+config_dict)", default_dict, verbose_level_threshold=1) 
    
    # config.add_section('dbstuff')
    # for k,v in config_dict.items(): # self.__dict__.items():
    #     config.set('dbstuff', k, v)
    # with open(CONFIG_FILE, 'wb') as configfile:
    #     config.write(configfile)

    # GPR.print_dict("db_connect(default_dict)", default_dict, verbose_level_threshold=1) 

    try:
        cnx = mysql.connector.connect(**default_dict)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (default_dict['user'], default_dict['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % default_dict['database']
        else:
            print 'err:', err
            
    GPR.print_attrs("mysql.connector", cnx, verbose_level_threshold=4) 
    
    return cnx
    
import objc
def GetD(item_dict):
    """Convert from item_dict (Cocoa) forms to something that the database DBI can convert from"""

    d = {}
    for dk, fk in databaseAndURLKeys:
        if dk:
            if fk in [NSURLNameKey, NSURLTypeIdentifierKey]:
                d[dk] =  item_dict[fk].encode('utf8')
            elif dk in ['file_create_date', 'file_mod_date']:
                d[dk] =  str(item_dict[fk])[:-len(" +0000")] # "2011-07-02 21:02:54 +0000" => "2011-07-02 21:02:54"
            elif  type(item_dict[fk]) == objc._pythonify.OC_PythonLong:
                # print """"type(item_dict[fk]) = objc._pythonify.OC_PythonLong""", item_dict[fk], int(item_dict[fk]) 
                d[dk] = int(item_dict[fk])
            # elif 'objc._pythonify.OC_PythonLong' in str(type(item_dict[fk])):
            #     print """"nscfnumber" in str(type(item_dict[fk]):""", item_dict[fk], int(item_dict[fk]), objc._pythonify.OC_PythonLong
            #     d[dk] = int(item_dict[fk])
            else:
                # print type(item_dict[fk])                
                d[dk] =  item_dict[fk]

    GPR.print_dict("GetD result", d, 32, 4)

    return d
    


def db_select_vol_idz(cnx, d):
    
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
        # print "vol_id is:", vol_id
    else:
        vol_id = r[0][0] # could have multiple results
    cursor.close()
    
    return  vol_id


def db_file_exists(cnx, in_dict): # , vol_id):
         
    gd = GetD(in_dict) 
    gd['vol_id'] = in_dict['vol_id'].encode('utf8')
    
    
    select_query = ( "select 1 from files "
            "where vol_id = %(vol_id)r and folder_id = %(folder_id)s "
            "and file_name = %(file_name)r and file_mod_date = %(file_mod_date)r "
            )


            # mysql.connector.errors.ProgrammingError: 1064 (42000): 
            # You have an error in your SQL syntax; check the manual that corresponds 
            #  to your MySQL server version for the right syntax to use 
            #  near ''vol0003' and folder_id = 2 and 
            #  file_name = 'TV Show\xe2\x80\x94single' and file' at line 1
            
            
    cursor = cnx.cursor()
    GPR.print_it(select_query % gd, 4)
    cursor.execute( select_query % gd )
    r = [z for z in cursor] 
    cursor.close()
    
    if r == [(1,)]:
        return True
    elif r == []:
        return False
    else:
        print "db_file_exists", r
        raise TypeError , ("db_file_exists says %r" % r)

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
            raise mysql.connector.InterfaceError , "No result set to fetch from."
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
    

        


def db_query_folder(cnx,  item_dict):
    """get database contents of item as folder."""

    vol_id                  =       item_dict['vol_id'].encode('utf8')
    this_folder_id          =       item_dict['NSFileSystemFileNumber']
    
    
# in sql format "%r" is good because it provides quotes but will also insert u'vol0001'
# so either: str() the text (or utf8 encode it?) or format it like   '%s'  (but this is dumb quotes)

    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "
            
    data = (vol_id, this_folder_id )
    
    cur = cnx.cursor(cursor_class=MySQLCursorDict)

    GPR.print_it( sql % data, verbose_level_threshold=2)
    cur.execute( sql % data )
    cur.set_rel_name(in_rel_name="files_del") # need name at relation init time (ie, inside cursor fetch)
    r = cur.fetchall()
    cur.close()
    
    return r

import sqlparse    
def execute_update_query(cnx, update_sql, sql_dict, label='execute_update_query', verbose_level_threshold=3):

    cursor = cnx.cursor()

    s = sqlparse.format(update_sql % sql_dict, reindent=True, encoding='utf8')
    GPR.print_it2( label, s, verbose_level_threshold)
    
    try:
        cursor.execute( update_sql  %  sql_dict)
        cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            if True or GPR.verbose_level >= n:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2-1]
                print "    "+repr(msg2)
        else:
            GPR.print_it2( label , "%r" % map(str , (err, err.errno , err.message , err.msg, err.sqlstate)), 0) # always print errors
    # Warning: It seems that you are trying to print a plain string containing unicode characters
    finally:
        cursor.close()

def do_db_delete_rel(cnx, in_rel):
        
    for rs in in_rel:
        do_db_delete_tuple(cnx, rs)


def do_db_delete_tuplez(cnx, rs, n=3):
        
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

        # print update_sql % d

        execute_update_query(cnx, update_sql , d, verbose_level_threshold=n)


def db_insert_volume_data(cnx, vol_id, volume_url):
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

    GPR.print_dict("volume info", values, 36, 1)
    
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
                    
    (l , vol_id) = execute_insert_query(cnx, query, data, 1)
    
    GPR.pr4(l, vol_id, "", data[1], 1)
    

#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
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

from lsdb.keystuff import databaseAndURLKeys, enumeratorURLKeys
from printstuff.PrintStuff import GPR
from relations.relation import relation


def db_connect():
    """open and return mysql connector object"""
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

    GPR.print_dict("insert data", d, 32, 4)

    return d
    


def db_select_vol_id(cnx, d):
    
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


def db_file_exists(cnx, in_dict): # , vol_id):
    
    # {
    #     NSFileSystemFileNumber = 2;
    #     NSFileSystemFolderNumber = 1L;
    #     NSURLContentModificationDateKey = "2013-03-30 18:11:07 +0000";
    #     NSURLCreationDateKey = "2011-07-02 21:02:54 +0000";
    #     NSURLIsDirectoryKey = 1;
    #     NSURLIsPackageKey = 0;
    #     NSURLIsVolumeKey = 1;
    #     NSURLLocalizedTypeDescriptionKey = Volume;
    #     NSURLNameKey = Genie;
    #     NSURLPathKey = "/";
    #     NSURLTotalFileSizeKey = 0;
    #     NSURLTypeIdentifierKey = "public.volume";
    #     NSURLVolumeURLKey = "file://localhost/";
    #     depth = "-4";
    #     url = "file://localhost/";
    #     "vol_id" = vol0010;
    # }
     
    gd = GetD(in_dict) 
    gd['vol_id'] = in_dict['vol_id']
    
    
    select_query = ( "select 1 from files "
            "where vol_id = %(vol_id)r and folder_id = %(folder_id)s "
            "and file_name = %(file_name)r and file_mod_date = %(file_mod_date)r "
            )


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

    
    vol_id         = item_dict['vol_id']
    this_folder_id         = item_dict['NSFileSystemFileNumber']
    
    # print "db_query_folder", item_dict['NSURLNameKey'], "folder_id", this_folder_id

    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "
            
    data = (vol_id, this_folder_id )
    
    cur = cnx.cursor(cursor_class=MySQLCursorDict)
    # print sql % data
    cur.execute( sql % data )
    cur.set_rel_name(in_rel_name="files_del") # need name at relation init time (ie, inside cursor fetch)
    r = cur.fetchall()
    cur.close()
    # GPR.print_it(update_sql % d, n)
    
    # print "db_query_folder", r
    return r
    # RS1_db_rels[ (depth, folder_id) ] =  r
    
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


def do_db_delete_rel(cnx, in_rel):
        
    for rs in in_rel:
        do_db_delete_tuple(cnx, rs)


def do_db_delete_tuple(cnx, rs, n=3):
        
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

        execute_update_query(cnx, update_sql , d, n)

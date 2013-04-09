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


def db_file_exists(cnx, d, vol_id):
    
    gd = GetD(d) 
    
    select_query = ( "select 1 from files "
            "where vol_id = %(vol_id)r and folder_id = %(folder_id)s "
            "and file_name = %(file_name)r and file_mod_date = %(file_mod_date)r "
            )

    gd['vol_id'] = vol_id

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
    

        


def db_query_folder(cnx,  vol_id,  item_dict, depth):
        
    folder_id         = item_dict['NSFileSystemFileNumber']
    
    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "
            
    data = (vol_id, folder_id )
    cur = cnx.cursor(cursor_class=MySQLCursorDict)
    cur.execute( sql % data )
    cur.set_rel_name(in_rel_name="files_del") # need name at relation init time
    r = cur.fetchall()
    cur.close()
    # print "db_query_folder", r
    return r
    # RS1_db_rels[ (depth, folder_id) ] =  r
    

#!/Users/donb/projects/VENV/lsdb/bin/python
# encoding: utf-8

# script: dbstuff.files
# module dbstuff.files

# code specific to the app logic and to the domain-layer tables: volumes, files, etc.

import os, sys

MY_FULLNAME = os.path.normpath(os.path.abspath(__file__))   # my file is always the same no matter where I am being executed from?
PROG_DIR = os.path.dirname(MY_FULLNAME)                       
DATA_DIR = PROG_DIR                                          
CONFIG_FILE = os.path.join(DATA_DIR, "postgres.cfg") # /Users/donb/projects/lsdb-master/dbstuff/postgres.cfg

if __package__ == None:
    super_dirname = os.path.dirname(PROG_DIR) # but we want the *filesystem* location, not whatever is sys.path[0]
    print "executing from without a package"
    print "inserting path %r into sys.path" %  super_dirname # os.path.join(sys.path[0], '..')
    sys.path.insert(1,  super_dirname )    
    # now imports below can find superior directory
    print "script: %s.%s" % (os.path.basename(PROG_DIR), os.path.splitext(os.path.basename(__file__))[0])
    
else:
    print "package %s.%s" %( __package__ , os.path.splitext(os.path.basename(__file__))[0])

from dbstuff.postgres import  db_insert_update # db_connect, db_file_exists, db_execute, db_execute_sql,


def db_update_volume_uuids(cnx, vol_id, volume_uuid_dict, verbose_level_threshold=2):
    """write out the volumes information"""
    
    label = "update volume uuids"
                    
    query1 = ("insert into volume_uuids "
                    "(vol_id, vol_uuid, vol_total_capacity, vol_available_capacity) "
                    "values ( %r, %r, %s, %s ) "   )
    
    data1 = (   vol_id, 
                str(volume_uuid_dict['NSURLVolumeUUIDStringKey']) ,
                int(volume_uuid_dict['NSURLVolumeTotalCapacityKey']),
                int(volume_uuid_dict['NSURLVolumeAvailableCapacityKey']) )                    

    query2 = ("update volume_uuids "
                    " set vol_total_capacity = %s, vol_available_capacity = %s  " 
                    " where"
                    " vol_id = %r and vol_uuid = %r  "  )
    
    data2 = (   int(volume_uuid_dict['NSURLVolumeTotalCapacityKey']),
                int(volume_uuid_dict['NSURLVolumeAvailableCapacityKey']),
                vol_id, 
                str(volume_uuid_dict['NSURLVolumeUUIDStringKey'])  )

    insert_query = query1 % data1
    update_query = query2 % data2
    # s1 = sqlparse.format(query1 % data1, reindent=True, encoding='utf8')
    # s2 = sqlparse.format(query2 % data2, reindent=True, encoding='utf8')
    # GPR.print_it2( label, s2, 2)

    db_insert_update(cnx, insert_query, update_query,  label=label, verbose_level_threshold=verbose_level_threshold)

    # 
    # return vol_id

#!/Users/donb/projects/VENV/lsdb/bin/python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-05-22.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from dbstuff.postgres import db_connect, db_execute_sql

def main():

    cnx = db_connect()
    

    vol_id = 'vol0004'
    file_id =  85948    
    
    (vol_id, file_id) = ('vol0004' , 86182)
    
    sql = "select path_from_vol_id_file_id(%r,  %d )" % (vol_id, file_id)
    
    r = db_execute_sql(cnx, sql)
    
    print r[0]
    
    
#  path_from_vol_id_file_id is better when the node doesn't have an ultimate parent (volume)
#
#   path_from_vol_id_file_id returns:
#  
#   (None,)
#  
#   while path_from_ids returns:
#  
#   /Volumes/math/Algebra (Math Complete)/Algebraic Groups and Discontinuous Subgroups - A. Borel, G. Mostow.pdf
 
 
#     path, path_list = path_from_ids(cnx, vol_id  , file_id  )
#     
#     print path
    
    

def path_from_ids(cnx, vol_id, file_id):

    z = []
    while file_id > 1:
        # sql = "select vol_id, folder_id, file_name, file_id" \
        #       " from files where vol_id = %r and file_id = %d" % (vol_id, file_id)

        sql = "select   folder_id, file_name " \
              " from files where vol_id = %r and file_id = %d" % (vol_id, file_id)
    
    
        ( folder_id, file_name ) = db_execute_sql(cnx, sql, "hi", 3)[0]
        
        
        r = (vol_id, folder_id, file_name, file_id)

        z.insert(0,r)
            
        file_id = folder_id
    
        # ('vol0003', 274342L, 'salma hayek 2.mp4', 274385L)
    
    path = "/Volumes/" + "/".join(  [ t[2] for t in z ] )

    return    path, z

if __name__ == '__main__':
    main()


def insertItem(cnx, item_dict, vol_id,  item_tally): 
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


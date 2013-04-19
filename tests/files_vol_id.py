    
def files_vol_id(cnx, my_files_gen):
    """processor for to find and add vol_id to each item as it goes by"""
    
    vol_id = None
    for file_dict in my_files_gen:
        if vol_id == None:
            vol_id = db_select_vol_id(cnx, file_dict)
            GPR.print_it2("gen for files_vol_id, vol_id =%r" %  vol_id, 2)
        file_dict['vol_id'] = vol_id
        yield file_dict

global_dict_vol_id = None

def dict_vol_id(cnx, file_dict):
    """processor for to find and add vol_id to each item as it goes by"""
    global global_dict_vol_id
    if global_dict_vol_id == None:
        global_dict_vol_id = db_select_vol_id(cnx, file_dict)
        GPR.print_it2("gen for files_vol_id", "%r, vol_id =%r" %  (file_dict[NSURLNameKey], global_dict_vol_id), 2)
    file_dict['vol_id'] = global_dict_vol_id
    return global_dict_vol_id
    
    # yield file_dict

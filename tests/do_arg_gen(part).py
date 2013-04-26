#     print "hey", "done with do_arg_gen. my_stak is", my_stak


    return
    
    sys.exit()
    
    my_stak = mySubStak() # contains self.RS1, self.RS2
        
    fs_gen = partial(files_stak_gen, in_stak=my_stak)  # keyword, not positional parameter
    
    y_gen = partial(vol_id_gen, cnx)

    for fs_dict in  y_gen( fs_gen( x_gen ) ):    

        folder_id = fs_dict['NSFileSystemFolderNumber']
        file_id = fs_dict['NSFileSystemFileNumber']
        depth = fs_dict['depth']
        
        # something that pop might have popped up for us:
        if len(my_stak.RS3) > 0:
            print "len(my_stak.RS3)", len(my_stak.RS3)
            for (k,r) in my_stak.RS3.items():
                if len(r) == 0:
                    print "(popped directory %r is empty)" % (k,),
                else:
                    print "(popped directory %r is not empty (%d))" % (k, len(r),),
                    for rs in r:
                        print "pop", "delete", rs
                        # yield rs

                del my_stak.RS3[k]          
                print "RS3after del", my_stak.RS3
        
        
        # the contents of the directory
        #   when it is stored…
        #   is stored into a location (one down from here)
        #   that will be pointed to via a (depth, folder_id) key
        #   that doesn't exist yet / hasn't been *pushed* onto the stack yet.
        # so, store it there (depth + 1, current *file_id*) and wait until the next
        #   the current item becomes the directory to be entered  ( next item)
        
        # each directory, if not up_to_date, is scanned and its contents are stored *for the next iteration*
        #       the current item is not touched by this section, only RS1 is stored_into if this is indicated.
        #       since this section only affects *the next iteration* is is independent/parallel of the next
        #       section.
         
        if is_a_directory(fs_dict, options):
            print "(directory)",
            dir_is_up_to_date = not options.force_folder_scan and db_file_exists(cnx, fs_dict) 
            fs_dict['directory_is_up_to_date'] = dir_is_up_to_date                  
            if (dir_is_up_to_date or depth < 0 ):
                print "(depth < 0)" if depth < 0 else "(up_to_date)" ,
            else:
                print "(to_be_scanned)",
                
            if (not dir_is_up_to_date) and (depth >= 0):   # depth=0 might belong to a folder that will be scanned; (ie basepath might need to be scanned)
                print "(scanning)", 
                r = db_query_folder(cnx, fs_dict)
                print "len=%r" % (len(r),) ,
                # still want to store even if empty: this indicates that files that are/might be in this directory are to be looked at
                # if len(r)==0:
                #     print "(database shows empty directory. don't store.)",
                # else:
                print "(storing at)" , (depth+1, file_id) ,
                my_stak.RS1[ (depth+1, file_id)  ] =  r

                print "RS1", "%r" % (my_stak,),
                
            print #end-of-line


        # all items are checked/debited against the list of database contents.
        #  items which are not accounted for at the end of the directory in question (at pop) are deleted
        #   those that are present in filesystem but not in database.

        # print "(current item)",

        fs_dict['current_item_directory_is_being_checked'] =  (depth, folder_id) in my_stak.RS1
        if fs_dict['current_item_directory_is_being_checked']:
          
            print "(check against container directory %r)" % ((depth,folder_id ) ,),

            vol_id = fs_dict['vol_id']

            # for *comparison with database value* use unicode, for *insert* use utf8. (?)
            filename        = fs_dict[NSURLNameKey] # .encode('utf8')  
            file_mod_date   = fs_dict[NSURLContentModificationDateKey]
            s = str(file_mod_date)
            file_mod_date = s[:-len(" +0000")]
            rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)

            try:                
                my_stak.RS1[ (depth,folder_id ) ] -= rs       
                # print "(ignore)(already in database)" , fs_dict[NSURLNameKey].encode('utf8')
                continue
            except KeyError:
                to_be_inserted = True
                my_stak.RS2[ (depth,folder_id ) ] += rs       
                fs_dict['to_be_inserted'] = True
                fs_dict['sql_action'] = "insert"
                print "(insert)"
                yield fs_dict
                continue
                
        # else (directory is not being checked)
        
        # some special cases.  print CR before yield


        if depth <= 0:
            print "(depth <= 0)"   # these are yielded because we don't know anything about them
            yield fs_dict
            continue
            
        if is_a_directory(fs_dict, options) and not dir_is_up_to_date:

            # this case is accidental (because we found it dureing the unrelated check of a directory's contents) 
            #       but we yield it anyway.
            
            # could handle it at *pop* time, when the contents of the directory are finished being examined.
            
            fs_dict['sql_action'] = "update_directory"
            print "(update directory)"
            yield fs_dict
            continue
            

        filename_utf8        = fs_dict[NSURLNameKey].encode('utf8')  

        # print "(ignore)(container directory is up to date)" , filename_utf8
        continue

        #     
        # 
        # yield fs_dict


    #
    #   end gen
    #

    # final pop back up to depth=0
    print "hey", "done with do_arg_gen. my_stak is", my_stak
    

            

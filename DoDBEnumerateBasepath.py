    
#===============================================================================
#       DoDBEnumerateBasepath
#===============================================================================

def DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack):
    
    # two steps: (1) handle basepath as singleton, and (2) enumerate all items below basepath
    #
    #   unless forced otherwise, each directory is compared to database version for modification date
    #    and if up-do-date then that directory's contents are not checked (assumed also up-to-date)
    #    (this doesn't catch a modification of a file in place: there is not directory modification in this case)


    #   Do the same things here for this directory as we would for any *inside* the enumeration (loop-and-a-half):

    basepath_url =  NSURL.fileURLWithPath_(basepath)
    basepath_dict = GetURLResourceValuesForKeys(basepath_url, enumeratorURLKeys)
    print_dict_tall("basepath dict", basepath_dict, 32, 4)

    depth = 0  # depth is defined as zero for basepath

    vol_id, insert_result = insertItem(cnx, basepath_dict, vol_id, depth, item_tally)  

    pr8(str(insert_result), vol_id, basepath_dict, depth)

    # if we are not a directory, then just exit gracefully
    if not basepath_dict[NSURLIsDirectoryKey]:
        pop_item_stack(depth, item_stack, 4)
        return vol_id
        
    #else (go aheard with enumeratoino f direcory)
    
    folder_id         = basepath_dict['NSFileSystemFileNumber']
    item_stack[depth] = 0  # placeholder, not actively searchable list

    if (not insert_result.is_existing()) or options.force_folder_scan:
        DoDBQueryFolder(cnx, "basepath", vol_id,  basepath_dict, item_stack, depth)
    
    
    enumeratorOptionKeys = 0L
    if not options.scan_packages:
        enumeratorOptionKeys = enumeratorOptionKeys | NSDirectoryEnumerationSkipsPackageDescendants
    if not options.scan_hidden_files:
        enumeratorOptionKeys = enumeratorOptionKeys | NSDirectoryEnumerationSkipsHiddenFiles
        
    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                            basepath_url, 
                            enumeratorURLKeys,
                            enumeratorOptionKeys,
                            errorHandler1 
                        )

    for url in enumerator2:

        item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

        # call enumerator2.skipDescendents() to skip all subdirectories

        print_dict_tall("item dict", item_dict, 32, 4)
        
        depth = enumerator2.level()

        #   pop_item_stack includes copying items to the list folderContentsAtDepth
        #    and could just to the deletion at "pop time".  currently we wait until the end.
        
        if max(item_stack.keys()) + 1 > depth:          # ie, if our current stack is larger than our current depth
            pop_item_stack(depth, item_stack, 4)

        if item_dict[NSURLIsDirectoryKey]:
            
            # is a directory
            
            # item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

            vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  

            # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))

            print_label = str(insert_result)

            # if the directory shows as modified get database contents for the directory
            #   DoDBQueryFolder marks this directory as "one worth following"

            if options.force_folder_scan or not insert_result.is_existing():
                DoDBQueryFolder(cnx, "directory", vol_id,  item_dict, item_stack, depth)
            else:
                item_stack[depth] = 0  # placeholder, not a real entry, won't ever match an item's folder_id
                
            # if we are looking at an existing directory (and not forced) (1) we don't need to query
            #  database but also (2) do we even need to run the rest of the filesystem enumerator
            #  past the database (they'll all exist, even if attribute data might have changed
            #       without the directory being updated)?

        else:
        
            # not a directory
            
            # don't have to do this if we are "within" an alrady checked existing directory? 
            #       ( or we have another "force" option to scan every file?  or is this force_scan?)
            
            # a file can be *updated* in the filesystem without updating the mod date of the directory?

            folder_id = item_dict['NSFileSystemFolderNumber']
            if not (depth-1 in item_stack and folder_id == item_stack[depth-1] ) :
                # print "skipped. assumed existing because immediate folder is not updated."
                # no insert_item but want to tally "skipped" also
                print_label = "skipped"
                item_tally[print_label].append(item_dict[NSURLNameKey].encode('utf8'))
            else:
                
                vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  
                
                # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
                print_label = str(insert_result)



        folder_id = item_dict['NSFileSystemFolderNumber']

        #
        #   Here's where we:
        #       (1)  check to see if we need to check: check if our current item is from a folder that
        #               we are keeping track of
        #       (2)  if we are even within a tracked folder, then we check if this particular item 
        #               is within the list obtained from the database when we "entered" this folder.
        #
        #       If the current item shows as haveing just been inserted then there is no need to check 
        #           to see if it is already in the database :-)
        #

        if depth-1 in item_stack and folder_id == item_stack[depth-1] \
                        and not insert_result.is_inserted():

            #   Remove a file item from the list of database contents.

            file_id         = item_dict['NSFileSystemFileNumber']
            filename        = item_dict[NSURLNameKey]
            file_mod_date        = item_dict[NSURLContentModificationDateKey]

            s = str(file_mod_date)
            file_mod_date = s[:-len(" +0000")]
            # print file_mod_date


            # these fields are those of the primary key of the table (minus file_mod_date).  define these somewhere/ retrieve them from the database at start?
            # rs = {'file_name': filename, 'vol_id': vol_id, 'folder_id': folder_id, 'file_id': file_id}
            rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)
            # print rs , folderContentsAtDepth[depth-1]

            # soon to be a comparison between a tuple_d and the contents of a relation
            if rs in folderContentsAtDepth[depth-1]:
                folderContentsAtDepth[depth-1].remove(rs)  # do we have a remove?  we are a set!
            else:
                print "not in database list"
                print folderContentsAtDepth[depth-1].tuple_d      # specialized namedtuple class
                print rs
                # print folderContentsAtDepth[depth-1]
                print [( "%s (%d)" % x[2:4] )for x in folderContentsAtDepth[depth-1] ] 
                # print "filesystem item \n%s not in database list [%d] %s\n" %  ( "%s (%d)" % (rs[2] , rs[3] ), depth-1, ", ".join([( "%s (%d)" % x[2:] )for x in folderContentsAtDepth[depth-1] ] ))
        
        if print_label != "skipped":
            pr8(print_label, vol_id, item_dict, depth)
            

            
    #end for url in enumerator2

    #  final pop(s) back up to depth zero
    
    depth = 0  # depth is defined as zero for basepath
    pop_item_stack(depth, item_stack, 4)
    
    return vol_id
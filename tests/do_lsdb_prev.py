
#===============================================================================
#   do_lsdb is the high-level, self-contained routine most like the command-line invocation
#   do_cnx_basepath is lower-level, uses caller's cnx, takes keyword arguments, requires globals like GPR and Tallys
#===============================================================================


def do_lsdb_prev(args, options):
    """this routine is self-contained, like the command-line invocation.  """
    
    
    # global g_options 
    # g_options = in_options

    #   this database connecting routine could be replaced with a more command-line or config file oriented
    #   DoStuff(cnx)                            # DoStuff™

    config = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'files',
        'buffered': True
    }

    try:
        cnx = mysql.connector.connect(**config)

        item_tally = defaultdict(list)  # initialize the item tallys here (kind of a per-connection tally?)
  

        try:
            for basepath in args:
                try:
                    # needs to return the (vol_id, file_id) at least for each argument
                    (vol_id, item_dict, insert_result) = do_cnx_basepath(cnx, basepath, item_tally, 
                                                                        force_folder_scan=options.force_folder_scan, 
                                                                        scan_hidden_files=options.scan_hidden_files, 
                                                                        depth_limit=options.depth_limit, 
                                                                        scan_packages=options.scan_packages,  
                                                                        do_recursion=options.do_recursion,
                                                                        verbose_level=options.verbose_level )
                except MyError, err:
                    print err.description
                    
        except KeyboardInterrupt:
            print "KeyboardInterrupt (hey!)"
 
        final_tallys(item_tally) # , folderIDAtDepth)

        if len(itemsAtDepth) != 0:
            DoDBItemsToDelete(cnx, itemsAtDepth)
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    finally:
        cnx.close()
        
        
        
        

#===============================================================================
#   do_cnx_basepath
#===============================================================================
import pprint
from Foundation import NSDate

def do_cnx_basepath(cnx, basepath, item_tally=defaultdict(list), force_folder_scan=False, 
                      scan_hidden_files=False, depth_limit=4, scan_packages=False, verbose_level=3, do_recursion=True ):

        GPR.verbose_level = verbose_level
    
        #
        #   do superfolder(s)
        #
        
        superfolder_list = get_superfolders_list(basepath)
        vol_id = None
        n = len(superfolder_list)
        for i, superfolder_dict in enumerate(superfolder_list):

            # to indicate this is a placeholder directory entry, not a fully listed directory 
            #   (which is what an up-to-date date would indicate)
            #   we are inserting a placeholder while there might also already be an actual one.
            #   will be cleaned up when the placeholder is not found to be in the database?
            
            superfolder_dict[NSURLContentModificationDateKey] = NSDate.distantPast() 

            # dvpr
            depth = i - n + 1
            vol_id, insert_result = insertItem(cnx, superfolder_dict, vol_id, depth, item_tally)  
            GPR.pr8(str(insert_result), vol_id, superfolder_dict, depth)

        #
        #   do basepath
        #

        basepath_url =  NSURL.fileURLWithPath_(basepath)
        basepath_dict = GetURLResourceValuesForKeys(basepath_url, enumeratorURLKeys)

        folderIDAtDepth = {}

        # dvpr
        depth = 0  # depth is defined as zero for basepath
        vol_id, insert_result = insertItem(cnx, basepath_dict, vol_id, depth, item_tally)  
        GPR.pr8(str(insert_result), vol_id, basepath_dict, depth)

        #
        #   enumerate through files and directories beneath basepath
        #

        #  if we are a directory and not a package (and we don't want to do packages)

        # check to see if basepath is a package
        nsd1, error =  basepath_url.resourceValuesForKeys_error_( [NSURLIsPackageKey] , None )
        
        if not (basepath_dict[NSURLIsDirectoryKey] and (scan_packages or not nsd1[NSURLIsPackageKey] )):
            GPR.print_it("\nskipping basepath because, though it is a directory, it is also a package and we're not doing packages.\n", 3)
            item_dict = basepath_dict
            
        if basepath_dict[NSURLIsDirectoryKey] and (scan_packages or not nsd1[NSURLIsPackageKey] ):
            
            # finish up some housekeeping on basepath now that we know its a directory
            
            # folder stuff
            folder_id         = basepath_dict['NSFileSystemFileNumber']
            folderIDAtDepth[depth] = 0  # placeholder, not actively searchable list

            if (not insert_result.is_existing()) or options.force_folder_scan:
                DoDBQueryFolder(cnx, "basepath", vol_id,  basepath_dict, folderIDAtDepth, depth)

            # the basepath enumeration
            enumeratorOptionKeys = 0L
            if not scan_packages:
                enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
            if not options.scan_hidden_files:
                enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles
        
            enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                    basepath_url, 
                                    enumeratorURLKeys,
                                    enumeratorOptionKeys,
                                    errorHandler1 )

            for url in enumerator2:

                item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

                # call enumerator2.skipDescendents() to skip all subdirectories

                print_dict_tall("item dict", item_dict, 32, 4)
        
                depth = enumerator2.level()

                #   pop_item_stack includes copying items to the list folderContentsAtDepth
                #    and could just to the deletion at "pop time".  currently we wait until the end.
        
                if max(folderIDAtDepth.keys()) + 1 > depth:          # ie, if our current stack is larger than our current depth
                    pop_item_stack(depth, folderIDAtDepth, 4)

                if item_dict[NSURLIsDirectoryKey]:
            
                    # is a directory
            
                    # item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

                    vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  

                    # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))

                    print_label = str(insert_result)

                    # if the directory shows as modified get database contents for the directory
                    #   DoDBQueryFolder marks this directory as "one worth following"

                    # folder stuff
                    if options.force_folder_scan or not insert_result.is_existing():
                        DoDBQueryFolder(cnx, "directory", vol_id,  item_dict, folderIDAtDepth, depth)
                    else:
                        folderIDAtDepth[depth] = 0  # placeholder, not a real entry, won't ever match an item's folder_id
                
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
                    if not (depth-1 in folderIDAtDepth and folder_id == folderIDAtDepth[depth-1] ) :
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

                if depth-1 in folderIDAtDepth and folder_id == folderIDAtDepth[depth-1] \
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
                    if rs in folderContentsAtDepth[depth-1]:
                        folderContentsAtDepth[depth-1].remove(rs)
                    else:
                        print "not in database list"
                        print rs
                        zs =  folderContentsAtDepth[depth-1].tuple_d(*rs)
                        print "zs in folderContentsAtDepth[depth-1]", zs in folderContentsAtDepth[depth-1]
                        print folderContentsAtDepth[depth-1]
                        # print [( "%s (%d)" % x[2:4] )for x in folderContentsAtDepth[depth-1] ] 
                        # print "filesystem item \n%s not in database list [%d] %s\n" %  ( "%s (%d)" % (rs[2] , rs[3] ), depth-1, ", ".join([( "%s (%d)" % x[2:] )for x in folderContentsAtDepth[depth-1] ] ))
        
                if print_label != "skipped":
                    GPR.pr8(print_label, vol_id, item_dict, depth)
            

            
            #end for url in enumerator2

            #  final pop(s) back up to depth zero
    
            depth = 0  # depth is defined as zero for basepath


        pop_item_stack(depth, folderIDAtDepth, 4)

        
        if folderIDAtDepth != {}:
            print "\n    folderIDAtDepth is not empty!", folderIDAtDepth

        volume_url = basepath_dict[NSURLVolumeURLKey]
        DoDBInsertVolumeData(cnx, vol_id, volume_url)
        
        return (vol_id, item_dict, insert_result)  # should return list of all id pairs?, list of superfolders?
        return (vol_id, superfolder_list, list_of_results) #item_dict for each?




#===============================================================================
#   do_cnx_basepath is lower-level, uses caller's cnx, takes keyword arguments, requires globals like GPR and Tallys
#===============================================================================
        
        
        
def do_fs_enumeration(basepath_url, folderIDAtDepth, scan_packages, scan_hidden_files):
    print "def do_fs_enumeration(basepath_url):", basepath_url

    enumeratorOptionKeys = 0L
    if not scan_packages:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
    if not scan_hidden_files:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles

    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                                                                        basepath_url, 
                                                                                        enumeratorURLKeys,
                                                                                        enumeratorOptionKeys,
                                                                                        errorHandler1 )

    for url in enumerator2:
        print "url", url

        item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)
    
        depth = enumerator2.level()

        if max(folderIDAtDepth.keys()) + 1 > depth:          # ie, if our current stack is larger than our current depth
            pop_item_stack(depth, folderIDAtDepth, 2)

        # if item_dict[NSURLIsDirectoryKey]:                    # is a directory

        print_dict_tall("item_dict", item_dict, 32, 3)

        yield item_dict
    
def do_fs_enumerationz(basepath_url):

    # return "gronk"


    d = {"hey":"you"}
    yield d

    # the basepath enumeration
    enumeratorOptionKeys = 0L
    if not scan_packages:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
    if not scan_hidden_files:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles

    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                            basepath_url, 
                            enumeratorURLKeys,
                            enumeratorOptionKeys,
                            errorHandler1 )

    for url in enumerator2:

        item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)
    
        depth = enumerator2.level()

        #   pop_item_stack includes copying items to the list folderContentsAtDepth
        #    and could just to the deletion at "pop time".  currently we wait until the end.

        if max(folderIDAtDepth.keys()) + 1 > depth:          # ie, if our current stack is larger than our current depth
            pop_item_stack(depth, folderIDAtDepth, 2)


        if item_dict[NSURLIsDirectoryKey]:                    # is a directory

            # # item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories
            # 
            #
            #   use a simple select rather than an insert/duplicate key error
            #   to determine is_existing()
        
            select_query = ( "select 1 from files "
                    "where vol_id = %(vol_id)s and folder_id = %(folder_id)s "
                    "and file_name = %(file_name)s and file_mod_date = %(file_mod_date)s "
                    )

            gd = GetD(item_dict)
            gd['vol_id'] = vol_id

            cursor = cnx.cursor()
            GPR.print_it(select_query % gd, 4)
            cursor.execute( select_query , gd )
            r = [z for z in cursor] 
            file_exists =  r == [(1,)] 
            cursor.close()
        
            print "file_exists:", file_exists
        
            # vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  
            # 
            # # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
            # 
            # print_label = str(insert_result)
            # 
            # # if the directory shows as modified get database contents for the directory
            # #   do_db_query_folder marks this directory as "one worth following"

            # folder stuff
            if force_folder_scan or not file_exists: # insert_result.is_existing():
                do_db_query_folder(cnx,  vol_id,  item_dict, folderIDAtDepth, depth)
            else:
                folderIDAtDepth[depth] = 0  # placeholder, not a real entry, won't ever match an item's folder_id
    

        else:

            # not a directory

            # don't have to do this if we are "within" an alrady checked existing directory? 
            #       ( or we have another "force" option to scan every file?  or is this force_scan?)

            # a file can be *updated* in the filesystem without updating the mod date of the directory?

            folder_id = item_dict['NSFileSystemFolderNumber']
            if not (depth-1 in folderIDAtDepth and folder_id == folderIDAtDepth[depth-1] ) :
                # print "skipped. assumed existing because immediate folder is not updated."
                # no insert_item but want to tally "skipped" also
                print_label = "skipped"
                item_tally[print_label].append(item_dict[NSURLNameKey].encode('utf8'))
            else:
    
                vol_id, insert_result = insertItem(cnx, item_dict, vol_id,  depth, item_tally)  
    
                # item_tally[str(insert_result)].append(item_dict[NSURLNameKey].encode('utf8'))
                print_label = str(insert_result)



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

        folder_id = item_dict['NSFileSystemFolderNumber']
        if depth-1 in folderIDAtDepth and folder_id == folderIDAtDepth[depth-1] \
                        and file_exists:

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
            if rs in folderContentsAtDepth[depth-1]:
                folderContentsAtDepth[depth-1].remove(rs)
            else:
                print "not in database list"
                print rs
                zs =  folderContentsAtDepth[depth-1].tuple_d(*rs)
                print "zs in folderContentsAtDepth[depth-1]", zs in folderContentsAtDepth[depth-1]
                print folderContentsAtDepth[depth-1]
                # print [( "%s (%d)" % x[2:4] )for x in folderContentsAtDepth[depth-1] ] 
                # print "filesystem item \n%s not in database list [%d] %s\n" %  ( "%s (%d)" % (rs[2] , rs[3] ), depth-1, ", ".join([( "%s (%d)" % x[2:] )for x in folderContentsAtDepth[depth-1] ] ))

        # if print_label != "skipped":
        GPR.pr8("print_label", vol_id, item_dict, depth)
        # GPR.pr8(print_label, vol_id, item_dict, depth)


    
        yield GetD(item_dict)




    #end for url in enumerator2

    #  final pop(s) back up to depth zero

    depth = 0  # depth is defined as zero for basepath




def DoDBQueryFolder(cnx, l, vol_id,  item_dict, folderIDAtDepth, depth):

    #   for modified directories (or if force_folder_scan is True):
    #       (1) get contents from database and 
    #       (2) compare this to the current filesystem (iterator's) results for that directory

    #   Here we do (1): get and store the directory's folder_id at folderIDAtDepth[depth].  
    #   While iterating through the filesystem, check each new item's folder_id against folderIDAtDepth[depth - 1]

    #   this marks this folder as one that the incoming items shoudl be compared against.
    
    folder_id         = item_dict['NSFileSystemFileNumber']
    folderIDAtDepth[depth] = folder_id   # we are always just at one folder for any particular depth

    # the fields returned here are those of the primary key of the table (minus file_mod_date).  
    #   define these somewhere/ retrieve them from the database at start?
    # get list of records contained in this directory
    # coming out of the database we decode utf8 to get unicode strings

    # current_folder_contents = [ dict(zip( ("vol_id", "folder_id", "file_name", "file_id") , rs )) 
    #       for rs in current_folder_contents] 
    
    # don't need mod date for comparison, but do need it later to avoid modifying current version
    #       in liew of deletable versin.
    
    sql = "select vol_id, folder_id, file_name, file_id, file_mod_date from files "+\
            "where vol_id = %r and folder_id = %d "

    data = (vol_id, folder_id )

    # current_folder_contents = execute_select_query(cnx, sql, data, 4)
    
    cur = cnx.cursor(cursor_class=MySQLCursorDict)
    cur.execute( sql % data )
    cur.set_rel_name(in_rel_name="folder_contents") # need name at relation init time
    r = cur.fetchall()
    
    # print "DoDBQueryFolder", len(r)
    
    # print cur.description
    # for z in r:
    #     # print [(k, z[k]) for k in z._fields]
    #     print z
    cur.close()
    
    # current_folder_contents = [  (i[0], i[1], i[2].decode('utf8'), i[3], str(i[4]))  for i in current_folder_contents] 
    # print "current_folder_contents", current_folder_contents


    #   Set the folder contents at our current depth to the database's contents for this folder
    
    if len(r) > 0:
        folderContentsAtDepth[depth] = r 



# 2013-02-17 00:14:36.649 python[18887:60b] existing              vol0001        1        2 Wed 2013.01.16 01:51 EST -4 Genie
#   repr() could look like:
# inserted(2,3) 8        vol0010 40014149 41291492 Thu 2013.03.07 11:51 EST  1 lsdb.py

        
        
        

    # 
    #     if p_dict[NSURLIsPackageKey] and not scan_packages:
    #         # package and we're not following packages
    #         GPR.pr7l( vol_id, basepath_dict, depth)
    #         gd = GetD(basepath_dict)    # the basepath
    #         yield gd            
    #         GPR.print_it("\nnot iterating below basepath because—though it is a directory—it is also a package and we're not doing packages.\n", 3)
    #         return
    #     else:
    #         #directory, not package
    #         folderIDAtDepth[depth] = 0 
    #         file_exists = do_db_file_exists(cnx, basepath_dict, vol_id)
    #         print "file_exists:", file_exists
    # 
    #         if (not file_exists) or  force_folder_scan:
    #             do_db_query_folder(cnx, "basepath", vol_id,  basepath_dict, folderIDAtDepth, depth)
    # 
    # 
    #         GPR.pr7l( vol_id, basepath_dict, depth)
    #         gd = GetD(basepath_dict)    # the basepath
    #         yield gd            
    # 
    #         print "do_fs_enumeration(basepath_url):", basepath_url
    # 
    #         zz = do_fs_enumeration(basepath_url, folderIDAtDepth, scan_packages, scan_hidden_files)
    #         
    #         print "do_fs_enumeration", type(zz),  zz
    #         # gronk
    # 
    #         folderIDAtDepth = {}
    # 
    #         # dvpr
    #         # vol_id, insert_result = insertItem(cnx, basepath_dict, vol_id, depth, item_tally)  
    #         # GPR.pr8(str(insert_result), vol_id, basepath_dict, depth)
    # 
    # 
    #         ISS.pop_item_stack(depth, folderIDAtDepth, 4)
    # 
    # 
    #         if folderIDAtDepth != {}:
    #             print "\n    folderIDAtDepth is not empty!", folderIDAtDepth
    # 
    #         return
    # 
    # else:
    #     # not directory.  no enumerate
    #     GPR.pr7l( vol_id, basepath_dict, depth)
    #     gd = GetD(basepath_dict)    # the basepath
    #     yield gd            
    #     return
    # 
    # print "you are not here."        
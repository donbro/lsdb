
# 
# Overwriting __new__() works if you want to modify the string on construction:
# 
# class caps(str):
#    def __new__(self, content):
#       return str.__new__(self, content.upper())
# But if you just want to add new methods, you don't even have to touch the constructor:
# 
# class text(str):
#    def duplicate(self):
#       return text(self + self)
#       
#       



#===============================================================================
#       DoDBItems
#===============================================================================

def DoDBItems(superfolder_list, volume_url):
    
    #   And now some mysql connector stuff…

    config = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'files',
        'buffered': True
        # 'charset': "utf8",
        # 'use_unicode': True
        # 'raise_on_warnings': True
    }


    # have to discover vol_id which will then be valid for all files in this group
    
    try:
        
        cnx = mysql.connector.connect(**config)


        # volumes(vol_id=u'vol0008', vol_uuid=u'1186DFD4-A592-3712-BA62-38B0D0FCD16C', vol_total_capacity=379580334080, vol_available_capacity=19091451904)
        
        #   initialize the item tally here
        #   (Using list as the default_factory, it is easy to group a sequence 
        #           of key-value pairs into a dictionary of lists)

        item_tally = defaultdict(list)
        item_stack = {}
        
        
        try:

            vol_id = DoDBInsertSuperfolders(cnx, superfolder_list, item_tally, item_stack)


       
            # our original path, basepath, is the last entry in the superfolder list

            basepath  = superfolder_list[-1]["NSURLPathKey"]

            # if superfolder_list[-1][NSURLIsDirectoryKey]:  
            vol_id = DoDBEnumerateBasepath(cnx, basepath, vol_id, item_tally, item_stack)
            # else:
                # print "no enumeration for non-directory."

            # update volume info for the volume which is the [0]'th entry.
            # could do this just after DoDBInsertSuperfolders but if we are enumerating
            # from the top of a (new) volume then vol_id could still be None at that point.

            DoDBInsertVolumeData(cnx, vol_id, volume_url)
            

        except KeyboardInterrupt:
            print "KeyboardInterrupt (hey!)"
            pass
        
        #
        #   wrapup: format and print final tallys
        #

        print "\nfinal tallys:"
        
        item_tally_keys = [k for k, v in item_tally.items() if len(v) > 0 ]

        if item_tally_keys == ['existing']:  
            print "\n    All filesystem items are existing (%d)." % len(item_tally['existing'])
        else:            
            print
            for k, v in item_tally.items():
                if len(v) > 0:
                    if k in ["skipped", "existing"]:
                        print  "%15s (%2d)" % (k, len(v))  
                        # print  "%15s (%2d) %s" % (k, len(v), (", ".join(map(str,v))).decode('utf8') )  
                    else:
                        print  "%15s (%2d) %s" % (k, len(v), (", ".join(map(str,v))).decode('utf8') )  
                        # print  "%15s (%d) %r" % (k, len(v), map(str,v) )  
                    print
            
                
            # print "\n".join(["%15s (%d) %r" % (k, len(v), map(str,v) ) for k, v in item_tally.items() if len(v) > 0 ])

        if item_stack == {}:
            # print "    item_stack is empty."
            pass
        else:
            print "\n    item_stack is not empty!", item_stack
    

        if len(folderContentsAtDepth) == 0:
            pass
            # print "    folderContentsAtDepth is empty."
        else:
            print "    folderContentsAtDepth is not empty!:\n\n", dict_set_short(folderContentsAtDepth), folderContentsAtDepth.keys()
            print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in folderContentsAtDepth.items()  ])

        if len(itemsToDelete2) == 0:
            print "    itemsToDelete2 is empty."
        else:
            print "    itemsToDelete2 is [%s]:\n" % dict_set_short(itemsToDelete2) # , itemsToDelete2.keys()
            # print '\n\n'.join([  "%d: (%d) %s" % (k, len(v), [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
            print '\n\n'.join([  "    %d: %s" % (k,  [b[2] for b in v ] ) for k, v in itemsToDelete2.items()  ])
            #  see "Just a little Zero" for more on  scheme to represent deletion.
            for k, v in itemsToDelete2.items(): # zz in itemsToDelete2:
                for rs in v:
                    d =   dict(zip( ("vol_id", "folder_id", "file_name", "file_id", "file_mod_date") , rs ))  
                    d["file_name"] = str(d["file_name"].decode('utf8'))
                    # print d
                    update_sql = ("update files "
                                    " set files.folder_id =  0 "
                                    " where files.vol_id  =  %(vol_id)r "
                                    " and files.folder_id =  %(folder_id)s "
                                    " and files.file_name =  %(file_name)r " 
                                    " and files.file_id =  '%(file_id)s' " 
                                    " and files.file_mod_date =  '%(file_mod_date)s' " 
                                    )  # file_name is already in utf8 form?    
                    print
                    execute_update_query(cnx, update_sql, d, 3)
    


        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    finally:
        cnx.close()
        
        
        
        
def GetSuperfolderList(basepath):

    """Generate Superfolder list, including volume """
    
    #  path given on command line is "basepath"

    url =  NSURL.fileURLWithPath_(basepath)

    # loop-and-a-half here.  go "upwards" and break (and hold) on first volume (ie, where d1[NSURLIsVolumeKey] is true)
    #   Work upwards from given path to first path that indicates that it is indeed a volume (eg, "/Volumes/volume_name")
    # breaking before moving "up" from the final directory leaves variable "url" pointing to top (volume) directory.        

    superfolder_list = []

    while True:       
        
        d1 = GetURLResourceValuesForKeys(url, enumeratorURLKeys)

        # d1.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

        superfolder_list.insert(0,d1)
        
        if d1[NSURLIsVolumeKey]:         # break before moving "up"
            break

        url = url.URLByDeletingLastPathComponent()            
    
    # last iteration is the volume
    
    volume_url = url
    
    # go forwards (downwards) thorugh the list setting each items "folder number" to the file number of its container

    for n, d in enumerate(superfolder_list):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
        else:
            d.update({'NSFileSystemFolderNumber': superfolder_list[n-1]['NSFileSystemFileNumber'] })
    
    print_supervolume_list("volume, superfolder(s) and basepath", superfolder_list, 4)
    
    return superfolder_list, volume_url

        
        
#===============================================================================
#       DoDBInsertSuperfolders
#===============================================================================
    
def DoDBInsertSuperfolders(cnx, superfolder_list, item_tally): # , folderIDAtDepth): 
    
    #
    #   Insert superfolders into the database
    #   (discovering/creating the vol_id with first insert without vol_id)
    #
    #   we don't do basepath here, makes more sense to do it within the basepath enumeration.
    #
        
    vol_id = None
    n = len(superfolder_list)
    # l = None
    for i, item_dict in enumerate(superfolder_list[0:-1]):

        depth = i - n + 1
        
        vol_id, insert_result = insertItem(cnx, item_dict, vol_id, depth, item_tally)  
        
        pr8(str(insert_result), vol_id, item_dict, depth)

    # basepath is processed in basepath enumerator (duh)
        
    if g_options.verbose_level >= 4 :
        print
            
    return vol_id
    # return vol_id, l

        
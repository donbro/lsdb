def GetVolID(cnx, volume_info_dict):
    
    # first, see if there is already an entry in the Volumes table
    
    # then, just do the insert, rely on the insert key to lookup the vol_id if approriate
    #   we do both "create" and "lookup" vol_ids in the insert trigger on table "files" 
    #   soley for consistency:  We rely on the insert trigger to "create" a vol_id
    #   if there is none.  we should also rely on the trigger to "lookup" an existing 
    #   one (eg, even if it is already in the volumes table).
    #   It is hard to remember if we get the vol_id from two different places


    query = ("select vol_id from volume_uuids "
                    "where vol_uuid = %r");
    
    data = (str(volume_info_dict['NSURLVolumeUUIDStringKey']) )
    
        
    x = execute_select_query(cnx, query, data)


    
    if len(x) != 0: # []
        vol_id = x[0][0] # x is: [(u'vol0009',)]
        return vol_id

    else:
    
        print "x:", type(x), x, len(x) == 0, x is [], x is not []
        filename         = volume_info_dict[NSURLNameKey]
        file_create_date = volume_info_dict['NSFileCreationDate']
        print filename, file_create_date;
        select_query = ( "select vol_id, folder_id, file_name, file_id, file_mod_date from files.files "
                        " where file_name = %r  and file_create_date = %r and folder_id = 1 " )
                        
        select_data = (filename.encode('utf8'), str(file_create_date) )
        
        print select_query % select_data

        sys.exit()
        
    

    
    # (l, zz) = execute_insert_query(cnx, query, data)
    
    pr4(l, vol_id, "", data[1])
    # pr5(l, vol_id, fid, d, p)    

    # l = "select"
    
    pathname = volume_info_dict["NSURLPathKey"]

    filename         = volume_info_dict[NSURLNameKey]
    file_id          = volume_info_dict['NSFileSystemFileNumber']
    file_size        = volume_info_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = volume_info_dict['NSFileCreationDate']

    select_query = ( "select vol_id, folder_id, file_name, file_id, file_mod_date from files.files "
                        " where file_name = %r  and file_create_date = %r and folder_id = 1 " )
                        
    select_data = (filename.encode('utf8'), str(file_create_date) )

    zz = execute_select_query(cnx, select_query, select_data)

    if zz == []:
        l = "creating"
        vol_id = None 
    else:
        l = "found"
        vol_id = zz[0][0]
    
    sa =  [d['df'].stringFromDate_(file_create_date) for d in dx]
    for a in sa:
        pr4(l, vol_id , a, pathname)

    return vol_id

        
from Foundation import NSDayCalendarUnit, NSWeekdayCalendarUnit,\
    NSYearCalendarUnit,  NSMonthCalendarUnit, NSHourCalendarUnit, \
    NSMinuteCalendarUnit,   NSSecondCalendarUnit, NSTimeZone, NSDate, \
    NSDateFormatter, NSGregorianCalendar
    



        
        #    basePath = [[openPanel filenames] objectAtIndex:0];
        #    enumerator = [[NSFileManager defaultManager] enumeratorAtPath:basePath];
        #    while(subpath = [enumerator nextObject]) {
        #        if([[[enumerator fileAttributes] objectForKey:NSFileType] isEqualToString:NSFileTypeDirectory]) {
        #            [enumerator skipDescendents];
        #            continue;
        #        }
        #        if([imageFileTypes containsObject:[subpath pathExtension]])
        #        [_fileList addObject:[basePath stringByAppendingPathComponent:subpath]];
        #    }        

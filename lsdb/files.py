#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
~/projects/lsdb/lsdb/files.py

Created by donb on 2013-01-22.
Copyright (c) 2013 Don Brotemarkle. All rights reserved.
"""

import sys

if sys.version_info < (2, 6):
    print "Sorry, python version is %d.%d.  We require Python %d.%d." %  ( sys.version_info.major , sys.version_info.minor, 2, 6)
    sys.exit(1)


# 
#   FSSpec
# 
#   RIP FSSpec
#   Note “FSSpec” is a deprecated type in Apple’s APIs.
#   The type is not availble for 64-bit code,
#   and shouldn’t be used for new development.
#   [http://packages.python.org/pyobjc/core/fsref-fsspec.html]
#   FSSpecs are deprecated on Mac OS X and their use is highly discouraged.
#   They have trouble with internationalization and cannot support some
#   files with more than 31 characters in their name. Avoid them at all costs.
#   [http://cocoadev.com/wiki/FSSpec]

import objc
import sys
import os


from Foundation import NSFileManager, NSURL, NSURLNameKey, NSURLTypeIdentifierKey , \
            NSURLIsDirectoryKey ,\
            NSURLIsVolumeKey, \
            NSURLLocalizedTypeDescriptionKey, CFURLGetFSRef,\
            NSFileModificationDate, NSFileTypeDirectory


import datetime

import mysql.connector
from mysql.connector import errorcode

__version__ = "0.5"


# global sharedFM

global options

sharedFM = NSFileManager.defaultManager()

props2 =[   NSURLNameKey, NSURLTypeIdentifierKey ,
    NSURLIsDirectoryKey , # NSURLFileSizeKey
    "NSURLTotalFileSizeKey" , "NSURLContentAccessDateKey",
    "NSURLFileResourceTypeKey",  # NSURLCreationDateKey,
    NSURLIsVolumeKey, "NSURLVolumeIdentifierKey",
    NSURLLocalizedTypeDescriptionKey
] # "NSURLIsUbiquitousItemKey"]

from Foundation import NSTimeZone, NSDateFormatter

from dates.dateutils import pr, tz_pr, get_datestrings, currentCalendar #  _DATETIME_to_python

# pr("Cocoa (Foundation) NSDate, etc.")


# choose some timezones with which to display some dates, they're fun!

    
time_zones = [
    
    ('Local' , NSTimeZone.localTimeZone()) ,
    ('GMT' ,   NSTimeZone.timeZoneForSecondsFromGMT_(0))
    # ('G' , NSTimeZone.timeZoneWithAbbreviation_(u'GMT'))

]

dx = [ {'name' : n , 'tz' : tz, 'df' : NSDateFormatter.alloc().init() } for n, tz in time_zones ]

map ( lambda y : NSDateFormatter.setTimeZone_(y[0], y[1])  , [ (x['df'], x['tz']) for x in dx] )

format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss z"   # ==> 'Fri 2011-07-29 19:46:39 EDT') or 'EST', or 'GMT-04:00'
format_string = "E yyyy.MM.dd HH:mm z"   # ==> 'Fri 2011-07-29 19:46:39 EDT') or 'EST', or 'GMT-04:00'

map ( lambda y : NSDateFormatter.setDateFormat_(y, format_string)  , [x['df'] for x in dx] )

# display list of timezones
if True:
    print "time_zones:"
    print
    s = [   "%12s: %s" % (x['name'], "%r (%s) %s%s" % tz_pr(x['tz']) ) for x in dx ]
    print "\n".join(s)
    print




def GetURLResourceValues(url, inProps):
    
    #  this can error when, eg, the file does not exist
    
    values, error =  url.resourceValuesForKeys_error_(
                inProps ,
                None )
    
    if error is not None:
        print
        print error
    
    # convert key strings from unicode(!) to string
    
    return  dict( zip(   [str(z) for z in values.allKeys() ] , values.allValues() ) )


def gocnx1(cnx, array_of_dict):
        
    vol_id = None
    
    # vol_id = GetVolID(cnx, array_of_dict[0]) # , vol_id)        
    

    for d in array_of_dict:

        vol_id = insertItem(cnx, d, vol_id)
        
    # might have vol_id at first select but will definitely have it here
    
    # print "updating volume uuid"
    
    query = ("insert into volume_uuids "
                    "(vol_id, vol_uuid, vol_total_capacity, vol_available_capacity) "
                    "values ( %s, %s, %s, %s ) ");
    
    data = (vol_id, str(array_of_dict[0]['NSURLVolumeUUIDStringKey']) , 
                    str(array_of_dict[0]['NSURLVolumeTotalCapacityKey']),                                                    
                    str(array_of_dict[0]['NSURLVolumeAvailableCapacityKey']) )
    
    # print data
    (l, zz) = execute_insert_query(cnx, query, data)
    pr4(l, vol_id, "", data[1])
    
def gocnx2(cnx, array_of_dict):
    
    # now enumerate through all files within/below the current file/directory
    
    basepath  = array_of_dict[-1]["NSURLPathKey"]
    
    depth_limit = 1

    # print "basepath:", basepath
    pr4("basepath:", "", "", basepath )
    enumerator = sharedFM.enumeratorAtPath_(basepath)
    subpath = enumerator.nextObject()
    while subpath:
        depth = subpath.count("/") + 1

        
        fullpath = basepath.stringByAppendingPathComponent_(subpath)
        ued =  NSURL.fileURLWithPath_(fullpath)
        
        ed1 =   GetURLResourceValues(ued, props2) 

        ed2 =  enumerator.fileAttributes()
        
        ed1.update(ed2)
        
        ed1.update(  {  "NSURLPathKey":  fullpath })
        
        if ed1[NSURLNameKey][0] == ".":  #  in ['.DS_Store']:
            # print "skipping:", subpath
            pr4("skipping:", "", "", subpath)

            if ed2['NSFileType'] == NSFileTypeDirectory :
                enumerator.skipDescendents() # dont need to skip whole directory, just this file
            subpath = enumerator.nextObject()
            continue
        
        # print ed2
        if ed2['NSFileType'] == NSFileTypeDirectory and depth > depth_limit-1:
            l =  "directory at depth (%d):" % ( depth,)
            pr4(l, "", "",  subpath+"/" )
            enumerator.skipDescendents()
            subpath = enumerator.nextObject()
            continue

        # this case might never happen?  we halt the descent at the directory above?  never get to depth_limit?
        if depth > depth_limit:
            print "depth limit: %s (%d)" % ( subpath, depth )
            enumerator.skipDescendents()
            subpath = enumerator.nextObject()
            continue

    
            
            
        # else:
            
        # do processing
    
        print "processing:", subpath
        fd1 =   GetURLResourceValues(ued, props2) 

        folder_url = ued.URLByDeletingLastPathComponent()            
        folder_dict =   GetAttributesOfItem(folder_url.path()) 
        
        # print folder_dict

        # my folder number is my container's file number
        
        ed1.update({'NSFileSystemFolderNumber': folder_dict['NSFileSystemFileNumber'] })


        # print ed2
        # fd2 =   GetAttributesOfItem(ued.path()) # enumerator isn't getting us the NSFileSystemFolderNumber?
        # print fd2 # ['NSFileSystemFolderNumber']
        # ed1.update(fd2)
        
        
        vol_id = insertItem(cnx, ed1, vol_id)
        
        subpath = enumerator.nextObject()
        
          
        
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

#
#   And now some mysql connector stuff…
#

def do_cnx_and_insert_array_of_dict(array_of_dict):
    
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
        
        gocnx1(cnx, array_of_dict)

        gocnx2(cnx, array_of_dict)

        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    finally:
        cnx.close()


def pr4(l, v, d, p):
    if options.verbose_level > 0:
        s =    "%-10s %-8s %27s %s" % (l, v , d,  p) 
        s =    "%-10s %-8s %s %s" % (l, v , d,  p)   # not fixed 27 but varies with width of third string.
        print s

def pr5(l, v, fid, d, p):
    if options.verbose_level > 0:
        s =    "%-10s %-8s %27s %s" % (l, v , d,  p) 
        s =    "%-10s %-8s %8d %s %s" % (l, v , fid, d,  p)   # not fixed 27 but varies with width of third string.
        print s

def print_vsd5(l, sl, n):
    if options.verbose_level >= n:     
        print l + ":\n"
        l = [ (d["NSURLPathKey"], 
                "is a volume" if d[NSURLIsVolumeKey] else "is not a volume", 
                    d['NSFileSystemFolderNumber']) for d in sl]
        s =    [ "    %8d  %-16s %s" % (fid,v ,   p) for ( p, v, fid) in l ]
        print "\n".join(s)
        print
    

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
    
def insertItem(cnx, itemDict, vol_id):

    # print "insert:", itemDict['NSURLNameKey']
    l = "insert"

    filename         = itemDict[NSURLNameKey]
    file_id          = itemDict['NSFileSystemFileNumber']
    file_size        = itemDict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = itemDict['NSFileCreationDate']
    file_mod_date    = itemDict[NSFileModificationDate]
    folder_id        = itemDict['NSFileSystemFolderNumber']


    sa =  dx[0]['df'].stringFromDate_(file_mod_date)

    pathname = itemDict["NSURLPathKey"]

    # pr4(l, vol_id , sa, pathname)
        
    if vol_id == None:

        add_file_sql = ("insert into files "
                        "(folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s ) "
                        );
        
        data_file = (int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        (l, zz) = execute_insert_query(cnx, add_file_sql, data_file)
        
        if l == "inserted" : 
            l = "created"       # we create a vol_id by inserting, when there is no vol_id to begin with.
        
        vol_id = zz[0][0]
        # print "    vol_id is: ", repr(vol_id)

        # pr4(l, vol_id, sa, pathname)
        pr5(l, vol_id, folder_id, sa, pathname)    
        # print
        
    
    else:  # vol_id != None:
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s, %s ) ");
        
        data_file = (vol_id, int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        (l, zz) = execute_insert_query(cnx, add_file_sql, data_file)
        # pr4(l, vol_id, sa, pathname)
        pr5(l, vol_id, folder_id, sa, pathname)    
        # print

    # end if vol_id is None

    return vol_id
    


def execute_select_query(cnx, select_query, select_data):

    cursor = cnx.cursor()

    if options.verbose_level >= 2:     
        print select_query % select_data
    
    cursor.execute( select_query % select_data )
    
    zz = [z for z in cursor]
    
    cursor.close()

    return zz
    

def execute_insert_query(cnx, query, data):
    """ returns (l,z) where l is a string indicating situation: created, existing, etc., and z is the entire result set """

    try:

        cursor = cnx.cursor() # buffered=True)      
        if options.verbose_level >= 3:     
            print query % data  
        cursor.execute(query, data) ## , multi=True)
        # zz = [z for z in cursor]
        # print "zz", zz
        cnx.commit()

        q = "select @vol_id"
        cursor.execute(q)
        zz3 = [z for z in cursor]
        
        # print "    vol_id (created):", zz3[0][0]
        
        cnx.commit()

        
  
        return ("inserted" , zz3 )
        

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            
            if options.verbose_level >= 3:
                n1 = err.msg.index('Duplicate entry')
                n2 = err.msg.index('for key ')
                msg2 = err.msg[n1:n2]
                print "    "+msg2

            cnx.commit()

            q = "select @vol_id"
            cursor.execute(q)
            zz3 = [z for z in cursor]
            # print "    vol_id (found):", zz3[0][0]
            cnx.commit()

            return ("existing" , zz3 )
            
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
        return None
        
    finally:
        
        cursor.close()


def GetAttributesOfItem(s):

    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
        print
        print error
    
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    return dz

def print_dict_tall(l, in_dict, left_col_width=24, verbose_level_threshold=1):
    if options.verbose_level >= verbose_level_threshold:
        print l + ":"
        print
        s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
        print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
        print

#===============================================================================
#   DoBasepath
#===============================================================================

def DoBasepath(options, basepath):

    #
    #   1. Generate Superfolder list, including volume
    #   Work upwards from given path to first path that indicates that it is indeed a volume (eg, "/Volumes/volume_name")
    #   Establish volume credentials
    #   Insert given path through volume path into database
    #   if given path is directory then enumerate through contained files and directories (according to options)
    #
    
    #  path given on command line is "basepath"

    url =  NSURL.fileURLWithPath_(basepath)

    # loop-and-a-half here.  go "upwards" and break (and hold) on first volume (ie, where d1[NSURLIsVolumeKey] is true)

    superfolder_list = []
    while True:       
        d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        d1.update(d2)
        d1.update(  {  "NSURLPathKey":  url.path() })
        superfolder_list.insert(0,d1)
        # if options.verbose_level >= 2: print "    "+repr(url.path())
        if d1[NSURLIsVolumeKey]: break
        # break before moving "up" a directory means variable "url" points to top directory.        
        url = url.URLByDeletingLastPathComponent()            

 
    #   get volume info and copy to the volume item's dictonary

    values, error =  url.resourceValuesForKeys_error_( ['NSURLVolumeUUIDStringKey',
                                                        'NSURLVolumeTotalCapacityKey',
                                                        'NSURLVolumeAvailableCapacityKey',
                                                        'NSURLVolumeSupportsPersistentIDsKey',
                                                        'NSURLVolumeSupportsVolumeSizesKey'] , None )

    d1.update(dict(values))

    print_dict_tall("volume info", values, 36, 3)
    
    # go forwards (downwards) thorugh the list setting each items "folder number" to the file number of its container

    for n, d in enumerate(superfolder_list):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
        else:
            d.update({'NSFileSystemFolderNumber': superfolder_list[n-1]['NSFileSystemFileNumber'] })
    
    print_vsd5("volume, superfolder(s) and basepath", superfolder_list, 2)    
    
    do_cnx_and_insert_array_of_dict(superfolder_list)
    
    return


#===============================================================================
# main
#===============================================================================


def main():

    #
    #   some favorite testing files
    #

    s = "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"
    #    s = u"/Users/donb/projects/lsdb/tests/unicode filename test/Adobe® Pro Fonts"

    s = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s = "/Volumes/Dunharrow"

    s = "/Users/donb/projects/files/get_files_values.py"

    s = "/Users/donb/projects"
    s = "/Volumes/Brandywine/erin esurance/"

    s = "/Volumes/Taos"
    s = "/Volumes/Dunharrow"
    s = "/Volumes/Brandywine/erin esurance/"
    s1 = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s2 = "/Volumes/Taos/TV series/Tron Uprising/Season 01/Tron Uprising - 1x01 - The Renegade (1).mkv"

    
    s = u'/Users/donb/projects/lsdb'
    
    s = u'/Volumes/Sapporo/TV Show/Winx Club/S01/Winx Club - 1x07 - Grounded (aka Friends in Need).avi'
    
    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/S03/'

    s = u'/Volumes/Ulysses/TV Shows/Lost Girl/'

    s = u'/Volumes/Ulysses/TV Shows/'

    s = "/"
    
    s = u"/Users/donb"
    
    s = u'/Volumes/Sacramento/Movies/The Dark Knight (2008) (720p).mkv'

    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        argv = ["--help"]+[s]
        argv = ["-rd 3"]+[s]
        argv = [s1,s2]
        argv = ["-v"]+[s]
    else:
        argv = sys.argv[1:]
    
    #
    #   optparse
    #
    # The optparse module is a modern alternative for command line option parsing 
    # that offers several features not available in getopt, including type conversion, 
    # option callbacks, and automatic help generation. There are many more features to 
    # optparse than can be covered here, but this section will introduce some of 
    # the more commonly used capabilities.
    # [http://www.doughellmann.com/PyMOTW/optparse/]

    
    from optparse import OptionParser, OptionValueError
    
    parser = OptionParser(usage='usage: %prog [options] [filename(s)] ',
                          version='%%prog %s' % __version__ )

    # --help ==>    Usage: get_files_values.py pathname [options] 
    # --version ==> get_files_values.py 0.6


    parser.add_option("-r", "--recursive",  dest="do_recursion",  action="store_const", const=True, 
        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,default=False )
    
                                                
    parser.add_option("-v", "--verbose", dest="verbose_level", 
        help="increment verbose count by one.  default=%default", action="count" ) 

    parser.add_option("-q", "--quiet", 
        action="store_const", const=0, dest="verbose_level", default=1, 
           help="Normal operation is to output one status line per file, status being \"inserted\", \"existing\", etc."
           " This option will prevent any output to stdout, Significant errors are still output to stderr.") 
        
        
    def _depth_callback(option, opt_str, value, parser): # , cls):
        if value == "None" or value == "none":
            setattr(parser.values, option.dest, None)
        else:
            try:
                setattr(parser.values, option.dest, int(value))
            except:
                raise OptionValueError("%s value must be integer or None. %s: %r received."
                                   % (option.dest, str(type(value)), value) )


    parser.add_option("-d", "--depth-limit", "--depth", dest="depth_limit", action="callback" , 
        callback=_depth_callback,
        help="limit recusion DEPTH. using DEPTH = 0 means process the directory only.  DEPTH=None means no depth limit (use with caution). "
        "Recursion is implied when any depth-limit is specified. default is %default.",
         metavar="DEPTH", type="string") 

    parser.add_option("-f", "--force-folder-scan", dest="force_folder_scan", action = "store_true", 
        help="explicitly check contents of directories even if directory timestamp not newer than"
        "database value.  Normal operation does not check the contents of a directory if its timestamp equals"
        "that in the database. default = %default", 
        default=False) 
        
        
    #
    #   set defaults and call parser
    #
                          
    parser.set_defaults( verbose_level=1,  ) # depth_limit=1,    

    global options
    
    (options, args) = parser.parse_args(argv)
    
    # no args means do the current directory
    
    if args == []: args = ["."]
    
    args = [os.path.abspath(a) for a in args]
    
    
    # print ', '.join([ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])
    # print reduce(lambda i,j:i+', '+j, [ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])

    if options.verbose_level > 0:
        print "sys.argv:"
        print
        print "\n".join(["    "+x for x in sys.argv])
        print

    if options.verbose_level > 0:
        print "options (after optparsing):"
        print
        print "\n".join([  "%20s: %r " % (k,v)  for k,v in options.__dict__.items() ])
        print
    if options.verbose_level > 0:
        print "args (after optparsing):"
        print
        if args == []:
            print [None]
        else:
            print "\n".join(["    "+x for x in args])
        print
        print
    
    
    for basepath in args:
        DoBasepath(options, basepath)
        
        
#   Calling main() from the interactive prompt (>>>). Really?  
#   This is a commandline utility; i'm never going to do that.
#
#   maybe.  for testing.  just sayin'

if __name__ == "__main__":
        main()
        
#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
~/projects/lsdb/lsdb/files.py

Created by donb on 2013-01-22.
Copyright (c) 2013 Don Brotemarkle. All rights reserved.
"""

import objc
import sys
import os

__version__ = "0.5"


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

from Foundation import NSFileManager, NSURL, NSURLNameKey, NSURLTypeIdentifierKey , \
            NSURLIsDirectoryKey ,\
            NSURLIsVolumeKey, \
            NSURLLocalizedTypeDescriptionKey, CFURLGetFSRef,\
            NSFileModificationDate


import datetime

import mysql.connector
from mysql.connector import errorcode

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

from dates.dateutils import pr

# def pr(l,v=None):
#     """prints str() of v"""
#     if v is not None:
#         print "%s:\n\n    %s\n" % (l, v)
#     else:
#         print "%s\n%s\n" % (l, "_"*len(l))

pr("Cocoa (Foundation) NSDate, etc.")

from Foundation import NSCalendar, NSTimeZone, NSDateFormatter

# try a few timezones, they're fun!

currentCalendar = NSCalendar.currentCalendar()
    
time_zones = [
    
    ('Local' , NSTimeZone.localTimeZone()) ,
    
    ('Pacific' , NSTimeZone.timeZoneWithName_(u'America/Los_Angeles')) ,
    
    ('Current' , currentCalendar.timeZone()) 
    
]

dx = [ {'name' : n , 'tz' : tz, 'df' : NSDateFormatter.alloc().init() } for n, tz in time_zones ]

def tz_pr(tz):
    return (
            tz.name(),
            tz.abbreviation(),
            "offset %d hours" % (tz.secondsFromGMT() / (60 * 60) ),
            "(**local**)" if  "Local Time Zone " in tz.description() else ""
            )
    

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
        
        vol_id = None
        
        vol_id = select_file(cnx, array_of_dict[0], vol_id)        

        for d in array_of_dict:

            vol_id = insert(cnx, d, vol_id)
            
        # might have vol_id at first select but will definitely have it here
        
        print "updating volume uuid"
        
        query = ("insert into volume_uuids "
                        "(vol_id, vol_uuid) "
                        "values ( %s, %s ) ");
        
        data = (vol_id, str(array_of_dict[0]['NSURLVolumeUUIDStringKey'] ))
        
        print data
        execute_query(cnx, query, data)
        
        
        cnx.close()
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err

def select_file(cnx, values_dict, vol_id):

    print "select_file:", values_dict['NSURLNameKey']

    filename         = values_dict[NSURLNameKey]
    file_id          = values_dict['NSFileSystemFileNumber']
    file_size        = values_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = values_dict['NSFileCreationDate']

    select_query = ( "select vol_id, folder_id, file_name, file_id, file_mod_date from files.files "
                        " where file_name = %r  and file_create_date = %r and folder_id = 1 " )
                        

    select_data = (filename.encode('utf8'), str(file_create_date) )

    # zz = execute_query(cnx, select_query, select_data)
    zz = execute_query2(cnx, select_query, select_data)

    if zz == []:
        print "    vol_id is None\n"
        return None
    else:
        print "    vol_id is %r\n" % ( zz[0][0], )

        return zz[0][0]

def execute_query2(cnx, select_query, select_data):

    cursor = cnx.cursor()
    
    # print "executing", select_query % select_data
    
    cursor.execute( select_query % select_data )
    
    zz = [z for z in cursor]
    
    cursor.close()
    return zz
    

def execute_query(cnx, query, data):

    # print "executing", query % data
    
    try:

        cursor = cnx.cursor()        
        cursor.execute(query, data)
        zz = [z for z in cursor]
        cnx.commit()
        
        print "zz", zz

        return zz
        

    except mysql.connector.Error as err:
        if err.errno == 1062 and err.sqlstate == '23000':
            n1 = err.msg.index('Duplicate entry')
            n2 = err.msg.index('for key ')
            msg2 = err.msg[n1:n2]
            print "    "+msg2
            print
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'erxr:', err, err.errno , err.message , err.msg, err.sqlstate #  , dir(err)
        return None
        
    finally:
        cursor.close()


# from mysql.conversion.py

def _DATETIME_to_python( in_date ):
    """
    Returns DATETIME column type as datetime.datetime type.
    """
    # pv = None
    # try:

    v = str(in_date) 
    a = v.split(" ")
    fs = 0
    dt = [ int(v) for v in  a[0].split('-') ] +\
         [ int(v) for v in  a[1].split(":") ] + [fs,]
    pv = datetime.datetime(*dt)

    # except ValueError:
    #     pv = None
    
    return pv
        
from Foundation import NSCalendar, NSDayCalendarUnit, NSWeekdayCalendarUnit,\
    NSYearCalendarUnit,  NSMonthCalendarUnit, NSHourCalendarUnit, \
    NSMinuteCalendarUnit,   NSSecondCalendarUnit, NSTimeZone, NSDate, \
    NSDateFormatter, NSGregorianCalendar
    
def insert(cnx, values_dict, vol_id):

    print "insert:", values_dict['NSURLNameKey']

    filename         = values_dict[NSURLNameKey]
    file_id          = values_dict['NSFileSystemFileNumber']
    file_size        = values_dict.get('NSURLTotalFileSizeKey',0) # folders have no filesize key?
    file_create_date = values_dict['NSFileCreationDate']
    file_mod_date    = values_dict[NSFileModificationDate]
    folder_id        = values_dict['NSFileSystemFolderNumber']
    
    
    print file_mod_date
    
    print _DATETIME_to_python(file_mod_date)

    print "file_mod_date", _DATETIME_to_python( str(file_mod_date) ),  str(file_mod_date) 
    # print "file_mod_date", _DATETIME_to_python( str(file_mod_date) ),  file_mod_date

    currentCalendar = NSCalendar.currentCalendar()
    
    # print currentCalendar
    # print dir(currentCalendar)
    
    
    pacificTime = NSTimeZone.timeZoneWithName_("America/Miami")

    currentCalendar.setTimeZone_(pacificTime)
    
    # file_mod_date_components
    fcdc =             currentCalendar.components_fromDate_(NSDayCalendarUnit | 
                    NSYearCalendarUnit |   NSMonthCalendarUnit |  NSHourCalendarUnit | 
    NSMinuteCalendarUnit |    NSSecondCalendarUnit | NSWeekdayCalendarUnit , file_mod_date )

    # print dir(cc)
    
    print [ fcdc.year(), fcdc.month(), fcdc.day(), fcdc.hour(), fcdc.minute(), fcdc.second(),  ]


    dateOfKeynote = currentCalendar.dateFromComponents_(fcdc)
    
    print dateOfKeynote
    
    # myDate = NSDate.dateWithTimeIntervalSinceReferenceDate_(343675999.713839)
    # dateFormatter
    dateFormatter = NSDateFormatter.alloc().init()
    calendar = NSCalendar.alloc().initWithCalendarIdentifier_(NSGregorianCalendar)
    dateFormatter.setCalendar_(currentCalendar)
    
    # locale
    
    dateFormatter.setDateFormat_("yyyy'-'MM'-'dd' 'HH':'mm':'ss' 'V'")  #  'V' => 'EST'
    
    myDateString = dateFormatter.stringFromDate_(file_mod_date)
    print myDateString    
    # 2011-07-02 17:02:54 EDT

    

    
    # from _datetime_to_mysql():  (string suitable for MySQL)
    #   if not value.microsecond:
    #   return '%d-%02d-%02d %02d:%02d:%02d' % (
    #         value.year, value.month, value.day,
    #         value.hour, value.minute, value.second)    
        
    if vol_id == None:

        add_file_sql = ("insert into files "
                        "(folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s ) ");
        
        data_file = (int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        execute_query(cnx, add_file_sql, data_file)
                
        cursor2 = cnx.cursor()
        query = "select max(vol_id) from files where vol_id RLIKE 'vol[0-9][0-9][0-9][0-9]' "

        cursor2.execute(query)
        print "    vol_id is none"
        zz = [z for z in cursor2]
        vol_id = zz[0][0]
        print "    vol_id is: ", repr(vol_id)
        cursor2.close()
    
    else:  # vol_id != None:
        
        add_file_sql = ("insert into files "
                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date) "
                        "values ( %s, %s, %s, %s, %s, %s, %s ) ");
        
        data_file = (vol_id, int(folder_id), filename.encode('utf8'), int(file_id), int(file_size),
                                str(file_create_date), str(file_mod_date)  )

        execute_query(cnx, add_file_sql, data_file)

    # end if vol_id is None

    return vol_id
    

def GetAttributesOfItem(s):
    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
        print
        print error
    # >>> map(  lambda x: x*x  ,   [1,2,3] )
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    
    return dz

def print_dict_tall(l, in_dict, left_col_width=24, verbose_count_threshold=1):
    if options.verbose_count >= verbose_count_threshold:
        print l + ":"
        print
        s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
        print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
        print

def run_files(options, in_path):
    
    print "arg and superfolders:"
    print

    url =  NSURL.fileURLWithPath_(in_path)  #  fileURLWithPath

    superfolder_list = []
    while True: # not d1[NSURLIsVolumeKey]:        
        d1, d2 = ( GetURLResourceValues(url, props2), GetAttributesOfItem(url.path()) )
        d1.update(d2)
        superfolder_list.insert(0,d1)
        print "    "+repr(url.path())

        if d1[NSURLIsVolumeKey]: break

        # modify the directory only if non-volume (ie, after break) means url will ve volume url.        
        url = url.URLByDeletingLastPathComponent()            

    print

    #   get volume info and copy to the volume item's dictonary

    values, error =  url.resourceValuesForKeys_error_(
        ['NSURLVolumeUUIDStringKey','NSURLVolumeTotalCapacityKey','NSURLVolumeSupportsPersistentIDsKey',
            'NSURLVolumeSupportsVolumeSizesKey'] ,
        None )

    d1.update(dict(values))

    print_dict_tall("volume info", values, 36)

    #    Volume UUID:              77E236DC-4145-3D23-BADB-CE8D1F233DDA
    
    # print "volume info:"
    # print
    # print "\n".join([  "%36s: %r " % (k,v)  for k,v in dict(values).items() ])
    # print
    
    
    # volume will be item zero in the list
    for n, d in enumerate(superfolder_list):
        if d[NSURLIsVolumeKey]:
            d.update( {'NSFileSystemFolderNumber': 1L} )
            print "is a volume", 1L
        else:
            d.update({'NSFileSystemFolderNumber': superfolder_list[n-1]['NSFileSystemFileNumber'] })
            print "is not a volume",  superfolder_list[n-1]['NSFileSystemFileNumber']
    
    print
    
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
    s = "/Users/donb/projects"
    s = "/Users/donb/projects/files/get_files_values.py"

    s = "/Users/donb/projects"
    s = "/Volumes/Brandywine/erin esurance/"

    s = "/Volumes/Taos"
    s = "/Volumes/Dunharrow"
    s = "/Volumes/Brandywine/erin esurance/"
    s1 = "/Volumes/Roma/Movies/Tron Legacy (2010) (1080p).mkv"

    s2 = "/Volumes/Taos/TV series/Tron Uprising/Season 01/Tron Uprising - 1x01 - The Renegade (1).mkv"

    s = "/"
    
    s = u'/Users/donb/projects/lsdb'
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        argv = ["--help"]+[s]
        argv = ["-rd 3"]+[s]
        argv = [s1,s2]
        argv = [s]
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
    
                                                
    parser.add_option("-v", "--verbose", dest="verbose_count", 
        help="increment verbose count by one.  default=%default", action="count" ) 

    parser.add_option("-q", "--quiet", 
        action="store_const", const=0, dest="verbose_count", default=1, 
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
                          
                          
    parser.set_defaults( verbose_count=1,  ) # depth_limit=1,    

    global options
    
    (options, args) = parser.parse_args(argv)
    
    #   ala "ls", if there are no args, that means do the current directory "."
    if args == []: args = ["."]
    
    args = [os.path.abspath(a) for a in args]
    
    
    # print ', '.join([ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])
    # print reduce(lambda i,j:i+', '+j, [ k0 +'='+repr(v0) for  k0,v0 in options.__dict__.items() ])

    if options.verbose_count > 1:
        print "sys.argv:"
        print
        print "\n".join(["    "+x for x in sys.argv])
        print

    if options.verbose_count > 1:
        print "options:"
        print
        print "\n".join([  "%20s: %r " % (k,v)  for k,v in options.__dict__.items() ])
        print
    

    if options.verbose_count > 1:
        print "args (after optparsing):"
        print
        if args == []:
            print [None]
        else:
            print "\n".join(["    "+x for x in args])
        print
    
    
    for s in args:
        run_files(options, s)
        
        
#   Calling main() from the interactive prompt (>>>). Really?  
#   This is a commandline utility; i'm never going to do that.
#
#   maybe.  for testing.  just sayin'

if __name__ == "__main__":
        main()
        
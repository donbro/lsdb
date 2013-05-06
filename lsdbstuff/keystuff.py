#!/Users/donb/projects/VENV/lsdb/bin/python
# encoding: utf-8

# keystuff
# the stuff that goes from NS to python to database
#


from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey, \
                        NSURLIsPackageKey


databaseAndURLKeys = [  ( 'file_name',            NSURLNameKey), 
                        (  None,                  NSURLIsDirectoryKey), 
                        (  None,                  NSURLVolumeURLKey), 
                        (  None,                  NSURLLocalizedTypeDescriptionKey), 
                        ( 'file_uti',             NSURLTypeIdentifierKey), 
                        ( 'file_create_date',     NSURLCreationDateKey), 
                        ( 'file_mod_date',        NSURLContentModificationDateKey), 
                        (  None,                  NSURLParentDirectoryURLKey), 
                        ( 'file_size',           'NSURLTotalFileSizeKey'),
                        ( 'file_id',             'NSFileSystemFileNumber'),
                        ( 'folder_id',           'NSFileSystemFolderNumber' ),
                        (  None,                  NSURLIsVolumeKey)                        
                    ]


enumeratorURLKeys = [t[1] for t in databaseAndURLKeys]

import os, sys

MY_FULLNAME = os.path.normpath(os.path.abspath(__file__))   # my file is always the same no matter where I am being executed from?
PROG_DIR = os.path.dirname(MY_FULLNAME)                       
DATA_DIR = PROG_DIR                                          
CONFIG_FILE = os.path.join(DATA_DIR, "keystuff.cfg") # /Users/donb/projects/lsdb-master/dbstuff/keystuff.cfg

print "CONFIG_FILE", CONFIG_FILE

from Foundation import NSDateFormatter, NSTimeZone, NSDateFormatterFullStyle

if __package__ == None:
    super_dirname = os.path.dirname(PROG_DIR) # but we want the *filesystem* location, not whatever is sys.path[0]
    print "executing from without a package"
    print "inserting path %r into sys.path" %  super_dirname # os.path.join(sys.path[0], '..')
    sys.path.insert(1,  super_dirname )    
    # now imports below can find superior directory
else:
    print "__package__", __package__


from printstuff.printstuff import GPR

# escape and quote are from [mysql-connector-python-1.0.8, file: "mysql/connector/conversion.py"]
def escape(value):
    """
    Escapes special characters as they are expected to by when MySQL
    receives them.
    As found in MySQL source mysys/charset.c
    
    Returns the value if not a string, or the escaped string.
    """
    if value is None:
        return value
    elif isinstance(value, (int,float,long )):  # ,Decimal)):
        return value
    res = value
    res = res.replace('\\','\\\\')
    res = res.replace('\n','\\n')
    res = res.replace('\r','\\r')
    res = res.replace('\047','\134\047') # single quotes
    res = res.replace('\042','\134\042') # double quotes
    res = res.replace('\032','\134\032') # for Win32
    return res

def quote(buf):
    """
    Quote the parameters for commands. General rules:
      o numbers are returns as str type (because operation expect it)
      o None is returned as str('NULL')
      o String are quoted with single quotes '<string>'
    
    Returns a string.
    """
    if isinstance(buf, (int,float,long)): # ,Decimal)):
        return str(buf)
    elif isinstance(buf, type(None)):
        return "NULL"
    else:
        # Anything else would be a string
        return "'%s'" % buf 



# put together a date formatter.  used to just use str()! [ :( ]

db_df = NSDateFormatter.alloc().init()
gmt0_tz = NSTimeZone.timeZoneForSecondsFromGMT_(0)
db_df.setTimeZone_( gmt0_tz )
db_df.setTimeStyle_(NSDateFormatterFullStyle)       # <=== magic.  have to do this(?)
db_df.setDateFormat_("yyyy-MM-dd HH:mm:ss")         #"yyyy-MM-dd hh:mm:ss") # "2013-03-30 18:11:07"


def GetDR(item_dict, required_fields, quote_and_escape=True, verbose_level_threshold=3):
    """Convert from item_dict (Cocoa) forms to database-ready forms"""

    GPR.print_dict("GetDR(in)" , item_dict, 36, verbose_level_threshold)
   
    result_dict = {}
    for db_field_name in required_fields:
        
        if db_field_name in item_dict:
            dict_key_name = db_field_name            
        else:
            try:
                db_field_name_index = map( lambda y: y[0], databaseAndURLKeys).index(db_field_name)
                dict_key_name = databaseAndURLKeys[db_field_name_index][1]
            except ValueError:
                dict_key_name = db_field_name            

        # print  "%16s => %-36s :" % (db_field_name,  dict_key_name),
        
        #   do special processing based on database field name, not on inherent type of argument?
            
        if db_field_name in ['vol_id', 'file_name', 'file_uti']:
            c = item_dict[dict_key_name].encode('utf8')
            if quote_and_escape:
                result_dict[db_field_name] =  quote(escape(c))
            else:
                result_dict[db_field_name] =  c
                            
        elif db_field_name in ['file_create_date', 'file_mod_date']:
            d = item_dict[dict_key_name]
            if isinstance( d, str):
                c = d
            else:
                c = str(db_df.stringFromDate_(d))
            if quote_and_escape:
                result_dict[db_field_name] =  quote(escape(c))
            else:
                result_dict[db_field_name] =  c

        elif db_field_name in ['file_size', 'file_id', 'folder_id']: # 
            
            result_dict[db_field_name] =  int(item_dict[dict_key_name])

        else:
            result_dict[db_field_name] =  item_dict[dict_key_name]

        
    GPR.print_dict_no_repr("GetDR(out)" + ( "(q+e)" if quote_and_escape else "(no q+e)"), result_dict, 36, verbose_level_threshold)

    return result_dict


import unittest

def dateFromString(myDateAsAStringValue):
    df = NSDateFormatter.alloc().init()
    df.setTimeStyle_(NSDateFormatterFullStyle)  # <=== magic.  have to do this(?)
    df.setDateFormat_("yyyy-MM-dd HH:mm:ss") #"yyyy-MM-dd hh:mm:ss") # "2013-03-30 18:11:07"
    myDate =  db_df.dateFromString_(myDateAsAStringValue)
    return myDate
    

class keystuff_TestCase( unittest.TestCase ):
    """ Class to test keystuff """
    
    def test_050_keystuff(self):
        """tuple_set uniqueness"""

        self.assertEqual( CONFIG_FILE   , "/Users/donb/projects/lsdb-master/lsdbstuff/keystuff.cfg")

    
    def test_051_escape(self):
        """escape"""
        xx = [ '\\', '\n', '\r', "'", '\042' ]
        yy = [ '\\\\', '\\n', '\\r', "\\'", '\\"' ]
        
        for n, s in enumerate(xx):
            self.assertEqual( escape(s)  , yy[n])

    def test_060_GetDR(self):
        """GetDR"""


        in_dict1 = {
                       'file_name': 'Saratoga' ,
                          'vol_id': 'vol0030' ,
                       'folder_id': 1 ,
                   'file_mod_date': '2013-04-26 05:57:55' 
                  }

        required_fields =  [   'vol_id', 'folder_id', 'file_name', 'file_mod_date'  ]
        sql_dict = GetDR(in_dict1, required_fields, verbose_level_threshold=2)
        d2 = dict(  [ (k, v if isinstance(v, (int,float,long)) else quote(v)) for (k, v) in in_dict1.items()])
        self.assertEqual( sql_dict , d2)
        
    def test_062_GetDR(self):
        """GetDR"""


        in_dict1 = {
            'NSFileSystemFileNumber' : 2,
            'NSFileSystemFolderNumber' : 1L,
            NSURLContentModificationDateKey:dateFromString("2013-04-26 05:57:55"),
            NSURLCreationDateKey:dateFromString("2012-07-05 19:53:24"),
            NSURLIsDirectoryKey : 1,
            NSURLIsPackageKey : 0,
            NSURLIsVolumeKey : 1,
            NSURLLocalizedTypeDescriptionKey : 'Volume',
            NSURLNameKey : u'Saratoga',
            NSURLParentDirectoryURLKey : "file://localhost/Volumes/",
            'NSURLPathKey' : "/Volumes/Saratoga",
            'NSURLTotalFileSizeKey' : 0,
            NSURLTypeIdentifierKey : "public.volume",
            NSURLVolumeURLKey : "file://localhost/Volumes/Saratoga/",
            "current_item_directory_is_being_checked" : 0,
            'depth' : 0,
            "directory_is_up_to_date" : 1,
            'url' : "file://localhost/Volumes/Saratoga/",
            "vol_id" : 'vol0030'
        }

        required_fields =  ['vol_id', 'folder_id', 'file_name', 'file_id', 'file_size', 'file_create_date', 'file_mod_date', 'file_uti' ]
        sql_dict = GetDR(in_dict1, required_fields, verbose_level_threshold=2)
        self.assertEqual(  sql_dict ,
            {'file_uti': "'public.volume'", 'file_name': "'Saratoga'", 'file_mod_date': "'2013-04-26 05:57:55'", 
                    'folder_id': 1, 'file_size': 0, 'file_create_date': "'2012-07-05 19:53:24'", 
                    'vol_id': "'vol0030'", 'file_id': 2}
            )
      
if __name__ == '__main__':
    unittest.main()
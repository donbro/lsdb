#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey

import sys
import os.path
sys.path.append(os.path.abspath('..'))

from Foundation import NSDate, NSOrderedSame, NSOrderedDescending, NSOrderedAscending
from Foundation import NSDateFormatter

from dates import dateFormatters # print_timezones

MY_FULLNAME = os.path.normpath(os.path.abspath(__file__))   # /Users/donb/projects/lsdb-master/printstuff/printstuff.py 
# MY_NAME = os.path.basename(MY_FULLNAME)                     # printstuff.py 
PROG_DIR = os.path.dirname(MY_FULLNAME)                     # /Users/donb/projects/lsdb-master/printstuff 
DATA_DIR = PROG_DIR                                         # /Users/donb/projects/lsdb-master/printstuff
CONFIG_FILE = os.path.join(DATA_DIR, "printstuff.cfg")

if __package__ == None:
    super_dirname = os.path.dirname(PROG_DIR)
    print "executing from without a package"
    print "inserting path %r into sys.path" %  super_dirname # os.path.join(sys.path[0], '..')
    sys.path.insert(1,  super_dirname )    
    # now imports below can find superior directory
else:
    print "package", __package__ , os.path.splitext(os.path.basename(__file__))[0]

# these attributes are setattr'd into printstuff at init() time
DEFAULT_CONFIGURATION = {
    'verbose_level': 2,
    'left_col_width': 24,
    'vol_id_width': 7,
    'file_id_width': 8,
    'file_uti_width' : 24, # 20
    
    # the full width date format strings
    
    'date_format'                : "E yyyy.MM.dd HH:mm z",
    'date_format_early'          : "E yyyy.MM.dd HH:mm z",

    # the shorter width date format strings (note single digit month format (ie, 1..12 not 01..12) this is modified as [0:3] + %14s % [3:])    

    'date_format_short'          : "E MM.dd HH:mm z",     # "Sat 03.30 18:11 EDT", "Tue 10.02 16:13 EDT"
    'date_format_short_early'    : "E  yyyy.MM.dd z",     # "Fri  2011.09.02 EDT"

    # even shorter width (no timezone)

    'date_format_shortest'          : "E M.dd HH:mm",     # "Sat  3.30 18:11", "Tue 10.02 16:13"
    'date_format_shortest_early'    : "E  yyyy.MM.dd",    # "Fri  2011.09.02"

    # If the modification time of the file is more than 6 months
    #  in the past or future, then the year of the last modification
    #  is displayed in place of the hour and minute fields. [man ls]
    
    


    # 'config_file': CONFIG_FILE,  # config file location is not to be put inside of the config file!??
    # 'unix_socket': None,
    # 'use_unicode': True,
    # 'charset': 'utf8',
    # 'collation': None,

    # 'time_zone': None,
    # 'sql_mode': None,

    # 'raw': False,
    # 'ssl_ca': None,
    # 'ssl_cert': None,
    # 'ssl_key': None,
    # 'passwd': None,
    # 'db': None,
    # 'connect_timeout': None,
    # 'dsn': None
}


# Three levels of config:
#   1.  here in the module (DEFAULT_CONFIGURATION)
#   2.  in one (or many) config files, eg, "printstuff.cfg"
#   3.  command-line options brought in as dict and passed to ,eg, init
#  config is called during init() but can be called separately

import ConfigParser

class printstuff(object):
    """docstring for printstuff"""
    
    def __init__(self, **kwargs):
        super(printstuff, self).__init__()

        default_dict = DEFAULT_CONFIGURATION
        
        config = ConfigParser.ConfigParser()
        config.readfp(open(CONFIG_FILE))
        config_dict = dict(config.items('printstuff'))
        default_dict.update(config_dict)
        
        for k, v in default_dict.items():
            setattr(self, k, v)        
                
        if True or len(kwargs) > 0:
            self.config(**kwargs)


    def write_config(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open(CONFIG_FILE))
        config.add_section('printstuff')
        for k,v in self.__dict__.items():
            config.set('printstuff', k, v)

        # Writing our configuration file to CONFIG_FILE
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
        
        
    def config(self, **kwargs):
        """called during init() but can be called separately"""

        for k, v in kwargs.items():
            setattr(self, k, v)        

        self.print_attrs("printstuff", self, verbose_level_threshold=3)
        
        # Three levels of config:
        #   1.  here in the module (DEFAULT_CONFIGURATION)
        #   2.  in one (or many) config files, eg, "printstuff.cfg"
        #   3.  command-line options brought in as dict and passed to ,eg, init        
         
  
    #===========================================================================
    #       print_dict
    #===========================================================================
    def print_dict(self, l, in_dict, left_col_width=None, verbose_level_threshold=1):
        if left_col_width == None:
            left_col_width = self.left_col_width
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s = "%%%ss: %%r " % left_col_width # '%36s: %r '
            print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
            print
    
    def print_dict_no_repr(self, l, in_dict, left_col_width=None, verbose_level_threshold=1):
        if left_col_width == None:
            left_col_width = self.left_col_width
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s_s = "%%%ss: %%s " % left_col_width # '%36s: %r '
            s_r = "%%%ss: %%r " % left_col_width # '%36s: %r '
            z = []
            for k,v in dict(in_dict).items():
                try:
                    z.append( ( s_s % (k,v) ).encode('ascii') )
                except UnicodeDecodeError:
                    z.append( s_r % (k,v) )
            print u"\n".join(z)
            print
    
    def print_list(self, l, in_list, left_col_width=None, verbose_level_threshold=1):
        if left_col_width == None:
            left_col_width = self.left_col_width
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s = "    %%%ss" % left_col_width
            print "\n".join([  s % x for x in in_list ])
            print

    def print_attrs(self, l, in_obj, type_list=(str, bool, int), without_underscore=True, verbose_level_threshold=2):
        """tall print of attrs of object matching type, without underscore"""

        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            r = [ (a, getattr(in_obj,a)) for a in dir(in_obj) if isinstance( getattr(in_obj,a), type_list )  
                                                                and ( (a[0]!="_") or not without_underscore) ]    
            print "\n".join([ "%24s = %r" % s for s in r ])
            print
    
    def print_it(self, s, verbose_level_threshold=2):
        if self.verbose_level >= verbose_level_threshold:     
            try:
                print s
            except UnicodeDecodeError as e:
                print  repr(e[1])
                # print u"UnicodeDecodeError", repr(e[1])
                
    print_it1 = print_it




    def print_it0(self, s, verbose_level_threshold=2):
        """ie, no trailing CR"""
        if self.verbose_level >= verbose_level_threshold:     
            try:
                print s,
            except UnicodeDecodeError as e:
                print  repr(e[1]),
                # print u"UnicodeDecodeError", repr(e[1])

    def print_it2(self, l, s, verbose_level_threshold):

        # files_generator:
        # 
        #     /Users/donb/Catherine Video Review.mp4
        
        tab_chars = "    "
        s = tab_chars+("\n"+tab_chars).join(s.split("\n"))
        
        if self.verbose_level >= verbose_level_threshold:     
            try:
                print "%s:" % l
                print
                print s
                print
            except UnicodeDecodeError as e:
                print "%r:" % l
                print
                print repr(s)
                print


    def print_it25(self, l, s, verbose_level_threshold):
        """ print simpler output for verbose_level_threshold - 1"""

        # files_generator:
        # 
        #     /Users/donb/Catherine Video Review.mp4

        if self.verbose_level >= verbose_level_threshold:     
            try:
                print "%s:" % l
                print
                print "    ", s
                print
            except UnicodeDecodeError as e:
                print "%r:" % l
                print
                print "    ", s
                print

        elif self.verbose_level == verbose_level_threshold - 1:     
            try:
                print "%s:" % l, "    ", s
                print
            except UnicodeDecodeError as e:
                print "%r:" % l, "    ", s
                print

        elif self.verbose_level == verbose_level_threshold - 2:     
            try:
                print "%s:" %  s
            except UnicodeDecodeError as e:
                print "%r:" %   s


    def print_superfolders_list(self, l, sl, verbose_level_threshold):
        if self.verbose_level >= verbose_level_threshold:     
            print l + ":\n"
            l = [ (d["NSURLPathKey"], 
                    "is a volume" if d[NSURLIsVolumeKey] else "is not a volume", 
                        d['NSFileSystemFolderNumber']) for d in sl]
            s =    [ "    %8d  %-16s %s" % (fid,v ,   p) for ( p, v, fid) in l ]
            print "\n".join(s)
            print
    
    def pr4(self, l, v, d, p, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            print "%-10s %-8s %27s %s" % (l, v , d,  p) 


         
    def pr7z(self,  item_dict,  stak=None, depth_limit=None, verbose_level_threshold=1):
        """0-0      vol0006     5651     6227 Wed 2013.03.20 13:29 EDT  1 <filename>"""

        if self.verbose_level < verbose_level_threshold:    
            return
            
        # from "man ls"
        # If the -l option is given, the following information is displayed for each file: 
        #     file mode, number of links, owner name, group name, number of bytes in the file,  
        #     abbreviated month, day-of-month file was last modified, hour file last modified, 
        #     minute file last modified, and the pathname.              
        
        # assemble a list of strings to print, then " ".join()
        
        s = []

        if GPR.verbose_level >= 2 and 'current_item_directory_is_being_checked' in item_dict:
            g = "[^]" if item_dict['current_item_directory_is_being_checked'] else "[-]"
            s += [g]
            
        # if RS1_db_rels is not None:
        #     s0 = dict([(k, RS1_db_rels[k]) for k in RS1_db_rels] )# avoid self-creation
        #     s1 =  '[%s]' % "-".join([ "%d"%(len(s0[k])) if k in s0 else "*" for k in stak])
        #     s += [ "%-6s" % s1 ]
        # 
        #     # this line *creates* an entry since RS is a *default* dict and k isn't already present in RS            
        #     # s1 =  '[%s]' % "-".join(["%d"%(len(RS1_db_rels[k])) for k in stak]) 
        # 
        #     if False:
        #         s2 = '[%s]' % "-".join(["%d"%(len(RS2_ins[k])) for k in RS2_ins])
        #         s1 += '+'+s2
        #         s += [ "%-12s" % s3 ]

        if 'vol_id' in item_dict:
            fmt = "%%-%ds" % self.vol_id_width # "%-7s"
            s += [ fmt % item_dict['vol_id'] ]

        if 'NSFileSystemFolderNumber' in item_dict:     # really, if is NSDict or relation
            folder_id           = item_dict['NSFileSystemFolderNumber']
        else:
            folder_id           = item_dict['folder_id']

        file_id             = item_dict['NSFileSystemFileNumber']
        
        fmt = "%%%dd %%%dd" % (self.file_id_width , self.file_id_width)
        
        s += [ "%8d %8d" % (folder_id, file_id) ]


        # If the modification time of the file is more than 6 months
        #  in the past or future, then the year of the last modification
        #  is displayed in place of the hour and minute fields. [man ls]

        file_mod_date       = item_dict[NSURLContentModificationDateKey]
        
        # compare:
        # Returns an NSComparisonResult value that indicates the temporal ordering of the receiver and another given date.
        
        # date_six_months_ago = NSDate.dateWithTimeIntervalSinceNow_(0- 6 * 30 * 24 *60 * 60)
        date_six_months_ago = NSDate.dateWithTimeIntervalSinceNow_(0- 12 * 30 * 24 *60 * 60) # one year ago

        if False:  # ie, if doing short versions
            if date_six_months_ago.compare_(file_mod_date) == NSOrderedDescending: # ie, date_six_months_ago is later in time than file_mod_date
                format_string = self.date_format_short_early
                if format_string.endswith(" z"):
                    fmt = "%3s %15s"
                else:
                    fmt = "%3s %11s"
            else:
                format_string = self.date_format_short
                if format_string.endswith(" z"):
                    fmt = "%3s %15s"
                else:
                    fmt = "%3s %11s"
            # don't need to set format string for this formatter? each time through?
            NSDateFormatter.setDateFormat_(dateFormatters[0]['df'], format_string)
            sa                  =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)
            s += [ fmt % ( sa[0:3], sa[4:] ) ]
                    
        else:   # no difference for early or recent for long date format
            if date_six_months_ago.compare_(file_mod_date) == NSOrderedDescending:
                format_string = self.date_format_early
                fmt = "%19s"
            else:
                format_string = self.date_format            
                fmt = "%19s"
                
            # don't need to set format string for this formatter? each time through?
            NSDateFormatter.setDateFormat_(dateFormatters[0]['df'], format_string)
            sa                  =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)

            s += [ fmt % ( sa, ) ]

        depth               = item_dict['depth']
        filename            = item_dict[NSURLNameKey]

        if item_dict['NSURLIsDirectoryKey']:  
            filename += "/" 
        if 'directory_is_up_to_date' in item_dict:
            filename +=  ("(up-to-date)" if item_dict['directory_is_up_to_date'] else "(modified)" )

        file_uti = item_dict[NSURLLocalizedTypeDescriptionKey] # NSURLTypeIdentifierKey]
        if len(file_uti) > self.file_uti_width:
            n1 = int(self.file_uti_width/2)
            n2 = self.file_uti_width - n1
            file_uti = file_uti[:n1] +  u"—" + file_uti[-n2:]

        fmt = "%%-%ds" % ( self.file_uti_width  )
            
        s += [ fmt %  file_uti ]

        if depth_limit and depth >= depth_limit-1: 
            s += [ "%2d! %-54s" % (depth, filename) ]
        else:   
            s += [ "%2d %-54s" % (depth, filename) ]

        
        if GPR.verbose_level >= 2:
            print
        print " ".join(s)
        #print repr(s) # " ".join(s)
        if GPR.verbose_level >= 2:
            print

            

GPR = printstuff()     

from Foundation import NSDateFormatterFullStyle

def dateFromString(myDateAsAStringValue):
    df = NSDateFormatter.alloc().init()
    df.setTimeStyle_(NSDateFormatterFullStyle)  # <=== magic.  have to do this(?)
    df.setDateFormat_("yyyy-MM-dd HH:mm:ss") #"yyyy-MM-dd hh:mm:ss") # "2013-03-30 18:11:07"
    myDate = df.dateFromString_(myDateAsAStringValue)
    return myDate
    
if __name__ == '__main__':


    # print dateFromString("2013-03-30")  # 2013-03-30 18:11:07")
    
    fs_dict = {
        'NSFileSystemFileNumber':2,
        'NSFileSystemFolderNumber':1L,
        NSURLContentModificationDateKey:dateFromString("2013-03-30 18:11:07"),
        NSURLCreationDateKey:dateFromString("2011-07-02 21:02:54"),
        NSURLIsDirectoryKey:1,
        NSURLIsVolumeKey:1,
        NSURLLocalizedTypeDescriptionKey:'Volume',
        NSURLNameKey:'Genie',
        'NSURLPathKey':"/",
        'NSURLTotalFileSizeKey':0,
        NSURLTypeIdentifierKey:"public.volume",
        NSURLVolumeURLKey:"file://localhost/",
        'depth':-4
    }


    GPR.pr7z( fs_dict )

   #     1        2 Sat  3.30 18:11 EDT Volume               -4 Genie/                                                

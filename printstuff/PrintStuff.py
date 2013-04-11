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
from dates import dateFormatters, print_timezones

# global container for verbose_level, basically.  (soon to be more logging-like)
class PrintStuff(object):
    """docstring for PrintStuff"""
    
    def __init__(self, verbose_level=3):
        super(PrintStuff, self).__init__()
        self.verbose_level = verbose_level

    def print_dict(self, l, in_dict, left_col_width=24, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
            print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
            print
    
    def print_list(self, l, in_list, left_col_width=24, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            print l + ":"
            print
            s = "    %%%ss" % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
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
    
    def print_it(self, s, verbose_level_threshold):
        if self.verbose_level >= verbose_level_threshold:     
            try:
                print s
            except UnicodeDecodeError as e:
                print  repr(e[1])
                # print u"UnicodeDecodeError", repr(e[1])

    def print_it2(self, l, s, verbose_level_threshold):
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


        
    def pr7z(self,  item_dict,  RS1_db_rels=None,  RS2_ins=None, stak=None, depth_limit=None, verbose_level_threshold=1):
        """0-0      vol0006     5651     6227 Wed 2013.03.20 13:29 EDT  1 <filename>"""

        if self.verbose_level < verbose_level_threshold:    
            return
        
        # assemble a list of strings to print, then " ".join() then
        
        s = []

        if 'current_item_directory_is_being_checked' in item_dict:
            g = "[^]" if item_dict['current_item_directory_is_being_checked'] else "[-]"
            s += [g]
            
        if RS1_db_rels is not None:
            s0 = dict([(k, RS1_db_rels[k]) for k in RS1_db_rels] )# avoid self-creation
            s1 =  '[%s]' % "-".join([ "%d"%(len(s0[k])) if k in s0 else "*" for k in stak])
            s += [ "%-6s" % s1 ]

            # this line *creates* an entry since RS is a *default* dict and k isn't already present in RS            
            # s1 =  '[%s]' % "-".join(["%d"%(len(RS1_db_rels[k])) for k in stak]) 

            if False:
                s2 = '[%s]' % "-".join(["%d"%(len(RS2_ins[k])) for k in RS2_ins])
                s1 += '+'+s2
                s += [ "%-12s" % s3 ]

        if 'vol_id' in item_dict:
            s += [ "%-7s" % item_dict['vol_id'] ]

        if 'NSFileSystemFolderNumber' in item_dict:     # really, if is NSDict or relation
            folder_id           = item_dict['NSFileSystemFolderNumber']
        else:
            folder_id           = item_dict['folder_id']

        file_id             = item_dict['NSFileSystemFileNumber']
        s += [ "%8d %8d" % (folder_id, file_id) ]

        file_mod_date       = item_dict[NSURLContentModificationDateKey]
        sa                  =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)
        s += [ "%s" % ( sa) ]

        depth               = item_dict['depth']
        filename            = item_dict[NSURLNameKey]

        if item_dict['NSURLIsDirectoryKey']:  
            filename += "/" 
        if 'directory_is_up_to_date' in item_dict:
            filename +=  ("(up-to-date)" if item_dict['directory_is_up_to_date'] else "(modified)" )
            # s += [ "%-12s" % ("(up-to-date)" if item_dict['directory_is_up_to_date'] else "(new)" )]

        if depth_limit and depth >= depth_limit-1: 
            s += [ "%d! %-54s" % (depth, filename) ]
        else:   
            s += [ "%d %-54s" % (depth, filename) ]
        # s += [ "%d %-60s" % (depth, filename) ]

        file_uti            = item_dict[NSURLLocalizedTypeDescriptionKey] # NSURLTypeIdentifierKey]

        if len(file_uti) > 20:
            file_uti = file_uti[:9] +  u"—" + file_uti[-10:]
        s += [ "%-20s" %  file_uti ]
        
        print " ".join(s)
        print

            

GPR = PrintStuff()     

if __name__ == '__main__':


    fs_dict = {
        'NSFileSystemFileNumber':2,
        'NSFileSystemFolderNumber':1L,
        NSURLContentModificationDateKey:"2013-03-30 18:11:07 +0000",
        NSURLCreationDateKey:"2011-07-02 21:02:54 +0000",
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

    "       1        2 None -4 Genie/ public.volume"
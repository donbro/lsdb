#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
t_lsdb.py

    skeleton app to import and call basic lsdb functions.

Created by donb on 2013-04-08.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from Foundation import NSURL, \
                            NSDirectoryEnumerationSkipsPackageDescendants , \
                            NSDirectoryEnumerationSkipsHiddenFiles
                            # # NSURLIsPackageKey

from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey

from dbstuff.dbstuff import db_connect, db_select_vol_id, db_file_exists, db_query_folder, \
            do_db_delete_tuple, GetD, execute_update_query
from files import MyError , sharedFM
from files import   GetURLValues, is_item_a_package, error_handler_for_enumerator, is_a_directory
from lsdb.parse_args import do_parse_args
from printstuff.PrintStuff import GPR
from relations.relation_dict import relation_dict
from relations.relation import relation # , tuple_d  ## relations.relation.tuple_d


from lsdb.keystuff import databaseAndURLKeys, enumeratorURLKeys


# from module files import files_generator

#===============================================================================
# files_generator
#===============================================================================
def files_generator(basepath, options):
    """a generator which yields all files (as file_dicts) including volume, superfolder(s), 
            basepath, and then all subfiles (subject to depth_limit and enumerator options). """

    GPR.print_it2("gen for basepath", basepath, 2)

    superfolders_list = []
    
    basepath_url =  NSURL.fileURLWithPath_(basepath)
    
    # begin loop going upwards
    url =  NSURL.fileURLWithPath_(basepath)
    while True:
        d1 = GetURLValues(url, enumeratorURLKeys)
        superfolders_list.insert(0,d1)
        if d1[NSURLIsVolumeKey]: 
            break
        url = url.URLByDeletingLastPathComponent()              # go "upwards" one level (towards volume)

    GPR.print_superfolders_list("volume, superfolder(s)", superfolders_list, 4)

    # now go back down, yielding dict objects at each step:
    n = len(superfolders_list)
    for i, superfolder_dict in enumerate(superfolders_list):  
        superfolder_dict['depth'] = i+1-n
        yield superfolder_dict 

    basepath_dict =  superfolder_dict                           # last dict in superfolder list is the basepath_dict

    item_is_package = is_item_a_package(basepath_url)    
    if basepath_dict[NSURLIsDirectoryKey] and item_is_package and not options.scan_packages:
        GPR.print_it("\nbasepath is a directory and a package but we're not scanning packages.\n", 2)
        return

    enumeratorOptionKeys = 0L
    if not options.scan_packages:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
    if not options.scan_hidden_files:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles

    enumerator = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                                                                    basepath_url,   
                                                                                    enumeratorURLKeys, 
                                                                                    enumeratorOptionKeys, 
                                                                                    error_handler_for_enumerator )                                        
    for url in enumerator:
        item_dict = GetURLValues(url, enumeratorURLKeys)
        depth = enumerator.level()                
        item_dict['depth'] = depth

        if options.depth_limit and (depth >= options.depth_limit-1):
            enumerator.skipDescendants()
        
        yield item_dict




#===============================================================================
#       do_arg_gen
#===============================================================================

def vol_id_gen(cnx, in_gen):
    """processor for to find and add vol_id to each item as it goes by"""

    local_vol_id = None

    for in_dict in in_gen:
        if local_vol_id == None:
            local_vol_id = db_select_vol_id(cnx, in_dict)
            print "vol_id_gen", "%r, vol_id =%r" %  (in_dict[NSURLNameKey], local_vol_id) 

        in_dict['vol_id'] = local_vol_id

        yield in_dict
    
def files_stak_gen(in_gen, in_stak=[]):
    
    #   pre gen    

    (prev_depth, prev_folder_id) = (None, None)

    #   begin gen
    
    for in_dict in in_gen:
        depth           = in_dict['depth']
        folder_file_id  = in_dict['NSFileSystemFolderNumber']

        if depth >= 1 and prev_depth != depth:
            print "files_stak_gen",            
            if depth > prev_depth:
                print "*push* (%r => %r) "% (prev_depth, depth) , 
                in_stak.append((depth, folder_file_id))             # "sub stak says *append*"      
                print "%r"  %  in_stak                              # end of line
            else:
                while len(in_stak) > depth: #  and depth >= 0:
                    print " *pop* (%r => %r) "% (len(in_stak), len(in_stak)-1) , 
                    (d,ffid) = in_stak.pop()                         # "sub stak says *pop*"  
                    print "%r"  %  in_stak 

        (prev_depth, prev_folder_id) = (depth, folder_file_id)
        
        yield in_dict
        
    #   end gen

    # final pop back up to depth=0
    print "hey", "done with files_stak_gen. popping back to depth=0 from depth=%d and stak=%r" %(  in_dict['depth'] , in_stak)
    depth=0
    while len(in_stak) > depth:
        print "*pop* (%r => %r)" % ( len(in_stak), len(in_stak) -1  ) , 
        (d,ffid) = in_stak.pop()
        print "%r"  %  in_stak 
        # print "*popped* (%r => %r) %r "% ( len(in_stak)+1, len(in_stak) , (d,ffid) ) , 
        

def z_gen(in_gen):
    for x in in_gen:
        print "z_gen", # x ,
        yield x




class mySubStak(list):
    """subclass of list to hold RS1 and RS2 and do extra stuff on append() and pop()"""
    
    def __init__(self, arg=[]):
        super(mySubStak, self).__init__(arg)
        self.RS1 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))
        self.RS2 = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))    

    def append(self, arg):
        print "sub stak says *append*",
        super(mySubStak, self).append(arg)
                 
    def pop(self):
        print "sub stack says *pop*!",
        # if a directory simply wasn't stored in RS1 because database was empty, then we just skip it here.
        if len(self) > 0 and self[-1] in self.RS1.keys():
            if len(self.RS1[self[-1]]) > 0:
                print "(popped directory %r is not empty (%d))" % (self[-1], len(self.RS1[self[-1]]),)
                for rs in (self.RS1[self[-1]]):
                    print "pop", "delete", rs
            else:
                print "(popped directory %r is empty)" % (self[-1], ) ,

            del self.RS1[self[-1]]          
        
        res =  super(mySubStak, self).pop()

        return res

    def __repr__(self):
        """repr string looks like: "(2) [(1, 399) * , (2, 448) <13>]" """
 
        # self (ie, the list) can be longer than RS, RS can be longer than self
        # RS can have gaps in sequence of depth of keys, eg, (1,xx), (3, xx) 
        #   though RS shouldn't have two keys at any particular depth value
        
        len_self = len(self)
        len_max_RS = 0 if len(self.RS1.keys())==0 else max(self.RS1.keys())[0]
        mx = max(len_self, len_max_RS)  # ie, highest index we need to display

        s=[]
        for k in self:
            if k in self.RS1.keys():    
                s += [ "%r %d" % (k, len(self.RS1[k])) ]
            else:
                s += [ "%r * " % (k,  ) ]

        # we can have RS entry(s) that are beyond the stak, (at least in the value of depth)
        s += [ ( "%r <%d>" ) % (k, len(self.RS1[k]))  for k in self.RS1.keys() if k[0] > len_self]  
                    
        return "(%d) [%s]" % (mx , ", ".join(s))        


from functools import partial
    
def do_arg_gen(basepath, cnx, options):  
    
    x_gen = files_generator(basepath, options)
    
    my_stak = mySubStak() # contains self.RS1
        
    fs_gen = partial(files_stak_gen, in_stak=my_stak)  # keyword, not positional parameter
    
    y_gen = partial(vol_id_gen, cnx)

    for fs_dict in  y_gen( fs_gen( x_gen ) ):    

        folder_id = fs_dict['NSFileSystemFolderNumber']
        file_id = fs_dict['NSFileSystemFileNumber']
        depth = fs_dict['depth']
        
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
                if len(r)==0:
                    print "(database shows empty directory. don't store.)",
                else:
                    print "(storing at)" , (depth+1, file_id) ,
                    my_stak.RS1[ (depth+1, file_id)  ] =  r

                print "RS1", "%r" % (my_stak,),
                
            print #end-of-line


        # all items are checked/debited against the list of database contents.
        #  items which are not accounted for at the end of the directory in question (at pop) are deleted
        #   those that are present in filesystem but not in database.

        print "(current item)",

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
                print "(ignore)(already in database)" , fs_dict[NSURLNameKey].encode('utf8')
                continue
            except KeyError:
                to_be_inserted = True
                my_stak.RS2[ (depth,folder_id ) ] += rs       
                fs_dict['to_be_inserted'] = True
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
            
            print "(update directory)"
            yield fs_dict
            continue
            

        filename_utf8        = fs_dict[NSURLNameKey].encode('utf8')  

        print "(ignore)(container directory is up to date)" , filename_utf8
        continue

        #     
        # 
        # yield fs_dict


    #
    #   end gen
    #

    # final pop back up to depth=0
    print "hey", "done with do_arg_gen. my_stak is", my_stak
    

            


#===============================================================================
# do_args
#===============================================================================
# from collections import namedtuple  # namedtuple isn't a type, cant appear in isinstance() (?)
def do_args(args, options):
    """do_args is the high-level, self-contained routine most like the command-line invocation"""

    cnx = db_connect()
    
    # item_tally = defaultdict(list)  # initialize the item tallys here (kind of a per-connection tally?)

    try:
        for basepath in args:
            # RS1_db_rels = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   
            # RS2_ins = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   
            # stak = []
            
            for arg_dict in do_arg_gen(basepath, cnx, options):  
                if isinstance(arg_dict, tuple):
                    print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)24s %(file_name)s" % arg_dict._asdict()
                    print                    
                    do_db_delete_tuple(cnx, arg_dict, n=4)
                else:
                    GPR.pr7z( arg_dict ) 
                    d = GetD(arg_dict)
                    # print "inserting", d
                    d['vol_id'] = arg_dict['vol_id']
                    add_file_sql = ("insert into files "
                                    "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                                    "values "
                                    "( %(vol_id)s, %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, "
                                    "%(file_mod_date)s, %(file_uti)s ) "
                                    )
                    

                    # print "inserting", add_file_sql % d
                    # GPR.print_it(add_file_sql % d, 3)

                    # execute_update_query(cnx, add_file_sql , d, 4)
                    print
                    
                    # sys.exit()
                    
            

    except MyError, err:
        print err.description
    except KeyboardInterrupt:
        print "KeyboardInterrupt (hey!)"


    cnx.close()

#===============================================================================
# main
#===============================================================================
def main():

    #   some favorite testing files


    s = '/Volumes/Ulysses/bittorrent'
    s =     u'/Users/donb/Downloads/incomplete'
    s = '/Volumes/Ulysses/TV Shows/Nikita/'

    # package
    s = u"/Users/donb/Documents/Installing Evernote v. 4.6.2—Windows Seven.rtfd"

    s = u'/Users/donb/Ashley+Roberts/'

    s = '/Volumes/Ulysses/bittorrent'

    s = '.'

    s = '/Volumes/Ulysses/TV Shows/Nikita/'
    s = u'/Users/donb/Ashley+Roberts/'
    s = u'/Users/donb/Downloads/incomplete'
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        argv = []
        argv += ["-v"]
        argv += ["-v"]
        # argv = ["-d 3"]        
        # argv += ["-f"]          # force folder scan
        # argv += ["-p"]      # scanning packages
        argv += [s]
    else:
        argv = sys.argv[1:]
    

    (options, args) = do_parse_args(argv)
    
    # no args means do the current directory
    
    if args == []: 
        args = ["."]
    
    args = [os.path.abspath(os.path.expanduser(a)) for a in args]

    GPR.print_list("sys.argv", sys.argv)

    # display list of timezones
    if options.verbose_level >= 4:
        print_timezones("time_zones")

    GPR.print_dict("options (after optparsing)", options.__dict__, left_col_width=24, verbose_level_threshold=2)

    GPR.print_list("args (after optparsing)", args, verbose_level_threshold=3)
        
    do_args(args, options)

#===============================================================================
        
if __name__ == "__main__":
    main()

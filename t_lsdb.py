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
from files import   GetURLValues, is_item_a_package, error_handler_for_enumerator
from lsdb.parse_args import do_parse_args
from printstuff.PrintStuff import GPR
from relations.relation_dict import relation_dict
from relations.relation import relation # , tuple_d  ## relations.relation.tuple_d


from lsdb.keystuff import databaseAndURLKeys, enumeratorURLKeys


# from module files import files_generator

def files_generator(basepath, options):
    """return list of all files (as file_dicts) including volume, basepath, all subfiles. """

    GPR.print_it2("gen for basepath", basepath, 2)

    superfolders_list = []
    
    url =  NSURL.fileURLWithPath_(basepath)
    while True:
        d1 = GetURLValues(url, enumeratorURLKeys)
        superfolders_list.insert(0,d1)
        if d1[NSURLIsVolumeKey]: 
            break
        url = url.URLByDeletingLastPathComponent()                    # go "upwards" one level (towards volume)

    GPR.print_superfolders_list("volume, superfolder(s)", superfolders_list, 4)

    n = len(superfolders_list)
    for i, superfolder_dict in enumerate(superfolders_list):  
        superfolder_dict['depth'] = i+1-n
        yield superfolder_dict 

    basepath_url =  superfolder_dict['url'] # NSURL.fileURLWithPath_(basepath)

    item_is_package = is_item_a_package(basepath_url)    
    if superfolder_dict[NSURLIsDirectoryKey] and item_is_package and not options.scan_packages:
        GPR.print_it("\nbasepath is a directory and a package but we're not scanning packages.\n", 2)
        return
    

    enumeratorOptionKeys = 0L
    if not options.scan_packages:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsPackageDescendants
    if not options.scan_hidden_files:
        enumeratorOptionKeys |= NSDirectoryEnumerationSkipsHiddenFiles

    enumerator2 = sharedFM.enumeratorAtURL_includingPropertiesForKeys_options_errorHandler_(
                                        basepath_url,   enumeratorURLKeys, enumeratorOptionKeys, 
                                        error_handler_for_enumerator )
                                        
    for url in enumerator2:
        # print "url", url
        item_dict = GetURLValues(url, enumeratorURLKeys)
        depth = enumerator2.level()                
        item_dict['depth'] = depth
        # print depth, options.depth_limit-1, depth >= options.depth_limit-1
        if options.depth_limit and (depth >= options.depth_limit-1):
            enumerator2.skipDescendants()
        
        yield item_dict




#===============================================================================
#       do_args
#===============================================================================

# from relations.relation_dict import relation_dict



            
    
def files_vol_id(cnx, my_files_gen):
    """processor for to find and add vol_id to each item as it goes by"""
    
    vol_id = None
    for file_dict in my_files_gen:
        if vol_id == None:
            vol_id = db_select_vol_id(cnx, file_dict)
            GPR.print_it2("gen for files_vol_id, vol_id =%r" %  vol_id, 2)
        file_dict['vol_id'] = vol_id
        yield file_dict

global_dict_vol_id = None

def dict_vol_id(cnx, file_dict):
    """processor for to find and add vol_id to each item as it goes by"""
    global global_dict_vol_id
    if global_dict_vol_id == None:
        global_dict_vol_id = db_select_vol_id(cnx, file_dict)
        GPR.print_it2("gen for files_vol_id", "%r, vol_id =%r" %  (file_dict[NSURLNameKey], global_dict_vol_id), 2)
    file_dict['vol_id'] = global_dict_vol_id
    return global_dict_vol_id
    
    # yield file_dict

def vol_id_gen(in_gen, cnx):
    """processor for to find and add vol_id to each item as it goes by"""
    local_vol_id = None
    for in_dict in in_gen:
        print "y_gen", in_dict['NSURLPathKey'] ,
        if local_vol_id == None:
            local_vol_id = db_select_vol_id(cnx, in_dict)
            GPR.print_it2("gen for files_vol_id", "%r, vol_id =%r" %  (in_dict[NSURLNameKey], local_vol_id), 2)
        in_dict['vol_id'] = local_vol_id

        yield in_dict
    
def y_gen(in_gen):
    for x in in_gen:
        print "y_gen", x ,
        yield x

def z_gen(in_gen):
    for x in in_gen:
        print "z_gen", # x ,
        yield x
    
def do_arg_gen(basepath, RS1_db_rels, RS2_ins, stak, cnx, options):
    
    x_gen = files_generator(basepath, options)

    def y_gen(x_gen):
         for z in vol_id_gen(x_gen, cnx):
             yield z

    for x in  z_gen( y_gen( x_gen ) ) :    
    # for x in  z_gen( y_gen( x_gen , cnx ) ) :    
        yield x

    return 
    
            
    my_previous_depth_folder_id = (None, None)
    
    my_files_gen = files_generator(basepath, options)
    
    for fs_dict in my_files_gen:
        yield fs_dict
        continue
        
        # this also updates fs_dict with vol_id (as "it goes by")
        vol_id =  dict_vol_id(cnx, fs_dict)

        depth             = fs_dict['depth']
        folder_id         = fs_dict['NSFileSystemFileNumber']

        if  my_previous_depth_folder_id != (depth, folder_id):
            my_previous_depth = my_previous_depth_folder_id[0]
            my_previous_folder_id = my_previous_depth_folder_id[1]
            if depth > my_previous_depth:
                print "push (%r => %r) "% (my_previous_depth, depth)
            elif depth == my_previous_depth:  # thus, folder_ids are different
                print "same"
                # end of previous folder.  check to see if we had any records stored there
                if (my_previous_depth,my_previous_folder_id) in RS1_db_rels:
                    print "yes! there are some!"
            else:
                print "POP (%r => %r) "% (my_previous_depth, depth)
                    
            #          and len(RS1_db_rels[ (d,ffid) ]) > 0:
            # 
            # 
            #     and depth <= my_arg_current_depth_folder_id[0]:
            # print "current_depth is equal to or less (pop) %r != (%d, %d)" % (my_arg_current_depth_folder_id,depth, folder_id)

        # here's where we would/could/have to acknowledge that a folder's processing is finished
        #  so we should yield up the results of the difference; its ready, the folder won't be seen again(??)
        #  the differences, here are those records seen in the database that didn't show up in the filesystem
        #  thus enough of a database key to delete.
        
            # even if we don't "pop" we might still have be moving to a new directory at the same level
            #  thus we should check to see if we have an entry in RS1
            
            # (d,ffid) = my_arg_current_depth_folder_id # previous depth and folder_id at this point, actually.
            # if (d,ffid) in RS1_db_rels and len(RS1_db_rels[ (d,ffid) ]) > 0:
            #     print "prev_is_different", (d,ffid) , "len=", len(RS1_db_rels[ (d,ffid) ]), RS1_db_rels[ (d,ffid) ]
            #     for t in RS1_db_rels[ (d,ffid) ]:
            #         # print t._asdict()
            #         print "delete", "          ",
            #         # print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)s %(file_name)s" % t._asdict()
            #         yield t

        while len(stak) > depth and depth >= 0:
            (d,ffid) = stak.pop()
            print "pop", (d,ffid), "len=", len(RS1_db_rels[ (d,ffid) ]) 
            if len(RS1_db_rels[ (d,ffid) ]) > 0:
                print "pop", (d,ffid) , "len=", len(RS1_db_rels[ (d,ffid) ]), RS1_db_rels[ (d,ffid) ]
                for t in RS1_db_rels[ (d,ffid) ]:
                    # print t._asdict()
                    print "delete", "          ",
                    # print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)s %(file_name)s" % t._asdict()
                    yield t

                    # no continue, this(these) yield(s) aren't made of this item, just triggered by this item (this item's level) 

        my_previous_depth_folder_id = (depth, folder_id)

        
        # step xxx

        url = fs_dict['url']
        item_is_package = is_item_a_package(url)
        if fs_dict[NSURLIsDirectoryKey] and ((not item_is_package) or options.scan_packages):
        
            file_exists = not options.force_folder_scan and db_file_exists(cnx, fs_dict, vol_id)
            fs_dict['directory_is_up_to_date'] = file_exists                  

            if not fs_dict['directory_is_up_to_date']:
                # folder_id         = fs_dict['NSFileSystemFileNumber']
                if depth >= 0:
                    r = db_query_folder(cnx,  vol_id,  fs_dict, depth)
                    RS1_db_rels[ (depth, folder_id) ] =  r

            folder_file_id = fs_dict['NSFileSystemFileNumber']            
            if depth >= 0:
                stak.append((depth, folder_file_id))

        # step yyy

        folder_id = fs_dict['NSFileSystemFolderNumber']
        fs_dict['current_item_directory_is_being_checked'] =  (depth-1, folder_id) in RS1_db_rels

        if fs_dict['current_item_directory_is_being_checked'] :
            file_id         = fs_dict['NSFileSystemFileNumber']
            filename        = fs_dict[NSURLNameKey].encode('utf8')  

            file_mod_date   = fs_dict[NSURLContentModificationDateKey]
            s = str(file_mod_date)
            file_mod_date = s[:-len(" +0000")]
            rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)

            # if the current item is present in RS1 then it is no longer a "file to be deleted"
            # if in filesystem but not in database then it is a "file to be inserted"

            to_be_inserted = False        
            try:                
                RS1_db_rels[ (depth-1, folder_id) ] -= rs       
            except KeyError:
                to_be_inserted = True
                RS2_ins[ (depth-1, folder_id) ] += rs       

        # step zzz

        # a directory that needed to be scanned could just be a new, not a modified, directory.
        # so check for new, before modified directory?
        
        if fs_dict[NSURLIsDirectoryKey] and ((not item_is_package) or options.scan_packages)\
                        and not fs_dict['directory_is_up_to_date']:
            print "update",
            yield fs_dict
        elif fs_dict['current_item_directory_is_being_checked'] and to_be_inserted:
            print "new   ",
            yield fs_dict
        else:
            # really, want this to be a part of verbosity 3 and above?
            # print "ignored", fs_dict[NSURLNameKey]
            pass

    # final pop back up to depth=0
    depth=0
    while len(stak) > depth and depth >= 0:
        (d,ffid) = stak.pop()
        if len(RS1_db_rels[ (d,ffid) ]) > 0:
            # print "pop", (d,ffid) , "len=", len(RS1_db_rels[ (d,ffid) ]), RS1_db_rels[ (d,ffid) ]
            for t in RS1_db_rels[ (d,ffid) ]:
                print "delete", "          ",
                yield t

            
def rel_tallys(RS1_db_rels, RS2_ins):
    nz = [rel for k, rel in RS1_db_rels.items() if len(rel) > 0]
    if nz == []:
        print "RS1_db_rels (No items to be deleted from database)", "\n"
    else:
        print "RS1_db_rels (to be deleted from database)"
        
        for rel in nz:
            for t in rel:
                # print t._asdict()
                print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)s %(file_name)s" % t._asdict()
        # print
        # print [rel for k, rel in RS1_db_rels.items() if len(rel) > 0]
        # print

    print "RS2 (files to be inserted into database)", "\n"
    nz2 = [rel for k, rel in RS2_ins.items() if len(rel) > 0]

    for rel in nz2:
        for t in rel:
            # print t._asdict()
            print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)s %(file_name)s" % t._asdict()

#===============================================================================
# do_args
#===============================================================================
from collections import namedtuple
def do_args(args, options):
    """do_args is the high-level, self-contained routine most like the command-line invocation"""

    cnx = db_connect()
    
    # item_tally = defaultdict(list)  # initialize the item tallys here (kind of a per-connection tally?)

    try:
        for basepath in args:
            RS1_db_rels = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   
            RS2_ins = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))   
            stak = []
            
            for arg_dict in do_arg_gen(basepath, RS1_db_rels, RS2_ins, stak, cnx, options):
                if isinstance(arg_dict, tuple):
                    print "%(vol_id)7s %(folder_id)8s %(file_id)8s %(file_mod_date)24s %(file_name)s" % arg_dict._asdict()
                    print                    
                    do_db_delete_tuple(cnx, arg_dict, n=4)
                else:
                    GPR.pr7z( arg_dict, RS1_db_rels, RS2_ins, stak=stak, depth_limit=options.depth_limit )
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

                    execute_update_query(cnx, add_file_sql , d, 4)
                    print
                    
                    # sys.exit()
                    
            
            # rel_tallys(RS1_db_rels, RS2_ins)
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
    s = '/Volumes/Ulysses/TV Shows/Nikita/'
    s = '.'
    s = u'/Users/donb/Ashley+Roberts/'
    # package
    s = u"/Users/donb/Documents/Installing Evernote v. 4.6.2—Windows Seven.rtfd"
    s = u'/Users/donb/Ashley+Roberts/'
    s = u'/Users/donb/Downloads/incomplete'
    s = '.'

    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        argv = []
        argv += ["-v"]
        argv += ["-v"]
        # argv = ["-d 3"]        
        argv += ["-f"]          # force folder scan
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

    GPR.print_list("args (after optparsing)", args)
        
    do_args(args, options)

#===============================================================================
        
if __name__ == "__main__":
    main()

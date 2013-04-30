#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
    lsdb.py
    
    filesystem, library files and database multitool.
    

usage: lsdb.py [-h] [-r] [-v] [-q] [-d DEPTH] [-f] [-p] [-a]
    -h, --help            show this help message and exit
    -r              recursive listing of directories, trees or graphs held in filesystem, file, or database.

    -d, --depth n      limit depth to n levels.  n=0 is do only argument as single node, no recursion.

    --force-folder-scan
        Normal operation is, when comparing, for example, filesystem to database, 
        to take into account timestamps (or other characteristics) of corresponding nodes 
        and to consider nodes with equal timestamps to be equal in content. 
        If this option is present, do not perform this optimization
        and compare the contents of all nodes without consideration of summary characteristics.
    
    
    This module is the skeleton for the command line invocation of the lsdb functions.  Database, filesystem,
    and other functions are imported from their respective packages.
    

Created by donbro@mac.com on 2013-04-08.
Copyright (c) 2013 donbro@mac.com All rights reserved.
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
# print "\n".join( sys.path)
# sys.exit()

from dbstuff.dbstuff import db_connect, db_select_vol_id, db_file_exists, db_query_folder, \
             GetD, execute_update_query  # do_db_delete_tuple,
from files import MyError , sharedFM
from files import   GetURLValues, is_item_a_package, error_handler_for_enumerator, is_a_directory
from lsdbstuff.keystuff import enumeratorURLKeys, databaseAndURLKeys
from lsdbstuff.parse_args import do_parse_args
from printstuff.printstuff import GPR
from relations.relation_dict import relation_dict
# from relations.relation import relation # , tuple_d  ## relations.relation.tuple_d

# from module files import files_generator

#===============================================================================
# files_generator
#===============================================================================
def files_generator(basepath, options):
    """a generator which yields all files (as file_dicts) including volume, superfolder(s), 
            basepath, and then all subfiles (subject to depth_limit and enumerator options). """

    GPR.print_it25("files_generator", basepath, 3)

    superfolders_list = []
    
    basepath_url =  NSURL.fileURLWithPath_(basepath)
    
    # begin loop going upwards
    url =  NSURL.fileURLWithPath_(basepath)
    while True:
        d1 = GetURLValues(url, enumeratorURLKeys)
        superfolders_list.insert(0,d1)
        if d1[NSURLIsVolumeKey]: 
            break
        # go "upwards" one level (towards volume)
        url = url.URLByDeletingLastPathComponent()              

    GPR.print_superfolders_list("volume, superfolder(s)", superfolders_list, 4)

    # now go back down, yielding dict objects at each step:
    n = len(superfolders_list)
    for i, superfolder_dict in enumerate(superfolders_list):  
        superfolder_dict['depth'] = i+1-n
        yield superfolder_dict 

    # last dict in superfolder list is the basepath_dict
    basepath_dict =  superfolder_dict                          

    item_is_package = is_item_a_package(basepath_url)    
    if basepath_dict[NSURLIsDirectoryKey] and item_is_package and not options.scan_packages:
        GPR.print_it("\nbasepath is a directory and a package but we're not scanning packages.\n", 2)
        return

    # we've yielded basepath above, don't enumerate if basepath is not a directory (or package and we want packages)
    
    if basepath_dict[NSURLIsDirectoryKey]:
    
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


    GPR.print_it2("end files_generator", basepath, verbose_level_threshold=3)


#===============================================================================
#       do_arg_gen
#===============================================================================

def vol_id_gen(cnx, in_gen):
    """processor for to find, store and then add vol_id to each item as it goes by"""
    
    # try:
    #   select vol_id from volumes_uuid (based on volume uuid)
    #   select vol_id from files (based on volume name and create date)
    #   do a "test" insert of the volume entry just to get the autocreated vol_id back. (then act like it didn't happen :)

    local_vol_id = None

    for in_dict in in_gen:
        
        if local_vol_id == None:
            volume_url = in_dict['url']
            values, error =  volume_url.resourceValuesForKeys_error_( ['NSURLVolumeUUIDStringKey',
                                                                'NSURLVolumeTotalCapacityKey',
                                                                'NSURLVolumeAvailableCapacityKey',
                                                                'NSURLVolumeSupportsVolumeSizesKey'] , None )
            
            select_query = ( "select  vol_id  from volume_uuids "
                                "where  vol_uuid = %r" % str(values['NSURLVolumeUUIDStringKey'])
                                )

            cursor = cnx.cursor()
            GPR.print_it(select_query, 3)
            cursor.execute( select_query )    
            r = [z for z in cursor] 
            if len(r) > 0:
                local_vol_id = r[0][0]
            
            # need to also update (roundtrip) the volume_uuid table with latest capacity, etc., data?
            #  but not until we have found/created the vol_id...
            
        if local_vol_id == None:

            local_vol_id = db_select_vol_id(cnx, in_dict)
            GPR.print_it2("vol_id_gen", "volume = %s, vol_id = %s" %  (in_dict[NSURLNameKey], local_vol_id), verbose_level_threshold=3)

        in_dict['vol_id'] = local_vol_id

        yield in_dict

    GPR.print_it("end vol_id_gen.", verbose_level_threshold=3)


class stak(list):
    """subclass of list to hold RS and do extra stuff on append() and pop()"""
    
    def __init__(self, arg=[]):
        super(stak, self).__init__(arg)
        self.RS = relation_dict(heading = ('vol_id' , 'folder_id' , 'file_name' , 'file_id' , 'file_mod_date'))

    def __repr__(self):
        """repr string looks like: "(2) [(1, 399) * , (2, 448) <13>]" """
        
        if False and len(self.RS) == 0:
            return super(stak, self).__repr__()
        #else:

        # self (ie, the list) can be longer than RS, RS can be longer than self
        # RS can have gaps in sequence of depth of keys, eg, (1,xx), (3, xx) 
        #   though RS shouldn't have two keys at any particular depth value
        
        len_self = len(self)
        len_max_RS = 0 if len(self.RS.keys())==0 else max(self.RS.keys())[0]
        mx = max(len_self, len_max_RS)  # ie, highest index we need to display

        s=[]
        for k in self:
            if k in self.RS.keys():    
                s += [ "%r %d" % (k, len(self.RS[k])) ]
            else:
                s += [ "%r * " % (k,  ) ]

        # we can have RS entry(s) that are beyond the stak, (at least in the value of depth)
        s += [ ( "%r <%d>" ) % (k, len(self.RS[k]))  for k in self.RS.keys() if k[0] > len_self]  
                    
        return "(%d) [%s]" % (mx , ", ".join(s))
        
def do_db_delete_tuple(cnx, rs, n=3):
        
        rel_dict =   dict(zip( ("vol_id", "folder_id", "file_name", "file_id", "file_mod_date") , rs ))  
        rel_dict["file_name"] = str(rel_dict["file_name"].encode('utf8'))
        rel_dict["vol_id"] = str(rel_dict["vol_id"].encode('utf8'))

        update_sql = ("update files "
                        " set files.folder_id =  0 "
                        " where files.vol_id  =      %(vol_id)s "
                        " and files.folder_id =      %(folder_id)s "
                        " and files.file_name =      %(file_name)s " 
                        " and files.file_id =        %(file_id)s " 
                        " and files.file_mod_date =  %(file_mod_date)s " 
                        ) 

        # print update_sql % d

        # sql_dict = GetDR(arg_dict, required_fields)

        # execute_update_query(cnx, update_sql , d, verbose_level_threshold=n)
        execute_update_query(cnx, update_sql , rel_dict, label='pop delete', verbose_level_threshold=n)
        sys.exit()

from collections import defaultdict
def files_stak_gen(in_gen, in_stak=[], cnx=None):
    
    # this generator could yields a relation (namedtuple) but 
    # it wouldn't be able to be indexed like a dict, etc.
    #  A better solution to just do the delete here rather than 
    # yield something that is so different from the ususal dict 
    # taht it would just require special case code for the rest of the way anyway?
    # but we *could* yield a tuple or a conversion of the tuple here.  that's the
    # point of having this code in the generator.
    
    tally = defaultdict(int)
    
    def do_push(in_value):
        """(push) (2 => 3) [(1, 40014149), (2, 42755279), (3, 45167012)]"""
        
        (depth, folder_file_id) = in_value
        # test for push of something other than just one.  shouldn't happen.
        if prev_depth != len(in_stak):
            GPR.print_it1( "(push) prev_depth (%d) != len(in_stak) (%d)\n" %  (prev_depth, len(in_stak)) )
        GPR.print_it0( "(push) (%r" % (prev_depth,) )
        in_stak.append(in_value)
        GPR.print_it0( "=> %r)" % (  depth) )
        GPR.print_it1( "%r"  %  in_stak                             )
        GPR.print_it1( "" )
        tally["(push)"] +=1
        
    def do_pop():
        """ (pop) (3 => 2)  [(1, 40014149), (2, 42755279)]"""

        # test for pop of something other than just one. can happen.  is okay:)
        if   depth+1 != len(in_stak):
            GPR.print_it1( " (pop) depth+1 (%d) != len(in_stak) (%d)\n" %  (depth+1, len(in_stak)) )

        GPR.print_it0( " (pop) (%r"% (len(in_stak), ) )
        tally["(pop)"] +=1

        (d,ffid) = in_stak.pop()
        GPR.print_it0( "=> %r) "% (len(in_stak), ) )

        if hasattr(in_stak, 'RS'):
            if (d,ffid) in in_stak.RS: # in_stak.RS.keys():
                GPR.print_it0( "key %r in stak: %r" % ((d,ffid), in_stak) )
                GPR.print_it1( "(dict)")
                GPR.print_it1("")
                return in_stak.RS.pop((d,ffid))   # in_stak.RS[(d,ffid)]
            else:
                # not error, directory was up to date(?)
                GPR.print_it1( "key %r not in stak: %r" % ((d,ffid), in_stak) ) 
                GPR.print_it1("")
                return []
        else:
            GPR.print_it0( "in_stak has no attr 'RS'" )
            GPR.print_it1( "%r"  %  in_stak )
            GPR.print_it1("")
            return []


    #   pre gen    

    (prev_depth, prev_folder_id) = (None, None)

    #   begin gen
    
    for in_dict in in_gen:
        depth           = in_dict['depth']
        folder_file_id  = in_dict['NSFileSystemFolderNumber']

        if depth >= 1 and prev_depth != depth:
            if depth > prev_depth:
                # push
                do_push( (depth, folder_file_id) )
            elif depth < prev_depth:
                # pop
                while len(in_stak) > depth:
                    stak_RS_d = do_pop()
                    for rs in stak_RS_d:
                        print "pop", "delete", rs
                        do_db_delete_tuple(cnx, rs, n=2)                        
                        tally["(pop delete)"] +=1                    

        (prev_depth, prev_folder_id) = (depth, folder_file_id)

        tally["files"] +=1
        yield in_dict
    
    #   end gen

    depth=0
    while len(in_stak) > depth:
        stak_RS_d = do_pop()
        for rs in stak_RS_d:
            print "pop", "delete", rs
            do_db_delete_tuple(cnx, rs, n=2)                        
            tally["(pop delete)"] +=1

    if GPR.verbose_level in [1,2]:
        print "\n".join(["%6d: %s" % (v, k) for (k, v) in sorted(tally.items())])
    elif GPR.verbose_level >= 3:
        print "end files_stak_gen:\n", "\n".join(["%6d: %s" % (v, k) for (k, v) in sorted(tally.items())])


from functools import partial
    
def do_arg_gen(basepath, cnx, options):  
    
    x_gen = files_generator(basepath, options)

    my_stak = stak() # contains self.RS

    fs_gen = partial(files_stak_gen, in_stak=my_stak, cnx=cnx) 

    y_gen = partial(vol_id_gen, cnx)

    # for fs_dict in  y_gen( fs_gen( x_gen ) ):    
    for fs_dict in  fs_gen( y_gen( x_gen ) ):    
    
        depth = fs_dict['depth']
        file_id = fs_dict['NSFileSystemFileNumber']

        if is_a_directory(fs_dict, options):
            GPR.print_it0( "(directory)" )
            if (depth < 0 ):
                GPR.print_it1( "(depth < 0)" )  # eol
            else:
                # first need of database connection
                dir_is_up_to_date = not options.force_folder_scan and db_file_exists(cnx, fs_dict) 
                fs_dict['directory_is_up_to_date'] = dir_is_up_to_date                  
                if (dir_is_up_to_date   ):
                    GPR.print_it1( "(up_to_date)" )  # eol
                else:
                    GPR.print_it0( "(to_be_scanned)" )
                    GPR.print_it0( "(scanning)" )
                    r = db_query_folder(cnx, fs_dict)
                    GPR.print_it0( "(len=%r)" % (len(r),) )
                    GPR.print_it0( "(storing at)" , (depth+1, file_id) )
                    # don't store those of zero length because you'll never pop them?  no:
                    #   do store zero lengths because we will want to "subtract against them" in directory check.
                    my_stak.RS[ (depth+1, file_id)  ] =  r
                    GPR.print_it1( "stak: %r" % (my_stak,) ) # eol

        folder_id = fs_dict['NSFileSystemFolderNumber']

        fs_dict['current_item_directory_is_being_checked'] =  (depth, folder_id) in my_stak.RS
        if fs_dict['current_item_directory_is_being_checked']:          
            GPR.print_it0( "(check against container directory %r)" % ((depth,folder_id ) ,) , verbose_level_threshold=3)
            vol_id = fs_dict['vol_id']
            filename        = fs_dict[NSURLNameKey] # .encode('utf8')              # comparing to database return use unicode, for *insert* use utf8. (?)
            file_mod_date   = fs_dict[NSURLContentModificationDateKey]
            s = str(file_mod_date)
            file_mod_date = s[:-len(" +0000")]
            rs = (  vol_id,   folder_id,  filename,  file_id, file_mod_date)

            required_fields =  ['vol_id', 'folder_id', 'file_name', 'file_id', 'file_mod_date' ]

            sql_dict = GetDR(fs_dict, required_fields)
            
            r_file_name =  [r.file_name for r in my_stak.RS[ (depth,folder_id ) ] ][0]
            print
            print "stak %r" % (r_file_name, ) , "filename %r" % filename , r_file_name == filename
            
            print
            print [r  for r in my_stak.RS[ (depth,folder_id ) ] ][0]
            print rs
            print
            try:                
                my_stak.RS[ (depth,folder_id ) ] -= rs       
                GPR.print_it0( "(ignore)" )
                GPR.print_it0( "(already in database) %r" % my_stak )
            except KeyError:
                fs_dict['to_be_inserted'] = True
                fs_dict['sql_action'] = "insert"
                GPR.print_it0( "(insert)" )

        yield fs_dict

    #   end gen

    if options.verbose_level >= 3:
        print "end do_arg_gen. my_stak is", my_stak



#===============================================================================
# do_args
#===============================================================================

from Foundation import NSDateFormatter, NSDateFormatterFullStyle

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

db_df = NSDateFormatter.alloc().init()
db_df.setTimeStyle_(NSDateFormatterFullStyle)  # <=== magic.  have to do this(?)
db_df.setDateFormat_("yyyy-MM-dd HH:mm:ss") #"yyyy-MM-dd hh:mm:ss") # "2013-03-30 18:11:07"
# need to set time zone in above?

def GetDR(item_dict, required_fields):
    """Convert from item_dict (Cocoa) forms to database-ready forms"""

    # similar to mysql-connector's "_%s_to_mysql" but some here are special to the NS forms
    # 'vol_id', 'folder_id', 'file_name', 'file_id', 'file_size', 'file_create_date', 'file_mod_date', 'file_uti'

    
    result_dict = {}
    # print
    for db_field_name in required_fields:
        try:
            db_field_name_index = map( lambda y: y[0], databaseAndURLKeys).index(db_field_name)
            dict_key_name = databaseAndURLKeys[db_field_name_index][1]
        except ValueError:
            dict_key_name = db_field_name            

        # print  "%16s => %-36s :" % (db_field_name,  dict_key_name),
        
        #   do special processing based on database field name, not on inherent type of argument?
            
        if db_field_name in ['vol_id', 'file_name', 'file_uti']:
            c = item_dict[dict_key_name].encode('utf8')
            result_dict[db_field_name] =  quote(escape(c))
            # GPR.print_it1  ( result_dict[db_field_name]  ) # %s for already string?
            
        elif db_field_name in ['file_create_date', 'file_mod_date']:
            
            c = str(db_df.stringFromDate_(item_dict[dict_key_name]))
            result_dict[db_field_name] = quote(escape(c))
            # GPR.print_it1  ("%s" % (result_dict[db_field_name]) ) # %s for already string?

        elif db_field_name in ['file_size', 'file_id', 'folder_id']: # 
            
            result_dict[db_field_name] =  int(item_dict[dict_key_name])
            # GPR.print_it1  ("%s" % (result_dict[db_field_name]) ) # %s for already string?

        else:
            result_dict[db_field_name] =  item_dict[dict_key_name]
            # GPR.print_it1  ("%r" % (result_dict[db_field_name]) ) # %s for already string?

            
        
    # for dk, fk in databaseAndURLKeys:
    #     if dk:
    #         if fk in [NSURLNameKey, NSURLTypeIdentifierKey]:
    #             d[dk] =  item_dict[fk].encode('utf8')
    #         elif dk in ['file_create_date', 'file_mod_date']:
    #             d[dk] =  str(item_dict[fk])[:-len(" +0000")] # "2011-07-02 21:02:54 +0000" => "2011-07-02 21:02:54"
    #         elif  type(item_dict[fk]) == objc._pythonify.OC_PythonLong:
    #             # print """"type(item_dict[fk]) = objc._pythonify.OC_PythonLong""", item_dict[fk], int(item_dict[fk]) 
    #             d[dk] = int(item_dict[fk])
    #         # elif 'objc._pythonify.OC_PythonLong' in str(type(item_dict[fk])):
    #         #     print """"nscfnumber" in str(type(item_dict[fk]):""", item_dict[fk], int(item_dict[fk]), objc._pythonify.OC_PythonLong
    #         #     d[dk] = int(item_dict[fk])
    #         else:
    #             # print type(item_dict[fk])                
    #             d[dk] =  item_dict[fk]

    GPR.print_dict("GetDR", result_dict, 32, 2) # 4)

    return result_dict
import sqlparse
def do_args(args, options):
    """do_args is the high-level, self-contained routine most like the command-line invocation"""

    cnx = db_connect()
    
    # item_tally = defaultdict(list)  # initialize the item tallys here (kind of a per-connection tally?)
    required_fields =  ['vol_id', 'folder_id', 'file_name', 'file_id', 'file_size', 'file_create_date', 'file_mod_date', 'file_uti' ]

    try:
        for basepath in args:
            
            for arg_dict in do_arg_gen(basepath, cnx, options):  

                if (arg_dict['depth'] <= 0):
                    GPR.pr7z( arg_dict ) 
                elif 'sql_action' in arg_dict:
                    d = GetD(arg_dict)
                    sql_dict = GetDR(arg_dict, required_fields)

                    # sql_dict['vol_id'] = arg_dict['vol_id']
                    if arg_dict['sql_action'] in  ["update_directory", "insert"]:
                        add_file_sql = ("insert into files "
                                        "(vol_id, folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                                        "values "
                                        "( %(vol_id)s, %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, "
                                        "%(file_mod_date)s, %(file_uti)s ) "
                                        )
                        execute_update_query(cnx, add_file_sql , sql_dict, label=arg_dict['sql_action'], verbose_level_threshold=2)  # sql and dict are "%"'ed inside function
                    else:
                        GPR.print_it(add_file_sql % d, 3)
                                                            
                    GPR.pr7z( arg_dict ) 
                        
                else:
                    
                    GPR.pr7z( arg_dict ) 
                    # print
                
                    
            

    except MyError, err:
        print err.description
    except KeyboardInterrupt:
        print "KeyboardInterrupt (hey!)"


    cnx.close()

#===============================================================================
# main
#===============================================================================
from dates import  print_timezones

def main():

    #   some favorite testing files


    s = '/Volumes/Ulysses/bittorrent'
    s =     u'/Users/donb/Downloads/incomplete'
    s = '/Volumes/Ulysses/TV Shows/Nikita/'

    # package
    s = u"/Users/donb/Documents/Installing Evernote v. 4.6.2—Windows Seven.rtfd"


    s = '/Volumes/Ulysses/bittorrent'


    s = '/Volumes/Ulysses/TV Shows/Nikita/'
    s = u'/Users/donb/Downloads/incomplete'


    s = '/Volumes/Ulysses/TV Shows/Nikita/'
    s = u'/Users/donb/Ashley+Roberts/'
    s = '.'
    
    

    s = u"~/Catherine Video Review.mp4"
    s = u'/Users/donb/Ashley+Roberts/'
    s = "/Volumes/Brandywine/TV Show—single/"
    
    
    s = "/Volumes/Taos/videogame/"
    
    s = "/Volumes/Taos/videogame/Perfect Dark/Joanna Dark/"
    
    # hack to have Textmate run with hardwired arguments while command line can be free…
    if os.getenv('TM_LINE_NUMBER' ):
        argv = []

        argv += ["-v"] # verbose_level = 2
        argv += ["-v"]
        # argv += ["-v 4"]  # verbose_level = 4
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
    
    args2 = []
    for a in args:
        try:
            unicode(a)
        except UnicodeDecodeError:
            a2 = a.decode('utf8')
            # print "arg [  %s  ] is a unicode string" % (a2, )
            GPR.print_it2("arg is a unicode string", a2, verbose_level_threshold=1)
            args2.append(a2)
        else:
            args2.append(a)
    args = args2
        
    args = [os.path.abspath(os.path.expanduser(a)) for a in args]
    
    GPR.verbose_level = options.verbose_level

    GPR.print_list("sys.argv", sys.argv, verbose_level_threshold=3)

    # display list of timezones
    if options.verbose_level >= 4:
        print_timezones("time_zones")

    GPR.print_dict("options (after optparsing)", options.__dict__, left_col_width=24, verbose_level_threshold=2)

    GPR.print_list("args (after optparsing)", args, verbose_level_threshold=3)
        
    do_args(args, options)

#===============================================================================
        
if __name__ == "__main__":
    main()

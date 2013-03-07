#!/usr/bin/env python
# encoding: utf-8
"""
test_relation_and_files.py

Created by donb on 2013-02-27.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import unittest



def print_dict_tall_z(l, in_dict, left_col_width=24):

        print l + ":"
        print
        s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
        print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
        print

 
class relation_TestCase( unittest.TestCase ):
    """ Class to test relation and files """
    
    def test_0700_relation(self):
        
        from files import databaseAndURLKeys, enumeratorURLKeys, \
                    GetNSFileAttributesOfItem, GetURLResourceValuesForKeys, pdt, NSURL

        # d = GetNSFileAttributesOfItem("/")
        # l = 'GetNSFileAttributesOfItem("/")'
        # pdt(l, d, 28)

        url =  NSURL.fileURLWithPath_("/")

        item_dict = GetURLResourceValuesForKeys(url, enumeratorURLKeys)
        item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories
        
        # print_dict_tall_z("item_dict", item_dict, 32 )
        
        #              NSURLIsDirectoryKey: 1 
        #  NSURLContentModificationDateKey: 2013-02-20 10:10:12 +0000 
        #                     NSURLNameKey: u'Genie' 
        #         NSFileSystemFolderNumber: 1L 
        #           NSURLTypeIdentifierKey: u'public.volume' 
        #                 NSURLIsVolumeKey: 1 
        #                NSURLVolumeURLKey: file://localhost/ 
        #             NSURLCreationDateKey: 2011-07-02 21:02:54 +0000 
        #            NSURLTotalFileSizeKey: 0 
        #                     NSURLPathKey: u'/' 
        #           NSFileSystemFileNumber: 2 
        # NSURLLocalizedTypeDescriptionKey: u'Volume' 
        
                 
        # Convert from item_dict (Cocoa) forms to something that the database DBI can convert from

        from Foundation import NSURLNameKey, NSURLTypeIdentifierKey
        d = {}
        for dk, fk in databaseAndURLKeys:
            if dk:
                if fk in [NSURLNameKey, NSURLTypeIdentifierKey]:
                    d[dk] =  item_dict[fk].encode('utf8')
                elif dk in ['file_create_date', 'file_mod_date']:
                    d[dk] =  str(item_dict[fk])[:-len(" +0000")]
                else:
                    d[dk] =  item_dict[fk]

        print_dict_tall_z("insert data", d, 32 )

        # insert data:
        # 
        #                        folder_id: 1L 
        #                          file_id: 2 
        #                        file_size: 0 
        #                 file_create_date: '2011-07-02 21:02:54' 
        #                        file_name: 'Genie' 
        #                         file_uti: 'public.volume' 
        #                    file_mod_date: '2013-02-20 10:10:12' 
        
        from relations.relation import relation
        
        # test relatin frm dictionary
        
        r1 = relation(  d.keys() , [d] , "files")

        r2 = relation(  d.keys() , (), "files")
        r2.add(d)
        
        print r1 == r2
        # print [r for r in r1]
        
        add_file_sql = ("insert into files "
                        " (folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti) "
                        " values ( %(folder_id)s, %(file_name)s, %(file_id)s, %(file_size)s, %(file_create_date)s, "
                        " %(file_mod_date)s, %(file_uti)s ) "
                        
                        );

        for t in r1:
            # print type(t)
            print add_file_sql % t._asdict()

        # insert into files  (folder_id, file_name, file_id, file_size, file_create_date, file_mod_date, file_uti)  
        #       values ( 1, Genie, 2, 0, 2011-07-02 21:02:54 +0000,  2013-02-20 10:10:12 +0000, public.volume ) 
         

    
if __name__ == '__main__':
    unittest.main()
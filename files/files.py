#!/usr/bin/env python
# encoding: utf-8
"""
files/files.py

Created by donb on 2013-02-20.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import objc
from Foundation import NSFileManager  , NSURL,   NSURLContentModificationDateKey


#
#   This table is pretty much what this module is about. 
#                        


# some Common File System Resource Keys

from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLAttributeModificationDateKey, \
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey, \
                        NSURLIsPackageKey

NSFileSystemFileNumber      = u'NSFileSystemFileNumber'                        
NSFileSystemFolderNumber    = u'NSFileSystemFolderNumber'
NSURLTotalFileSizeKey       = u'NSURLTotalFileSizeKey'
NSURLPathKey                = u'NSURLPathKey'       # will be defined in later pyobjc version?


databaseAndURLKeys = [  ( 'file_name',            NSURLNameKey), 
                        (  None,                  NSURLIsDirectoryKey), 
                        (  None,                  NSURLVolumeURLKey), 
                        (  None,                  NSURLLocalizedTypeDescriptionKey), 
                        ( 'file_uti',             NSURLTypeIdentifierKey), 
                        ( 'file_create_date',     NSURLCreationDateKey), 
                        ( 'file_mod_date',        NSURLContentModificationDateKey), 
                        (  None,                  NSURLParentDirectoryURLKey), 
                        ( 'file_size',            NSURLTotalFileSizeKey),
                        ( 'file_id',              NSFileSystemFileNumber),
                        ( 'folder_id',            NSFileSystemFolderNumber ),
                        (  None,                  NSURLIsVolumeKey)
                    ]


enumeratorURLKeys = [t[1] for t in databaseAndURLKeys]

file_record_keys = [t[0] for t in databaseAndURLKeys if t[0] ]

from collections import namedtuple        

file_record = namedtuple("file_record", file_record_keys) 
 


# print "enumeratorURLKeys:", enumeratorURLKeys

    # NSURLAttributeModificationDateKey           ??
    # NSURLContentAccessDateKey;
    # NSURLContentModificationDateKey             props2, enumerator2, pr8, insertitems
    # NSURLCreationDateKey                        props2, enumerator2, insertitem
    # NSURLCustomIconKey;
    # NSURLEffectiveIconKey;
    
    # NSURLFileResourceIdentifierKey:<36a07402 00000000 67456400 00000000>
     
    # NSURLFileResourceTypeKey;
    # 
    #   Possible values for the NSURLFileResourceTypeKey key.
    #     NSURLFileResourceTypeNamedPipe
    #     NSURLFileResourceTypeCharacterSpecial;
    #     NSURLFileResourceTypeDirectory;
    #     NSURLFileResourceTypeBlockSpecial;
    #     NSURLFileResourceTypeRegular;
    #     NSURLFileResourceTypeSymbolicLink;
    #     NSURLFileResourceTypeSocket;
    #     NSURLFileResourceTypeUnknown;
    #     
    # NSURLFileSecurityKey;
    # NSURLHasHiddenExtensionKey;

    # NSURLIsDirectoryKey                       props2, enumerator2 (twice)

    # NSURLIsExcludedFromBackupKey;
    # NSURLIsExecutableKey;
    # NSURLIsHiddenKey;
    # NSURLIsMountTriggerKey;
    # NSURLIsPackageKey;
    # NSURLIsReadableKey;
    # NSURLIsRegularFileKey;
    # NSURLIsSymbolicLinkKey;
    # NSURLIsSystemImmutableKey;
    # NSURLIsUserImmutableKey;
    # NSURLIsVolumeKey                          GetSuperfolderList, props2, print_vsd5
    # 
    # NSURLIsWritableKey;
    # NSURLLabelColorKey;
    # NSURLLabelNumberKey;
    # NSURLLinkCountKey;
    # NSURLLocalizedLabelKey;
    # NSURLLocalizedNameKey;
    # NSURLLocalizedTypeDescriptionKey          props2, enumerator2     ,  # eg, 'Folder'

    # NSURLNameKey                              insertitem, pr8

    # NSURLParentDirectoryURLKey                enumerator2 (twice)
    # 'NSURLPathKey'                            Have to define and set this ourselves.
    
    # NSURLPreferredIOBlockSizeKey;
    
    # NSURLTypeIdentifierKey                 props2, enumerator2   
    
    # NSURLVolumeIdentifierKey  
            # The unique identifier of the resource’s volume, returned as an id.
            # This identifier can be used with the isEqual: method to determine whether
            #     two file system resources are on the same volume.
            # The value of this identifier is not persistent across system restarts.

    # NSURLVolumeURLKey;
            # The root directory of the resource’s volume, returned as an NSURL object.

    # 
    #   Files
    # 
    
    # NSURLFileSizeKey;
    # NSURLFileAllocatedSizeKey;
    # NSURLIsAliasFileKey;
    # NSURLTotalFileAllocatedSizeKey;
    # 
    # 'NSURLTotalFileSizeKey'                 props2, insertitem
    # 
    # total displayable size of the file in bytes; includes the size of any file metadata)
    # 
    # # Volumes
    # 
    # NSURLVolumeLocalizedFormatDescriptionKey;
    # NSURLVolumeTotalCapacityKey                               DoDBInsertVolumeData
    # NSURLVolumeAvailableCapacityKey                           DoDBInsertVolumeData
    # NSURLVolumeResourceCountKey;
    # NSURLVolumeSupportsPersistentIDsKey;
    # NSURLVolumeSupportsSymbolicLinksKey;
    # NSURLVolumeSupportsHardLinksKey;
    # NSURLVolumeSupportsJournalingKey;
    # NSURLVolumeIsJournalingKey;
    # NSURLVolumeSupportsSparseFilesKey;
    # NSURLVolumeSupportsZeroRunsKey;
    # NSURLVolumeSupportsCaseSensitiveNamesKey;
    # NSURLVolumeSupportsCasePreservedNamesKey;
    # NSURLVolumeSupportsRootDirectoryDatesKey;
    # NSURLVolumeSupportsVolumeSizesKey;
    # NSURLVolumeSupportsRenamingKey;
    # NSURLVolumeSupportsAdvisoryFileLockingKey;
    # NSURLVolumeSupportsExtendedSecurityKey;
    # NSURLVolumeIsBrowsableKey;
    # NSURLVolumeMaximumFileSizeKey;
    # NSURLVolumeIsEjectableKey;
    # NSURLVolumeIsRemovableKey;
    # NSURLVolumeIsInternalKey                ??
    # NSURLVolumeIsAutomountedKey;
    # NSURLVolumeIsLocalKey;
    # NSURLVolumeIsReadOnlyKey;
    # NSURLVolumeCreationDateKey;
    # NSURLVolumeURLForRemountingKey;
    # NSURLVolumeNameKey;
    # NSURLVolumeLocalizedNameKey;



# print asdf(NSURL,42)


sharedFM = NSFileManager.defaultManager()

def df2fk(v):
        # v = itemDict[fk]
        t = type(v)
        if isinstance(v, objc.pyobjc_unicode):
            return unicode(v) # .encode('utf8')
        # elif isinstance(v, NSDate):
        #     return str(v) # yeah, could be a python datetime?  str() works. date needed for timezone formatting?
        elif isinstance(v, (objc._pythonify.OC_PythonLong, int)):
            return int(v)
        else:
            return v # (type(itemDict[fk]), itemDict[fk])        
    

class MyError(Exception):
    def __init__(self, code, description=""):
        self.code = code
        self.description = description
    def __str__(self):
        return "%s (%d)" %  (self.description,  self.code)

from PyObjCTools import Conversion
from Foundation import NSMutableDictionary

def is_item_a_package(item_url):
    p_dict, error =  item_url.resourceValuesForKeys_error_( [NSURLIsPackageKey] , None )
    if error is not None:
        raise MyError(error.code()  , error.localizedDescription())
    return p_dict[NSURLIsPackageKey]

def is_a_directory(fs_dict, options):
    """ie, is a diretory but not a package unless we want to scan packages"""

    item_is_package = fs_dict[NSURLIsPackageKey]
    return fs_dict[NSURLIsDirectoryKey] and ((not item_is_package) or options.scan_packages)
            
                

def error_handler_for_enumerator(y,error):
    print "enumeratorAtURL error: %s (%d)" % (error.localizedDescription(), error.code())

def GetURLValues(url, inProps):

    ns_dict, error =  url.resourceValuesForKeys_error_( inProps+[NSURLIsVolumeKey, u'NSURLParentDirectoryURLKey', NSURLIsDirectoryKey, NSURLIsPackageKey] , None )
    
    if error is not None:
        raise MyError(error.code()  , error.localizedDescription())

    ns_dict = ns_dict.mutableCopy()

    p = url.path()
    file_id = os.lstat(p).st_ino

    # [anotherDict setObject: dict forKey: "sub-dictionary-key"];
    ns_dict[NSFileSystemFileNumber] = file_id 
    ns_dict[NSURLPathKey] = p 
    ns_dict['url'] = url

    if ns_dict[NSURLIsDirectoryKey]:
        ns_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

    if ns_dict[NSURLIsVolumeKey]:
        ns_dict[NSFileSystemFolderNumber] = 1L
    else:
        folder_url  = ns_dict[NSURLParentDirectoryURLKey]
        fp          = folder_url.path()
        folder_id   = os.lstat(fp).st_ino
        ns_dict[NSFileSystemFolderNumber] = int(folder_id)

    return ns_dict
    # return Conversion.pythonCollectionFromPropertyList(ns_dict, lambda x: x)
    # conversion gets you, eg
    #    ' NSURLContentModificationDateKey = datetime.datetime(2013, 3, 11, 10, 59, 42)',

    
def GetURLResourceValuesForKeys(url, inProps):
    """raises custom exception MyError when, eg, the file does not exist"""
    
    # add keys needed by this routine
    values, error =  url.resourceValuesForKeys_error_( inProps+[NSURLIsVolumeKey, u'NSURLParentDirectoryURLKey', NSURLIsDirectoryKey] , None )
    
    if error is not None:
        raise MyError(error.code()  , error.localizedDescription())

    # convert unicode key strings to string
    # convert objc types to python types (for mysql converter)
    
    item_dict =   dict( zip(   [str(z) for z in values.allKeys() ] , [df2fk(v) for v in values.allValues()] ) )

    # add fields that are filesystem related, but not directly gotten as keys in the URL values
    
    p = url.path()
    file_id = os.lstat(p).st_ino
    item_dict[NSFileSystemFileNumber] = file_id 
    item_dict[NSURLPathKey] = p 

    if item_dict[NSURLIsDirectoryKey]:
        item_dict.update(  {  "NSURLTotalFileSizeKey":  0 })  # file size is zero for directories

    if item_dict[NSURLIsVolumeKey]:
        item_dict[NSFileSystemFolderNumber] = 1L
    else:
        folder_url  = values[NSURLParentDirectoryURLKey]
        fp          = folder_url.path()
        folder_id   = os.lstat(fp).st_ino
        item_dict[NSFileSystemFolderNumber] = int(folder_id)
    
    return item_dict



def GetNSFileAttributesOfItem(s):
    """deprecated!"""

    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
        print
        print error
    
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    return dz


def pdt(l, in_dict, left_col_width=24):
    # if options.verbose_level >= verbose_level_threshold:
    print l + ":"
    print
    s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
    print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
    print


import unittest

from Foundation import NSFileType, NSFileTypeDirectory, NSFileOwnerAccountName, NSFileGroupOwnerAccountName, NSFileSystemFileNumber
 
class files_TestCase( unittest.TestCase ):
    """ Class to test files """
    
    def test_050_NSFiles(self):
        """ GetNSFileAttributesOfItem """
    
        d = GetNSFileAttributesOfItem("/")

        self.assertEqual(d[NSFileType]  ,  NSFileTypeDirectory)
        self.assertEqual(d[NSFileOwnerAccountName]  ,  u'root')
        self.assertEqual(d[NSFileGroupOwnerAccountName]  ,  u'wheel')
        self.assertEqual(d[NSFileSystemFileNumber]  ,  2L)
        
        # rest of attributes are probably different
                  
        # l = 'GetNSFileAttributesOfItem("/")'
        # pdt(l, d, 28)

        p = "/Users/donb"
        d = GetNSFileAttributesOfItem(p)
        self.assertEqual(d[NSFileType]                  , NSFileTypeDirectory)
        self.assertEqual(d[NSFileOwnerAccountName]      , u'donb')
        self.assertEqual(d[NSFileGroupOwnerAccountName] , u'staff')
        self.assertEqual(d[NSFileSystemFileNumber]      , 328394L)

    def test_050_NSURL(self):
        """ GetURLResourceValuesForKeys """

        url =  NSURL.fileURLWithPath_("/")

        d1 = GetURLResourceValuesForKeys(url, [NSURLTotalFileSizeKey, NSURLContentModificationDateKey ])
        
        self.assertEqual(d1[NSURLPathKey]              , u'/')
        self.assertEqual(d1[NSFileSystemFolderNumber]    , 1L)
        self.assertTrue(d1[NSURLIsDirectoryKey])
        self.assertTrue(d1[NSURLIsVolumeKey])
        self.assertEqual(d1[NSFileSystemFileNumber]      , 2)

        # l = 'GetURLResourceValuesForKeys("")'
        # pdt(l, du, 28)

        url =  NSURL.fileURLWithPath_("/Users/donb")

        d2 = GetURLResourceValuesForKeys(url, [NSURLTotalFileSizeKey, NSURLContentModificationDateKey ])

        self.assertEqual( d2[NSURLPathKey]              , u'/Users/donb' )
        self.assertEqual( d2[NSFileSystemFolderNumber]    , 48946 )
        self.assertTrue(  d2[NSURLIsDirectoryKey])
        self.assertEqual(  d2[NSURLTotalFileSizeKey], 0)
        self.assertTrue(  d2[NSURLParentDirectoryURLKey], "file://localhost/Users/")
        self.assertFalse( d2[NSURLIsVolumeKey])
        self.assertEqual( d2[NSFileSystemFileNumber]      , 328394)
        
        # now with the full set of enumerator keys
        
        url =  NSURL.fileURLWithPath_("/")
        d3 = GetURLResourceValuesForKeys(url, enumeratorURLKeys)
    
        self.assertEqual(  d3[NSURLPathKey]              ,u'/' )
        self.assertEqual(  d3[NSURLNameKey]              , u'Genie'  )
        self.assertEqual(  d3[NSFileSystemFolderNumber]    , 1L )
        self.assertTrue(   d3[NSURLIsDirectoryKey])
        self.assertEqual(  d3[NSURLTotalFileSizeKey]        , 0)
        with self.assertRaises(KeyError):                       # no  NSURLVolumeURLKey for volume-level item
             d3[NSURLParentDirectoryURLKey]
        self.assertTrue(  d3[NSURLIsVolumeKey])
        self.assertEqual(  d3[NSFileSystemFileNumber]      , 2)
        self.assertEqual(  d3[NSURLLocalizedTypeDescriptionKey]      , u'Volume' )
        self.assertEqual(  d3[NSURLTypeIdentifierKey]      , u'public.volume' )

        # from Foundation import NSURLNameKey, NSURLTypeIdentifierKey
        d = {}
        for dk, fk in databaseAndURLKeys:
            if dk:
                if fk in [NSURLNameKey, NSURLTypeIdentifierKey]:
                    d[dk] =  d3[fk].encode('utf8')
                elif dk in ['file_create_date', 'file_mod_date']:
                    d[dk] =  str(d3[fk])[:-len(" +0000")]
                else:
                    d[dk] =  d3[fk]
 
        file1 = file_record( *(map (d.get , file_record_keys ))  )
        print file1

        from dates import dateFormatters        
        
        sa =  dateFormatters[0]['df'].stringFromDate_(item_dict[NSURLContentModificationDateKey])
        print sa

        pathname         = item_dict["NSURLPathKey"]
        folder_id        = item_dict['NSFileSystemFolderNumber']
        filename         = item_dict[NSURLNameKey]
        file_id          = item_dict['NSFileSystemFileNumber']
        # depth = i - n + 1

        if options.verbose_level >= n:
            s =    "%-12s %-8s %-7s %8d %8d %s %2d %s" % (l, itemsToDelete_repr(itemsToDelete), vol_id , folder_id, file_id, sa,  depth, filename) 
            print s
            # NSLog(s)

        
        
        vol_id = "vol0007"
        print "vol0007 42884672 42884713 Wed 2013.02.20 18:02 EST  2 __init__.py" , vol_id, file1.file_id
#   repr of a file record is "vol0007 42884672 42884713 Wed 2013.02.20 18:02 EST  2 __init__.py"

if __name__ == '__main__':
    unittest.main()
    

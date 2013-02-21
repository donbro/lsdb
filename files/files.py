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
from Foundation import NSFileManager  , NSURL, NSURLIsVolumeKey, NSURLContentModificationDateKey, \
                    NSURLParentDirectoryURLKey


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
    # NSURLVolumeUUIDStringKey                DoDBInsertVolumeData
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


def GetURLResourceValuesForKeys(url, inProps):
    """raises custom exception MyError when, eg, the file does not exist"""
    
    values, error =  url.resourceValuesForKeys_error_( inProps+[NSURLIsVolumeKey, u'NSURLParentDirectoryURLKey'] , None )
    
    if error is not None:
        raise MyError(error.code()  , error.localizedDescription())

    # convert unicode key strings to string
    # convert objc types to python types (for mysql converter)
    
    item_dict =   dict( zip(   [str(z) for z in values.allKeys() ] , [df2fk(v) for v in values.allValues()] ) )

    # add fields that are filesystem related, but not directly gotten as keys in the URL values
    
    p = url.path()
    file_id = os.lstat(p).st_ino
    item_dict['NSFileSystemFileNumber'] = file_id 
    item_dict['NSURLPathKey'] = p 

    if item_dict[NSURLIsVolumeKey]:
        item_dict['NSFileSystemFolderNumber'] = 1L
    else:
        folder_url  = values[NSURLParentDirectoryURLKey]
        fp          = folder_url.path()
        folder_id   = os.lstat(fp).st_ino
        item_dict['NSFileSystemFolderNumber'] = int(folder_id)
    
    return item_dict



def GetNSFileAttributesOfItem(s):
    """deprecated!"""

    (attrList,error) = sharedFM.attributesOfItemAtPath_error_(s,None)  # returns NSFileAttributes
    
    if error is not None:
        print
        print error
    
    dz =  dict(zip( map (str, attrList.allKeys()) , attrList.allValues() ))
    return dz

    # GetNSFileAttributesOfItem("/"):
    # 
    #                   NSFileType: u'NSFileTypeDirectory' 
    #       NSFileOwnerAccountName: u'root' 
    #    NSFileGroupOwnerAccountID: 0L 
    #           NSFileSystemNumber: 234881026L 
    #         NSFileReferenceCount: 34L 
    #           NSFileCreationDate: 2011-07-02 21:02:54 +0000 
    #        NSFileExtensionHidden: False 
    #  NSFileGroupOwnerAccountName: u'wheel' 
    #         NSFileOwnerAccountID: 0L 
    #       NSFilePosixPermissions: 493L 
    #       NSFileSystemFileNumber: 2L 
    #       NSFileModificationDate: 2013-02-20 10:10:12 +0000 
    #                   NSFileSize: 1224L 

def pdt(l, in_dict, left_col_width=24):
    # if options.verbose_level >= verbose_level_threshold:
    print l + ":"
    print
    s = "%%%ss: %%r " % left_col_width # "%%%ss: %%r " % 36  ==>  '%36s: %r '
    print "\n".join([  s % (k,v)  for k,v in dict(in_dict).items() ])
    print

def main():
    
    try:
    
        d = GetNSFileAttributesOfItem("/")
        # print d
        l = 'GetNSFileAttributesOfItem("/")'
        pdt(l, d, 28)

        p = "/Users/donb"
        d = GetNSFileAttributesOfItem(p)
        # print d
        l = 'GetNSFileAttributesOfItem("' + p +'")'
        pdt(l, d, 28)

        url =  NSURL.fileURLWithPath_("/")

        du = GetURLResourceValuesForKeys(url, ['NSURLTotalFileSizeKey', NSURLContentModificationDateKey])
        l = 'GetURLResourceValuesForKeys("")'
        pdt(l, du, 28)

        url =  NSURL.fileURLWithPath_("/Users/donb")

        du = GetURLResourceValuesForKeys(url, ['NSURLTotalFileSizeKey', NSURLContentModificationDateKey ])
        l = 'GetURLResourceValuesForKeys("")'
        pdt(l, du, 28)
    
    except MyError as e:
            print "Error: " + "%s (%d)" %  ( e.description, e.code )


if __name__ == '__main__':
    main()


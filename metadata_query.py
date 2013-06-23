#!/Users/donb/projects/VENV/lsdb/bin/python
# encoding: utf-8

"""
begin special truncated version of aperture library process
"""

import sys
from Cocoa import NSMetadataQuery, NSPredicate, NSMetadataQueryLocalComputerScope, \
                    NSNotificationCenter, NSMetadataQueryDidFinishGatheringNotification, \
                    NSMetadataQueryDidUpdateNotification, NSMetadataQueryGatheringProgressNotification, \
                    NSDefaultRunLoopMode, NSDictionary
                    
from PyObjCTools import AppHelper
                    

def do_metadata_query(q):

    query = NSMetadataQuery.alloc().init()
    query.setPredicate_(NSPredicate.predicateWithFormat_( q ))

    scopes = [NSMetadataQueryLocalComputerScope]       # or [NSMetadataQueryUserHomeScope]
    query.setSearchScopes_( scopes )

    do_run_query_loop(query)
    
    print "query.resultCount() is:", query.resultCount()
    
    return query

def do_run_query_loop(query):    
    
    class MyEventHandlers():
        
        def __init__(self, code, description=""):
            self.code = code
            self.description = description
        def __str__(self):
            return "%s (%d)" %  (self.description,  self.code)
        def gathering_(self, notification):
            print   notification.name() # NSMetadataQueryGatheringProgressNotification
        def did_update_(self, notification):
            print   "name", notification.name()
            print   "userInfo is: " , notification.userInfo()
        
        def did_finish_(self, notification):
            print   notification.name() # NSMetadataQueryDidFinishGatheringNotification
            # Stops the event loop (if started by runConsoleEventLoop) or sends the NSApplication a terminate: message.
            didStop = AppHelper.stopEventLoop()
            if didStop: 
                print "stopping the event loop "
            raise ValueError, "this will stop you!"

    my_handlers = MyEventHandlers(1)

    nc.addObserver_selector_name_object_(my_handlers, "did_finish:", NSMetadataQueryDidFinishGatheringNotification, query)
    nc.addObserver_selector_name_object_(my_handlers, "did_update:", NSMetadataQueryDidUpdateNotification, query)
    nc.addObserver_selector_name_object_(my_handlers, "gathering:",  NSMetadataQueryGatheringProgressNotification, query)

    query.startQuery()

    print "Listening for new tunes...."
    try:
        AppHelper.runConsoleEventLoop( mode = NSDefaultRunLoopMode)
    except ValueError, e:
        print "ValueError", e
#     except e:
#         print e
        
    print "finished with runConsoleEventLoop()"
    query.stopQuery()
 
def do_aperture_library(pathname): # i, s, vol_id, file_id):
        
    lib_info_plist = NSDictionary.dictionaryWithContentsOfFile_(pathname+"/Info.plist")
 
    print  lib_info_plist['CFBundleShortVersionString'] ,  
    
    if lib_info_plist['CFBundleShortVersionString'] == "2.1":
        print "convert version 2.1 library"
        return 
    
    print pathname
    
    DataModelVersionDict = NSDictionary.dictionaryWithContentsOfFile_(pathname+"/Aperture.aplib/DataModelVersion.plist")
    
#     d1.update(Conversion.pythonCollectionFromPropertyList(ns_dict))
    
    print DataModelVersionDict['databaseUuid']

    print DataModelVersionDict    
    
 
    
#
#        begin
#

nc = NSNotificationCenter.defaultCenter()

q = 'kMDItemKind = "Aperture Library"'

query = do_metadata_query(q)

n = query.resultCount()

for i in range(n):
    item = query.resultAtIndex_(i)
    d1 =  item.valuesForAttributes_( [  'kMDItemFSName',
                                            'kMDItemDisplayName',
                                            'kMDItemPath',
                                            'kMDItemKind',
                                            'kMDItemContentType',
                                            'kMDItemDateAdded',
                                            'kMDItemFSCreationDate',
                                            'kMDItemContentTypeTree',
                                            'kMDItemFSContentChangeDate'])
    pathname = d1['kMDItemPath']
    
    do_aperture_library(pathname)
    
    sys.exit()




"""
metadata_query.py

    Run metadata lookup; pass results to lsdb()

Created by donb on 2013-03-11.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

# import sqlite3 as sqlite
# 
# with sqlite.connect(db_filename) as conn:
#     query = "INSERT OR IGNORE INTO shapes VALUES (?,?);"
#     results = conn.execute(query, ("ID1","triangle"))
# 
# 
# sys.exit()

# import mysql.connector

# from lsdb import do_cnx_basepath, do_fs_basepath, MyError, execute_insert_query

#
#       do_run_query_loop
#

def do_run_query_loop0(query):
    """docstring for do_run_loop"""
    
    class MyEventHandlers():
        def __init__(self, code, description=""):
            self.code = code
            self.description = description
        
        def __str__(self):
            return "%s (%d)" %  (self.description,  self.code)
        
        def gathering_(self, notification):
            print   notification.name() # NSMetadataQueryGatheringProgressNotification

        def did_update_(self, notification):
            print   "name", notification.name()
            print   "userInfo is: " , notification.userInfo()
        
        def did_finish_(self, notification):
            print   notification.name() # NSMetadataQueryDidFinishGatheringNotification
            # Stops the event loop (if started by runConsoleEventLoop) or sends the NSApplication a terminate: message.
            didStop = AppHelper.stopEventLoop()
            if didStop: 
                print "stopping the event loop "
            raise ValueError, "this will stop you!"

    my_handlers = MyEventHandlers(1)

    nc.addObserver_selector_name_object_(my_handlers, "did_finish:", NSMetadataQueryDidFinishGatheringNotification, query)
    nc.addObserver_selector_name_object_(my_handlers, "did_update:", NSMetadataQueryDidUpdateNotification, query)
    nc.addObserver_selector_name_object_(my_handlers, "gathering:",  NSMetadataQueryGatheringProgressNotification, query)

    query.startQuery()

    print "Listening for new tunes...."
    try:
        AppHelper.runConsoleEventLoop( mode = NSDefaultRunLoopMode)
    except ValueError, e:
        print "ValueError", e
    except e:
        print e
        
    print "finished with runConsoleEventLoop()"
    query.stopQuery()


import pprint
def do_metadata_query():

    query = NSMetadataQuery.alloc().init()
    q = 'kMDItemKind = "Aperture Library"'
    query.setPredicate_(NSPredicate.predicateWithFormat_( q ))

    scopes = [NSMetadataQueryLocalComputerScope]       
    # scopes = [NSMetadataQueryUserHomeScope]             
    query.setSearchScopes_( scopes )


    do_run_query_loop(query)
    
    #   process results

    n = query.resultCount()

    print "query.resultCount() is:", query.resultCount()


    config = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'files',
        'buffered': True
    }

    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password %r and %r?" % (config['user'], config['password']))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database %r does not exist." % config['database']
        else:
            print 'err:', err
    
    
    for i in range(n):
        item = query.resultAtIndex_(i)
                
        # print "item.attributes(): ", item.attributes()    
        
        #     kMDItemContentTypeTree,   kMDItemContentType,   kMDItemKind,
        #     kMDItemDisplayName,   kMDItemAlternateNames,   kMDItemDateAdded,
        #     kMDItemContentCreationDate,   kMDItemContentModificationDate,   kMDItemFSName,
        #     kMDItemFSSize,                kMDItemFSCreationDate,            kMDItemFSContentChangeDate,
        #     kMDItemFSOwnerUserID,   kMDItemFSOwnerGroupID,   kMDItemFSNodeCount,   kMDItemFSInvisible,
        #     kMDItemFSTypeCode,   kMDItemFSCreatorCode,   kMDItemFSFinderFlags,   kMDItemFSHasCustomIcon,
        #     kMDItemFSIsExtensionHidden,   kMDItemFSIsStationery,   kMDItemFSLabel
        


        d1 =  item.valuesForAttributes_( [  'kMDItemFSName',
                                            'kMDItemDisplayName',
                                            'kMDItemPath',
                                            'kMDItemKind',
                                            'kMDItemContentType',
                                            'kMDItemDateAdded',
                                            'kMDItemFSCreationDate',
                                            'kMDItemContentTypeTree',
                                            'kMDItemFSContentChangeDate'])
        basepath = d1['kMDItemPath']
        
        #
        #       call do_fs_basepath
        #
        
        try:
            basepath = "/Users/donb/projects/lsdb-master"
            
            print "\nbasepath:", basepath, "\n"
            
            for fs_dict in do_fs_basepath(cnx, basepath ): # , force_folder_scan=True
                pass
                # print  "do_fs_basepath:", fs_dict['file_name'].decode('utf8')
                
            sys.exit()
            
            (vol_id, item_dict, insert_result) = do_cnx_basepath(cnx, basepath ,verbose_level = 0 )  
            
            file_id         = item_dict['NSFileSystemFileNumber']

            # print (vol_id, file_id, str(insert_result)) # ('vol0010', 27444211, 'existing')

        except MyError, err:
                print err.description
        
        db_fields_dict = do_aperture_library(i, basepath, vol_id, file_id)
        if db_fields_dict:
            # print_dict(db_fields_dict)     
            sql = ("insert into aperture_libs "
                            "(databaseUuid, external_masters_count, file_id, "
                                    " vol_id, masterCount, versionCount, lib_version) "
                            "values ( %(databaseUuid)s, %(external_masters_count)s, %(file_id)s, "
                            "%(vol_id)s, %(masterCount)s, %(versionCount)s, %(lib_version)s ) " 
                            # "on duplicate key update "
                            #              "vol_total_capacity = values(vol_total_capacity), "
                            #              "vol_available_capacity = values(vol_available_capacity)"
                            );
                            
            # print sql % db_fields_dict

            (l , vol_id) = execute_insert_query(cnx, sql, db_fields_dict, 1)
    
            # GPR.pr4(l, vol_id, "", data[1], 4)
                
        
        # if i >= 20: break
    
    
    cnx.close()

def ddkk(d1, d2, k1, k2=None):
    """docstring for xxdf"""
    if k2 == None: k2 = k1
    d1.update( {k1: d2.get(k2,None)} )

def do_aperture_library(i, s, vol_id, file_id):
    
    db_fields_dict = {'vol_id':vol_id, 'file_id':file_id}

    print
    print "[%-2d]==>%s" % (i+1, s) ,
        
    lib_path = s+"/Info.plist"
    # print lib_path
    lib_info_plist = NSDictionary.dictionaryWithContentsOfFile_(s+"/Info.plist")

 
    print  lib_info_plist['CFBundleShortVersionString'] ,  
    
    if lib_info_plist['CFBundleShortVersionString'] == "2.1":
        print "convert version 2.1 library"
        return 
    
    db_fields_dict['lib_version'] = str(lib_info_plist['CFBundleShortVersionString'])
    
    
    lib_data_model_plist = NSDictionary.dictionaryWithContentsOfFile_(s+"/Aperture.aplib/DataModelVersion.plist")

    print "(%s)" % (lib_info_plist['CFBundleShortVersionString'] , ) , 
    
    db_fields_dict['versionCount'] = int(lib_data_model_plist.get('versionCount',0))
    db_fields_dict['masterCount'] = int(lib_data_model_plist.get('masterCount',0))
    db_fields_dict['databaseUuid'] = str(lib_data_model_plist['databaseUuid'])
    
    
    dbPath = s + "/Database/Library.apdb"


    # """I am used to (spoiled by?) python's SQLite interface to deal with SQL databases. 
    # One nice feature in python's SQLite's API the "context manager," i.e., python's with statement. 
    # I usually execute queries in the following way:
    # 
    # import as sqlite
    # 
    # with sqlite.connect(db_filename) as conn:
    #     query = "INSERT OR IGNORE INTO shapes VALUES (?,?);"
    #     results = conn.execute(query, ("ID1","triangle"))
    # 
    # With the code above, if my query modifies the database and I forget to run
    #  conn.commit(),the context manager runs it for me automatically upon exiting 
    #  the with statement. It also handles exceptions nicely: if an exception
    #   occurs before I commit anything, then the database is rolled back.
    # 
    # I am now using the MySQLdb interface, which doesn't seem to support
    #  a similar context manager out of the box. How do I create my own? 
    #  There is a related question here, but it doesn't offer a complete solution.
    # 
    # """    

    conn = sqlite3.connect(dbPath)
    # print conn
    
    cursor = conn.cursor()
 
    # Overall counts
    
    cursor.execute("SELECT count(*) FROM RKMaster")    


    print " (%d masters)" % ( [r for r in cursor][0][0] , )
    # print "==>%s (%s) (%d masters)" % (s, lib_info_plist['CFBundleShortVersionString'] , [r for r in cursor][0][0] )

    # print "overall count of masters:", [r for r in cursor][0][0]

    
    # Folders and Projects

    sql =  "select ModelID, folderType, name, folderPath from RKFolder"     # folderPath is heirarchy information.  not currently being used.
    folder_names =  [ r['name']  for r in xda2(cursor, sql) if r['name'] not in folder_names_to_exclude]
    # print "\nfolders are: (%d) %s" % (len(folder_names), u", ".join(folder_names))
    
    # Volumes
    
    sql =  "SELECT   RKVolume.name  FROM RKVolume"
    volumes_list =  xda2(cursor, sql)
    # print volumes_list
    
    if volumes_list == []:
        print
        print "no external masters"
        # print "\nNo (external) volumes; all image versions are within library."

        db_fields_dict['external_masters_count'] = 0
        
        return db_fields_dict

    # else:

    zfd = ", ".join([r['name'] for r in volumes_list])
    # print "\nVolumes are:", ", ".join([r['name'] for r in volumes_list])
    sql =  """SELECT count(*) FROM RKMaster INNER JOIN RKVolume ON RKMaster.fileVolumeUuid = RKVolume.uuid"""

    cursor.execute( sql )
    external_masters_count = [r for r in cursor][0][0]
    print
    print "external masters (%d) on %s" % ( external_masters_count, zfd )
    db_fields_dict['external_masters_count'] = external_masters_count
    return db_fields_dict


def do_mounted_volumes():
            
    mounted_volumes_list = []
    for vol_name in volumes_list:
        vol_name = vol_name['name']      # each row is a tuple ( vol_name, os.lstat(fp) )
        # fp = 
        try:
            os.lstat("/Volumes/" + vol_name) 
            mounted_volumes_list.append( vol_name )
        except OSError:
            pass
    # print "mounted volumes are", ", ".join([r  for r in mounted_volumes_list])

    for vol_name in mounted_volumes_list:
        # vol_name = vol_name[0]      # each row is a tuple ( vol_name, os.lstat(fp) )
        
        do_volume_images(cursor, vol_name)

    conn.close()
    
def do_volume_images(cursor, vol_name):

    sql = ( "SELECT count(*) "
        "FROM RKMaster , RKVolume where RKMaster.fileVolumeUuid = RKVolume.uuid  "
        "and RKVolume.name = '%s'" % vol_name  )

    print
    print "%s masters (%d) are " % ( vol_name, xda(cursor, sql)[0][0],) ,
    
    # print
    
    sql = ( "SELECT * FROM RKMaster , RKVolume "
                "where RKMaster.fileVolumeUuid = RKVolume.uuid  "
                "and RKVolume.name = '%s' limit 0,10" 
                                % vol_name  )
                
    # print xda2(cursor, sql)
    
    # print

    sql = ( "SELECT RKVolume.name, RKMaster.fileName, RKMaster.imagePath, RKMaster.uuid, projectUuid, fileCreationDate "
                "FROM RKVolume, RKMaster "
                "where RKVolume.name = '" + vol_name + "' "
                " and RKMaster.fileVolumeUuid = RKVolume.uuid " ) # " limit 0,100" )
                
    theImages =  xda2(cursor, sql)
    
    foundImages = []
    notFoundImages = []
    for m in theImages:
        m['imagePath'] = "/Volumes/" + vol_name + "/" + m['imagePath']
        
        try:
            os.lstat(m['imagePath']) 
            foundImages.append( m['imagePath'] )
        except OSError:
            notFoundImages.append( m['imagePath'] )
            
    if len(foundImages) > 0: print "foundImages=%d "% len(foundImages),
    # print u"\n".join(foundImages)
    if len(notFoundImages) > 0:     print "notFoundImages=%d" % len(notFoundImages),
    # print u"\n".join(notFoundImages)
    print
    print


import sys
import os
import unittest

import objc

from Cocoa import NSMetadataQuery, NSPredicate, NSRunLoop, NSDate, \
    NSMetadataQueryLocalComputerScope, NSMetadataQueryUserHomeScope, \
    NSWorkspace, NSMetadataQueryDidFinishGatheringNotification, NSWorkspaceDidTerminateApplicationNotification, \
    NSWorkspaceActiveSpaceDidChangeNotification, NSMetadataQueryDidUpdateNotification, \
    NSNotificationCenter, NSMetadataQueryDidStartGatheringNotification, NSDefaultRunLoopMode, \
    NSObject, NSMetadataQueryGatheringProgressNotification


from Foundation import NSDictionary
    
# from Foundation import NSMetadataItemFSNameKey,\
#                                             NSMetadataItemDisplayNameKey,\
#                                             NSMetadataItemURLKey,\
#                                             NSMetadataItemPathKey,\
#                                             NSMetadataItemFSSizeKey,\
#                                             NSMetadataItemFSCreationDateKey,\
#                                             NSMetadataItemFSContentChangeDateKey

import sys


# ws = NSWorkspace.sharedWorkspace() # .sharednotificationCenter()
# nc = ws.notificationCenter()
# print nc


from PyObjCTools import Conversion
       
 # do_lsdb

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

# that's it!  Now, you can create a Bunch
# whenever you want to group a few variables



def print_dict(d):
    print
    print "\n".join(["%32s = %r" % (k,list(v) if k == 'kMDItemContentTypeTree' else v) for (k,v) in d.items() ])
    print

import sqlite3

print "sqlite3.version (this module)", sqlite3.version
# The version number of this module, as a string. This is not the version of the SQLite library.

# print "sqlite3.version_info", sqlite3.version_info
# The version number of this module, as a tuple of integers. This is not the version of the SQLite library.

print "sqlite3.sqlite_version (run-time)", sqlite3.sqlite_version
# The version number of the run-time SQLite library, as a string.

# print "sqlite3.sqlite_version_info", sqlite3.sqlite_version_info
# The version number of the run-time SQLite library, as a tuple of integers.


folder_names_to_exclude = [
                        "", 
                        'Projects',
                        "TopLevelBooks", 
                        "TopLevelKeepsakes", 
                        "TopLevelAlbums", 
                        "TopLevelWebProjects", 
                        "PublishedProjects", 
                        "IPHPublishServiceMobileMe", 
                        "TopLevelLightTables", 
                        "Library Albums", 
                        "TopLevelSlideshows", 
                        "Trash"
                        ]
         

import os
         


        # {'imageDate': 374332571, 'duration': None, 'isInTrash': 0, 
        # 'isOffline': 0, 'alternateMasterUuid': None, 'hasNotes': 1, 
        # 'originalVersionUuid': u'BVlZnOrbTtaOPIwRGPSnPg', 'fileModificationDate': 374332571, 
        # 'uuid': u'esuuBTIRRg2e%5TjqKr+Nw', 'subtype': u'JPGST', 'importGroupUuid': u'RKStreamImportGroup', 
        # 'label': None, 'originalFileSize': None, 'modDate': 371305769.38502, 
        # 'faceDetectionState': 0, 'type': u'IMGT', 'fileIsReference': 1, 
        # 'modelId': 1, 
        # 'imagePath': u'Users/donb/Library/Application Support/iLifeAssetManagement/assets/sub/0188414a4e5fa44292e4c65ca19163ae41f793e455/IMG_2776.JPG', 
        # 'fileCreationDate': 374332571, 'isTrulyRaw': 0, 'importedBy': 2, 
        # 'fileName': u'IMG_2776.JPG', 'pixelFormat': 9, 'fileSize': 122553, 
        # 'colorSpaceName': u'sRGB IEC61966-2.1', 'hasFocusPoints': 0, 'originalFileName': u'IMG_2776.JPG', 
        # 'name': u'Genie', 'diskUuid': u'77E236DC-4145-3D23-BADB-CE8D1F233DDA', 'hasAttachments': 0, 
        # 'imageHash': None, 'fileAliasData': None, 'originalVersionName': u'IMG_2776', 
        # 'projectUuid': u'RKPhotostreamFolder', 'isExternallyEditable': 0, 'isMissing': 0, 
        # 'imageFormat': 1246774599, 'fileVolumeUuid': u'esuuBTIRRg2e%5TjqKr+Nw', 'createDate': 371305769.38502, 
        # 'colorSpaceDefinition': None}, 
        
        
def do_aperture_libraryX(d):
    
    # python version has dates like: datetime.datetime(2012, 10, 7, 8, 27, 23)
    d1 = Conversion.pythonCollectionFromPropertyList(d)

    # d1['kMDItemPath'] = "/Volumes/Taos/model/Heidi Klum.aplibrary/"  # fixed library for testing, query can return different order!
    # d1['kMDItemPath'] = u"/Volumes/Brandywine/Aperture Library—Rialto—lib 23G.aplibrary/"    
    s = d1['kMDItemPath']

    print s
    
    print_dict(d)
    print_dict(d1)
    
    #
    #       invoke lsdb on the original library file, to get the vol_id, file_id for use when recording 
    #           the rest of the info from the library file
    #
    



    
    # except mysql.connector.Error as err:
    #     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    #         print("Username or password %r and %r?" % (config['user'], config['password']))
    #     elif err.errno == errorcode.ER_BAD_DB_ERROR:
    #         print "Database %r does not exist." % config['database']
    #     else:
    #         print 'err:', err
    # finally:
    #     
    # 
    
    ns_dict = NSDictionary.dictionaryWithContentsOfFile_(s+"/Info.plist")
    d1.update(Conversion.pythonCollectionFromPropertyList(ns_dict))

    
    if d1['CFBundleShortVersionString'] == "2.1":
        print "convert version 2.1 library"
        sys.exit()
        

    ns_dict = NSDictionary.dictionaryWithContentsOfFile_(s+"/Aperture.aplib/DataModelVersion.plist")
    d1.update(Conversion.pythonCollectionFromPropertyList(ns_dict))
    
    print d1['databaseUuid']

    print_dict(d1)    

    # {
    #     DatabaseMinorVersion = 119;
    #     DatabaseVersion = 110;
    #     createDate = "2012-02-23 19:27:27 +0000";
    #     databaseUuid = GJVtWD2pRnGz3Qin9Gze4g;
    #     isIPhotoLibrary = 0;
    #     masterCount = 35;
    #     projectCompatibleBackToVersion = 6;
    #     projectVersion = 6;
    #     versionCount = 35;
    # }

    # 		set theDBPosixPath to theApLibPosixPath & "/Database/Library.apdb"

    dbPath = s + "/Database/Library.apdb"
    print dbPath
    import sqlite3

    print sqlite3.version
    # The version number of this module, as a string. This is not the version of the SQLite library.

    print sqlite3.version_info
    # The version number of this module, as a tuple of integers. This is not the version of the SQLite library.

    print sqlite3.sqlite_version
    # The version number of the run-time SQLite library, as a string.

    print sqlite3.sqlite_version_info
    # The version number of the run-time SQLite library, as a tuple of integers.

    
    conn = sqlite3.connect(dbPath)
    print conn
    
    cursor = conn.cursor()
 
    # overall conunts
    cursor.execute("SELECT count(*) FROM RKMaster")
    # print cursor.fetchall()  # or use fetchone()
    
    print [r for r in cursor]

    # Folders and Projects

    sql =  "select ModelID, folderType, name, folderPath from RKFolder"
    # -- folderPath is heirarchy information.  not currently being used.
    z =  xda(cursor, sql)
    print repr(", ".join([ r[2].encode('utf8') for r in z if r[2] not in [
    
         "", "TopLevelBooks", "TopLevelKeepsakes", "TopLevelAlbums", "TopLevelWebProjects", 
         "PublishedProjects", "IPHPublishServiceMobileMe", "TopLevelLightTables", "Library Albums", 
         "TopLevelSlideshows", "Trash"
    
         ]]))

    
    # Volumes
    
    sql =  "SELECT   RKVolume.name  FROM RKVolume"
    volumes_list =  xda(cursor, sql)
    print "volumes_list", ", ".join([r[0] for r in volumes_list])
    
    if volumes_list == []:
        print "no (external) volumes; all image versions are within library."
        return

    # else:

    # for those with external volumes (though db can mention volume without any images being there :?)

    sql =  """SELECT count(*) FROM RKMaster INNER JOIN RKVolume ON RKMaster.fileVolumeUuid = RKVolume.uuid"""

    cursor.execute( sql )
    print "external volume masters count:", [r for r in cursor][0][0]

    mounted_volumes_list = []
    for vol_name in volumes_list:
        vol_name = vol_name[0]      # each row is a tuple ( vol_name, os.lstat(fp) )
        import os
        fp = "/Volumes/" + vol_name
        try:
            mounted_volumes_list.append( ( vol_name, os.lstat(fp) )  )
        except OSError:
            pass
    print "mounted volumes", mounted_volumes_list
    
    for vol_name in mounted_volumes_list:
        vol_name = vol_name[0]      # each row is a tuple ( vol_name, os.lstat(fp) )
        
        print "vol_name", vol_name

        sql = ( "SELECT count(*) "
            "FROM RKMaster , RKVolume where RKMaster.fileVolumeUuid = RKVolume.uuid  "
            "and RKVolume.name = '%s'" % vol_name  )
        print xda(cursor, sql)[0]
        
        print
        
        sql = ( "SELECT * "
            "FROM RKMaster , RKVolume where RKMaster.fileVolumeUuid = RKVolume.uuid  "
            "and RKVolume.name = '%s' limit 0,10" % vol_name  )
        print xda2(cursor, sql)
        
        print

        sql = ( "SELECT RKVolume.name, RKMaster.fileName, RKMaster.imagePath, fileCreationDate "
                    "FROM RKVolume, RKMaster "
                    "where RKVolume.name = '" + vol_name + "' "
                    " and RKMaster.fileVolumeUuid = RKVolume.uuid" ) # " limit 0,100" )
        theImages =  xda2(cursor, sql)
        
        zz = []
        for m in theImages:
            fp = "/Volumes/" + vol_name + "/" + m['imagePath']
            try:
                zz.append( ( fp, os.lstat(fp) )  )
            except OSError:
                pass
                
        print
        print zz
        print


        # fp = "/Volumes/" + vol_name
        # try:
        #     mounted_volumes_list.append( ( vol_name, os.lstat(fp) )  )
        
        # 		set t to "/Volumes/" & VolumeName & "/" & imagePath


        # in " & mountedVolumesString
            
    
    

# for row in cursor.execute("SELECT rowid, * FROM albums ORDER BY artist"):
#     print row



    if False:
        opts_dict = {'force_folder_scan': True, 'scan_hidden_files': False, 'depth_limit': 4, 'scan_packages': False, 'verbose_level': 3, 'do_recursion': True} 
        options = Bunch(**opts_dict)

        # print type(options), options.force_folder_scan

        args = [s]
        do_lsdb(options, args)
        
        do_lsdb(args, force_folder_scan=False, scan_hidden_files=False, depth_limit=4, scan_packages=False, verbose_level=3, do_recursion=True )
        
    
    # call lsdb once for each entry?

def xda2(cursor, sql):
    cursor.execute(sql)
    column_names =  [d[0] for d in cursor.description]
    return [dict(zip(column_names, r)) for r in cursor]

def xda(cursor, sql):
    cursor.execute(sql)
    return [r for r in cursor]
    

if __name__ == '__main__':
    do_metadata_query()
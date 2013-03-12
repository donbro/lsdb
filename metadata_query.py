#!/usr/bin/env python
# encoding: utf-8
"""
metadata_query.py

Created by donb on 2013-03-11.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

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

from PyObjCTools import AppHelper

# ws = NSWorkspace.sharedWorkspace() # .sharednotificationCenter()
# nc = ws.notificationCenter()
nc = NSNotificationCenter.defaultCenter()
# print nc

    

class MyError():
    def __init__(self, code, description=""):
        self.code = code
        self.description = description
        # print "init"
        
    def __str__(self):
        return "%s (%d)" %  (self.description,  self.code)
        
        
    def gathering_(self, notification):
        """DidUpdate"""
        # print "test_"   , notification
        print   notification.name() # NSMetadataQueryGatheringProgressNotification
        # print   "userInfo is: " , notification.userInfo()

    def did_update_(self, notification):
        """DidUpdate"""
        # print "test_"   , notification
        print   "name", notification.name()
        print   "userInfo is: " , notification.userInfo()
        
    def did_finish_(self, notification):
        print   notification.name() # NSMetadataQueryDidFinishGatheringNotification
        # print   "userInfo is: " , notification.userInfo()
        # Stops the event loop (if started by runConsoleEventLoop) or sends the NSApplication a terminate: message.
        didIDoIt = AppHelper.stopEventLoop()
        if didIDoIt: 
            print "Stops the event loop?"
        raise ValueError, "this will stop you!"

    #     
    # 
    # def calendarsChanged_(self, notification):
    #     print "c"
    # 
    # # @objc.typedSelector('v@0:@8') # objc.typedSelector
    # def mycallback_(self,note):
    #     print 'note'
    #     print note.description()
    #     

def a():
    a = MyError(1)

    query = NSMetadataQuery.alloc().init()
    q = 'kMDItemKind = "Aperture Library"'
    query.setPredicate_(NSPredicate.predicateWithFormat_( q ))

    scopes = [NSMetadataQueryLocalComputerScope]       
    # scopes = [NSMetadataQueryUserHomeScope]             

    query.setSearchScopes_( scopes )



    # class ThisEventLoopStopper(NSObject):
    #     def interpFinished_(self, notification):
    #         print "stopper"
    #         didIDoIt = AppHelper.stopEventLoop()
    #         print "didIDoIt", didIDoIt
    #         print "after stopper"
    #         raise ValueError, "this will stop you"

    # stopper = ThisEventLoopStopper.alloc().init()
    # print "this stopper is",  type(stopper), stopper
    # NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(stopper, 'interpFinished:', NSMetadataQueryDidFinishGatheringNotification, query)


    nc.addObserver_selector_name_object_(a, "did_finish:", NSMetadataQueryDidFinishGatheringNotification, query)
    nc.addObserver_selector_name_object_(a, "did_update:", NSMetadataQueryDidUpdateNotification, query)
    nc.addObserver_selector_name_object_(a, "gathering:", NSMetadataQueryGatheringProgressNotification, query)
    query.startQuery()

    # import time
    # while True: time.sleep(0.2)      # 0% CPU


    print "Listening for new tunes...."
    try:
        AppHelper.runConsoleEventLoop( mode = NSDefaultRunLoopMode)
    except ValueError, e:
        print "ValueError", e
    # except:
    #     pass
    print "finished with runConsoleEventLoop()"

    query.stopQuery()
    n = query.resultCount()
    for i in range(n):
        item = query.resultAtIndex_(i)
        # s = item.valueForAttribute_("kMDItemPath")
        d =  item.valuesForAttributes_( [  'kMDItemFSName',
                                            'kMDItemDisplayName',
                                            'kMDItemPath',
                                            'kMDItemFSCreationDate',
                                            'kMDItemContentTypeTree',
                                            'kMDItemFSContentChangeDate']) #    'kMDItemURL',      'kMDItemFSSize','kMDItemUsedDates',
        DoIt(i, d)

from PyObjCTools import Conversion
       

def DoIt(i, d):
    
    s = d['kMDItemPath']
    d2 = NSDictionary.dictionaryWithContentsOfFile_(s+"/Info.plist")

    e = Conversion.pythonCollectionFromPropertyList(d)
    e.update(Conversion.pythonCollectionFromPropertyList(d2))
    # print e 
    print "%2d" %  i, 
    print "%(kMDItemDisplayName)40s  %(CFBundleShortVersionString)s" % e


# 
# .............................
# 
# Functions for converting between Cocoa and pure Python data structures.
# 
# * ``propertyListFromPythonCollection(pyCol, conversionHelper=None) -> ocCol``
# 
#   Convert a Python collection (dictionary, array, tuple, string) into an 
#   Objective-C collection.
# 
#   If conversionHelper is defined, it must be a callable.  It will be called 
#   for any object encountered for which ``propertyListFromPythonCollection()``
#   cannot automatically convert the object.   The supplied helper function 
#   should convert the object and return the converted form.  If the conversion 
#   helper cannot convert the type, it should raise an exception or return None.
# 
# * ``pythonCollectionFromPropertyList(ocCol, conversionHelper=None) -> pyCol``
# 


        # NSData *plistXML = [[NSFileManager defaultManager] contentsAtPath:plistPath];


# {
#     CFBundleGetInfoString = "Aperture Library 2.1";
#     CFBundleShortVersionString = "2.1";
# }


# {
#     CFBundleGetInfoString = "Aperture Library 3.3.1";
#     CFBundleIdentifier = "com.apple.Aperture.library";
#     CFBundleName = "Aperture Library";
#     CFBundleShortVersionString = "3.3.1";
# }




# 
# 
# class untitled:
#   def __init__(self):
#       pass
# 
# 
# class untitledTests(unittest.TestCase):
#   def setUp(self):
#       pass
# 
# 
if __name__ == '__main__':
    a()
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
        print   "userInfo is: " , notification.userInfo()

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
        print "didIDoIt", didIDoIt
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
    # print a


    # nc.addObserver_selector_name_object_(a, "test:", NSWorkspaceActiveSpaceDidChangeNotification, objc.nil)


    # defNC.addObserver_selector_name_object_(self,
    #   'windowDidResize:',
    #   NSWindowDidResizeNotification,
    #   self)
  
    # nc.addObserver:observer
    #                          selector:@selector(applicationDidTerminate:)
    #                              name:@"NSWorkspaceDidTerminateApplicationNotification"
    #                            object:nil];
    
    # sys.exit()

    query = NSMetadataQuery.alloc().init()
    # print query
    q = 'kMDItemKind = "Aperture Library"'
    query.setPredicate_(NSPredicate.predicateWithFormat_( q ))

    # ValueError: 'NSInvalidArgumentException - Unable to parse the format string "\'kMDItemKind = "Aperture Library"\'"'


    # scopes = [NSMetadataQueryLocalComputerScope]        # count:  84
    scopes = [NSMetadataQueryUserHomeScope]             # count:  5

        # item:  /Users/donb/Pictures/Aperture Library—Photostream.aplibrary
        # item:  /Users/donb/character reference/All Naturals/Alanna Hensley - All Naturals.aplibrary
        # item:  /Users/donb/Corinne 58/Corinne 58.aplibrary
        # item:  /Users/donb/Teen Models Trisha/TeenModels - Trisha.aplibrary
        # item:  /Users/donb/Pictures/Aperture Library.aplibrary


    query.setSearchScopes_( scopes )

    # NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
    #     0.0, foo, 'doBadThingsNow:', None, False
    # )


    class ThisEventLoopStopper(NSObject):
        def interpFinished_(self, notification):
            print "stopper"
            didIDoIt = AppHelper.stopEventLoop()
            print "didIDoIt", didIDoIt
            print "after stopper"
            raise ValueError, "this will stop you"

    # stopper = ThisEventLoopStopper.alloc().init()
    # print "this stopper is",  type(stopper), stopper

    nc.addObserver_selector_name_object_(a, "did_finish:", NSMetadataQueryDidFinishGatheringNotification, query)
    nc.addObserver_selector_name_object_(a, "did_update:", NSMetadataQueryDidUpdateNotification, query)
    nc.addObserver_selector_name_object_(a, "gathering:", NSMetadataQueryGatheringProgressNotification, query)

    # NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(stopper, 'interpFinished:', NSMetadataQueryDidFinishGatheringNotification, query)

    query.startQuery()

    import time
    # while True: time.sleep(0.2)      # 0% CPU

    # while isDone == False:
    #     time.sleep(0.2) 

    # theRunLoop = NSRunLoop.currentRunLoop()
    # print dir(theRunLoop)
    # Runs the loop once, blocking for input in the specified mode until a given date.


    # * runConsoleEventLoop - run NSRunLoop.run() in a stoppable manner


    print "Listening for new tunes...."
    try:
        AppHelper.runConsoleEventLoop( mode = NSDefaultRunLoopMode)
    except ValueError, e:
        print "ValueError", e
    except:
        pass

    print "after runConsoleEventLoop()"




    query.stopQuery()
    # print dir(query)
    n = query.resultCount()
    # print "count: ", len(query.results())
    for i in range(n): # item in query.results():
        item = query.resultAtIndex_(i)
        print "item: ", i, 
        s = item.valueForAttribute_("kMDItemPath")
        print item.valuesForAttributes_( [  'kMDItemFSName',
                                            'kMDItemDisplayName',
                                            'kMDItemPath',
                                            'kMDItemFSCreationDate',
                                            'kMDItemContentTypeTree',
                                        
                                            'kMDItemFSContentChangeDate']) #    'kMDItemURL',      'kMDItemFSSize','kMDItemUsedDates',
        DoIt(s)
        # sys.exit()

def DoIt(s):

    # sys.exit()


    # s = "/Volumes/Romika/Aperture Libraries/Aperture Esquire.aplibrary/Info.plist"
    # 
    # s = "/Volumes/Taos/Aperture Libraries/Aperture Library copy.aplibrary/Info.plist"
    # 
    # s = u"/Volumes/Romika/Aperture Libraries/Aperture Library—indoor.aplibrary/Info.plist"

    d = NSDictionary.dictionaryWithContentsOfFile_(s+"/Info.plist")

    from PyObjCTools import Conversion

    e = Conversion.pythonCollectionFromPropertyList(d)
    # print d

    print e['CFBundleShortVersionString']


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
#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-03-11.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os


from Foundation import NSObject, NSNotificationCenter, NSMetadataQuery, NSPredicate, NSMetadataQueryUserHomeScope, \
        NSMetadataQueryDidFinishGatheringNotification
from PyObjCTools import AppHelper

# from ConsoleReactor import ConsoleReactor
# host = '127.0.0.1'
# port = 0
# interpreterPath = sys.executable
# scriptPath = unicode(os.path.abspath('tcpinterpreter.py'))
# commandReactor = ConsoleReactor.alloc().init()
# interp = AsyncPythonInterpreter.alloc().initWithHost_port_interpreterPath_scriptPath_commandReactor_(host, port, interpreterPath, scriptPath, commandReactor)
# interp.connect()

query = NSMetadataQuery.alloc().init()
query.setPredicate_(NSPredicate.predicateWithFormat_( 'kMDItemKind = "Aperture Library"' ))
scopes = [NSMetadataQueryUserHomeScope]             
query.setSearchScopes_( scopes )


class ThisEventLoopStopper(NSObject):
    def interpFinished_(self, notification):
        AppHelper.stopEventLoop()
stopper = ThisEventLoopStopper.alloc().init()

NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(stopper, 'interpFinished:', NSMetadataQueryDidFinishGatheringNotification, query)
query.startQuery()

# NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(stopper, 'interpFinished:', u'AsyncPythonInterpreterClosed', interp)
AppHelper.runConsoleEventLoop(installInterrupt=True)

query.stopQuery()
print "count: ", len(query.results())
for item in query.results():
    print "item: ", item.valueForAttribute_("kMDItemPath")

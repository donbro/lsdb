from PyObjCTools.TestSupport import *
from LaunchServices import *

class TestUTCoreTypes (TestCase):
    def testConstants(self):
        self.failUnlessIsInstance(kUTTypeItem, unicode)
        self.failUnlessIsInstance(kUTTypeContent, unicode)
        self.failUnlessIsInstance(kUTTypeCompositeContent, unicode)
        self.failUnlessIsInstance(kUTTypeApplication, unicode)
        self.failUnlessIsInstance(kUTTypeMessage, unicode)
        self.failUnlessIsInstance(kUTTypeContact, unicode)


        self.failUnlessIsInstance(kUTTypeFramework, unicode)
        self.failUnlessIsInstance(kUTTypeApplicationBundle, unicode)
        self.failUnlessIsInstance(kUTTypeApplicationFile, unicode)
        self.failUnlessIsInstance(kUTTypeVCard, unicode)
        self.failUnlessIsInstance(kUTTypeInkText, unicode)

if __name__ == "__main__":
    main()
from LaunchServices import kUTTypeApplication, kUTTypeData, \
                                    UTGetOSTypeFromString, UTTypeCopyDeclaringBundleURL,\
                                    UTTypeCopyDescription, UTTypeCopyDeclaration, UTTypeConformsTo, \
                                    LSCopyItemInfoForURL, kLSRequestExtension, kLSRequestTypeCreator
                                    # _LSCopyAllApplicationURLs


def DoSomeUTIStuff():
    """A Uniform Type Identifier (UTI) is a text string that uniquely identifies a given class or type of item."""
    
    ts1 = item_dict[NSURLLocalizedTypeDescriptionKey]    # eg, 'Folder'


    # conformance hierarchy
    #  A conformance hierarchy says that if type A is "above" type B then
    #   “all instances of type A are also instances of type B.”        

    #  UTCreateStringForOSType
    #  UTGetOSTypeFromString
    #  UTTypeConformsTo
    #  UTTypeCopyDeclaration
    #  UTTypeCopyDeclaringBundleURL
    #  UTTypeCopyDescription
    #  UTTypeCopyPreferredTagWithClass
    #  UTTypeCreateAllIdentifiersForTag
    #  UTTypeCreatePreferredIdentifierForTag
    #  UTTypeEqual',


    uti = item_dict[NSURLTypeIdentifierKey]     


    # NSLog(t)   
    # print type(t)
    # print ts1, uti

    uti_declaration =  UTTypeCopyDeclaration(uti)

    # print "UTTypeCopyDeclaration:", type(uti_declaration), uti_declaration
    # print "UTTypeCopyDeclaringBundleURL:", UTTypeCopyDeclaringBundleURL(uti)  # Folder, public.folder, 'publ'
    # print "UTTypeCopyDescription:", UTTypeCopyDescription(uti)
    # print "UTTypeConformsTo(uti, kUTTypeData):", UTTypeConformsTo(uti, kUTTypeData)


    # declaring bundle is, eg, file://localhost/Users/donb/Downloads/ComicBookLover.app/ or
    #                       file://localhost/System/Library/CoreServices/CoreTypes.bundle/


 
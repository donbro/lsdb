from Foundation import  NSURLNameKey, \
                        NSURLIsDirectoryKey,\
                        NSURLVolumeURLKey, \
                        NSURLLocalizedTypeDescriptionKey,\
                        NSURLTypeIdentifierKey,\
                        NSURLCreationDateKey,\
                        NSURLContentModificationDateKey,\
                        NSURLIsVolumeKey,  \
                        NSURLParentDirectoryURLKey


databaseAndURLKeys = [  ( 'file_name',            NSURLNameKey), 
                        (  None,                  NSURLIsDirectoryKey), 
                        (  None,                  NSURLVolumeURLKey), 
                        (  None,                  NSURLLocalizedTypeDescriptionKey), 
                        ( 'file_uti',             NSURLTypeIdentifierKey), 
                        ( 'file_create_date',     NSURLCreationDateKey), 
                        ( 'file_mod_date',        NSURLContentModificationDateKey), 
                        (  None,                  NSURLParentDirectoryURLKey), 
                        ( 'file_size',           'NSURLTotalFileSizeKey'),
                        ( 'file_id',             'NSFileSystemFileNumber'),
                        ( 'folder_id',           'NSFileSystemFolderNumber' ),
                        (  None,                  NSURLIsVolumeKey)                        
                    ]


enumeratorURLKeys = [t[1] for t in databaseAndURLKeys]

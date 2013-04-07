

    # def xx_pr6(self, l, v, folder_id, file_id, d, p, verbose_level_threshold=1):
    #     if self.verbose_level >= verbose_level_threshold:
    #         s =    "%-10s %-8s %7d %7d %s %s" % (l, v , folder_id, file_id, d,  p) 
    #         print s

    def xx_pr8(self, l, vol_id, item_dict, depth, verbose_level_threshold=1):

        file_mod_date    = item_dict[NSURLContentModificationDateKey]

        sa =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)  # needs a real NSDate here?

        # pathname         = item_dict["NSURLPathKey"]
        folder_id        = item_dict['NSFileSystemFolderNumber']
        filename         = item_dict[NSURLNameKey]
        file_id          = item_dict['NSFileSystemFileNumber']

        if self.verbose_level >= verbose_level_threshold:
            s = "%-14s %-8s %-7s %8d %8d %s %2d %s" % \
                    (l, d_lengths(ISS.folderContentsAtDepth), vol_id , folder_id, file_id, sa,  depth, filename) 
            print s

        
    def xx_pr8p(self, l, vol_id, item_dict, depth, verbose_level_threshold=1):
        """longest version prints full pathname"""

        file_mod_date    = item_dict[NSURLContentModificationDateKey]

        sa =  dateFormatters[0]['df'].stringFromDate_(file_mod_date)  # needs a real NSDate here?

        pathname         = item_dict["NSURLPathKey"]
        folder_id        = item_dict['NSFileSystemFolderNumber']
        # filename         = item_dict[NSURLNameKey]
        file_id          = item_dict['NSFileSystemFileNumber']

        if self.verbose_level >= verbose_level_threshold:
            s = "%-14s %-8s %-7s %8d %8d %s %2d %s" % \
                    (l, d_lengths(ISS.folderContentsAtDepth), vol_id , folder_id, file_id, sa,  depth, pathname) 
            print s



    def pr5(self, l, v, fid, d, p, verbose_level_threshold=1):
        if self.verbose_level >= verbose_level_threshold:
            s =    "%-10s %-8s %27s %s" % (l, v , d,  p) 
            s =    "%-10s %-8s %8d %s %s" % (l, v , fid, d,  p)   # not fixed 27 but varies with width of third string.
            print s

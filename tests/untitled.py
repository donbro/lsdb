#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-03-26.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os


def do_parse_argv(argv):
    
    
    from argparse import ArgumentParser
    parser = ArgumentParser(description="filesystem, library files and database multitool.")

    parser.add_argument("-s", "--server",
                       action="store", dest="server",
                       default="irc.freenode.net",
                       help="IRC server to connect to")

    parser.add_argument("-r", "--recursive",  dest="do_recursion",  
                        action="store_const", const=True, 
                        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,
                        default=False )

    parser.add_argument("-v", "--verbose", 
                        dest="verbose_level", 
        help="increment verbose count (verbosity) by one. "\
                "Normal operation is to output one status line per file. "\
                "One -v option will give you slightly more information on each file.  Two -v options "\
                " shows all debugging info available.", action="count" ) 

    parser.add_argument("-q", "--quiet", 
                        action="store_const", 
                        const=0, dest="verbose_level", default=1, 
                        help="Normal operation is to output one status line per file, status being \"inserted\", \"existing\", etc."
                        " This option will prevent any output to stdout, Significant errors are still output to stderr.") 


    def _depth_callback(option, opt_str, value, parser): # , cls):
        if value == "None" or value == "none":
            setattr(parser.values, option.dest, None)
        else:
            try:
                setattr(parser.values, option.dest, int(value))
            except:
                raise OptionValueError("%s value must be integer or None. %s: %r received."
                                   % (option.dest, str(type(value)), value) )


    # ValueError: 'unknown action "callback"'


    # parser.add_argument("-d", "--depth-limit", "--depth", dest="depth_limit", action="callback" , 
    #     callback=_depth_callback,
    #     help="limit recusion DEPTH. using DEPTH = 0 means process the directory only.  DEPTH=None means no depth limit (use with caution). "
    #     "Recursion is implied when any depth-limit is specified. default is %default.",
    #      metavar="DEPTH", type="string") 


    parser.add_argument("-f", "--force-folder-scan", dest="force_folder_scan", action = "store_true", 
        help="explicitly check contents of directories even if directory timestamp not newer than"
        "database value.  Normal operation does not check the contents of a directory if its timestamp equals"
        "that in the database.", 
        default=False) 
        
    parser.add_argument("-p", "--scan-packages", dest="scan_packages", action = "store_true", 
        help="scan contents of packages. Normal operation does not check the contents of packages.", 
        default=False) 
        
    parser.add_argument("-a", "--scan-hidden-files", dest="scan_hidden_files", action = "store_true", 
        help="Include directory entries whose names begin with a dot. Normal operation does not include hidden files.", 
        default=False) 


    
    (options, args) = parser.parse_known_args(argv)
    return (options, args)


if __name__ == '__main__':
    
    # argv = ["--help"]
    argv = ["-s MONDO", "-r", "-v"]
    
    # argv += [u"/Users/Volumes/donb/bittorrent"]


    (options, args) = do_parse_argv(argv)
    
    print options, args

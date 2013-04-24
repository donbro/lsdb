#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

"""
    do_parse_args.py
"""
import os
from argparse import ArgumentParser, Namespace

def do_parse_args(argv):


    parser = ArgumentParser(description="filesystem, library files and database multitool.")

    parser.add_argument("-r", "--recursive",  dest="do_recursion",  
                        action="store_const", const=True, 
                        help="Recursively process subdirectories. Recursion can be limited by setting DEPTH." ,
                        default=False )

    parser.add_argument("-v", "--verbose", 
                        action="count", dest="verbose_level", 
                        help="increment verbose count (verbosity) by one. "\
                        "Normal operation is to output one status line per file. "\
                        "One -v option will give you slightly more information on each file.  Two -v options "\
                        " shows all debugging info available.") 

    parser.add_argument("-q", "--quiet", 
                        action="store_const", 
                        const=0, dest="verbose_level", default=1, 
                        help="Normal operation is to output one status line per file, "
                                    "status being \"inserted\", \"existing\", etc."
                                    " This option will prevent any output to stdout, "
                                    "Significant errors are still output to stderr.") 

    # def _depth_callback(option, opt_str, value, parser): # , cls):
    #     if value == "None" or value == "none":
    #         setattr(parser.values, option.dest, None)
    #     else:
    #         try:
    #             setattr(parser.values, option.dest, int(value))
    #         except:
    #             raise OptionValueError("%s value must be integer or None. %s: %r received."
    #                                % (option.dest, str(type(value)), value) )

    # depth_limit=None,

    parser.add_argument("-d", "--depth-limit", "--depth", dest="depth_limit", action="store",
        help="limit recusion DEPTH. using DEPTH = 0 means process the directory only.  "
          "DEPTH=None means no depth limit (use with caution). "
        "Recursion is implied when any depth-limit is specified.",
         metavar="DEPTH", type=int) 


    parser.add_argument("-f", "--force-folder-scan", dest="force_folder_scan", action = "store_true", 
                        help="explicitly check contents of directories even if directory timestamp not newer than"
                        "database value.  Normal operation does not check the contents of a directory if its "
                        "timestamp equals that in the database.", 
                        default=False) 
        
    parser.add_argument("-p", "--scan-packages", dest="scan_packages", action = "store_true", 
        help="scan contents of packages. Normal operation does not check the contents of packages.", 
        default=False) 
        
    parser.add_argument("-a", "--scan-hidden-files", dest="scan_hidden_files", action = "store_true", 
                            help="""Include hidden entries, eg, those whose names begin
                                    with a dot or are otherwise hidden. Normal operation does not include hidden
                                    files.""", default=False) 
    
    return parser.parse_known_args(argv) # (options, args)

import unittest
class do_parse_args_TestCase( unittest.TestCase ):
    """ Class to test relation_dict """
    
    def test_010_do_parse_args(self):

        s = u'/Users/donb/Ashley+Roberts/'



        argv = []
        # argv = ["--help"]+[s]
        # argv = ["-rd 4"]
        argv = ["-d 2"]
        argv += ["-v"]
        argv += ["-v"]
        # argv += ["-v"]
        # argv += ["-a"]
        argv += ["-p"]
        # argv += ["-f"] 
        argv += [s]
        


        (options, args) = do_parse_args(argv)

        self.assertEqual(options, 
                Namespace(do_recursion=False, depth_limit=2, force_folder_scan=False, scan_hidden_files=False, scan_packages=True, verbose_level=2))
                
        self.assertEqual( args,  [u'/Users/donb/Ashley+Roberts/'] )
        

    def test_020_do_parse_args(self):

        argv = ["--help"]
        (options, args) = do_parse_args(argv)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(do_parse_args_TestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)  

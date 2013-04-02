#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by donb on 2013-03-26.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os


def main():

    r = set([
    "/Users/donb/projects"
    , "/Volumes/Brandywine/erin esurance/"

    , "/Volumes/Taos"
    , "/Volumes/Brandywine/erin esurance/"


    
    , u'/Volumes/Sapporo/TV Show/Winx Club/S01/Winx Club - 1x07 - Grounded (aka Friends in Need).avi'
    

    , u'/Volumes/Ulysses/TV Shows/'

    , "/"
    
    , u"/Users/donb"
    
    , u'/Volumes/Sacramento/Movies/The Dark Knight (2008) (720p).mkv'

    , "/Volumes/Dunharrow/pdf/Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf"


    , u'/Users/donb/projects/lsdb'
    
    , '~/dev-mac/sickbeard'
    
    , "/Users/donb/Downloads/Sick-Beard-master/sickbeard"
    
    , "/Volumes/Brandywine/TV Series/White Collar/S04"

    , u'/Users/donb/Downloads/incomplete'

    , u'/Volumes/Ulysses/TV Shows/Lost Girl/'

    , "/Volumes/Brandywine/erin esurance/"


    , "/Volumes/Ulysses/bittorrent/"
    
    , u"/Volumes/Romika/Movies/"


    , "."

    , "/Volumes/Katie"

    
    

    
    , u"/Volumes/Dunharrow/iTunes Dunharrow/TV Shows/The No. 1 Ladies' Detective Agency"
    
    , u"/Volumes/Romika/Movies/Animation | Simulation | Warrior"


    , "/Volumes/Romika/Aperture Libraries/"

    , "/Volumes/Ulysses/TV Shows/Nikita/Nikita.S03E01.1080p.WEB-DL.DD5.1.H.264-KiNGS.mkv"

    # s = "/Volumes/Romika/Aperture Libraries/Aperture Esquire.aplibrary"

    # test for "basepath is a directory and a package but we're not scanning packages."
    , u"/Users/donb/Documents/Delete Imported Items on matahari?.rtfd"

    , "."
    
    , "/Volumes/Chronos/TV Show"
    , "/Volumes/Ulysses/bittorrent"  ])
    
    import os

    t = []
    z = []
    for a in sorted(r):
        try:
            p = os.path.abspath(os.path.expanduser(a))
        
            os.stat(p)
            
            t.append(p)
        except OSError, e:
            print p, e
            z.append ( p )

    print "\n".join([repr(e) for e in t]) #  z
    
if __name__ == '__main__':
	main()


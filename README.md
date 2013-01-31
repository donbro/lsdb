# `lsdb`  


`lsdb` is a python/pyobjc command line utility for Macintosh that inspects files and directories and stores the file info and metadata in a MySQL database.


`lsdb` and its associated MySQL database `files` are part of a larger asset management system.

## installation

Source available via `github`. The lsdb git repo is:

    git clone git://github.com/donbro/lsdb.git

This package may be installed globally:

	cd lsdb
	python setup.py install

or locally:

	cd lsdb
    python setup.py install --prefix=${HOME}

or, to use it without installing, e.g., for development work:

	cd lsdb
	python setup.py develop

In this case the lsdb script points to the working version, not an installed version.
Installation from source

## License

Please read LICENSE.txt in this directory.

## database

The MySQL database can be created using

    vi `lsdb --create-tables`


## Basic usage

    import tvdb_api
    t = tvdb_api.Tvdb()
    episode = t['My Name Is Earl'][1][3] # get season 1, episode 3 of show
    print episode['episodename'] # Print episode name

Or, if you want to run in the background:

```
python -d -f /path/to/sabnzbd.ini
```


	(mysql-connector-python)genie:~/projects/lsdb (710) lsdb --help

	Usage: lsdb [options] [filename(s)] 

	Options:
	  --version             show program's version number and exit
	  -h, --help            show this help message and exit
	  -r, --recursive       Recursively process subdirectories. Recursion can be
	                        limited by setting DEPTH.
	  -v, --verbose         increment verbose count by one.  default=1
	  -q, --quiet           Normal operation is to output one status line per
	                        file, status being "inserted", "existing", etc. This
	                        option will prevent any output to stdout, Significant
	                        errors are still output to stderr.
	  -d DEPTH, --depth-limit=DEPTH, --depth=DEPTH
	                        limit recusion DEPTH. using DEPTH = 0 means process
	                        the directory only.  DEPTH=None means no depth limit
	                        (use with caution). Recursion is implied when any
	                        depth-limit is specified. default is none.
	  -f, --force-folder-scan
	                        explicitly check contents of directories even if
	                        directory timestamp not newer thandatabase value.
	                        Normal operation does not check the contents of a
	                        directory if its timestamp equalsthat in the database.
	                        default = False



## Advanced usage

Most of the documentation is in docstrings. The examples are tested (using doctest) so will always be up to date and working.

The docstring for `Tvdb.__init__` lists all initialisation arguments, including support for non-English searches, custom "Select Series" interfaces and enabling the retrieval of banners and extended actor information. You can also override the default API key using `apikey`, recommended if you're using `tvdb_api` in a larger script or application

Features include:

* automatically retrieves new episode torrent or nzb files
* can scan your existing library and then download any old seasons or episodes you're missing
* can watch for better versions and upgrade your existing episodes (to from TV DVD/BluRay for example)
* XBMC library updates, poster/fanart downloads, and NFO/TBN generation
* configurable episode renaming
* sends NZBs directly to SABnzbd, prioritizes and categorizes them properly
* available for any platform, uses simple HTTP interface
* can notify XBMC, Growl, or Twitter when new episodes are downloaded
* specials and double episode support


Sick Beard makes use of the following projects:

* [cherrypy][cherrypy]
* [Cheetah][cheetah]
* [simplejson][simplejson]
* [tvdb_api][tvdb_api]
* [ConfigObj][configobj]
* [SABnzbd+][sabnzbd]
* [jQuery][jquery]
* [Python GNTP][pythongntp]
* [SocksiPy][socks]
* [python-dateutil][dateutil]

## Dependencies

To run Sick Beard from source you will need Python 2.5+ and Cheetah 2.1.0+. The [binary releases][googledownloads] are standalone.

## Bugs

If you find a bug please report it or it'll never get fixed. Verify that it hasn't [already been submitted][googleissues] and then [log a new bug][googlenewissue]. Be sure to provide as much information as possible.

[cherrypy]: http://www.cherrypy.org
[cheetah]: http://www.cheetahtemplate.org/
[simplejson]: http://code.google.com/p/simplejson/ 
[tvdb_api]: http://github.com/dbr/tvdb_api
[configobj]: http://www.voidspace.org.uk/python/configobj.html
[sabnzbd]: http://www.sabnzbd.org/
[jquery]: http://jquery.com
[pythongntp]: http://github.com/kfdm/gntp
[socks]: http://code.google.com/p/socksipy-branch/
[dateutil]: http://labix.org/python-dateutil
[googledownloads]: http://code.google.com/p/sickbeard/downloads/list
[googleissues]: http://code.google.com/p/sickbeard/issues/list
[googlenewissue]: http://code.google.com/p/sickbeard/issues/entry
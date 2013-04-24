#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'lsdb==0.5','console_scripts','lsdb'
__requires__ = 'lsdb==0.5'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('lsdb==0.5', 'console_scripts', 'lsdb')()
)

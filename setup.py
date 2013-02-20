#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8

from setuptools import setup

# from files import __version__

setup(

    name='lsdb',
    version='0.5',
    # packages=['lsdb', ],
    license='LICENSE',
    description='lsdb is a python/pyobjc command line utility for Macintosh that inspects files and directories and stores the file info and metadata into a MySQL database.',
    long_description=open('README.md').read(),
    author='Don Brotemarkle',
    author_email='donb@terrestrialdownlink.com',
    url="git://github.com/donbro/lsdb.git",

    #install_requires=['other_dependency_a', 'other_dependency_b'],
    install_requires=[],

    modules=['lsdb'],
    
    entry_points = {
    
        'console_scripts': [
            'lsdb = lsdb:main',
            # 'lsdb = lsdb.files:main',
        ],
    }
)

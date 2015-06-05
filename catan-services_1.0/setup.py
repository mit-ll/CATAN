#!/usr/bin/env python
# © 2015 Massachusetts Institute of Technology

# Native
import os
from distutils.core import setup

# CATAN
import catan.globals as G


def get_data_files(rel_dir):
    """
        Get a list of data files to include in install package
    """
    install_list = []
    for x in os.walk(rel_dir):
        directory = x[0]
        install_files = []
        
        # Get all the .py files
        for filename in x[2]:
            if not filename.endswith(".pyc"):
                install_files.append( os.path.join(directory, filename) )
        
        if len(install_files) > 0:
            install_path = os.path.join(G.DIR_ROOT,directory)
            install_list.append( (install_path, install_files) )
        
    
    return install_list

data_files = []
data_files += get_data_files(G.DIR_EXAMPLES)
data_files += get_data_files(G.DIR_CONF)
data_files += get_data_files(G.DIR_BINARIES)
data_files += get_data_files(G.DIR_SCRIPTS)
# Web stuff
data_files += get_data_files("www")
data_files += get_data_files("cgi-bin")



setup(name='CATAN',
      version='1.0',
      description='This package contains all of the communication libraries for CATAN.',
      author='Chad Spensky',
      author_email='chad.spensky@ll.mit.edu',
      url='N/A',
      data_files = data_files,
      packages=['catan'],
     )

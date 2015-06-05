# © 2015 Massachusetts Institute of Technology

from distutils.core import setup, Extension

ax25mod = Extension('catanAX25', 
                    libraries=['ax25'],
		    sources=['ax25module.c'])

setup(name="CATAN_AX25_EXTENSIONS", 
      version='1.0', 
      description="This extension module allows access to ax25 amateur radio protocols for use with the CATAN project",
      author='Ben Bullough',
      author_email='ben.bullough@ll.mit.edu',
      url='N/A', 
      ext_modules=[ax25mod]
      )


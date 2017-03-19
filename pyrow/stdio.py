#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

from pyrow import pyrow
from ergmanager import ErgManager

def new_erg_callback():
    pass

def update_erg_callback(*args):
    print(args)

def main():
    ergman = ErgManager(pyrow,
                        new_callback=new_erg_callback, 
                        update_callback=update_erg_callback)

if __main__:
    main()

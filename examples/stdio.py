#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

from pyrow import pyrow
from pyrow.ergmanager import ErgManager

def new_erg_callback(*args):
    print("New ", *args)

def update_erg_callback(*args):
    print("Update: ", *args)

def main():
    ergman = ErgManager(pyrow,
                        add_callback=new_erg_callback,
                        update_callback=update_erg_callback)
    while True:
        a = input(str("Test-->"))
        print(a, "was entered\n")
        if a == '0':
            break
    ergman.stop()

if __name__ == "__main__":
    main()

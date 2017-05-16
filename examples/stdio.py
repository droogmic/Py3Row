#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

# pylint: disable=C0111,C0103

import time
#from pyrow import simpyrow as pyrow
from pyrow import pyrow as pyrow
from pyrow.ergmanager import ErgManager

def new_erg_callback(erg):
    print("New: {}".format(erg))

def update_erg_callback(erg):
    print("Update {}: {}".format(erg, erg.data))

def main():
    ergman = ErgManager(pyrow,
                        add_callback=new_erg_callback,
                        update_callback=update_erg_callback)

    try:
        while True:
            time.sleep(1)
        # a = input("0 to exit-->")
        # print("{} was entered!\n".format(a))
        # if a == '0':
        #     break
    except KeyboardInterrupt:
        ergman.stop()

if __name__ == "__main__":
    main()

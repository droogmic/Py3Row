#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

import socket
import json
import time
from pyrow import simpyrow as pyrow
from pyrow.ergmanager import ErgManager

HOST = ''
PORT = 1347

def send_socket(data_dict):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        json_payload = json.dumps(data_dict)
        s.connect((HOST, PORT))
        s.sendall(json_payload.encode())

def new_erg_callback(erg):
    send_socket(data_dict={
        'uid': str(erg),
        'data': "Added",
    })

def update_erg_callback(erg):
    send_socket(data_dict={
        'uid': str(erg),
        'data': erg.data,
    })

def main():
    ergman = ErgManager(pyrow,
                        add_callback=new_erg_callback,
                        update_callback=update_erg_callback)
    time.sleep(10)
    ergman.stop()

if __name__ == "__main__":
    main()

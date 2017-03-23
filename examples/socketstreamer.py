#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

import socket
import json
from pyrow.ergmanager import ErgManager

class ErgManagerSocketStream(ErgManager):

    def __init__(self, *args, host='', port='1347', **kwargs):

        self.host = host    # Symbolic name meaning all available interfaces
        self.port = port    # Arbitrary non-privileged port

        def new_update_callback(self, *args):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                json_payload = json.dumps({
                    'uid': args[0],
                    'data': args[1],
                })
                s.connect((self.host, self.port))
                s.sendall(json_payload.encode())
            kwargs['update_callback'](*args)

        kwargs['update_callback'] = new_update_callback
        super().__init__(*args, **kwargs)

#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

import threading
import queue
import time


class ErgManager(object):

    device_ergs = []
    pyrow_ergs = []

    def __init__(self, pyrow, *, add_callback, update_callback, checker_rate=5):
        """
        Sets up erg manager
        Creates threads for detecting ergs and getting their status'
        """
        self.pyrow = pyrow

        self.add_callback = add_callback
        self.update_callback = update_callback

        self.checker_rate = checker_rate

        self.status_q = queue.Queue()
        self.ergs_status = {}
        self.exit_requested = False
        self.threads = {
            'erg_check': threading.Thread(target=self.erg_checker),
            'status_get': threading.Thread(target=self.status_getter),
        }
        for t in self.threads.values():
            t.start()

        self.device_ergs = []
        self.pyrow_ergs = []

    def stop(self):
        self.status_q.put(None)
        for pyerg in self.pyrow_ergs:
            self.exit_requested = True
            pyerg.exit_requested = True
            for t in self.threads.values():
                t.join()

    def set_distance(self, **kwargs):
        for pyerg in self.pyrow_ergs:
            pyerg.set_workout(**kwargs)

    def erg_checker(self):
        while not self.exit_requested:
            print("checking")
            try:
                device_ergs = list(self.pyrow.find())
                if len(device_ergs) == 0:
                    exit("No ergs found.")
                # print("{} ergs found.".format(len(self.ergs)))
                for device_erg in device_ergs:
                    if device_erg not in self.device_ergs:
                        self.device_ergs.append(device_erg)
                        self.pyrow_ergs.append(Erg(self.pyrow, device_erg, self.status_q))
                        self.add_callback(self.pyrow_ergs[-1])
            except ConnectionError:
                pass

            time.sleep(self.checker_rate)

    def status_getter(self):
        while not self.exit_requested:
            item = self.status_q.get()
            if item is None:
                break
            self.ergs_status[item['erg_repr']] = item['status']
            self.update_callback(item['erg_repr'], item['status'])
            self.status_q.task_done()


class Erg(object):
    def __init__(self, pyrow, erg, status_q, rate=1):
        """
        Sets up erg
        """

        self.pyrow = pyrow

        self.device_erg = erg
        self.pyrow_erg = self.pyrow.PyRow(erg)

        self.status_q = status_q

        self.rate = rate

        self.exit_requested = False
        self.thread = threading.Thread(target=self.erg_monitor)
        self.thread.start()

        print("Setting up erg: {}".format(self.__repr__()))

    def __repr__(self):
        return self.device_erg.__repr__()

    def erg_monitor(self):

        #prime status number
        cstate = -1
        cstroke = -1
        cworkout = -1

        while not self.exit_requested:
            try:
                status = self.pyrow_erg.get_status(pretty=True)
                monitor = self.pyrow_erg.get_monitor(pretty=True)
                workout = self.pyrow_erg.get_workout(pretty=True)
                if ERG_state[status['status']] != 'Ready':
                    print("status: ", status)
                    print("monitor: ", monitor)
                    print("workout: ", workout)
                if workout['state'] == 11:
                    print(f"Workout erg {erg_num} finished")
                else:
                    s = {}
                    s['distance'] = monitor['distance']
                    s['pace'] = monitor['pace']
                    s['spm'] = monitor['spm']
                self.status_q.put({'erg_repr': self.device_erg.__repr__(), 'status': s})
            except ConnectionError as e:
                print(e)
            time.sleep(self.rate)

    def set_workout(**kwargs):
        erg.set_workout(**kwargs)

#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

import threading
import queue
import time


class ErgManager(object):

    def __init__(self, pyrow, *, add_callback, update_callback, check_rate=5, update_rate=1):
        """
        Sets up erg manager
        Creates threads for detecting ergs and getting their status'
        """
        self._pyrow = pyrow

        self.add_callback = add_callback
        self.update_callback = update_callback

        self.check_rate = check_rate
        self.update_rate = update_rate


        self._devices = []
        self._pyergs = []

        # self.ergs_status = {}
        self.exit_requested = False
        self._status_q = queue.Queue()
        self._threads = {
            'erg_check': threading.Thread(target=self._erg_checker),
            'status_get': threading.Thread(target=self._status_getter),
        }
        for t in self._threads.values():
            t.start()

    def stop(self):
        self._status_q.put(None)
        for pyerg in self._pyergs:
            self.exit_requested = True
            pyerg.exit_requested = True
            for t in self._threads.values():
                t.join()

    def set_distance(self, **kwargs):
        for pyerg in self._pyergs:
            pyerg.set_workout(**kwargs)

    def _erg_checker(self):
        while not self.exit_requested:
            print("Checking for ergs:")
            try:
                devices = list(self._pyrow.find())
                if len(devices) == 0:
                    exit("No ergs found.")
                # print("{} ergs found.".format(len(self.ergs)))
                for device in devices:
                    if device not in self._devices:
                        self._devices.append(device)
                        new_erg = Erg(self._pyrow, device, self._status_q, rate=self.update_rate)
                        self._pyergs.append(new_erg)
                        print("new_erg: ",new_erg)
                        self.add_callback(new_erg)
            except ConnectionError:
                pass

            time.sleep(self.check_rate)

    def _status_getter(self):
        while not self.exit_requested:
            item = self._status_q.get()
            if item is None:
                break
            # self.ergs_status[item['erg_repr']] = item['status']
            self.update_callback(item['erg_repr'], item['status'])
            self._status_q.task_done()


class Erg(object):
    def __init__(self, pyrow, erg, status_q, rate=1):
        """
        Sets up erg
        """
        self._pyrow = pyrow

        self._device = erg
        self._pyerg = self._pyrow.PyRow(erg)

        self.data = {}
        self._status_q = status_q

        self.rate = rate

        self.exit_requested = False
        self._thread = threading.Thread(target=self.erg_monitor)
        self._thread.start()

        print("Setting up erg: {}".format(self.__repr__()))

    def __repr__(self):
        return self._device.__repr__()

    def erg_monitor(self):

        #prime status number
        cstate = -1
        cstroke = -1
        cworkout = -1

        while not self.exit_requested:
            try:
                monitor = self._pyerg.get_monitor(pretty=True, forceplot=True)
                workout = self._pyerg.get_workout(pretty=True)
                erg = self._pyerg.get_erg(pretty=True)
                if monitor['status'] != 'Ready':
                    pass
                    # print("monitor: ", monitor)
                    # print("workout: ", workout)
                    # print("erg: ", erg)
                if workout['state'] == 'Workout end':
                    print("Workout erg {} finished".format(erg_num))
                else:
                    s = {}
                    s['distance'] = monitor['distance']
                    s['pace'] = monitor['pace']
                    s['spm'] = monitor['spm']
                self._status_q.put({'erg_repr': self.__repr__(), 'status': s})
            except ConnectionError as e:
                # TODO: determine
                print(e)
            time.sleep(self.rate)

    def set_workout(**kwargs):
        erg.set_workout(**kwargs)

#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

# pylint: disable=C0111,C0103

import threading
import queue
import time


class ErgManager(object):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, pyrow, *, add_callback, update_callback, check_rate=2, update_rate=0.5):
        """
        Sets up erg manager
        Creates threads for detecting ergs and getting their status'
        The callbaks are for the addition and update events of the ergs
        """
        self._pyrow = pyrow

        self.add_callback = add_callback
        self.update_callback = update_callback

        self.check_rate = check_rate
        self.update_rate = update_rate


        self._devices = []
        self.ergs = []

        self.exit_requested = False
        self._status_q = queue.Queue()
        self._threads = {
            'erg_check': threading.Thread(target=self._erg_checker),
            'status_get': threading.Thread(target=self._status_getter),
        }
        for name, t in self._threads.items():
            #t.daemon = True
            t.name = name
            t.start()

    def stop(self):
        self._status_q.put(None)
        self.exit_requested = True
        for _erg in self.ergs:
            _erg.exit_requested = True
            for name, t in self._threads.items():
                print("Waiting on thread-{}".format(name))
                t.join()

    def set_workout(self, **kwargs):
        for _erg in self.ergs:
            _erg.set_workout(**kwargs)

    def set_distance(self, distance):
        for _erg in self.ergs:
            _erg.set_workout(distance=distance)

    def get_names(self):
        return [_erg.name for _erg in self.ergs]

    def _erg_checker(self):
        while not self.exit_requested:
            # print("Checking for ergs:")
            try:
                devices = list(self._pyrow.find())
                if not devices:
                    pass
                    # print("No ergs found.")
                # print("{} ergs found.".format(len(self.ergs)))
                for device in devices:
                    # TODO use self.ergs instead of seperate devices list
                    if device.__repr__() not in self._devices:
                        self._devices.append(device.__repr__())
                        new_erg = Erg(
                            pyrow=self._pyrow,
                            device=device,
                            status_q=self._status_q,
                            rate=self.update_rate
                        )
                        self.ergs.append(new_erg)
                        new_name = self.add_callback(new_erg)
                        if new_name is not None:
                            if new_name not in self.get_names():
                                new_erg.name = new_name
                            else:
                                raise ValueError(
                                    "Name {} already exists".format(new_name))
            except ConnectionError:
                # print("Connection Error")
                raise
            time.sleep(self.check_rate)

    def _status_getter(self):
        while not self.exit_requested:
            item = self._status_q.get()
            if item is None:
                break
            self.update_callback(item)
            self._status_q.task_done()


class Erg(object):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, pyrow, device, status_q, rate=1):
        """
        Sets up erg
        """
        self._pyrow = pyrow

        self._device = device
        self._pyerg = self._pyrow.PyErg(device)

        self.id = self._device.__repr__()
        self.name = self._device.__repr__()
        self.data = {}
        self._status_q = status_q

        self.rate = rate

        self.exit_requested = False
        self._thread = threading.Thread(target=self.erg_monitor)
        self._thread.name = "erg_monitor - {}".format(self.id)
        self._thread.start()

        # print("Setting up erg: {}".format(self.__repr__()))

    def __repr__(self):
        return self.name
        #return self._device.__repr__()

    def erg_monitor(self):

        #prime status number
        cstate = -1
        cstroke = -1
        cworkout = -1

        while not self.exit_requested:
            try:
                monitor = self._pyerg.get_monitor(pretty=True, forceplot=True)
                workout = self._pyerg.get_workout(pretty=True)
                # erg = self._pyerg.get_erg(pretty=True)
                # print("monitor: ", monitor)
                # print("workout: ", workout)
                # print("erg: ", erg)
                self.data.update(monitor)
                self.data.update(workout)
                if workout['state'] == 'Workout end':
                    print("Workout erg {} finished".format(self))
                self._status_q.put(self)

            except ConnectionError as e:
                # TODO: determine
                # print(e)
                raise ConnectionError("Ergmanager line 139")

            time.sleep(self.rate)

    def set_workout(self, **kwargs):
        self._pyerg.set_workout(**kwargs)

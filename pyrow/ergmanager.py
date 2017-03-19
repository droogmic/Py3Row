#!/usr/bin/env python
#Copyright (c) 2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

import threading
import queue

#Create a dictionary of the different status states
ERG_state = ['Error', 'Ready', 'Idle', 'Have ID', 'N/A', 'In Use',
         'Pause', 'Finished', 'Manual', 'Offline']


ERG_stroke = ['Wait for min speed', 'Wait for acceleration', 'Drive', 'Dwelling', 'Recovery']

ERG_workout = ['Waiting begin', 'Workout row', 'Countdown pause', 'Interval rest',
           'Work time inverval', 'Work distance interval', 'Rest end time', 'Rest end distance',
           'Time end rest', 'Distance end rest', 'Workout end', 'Workout terminate',
           'Workout logged', 'Workout rearm']


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

        print("Connected to erg.")
        self.thread = threading.Thread(target=erg_monitor)
        self.thread.start()

    def __repr__(self):
        return self.device_erg.__repr__()

    def erg_monitor(self):

        #prime status number
        cstate = -1
        cstroke = -1
        cworkout = -1

        while not exit_requested:
            status = self.pyrow_erg.get_status()
            monitor = self.pyrow_erg.get_monitor()
            workout = self.pyrow_erg.get_workout()
            if ERG_state[status['status']] != 'Ready':
                print(ERG_state[status['status']])
                print(workout)
            if workout['state'] == 11:
                print(f"Workout erg {erg_num} finished")
            else:
                s = {}
                s['distance'] = monitor['distance']
                s['pace'] = monitor['pace']
                s['spm'] = monitor['spm']
            status_q.put({'erg_repr': self.device_erg.__repr__(), 'status': s})
            time.sleep(self.rate)

    def set_distance(distance):
        erg.set_workout(distance=distance)

class ErgManager(object):

    exit_requested = False

    status_q = queue.Queue()
    status = {}

    device_ergs = []
    pyrow_ergs = []

    def __init__(self, pyrow, *, add_callback, update_callback, checker_rate=2):
        """
        Sets up thread
        """
        self.pyrow = pyrow

        self.add_callback = add_callback
        self.update_callback = update_callback

        self.checker_rate = checker_rate

        self.threads = {
            'erg_checker': threading.Thread(target=erg_checker)
            'erg_status': threading.Thread(target=erg_status)
        }
        for t in self.threads.values():
            t.start()

        self.device_ergs = []
        self.pyrow_ergs = []

        self.ergs_status = {}

        # while not exit_requested:
        #     response = input("Please enter 0 to exit: \n")
        #     try:
        #         response = int(response)
        #             exit_requested = True
        #     except ValueError:
        #         print("Invalid number")

    def stop():
        for pyerg in self.pyrow_ergs:
            pyerg.status_q.put(None)
            for t in self.threads.values():
                t.join()

    def set_distance(distance=2000):
        for pyerg in self.pyrow_ergs:
            pyerg.set_distance(distance)

    def erg_checker():
        while not exit_requested:
            device_ergs = list(self.pyrow.find())
            if len(device_ergs) == 0:
                exit("No ergs found.")
            # print("{} ergs found.".format(len(self.ergs)))
            for device_erg in device_ergs:
                if device_erg not in self.device_ergs:
                    self.device_ergs.append(device_erg)
                    self.pyrow_ergs.append(Erg(self.pyrow, device_erg))
                    self.add_callback(self.pyrow_ergs[-1])

            time.sleep(self.checker_rate)

    def status_getter():
        while not exit_requested:
            item = self.status_q.get()
            if item is None:
                break
            self.ergs_status[item['erg_repr']] = item['status']
            self.update_callback(item['erg_repr'], item['status'])
            self.status_q.task_done()

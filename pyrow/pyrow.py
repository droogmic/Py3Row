#!/usr/bin/env python
#Copyright (c) 2011 Sam Gambrell, 2016-2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

# pylint: disable=C0103,R0912,R0913

"""
pyrow.py
Interface to concept2 indoor rower
"""

import datetime
import time
import sys

import usb.core
import usb.util
from usb import USBError

from pyrow.csafe import csafe_cmd

C2_VENDOR_ID = 0x17a4
MIN_FRAME_GAP = .050 #in seconds
INTERFACE = 0

ERG_MAPPING = {
    # List of stroke states
    'strokestate': [
        'Wait for min speed',
        'Wait for acceleration',
        'Drive',
        'Dwelling',
        'Recovery',
    ],
    # List of workout types
    'workouttype': [
        'Just Row / no splits',
        'Just Row / splits',
        'Fixed Distance / splits',
        'Fixed Distance / no splits',
        'Fixed Time / no splits',
        'Fixed Time Interval',
        'Fixed Distance Interval',
        'Variable Interval',
    ],
    # List of workout state
    'workoutstate': [
        'Waiting begin',
        'Workout row',
        'Countdown pause',
        'Interval rest',
        'Work time inverval',
        'Work distance interval',
        'Rest end time',
        'Rest end distance',
        'Time end rest',
        'Distance end rest',
        'Workout end',
        'Workout terminate',
        'Workout logged',
        'Workout rearm'
    ],
    # List of workout types
    'inttype': [
        'Time',
        'Distance',
        'Rest',
    ],
    # List of display types
    'displaytype': [
        'Standard',
        'Force/Velocity',
        'Paceboat',
        'Per Stroke',
        'Simple',
        'Target',
    ],
    # List of display units types
    'displayunitstype': [
        'Time/Meters',
        'Pace',
        'Watts',
        'Calories',
    ],
    # List of machine states
    'status': [
        'Error',
        'Ready',
        'Idle',
        'Have ID',
        'N/A',
        'In Use',
        'Pause',
        'Finished',
        'Manual',
        'Offline'
    ]
}

def checkvalue(value, label, minimum, maximum):
    """
    Checks that value is an integer and within the specified range
    """
    if not isinstance(value, int):
        raise TypeError(label)
    if  not minimum <= value <= maximum:
        raise ValueError(label + " outside of range")
    return True

def get_pretty(data_dict, pretty):
    """
    Makes data_dict values pretty
    """
    if pretty:
        for key in data_dict.keys():
            if key in ERG_MAPPING:
                try:
                    data_dict[key] = ERG_MAPPING[key][data_dict[key]]
                except IndexError:
                    # TODO, find exceptions and patch into ERG_MAPPING,found:
                    # inttype 255
                    pass
                    # print("IndexError")
    return data_dict

def find():
    """
    Returns list of pyusb Devices which are ergs.
    """
    try:
        ergs = usb.core.find(find_all=True, idVendor=C2_VENDOR_ID)
    # Checks for USBError 16: Resource busy
    except USBError as e:
        if e.errno != 16:
            raise ConnectionRefusedError("USB busy")
    if ergs is None:
        raise ValueError('Ergs not found')
    return ergs


class PyErg(object):
    """
    Manages low-level erg communication
    """
    def __init__(self, erg):
        """
        Configures usb connection and sets erg value
        """
        from warnings import warn

        if sys.platform != 'win32':
            try:
                #Check to see if driver is attached to kernel (linux)
                if erg.is_kernel_driver_active(INTERFACE):
                    erg.detach_kernel_driver(INTERFACE)
                else:
                    warn("DEBUG: usb kernel driver not on {}".format(sys.platform))
            except:
                raise

        #Claim interface (Needs Testing To See If Necessary)
        usb.util.claim_interface(erg, INTERFACE)

        #Linux throws error, reason unknown
        try:
            erg.set_configuration() #required to configure USB connection
            #Ubuntu Linux returns 'usb.core.USBError: Resource busy' but rest of code still works
        except USBError as e:
            warn("DEBUG: usb error whilst setting configuration, {}".format(e))
        # except Exception as e:
        #     if not isinstance(e, USBError):
        #         raise e

        self.erg = erg

        configuration = erg[0]
        iface = configuration[(0, 0)]
        self.inEndpoint = iface[0].bEndpointAddress
        self.outEndpoint = iface[1].bEndpointAddress

        self.__lastsend = datetime.datetime.now()

    @staticmethod
    def _checkvalue(*args, **kwargs):
        return checkvalue(*args, **kwargs)

    def get_monitor(self, forceplot=False, pretty=False):
        """
        Returns values from the monitor that relate to the current workout,
        optionally returns force plot data and stroke state. (* required)
        time: time in seconds
        distance: distance in meters
        spm: strokes per minute
        power: power in watts
        pace: seconds/500m
        calhr: calories burned per hour
        calories: calories burned
        heartrate: heartrate
        status
        if heartrate:
            forceplot: force plot data
            strokestate
        """

        command = ['CSAFE_PM_GET_WORKTIME', 'CSAFE_PM_GET_WORKDISTANCE', 'CSAFE_GETCADENCE_CMD',
                   'CSAFE_GETPOWER_CMD', 'CSAFE_GETCALORIES_CMD', 'CSAFE_GETHRCUR_CMD']

        if forceplot:
            command.extend(['CSAFE_PM_GET_FORCEPLOTDATA', 32, 'CSAFE_PM_GET_STROKESTATE'])
        results = self.send(command)

        monitor = {}
        monitor['time'] = (results['CSAFE_PM_GET_WORKTIME'][0] + \
            results['CSAFE_PM_GET_WORKTIME'][1])/100.

        monitor['distance'] = (results['CSAFE_PM_GET_WORKDISTANCE'][0] + \
            results['CSAFE_PM_GET_WORKDISTANCE'][1])/10.

        monitor['spm'] = results['CSAFE_GETCADENCE_CMD'][0]
        #Rowing machine always returns power as Watts
        monitor['power'] = results['CSAFE_GETPOWER_CMD'][0]
        if monitor['power']:
            monitor['pace'] = ((2.8 / results['CSAFE_GETPOWER_CMD'][0]) ** (1./3)) * 500
            monitor['calhr'] = results['CSAFE_GETPOWER_CMD'][0]  * (4.0 * 0.8604) + 300.
        else:
            monitor['pace'], monitor['calhr'] = 0, 0
        monitor['calories'] = results['CSAFE_GETCALORIES_CMD'][0]
        monitor['heartrate'] = results['CSAFE_GETHRCUR_CMD'][0]

        if forceplot:
            #get amount of returned data in bytes
            datapoints = results['CSAFE_PM_GET_FORCEPLOTDATA'][0] // 2
            monitor['forceplot'] = results['CSAFE_PM_GET_FORCEPLOTDATA'][1:(datapoints+1)]
            monitor['strokestate'] = results['CSAFE_PM_GET_STROKESTATE'][0]

        monitor['status'] = results['CSAFE_GETSTATUS_CMD'][0] & 0xF

        monitor = get_pretty(monitor, pretty)
        return monitor

    def get_forceplot(self, pretty=False):
        """
        Returns force plot data and stroke state
        """

        command = ['CSAFE_PM_GET_FORCEPLOTDATA', 32, 'CSAFE_PM_GET_STROKESTATE']
        results = self.send(command)

        forceplot = {}
        datapoints = results['CSAFE_PM_GET_FORCEPLOTDATA'][0] // 2
        forceplot['forceplot'] = results['CSAFE_PM_GET_FORCEPLOTDATA'][1:(datapoints+1)]
        forceplot['strokestate'] = results['CSAFE_PM_GET_STROKESTATE'][0]

        forceplot['status'] = results['CSAFE_GETSTATUS_CMD'][0] & 0xF

        forceplot = get_pretty(forceplot, pretty)
        return forceplot


    def get_workout(self, pretty=False):
        """
        Returns overall workout data
        """

        command = ['CSAFE_GETID_CMD', 'CSAFE_PM_GET_WORKOUTTYPE', 'CSAFE_PM_GET_WORKOUTSTATE',
                   'CSAFE_PM_GET_INTERVALTYPE', 'CSAFE_PM_GET_WORKOUTINTERVALCOUNT']
        results = self.send(command)

        workoutdata = {}
        workoutdata['userid'] = results['CSAFE_GETID_CMD'][0]
        workoutdata['type'] = results['CSAFE_PM_GET_WORKOUTTYPE'][0]
        workoutdata['state'] = results['CSAFE_PM_GET_WORKOUTSTATE'][0]
        workoutdata['inttype'] = results['CSAFE_PM_GET_INTERVALTYPE'][0]
        workoutdata['intcount'] = results['CSAFE_PM_GET_WORKOUTINTERVALCOUNT'][0]

        workoutdata['status'] = results['CSAFE_GETSTATUS_CMD'][0] & 0xF

        workoutdata = get_pretty(workoutdata, pretty)
        return workoutdata

    def get_erg(self, pretty=False):
        """
        Returns all erg data that is not related to the workout
        """

        command = ['CSAFE_GETVERSION_CMD', 'CSAFE_GETSERIAL_CMD', 'CSAFE_GETCAPS_CMD', 0x00]
        results = self.send(command)

        ergdata = {}
        #Get data from csafe get version command
        ergdata['mfgid'] = results['CSAFE_GETVERSION_CMD'][0]
        ergdata['cid'] = results['CSAFE_GETVERSION_CMD'][1]
        ergdata['model'] = results['CSAFE_GETVERSION_CMD'][2]
        ergdata['hwversion'] = results['CSAFE_GETVERSION_CMD'][3]
        ergdata['swversion'] = results['CSAFE_GETVERSION_CMD'][4]
        #Get data from csafe get serial command
        ergdata['serial'] = results['CSAFE_GETSERIAL_CMD'][0]
        #Get data from csafe get capabilities command
        ergdata['maxrx'] = results['CSAFE_GETCAPS_CMD'][0]
        ergdata['maxtx'] = results['CSAFE_GETCAPS_CMD'][1]
        ergdata['mininterframe'] = results['CSAFE_GETCAPS_CMD'][2]

        ergdata['status'] = results['CSAFE_GETSTATUS_CMD'][0] & 0xF

        ergdata = get_pretty(ergdata, pretty)
        return ergdata

    def get_status(self, pretty=False):
        """
        Returns the status of the erg
        """
        command = ['CSAFE_GETSTATUS_CMD', ]
        results = self.send(command)

        status = {}
        status['status'] = results['CSAFE_GETSTATUS_CMD'][0] & 0xF

        status = get_pretty(status, pretty)
        return status

    def set_clock(self):
        """
        Sets the erg clock to the computers current time and date
        """
        now = datetime.datetime.now() #Get current date and time

        command = ['CSAFE_SETTIME_CMD', now.hour, now.minute, now.second]
        command.extend(['CSAFE_SETDATE_CMD', (now.year-1900), now.month, now.day])

        self.send(command)

    def set_workout(self, program=None, workout_time=None, distance=None,
                    split=None,
                    pace=None, calpace=None, powerpace=None):
        """
        If machine is in the ready state, function will set the
        workout and display the start workout screen
        Choose one of:
        program: workout program 0 to 15
        workout_time: workout time as a list, [hours, minutes, seconds]
        distance: meters
        If workout_time or distance, optional: split
        One of the following for pace boat (optional):
        pace: seconds
        calpace: calories per hour
        powerpace: watts
        """
        self.send(['CSAFE_RESET_CMD'])
        command = []

        #Set Workout Goal
        if program != None:
            self._checkvalue(program, "Program", 0, 15)
        elif workout_time != None:
            if len(workout_time) == 1:
                #if only seconds in workout_time then pad minutes
                workout_time.insert(0, 0)
            if len(workout_time) == 2:
                #if no hours in workout_time then pad hours
                workout_time.insert(0, 0) #if no hours in workout_time then pad hours
            self._checkvalue(workout_time[0], "Time Hours", 0, 9)
            self._checkvalue(workout_time[1], "Time Minutes", 0, 59)
            self._checkvalue(workout_time[2], "Time Seconds", 0, 59)

            if workout_time[0] == 0 and workout_time[1] == 0 and workout_time[2] < 20:
                #checks if workout is < 20 seconds
                raise ValueError("Workout too short")

            command.extend(['CSAFE_SETTWORK_CMD', workout_time[0],
                            workout_time[1], workout_time[2]])

        elif distance != None:
            self._checkvalue(distance, "Distance", 100, 50000)
            command.extend(['CSAFE_SETHORIZONTAL_CMD', distance, 36]) #36 = meters

        #Set Split
        if split is not None:
            if workout_time is not None and program is None:
                split = int(split*100)
                #total workout workout_time (1 sec)
                time_raw = workout_time[0]*3600+workout_time[1]*60+workout_time[2]
                #split workout_time that will occur 30 workout_times (.01 sec)
                minsplit = int(time_raw/30*100+0.5)
                self._checkvalue(split, "Split Time", max(2000, minsplit), time_raw*100)
                command.extend(['CSAFE_PM_SET_SPLITDURATION', 0, split])
            elif distance is not None and program is None:
                minsplit = int(distance/30+0.5) #split distance that will occur 30 workout_times (m)
                self._checkvalue(split, "Split distance", max(100, minsplit), distance)
                command.extend(['CSAFE_PM_SET_SPLITDURATION', 128, split])
            else:
                raise ValueError("Cannot set split for current goal")


        #Set Pace
        if pace is not None:
            powerpace = int(round(2.8 / ((pace / 500.) ** 3)))
        elif calpace is not None:
            powerpace = int(round((calpace - 300.)/(4.0 * 0.8604)))
        if powerpace is not None:
            command.extend(['CSAFE_SETPOWER_CMD', powerpace, 88]) #88 = watts

        if program is None:
            program = 0

        command.extend(['CSAFE_SETPROGRAM_CMD', program, 0, 'CSAFE_GOINUSE_CMD'])

        self.send(command)

    def send(self, message):
        """
        Converts and sends message to erg; receives, converts, and returns ergs response
        """

        #Checks that enough time has passed since the last message was sent,
        #if not program sleeps till time has passed
        now = datetime.datetime.now()
        delta = now - self.__lastsend
        deltaraw = delta.seconds + delta.microseconds/1000000.
        if deltaraw < MIN_FRAME_GAP:
            time.sleep(MIN_FRAME_GAP - deltaraw)

        #convert message to byte array
        csafe = csafe_cmd.write(message)
        #sends message to erg and records length of message
        try:
            length = self.erg.write(self.outEndpoint, csafe, timeout=2000)
        # Checks for USBError 16: Resource busy
        except USBError as e:
            if e.errno != 19:
                raise ConnectionError("USB device disconected")
        #records time when message was sent
        self.__lastsend = datetime.datetime.now()

        response = []
        while not response:
            try:
                #recieves byte array from erg
                transmission = self.erg.read(self.inEndpoint, length, timeout=2000)
                response = csafe_cmd.read(transmission)
            except Exception as e:
                raise e
                #Replace with error or let error trigger?
                #No message was recieved back from erg
                # return []

        #convers byte array to response dictionary
        return response

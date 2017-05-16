#!/usr/bin/env python
#Copyright (c) 2016-2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code may not function as advertised.

import datetime
import time

import numpy as np

from pyrow.pyrow import get_pretty

STATUS = 9

def find(n=2):
    return range(0,n)

class PyErg(object):

    def __init__(self, erg):
        """
        Sets erg value
        """
        self.erg = erg
        self._start_time = time.time()
        self._factor = np.random.normal(1, 0.02)
        self.__lastsend = datetime.datetime.now()

    @classmethod
    def __checkvalue(self, value, label, minimum, maximum):
        """
        Checks that value is an integer and within the specified range
        """
        if type(value) is not int:
            raise TypeError(label)
        if  not minimum <= value <= maximum:
            raise ValueError(label + " outside of range")
        return True

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
        SPM = 30
        POWER = 150
        CAL_TO_TIME = 1

        VEL = lambda x: 4 + np.sin(np.pi*x) + 0.5*np.cos(np.pi*x/480) + 0.5*np.exp(-x/120) - 5*np.exp(-x/4)
        VELOCITY = 5
        DIST = lambda x: 40.3 + 4*x - 60*np.exp(-x/120) + 20*np.exp(-x/4) + 80*np.sin(np.pi*x/480) - 0.3*np.cos(np.pi*x)

        elapsed_time = round(time.time() - self._start_time,2)
        monitor = {}
        monitor['time'] = round(elapsed_time, 2)
        monitor['distance'] = int(round(self._factor*DIST(elapsed_time)))
        monitor['spm'] = SPM
        #Rowing machine always returns power as Watts
        monitor['power'] = POWER
        if monitor['power']:
            monitor['pace'] = ((2.8 / POWER) ** (1./3)) * 500
            monitor['calhr'] = POWER  * (4.0 * 0.8604) + 300.
        else:
            monitor['pace'], monitor['calhr'] = 0, 0
        monitor['calories'] = round(CAL_TO_TIME * elapsed_time)
        monitor['heartrate'] = 100
        if forceplot:
            monitor['forceplot'] = [1]*32
            monitor['strokestate'] = 4
        # 1 or 5
        monitor['status'] = STATUS

        monitor = get_pretty(monitor, pretty)
        return monitor

    def get_forceplot(self, pretty=False):
        """
        Returns force plot data and stroke state
        """
        forceplot = {}
        forceplot['forceplot'] = [1]*32
        forceplot['strokestate'] = 4
        forceplot['status'] = STATUS

        forceplot = get_pretty(forceplot, pretty)
        return forceplot

    def get_workout(self, pretty=False):
        """
        Returns overall workout data
        """
        workoutdata = {}
        workoutdata['userid'] = 0
        workoutdata['type'] = 0
        workoutdata['state'] = 1
        workoutdata['inttype'] = 1
        workoutdata['intcount'] = 0
        workoutdata['status'] = STATUS

        workoutdata = get_pretty(workoutdata, pretty)
        return workoutdata

    def get_erg(self, pretty=False):
        """
        Returns all erg data that is not related to the workout
        """
        ergdata = {}
        #Get data from csafe get version command
        ergdata['mfgid'] = 0
        ergdata['cid'] = 0
        ergdata['model'] = 0
        ergdata['hwversion'] = 0
        ergdata['swversion'] = 0
        #Get data from csafe get serial command
        ergdata['serial'] = 0
        #Get data from csafe get capabilities command
        ergdata['maxrx'] = 0
        ergdata['maxtx'] = 0
        ergdata['mininterframe'] = 0
        ergdata['status'] = STATUS

        ergdata = get_pretty(ergdata, pretty)
        return ergdata

    def get_status(self, pretty=False):
        """
        Returns the status of the erg
        """
        status = {}
        status['status'] = STATUS

        status = get_pretty(status, pretty)
        return status

    def set_clock(self):
        """
        Sets the erg clock to the computers current time and date
        """
        now = datetime.datetime.now() #Get current date and time

    def set_workout(self, program=None, workout_time=None,
                    distance=None, split=None,
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
        #Set Workout Goal
        if program != None:
            self.__checkvalue(program, "Program", 0, 15)
        elif workout_time != None:
            if len(workout_time) == 1:
                #if only seconds in workout_time then pad minutes
                workout_time.insert(0, 0)
            if len(workout_time) == 2:
                #if no hours in workout_time then pad hours
                workout_time.insert(0, 0) #if no hours in workout_time then pad hours
            self.__checkvalue(workout_time[0], "Time Hours", 0, 9)
            self.__checkvalue(workout_time[1], "Time Minutes", 0, 59)
            self.__checkvalue(workout_time[2], "Time Seconds", 0, 59)

            if workout_time[0] == 0 and workout_time[1] == 0 and workout_time[2] < 20:
                #checks if workout is < 20 seconds
                raise ValueError("Workout too short")

            # TODO
            # command.extend(['CSAFE_SETTWORK_CMD', workout_time[0],
            #                 workout_time[1], workout_time[2]])

        elif distance != None:
            self.__checkvalue(distance, "Distance", 100, 50000)
            # command.extend(['CSAFE_SETHORIZONTAL_CMD', distance, 36]) #36 = meters

        #Set Split
        if split != None:
            if workout_time != None and program == None:
                split = int(split*100)
                #total workout workout_time (1 sec)
                time_raw = workout_time[0]*3600+workout_time[1]*60+workout_time[2]
                #split workout_time that will occur 30 workout_times (.01 sec)
                minsplit = int(time_raw/30*100+0.5)
                self.__checkvalue(split, "Split Time", max(2000, minsplit), time_raw*100)
                # TODO
                # command.extend(['CSAFE_PM_SET_SPLITDURATION', 0, split])
            elif distance != None and program == None:
                minsplit = int(distance/30+0.5) #split distance that will occur 30 workout_times (m)
                self.__checkvalue(split, "Split distance", max(100, minsplit), distance)
                # TODO
                # command.extend(['CSAFE_PM_SET_SPLITDURATION', 128, split])
            else:
                raise ValueError("Cannot set split for current goal")


        #Set Pace
        if pace != None:
            powerpace = int(round(2.8 / ((pace / 500.) ** 3)))
        elif calpace != None:
            powerpace = int(round((calpace - 300.)/(4.0 * 0.8604)))
        if powerpace != None:
            pass
            # TODO
            # command.extend(['CSAFE_SETPOWER_CMD', powerpace, 88]) #88 = watts

        if program == None:
            program = 0

        # TODO
        # command.extend(['CSAFE_SETPROGRAM_CMD', program, 0, 'CSAFE_GOINUSE_CMD'])

        # self.send(command)

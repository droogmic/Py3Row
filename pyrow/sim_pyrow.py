#!/usr/bin/env python
#Copyright (c) 2016-2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code may not function as advertised.

import datetime
import time

#Create a dictionary of the statuses and stoke states
status = ['Error', 'Ready', 'Idle', 'Have ID', 'N/A', 'In Use',
         'Pause', 'Finished', 'Manual', 'Offline']
strokestate = ['Wait for min speed', 'Wait for acceleration', 'Drive', 'Dwelling', 'Recovery']

def find(n=10):
    return range(0,n)

class PyRow(object):

    def __init__(self, erg):
        """
        Sets erg value
        """

        self.erg = erg
        self._start_time = time.time()
        self.__lastsend = datetime.datetime.now()

    def __checkvalue(self, value, label, minimum, maximum):
        """
        Checks that value is an integer and within the specified range
        """

        if type(value) is not int:
            raise TypeError(label)
        if  not minimum <= value <= maximum:
            raise ValueError(label + " outside of range")
        return True

    def get_monitor(self, forceplot=False):
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
        """

        DIST_TO_TIME = 10
        SPM = 20
        POWER = 150
        CAL_TO_TIME = 1

        elapsed_time = round(time.time() - self._start_time,2)
        monitor = {}

        monitor['time'] = elapsed_time
        monitor['distance'] = round(DIST_TO_TIME * elapsed_time)
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
        monitor['status'] = 1 & 0xF

        return monitor

    def get_force_plot(self):
        """
        Returns force plot data and stroke state
        """

        forceplot = {}
        forceplot['forceplot'] = [1]*32
        forceplot['strokestate'] = 4
        forceplot['status'] = 1 & 0xF

        return forceplot

    def get_workout(self):
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

        return workoutdata

    def get_erg(self):
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

        return ergdata

    def get_status(self):
        """
        Returns the status of the erg
        """

        command = ['CSAFE_GETSTATUS_CMD', ]
        results = self.send(command)

        status = {}
        status['status'] = results['CSAFE_GETSTATUS_CMD'][0] & 0xF

        return status


    def set_clock(self):
        """
        Sets the erg clock to the computers current time and date
        """

        now = datetime.datetime.now() #Get current date and time

        command = ['CSAFE_SETTIME_CMD', now.hour, now.minute, now.second]
        command.extend(['CSAFE_SETDATE_CMD', (now.year-1900), now.month, now.day])

        self.send(command)

    def set_workout(self, program=None, workout_time=None, distance=None, split=None,
                    pace=None, calpace=None, powerpace=None):
        """
        If machine is in the ready state, function will set the
        workout and display the start workout screen
        """

        self.send(['CSAFE_RESET_CMD'])
        command = []

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

            command.extend(['CSAFE_SETTWORK_CMD', workout_time[0],
                            workout_time[1], workout_time[2]])

        elif distance != None:
            self.__checkvalue(distance, "Distance", 100, 50000)
            command.extend(['CSAFE_SETHORIZONTAL_CMD', distance, 36]) #36 = meters

        #Set Split
        if split != None:
            if workout_time != None and program == None:
                split = int(split*100)
                #total workout workout_time (1 sec)
                time_raw = workout_time[0]*3600+workout_time[1]*60+workout_time[2]
                #split workout_time that will occur 30 workout_times (.01 sec)
                minsplit = int(time_raw/30*100+0.5)
                self.__checkvalue(split, "Split Time", max(2000, minsplit), time_raw*100)
                command.extend(['CSAFE_PM_SET_SPLITDURATION', 0, split])
            elif distance != None and program == None:
                minsplit = int(distance/30+0.5) #split distance that will occur 30 workout_times (m)
                self.__checkvalue(split, "Split distance", max(100, minsplit), distance)
                command.extend(['CSAFE_PM_SET_SPLITDURATION', 128, split])
            else:
                raise ValueError("Cannot set split for current goal")


        #Set Pace
        if pace != None:
            powerpace = int(round(2.8 / ((pace / 500.) ** 3)))
        elif calpace != None:
            powerpace = int(round((calpace - 300.)/(4.0 * 0.8604)))
        if powerpace != None:
            command.extend(['CSAFE_SETPOWER_CMD', powerpace, 88]) #88 = watts

        if program == None:
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
        length = self.erg.write(self.outEndpoint, csafe, timeout=2000)
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

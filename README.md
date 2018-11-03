# Py3Row

[![Build Status](https://travis-ci.org/droogmic/Py3Row.svg?branch=master)](https://travis-ci.org/droogmic/Py3Row)

#### NOTE
+ This code may not function as advertised.
+ This documentation is incomplete
+ Please submit PRs to improve this

## ABOUT

### Code history
Original Site: http://www.newhavenrowingclub.org/pyrow/  
Forked from: https://github.com/uvd/PyRow

### Description
PyRow is python3 code that allows one to interact with a Concept2 Rowing Ergometer PM3, PM4 or PM5 monitor using python.  PyRow sends and receives information from the Ergometer using csafe commands or built in functions (listed below).  The goal of PyRow is to allow for multiple platforms to have easy access to the Ergometer.

### CSAFE
For an explanation of the csafe commands please use the documentation found here:
- Concept2 PM Communication Interface Definition
  - [Original](http://www.concept2.com/service/software/software-development-kit) (Need to download the SDK to get the document)
  - [Local saved in 2016-12](docs/Concept2PMCommInterfaceDef.pdf)
- [Communications Specification for Fitness Equipment](http://www.fitlinxx.com/CSAFE/)

## LICENSE
Copyright (c) 2011 - 2015, Sam Gambrell
Copyright (c) 2016 - 2017, Michael Droogleever
Licensed under the Simplified BSD License.

## REQUIREMENTS
Py3Row has not been widely tested but should be able to work on any machine that can run Python & PyUSB. This has not been tested and confirmed.

### Tested Configurations

#### ArchLinux
`# sudo pacman -S python libusb`
or
`# sudo pacman -S python libusb python-pyusb` (unstested)
- [Python](http://python.org/) (Tested with 3.5.2)
- [libusb](http://www.libusb.org/) (1.0.21-1 from core)
- [Walac's PyUSB](https://github.com/walac/pyusb) (1.0.0) or [PyUsb](https://github.com/pyusb/pyusb) (1.0.3) via pip install pyusb

#### Linux and PyUSB Access denied (insufficient permissions)
Sometimes the administration roles for python to access usb devices are too strict and pyusb generates the following error:
- usb.core.USBError: [Errno 13] Access denied (insufficient permissions)

When this occurs, use `lsusb` to see if the Concept2 device is found and what bus # and device # it is.  Once you have those two numbers run the udevadm command to get the specific information.  Follow this example:

`lsusb`

`...
Bus 006 Device 045: ID 17a4:0001 Concept2 Performance Monitor 3...`

note bus # and device # and then do the following:

`udevadm info -a -p $(udevadm info -q path -n /dev/bus/usb/006/045)`

This will show you the idVendor, idProduct and other information about the Performance Monitor. From this you can create a rule for that device in `/etc/udev/rules.d/10-local.rules` with the following line matching the information you get from udevadm.  You shouldn't have to change the idVendor but the idProduct might be different from this example.

`SUBSYSTEMS=="usb", ENV{DEVTYPE}=="usb_device", ATTRS{idVendor}=="17a4", ATTRS{idProduct}=="0001", GROUP="plugdev", MODE="777"`

Make sure your system has plugdev group and your userid is in the group too.

## INSTALLING
+ After the software has become stable the software will be packaged as a module, you can try using `pip install -e git+https://github.com/droogmic/Py3Row.git#egg=pyrow`.  
+ For now copying he pyrow directory and importing will work.

Include PyRow in your code with the following line of code:
`from pyrow import pyrow`


## RUNNING
`pyrow.find()` - returns an array of all the ergs currently connected to the computer

---------------------------------------

`pyrow.PyErg(erg)` - creates an object for communicating with the erg, erg is obtained from the pyrow.find() function
 ex: creating a pyrow object from the first erg found
   ergs = pyrow.find()
   erg = pyrow.pyrow(ergs[0])

---------------------------------------

`pyrow.PyErg.get_status()` - returns status of machine as a number
  - 0 = 'Error'
  - 1 = 'Ready'
  - 2 = 'Idle'
  - 3 = 'Have ID'
  - 4 = 'N/A'
  - 5 = 'In Use'
  - 6 = 'Pause'
  - 7 = 'Finished'
  - 8 = 'Manual'
  - 9 = 'Offline'

---------------------------------------

`pyrow.PyErg.get_monitor(forceplot=False)` - returns data from the monitor in dictionary format, keys listed below with descriptions
  - time = Monitor time in seconds
  - distance = Monitor distance in meters
  - spm = Strokes per Minute
  - power = Power in watts
  - pace = /500m pace
  - calhr = Calories Burned per Hours
  - calories = Total Calories Burned
  - heartrate = Current Heart Rate
  - status = Machine Status
 If keyvalue forceplot is set to true
  - forceplot = Force Plot Data
  - strokestate = Stroke State

---------------------------------------

`pyrow.PyErg.get_forceplot()` - returns force plot data and stroke state in dictionary format, keys listed below with descriptions
  - forceplot = Force Plot Data (array varying in length from 0 to 16)
  - strokestate = Stroke State
  - status = Machine status

---------------------------------------

`pyrow.PyErg.get_workout()` - returns data related to the overall workout in dictionary format, keys listed below with descriptions
  - userid = User ID
  - type = Workout Type
  - state = Workout State
  - inttype = Interval Type
  - intcount = Workout Interval Count
  - status = Machine Status

---------------------------------------

`pyrow.PyErg.get_erg()` - returns non workout related data about the erg in dictionary format, keys listed below with descriptions
  - mfgid = Manufacturing ID
  - cid = CID
  - model = Erg Model
  - hwversion = Hardware Version
  - swversion = Software Version
  - serial = Ascii Serial Number
  - maxrx = Max Rx Frame
  - maxtx = Max Tx Frame
  - mininterframe = Min Interframe
  - status = Machine status

---------------------------------------

`pyrow.PyErg.set_clock()` - sets the clock on the erg equal to the clock on the computer

---------------------------------------

`pyrow.PyErg.set_workout()` - if machine is in the ready state function will set the workout and display the start workout screen, allowable parameters are listed below (the current PM SDK does not allow for setting invervaled workouts)

**Choose one**

  `program=programNumber` - number from 0 to 10 (15 if the log card is installed), 1 thru 10 relate to workouts saved in the monitor.

  `time=[hours, minutes, seconds]` - Min allowable is 20 sec & max allowable is 9:59:59.

  `distance=meters` - Min allowable is 100 and max allowable is 20000.

 **Not required, can only chose if time or distance is set**

  `split=seconds` - If time is set or meters if distance is set, must be less than the total goal and greater
         than or equal to 20 seconds or 100 meters, cannot occur more then 30 times during the workout, time
         has a resolution of .01 sec

 **Not required, chose one**

  `pace=seconds` - Seconds for pace boat to complete 500 meters (/500m)
  `powerpace=watts` - Watts for pace boat to generate
  `calpace=cal` - Calories per hour for pace boat to burn

 ex: set a 2000m workout with a 500m split and a pace boat with a 2 minute pace (120 seconds)

  `erg.set_workout(distance=2000, split=500, pace=120)`

---------------------------------------

`pyrow.PyErg.send(command)` - sends a csafe command to the rowing machine and returns the result. The command is an array and
 results are returned as a dictionary with the key being the csafe command name

 ex: setting a workout of 10 minutes with a split of 1 minute (60 seconds)

    command = ['CSAFE_SETTWORK_CMD', 0, 10, 0,'CSAFE_PM_SET_SPLITDURATION', 0, 60]
    erg.send(command)

 ex: getting pace and printing it out

    command = ['CSAFE_GETPACE_CMD',]
    result = erg.send(command)
    print("Stroke Pace = " + str(result['CSAFE_GETPACE_CMD'][0]))
    print("Stroke Units = " + str(result['CSAFE_GETPACE_CMD'][1]))

## FILES

`pyrow`
+ `pyrow.py` - file to be loaded by user, used to connect to erg and send/receive data on a low-level
+ `simpyrow.py` - file to be loaded by user, used to simulate erg communication on a low-level
+ `ergmanager.py` - file to be loaded by user, used to connect to erg and send/receive data on a high-level
+ `csafe`
  - `csafe_cmd.py` - converts between csafe commands and byte arrays for pyrow.py, user does not need to load this file directly
  - `csafe_dic.py` - contains dictionaries of the csafe commands to be used by csafe_cmd.py, user does not need to load this file directly

`tests` - contains unittests

`examples`
+ `stdio.py` - User I/O demo
+ `socketstream.py`
+ `socketstreamer.py`
+ `superceded`
  - `strokelog.py` - an example program that records time, distance, strokes per min, pace, and force plot data for each stroke to a csv file
  - `statshow.py` - an example program that displays the current machine, workout, and stroke status

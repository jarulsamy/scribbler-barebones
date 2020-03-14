# -*- coding: utf-8 -*-

__AUTHOR__ = "Joshua Arulsamy"

from struct import unpack
from myro.globalvars import *

import time
import os
import serial
import threading


class Robot(object):
    _app = None
    _joy = None
    _cal = None

    def __init__(self):
        """
        Base robot class.
        """
        self.lock = threading.Lock()

    # def initializeRemoteControl(self, password):
    #     self.chat = Chat(self.getName(), password)

    def processRemoteControlLoop(self, threaded=1):
        if threaded:
            self.thread = BackgroundThread(self.processRemoteControl, 1)  # seconds
            self.thread.start()
        else:
            while 1:
                self.processRemoteControl()

    def processRemoteControl(self):
        messages = self.chat.receive()
        # print "process", messages
        for _from, message in messages:
            if message.startswith("robot."):
                # For user IM messages
                # print ">>> self." + message[6:]
                retval = eval("self." + message[6:])
                name, domain = _from.split("@")
                # print "sending:", pickle.dumps(retval)
                self.chat.send(name.lower(), pickle.dumps(retval))

    def translate(self, amount):
        raise AttributeError("this method needs to be written")

    def rotate(self, amount):
        raise AttributeError("this method needs to be written")

    def move(self, translate, rotate):
        raise AttributeError("this method needs to be written")

    # def beep(self, duration, frequency1, frequency2=None):
    #     import myro.graphics
    #     print("beep!")
    #     return myro.graphics._tkCall(myro.graphics._beep, duration, frequency1, frequency2)

    def getLastSensors(self):
        """ Should not get the current, but the last. This is default behavior. """
        return self.get("all")

    def update(self):
        """ Update the robot """
        raise AttributeError("this method needs to be written")

    # The rest of these methods are just rearrangements of the above
    def getVersion(self):
        """ Returns robot version information. """
        return self.get("version")

    def getLight(self, *position):
        """ Return the light readings. """
        return self.get("light", *position)

    def getIR(self, *position):
        """ Returns the infrared readings. """
        return self.get("ir", *position)

    def getDistance(self, *position):
        """ Returns the S2 Distance readings. """
        return self.getDistance(*position)

    def getLine(self, *position):
        """ Returns the line sensor readings. """
        return self.get("line", *position)

    def getStall(self):
        """ Returns the stall reading. """
        return self.get("stall")

    def getInfo(self, *item):
        """ Returns the info. """
        retval = self.get("info", *item)
        retval["myro"] = __VERSION__
        return retval

    def getName(self):
        """ Returns the robot's name. """
        return self.get("name")

    def getPassword(self):
        """ Returns the robot's password. """
        return self.get("password")

    def getForwardness(self):
        """ Returns the robot's directionality. """
        return self.get("forwardness")

    def getAll(self):
        return self.get("all")

    def setLED(self, position, value):
        return self.set("led", position, value)

    def setName(self, name):
        return self.set("name", name)

    def setForwardness(self, value):
        return self.set("forwardness", value)

    def setVolume(self, value):
        return self.set("volume", value)

    def setStartSong(self, songName):
        return self.set("startsong", songName)

    def forward(self, speed=1, interval=None):
        self.move(speed, 0)
        if interval is not None:
            time.sleep(interval)
            self.stop()

    def backward(self, speed=1, interval=None):
        self.move(-speed, 0)
        if interval is not None:
            time.sleep(interval)
            self.stop()

    def turn(self, direction, value=0.8, interval=None):
        if type(direction) in [float, int]:
            retval = self.move(0, direction)
        else:
            direction = direction.lower()
            if direction == "left":
                retval = self.move(0, value)
            elif direction == "right":
                retval = self.move(0, -value)
            elif direction in ["straight", "center"]:
                retval = self.move(0, 0)  # aka, stop!
            else:
                retval = "error"
        if interval is not None:
            time.sleep(interval)
            self.stop()
        return retval

    def turnLeft(self, speed=1, interval=None):
        retval = self.move(0, speed)
        if interval is not None:
            time.sleep(interval)
            self.stop()
        return retval

    def turnRight(self, speed=1, interval=None):
        retval = self.move(0, -speed)
        if interval is not None:
            time.sleep(interval)
            self.stop()
        return retval

    def stop(self):
        return self.move(0, 0)

    def motors(self, left, right):
        trans = (right + left) / 2.0
        rotate = (right - left) / 2.0
        return self.move(trans, rotate)

    def restart(self):
        pass

    def close(self):
        pass

    def open(self):
        pass

    def playSong(self, song, wholeNoteDuration=0.545):
        """ Plays a song [(freq, [freq2,] duration),...] """
        # 1 whole note should be .545 seconds for normal
        for tuple in song:
            self.playNote(tuple, wholeNoteDuration)

    def playNote(self, tuple, wholeNoteDuration=0.545):
        if len(tuple) == 2:
            (freq, dur) = tuple
            self.beep(dur * wholeNoteDuration, freq)
        elif len(tuple) == 3:
            (freq1, freq2, dur) = tuple
            self.beep(dur * wholeNoteDuration, freq1, freq2)


# class BufferedRead:
#     def __init__(self, serial, size, start=1):
#         self.serial = serial
#         self.size = size
#         if start:
#             self.data = self.serial.read(size)
#         else:
#             self.data = ""

#     def __getitem__(self, position):
#         """ Return an element of the string """
#         while position >= len(self.data):
#             #self.data += self.serial.read(self.size - len(self.data))
#             self.data += self.serial.read(self.size - len(self.data))
#             # print "      length so far = ", len(self.data), " waiting for total = ", self.size
#         return self.data[position]

#     def __len__(self):
#         """ Lie. Tell them it is this long. """
#         return self.size


def _commport(s):
    if type(s) == int:
        return 1
    if type(s) == str:
        s = s.replace("\\", "")
        s = s.replace(".", "")
        if s.lower().startswith("com") and s[3:].isdigit():
            return 1
        if s.startswith("/dev/"):
            return 1
    return 0


def isTrue(value):
    """
    Returns True if value is something we consider to be "on".
    Otherwise, return False.
    """
    if type(value) == str:
        return value.lower() == "on"
    elif value:
        return True
    return False


class Scribbler(Robot):
    SOFT_RESET = 33
    GET_ALL = 65
    GET_ALL_BINARY = 66
    GET_LIGHT_LEFT = 67
    GET_LIGHT_CENTER = 68
    GET_LIGHT_RIGHT = 69
    GET_LIGHT_ALL = 70
    GET_IR_LEFT = 71
    GET_IR_RIGHT = 72
    GET_IR_ALL = 73
    GET_LINE_LEFT = 74
    GET_LINE_RIGHT = 75
    GET_LINE_ALL = 76
    GET_STATE = 77
    GET_NAME1 = 78
    GET_NAME2 = 64
    GET_STALL = 79
    GET_INFO = 80
    GET_DATA = 81

    GET_PASS1 = 50
    GET_PASS2 = 51

    GET_RLE = 82  # a segmented and run-length encoded image
    GET_IMAGE = 83  # the entire 256 x 192 image in YUYV format
    GET_WINDOW = 84  # the windowed image (followed by which window)
    GET_DONGLE_L_IR = 85  # number of returned pulses when left emitter is turned on
    GET_DONGLE_C_IR = 86  # number of returned pulses when center emitter is turned on
    GET_DONGLE_R_IR = 87  # number of returned pulses when right emitter is turned on
    GET_WINDOW_LIGHT = 88  # average intensity in the user defined region
    GET_BATTERY = 89  # battery voltage
    GET_SERIAL_MEM = 90  # with the address returns the value in serial memory
    GET_SCRIB_PROGRAM = 91  # with offset, returns the scribbler program buffer
    GET_CAM_PARAM = 92  # with address, returns the camera parameter at that address

    GET_BLOB = 95

    SET_PASS1 = 55
    SET_PASS2 = 56
    SET_SINGLE_DATA = 96
    SET_DATA = 97
    SET_ECHO_MODE = 98
    SET_LED_LEFT_ON = 99
    SET_LED_LEFT_OFF = 100
    SET_LED_CENTER_ON = 101
    SET_LED_CENTER_OFF = 102
    SET_LED_RIGHT_ON = 103
    SET_LED_RIGHT_OFF = 104
    SET_LED_ALL_ON = 105
    SET_LED_ALL_OFF = 106
    SET_LED_ALL = 107
    SET_MOTORS_OFF = 108
    SET_MOTORS = 109
    SET_NAME1 = 110
    SET_NAME2 = 119  # set name2 byte
    SET_LOUD = 111
    SET_QUIET = 112
    SET_SPEAKER = 113
    SET_SPEAKER_2 = 114

    SET_DONGLE_LED_ON = 116  # turn binary dongle led on
    SET_DONGLE_LED_OFF = 117  # turn binary dongle led off
    SET_RLE = 118  # set rle parameters
    SET_DONGLE_IR = 120  # set dongle IR power
    SET_SERIAL_MEM = 121  # set serial memory byte
    SET_SCRIB_PROGRAM = 122  # set scribbler program memory byte
    SET_START_PROGRAM = 123  # initiate scribbler programming process
    SET_RESET_SCRIBBLER = 124  # hard reset scribbler
    SET_SERIAL_ERASE = 125  # erase serial memory
    SET_DIMMER_LED = 126  # set dimmer led
    SET_WINDOW = 127  # set user defined window
    SET_FORWARDNESS = 128  # set direction of scribbler
    SET_WHITE_BALANCE = 129  # turn on white balance on camera
    SET_NO_WHITE_BALANCE = 130  # diable white balance on camera (default)
    SET_CAM_PARAM = (
        131  # with address and value, sets the camera parameter at that address
    )

    GET_JPEG_GRAY_HEADER = 135
    GET_JPEG_GRAY_SCAN = 136
    GET_JPEG_COLOR_HEADER = 137
    GET_JPEG_COLOR_SCAN = 138

    SET_PASS_N_BYTES = 139
    GET_PASS_N_BYTES = 140
    GET_PASS_BYTES_UNTIL = 141

    GET_VERSION = 142

    GET_IR_MESSAGE = 150
    SEND_IR_MESSAGE = 151
    SET_IR_EMITTERS = 152

    SET_START_PROGRAM2 = 153  # initiate scribbler2 programming process
    SET_RESET_SCRIBBLER2 = 154  # hard reset scribbler2
    SET_SCRIB_BATCH = 155  # upload scribbler2 firmware
    GET_ROBOT_ID = 156
    SET_VOLUME = 160  # Format 160 volume (0-100) Percent Volume Level
    SET_PATH = 161  # Format 161 begin_or_end speed         0            1           2
    #                                begin=0 end=1   hSpeedByte lSpeedByte
    SET_MOVE = 162  # Format 162 type hXByte lXByte hYByte lYByte
    SET_ARC = 163  # Format 163 type hXByte lXByte hYByte lYByte hRadByte lRadByte
    SET_TURN = 164  # Format 164 type hAngleByte lAngleByte
    GET_POSN = 165  # Format 165
    SET_POSN = 166  # Format 166 x0Byte x1Byte x2Byte x3Byte y0Byte y1Byte y2Byte y3Byte
    GET_ANGLE = 167  # Format 167
    SET_ANGLE = 168  # Format 168 angle0Byte angle1Byte angle2Byte angle3Byte
    GET_MIC_ENV = 169  # Format 169
    GET_MOTOR_STATS = 170  # Format 170
    GET_ENCODERS = 171  # Format 171 type

    GET_IR_EX = 172  # Format 172 side type thres
    GET_LINE_EX = 173  # Format 173 side type thres
    GET_DISTANCE = 175  # Format 175 side

    PACKET_LENGTH = 9
    BEGIN_PATH = 0  # Used with SET_PATH to say beginning of a path
    END_PATH = 1  # Used with SET_PATH to say end of a path
    BY = 4  # Used in movement commands, by means how much you wish to move by
    TO = 2  # Used in movement commands, to means the heading you want to turn to
    DEG = 1  # Used in movement commands, specifies using degress instead of S2 angle units

    def __init__(self, serialport=None, baudrate=38400):
        Robot.__init__(self)

        # Camera Addresses
        # self.CAM_PID = 0x0A
        # self.CAM_PID_DEFAULT = 0x76

        # self.CAM_VER = 0x0B
        # self.CAM_VER_DEFAULT = 0x48

        # self.CAM_BRT = 0x06
        # self.CAM_BRT_DEFAULT = 0x80

        # self.CAM_EXP = 0x10
        # self.CAM_EXP_DEFAULT = 0x41

        # self.CAM_COMA = 0x12
        # self.CAM_COMA_DEFAULT = 0x14
        # self.CAM_COMA_WHITE_BALANCE_ON = (self.CAM_COMA_DEFAULT | (1 << 2))
        # self.CAM_COMA_WHITE_BALANCE_OFF = (self.CAM_COMA_DEFAULT & ~(1 << 2))

        # self.CAM_COMB = 0x13
        # self.CAM_COMB_DEFAULT = 0xA3
        # self.CAM_COMB_GAIN_CONTROL_ON = (self.CAM_COMB_DEFAULT | (1 << 1))
        # self.CAM_COMB_GAIN_CONTROL_OFF = (self.CAM_COMB_DEFAULT & ~(1 << 1))
        # self.CAM_COMB_EXPOSURE_CONTROL_ON = (self.CAM_COMB_DEFAULT | (1 << 0))
        # self.CAM_COMB_EXPOSURE_CONTROL_OFF = (self.CAM_COMB_DEFAULT & ~(1 << 0))

        self.ser = None
        self.requestStop = 0
        self.debug = 0
        self._lastTranslate = 0
        self._lastRotate = 0
        self._volume = 0
        self.emitters = 0x1 | 0x2 | 0x4
        if serialport is None:
            if "MYROROBOT" in os.environ:
                serialport = os.environ["MYROROBOT"]
                print("Connecting to", serialport)
            else:
                serialport = ask("Port", useCache=1)
        # Deal with requirement that Windows "COM#" names where # >= 9 needs to
        # be in the format "\\.\COM#"
        hasPort = True
        if type(serialport) == str and serialport.lower().startswith("com"):
            portnum = int(serialport[3:])
        elif isinstance(serialport, int):  # allow integer input
            portnum = serialport
        else:
            hasPort = False
        if hasPort:
            if portnum >= 10:
                serialport = r"\\.\COM%d" % (portnum)
        self.serialPort = serialport
        self.baudRate = baudrate
        self.open()

        robot = self
        self._fudge = list(range(4))
        self._oldFudge = list(range(4))
        self.dongle = None
        self.dongle_version = 0
        self.imagewidth = 0
        self.imageheight = 0

        info = self.getInfo()
        if "fluke" in list(info.keys()):
            self.dongle = info["fluke"]
            print("You are using fluke firmware", info["fluke"])
        elif "dongle" in list(info.keys()):
            self.dongle = info["dongle"]
            print("You are using fluke firmware", info["dongle"])
        if self.dongle is not None:
            self.dongle_version = list(map(int, self.dongle.split(".")))
            if self.dongle_version >= [3, 0, 0]:
                self.imagewidth = 1280
                self.imageheight = 800
            else:
                self.imagewidth = 256
                self.imageheight = 192

            # Turning on White Balance, Gain Control, and Exposure Control
            # self.set_cam_param(self.CAM_COMA, self.CAM_COMA_WHITE_BALANCE_ON)
            # self.set_cam_param(self.CAM_COMB, self.CAM_COMB_GAIN_CONTROL_ON |
            #                    self.CAM_COMB_EXPOSURE_CONTROL_ON)
            # # Config grayscale on window 0, 1, 2
            # conf_gray_window(self, 0, 2, 0, self.imagewidth /
            #                  2, self.imageheight - 1, 1, 1)
            # conf_gray_window(self, 1, self.imagewidth / 4, 0, self.imagewidth /
            #                  4 + self.imagewidth / 2 - 2, self.imageheight - 1, 1, 1)
            # conf_gray_window(self, 2, self.imagewidth / 2, 0,
            #                  self.imagewidth - 2, self.imageheight - 1, 1, 1)
            # # conf_gray_window(self.ser, 0, 2,   0, 128, 191, 1, 1)
            # # conf_gray_window(self.ser, 1, 64,  0, 190, 191, 1, 1)
            # # conf_gray_window(self.ser, 2, 128, 0, 254, 191, 1, 1)
            # set_ir_power(self.ser, 135)
            # self.conf_rle(delay=90, smooth_thresh=4,
            #               y_low=0, y_high=255,
            #               u_low=51, u_high=136,
            #               v_low=190, v_high=255)

        self.robotinfo = {}
        if "robot" in list(info.keys()):
            self.robotinfo = info["robot"]
            if "robot-version" in list(info.keys()):
                print("You are using scribbler firmware", info["robot-version"])
            elif "api" in list(info.keys()):
                print("You are using scribbler firmware", info["api"])
            self.restart()
            self.loadFudge()

    def search(self):
        answer = _askQuestion(
            title="Search for " + self.serialPort,
            question="Press the red resest button on the robot\nPress OK when ready to search",
            answers=["OK", "Cancel"],
        )
        if answer != "OK":
            raise KeyboardInterrupt
        for x in range(1, 21):
            if x >= 10:
                port = r"\\.\COM%d" % x
            else:
                port = "COM" + str(x)
            prettyPort = "COM" + str(x)
            print(
                "Searching on port %s for robot named '%s'..."
                % (prettyPort, self.serialPort)
            )
            try:
                self.ser = serial.Serial(port, timeout=10)
            except KeyboardInterrupt:
                raise
            except serial.SerialException:
                print(
                    "   Serial element not found. If this continues, remove/replace serial device..."
                )
                continue
            self.ser.baudrate = self.baudRate
            # assume that it has been running for at least a second!
            time.sleep(1)
            lines = self.ser.readlines()
            lines = "".join(lines)
            if "IPRE" in lines:
                position = lines.index("IPRE")
                name = lines[position + 4: position + 9 + 4]
                name = name.replace("\x00", "")
                name = name.strip()
                s = port.replace("\\", "")
                s = s.replace(".", "")
                print("   Found robot named", name, "on port", s, "!")
                if name == self.serialPort:
                    self.serialPort = port
                    self.ser.timeout = 10
                    s = self.serialPort.replace("\\", "")
                    s = s.replace(".", "")
                    _askQuestion(
                        'You can use "%s" from now on, like this:\n   initialize("%s")'
                        % (s, s),
                        answers=["Ok"],
                    )
                    return
                else:
                    self.ser.close()
        raise ValueError("Couldn't find robot named '%s'" % self.serialPort)

    def open(self):
        try:
            if self.serialPort == robot.ser.portstr:
                robot.ser.close()
                print("Closing serial port...")
                time.sleep(1)
        except KeyboardInterrupt:
            raise
        except Exception:
            pass
        if not _commport(self.serialPort):
            self.search()
        else:
            while 1:
                try:
                    self.ser = serial.Serial(self.serialPort, timeout=10)
                    # for directly connected scribler-2's
                    self.ser.setDTR(0)

                    break
                except KeyboardInterrupt:
                    raise
                except serial.SerialException:
                    print(
                        "   Serial element not found. If this continues, remove/replace serial device..."
                    )
                    try:
                        self.ser.close()
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        pass
                    try:
                        del self.ser
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        pass
                    time.sleep(1)
                except Exception:
                    print("Waiting on port...", self.serialPort)
                    try:
                        self.ser.close()
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        pass
                    try:
                        del self.ser
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        pass
                    time.sleep(1)
        self.ser.baudrate = self.baudRate
        # self.restart()

    def close(self):
        self.ser.close()

    def manual_flush(self):
        old = self.ser.timeout
        # self.ser.setTimeout(.5)
        self.ser.timeout = 0.5
        l = "a"
        count = 0
        while len(l) != 0 and count < 50000:
            l = self.ser.read(1)
            count += len(l)
        # self.ser.setTimeout(old)
        self.ser.timeout = old

    def restart(self):

        self.manual_flush()
        self.setEchoMode(0)  # send command to get out of broadcast; turn off echo
        time.sleep(0.25)  # give it some time
        while 1:
            self.ser.flushInput()  # flush "IPREScribby"...
            self.ser.flushOutput()
            time.sleep(1.2)  # give it time to see if another IPRE show up
            if self.ser.inWaiting() == 0:  # if none, then we are out of here!
                break
            print("Waking robot from sleep...")
            self.setEchoMode(0)  # send command to get out of broadcast; turn off echo
            time.sleep(0.25)  # give it some time
        self.ser.flushInput()
        self.ser.flushOutput()
        self.stop()
        self.set("led", "all", "off")
        self.beep(0.03, 784)
        self.beep(0.03, 880)
        self.beep(0.03, 698)
        self.beep(0.03, 349)
        self.beep(0.03, 523)
        name = self.get("name")
        print("Hello, I'm %s!" % name)

    def beep(self, duration, frequency, frequency2=None):

        self.lock.acquire()  # print "locked acquired"

        old = self.ser.timeout
        self.ser.timeout = duration + 2

        if frequency2 is None:
            self._set_speaker(int(frequency), int(duration * 1000))
        else:
            self._set_speaker_2(int(frequency), int(frequency2), int(duration * 1000))

        v = self.ser.read(Scribbler.PACKET_LENGTH + 11)

        # if self.debug:
        #     print(["0x%x" % ord(x) for x in v])

        self.ser.timeout = old
        self.lock.release()

    def get(self, sensor="all", *position):
        sensor = sensor.lower()
        if sensor == "config":
            if self.dongle is None:
                return {"ir": 2, "line": 2, "stall": 1, "light": 3}
            else:
                return {
                    "ir": 2,
                    "line": 2,
                    "stall": 1,
                    "light": 3,
                    "battery": 1,
                    "obstacle": 3,
                    "bright": 3,
                }
        elif sensor == "stall":
            retval = self._get(Scribbler.GET_ALL, 11)  # returned as bytes
            self._lastSensors = retval  # single bit sensors
            return retval[10]
        elif sensor == "forwardness":
            if read_mem(self.ser, 0, 0) != 0xDF:
                retval = "fluke-forward"
            else:
                retval = "scribbler-forward"
            return retval
        elif sensor == "startsong":
            # TODO: need to get this from flash memory
            return "tada"
        elif sensor == "version":
            # TODO: just return this version for now; get from flash
            return __REVISION__.split()[1]
        elif sensor == "data":
            return self.getData(*position)
        elif sensor == "info":
            return self.getInfo(*position)
        elif sensor == "name":
            c = self._get(Scribbler.GET_NAME1, 8)
            c += self._get(Scribbler.GET_NAME2, 8)
            c = "".join([chr(x) for x in c if "0" <= chr(x) <= "z"]).strip()
            return c
        elif sensor == "volume":
            return self._volume
        elif sensor == "battery":
            return self.getBattery()
        else:
            if len(position) == 0:
                if sensor == "light":
                    return self._get(Scribbler.GET_LIGHT_ALL, 6, "word")
                elif sensor == "line":
                    return self._get(Scribbler.GET_LINE_ALL, 2)
                elif sensor == "ir":
                    return self._get(Scribbler.GET_IR_ALL, 2)
                elif sensor == "obstacle":
                    return [
                        self.getObstacle("left"),
                        self.getObstacle("center"),
                        self.getObstacle("right"),
                    ]
                elif sensor == "distance":
                    return [self.getDistance("left"), self.getDistance("right")]
                elif sensor == "bright":
                    return [
                        self.getBright("left"),
                        self.getBright("middle"),
                        self.getBright("right"),
                    ]
                elif sensor == "all":
                    retval = self._get(Scribbler.GET_ALL, 11)  # returned as bytes
                    self._lastSensors = retval  # single bit sensors
                    if self.dongle is None:
                        return {
                            "light": [
                                retval[2] << 8 | retval[3],
                                retval[4] << 8 | retval[5],
                                retval[6] << 8 | retval[7],
                            ],
                            "ir": [retval[0], retval[1]],
                            "line": [retval[8], retval[9]],
                            "stall": retval[10],
                        }
                    else:
                        return {
                            "light": [
                                retval[2] << 8 | retval[3],
                                retval[4] << 8 | retval[5],
                                retval[6] << 8 | retval[7],
                            ],
                            "ir": [retval[0], retval[1]],
                            "line": [retval[8], retval[9]],
                            "stall": retval[10],
                            "obstacle": [
                                self.getObstacle("left"),
                                self.getObstacle("center"),
                                self.getObstacle("right"),
                            ],
                            "bright": [
                                self.getBright("left"),
                                self.getBright("middle"),
                                self.getBright("right"),
                            ],
                            "blob": self.getBlob(),
                            "battery": self.getBattery(),
                        }
                else:
                    raise "invalid sensor name: '%s'"
            retvals = []
            for pos in position:
                if sensor == "light":
                    values = self._get(Scribbler.GET_LIGHT_ALL, 6, "word")
                    if pos in [0, "left"]:
                        retvals.append(values[0])
                    elif pos in [1, "middle", "center"]:
                        retvals.append(values[1])
                    elif pos in [2, "right"]:
                        retvals.append(values[2])
                    elif pos is None or pos == "all":
                        retvals.append(values)
                elif sensor == "ir":
                    values = self._get(Scribbler.GET_IR_ALL, 2)
                    if pos in [0, "left"]:
                        retvals.append(values[0])
                    elif pos in [1, "right"]:
                        retvals.append(values[1])
                    elif pos is None or pos == "all":
                        retvals.append(values)
                elif sensor == "line":
                    values = self._get(Scribbler.GET_LINE_ALL, 2)
                    if pos in [0, "left"]:
                        retvals.append(values[0])
                    elif pos in [1, "right"]:
                        retvals.append(values[1])
                elif sensor == "obstacle":
                    return self.getObstacle(pos)
                elif sensor == "bright":
                    return self.getBright(pos)
                elif sensor == "picture":
                    return self.takePicture(pos)
                else:
                    raise "invalid sensor name: '%s'"
            if len(retvals) == 0:
                return None
            elif len(retvals) == 1:
                return retvals[0]
            else:
                return retvals

    def getData(self, *position):
        if len(position) == 0:
            return self._get(Scribbler.GET_DATA, 8)
        else:
            retval = []
            for p in position:
                retval.append(self._get(Scribbler.GET_DATA, 8)[p])
            if len(retval) == 1:
                return retval[0]
            else:
                return retval

    def getInfo(self, *item):
        # retval = self._get(Scribbler.GET_INFO, mode="line")

        oldtimeout = self.ser.timeout
        # self.ser.setTimeout(4)
        self.ser.timeout = 4

        # self.ser.flushInput()
        # self.ser.flushOutput()

        self.manual_flush()
        # have to do this twice since sometime the first echo isn't
        # echoed correctly (spaces) from the scribbler

        # self.ser.write(chr(Scribbler.GET_INFO) + (' ' * 8))
        self.ser.write(bytes(chr(Scribbler.GET_INFO) + (" " * 8), "ISO-8859-1"))
        retval = self.ser.readline()
        # print "Got", retval

        time.sleep(0.1)

        # self.ser.write(chr(Scribbler.GET_INFO) + (' ' * 8))
        self.ser.write(bytes(chr(Scribbler.GET_INFO) + (" " * 8), "ISO-8859-1"))

        retval = self.ser.readline().decode("ISO-8859-1")
        # print "Got", retval

        # remove echoes
        if retval is None or len(retval) == 0:
            return {}

        if retval[0] == "P" or retval[0] == "p":
            retval = retval[1:]

        if retval[0] == "P" or retval[0] == "p":
            retval = retval[1:]

        # self.ser.setTimeout(oldtimeout)
        self.ser.timeout = oldtimeout

        retDict = {}
        # for pair in retval.split(","):
        for pair in retval.split(","):
            if ":" in pair:
                it, value = pair.split(":")
                retDict[it.lower().strip()] = value.strip()
        if len(item) == 0:
            return retDict
        else:
            retval = []
            for it in item:
                retval.append(retDict[it.lower().strip()])
            if len(retval) == 1:
                return retval[0]
            else:
                return retval

    def getBattery(self):
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.GET_BATTERY))
            retval = read_2byte(self.ser) / 20.9813
        finally:
            self.lock.release()
        return retval

    def identifyRobot(self):
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.GET_ROBOT_ID))
            retval = self.ser.readline()
        finally:
            self.lock.release()
        return retval

    def getIRMessage(self):
        line = ""

        if self.dongle:
            version = list(map(int, self.dongle.split(".")))
        else:
            version = [1, 0, 0]

        if version < [2, 8, 1]:
            print("IR Messaging not support with your firmware")
            return None

        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.GET_IR_MESSAGE))
            size = read_2byte(self.ser)
            while len(line) < size:
                line += self.ser.read(size - len(line))
        finally:
            self.lock.release()
        return line

    def sendIRMessage(self, data):
        if self.dongle:
            version = list(map(int, self.dongle.split(".")))
        else:
            version = [1, 0, 0]

        if version < [2, 8, 1]:
            print("IR Messaging not support with your firmware")
            return None

        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SEND_IR_MESSAGE))
            self.ser.write(chr(len(data)))
            for i in data:
                self.ser.write(i)
        finally:
            self.lock.release()
        return

    def setCommunicateLeft(self, on=True):
        if on:
            self.emitters = self.emitters | 0x04
        else:
            self.emitters = self.emitters & ~0x04
        return self.setCommunicate()

    def setCommunicateCenter(self, on=True):
        if on:
            self.emitters = self.emitters | 0x02
        else:
            self.emitters = self.emitters & ~0x02
        return self.setCommunicate()

    def setCommunicateRight(self, on=True):
        if on:
            self.emitters = self.emitters | 0x01
        else:
            self.emitters = self.emitters & ~0x01
        return self.setCommunicate()

    def setCommunicateAll(self, on=True):
        if on:
            self.emitters = 0x01 | 0x02 | 0x04
        else:
            self.emitters = 0
        return self.setCommunicate()

    def setCommunicate(self):
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SET_IR_EMITTERS))
            self.ser.write(chr(self.emitters))
        finally:
            self.lock.release()
        return

    def setBrightPower(self, power):
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SET_DONGLE_IR))
            self.ser.write(chr(power))
        finally:
            self.lock.release()

    def setLEDFront(self, value):
        value = int(min(max(value, 0), 1))
        try:
            self.lock.acquire()
            if isTrue(value):
                self.ser.write(chr(Scribbler.SET_DONGLE_LED_ON))
            else:
                self.ser.write(chr(Scribbler.SET_DONGLE_LED_OFF))
        finally:
            self.lock.release()

    def setLEDBack(self, value):
        if value > 1:
            value = 1
        elif value <= 0:
            value = 0
        else:
            value = int(float(value) * (255 - 170) + 170)  # scale
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SET_DIMMER_LED))
            self.ser.write(chr(value))
        finally:
            self.lock.release()

    def getObstacle(self, value=None):
        if value is None:
            return self.get("obstacle")
        try:
            self.lock.acquire()
            if value in ["left", 0]:
                self.ser.write(chr(Scribbler.GET_DONGLE_L_IR))
            elif value in ["middle", "center", 1]:
                self.ser.write(chr(Scribbler.GET_DONGLE_C_IR))
            elif value in ["right", 2]:
                self.ser.write(chr(Scribbler.GET_DONGLE_R_IR))
            retval = read_2byte(self.ser)
        finally:
            self.lock.release()
        return retval

    def getDistance(self, value=None):
        if self._IsScribbler2():
            if value is None:
                return self.get("distance")
            try:
                self.lock.acquire()
                if value in ["left", 0]:
                    self._write([Scribbler.GET_DISTANCE, 0])
                elif value in ["right", 1]:
                    self._write([Scribbler.GET_DISTANCE, 1])
                self._read(Scribbler.PACKET_LENGTH)  # read echo
                retval = ord(self.ser.read(1))
            finally:
                self.lock.release()
            return retval

    def getBright(self, window=None):
        # left, middle, right

        # assumes this configuartion of the windows
        # conf_gray_window(self.ser, 0, 0, 0,    84, 191, 1, 1)
        # conf_gray_window(self.ser, 1, 84,  0, 170, 191, 1, 1)
        # conf_gray_window(self.ser, 2, 170, 0, 254, 191, 1, 1)

        if window is None or window == "all":
            return self.get("bright")
        if type(window) == str:
            if window in ["left"]:
                window = 0
            elif window in ["middle", "center"]:
                window = 1
            elif window in ["right"]:
                window = 2
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.GET_WINDOW_LIGHT))
            self.ser.write(chr(window))
            retval = read_3byte(self.ser)  # / (63.0 * 192.0 * 255.0)
        finally:
            self.lock.release()
        return retval

    def setForwardness(self, direction):
        if direction in ["fluke-forward", 1]:
            direction = 1
        elif direction in ["scribbler-forward", 0]:
            direction = 0
        else:
            raise AttributeError(
                "unknown direction: '%s': should be 'fluke-forward' or 'scribbler-forward'"
                % direction
            )
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SET_FORWARDNESS))
            self.ser.write(chr(direction))
        finally:
            self.lock.release()

    def setIRPower(self, power):
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SET_DONGLE_IR))
            self.ser.write(chr(power))
        finally:
            self.lock.release()

    def setWhiteBalance(self, value):
        try:
            self.lock.acquire()
            if isTrue(value):
                self.ser.write(chr(Scribbler.SET_WHITE_BALANCE))
            else:
                self.ser.write(chr(Scribbler.SET_NO_WHITE_BALANCE))
        finally:
            self.lock.release()

    def reboot(self):
        try:
            self.lock.acquire()
            self.ser.write(chr(Scribbler.SET_RESET_SCRIBBLER))
        finally:
            self.lock.release()

    def reset(self):
        for p in [127, 127, 127, 127, 0, 0, 0, 0]:
            self.setSingleData(p, 0)
        self.setName("Scribby")

    def setData(self, position, value):
        data = self._get(Scribbler.GET_DATA, 8)
        data[position] = value
        return self._set(*([Scribbler.SET_DATA] + data))

    def setSingleData(self, position, value):
        data = [position, value]
        return self._set(*([Scribbler.SET_SINGLE_DATA] + data))

    def setEchoMode(self, value):
        if isTrue(value):
            self._set(Scribbler.SET_ECHO_MODE, 1)
        else:
            self._set(Scribbler.SET_ECHO_MODE, 0)
        time.sleep(0.25)
        self.ser.flushInput()
        self.ser.flushOutput()
        return

    def set(self, item, position, value=None):
        item = item.lower()
        if item == "led":
            if type(position) in [int, float]:
                if position == 0:
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_LEFT_ON)
                    else:
                        return self._set(Scribbler.SET_LED_LEFT_OFF)
                elif position == 1:
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_CENTER_ON)
                    else:
                        return self._set(Scribbler.SET_LED_CENTER_OFF)
                elif position == 2:
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_RIGHT_ON)
                    else:
                        return self._set(Scribbler.SET_LED_RIGHT_OFF)
                else:
                    raise AttributeError("no such LED: '%s'" % position)
            else:
                position = position.lower()
                if position == "center":
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_CENTER_ON)
                    else:
                        return self._set(Scribbler.SET_LED_CENTER_OFF)
                elif position == "left":
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_LEFT_ON)
                    else:
                        return self._set(Scribbler.SET_LED_LEFT_OFF)
                elif position == "right":
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_RIGHT_ON)
                    else:
                        return self._set(Scribbler.SET_LED_RIGHT_OFF)
                elif position == "front":
                    return self.setLEDFront(value)
                elif position == "back":
                    return self.setLEDBack(value)
                elif position == "all":
                    if isTrue(value):
                        return self._set(Scribbler.SET_LED_ALL_ON)
                    else:
                        return self._set(Scribbler.SET_LED_ALL_OFF)
                else:
                    raise AttributeError("no such LED: '%s'" % position)
        elif item == "name":
            position = position + (" " * 16)
            name1 = position[:8].strip()
            name1_raw = [ord(x) for x in name1]
            name2 = position[8:16].strip()
            name2_raw = [ord(x) for x in name2]
            self._set(*([Scribbler.SET_NAME1] + name1_raw))
            self._set(*([Scribbler.SET_NAME2] + name2_raw))
        elif item == "password":
            position = position + (" " * 16)
            pass1 = position[:8].strip()
            pass1_raw = [ord(x) for x in pass1]
            pass2 = position[8:16].strip()
            pass2_raw = [ord(x) for x in pass2]
            self._set(*([Scribbler.SET_PASS1] + pass1_raw))
            self._set(*([Scribbler.SET_PASS2] + pass2_raw))
        elif item == "whitebalance":
            self.setWhiteBalance(position)
        elif item == "irpower":
            self.setIRPower(position)
        elif item == "volume":
            if isTrue(position):
                self._volume = 1
                return self._set(Scribbler.SET_LOUD)
            else:
                self._volume = 0
                return self._set(Scribbler.SET_QUIET)
        elif item == "startsong":
            self.startsong = position
        elif item == "echomode":
            return self.setEchoMode(position)
        elif item == "data":
            return self.setData(position, value)
        elif item == "password":
            return self.setPassword(position)
        elif item == "forwardness":
            return self.setForwardness(position)
        else:
            raise "invalid set item name: '%s'"

    # Sets the fudge values (in memory, and on the flash memory on the robot)
    def setFudge(self, f1, f2, f3, f4):

        self._fudge[0] = f1
        self._fudge[1] = f2
        self._fudge[2] = f3
        self._fudge[3] = f4

        # Save the fudge data (in integer 0..255 form) to the flash memory
        # f1-f4 are float values 0..2, convert to byte values
        # But to make things quick, only save the ones that have changed!
        # 0..255 and save.

        if self._oldFudge[0] != self._fudge[0]:
            if self.dongle is None:
                self.setSingleData(0, int(self._fudge[0] * 127.0))
            else:
                self.setSingleData(3, int(self._fudge[0] * 127.0))

            self._oldFudge[0] = self._fudge[0]

        if self._oldFudge[1] != self._fudge[1]:
            if self.dongle is None:
                self.setSingleData(1, int(self._fudge[1] * 127.0))
            else:
                self.setSingleData(2, int(self._fudge[1] * 127.0))
            self._oldFudge[1] = self._fudge[1]

        if self._oldFudge[2] != self._fudge[2]:
            if self.dongle is None:
                self.setSingleData(2, int(self._fudge[2] * 127.0))
            else:
                self.setSingleData(1, int(self._fudge[2] * 127.0))
            self._oldFudge[2] = self._fudge[2]

        if self._oldFudge[3] != self._fudge[3]:
            if self.dongle is None:
                self.setSingleData(3, int(self._fudge[3] * 127.0))
            else:
                self.setSingleData(0, int(self._fudge[3] * 127.0))
            self._oldFudge[3] = self._fudge[3]

    # Called when robot is initialized, after serial connection is established.
    # Checks to see if the robot has fudge factors saved in it's data area
    # 0,1,2,3, and uses them. If the robot has zeros, it replaces them with 127
    # which is the equivalent of no fudge. Each factor goes from 0..255, where
    # a 127 is straight ahead (no fudging)
    def loadFudge(self):

        for i in range(4):
            self._fudge[i] = self.get("data", i)
            if self._fudge[i] == 0:
                self._fudge[i] = 127
            self._fudge[i] = self._fudge[i] / 127.0  # convert back to floating point!

        if self.dongle is not None:
            self._fudge[0], self._fudge[1], self._fudge[2], self._fudge[3] = (
                self._fudge[3],
                self._fudge[2],
                self._fudge[1],
                self._fudge[0],
            )

    # Gets the fudge values (from memory, so we don't get penalized by a slow
    # serial link)
    def getFudge(self):
        return (self._fudge[0], self._fudge[1], self._fudge[2], self._fudge[3])

    def stop(self):
        self._lastTranslate = 0
        self._lastRotate = 0
        return self._set(Scribbler.SET_MOTORS_OFF)

    def hardStop(self):
        values = [Scribbler.SET_MOTORS_OFF]
        self._lastTranslate = 0
        self._lastRotate = 0
        self._write(values)
        self._read(Scribbler.PACKET_LENGTH)  # read echo
        self._lastSensors = self._read(11)  # single bit sensors

    def translate(self, amount):
        self._lastTranslate = amount
        self._adjustSpeed()

    def rotate(self, amount):
        self._lastRotate = amount
        self._adjustSpeed()

    def move(self, translate, rotate):
        self._lastTranslate = translate
        self._lastRotate = rotate
        self._adjustSpeed()

    def getPosition(self):
        """This returns the x and y coordinates of the scribbler 2"""
        if self._IsScribbler2():
            return self._get(Scribbler.GET_POSN, 8, "long")

    def setHereIs(self, x, y):
        if self._IsScribbler2():
            self._set(
                Scribbler.SET_POSN,
                (x >> 24) & 0xFF,
                (x >> 16) & 0xFF,
                (x >> 8) & 0xFF,
                x & 0xFF,
                (y >> 24) & 0xFF,
                (y >> 16) & 0xFF,
                (y >> 8) & 0xFF,
                y & 0xFF,
            )

    def getAngle(self):
        """This returns the current angle of the scribbler 2"""
        if self._IsScribbler2():
            return self._get(Scribbler.GET_ANGLE, 4, "long")[0]

    def setAngle(self, angle):
        if self._IsScribbler2():
            self._set(
                Scribbler.SET_ANGLE,
                (angle >> 24) & 0xFF,
                (angle >> 16) & 0xFF,
                (angle >> 8) & 0xFF,
                angle & 0xFF,
            )

    def setBeginPath(self, speed=7):
        """Speed can be a value from 1 to 15"""
        if self._IsScribbler2():
            self._set(Scribbler.SET_PATH, Scribbler.BEGIN_PATH, 0, speed)

    def setTurn(self, angle, turnType="to", radOrDeg="rad"):
        if self._IsScribbler2():
            # checkin for valid arguments
            if turnType.lower() != "to" and turnType.lower() != "by":
                print(
                    "Invalid turnType specified must be 'to' or 'by', value:", turnType
                )
                return
            if radOrDeg.lower() != "rad" and radOrDeg.lower() != "deg":
                print(
                    "Invalid radOrDeg specified must be 'rad' or 'deg', value:",
                    radOrDeg,
                )
                return

            if turnType.lower() == "to" and radOrDeg.lower() == "rad":
                self._set(
                    Scribbler.SET_TURN, Scribbler.TO, (angle >> 8) & 0xFF, angle & 0xFF
                )
            elif turnType.lower() == "by" and radOrDeg.lower() == "rad":
                self._set(
                    Scribbler.SET_TURN, Scribbler.BY, (angle >> 8) & 0xFF, angle & 0xFF
                )
            elif turnType.lower() == "to" and radOrDeg.lower() == "deg":
                self._set(
                    Scribbler.SET_TURN,
                    Scribbler.TO + Scribbler.DEG,
                    (angle >> 8) & 0xFF,
                    angle & 0xFF,
                )
            elif turnType.lower() == "by" and radOrDeg.lower() == "deg":
                self._set(
                    Scribbler.SET_TURN,
                    Scribbler.BY + Scribbler.DEG,
                    (angle >> 8) & 0xFF,
                    angle & 0xFF,
                )
            # loop until motor command finishes
            scribblerBusy = True
            while scribblerBusy:
                scribblerBusy = self._IsInTransit()
                if scribblerBusy:
                    time.sleep(1)

    def setMove(self, x, y, moveType="to"):
        if self._IsScribbler2():
            if moveType.lower() == "to":
                self._set(
                    Scribbler.SET_MOVE,
                    Scribbler.TO,
                    (x >> 8) & 0xFF,
                    x & 0xFF,
                    (y >> 8) & 0xFF,
                    y & 0xFF,
                )
            elif moveType.lower() == "by":
                self._set(
                    Scribbler.SET_MOVE,
                    Scribbler.BY,
                    (x >> 8) & 0xFF,
                    x & 0xFF,
                    (y >> 8) & 0xFF,
                    y & 0xFF,
                )
            else:
                print(
                    "Invalid moveType specified must be 'to' or 'by', value:", moveType
                )
                return
            scribblerBusy = True
            while scribblerBusy:
                scribblerBusy = self._IsInTransit()
                if scribblerBusy:
                    time.sleep(1)

    def setArc(self, x, y, radius, arcType="to"):
        if self._IsScribbler2():
            if arcType.lower() == "to":
                self._set(
                    Scribbler.SET_ARC,
                    Scribbler.TO,
                    (x >> 8) & 0xFF,
                    x & 0xFF,
                    (y >> 8) & 0xFF,
                    y & 0xFF,
                    (radius >> 8) & 0xFF,
                    radius & 0xFF,
                )
            elif arcType.lower() == "by":
                self._set(
                    Scribbler.SET_ARC,
                    Scribbler.BY,
                    (x >> 8) & 0xFF,
                    x & 0xFF,
                    (y >> 8) & 0xFF,
                    y & 0xFF,
                    (radius >> 8) & 0xFF,
                    radius & 0xFF,
                )
            else:
                print("Invalid arcType specified must be 'to' or 'by', value:", arcType)
                return
            scribblerBusy = True
            while scribblerBusy:
                scribblerBusy = self._IsInTransit()
                if scribblerBusy:
                    time.sleep(1)

    def setEndPath(self):
        if self._IsScribbler2():
            self._set(Scribbler.SET_PATH, Scribbler.END_PATH, 0, 7)

    def setS2Volume(self, level):
        """Level can be between 0-100 and represents the percent volume level of the speaker"""
        if self._IsScribbler2():
            self._set(Scribbler.SET_VOLUME, level)

    def getMicEnvelope(self):
        """Returns a number representing the microphone envelope noise"""
        if self._IsScribbler2():
            return self._get(Scribbler.GET_MIC_ENV, 4, "long")[0]

    def getMotorStats(self):
        """Return the current motion status as a packed long and single additional byte showing if motors are ready for commands (1=ready, 0=busy):
     Left wheel and right wheel are signed, twos complement eight bit velocity values,
     Idler timer is the time in 1/10 second since the last idler edge,
     Idler spd is an unsigned six-bit velocity value, and
     Mov is non-zero iff one or more motors are turning.
     Left and right wheel velocities are instanteous encoder counts over a 1/10-second interval.
     Idler wheel wheel velocity is updated every 1/10 second and represents the idler encoder count during the last 1.6 seconds."""

        if self._IsScribbler2():
            rawMotorStats = self._get(Scribbler.GET_MOTOR_STATS, 5, "byte")
            return {
                "wheel": [rawMotorStats[3], rawMotorStats[2]],
                "IdlerTimer": [rawMotorStats[1]],
                "IdlerSpeed": [rawMotorStats[0] >> 2],
                "Mov": [bool(rawMotorStats[0] & 0x03)],
                "Ready": [bool(rawMotorStats[4])],
            }

    def getEncoders(self, zeroEncoders=False):
        """Gets the values for the left and right encoder wheels.  Negative value means they have moved
        backwards from the robots perspective.  Each turn of the encoder wheel is counted as and increment or
        decrement of 2 depending on which direction the wheels moved.
        if zeroEncoders is set to True then the encoders will be set to zero after reading the values"""
        if self._IsScribbler2():
            if zeroEncoders:
                return self._getWithSetByte(Scribbler.GET_ENCODERS, 8, "long", 0x00)
            else:
                return self._getWithSetByte(Scribbler.GET_ENCODERS, 8, "long", 0x01)

    def getLastSensors(self):
        retval = self._lastSensors
        return {
            "light": [
                retval[2] << 8 | retval[3],
                retval[4] << 8 | retval[5],
                retval[6] << 8 | retval[7],
            ],
            "ir": [retval[0], retval[1]],
            "line": [retval[8], retval[9]],
            "stall": retval[10],
        }

    def update(self):
        pass

    # Private

    def _IsScribbler2(self):
        if self.robotinfo == "Scribbler2":
            return True
        else:
            print("Not a Scribbler 2 robot")
            return False

    def _IsInTransit(self):
        return not bool(self._get(Scribbler.GET_MOTOR_STATS, 5, "byte")[4])

    def _adjustSpeed(self):
        left = min(max(self._lastTranslate - self._lastRotate, -1), 1)
        right = min(max(self._lastTranslate + self._lastRotate, -1), 1)

        # JWS additions for "calibration" of motors.
        # Use fudge values 1-4 to change the actual power given to each
        # motor based upon the forward speed.
        #
        # This code is here for documentation purposes only.
        #
        # The algorithm shown here is now implemented on the basic stamp
        # on the scribbler directly.

        # fudge the left motor when going forward!
        # if (self._fudge[0] > 1.0 and left > 0.5 ):
        # left = left - (self._fudge[0] - 1.0)
        # if (self._fudge[1] > 1.0 and 0.5 >= left > 0.0):
        # left = left - (self._fudge[1] - 1.0)
        # fudge the right motor when going forward!
        # if (self._fudge[0] < 1.0 and right > 0.5):
        # right = right - (1.0 - self._fudge[0])
        # if (self._fudge[1] < 1.0 and 0.5 >= right > 0.0):
        # right = right - (1.0 - self._fudge[1])

        # Backwards travel is just like forwards travel, but reversed!
        # fudge the right motor when going backwards.
        # if (self._fudge[2] > 1.0 and 0.0 > right >= -0.5):
        #        right = right + (self._fudge[2] - 1.0)
        # if (self._fudge[3] > 1.0 and -0.5 > right ):
        #        right = right + (self._fudge[3] - 1.0)

        # fudge the left motor when going backwards.
        # if (self._fudge[2] < 1.0 and 0.0 > left >= -0.5):
        #        left = left + (1.0 - self._fudge[2])
        # if (self._fudge[3] < 1.0 and -0.5 > left):
        #        left = left + (1.0 - self._fudge[3])

        # print "actual power: (",left,",",right,")"

        # end JWS additions for "calibration of motors.
        leftPower = (left + 1.0) * 100.0
        rightPower = (right + 1.0) * 100.0

        self._set(Scribbler.SET_MOTORS, rightPower, leftPower)

    def _read(self, bytes_=1):

        if self.debug:
            print("Trying to read", bytes_, "bytes_", "timeout =", self.ser.timeout)

        c = self.ser.read(bytes_)
        c = c.decode("ISO-8859-1")

        if self.debug:
            print("Initially read", len(c), "bytes_:", end=" ")
            print(["0x%x" % ord(x) for x in c])

        # .nah. bug fix
        while bytes_ > 1 and len(c) < bytes_:
            c = c + self.ser.read(bytes_ - len(c))
            if self.debug:
                print(["0x%x" % ord(x) for x in c])

        # .nah. end bug fix
        if self.debug:
            print("_read (%d)" % len(c))
            print(["0x%x" % ord(x) for x in c])

        if self.dongle is None:
            time.sleep(0.01)  # HACK! THIS SEEMS TO NEED TO BE HERE!
        if bytes_ == 1:
            x = -1
            if c != "":
                x = ord(c)
            elif self.debug:
                print("timeout!")
                return x
        else:
            return list(map(ord, c))

    def _write(self, rawdata):
        t = [chr(int(x)) for x in rawdata]
        data = bytes(
            "".join(t) + (chr(0) * (Scribbler.PACKET_LENGTH - len(t)))[:9], "UTF-8"
        )
        # if self.debug:
        #     print("_write:", data, len(data), end=' ')
        #     print("data:", end=' ')
        #     print(["0x%x" % ord(x) for x in data])

        if self.dongle is None:
            time.sleep(0.01)  # HACK! THIS SEEMS TO NEED TO BE HERE!
        self.ser.write(data)  # write packets

    def _set(self, *values):
        try:
            self.lock.acquire()  # print "locked acquired"
            self._write(values)
            test = self._read(Scribbler.PACKET_LENGTH)  # read echo
            self._lastSensors = self._read(11)  # single bit sensors
            # self.ser.flushInput()
            if self.requestStop:
                self.requestStop = 0
                self.stop()
                self.lock.release()
                raise KeyboardInterrupt
        finally:
            self.lock.release()

    def _setWithTime(self, waitTime, *values):
        try:
            self.lock.acquire()  # print "locked acquired"
            self._write(values)
            time.sleep(waitTime)
            # test = self._read(Scribbler.PACKET_LENGTH)  # read echo
            self._read(Scribbler.PACKET_LENGTH)  # read echo
            self._lastSensors = self._read(11)  # single bit sensors
            # self.ser.flushInput()
            if self.requestStop:
                self.requestStop = 0
                self.stop()
                self.lock.release()
                raise KeyboardInterrupt
        finally:
            self.lock.release()

    def _getWithSetByte(self, packetValue, bytes=1, mode="byte", setByte=0xFF):
        """Allows user to pass in a byte when calling a method that get data.   Can be used to zero out values like encoders"""
        return self._get(packetValue, bytes, mode, setByte)

    def _get(self, value, bytes=1, mode="byte", setByte=0xFF):
        try:
            self.lock.acquire()
            if setByte != 0xFF:
                self._write([value, setByte])
            else:
                self._write([value])
            self._read(Scribbler.PACKET_LENGTH)  # read the echo
            if mode == "byte":
                retval = self._read(bytes)
            elif mode == "word":
                retvalBytes = self._read(bytes)
                retval = []
                for p in range(0, len(retvalBytes), 2):
                    retval.append(retvalBytes[p] << 8 | retvalBytes[p + 1])
            elif mode == "long":
                retvalBytes = self.ser.read(bytes)
                retval = list(unpack(">" + "i" * (bytes / 4), retvalBytes))
            elif mode == "line":  # until hit \n newline
                retval = self.ser.readline()
                if self.debug:
                    print("_get(line)", retval)
            # self.ser.flushInput()
        finally:
            self.lock.release()

        return retval

    def _set_speaker(self, frequency, duration):
        self._write(
            [
                Scribbler.SET_SPEAKER,
                duration >> 8,
                duration % 256,
                frequency >> 8,
                frequency % 256,
            ]
        )

    def _set_speaker_2(self, freq1, freq2, duration):
        self._write(
            [
                Scribbler.SET_SPEAKER_2,
                duration >> 8,
                duration % 256,
                freq1 >> 8,
                freq1 % 256,
                freq2 >> 8,
                freq2 % 256,
            ]
        )


def cap(c):
    if c > 255:
        return 255
    if c < 0:
        return 0

    return c


def read_2byte(ser):
    hbyte = ord(ser.read(1))
    lbyte = ord(ser.read(1))
    lbyte = (hbyte << 8) | lbyte
    return lbyte


def read_3byte(ser):
    hbyte = ord(ser.read(1))
    mbyte = ord(ser.read(1))
    lbyte = ord(ser.read(1))
    lbyte = (hbyte << 16) | (mbyte << 8) | lbyte
    return lbyte


def write_2byte(ser, value):
    ser.write(chr((value >> 8) & 0xFF))
    ser.write(chr(value & 0xFF))


def read_mem(ser, page, offset):
    ser.write(chr(Scribbler.GET_SERIAL_MEM))
    write_2byte(ser, page)
    write_2byte(ser, offset)
    return ord(ser.read(1))


def write_mem(ser, page, offset, byte):
    ser.write(chr(Scribbler.SET_SERIAL_MEM))
    write_2byte(ser, page)
    write_2byte(ser, offset)
    ser.write(chr(byte))


def erase_mem(ser, page):
    ser.write(chr(Scribbler.SET_SERIAL_ERASE))
    write_2byte(ser, page)


# Also copied into system.py:


def set_scribbler_memory(ser, offset, byte):
    ser.write(chr(Scribbler.SET_SCRIB_PROGRAM))
    write_2byte(ser, offset)
    ser.write(chr(byte))


def get_scribbler_memory(ser, offset):
    ser.write(chr(Scribbler.GET_SCRIB_PROGRAM))
    write_2byte(ser, offset)
    v = ord(ser.read(1))
    return v


def set_scribbler_start_program(ser, size):
    ser.write(chr(Scribbler.SET_START_PROGRAM))
    write_2byte(ser, size)


def set_scribbler2_start_program(ser, size):
    ser.write(chr(Scribbler.SET_START_PROGRAM2))
    write_2byte(ser, size)


def get_window_avg(ser, window):
    ser.write(chr(Scribbler.GET_WINDOW_LIGHT))
    ser.write(chr(window))
    return read_2byte(ser)


def quadrupleSize(line, width):
    retval = [" "] * len(line) * 4
    col = 0
    row = 0
    for c in line:
        retval[row * 2 * width + col] = c
        retval[row * 2 * width + col + 1] = c
        retval[(row + 1) * 2 * width + col] = c
        retval[(row + 1) * 2 * width + col + 1] = c
        col += 2
        if col == width * 2:
            col = 0
            row += 2
    return "".join(retval)


def set_ir_power(ser, power):
    ser.write(chr(Scribbler.SET_DONGLE_IR))
    ser.write(chr(power))

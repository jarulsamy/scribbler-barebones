# -*- coding: utf-8 -*-
import atexit
import random
import signal
import sys
import threading
import time
import traceback

from .globalvars import makeEnvironment
from .globalvars import robot
from .globalvars import setup
from .robots.scribbler import Scribbler

__AUTHOR__ = "Joshua Arulsamy"
__VERSION__ = "0.0.1"


def wait(seconds):
    """
    Wrapper for time.sleep() so that we may later overload.
    """
    return time.sleep(seconds)


def currentTime():
    """
    Returns current time in seconds since
    """
    return time.time()


def pickOne(*args):
    """
    Randomly pick one of a list, or one between [0, arg).
    """
    if len(args) == 1:
        return random.randrange(args[0])
    else:
        return args[random.randrange(len(args))]


def pickOneInRange(start, stop):
    """
    Randomly pick one of a list, or one between [0, arg).
    """
    return random.randrange(start, stop)


def heads():
    return flipCoin() == "heads"


def tails():
    return flipCoin() == "tails"


def flipCoin():
    """
    Randomly returns "heads" or "tails".
    """
    return ("heads", "tails")[random.randrange(2)]


def randomNumber():
    """
    Returns a number between 0 (inclusive) and 1 (exclusive).
    """
    return random.random()


class BackgroundThread(threading.Thread):
    """
    A thread class for running things in the background.
    """

    def __init__(self, function, pause=0.01):
        """
        Constructor, setting initial variables
        """
        self.function = function
        self._stopevent = threading.Event()
        self._sleepperiod = pause
        threading.Thread.__init__(self, name="MyroThread")

    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            self.function()
            # self._stopevent.wait(self._sleepperiod)

    def join(self, timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)


def _cleanup():
    if robot:
        if "robot" in robot.robotinfo:
            try:
                robot.stop()  # hangs?
                time.sleep(0.5)
            except Exception:  # catch serial.SerialException
                # port already closed
                pass
        try:
            robot.close()
        except Exception:
            pass


def ctrlc_handler(signum, frame):
    if robot:
        # robot.open()
        # print "done opening"
        robot.manual_flush()
        if "robot" in robot.robotinfo:
            robot.hardStop()
    # raise KeyboardInterrupt
    orig_ctrl_handler()


orig_ctrl_handler = signal.getsignal(signal.SIGINT)
# Set the signal handler and a 5-second alarm
signal.signal(signal.SIGINT, ctrlc_handler)

# Get ready for user prompt; set up environment:
if not setup:
    setup = 1
    atexit.register(_cleanup)
    # Ok, now we're ready!
    print("(c) 2006-2007 Institute for Personal Robots in Education", file=sys.stderr)
    print("[See http://www.roboteducation.org/ for more information]", file=sys.stderr)
    print("Myro version %s is ready!" % (__VERSION__,), file=sys.stderr)

# Functional interface:


def requestStop():
    if robot:
        robot.requestStop = 1


def initialize(port):
    global robot
    robot = Scribbler(port)
    __builtins__["robot"] = robot


init = initialize


# def simulator(id=None):
#     _startSimulator()
#     time.sleep(2)
#     robot = SimScribbler(id)
#     __builtins__["robot"] = robot


def translate(amount):
    if robot:
        return robot.translate(amount)
    else:
        raise AttributeError("need to initialize robot")


def rotate(amount):
    if robot:
        return robot.rotate(amount)
    else:
        raise AttributeError("need to initialize robot")


def move(translate, rotate):
    if robot:
        return robot.move(translate, rotate)
    else:
        raise AttributeError("need to initialize robot")


def forward(speed=1, seconds=None):
    if robot:
        return robot.forward(speed, seconds)
    else:
        raise AttributeError("need to initialize robot")


def backward(speed=1, seconds=None):
    if robot:
        return robot.backward(speed, seconds)
    else:
        raise AttributeError("need to initialize robot")


def turn(direction, amount=0.8, seconds=None):
    if robot:
        return robot.turn(direction, amount, seconds)
    else:
        raise AttributeError("need to initialize robot")


def turnLeft(speed=1, seconds=None):
    if robot:
        return robot.turnLeft(speed, seconds)
    else:
        raise AttributeError("need to initialize robot")


def turnRight(speed=1, seconds=None):
    if robot:
        return robot.turnRight(speed, seconds)
    else:
        raise AttributeError("need to initialize robot")


def stop():
    if robot:
        return robot.stop()


def getPosition():
    """This returns the x and y coordinates of the scribbler 2"""
    if robot:
        return robot.getPosition()
    else:
        raise AttributeError("need to initialize robot")


def hereIs(x=0, y=0):
    if robot:
        return robot.setHereIs(x, y)
    else:
        raise AttributeError("need to initialize robot")


def getAngle():
    """This returns the current angle of the scribbler 2"""
    if robot:
        return robot.getAngle()
    else:
        raise AttributeError("need to initialize robot")


def setAngle(angle):
    if robot:
        return robot.setAngle(angle)
    else:
        raise AttributeError("need to initialize robot")


def beginPath():
    """Speed can be a value from 1 to 15"""
    if robot:
        return robot.setBeginPath()
    else:
        raise AttributeError("need to initialize robot")


def moveTo(x, y):
    if robot:
        return robot.setMove(x, y, "to")
    else:
        raise AttributeError("need to initialize robot")


def moveBy(x, y):
    if robot:
        return robot.setMove(x, y, "by")
    else:
        raise AttributeError("need to initialize robot")


def turnTo(angle, radsOrDegrees):
    if robot:
        return robot.setTurn(angle, "to", radsOrDegrees)
    else:
        raise AttributeError("need to initialize robot")


def turnBy(angle, radsOrDegrees):
    if robot:
        return robot.setTurn(angle, "by", radsOrDegrees)
    else:
        raise AttributeError("need to initialize robot")


def arcTo(x, y, radius):
    if robot:
        return robot.setArc(x, y, radius, "to")
    else:
        raise AttributeError("need to initialize robot")


def arcBy(x, y, radius):
    if robot:
        return robot.setArc(x, y, radius, "by")
    else:
        raise AttributeError("need to initialize robot")


def endPath():
    if robot:
        return robot.setEndPath()
    else:
        raise AttributeError("need to initialize robot")


# def getMicEnvelope():
#     """Returns a number representing the microphone envelope noise"""
#     if robot:
#         return robot.getMicEnvelope()
#     else:
#         raise AttributeError("need to initialize robot")


def getMotorStats():
    """Return the current motion status as a packed long and single additional byte showing if motors are ready for commands (1=ready, 0=busy):
 Left wheel and right wheel are signed, twos complement eight bit velocity values,
 Idler timer is the time in 1/10 second since the last idler edge,
 Idler spd is an unsigned six-bit velocity value, and
 Mov is non-zero iff one or more motors are turning.
 Left and right wheel velocities are instanteous encoder counts over a 1/10-second interval.
 Idler wheel wheel velocity is updated every 1/10 second and represents the idler encoder count during the last 1.6 seconds."""
    if robot:
        return robot.getMotorStats()
    else:
        raise AttributeError("need to initialize robot")


def getEncoders(zeroEncoders=False):
    """Gets the values for the left and right encoder wheels.  Negative value means they have moved
    backwards from the robots perspective.  Each turn of the encoder wheel is counted as and increment or
    decrement of 2 depending on which direction the wheels moved.
    if zeroEncoders is set to True then the encoders will be set to zero after reading the values"""
    if robot:
        return robot.getEncoders(zeroEncoders)
    else:
        raise AttributeError("need to initialize robot")


def openConnection():
    if robot:
        return robot.open()
    else:
        raise AttributeError("need to initialize robot")


def closeConnection():
    if robot:
        return robot.close()
    else:
        raise AttributeError("need to initialize robot")


def get(sensor="all", *pos):
    if robot:
        return robot.get(sensor, *pos)
    else:
        raise AttributeError("need to initialize robot")


def getVersion():
    if robot:
        return robot.get("version")
    else:
        raise AttributeError("need to initialize robot")


def getLight(*pos):
    if robot:
        return robot.get("light", *pos)
    else:
        raise AttributeError("need to initialize robot")


def getIR(*pos):
    if robot:
        return robot.get("ir", *pos)
    else:
        raise AttributeError("need to initialize robot")


def getDistance(*pos):
    if robot:
        return robot.getDistance(*pos)
    else:
        raise AttributeError("need to initialize robot")


def getLine(*pos):
    if robot:
        return robot.get("line", *pos)
    else:
        raise AttributeError("need to initialize robot")


def getStall():
    if robot:
        return robot.get("stall")
    else:
        raise AttributeError("need to initialize robot")


def getInfo(*item):
    if robot:
        retval = robot.getInfo(*item)
        retval["myro"] = __VERSION__
        return retval
    else:
        return {"myro": __VERSION__}


def getAll():
    if robot:
        return robot.get("all")
    else:
        raise AttributeError("need to initialize robot")


def getName():
    if robot:
        return robot.get("name")
    else:
        raise AttributeError("need to initialize robot")


def getPassword():
    if robot:
        return robot.get("password")
    else:
        raise AttributeError("need to initialize robot")


def getForwardness():
    if robot:
        return robot.get("forwardness")
    else:
        raise AttributeError("need to initialize robot")


def getStartSong():
    if robot:
        return robot.get("startsong")
    else:
        raise AttributeError("need to initialize robot")


def getVolume():
    if robot:
        return robot.get("volume")
    else:
        raise AttributeError("need to initialize robot")


def update():
    if robot:
        return robot.update()
    else:
        raise AttributeError("need to initialize robot")


def beep(duration=0.5, frequency1=None, frequency2=None):
    if type(duration) in [tuple, list]:
        frequency2 = frequency1
        frequency1 = duration
        duration = 0.5
    if frequency1 is None:
        frequency1 = random.randrange(200, 10000)
    if type(frequency1) in [tuple, list]:
        if frequency2 is None:
            frequency2 = [None for i in range(len(frequency1))]
        for (f1, f2) in zip(frequency1, frequency2):
            if robot:
                robot.beep(duration, f1, f2)
    else:
        if robot:
            robot.beep(duration, frequency1, frequency2)


def scaleDown(loopCount):
    beep(0.5, 9000 - 200 * loopCount)


def scaleUp(loopCount):
    beep(0.5, 200 + 200 * loopCount)


def set(item, position, value=None):
    if robot:
        return robot.set(item, position, value)
    else:
        raise AttributeError("need to initialize robot")


def setLED(position, value):
    if robot:
        return robot.set("led", position, value)
    else:
        raise AttributeError("need to initialize robot")


def setName(name):
    if robot:
        return robot.set("name", name)
    else:
        raise AttributeError("need to initialize robot")


def setPassword(password):
    if robot:
        return robot.set("password", password)
    else:
        raise AttributeError("need to initialize robot")


def setForwardness(value):
    if robot:
        return robot.set("forwardness", value)
    else:
        raise AttributeError("need to initialize robot")


def setVolume(value):
    if robot:
        return robot.set("volume", value)
    else:
        raise AttributeError("need to initialize robot")


def setS2Volume(value):
    """Level can be between 0-100 and represents the percent volume level of the speaker"""
    if robot:
        return robot.setS2Volume(value)
    else:
        raise AttributeError("need to initialize robot")


def setStartSong(songName):
    if robot:
        return robot.set("startsong", songName)
    else:
        raise AttributeError("need to initialize robot")


def motors(left, right):
    if robot:
        return robot.motors(left, right)
    else:
        raise AttributeError("need to initialize robot")


def restart():
    if robot:
        return robot.restart()
    else:
        raise AttributeError("need to initialize robot")


def playSong(song, wholeNoteDuration=0.545):
    if robot:
        return robot.playSong(song, wholeNoteDuration)
    else:
        raise AttributeError("need to initialize robot")


def playNote(tup, wholeNoteDuration=0.545):
    if robot:
        return robot.playNote(tup, wholeNoteDuration)
    else:
        raise AttributeError("need to initialize robot")


# New dongle commands


def getBright(position=None):
    if robot:
        return robot.getBright(position)
    else:
        raise AttributeError("need to initialize robot")


def getBlob():
    if robot:
        return robot.getBlob()
    else:
        raise AttributeError("need to initialize robot")


def getObstacle(position=None):
    if robot:
        return robot.getObstacle(position)
    else:
        raise AttributeError("need to initialize robot")


def setIRPower(value):
    if robot:
        return robot.setIRPower(value)
    else:
        raise AttributeError("need to initialize robot")


def getBattery():
    if robot:
        return robot.getBattery()
    else:
        raise AttributeError("need to initialize robot")


def identifyRobot():
    if robot:
        return robot.identifyRobot()
    else:
        raise AttributeError("need to initialize robot")


def getIRMessage():
    if robot:
        return robot.getIRMessage()
    else:
        raise AttributeError("need to initialize robot")


def sendIRMessage(msg):
    if robot:
        return robot.sendIRMessage(msg)
    else:
        raise AttributeError("need to initialize robot")


def setCommunicateLeft(on=True):
    if robot:
        return robot.setCommunicateLeft(on)
    else:
        raise AttributeError("need to initialize robot")


def setCommunicateRight(on=True):
    if robot:
        return robot.setCommunicateLeft(on)
    else:
        raise AttributeError("need to initialize robot")


def setCommunicateCenter(on=True):
    if robot:
        return robot.setCommunicateCenter(on)
    else:
        raise AttributeError("need to initialize robot")


def setCommunicateAll(on=True):
    if robot:
        return robot.setCommunicateAll(on)
    else:
        raise AttributeError("need to initialize robot")


def configureBlob(
    y_low=0, y_high=255, u_low=0, u_high=255, v_low=0, v_high=255, smooth_thresh=4
):
    if robot:
        return robot.configureBlob(
            y_low, y_high, u_low, u_high, v_low, v_high, smooth_thresh
        )
    else:
        raise AttributeError("need to initialize robot")


def setWhiteBalance(value):
    if robot:
        return robot.setWhiteBalance(value)
    else:
        raise AttributeError("need to initialize robot")


def darkenCamera(value=0):
    if robot:
        return robot.darkenCamera(value)
    else:
        raise AttributeError("need to initialize robot")


def manualCamera(gain=0x00, brightness=0x80, exposure=0x41):
    if robot:
        return robot.manualCamera(gain, brightness, exposure)
    else:
        raise AttributeError("need to initialize robot")


def autoCamera(value=0):
    if robot:
        return robot.autoCamera()
    else:
        raise AttributeError("need to initialize robot")


def setLEDFront(value):
    """ Set the Light Emitting Diode on the robot's front. """
    if robot:
        return robot.setLEDFront(value)
    else:
        raise AttributeError("need to initialize robot")


def setLEDBack(value):
    """ Set the Light Emitting Diode on the robot's back. """
    if robot:
        return robot.setLEDBack(value)
    else:
        raise AttributeError("need to initialize robot")


def _ndim(n, *args, **kwargs):
    if not args:
        return [kwargs.get("value", 0)] * n
    A = []
    for i in range(n):
        A.append(_ndim(*args, **kwargs))
    return A


class Column(object):
    def __init__(self, picture, column):
        self.picture = picture
        self.column = column

    def __getitem__(self, row):
        return self.picture.getPixel(self.column, row)


# --------------------------------------------------------
# Error handler:
# --------------------------------------------------------


def _myroExceptionHandler(etype, value, tb):
    # make a window
    # win = HelpWindow()
    lines = traceback.format_exception(etype, value, tb)
    print(
        "Myro is stopping: -------------------------------------------", file=sys.stderr
    )
    for line in lines:
        print(line.rstrip(), file=sys.stderr)


sys.excepthook = _myroExceptionHandler


_functions = (
    "set Forwardness",
    "wait",
    "current Time",
    "pick One",
    "flip Coin",
    "random Number",
    "request Stop",
    "initialize",
    "translate",
    "rotate",
    "move",
    "forward",
    "backward",
    "turn",
    "turn Left",
    "turn Right",
    "stop",
    "open Connection",
    "close Connection",
    "get",
    "get Version",
    "get Light",
    "get I R",
    "get Line",
    "get Stall",
    "get Info",
    "get All",
    "get Name",
    "get Volume",
    "update",
    "beep",
    "set",
    "set L E D",
    "set Name",
    "set Volume",
    "set Start Song",
    "motors",
    "restart",
    "play Song",
    "play Note",
    "get Bright",
    "get Obstacle",
    "set I R Power",
    "get Battery",
    "set L E D Front",
    "set L E D Back",
)

makeEnvironment(locals(), _functions)

from random import random
import json

class InputOutputError(Exception):
    pass

conf={}
TEST='test'
conf[TEST]=False
IN=1
OUT=0
HIGH=1
LOW=0
BCM=0
BOARD=1
pins={}
out={}
values={}

def config(path):
    global conf
    with open(path) as c:
        conf = json.load(c)
    if not conf[TEST]:
        global RPi
        global GPIO
        import RPi.GPIO as GPIO

#TODO check if initial is discarded for input or error is raised
def setup(channel,in_out,initial=HIGH):
    global conf
    if type(channel) is list:
        for el in channel:
            _setup_one(el,in_out,initial)
    else:
        _setup_one(channel,in_out,initial)

def _setup_one(channel,in_out,initial):
    if conf[TEST]:
        pins[channel]=in_out
    else:
        if initial == HIGH:
            initial = GPIO.HIGH
        else:
            initial = GPIO.LOW
        if in_out == IN:
            GPIO.setup(channel,GPIO.IN) # initial not a valid parameter for input, GPIO error
        else:
            GPIO.setup(channel,GPIO.OUT,initial=initial)

def check_in_out(channel,in_out):
    try:
        if pins[channel]==IN and in_out==OUT:
            pass
        elif not pins[channel]==in_out:
            raise InputOutputError("Wrong configuration for channel {}! You're treating an input channel as output or vice versa.")
    except KeyError:
        raise InputOutputError("Wrong configuration for channel {}! setup() not called for this channel before calling input() or output().")

def setmode(mode):
    if conf[TEST]:
        pass
    else:
        if mode == BCM:
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)
        
def input(channel):
    if conf[TEST]:
        check_in_out(channel,IN)
        try:
            values[channel]
        except KeyError:
            return random()
        return values[channel]
    else:
        return GPIO.input(channel)

def output(channel,value):
    if type(channel) is list:
        for el in channel:
            _output_one(el,value)
    else:
        _output_one(channel,value)

def _output_one(channel,value):
    if conf[TEST]:
        check_in_out(channel,OUT)
        out[channel]=value
    else:
        GPIO.output(channel,value)

def set_value(channel,value):
    values[channel]=value

def get_output(channel):
    return out[channel]
    
def cleanup(channel=None):
    global pins,out,values
    if channel==None:
        if conf[TEST]: 
            pins,out,values={},{},{}
        else:
            GPIO.cleanup()
    else:
        if type(channel) is list or type(channel) is tuple:
            for el in channel:
                _cleanup_one(el)
        else:
            _cleanup_one(channel)

def _cleanup_one(channel):
    global pins,out,values
    if conf[TEST]:
        if channel in values.keys() and pins[channel]==IN:
            del values[channel]
        elif channel in out.keys():
            del out[channel]
        if channel in pins.keys():
            del pins[channel]
    else:
        GPIO.cleanup(channel)

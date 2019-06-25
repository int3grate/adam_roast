import time
import spidev
import RPi.GPIO as GPIO          

from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

from multiprocessing import Queue, Process

import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
spi = spidev.SpiDev()

heater_pin = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(heater_pin, GPIO.OUT)
GPIO.output(heater_pin, GPIO.LOW)

heater=GPIO.PWM(heater_pin,1)
heater.start(0)

in1 = 24
in2 = 23
en = 25
temp1=1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)

GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)

fan=GPIO.PWM(en,1000)
fan.start(0)

fan_dc = 0
heater_dc = 0

class CallbackDataBlock(ModbusSparseDataBlock):
    def __init__(self, devices, queue):
        self.devices = devices
        self.queue = queue

        values = {k: 0 for k in devices.keys()}
        values[0xbeef] = len(values)  # the number of devices
        super(CallbackDataBlock, self).__init__(values)

    def getValues(self, address, count=1):
        global heater_dc, fan_dc
        if(address == 1): # thermostat
            return [get_temp_c()]
        elif(address == 2): # heater
            print("Heater Query")
            return [heater_dc]
        elif(address == 3): # fan
            print("Fan Query")
            return [fan_dc]

    def setValues(self, address, value):
        if(address == 2): # heater
            set_heat(value[0])
            print ("Heater Control, value=" + str(value))
        if(address == 3): # fan control
            set_fan(value[0])
            print ("Fan Control, value=" + str(value))

def device_handler(queue):
    while True:
        device, value = queue.get()
        scaled = rescale_value(value[0])
        log.debug("Write(%s) = %s" % (device, value))
        if not device: continue
        # do any logic here to update your devices

def run_callback_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    queue = Queue()
    devices = {}
    temp = get_temp_c()

    devices[1] = temp # thermostat BT
    devices[2] = 0 # heater
    devices[3] = 0 # fan

    block = CallbackDataBlock(devices, queue)
    store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'nick_labs'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'poppycock Server'
    identity.ModelName = 'poppycock Server'
    identity.MajorMinorRevision = '1.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    p = Process(target=device_handler, args=(queue,))
    p.start()
    StartTcpServer(context, identity=identity, address=("0.0.0.0", 5020))

# returns temp in C times 100
def get_temp_c():
    vals = spi.readbytes(2)
    temp_c = ((vals[0] << 8 | vals[1]) >> 3) * 0.25
    return int(temp_c * 100)

def set_heat(dc):
    global heater_dc
    heater_dc = dc
    heater.ChangeDutyCycle(dc)

def set_fan(dc):
    global in1, in2, fan_dc
    fan_dc = dc
    fan.ChangeDutyCycle(dc)
    if(dc > 0):
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
    elif(dc == 0):
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)

if __name__ == "__main__":
    spi.open(0,0)
    spi.max_speed_hz = 976000 
    spi.mode = 1 
    run_callback_server()


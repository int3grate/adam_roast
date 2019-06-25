import RPi.GPIO as GPIO          
from time import sleep
from multiprocessing import Process, Value

heater_pin = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(heater_pin, GPIO.OUT)
GPIO.output(heater_pin, GPIO.LOW)

p=GPIO.PWM(heater_pin,1)
p.start(0)

#def handle_heater(dc):
#    while(True):
#        for i in range(0,100):
#            if(i<dc.value):
#                GPIO.output(heater_pin, GPIO.HIGH)
#            else:
#                GPIO.output(heater_pin, GPIO.LOW)
#            sleep(.005)

print("Run heater (l=low, m=medium, h=high, s=stop/off, e=exit)")

#duty_cycle = Value('i',0)
#p = Process(target=handle_heater, args=(duty_cycle,))
#p.start()

while(1):
    x = raw_input()

    if x == 'l':
        print("heat set to low")
        p.ChangeDutyCycle(25) 
 #       duty_cycle.value = 10
    elif x == 'm':
        print("heat set to medium")
        p.ChangeDutyCycle(50) 
 #       duty_cycle.value = 50
    elif x == 'h':
        print("heat set to high")
        p.ChangeDutyCycle(100) 
 #       duty_cycle.value = 100
    elif x == 's':
        p.ChangeDutyCycle(0) 
        print("heat stopped")
 #       duty_cycle.value = 0
    elif x == 'e':
        exit()

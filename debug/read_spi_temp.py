import time
import spidev

spi = spidev.SpiDev()
spi.open(0,0)

spi.max_speed_hz = 976000 
spi.mode = 1 

while(True):
  time.sleep(.5)
  vals = spi.readbytes(2)
  temp_c = ((vals[0] << 8 | vals[1]) >> 3) * 0.25
  temp_f = (temp_c * 1.8) + 32
  print("temp (C): " + str(temp_c))
  print("temp (F): " + str(temp_f))
  print ("")

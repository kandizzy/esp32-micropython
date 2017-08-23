# This file is executed on every boot (including wake-boot from deepsleep)
import machine, network, utime, neopixel, time
import ubinascii
from pye import pye

from ppg.MAX30105 import ParticleSensor
from ppg.heartbeat import HeartBeat

# gpio==
from machine import Pin, ADC #ws2812, piezo
np = neopixel.NeoPixel(Pin(16), 4, timing=1)
adc = ADC(Pin(34))



print("")
print("Starting WiFi ...")
sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.connect("workshops", "floating")
while not sta_if.isconnected():
    utime.sleep_ms(100)

print("WiFi started")
utime.sleep_ms(500)
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

rtc = machine.RTC()
print("Synchronize time from NTP server ...")
rtc.ntp_sync(server="hr.pool.ntp.org")
while not rtc.synced():
    utime.sleep_ms(100)

print("Time set")
utime.sleep_ms(500)
t = rtc.now()
print(str(t[3])+':'+str(t[4])+':'+str(t[5])+' '+str(t[2])+'/'+str(t[1])+'/'+str(t[0]))
print("")

def red():
  print("red")
  n = np.n
  for i in range(n):
    np[i] = (255, 0, 0)
  np.write()

def green():
  print("green")
  n = np.n
  for i in range(n):
    np[i] = (0, 255, 0)
  np.write()

def blue():
  print("blue")
  n = np.n
  for i in range(n):
    np[i] = (0, 0, 255)
  np.write()

def off():
  n = np.n
  for i in range(n):
    np[i] = (0, 0, 0)
  np.write()

threshold = 100
color = (255,0,0)

def blink(color):
    for i in range(np.n):
        np[i] = color
    np.write()
    time.sleep(.01)
    for i in range(np.n):
        np[i] = (0, 0, 0)
    np.write()

def listen():
    #print(adc.read())
    if adc.read() < threshold:
      blink(color)

def main():
  print("mac address", mac)
  off()

  # this should only be enabled on the red light mode
  MAX30105 = ParticleSensor(HEX_ADDRESS=0x57)
  part_id = MAX30105.i2c_read_register(0xFF)
  rev_id = MAX30105.i2c_read_register(0xFE)
  print("MAX30105: part ID", hex(ord(part_id)), "revision:", ord(rev_id))
  print("Setting up sensor now:", '\n')
  MAX30105.setup_sensor()
  MAX30105.setPulseAmplitudeRed(0x0A)
  MAX30105.setPulseAmplitudeGreen(0x00)

  try:
    while True:
      listen()

      lastBeat = time.ticks_ms()
        for FIFO_pointer in range(32):
            #try:
            sensor_data = MAX30105.read_sensor_multiLED(FIFO_pointer)
            #print("sensor_data", sensor_data)
            irValue = int(sensor_data[1])

            # red led will be greater than 50000 if your finger is on the sensor
            if (sensor_data[0] < 50000):
                rates = [0] * 4
                rateSpot = 0
                lastBeat = time.ticks_ms()
            else:
              # print("hr ir:", irValue, "red:", sensor_data[0])
              if (HearRateSensor.checkForBeat(irValue)):
                  print("beat")
                  delta = time.ticks_diff(time.ticks_ms(), lastBeat)
                  lastBeat = time.ticks_ms()
                  beatsPerMinute = 60 / (delta/1000)

                  if (beatsPerMinute < 255 and beatsPerMinute > 20):
                      
                      if (rateSpot > 3):
                        rateSpot = 0

                      rates[rateSpot] = beatsPerMinute
                      rateSpot += 1
                      print("rates", rates)

                      beatAvg = 0
                      for x in range(rateSize):
                          beatAvg += rates[x]
                      beatAvg /= rateSize
                      print (beatAvg)


  except (KeyboardInterrupt):
    print('\n', "Exit on Ctrl-C: Good bye!")

  finally:
    print('\n', "Disconnecting.")
   
if __name__ == "__main__":
    main()

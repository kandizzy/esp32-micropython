# This file is executed on every boot (including wake-boot from deepsleep)
import machine, network, utime, neopixel, time
import network
import ubinascii
from pye import pye
from umqtt.simple import MQTTClient
from ppg.MAX30105 import ParticleSensor
from ppg.heartbeat import HeartBeat
from led.ledCtrl import LEDCtrl
from piezo.piezoCtrl import PIEZOCtrl

HearRateSensor = HeartBeat()
LedCtrl = LEDCtrl()
PiezoCtrl = PIEZOCtrl()

#
from machine import Pin
np = neopixel.NeoPixel(Pin(16), 3, timing=1)

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

def alloff():
  n = np.n
  print("all off")
  for i in range(n):
    np[i] = (0,0,0)
  np.write()

def allon():
  print("all on")
  n = np.n
  for i in range(n):
    np[i] = (255, 255, 255)
  np.write()

def heartbeatOnly():
  print("heartbeatOnly")
  LedCtrl.blink( (0,0,0), 500 )

def weatherOnly():
  print("weatherOnly")
  n = np.n
  for i in range(n):
    np[i] = (0, 0, 255)
  np.write()

def heartbeatWeather():
  print("heartbeatWeather")
  n = np.n
  for i in range(n):
    np[i] = (255, 0, 255)
  np.write()

def stockOnly():
  print("stockOnly")
  n = np.n
  for i in range(n):
    np[i] = (0, 255, 0)
  np.write()

def stockHeartbeat():
  print("stockHeartbeat")
  n = np.n
  for i in range(n):
    np[i] = (255, 255, 0)
  np.write()

def stockWeather():
  print("stockWeather")
  n = np.n
  for i in range(n):
    np[i] = (0, 255, 255)
  np.write()

# state
modes = {
  "stock": 0,
  "weather": 0,
  "heartbeat": 0
}
state = 0
switchModes = {
  0: alloff, #000
  1: heartbeatOnly, #001
  2: weatherOnly, #010
  3: heartbeatWeather, #011
  4: stockOnly, #100
  5: stockHeartbeat, #101
  6: stockWeather, #110
  7: allon #111
}
weather = ""

# Default MQTT server to connect to
SERVER = "52.23.85.220"
CLIENT_ID = mac
WEATHER_TOPIC = "spacemen/ck_yr34-35/weather"
STOCK_TOPIC = "spacemen/stock"
MODE_TOPIC = "spacemen/ck_yr34-35/toggle"

def toggleState(mode, onOff):
  global modes
  if onOff =="on":
    toggle = 1
  else:
    toggle = 0 
  modes[mode] = toggle

def setWeather(desc):
  global weather
  weather = desc

def sub_cb(topic, msg):
    global state
    global modes
    t = str(topic, 'utf-8').split("/")
    m = str(msg, 'utf-8').split("/")
    print(t,m)
    data = {}
    for i in range(0, len(m), 2):
      data[m[i]] = m[i+1] 
    if (t[1] == "ck_yr34-35"):
      if t[2] == "toggle":
        toggleState(data["mode"], data["set"])
      if t[2] == "weather":
        setWeather(data["description"])
    blist = []
    blist.append( modes["stock"] )
    blist.append( modes["weather"] )
    blist.append( modes["heartbeat"] )
    s = "".join(map(str, blist))

    if (state != int(s,2)):
      state = int(s, 2)
      switchModes[state]()

def main(server=SERVER):
  print(mac)
  alloff()
  
  print('\n', "Attempting to connect to MQTT server.")
  c = MQTTClient(CLIENT_ID, server)
  c.set_callback(sub_cb)
  c.connect()
  c.subscribe(WEATHER_TOPIC)
  c.subscribe(STOCK_TOPIC)
  c.subscribe(MODE_TOPIC)
  print("Connected to %s, subscribed to %s, %s, %s topics" % (server, WEATHER_TOPIC, STOCK_TOPIC, MODE_TOPIC))

  # this should only be enabled on the red light mode
  MAX30105 = ParticleSensor(HEX_ADDRESS=0x57)
  part_id = MAX30105.i2c_read_register(0xFF)
  rev_id = MAX30105.i2c_read_register(0xFE)
  print("MAX30105: part ID", hex(ord(part_id)), "revision:", ord(rev_id))
  print("Setting up sensor now:", '\n')
  MAX30105.setup_sensor()
  MAX30105.setPulseAmplitudeRed(0x0A)
  MAX30105.setPulseAmplitudeGreen(0x00)

  rates = [0] * 4
  rateSize = len(rates)
  rateSpot = 0
  lastBeat = 0

  try:
    while True:
      PiezoCtrl.listen()
      #micropython.mem_info()
      c.check_msg()
      if (state == 1):
        # print("state 1")
        lastBeat = time.ticks_ms()
        for FIFO_pointer in range(32):
            #try:
            sensor_data = MAX30105.read_sensor_multiLED(FIFO_pointer)
            #print("sensor_data", sensor_data)
            irValue = int(sensor_data[1])
            #print(sensor_data[0])

            # red led will be greater than 50000 if your finger is on the sensor
            if (sensor_data[0] < 40000):
                rates = [0] * 4
                rateSpot = 0
                lastBeat = time.ticks_ms()
                LedCtrl.beatPerMinute(0, False)
                #print("FINGER NOT PRESENT")
            else:
              # print("hr ir:", irValue, "red:", sensor_data[0])
              if (HearRateSensor.checkForBeat(irValue)):
                  
                  delta = time.ticks_diff(time.ticks_ms(), lastBeat)
                  lastBeat = time.ticks_ms()
                  beatsPerMinute = 60 / (delta/1000)
                  print("beatsPerMinute", beatsPerMinute)
                  if (beatsPerMinute < 255 and beatsPerMinute > 20):
                      
                      if (rateSpot > 3):
                        rateSpot = 0

                      rates[rateSpot] = beatsPerMinute
                      rateSpot += 1
                      beatAvg = 0
                      for x in range(rateSize):
                          beatAvg += rates[x]
                      beatAvg /= rateSize
                      print ("beatAvg", beatAvg)
                      LedCtrl.beatPerMinute(beatAvg, True)
      else:
        LedCtrl.beatPerMinute(60, False)

  except (KeyboardInterrupt):
    print('\n', "Exit on Ctrl-C: Good bye!")

  finally:
    print('\n', "Disconnecting.")
    c.disconnect()

    print('\n', "Resetting sensor to power-on defaults!")
    MAX30105.set_bitMask(0x09, 0xBF, 0x40)  # reset to POR

if __name__ == "__main__":
    main()

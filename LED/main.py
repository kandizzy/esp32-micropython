# This file is executed on every boot (including wake-boot from deepsleep)
import machine, network, utime, neopixel, time
import ubinascii
from pye import pye

# gpio==
from machine import Pin# ws2812
np = neopixel.NeoPixel(Pin(16), 4, timing=1)

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

def main():

  print("mac address", mac)
  
 
if __name__ == "__main__":
    main()

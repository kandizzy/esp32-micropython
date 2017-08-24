import time, neopixel
from machine import Pin, Timer
np = neopixel.NeoPixel(Pin(16), 3, timing=1)


class LEDCtrl(object):
    def __init__(self):
        print("LED Display")
        self.deadline = 0
        self.beating = False
        self.beat = 0
        self.fingerPresent = False

    def wheel(self, pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    def showAnimation(self, description):
        print("shownAnimation", description)
        # clear sky
        # few clouds
        # scattered clouds
        # broken clouds
        # shower rain
        # rain
        # thunderstorm
        # snow
        # mist
        # https://openweathermap.org/weather-conditions

    def showKnock(self):
        for i in range(np.n):
            np[i] = (255, 255, 255)
        np.write()
        time.sleep(.2)
        for i in range(np.n):
            np[i] = (0, 0, 0)
        np.write()


    def blink(self, color, duration=100):
        for i in range(np.n):
            np[i] = color
        np.write()
        time.sleep_ms(duration)
        for i in range(np.n):
            np[i] = (0, 0, 0)
        np.write()

    def wrong(self, color):
        for i in range(np.n):
            np[i] = color
        np.write()
        time.sleep_ms(500)
        for i in range(np.n):
            np[i] = (0, 0, 0)
        np.write()
                 
    def rainbow(self, iterations=5):
        n = np.n
        for j in range(256*iterations):
            for i in range(n):
                np[i] = self.wheel((int(i * 256 / n + j) & 255))
                np.write()
                time.sleep_ms(2)

        for i in range(n):
            np[i] = (0, 0, 0)
        np.write()  

    def heartbeat(self):
        print("heartbeat")
        for i in range(0, 4 * 256, 8):
            for j in range(np.n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                np[j] = (val, 0, 0) 
            np.write()
            time.sleep_ms(2)
        self.beating = False
        print("end heartbeat")
        self.beatPerMinute(self.beat, self.fingerPresent)

    def pulseTimer(self, t):
        if (time.ticks_ms() >= self.deadline):
            self.beating = True
            t.deinit()
            self.heartbeat()

    def beatPerMinute(self, beat, on): 
        self.beat = beat
        self.fingerPresent = on
        if self.fingerPresent:
            # finger is on
            if self.beating == False:
                self.beating = True
                # calculate the time to wait in between pulses
                pulse = int( (60 * 1000) / beat )
                self.deadline = time.ticks_add(time.ticks_ms(), pulse)
                print("d:", self.deadline, "pulse:", pulse)
                timer = Timer(0)  # timer id is in range 0-3     
                timer.init(period=80, mode=Timer.PERIODIC, callback=self.pulseTimer)

        else:
            self.deadline = time.ticks_ms()
            #print("no finger")  


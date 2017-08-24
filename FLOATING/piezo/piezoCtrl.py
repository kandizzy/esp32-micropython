from machine import ADC, Pin
from led.ledCtrl import LEDCtrl
import utime
import time
adc = ADC(Pin(34))

class PIEZOCtrl(object):
    def __init__(self):
        self.LedCtrl = LEDCtrl()
        self.threshold = 100 # detect knock
        self.rejectVal = 25 # single knock reject
        self.averageRejectVal = 15 # overall reject
        self.knockFadeTime = 150 # sleep
        self.maximumKnocks = 6 #max knocks
        self.knockComplete = 1200 # timeout
        self.secretCode = [50, 25, 25, 50, 100, 50]
        self.knockReadings = []
        self.knockSensorValue = 0
        self.programming = False

    def map(self, x, in_min, in_max, out_min, out_max):
        return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

    def validateKnock(self):
        print("validateKnock", self.knockReadings)
        if (len(self.knockReadings) < 1):
            return False
        i = 0
        currentKnockCount = 0
        secretKnockCount = 0
        maxKnockInterval = 0

        for i in range(len(self.knockReadings)):
            if (self.knockReadings[i] > 0):
                currentKnockCount += 1
            if (self.secretCode[i] > 0):
                secretKnockCount += 1
            if (self.knockReadings[i] > maxKnockInterval):
                maxKnockInterval = self.knockReadings[i]

        if (self.programming == True):
            for i in range(len(self.secretCode)):
                secretCode[i] = self.map(self.knockReadings[i], 0, maxKnockInterval, 0, 100)
            self.LedCtrl.blink( (0,255,0) ) #recorded
            time.sleep_ms(50)

        if (currentKnockCount != secretKnockCount):
            return False

        totaltimeDifferences = 0
        timeDiff = 0
        for i in range(len(self.knockReadings)):
            self.knockReadings[i] = self.map(self.knockReadings[i], 0, maxKnockInterval, 0, 100)
            timeDiff = abs(self.knockReadings[i] - self.secretCode[i]);
            if (timeDiff > self.rejectVal):
                return False
    
            totaltimeDifferences += timeDiff
 
        if (totaltimeDifferences / secretKnockCount > self.averageRejectVal):
            return False

        return True

    def listenForSecret(self):
        print("knock starting")
        self.knockReadings = []
        
        currentKnockNumber = 0
        startTime = time.ticks_ms()
        now = time.ticks_diff(time.ticks_ms(), startTime)
        self.LedCtrl.blink( (0,125,0) )
        if (self.programming == True):
            self.LedCtrl.blink( (255, 0 ,0) )
        time.sleep_ms(self.knockFadeTime)
              
        #listen for the next knock or wait for it to timeout.
        while ((now <= self.knockComplete) and (currentKnockNumber < len(self.secretCode))):
            self.knockSensorValue = adc.read()
            if (self.knockSensorValue <= self.threshold):
                print(self.knockSensorValue, ": knock")
                delta = time.ticks_diff(time.ticks_ms(), startTime)
                self.knockReadings.append(delta);
                currentKnockNumber += 1
                startTime = time.ticks_ms()
                now = time.ticks_diff(time.ticks_ms(), startTime)
                self.LedCtrl.blink( (0,125,0) )
                if (self.programming == True):
                    self.LedCtrl.blink( (125, 0 ,0) )
                time.sleep_ms(self.knockFadeTime)
            now = time.ticks_diff(time.ticks_ms(), startTime)
                
        if (self.programming == False):
            if (self.validateKnock() == True):
                print("success")
                self.LedCtrl.rainbow(2)
            else:
                print("fail")
                self.LedCtrl.wrong( (125, 0 ,0) )
        else:
            print("completed programming !")
            self.LedCtrl.blink( (0, 255, 0), 1000)


    def listen(self):
        if adc.read() < self.threshold:
            self.listenForSecret()



from ustruct import unpack
from machine import I2C, Pin
import time
#init i2c var
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)

# PARTICLE SENSOR
class ParticleSensor(object):
    def __init__(self, HEX_ADDRESS):
        self._address = HEX_ADDRESS
        self._led_mode = None
        self._pulse_width_set = None
        try:
            i2c.readfrom(self._address, 1)
        except OSError as error:
            raise SystemExit(error)
        else:
            print("Found MAX30105 ParticleSensor: [%s]" % hex(self._address))

    def CreateImage(self, value):
        unit = (2 ** (18 - self._pulse_width_set)) // (250)
        image_p1 = (value // (unit * 50)) * (str(9) * 5)
        image_p2 = ((value % (unit * 50)) // (unit * 10)) * str(9)
        points = (((value % (unit * 50)) % (unit * 10))) // unit
        if points > 0:
            image_p3 = str(points)
        else:
            image_p3 = ""
        image_p4 = ((25) - len(image_p1 + image_p2 + image_p3)) * str(0)
        tmp_image = image_p1 + image_p2 + image_p3 + image_p4
        return ':'.join([tmp_image[i:i+5] for i in range(0, len(tmp_image), 5)])

    def i2c_read_register(self, REGISTER, n_bytes=1):
        i2c.writeto(self._address, bytearray([REGISTER]))
        return i2c.readfrom(self._address, n_bytes)

    def i2c_set_register(self, REGISTER, VALUE):
        i2c.writeto(self._address, bytearray([REGISTER, VALUE]))
        return

    def set_bitMask(self, REGISTER, MASK, NEW_VALUES):
        newCONTENTS = (ord(self.i2c_read_register(REGISTER)) & MASK) | NEW_VALUES
        self.i2c_set_register(REGISTER, newCONTENTS)
        return

    def enableSlot(self, slotNumber, device):
        if (slotNumber == 1):
            self.bitMask(0x11, 0xF8, 0x01) # 0x11 config1, slot mask 1, 0x01 red
        if (slotNumber == 2):
            self.bitMask(0x11, 0x8F, 0x02 << 4) # 0x11 config1, slot mask 2, 0x01 IR
        if (slotNumber == 3):
            self.bitMask(0x12, 0xF8, 0x03) # 0x11 config2, slot mask 3, 0x01 green

    def bitMask(self, reg, slotMask, thing):

        originalContents = ord(self.i2c_read_register(reg))
        originalContents = originalContents & slotMask
        self.i2c_set_register(reg, originalContents | thing)

    def setup_sensor(self, LED_MODE=3, LED_POWER=0x1F, PULSE_WIDTH=0):
        self.set_bitMask(0x09, 0xBF, 0x40)
        time.sleep_ms(1000)
        # 3: 69 (15-bit), 2: 118 (16-bit), 1: 215 (17-bit), 0: 411 (18-bit)          
        self.set_bitMask(0x0A, 0xFC, PULSE_WIDTH)
        self._pulse_width_set = PULSE_WIDTH

        if LED_MODE not in [1, 2, 3]:
            raise ValueError('wrong LED mode:{0}!'.format(LED_MODE))
        elif LED_MODE == 1:
            self.set_bitMask(0x09, 0xF8, 0x02)
            self.i2c_set_register(0x0C, LED_POWER) #red
        elif LED_MODE == 2:
            self.set_bitMask(0x09, 0xF8, 0x03)
            self.i2c_set_register(0x0C, LED_POWER) #red
            self.i2c_set_register(0x0D, LED_POWER) #ir
        elif LED_MODE == 3:
            self.set_bitMask(0x09, 0xF8, 0x07)
            self.i2c_set_register(0x0C, LED_POWER) #red
            self.i2c_set_register(0x0D, LED_POWER) #ir
            self.i2c_set_register(0x0E, LED_POWER) #green
            
            #self.setPulseAmplitudeRed(LED_POWER)
            #self.setPulseAmplitudeIR(LED_POWER)
            #self.setPulseAmplitudeGreen(LED_POWER)
            #self.setPulseAmplitudeProximity(LED_POWER)


            #self.enableSlot(1, 0x01) # is this gonnna work?
            #self.enableSlot(2, 0x02)
            #self.enableSlot(3, 0x03)

            self.i2c_set_register(0x11, 0b00100001) #mulitledconfig1
            self.i2c_set_register(0x12, 0b00000011) #mutliledconfig2
        self._led_mode = LED_MODE

        # OG self.set_bitMask(0x0A, 0xE3, 0x00)  # sampl. rate: 50
        self.set_bitMask(0x0A, 0xE3, 0x00)
        # 50: 0x00, 100: 0x04, 200: 0x08, 400: 0x0C,
        # 800: 0x10, 1000: 0x14, 1600: 0x18, 3200: 0x1C

        self.set_bitMask(0x0A, 0x9F, 0x00)  # ADC range: 2048
        # 2048: 0x00, 4096: 0x20, 8192: 0x40, 16384: 0x60

        self.set_bitMask(0x08, ~0b11100000, 0x40)  # FIFO sample avg: (no)
        # 1: 0x00, 2: 0x20, 4: 0x40, 8: 0x60, 16: 0x80, 32: 0xA0

        self.set_bitMask(0x08, 0xEF, 0x10)  # FIFO rollover: enable
        # 0x00/0x01: dis-/enable

        # clears the fifo
        self.i2c_set_register(0x04, 0) # fifowriteptr
        self.i2c_set_register(0x05, 0) # fifooverflow
        self.i2c_set_register(0x06, 0) # fifoadapter

    def setPulseAmplitudeRed(self, amplitude):
        self.i2c_set_register(0x0C, amplitude)

    def setPulseAmplitudeGreen(self, amplitude):
        self.i2c_set_register(0x0E, amplitude)
    
    def setPulseAmplitudeIR(self, amplitude):
        self.i2c_set_register(0x0D, amplitude)

    def setPulseAmplitudeProximity(self, amplitude):
        self.i2c_set_register(0x10, amplitude)

    def FIFO_bytes_to_int(self, FIFO_bytes):
        value = unpack(">i", b'\x00' + FIFO_bytes)
        return (value[0] & 0x3FFFF) >> self._pulse_width_set

    def read_sensor_multiLED(self, pointer_position):
        time.sleep_ms(25)
        self.i2c_set_register(0x06, pointer_position) #mutliled
        fifo_bytes = self.i2c_read_register(0x07, self._led_mode * 3) #mode_mult

        red_int = self.FIFO_bytes_to_int(fifo_bytes[0:3])
        IR_int = self.FIFO_bytes_to_int(fifo_bytes[3:6])
        green_int = self.FIFO_bytes_to_int(fifo_bytes[6:9])
        
        #print("[Red:", red_int, " IR:", IR_int, " G:", green_int, "]", sep='')
        
        return red_int, IR_int, green_int

import RPi.GPIO as GPIO
import time


class pinmode(object):
    def __init__(self):
        # sensor
        self._CS = 5
        self._CLOCK = 25
        self._ADDRESS = 24
        self._DATAOUT = 23
        # motor
        self._left_1 = 12
        self._left_2 = 13
        self._CONTROL_A = 6
        self._right_1 = 20
        self._right_2 = 21
        self._CONTROL_B = 26
        # avoidance
        self._DR = 16
        self._DL = 19
        # IRremote
        self._IR = 17
        self.mode()

    @staticmethod
    def mode():
        GPIO.setmode(GPIO.BCM)

    @staticmethod
    def clean():
        GPIO.cleanup()


class setmotor(pinmode):
    def __init__(self):
        super(setmotor, self).__init__()
        GPIO.setup((self._left_1, self._left_2, self._CONTROL_A), GPIO.OUT)
        GPIO.setup((self._right_1, self._right_2, self._CONTROL_B), GPIO.OUT)
        self._speed_A = GPIO.PWM(self._CONTROL_A, 1000)
        self._speed_B = GPIO.PWM(self._CONTROL_B, 1000)
        self._speed_A.start(0)
        self._speed_B.start(0)

    @staticmethod
    def __judgespeed__(velocity):
        if 100 >= velocity >= 0:
            pass
        else:
            velocity = 20
        return velocity

    def changespeed(self, velocity):
        velocity = self.__judgespeed__(velocity)
        self._speed_A.ChangeDutyCycle(velocity)
        self._speed_B.ChangeDutyCycle(velocity)

    def forward(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (0, 1))
        GPIO.output((self._right_1, self._right_2), (0, 1))
        velocity = self.__judgespeed__(velocity)
        if velocity < 5:
            self._speed_A.ChangeDutyCycle(5)
            self._speed_B.ChangeDutyCycle(5)
        else:
            self._speed_A.ChangeDutyCycle(velocity)
            self._speed_B.ChangeDutyCycle(velocity)

    def backward(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (1, 0))
        GPIO.output((self._right_1, self._right_2), (1, 0))
        velocity = self.__judgespeed__(velocity)
        self._speed_A.ChangeDutyCycle(velocity)
        self._speed_B.ChangeDutyCycle(velocity)

    def stop(self):
        self._speed_A.ChangeDutyCycle(0)
        self._speed_B.ChangeDutyCycle(0)

    def rightward(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (0, 1))
        GPIO.output((self._right_1, self._right_2), (1, 0))
        self._speed_A.ChangeDutyCycle(velocity)
        self._speed_B.ChangeDutyCycle(velocity)
        time.sleep(0.2)
        self.forward(velocity)

    def leftward(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (1, 0))
        GPIO.output((self._right_1, self._right_2), (0, 1))
        self._speed_A.ChangeDutyCycle(velocity)
        self._speed_B.ChangeDutyCycle(velocity)
        time.sleep(0.2)
        self.forward(velocity)

    def swerveright(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (0, 1))
        GPIO.output((self._right_1, self._right_2), (0, 1))
        self._speed_A.ChangeDutyCycle(velocity + 5)
        self._speed_B.ChangeDutyCycle(velocity)

    def swerveleft(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (0, 1))
        GPIO.output((self._right_1, self._right_2), (0, 1))
        self._speed_A.ChangeDutyCycle(velocity)
        self._speed_B.ChangeDutyCycle(velocity + 5)

    def backswerveright(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (1, 0))
        GPIO.output((self._right_1, self._right_2), (1, 0))
        self._speed_A.ChangeDutyCycle(velocity + 5)
        self._speed_B.ChangeDutyCycle(velocity)

    def backswerveleft(self, velocity=20):
        GPIO.output((self._left_1, self._left_2), (1, 0))
        GPIO.output((self._right_1, self._right_2), (1, 0))
        self._speed_A.ChangeDutyCycle(velocity)
        self._speed_B.ChangeDutyCycle(velocity + 5)


class setavoid(setmotor):
    def __init__(self):
        super(setavoid, self).__init__()
        GPIO.setwarnings(False)
        GPIO.setup(self._DR, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self._DL, GPIO.IN, GPIO.PUD_UP)
        # self.av = setmotor()

    def __status__(self):
        DR_status = GPIO.input(self._DR)
        DL_status = GPIO.input(self._DL)
        return [DL_status, DR_status]

    def avoidance(self):
        status = self.__status__()
        if status[0] == 0 and status[1] == 1:
            self.rightward()
            time.sleep(0.5)
        elif status[0] == 1 and status[1] == 0:
            self.leftward()
            time.sleep(0.5)
        elif status[0] == 0 and status[1] == 0:
            self.leftward()
            time.sleep(1)
        else:
            self.forward(10)


class remote(setmotor):
    def __init__(self):
        super(remote, self).__init__()
        GPIO.setup(self._IR, GPIO.IN, GPIO.PUD_UP)

        # avoid
        GPIO.setwarnings(False)
        GPIO.setup(self._DR, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self._DL, GPIO.IN, GPIO.PUD_UP)

        # tracksensor
        self.__base = 5
        self.__base2 = self.__base * 2
        self.__wait = 0.1
        self.__wait2 = self.__wait * 2
        GPIO.setup((self._CS, self._CLOCK, self._ADDRESS),
                   GPIO.OUT)
        GPIO.setup(self._DATAOUT, GPIO.IN, GPIO.PUD_UP)

        self.__velocity = 10
        self.__keymap = {
            0x45: 'CH-', 0x46: 'CH ', 0x47: 'CH+',
            0x44: '<<<', 0x40: '>>>', 0x43: '>>|',
            0x07: ' - ', 0x15: ' + ', 0x09: 'EQ ',
            0x16: ' 0 ', 0x19: '100+', 0x0D: '200+',
            0x0C: ' 1 ', 0x18: ' 2 ', 0x5E: ' 3 ',
            0x08: ' 4 ', 0x1C: ' 5 ', 0x5A: ' 6 ',
            0x42: ' 7 ', 0x52: ' 8 ', 0x4A: ' 9 '
        }

    @staticmethod
    def getkey():
        f = open('/dev/input/event0', 'rb')
        line = f.read(21)
        key_decimal = int(line[-1])
        f.read(75)
        f.close()
        return key_decimal

    def __accelerate__(self):
        if self.__velocity < 100:
            self.__velocity += 1
        else:
            self.__velocity = 100
        self.changespeed(self.__velocity)

    def __moderate__(self):
        if self.__velocity > 0:
            self.__velocity -= 1
        else:
            self.__velocity = 0
        self.changespeed(self.__velocity)

    def __highacceralte__(self):
        if self.__velocity + 10 > 100:
            self.__velocity = 100
        else:
            self.__velocity += 10
        self.changespeed(self.__velocity)

    def __highmoderate__(self):
        if self.__velocity - 10 < 0:
            self.__velocity = 0
        else:
            self.__velocity -= 10
        self.changespeed(self.__velocity)

    def __maxspeed__(self):
        self.__velocity = 100
        self.changespeed(self.__velocity)

    def __status__(self):
        DR_status = GPIO.input(self._DR)
        DL_status = GPIO.input(self._DL)
        return [DL_status, DR_status]

    def __avoidance__(self):
        status = self.__status__()
        if status[0] == 0 and status[1] == 1:
            self.rightward(self.__velocity)
        elif status[0] == 1 and status[1] == 0:
            self.leftward(self.__velocity)
        elif status[0] == 0 and status[1] == 0:
            self.leftward(self.__velocity)
        else:
            pass

    def __analogread__(self):
        value = [0] * 6
        for j in range(0, 6):
            GPIO.output(self._CS, GPIO.LOW)
            for i in range(0, 10):
                if i < 4:
                    bit = ((j >> (3 - i)) & 0x01)
                    GPIO.output(self._ADDRESS, bit)
                value[j] <<= 1
                value[j] |= GPIO.input(self._DATAOUT)
                GPIO.output(self._CLOCK, GPIO.HIGH)
                GPIO.output(self._CLOCK, GPIO.LOW)
            GPIO.output(self._CS, GPIO.HIGH)
            time.sleep(0.0001)
        return value[1:]

    def track(self):
        data = self.__analogread__()
        number = 0
        judge = 0
        if data[0] > 200:
            judge = -1
        for i in range(1, 5):
            if data[i] < data[number] and data[i] < 200:
                number = i
        if number == 0 and judge == -1:
            number = -1
        if number == 0:
            self.swerveleft(self.__base)
            time.sleep(self.__wait2)
        elif number == 1:
            self.swerveleft(self.__base)
            time.sleep(self.__wait)
        elif number == 2:
            self.forward(self.__base2)
        elif number == 3:
            self.swerveright(self.__base)
            time.sleep(self.__wait)
        elif number == 4:
            self.swerveright(self.__base)
            time.sleep(self.__wait2)
        else:
            self.forward(self.__base2)

    def move(self):
        key = self.getkey()
        # self.__avoidance__()
        if key is not None:
            try:
                if self.__keymap[key] == ' 2 ':
                    self.forward(self.__velocity)
                elif self.__keymap[key] == ' 8 ':
                    self.backward(self.__velocity)
                elif self.__keymap[key] == ' 4 ':
                    self.leftward(self.__velocity)
                elif self.__keymap[key] == ' 6 ':
                    self.rightward(self.__velocity)
                elif self.__keymap[key] == ' 5 ':
                    self.stop()
                elif self.__keymap[key] == ' + ':
                    self.__accelerate__()
                elif self.__keymap[key] == ' - ':
                    self.__moderate__()
                elif self.__keymap[key] == '>>>':
                    self.__highacceralte__()
                elif self.__keymap[key] == '<<<':
                    self.__highmoderate__()
                elif self.__keymap[key] == '>>|':
                    self.__maxspeed__()
                elif self.__keymap[key] == ' 1 ':
                    self.swerveleft(self.__velocity)
                elif self.__keymap[key] == ' 3 ':
                    self.swerveright(self.__velocity)
                elif self.__keymap[key] == ' 7 ':
                    self.backswerveleft(self.__velocity)
                elif self.__keymap[key] == ' 9 ':
                    self.backswerveright(self.__velocity)
                # elif self.__keymap[key] == 'EQ ':
                #     self.track()
            except IndexError:
                pass


class setsensor(setmotor):
    def __init__(self):
        super(setsensor, self).__init__()
        self.__base = 5
        self.__base2 = self.__base * 2
        self.__wait = 0.1
        self.__wait2 = self.__wait * 2
        GPIO.setup((self._CS, self._CLOCK, self._ADDRESS),
                   GPIO.OUT)
        GPIO.setup(self._DATAOUT, GPIO.IN, GPIO.PUD_UP)

    def analogread(self):
        value = [0] * 6
        for j in range(0, 6):
            GPIO.output(self._CS, GPIO.LOW)
            for i in range(0, 10):
                if i < 4:
                    bit = ((j >> (3 - i)) & 0x01)
                    GPIO.output(self._ADDRESS, bit)
                value[j] <<= 1
                value[j] |= GPIO.input(self._DATAOUT)
                GPIO.output(self._CLOCK, GPIO.HIGH)
                GPIO.output(self._CLOCK, GPIO.LOW)
            GPIO.output(self._CS, GPIO.HIGH)
            time.sleep(0.0001)
        return value[1:]

    def track(self):
        data = self.analogread()
        number = 0
        judge = 0
        if data[0] > 200:
            judge = -1
        for i in range(1, 5):
            if data[i] < data[number] and data[i] < 200:
                number = i
        if number == 0 and judge == -1:
            number = -1
        if number == 0:
            self.swerveleft(self.__base)
            time.sleep(self.__wait2)
        elif number == 1:
            self.swerveleft(self.__base)
            time.sleep(self.__wait)
        elif number == 2:
            self.forward(self.__base2)
        elif number == 3:
            self.swerveright(self.__base)
            time.sleep(self.__wait)
        elif number == 4:
            self.swerveright(self.__base)
            time.sleep(self.__wait2)
        else:
            self.forward(self.__base2)



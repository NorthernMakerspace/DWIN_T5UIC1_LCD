# Class to monitor a rotary encoder and update a value.  You can either read the value when you need it, by calling getValue(), or
# you can configure a callback which will be called whenever the value changes.

import odroid_wiringpi as wiringpi

class Encoder:

    def __init__(self, leftPin, rightPin, callback=None):
        self.leftPin = leftPin
        self.rightPin = rightPin
        self.value = 0
        self.state = '00'
        self.direction = None
        self.callback = callback
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.leftPin, 0)
        wiringpi.pinMode(self.rightPin, 0)
        wiringpi.pullUpDnControl(self.leftPin, wiringpi.PUD_UP)
        wiringpi.pullUpDnControl(self.rightPin, wiringpi.PUD_UP)
        wiringpi.wiringPiISR(self.leftPin, wiringpi.INT_EDGE_BOTH, self.transitionOccurred)
        wiringpi.wiringPiISR(self.rightPin, wiringpi.INT_EDGE_BOTH, self.transitionOccurred)

    def transitionOccurred(self, channel):
        p1 = wiringpi.digitalRead(self.leftPin)
        p2 = wiringpi.digitalRead(self.rightPin)
        newState = "{}{}".format(p1, p2)

        if self.state == "00": # Resting position
            if newState == "01": # Turned right 1
                self.direction = "R"
            elif newState == "10": # Turned left 1
                self.direction = "L"

        elif self.state == "01": # R1 or L3 position
            if newState == "11": # Turned right 1
                self.direction = "R"
            elif newState == "00": # Turned left 1
                if self.direction == "L":
                    self.value = self.value - 1
                    if self.callback is not None:
                        self.callback(self.value)

        elif self.state == "10": # R3 or L1
            if newState == "11": # Turned left 1
                self.direction = "L"
            elif newState == "00": # Turned right 1
                if self.direction == "R":
                    self.value = self.value + 1
                    if self.callback is not None:
                        self.callback(self.value)

        else: # self.state == "11"
            if newState == "01": # Turned left 1
                self.direction = "L"
            elif newState == "10": # Turned right 1
                self.direction = "R"
            elif newState == "00": # Skipped an intermediate 01 or 10 state, but if we know direction then a turn is complete
                if self.direction == "L":
                    self.value = self.value - 1
                    if self.callback is not None:
                        self.callback(self.value)
                elif self.direction == "R":
                    self.value = self.value + 1
                    if self.callback is not None:
                        self.callback(self.value)
                
        self.state = newState

    def getValue(self):
        return self.value

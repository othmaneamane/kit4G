__author__ = 'amaneothmane'

# !/usr/bin/env python
# -*- coding: latin-1 -*-
# inspired by the code from http://mchobby.be/wiki/index.php?title=Rasp-Hack-PiAnalog
# made for 4Gkit for IoT
# Author : AMANE Othmane (Orange)

import time
from pyA13.gpio import gpio
from pyA13.gpio import port

gpio.init()
DEBUG = 1


# this function reads adc value from the channel channelNumber of the mcp3008 ADC
#  clockPin is the pin to the


def readadc(channelNumber, clockPin, kitoutputPin, kitInputPin, chipSelectPin):
    # First of all we only have eight channels from 0 to 7, other values are not accepted, sorry!

    if (channelNumber > 7) or (channelNumber < 0):
        print("channel number should be between 0 and 7")
        return -1

    # chipSelectPin should be brought high and back low to initiate communication

    gpio.output(chipSelectPin, gpio.HIGH)
    gpio.output(clockPin, gpio.LOW)
    gpio.output(chipSelectPin, gpio.LOW)

    # configuration bits (configBits) sequence is constructed as follow :
    # start bit + single-ended bit + channel number (3 bits) + 000 (not sent; see below)

    # Example : let's say I am using channel number 3 then configBits = start bit (1) +
    #                      single-ended bit (1) + channel number (011) + 000 = 11011000

    # another way to find the same value is channelNumber channelNumber (00000011) LOGICAL OR 0x18 (00011000)
    #                                        SHIFTED three bits to left      = 11011000

    configBits = channelNumber
    configBits |= 0x18
    configBits <<= 3

    # send configurationn bits to the mcp3008 module
    # every time the MSB is extracted then sent

    for i in range(5):
        if configBits & 0x80:
            gpio.output(kitoutputPin, gpio.HIGH)
        else:
            gpio.output(kitoutputPin, gpio.LOW)
        configBits <<= 1

        # clock signal
        gpio.output(clockPin, gpio.HIGH)
        gpio.output(clockPin, gpio.LOW)

        # reading bits from the mcp3008 module channel, the module sends 10 bit
        # one idle bit is sent before and another one after the data, a total of twelve bits is sent

        readInput = 0
        for index in range(10):
            # clock
            gpio.output(clockPin, gpio.HIGH)
            gpio.output(clockPin, gpio.LOW)
            readInput <<= 1
            if gpio.input(kitInputPin):
                readInput |= 0x1

        # disable the mcp3008 module
        gpio.output(chipSelectPin, gpio.HIGH)

        return readInput


SPICLK = port.PE9
SPIMISO = port.PE8
SPIMOSI = port.PE7
SPICS = port.PE6

# Initialization of the gpios used
gpio.setcfg(SPIMOSI, gpio.OUTPUT)
gpio.setcfg(SPIMISO, gpio.INPUT)
gpio.setcfg(SPICLK, gpio.OUTPUT)
gpio.setcfg(SPICS, gpio.OUTPUT)

# the analog device is placed on channel 0 here, you can change it if you
# need to do so
chosenChannel = 0

while gpio.HIGH:
    # read analog value (0 to 1023)
    trim_pot = readadc(chosenChannel, SPICLK, SPIMOSI, SPIMISO, SPICS)

    print("Value: " + str(trim_pot))

    # convert the read value to a voltage
    print("voltage: " + str((3.3 * trim_pot) / 1024))
    print("")
    # wait half a second
    time.sleep(0.5)

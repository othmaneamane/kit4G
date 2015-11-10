#!/usr/bin/python
# inspired by http://www.uugear.com/portfolio/dht11-humidity-temperature-sensor-module/
# made for 4Gkit for IoT
# Author : AMANE Othmane (Orange)

import time
import os
import sys
import getopt

if not os.getegid() == 0:
    sys.exit('Script must be run as root')

from pyA13.gpio import gpio
from pyA13.gpio import port


def DHT11Measures():
    # --------------------------------------
    # initialisation
    # refer to the tutorial for more information about the
    # GPIO pins in the A13-SOM-LTE

    sensor = port.PE11
    gpio.init()

    # --------------------------------------
    # trigger measure

    gpio.setcfg(sensor, gpio.OUTPUT)
    gpio.output(sensor, 1)
    time.sleep(0.025)
    gpio.output(sensor, 0)
    time.sleep(0.02)

    # ----------------------------------------
    # grab data

    gpio.setcfg(sensor, gpio.INPUT)


    data = []
    bit_count = 0
    tmp = 0
    count = 0
    HumidityBit = "0"
    TemperatureBit = ""
    crc = ""
    threshold = 9

    for i in range(0, 1500):
        data.append(gpio.input(sensor))
    print(data)
    print("")
    print("")

    # --------------------------------------------
    # treat data to extract the values


    def bin2dec(string_num):
        return str(int(string_num, 2))

    try:

        # You may need to add this to your code, as normally the sensor
        # starts by sending a short sequence of 0s then another short
        # sequence of 1s to show it is available before sending the
        # metrics data, as I could not see this in my data I just did not
        # use this code

        # The first bit of data being normally truncated and as it is a zero for sure
        # (humidity is always under 100%) then we directly put a 0 in HumidityBit and we read
        # the next 31 bits which are structured as follows :
        # Humidity (7bits) - 0 byte - Temperature (8bits) - 0
        for i in range(0, 31):
            bit_count = 0

            while data[count] == 0:
                tmp = 1
                count += 1

            while data[count] == 1:
                bit_count += 1
                count += 1

            if bit_count > threshold:
                if 0 <= i < 7:
                    HumidityBit += "1"
                if 15 <= i < 23:
                    TemperatureBit += "1"
            else:
                if 0 <= i < 7:
                    HumidityBit += "0"
                if 15 <= i < 23:
                    TemperatureBit += "0"

    except Exception as e:
        print(e)
        print("A problem occurred during data gathering")
        exit(0)

    # the next 8 bits encode CRC which is equal to the sum of
    # the temperature value and the humidity value

    try:
        for i in range(0, 8):
            bit_count = 0

            while data[count] == 0:
                tmp = 1
                count += 1

            while data[count] == 1:
                bit_count += 1
                count += 1

            if bit_count > threshold:
                crc += "1"
            else:
                crc += "0"

    except Exception as e:
        print(e)
        print("A problem occurred during CRC calculation")
        exit(0)

    Humidity = bin2dec(HumidityBit)
    Temperature = bin2dec(TemperatureBit)

    # --------------------------------------
    # Check CRC is correct then print results

    if int(Humidity) + int(Temperature) - int(bin2dec(crc)) == 0:
        return int(Humidity), int(Temperature)
    else:
        print("Wrong data, incorrect CRC")
        return None

def main(argv):

    # variables initialisation

    measurementNumber = 1
    sleepingTime = 20
    measurements = []

    # command line arguments processing

    try:
        opts, args = getopt.getopt(argv, "hn:s:")
    except getopt.GetoptError:
        print('test.py -n <measurementsNumber> -s <sleepingTime>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -n <measurementsNumber> -s <sleepingTime>')
            sys.exit()
        elif opt == '-n':
            measurementNumber = int(arg)
        elif opt == '-s':
            sleepingTime = int(arg)

    print("number of measurements : ", measurementNumber)
    print("sleeping time : ", sleepingTime)

    # Sensor data gathering

    for index in range(0, measurementNumber):
        measurements.append((index + 1, DHT11Measures()))
        time.sleep(sleepingTime)

    print(measurements)

if __name__ == "__main__":
    main(sys.argv[1:])
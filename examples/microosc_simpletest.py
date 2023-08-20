# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: Unlicense

"""Demonstrate MicroOSC library in CircuitPython, assumes native `wifi` support"""

import time
import os
import wifi

import micro_osc

UDP_HOST = "224.0.0.1"  # multicast UDP
UDP_PORT = 5000

ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

print("connecting to WiFi", ssid)
wifi.radio.connect(ssid, password)

def fader_handler(msg):
    """Used to handle 'fader' OscMsgs, printing it as a '*' text progress bar
    :param OscMsg msg: message with one required float32 value
    """
    print(msg.addr, "*" * int(20 * msg.args[0]))  # make a little bar chart

dispatch_map = {
    "/": lambda msg: print("/:", msg.addr, msg.args),  # prints all messages
    "/1/fader": fader_handler,
    "/filter1": fader_handler,
}

osc_server = micro_osc.Server(UDP_HOST, UDP_PORT)

print("MicroOSC server started on ", UDP_HOST, UDP_PORT)

last_time = time.monotonic()

while True:
    osc_server.poll(dispatch_map)  # blocks until packet comes in
    if time.monotonic() - last_time > 1.0:
        last_time = time.monotonic()
        print(f"waiting {last_time:.2f}")

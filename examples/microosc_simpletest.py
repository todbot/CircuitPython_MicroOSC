# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: Unlicense


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

osc_server = micro_osc.Server(UDP_HOST, UDP_PORT)


# last_velocity = 0
def note_handler(msg, last_velocity=0):
    # global last_velocity
    if msg.addr == "/Note1":
        print("NOTE", msg.args[0], last_velocity)
    elif msg.addr == "/Velocity1":
        last_velocity = msg.args[0]


dispatch_map = {
    "/": lambda msg: print("/:", msg.addr, msg.args),
    # this is how Live's OSC MIDI Send plugin works
    "/Note1": note_handler,
    "/Velocity1": note_handler,
}

print("MicroOSC server started on ", UDP_HOST, UDP_PORT)

last_time = time.monotonic()

while True:
    osc_server.poll(dispatch_map)  # blocks until packet comes in
    if time.monotonic() - last_time > 0.5:
        last_time = time.monotonic()
        # print("hi")
    time.sleep(0.01)

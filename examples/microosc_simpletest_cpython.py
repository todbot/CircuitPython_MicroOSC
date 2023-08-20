# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: Unlicense

"""Demonstrate MicroOSC library in desktop Python (CPython)"""

import sys
import time

import microosc

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("microosc_simpletest_cpython.py <host> <port>")
    sys.exit(0)

UDP_HOST = sys.argv[1]
UDP_PORT = int(sys.argv[2])


def fader_handler(msg):
    """Used to handle 'fader' OscMsgs, printing it as a '*' text progress bar
    :param OscMsg msg: message with one required float32 value
    """
    print(msg.addr, "*" * int(20 * msg.args[0]))  # make a little bar chart


dispatch_map = {
    # matches all messages
    "/": lambda msg: print("msg:", msg.addr, msg.args),
    # maches how Live's OSC MIDI Send plugin works
    #'/Note1' : note_handler,
    #'/Velocity1' : note_handler,
    # /1/fader3 matches how TouchOSC sends faders ,"/1" is screen, "fader3" is 3rd fader
    "/1/fader": fader_handler,
    "/filter1": fader_handler,
}

osc_server = microosc.OSCServer(UDP_HOST, UDP_PORT, dispatch_map)

print("server started on ", UDP_HOST, UDP_PORT)

last_time = time.monotonic()

while True:
    osc_server.poll()

    if time.monotonic() - last_time > 0.5:
        last_time = time.monotonic()
        print(f"waiting {time.monotonic():.2f}")

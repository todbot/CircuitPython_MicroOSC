# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: Unlicense

"""Demonstrate MicroOSC library in CPython"""

import time
import socket

import microosc

# osc_client = microosc.OSCClient(socket, "224.0.0.1", 5000)  # Multicast UDP
osc_client = microosc.OSCClient(socket, "127.0.0.1", 5000)  # regular UDP

# send two floats
# msg = microosc.OscMsg("/1/xy1", [0.99, 0.3], ("f", "f")) # fmt-skip
# send two ints
# msg = microosc.OscMsg("/1/xy1", [3, 3], ("i", "i")) # fmt-skip
# send four ints
msg = microosc.OscMsg("/1/xyzw", [3, 4, 5, 6], ("i", "i", "i", "i"))  # fmt-skip
# send alternating floats and ints
# msg = microosc.OscMsg("/1/xyzw", [3, 4, 5, 6], ("f", "i", "f", "i")) # fmt-skip
# send int and string
# msg = microosc.OscMsg("/1/message", [123, "hello there"], ("i", "s")) # fmt-skip

i = 100
while True:
    # msg.args[0] = i * 0.01  # move the value a bit
    msg.args[0] = i * 1

    pkt_size = osc_client.send(msg)
    print("packet_size sent:", pkt_size, "msg:", msg)

    time.sleep(1)
    i -= 1

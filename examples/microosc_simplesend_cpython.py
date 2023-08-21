# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: Unlicense

"""Demonstrate MicroOSC library in CPython"""

import time
import socket

import microosc


# test low-level functions
def test_low_level():
    """Test internals of microosc a little"""
    packet = bytearray(256)
    # data = bytearray(('b\x21' * 256).encode())
    # msg = microosc.OscMsg('/1/fader1', [1234,], ('i',))
    # msg = microosc.OscMsg('/1/fader1', [0.99,], ('f',))
    msg1 = microosc.OscMsg("/1/xy1", [ 0.99, 0.3, ], ( "f", "f", ) )  # fmt: skip

    print("msg1:", msg1)
    packet_size = microosc.create_osc_packet(msg1, packet)
    print("packet_size:", packet_size)
    msg2 = microosc.parse_osc_packet(packet, packet_size)
    print("msg2:", msg2)


test_low_level()

osc_client = microosc.OSCClient(socket, "224.0.0.1", 5000)
# osc_client = microosc.OSCClient(socket, '127.0.0.1', 5000)

msg = microosc.OscMsg( "/1/xy1", [0.99, 0.3, ], ("f", "f", ) )  # fmt: skip

i = 100
while True:
    msg.args[0] = i * 0.01  # move the value a bit

    pkt_size = osc_client.send(msg)
    print("packet_size sent:", pkt_size, "msg:", msg)

    time.sleep(1)
    i -= 1

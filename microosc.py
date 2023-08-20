# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: MIT
"""
`microosc`
================================================================================

Minimal OSC parser and server for CircuitPython and CPython


* Author(s): Tod Kurt

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies
  based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/todbot/CircuitPython_MicroOSC.git"


import sys
import time
import struct
from collections import namedtuple

impl = sys.implementation.name
debug = False

if impl == 'circuitpython':
    import wifi
    import socketpool
    import ipaddress
    socket = socketpool.SocketPool(wifi.radio)
    # these defines are not yet in CirPy socket, known to work for ESP32 native WiFI
    IPPROTO_IP = 0         # super secret from @jepler
    IP_MULTICAST_TTL = 5   # super secret from @jepler
else:
    import socket
    IPPROTO_IP = socket.IPPROTO_IP
    IP_MULTICAST_TTL = socket.IP_MULTICAST_TTL


OscMsg = namedtuple("OscMsg", ['addr','args'])
"""Objects returned by `parse_osc_packet()`"""

"""Simple example of a dispatch_map"""
default_dispatch_map = {
    '/' : lambda msg: print("default_map:",msg.addr, msg.args)
}


def parse_osc_packet(data, packet_size):
    """Parse OSC packets into OscMsg objects.
    :param bytearray data: a data buffer containing a binary OSC packet
    :param int datasize: the size of the OSC packet (may be smaller than len(data))

    OSC packets contain, in order:
    - a string that is the OSC Address (null-terminated), e.g. "/1/faderB"
    - a tag-type string starting with ',' and one or more 'f','i','s' types,
        (optional, null-terminated), e.g. ",ffi" indicates two float32s, one int32
    - zero or more OSC Arguments in binary form, depending on tag-type string
    - OSC packet size is always a multiple of 4
    """

    type_start = data.find(b',')
    type_end = type_start+4  # OSC parts are 4-byte aligned
    # TODO: check type_start is 4-byte aligned

    oscaddr = data[:type_start].decode().rstrip("\x00")
    osctypes = data[type_start+1:type_end].decode()

    if debug:
        print('oscaddr:',oscaddr, "osctypes:", osctypes,
              "data:", data[type_end:], packet_size-type_end, type_end, packet_size)

    args = []
    dpos = type_end
    for t in osctypes:
        if t == 'f':  # osc float32
            arg = struct.unpack(">f", data[dpos:dpos+4])
            args.append(arg[0])
            dpos += 4
        elif t == 'i': # osc int32
            arg = struct.unpack(">i", data[dpos:dpos+4])
            args.append(arg[0])
            dpos += 4
        elif t == 's': # osc string  TODO: find OSC emitter that sends string
            arg = data.decode()
            args.append(arg[0])
            dpos += len(arg)
        elif t == '\x00':  # null padding
            pass
        else:
            args.append("unknown type:"+t)

    return OscMsg(addr=oscaddr, args=args)


class OSCServer:
    """
    In OSC parlance, a "server" is a receiver of OSC messages, usually UDP packets.
    This OSC server is an OSC UDP receiver.

    :param str host: hostname or IP address to receive on,
                     can use multicast addresses like '224.0.0.1'
    :param int port: port to receive on
    :param dict dispatch_map: map of OSC Addresses to functions,
                     if no dispatch_map is specified, a default_map will be used
                     that prints out OSC messages
    """
    def __init__(self, host=None, port=None, dispatch_map=default_dispatch_map):
        self.host = host
        self.port = port
        self.dispatch_map = dispatch_map
        self._server_start()

    def _server_start(self, buf_size=256, timeout=0.001, ttl=2):
        """
        """
        self._buf = bytearray(buf_size)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        # TODO: check for IP address type? (multicast/unicast)
        self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(timeout)

    def poll(self):
        """
        Call this method inside your main loop to get the server to check for
        new incoming packets. When a packet comes in, it will be parsed and
        dispatched to your provided handler functions specified in your dispatch_map.
        """
        try:
            datasize, addr = self.sock.recvfrom_into(self._buf)
            msg = parse_osc_packet(self._buf, datasize)
            self.dispatch(msg)
        except OSError as ex:
            pass  # timeout

    def dispatch(self, msg):
        """:param OscMsg msg: message to be dispatched using dispatch_map"""
        for addr, func in self.dispatch_map.items():
            if msg.addr.startswith( addr ):
                func(msg)

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

To run this library you will need one of:

* CircuitPython board with native wifi support, like those based on ESP32-S2, ESP32-S3, etc.
* Desktop Python (CPython) computer

To send OSC messages, you will need an OSC UDP sender (aka "OSC client").
Some easy-to-use OSC clients are:

* `TouchOSC <https://hexler.net/touchosc>`_
* `OSCSend for Ableton Live <https://www.ableton.com/en/packs/connection-kit/>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads


**References:**

* `Open Sound Control Spec 1.0 <https://opensoundcontrol.stanford.edu/spec-1_0.html>`_

"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/todbot/CircuitPython_MicroOSC.git"


import sys
import struct
from collections import namedtuple

impl = sys.implementation.name
DEBUG = False

if impl == "circuitpython":
    # import socket
    # import socketpool
    # these defines are not yet in CirPy socket, known to work for ESP32 native WiFI
    IPPROTO_IP = 0  # super secret from @jepler
    IP_MULTICAST_TTL = 5  # super secret from @jepler
else:
    import socket

    IPPROTO_IP = socket.IPPROTO_IP
    IP_MULTICAST_TTL = socket.IP_MULTICAST_TTL


OscMsg = namedtuple("OscMsg", ["addr", "args"])
"""Objects returned by `parse_osc_packet()`"""

# fmt: off
"""Simple example of a dispatch_map"""
default_dispatch_map = {
    "/": lambda msg: print("default_map:", msg.addr, msg.args)
}
# fmt: on


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

    type_start = data.find(b",")
    type_end = type_start + 4  # OSC parts are 4-byte aligned
    # TODO: check type_start is 4-byte aligned

    oscaddr = data[:type_start].decode().rstrip("\x00")
    osctypes = data[type_start + 1 : type_end].decode()

    if DEBUG:
        print(
            "oscaddr:",
            oscaddr,
            "osctypes:",
            osctypes,
            "data:",
            data[type_end:],
            packet_size - type_end,
            type_end,
            packet_size,
        )

    args = []
    dpos = type_end
    for otype in osctypes:
        if otype == "f":  # osc float32
            arg = struct.unpack(">f", data[dpos : dpos + 4])
            args.append(arg[0])
            dpos += 4
        elif otype == "i":  # osc int32
            arg = struct.unpack(">i", data[dpos : dpos + 4])
            args.append(arg[0])
            dpos += 4
        elif otype == "s":  # osc string  TODO: find OSC emitter that sends string
            arg = data.decode()
            args.append(arg[0])
            dpos += len(arg)
        elif otype == "\x00":  # null padding
            pass
        else:
            args.append("unknown type:" + otype)

    return OscMsg(addr=oscaddr, args=args)


class OSCServer:
    """
    In OSC parlance, a "server" is a receiver of OSC messages, usually UDP packets.
    This OSC server is an OSC UDP receiver.
    :param socket: An object that is a source of sockets. This could be a `socketpool`
                     in CircuitPython or the `socket` module in CPython.
    :param str host: hostname or IP address to receive on,
                     can use multicast addresses like '224.0.0.1'
    :param int port: port to receive on
    :param dict dispatch_map: map of OSC Addresses to functions,
                     if no dispatch_map is specified, a default_map will be used
                     that prints out OSC messages
    """

    def __init__(self, socket_source, host, port, dispatch_map=None):
        self._socket_source = socket_source
        self.host = host
        self.port = port
        self.dispatch_map = dispatch_map or default_dispatch_map
        self._server_start()

    def _server_start(self, buf_size=256, timeout=0.001, ttl=2):
        """ """
        self._buf = bytearray(buf_size)
        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_DGRAM
        )  # UDP
        # TODO: check for IP address type? (multicast/unicast)
        self._sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
        self._sock.bind((self.host, self.port))
        self._sock.settimeout(timeout)

    def poll(self):
        """
        Call this method inside your main loop to get the server to check for
        new incoming packets. When a packet comes in, it will be parsed and
        dispatched to your provided handler functions specified in your dispatch_map.
        """
        try:
            # pylint: disable=unused-variable
            datasize, addr = self._sock.recvfrom_into(self._buf)
            msg = parse_osc_packet(self._buf, datasize)
            self._dispatch(msg)
        except OSError:
            pass  # timeout

    def _dispatch(self, msg):
        """:param OscMsg msg: message to be dispatched using dispatch_map"""
        for addr, func in self.dispatch_map.items():
            if msg.addr.startswith(addr):
                func(msg)

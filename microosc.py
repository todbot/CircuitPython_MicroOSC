# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
#
# SPDX-License-Identifier: MIT
"""
`microosc`
================================================================================

Minimal OSC parser, server, and client for CircuitPython and CPython


* Author(s): Tod Kurt

Implementation Notes
--------------------

This is a minimal OSC library.  It can parse and emit OSC packets with the
following OSC data types:

* floating point numbers ("float32")
* integer numbers ("int32")
* strings


**Hardware:**

To run this library you will need one of:

* CircuitPython board with native wifi support, like those based on ESP32-S2, ESP32-S3, etc.
* Desktop Python (CPython) computer

To send OSC messages, you will need an OSC UDP sender (aka "OSC client").
Some easy-to-use OSC clients are:

* `TouchOSC for Mac/Win/Linux/iOS/Android <https://hexler.net/touchosc>`_
* `OSCSend for Ableton Live <https://www.ableton.com/en/packs/connection-kit/>`_

To receive OSC messages, you will need an OSC UDP receiver (aka "OSC server").
Some easy-to-use OSC clients are:

* `Protokol for Mac/Win/Linux/iOS/Android <https://hexler.net/protokol>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

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
    # these defines are not yet in CirPy socket, known to work for ESP32 native WiFI
    IPPROTO_IP = 0  # super secret from @jepler
    IP_MULTICAST_TTL = 5  # super secret from @jepler
else:
    import socket

    IPPROTO_IP = socket.IPPROTO_IP
    IP_MULTICAST_TTL = socket.IP_MULTICAST_TTL


OscMsg = namedtuple("OscMsg", ["addr", "args", "types"])
"""Objects returned by `parse_osc_packet()`"""

# fmt: off
default_dispatch_map = {
    "/": lambda msg: print("default_map:", msg.addr, msg.args)
}
"""Simple example of a dispatch_map"""
# fmt: on


def read_string(data, pos):
    """Read padded string from a position, return string and new end pos"""
    str_end = data.index(b"\x00", pos)  # from pos find null
    str_len = str_end - pos
    padded_len = (str_len // 4 + 1) * 4  # account for variable null-padding
    return str(data[pos : pos + str_len], "ascii"), pos + padded_len


def pack_string(astr, data, pos):
    """Pack a string s into data bytearray at position pos, returns new end pos"""
    n = len(astr) + 1  # for the added extra \x00
    pos_end = pos + n
    data[pos:pos_end] = bytes(astr + "\x00", "ascii")
    if pad_needed := n % 4:
        extra = 4 - pad_needed
        data[pos_end : pos_end + extra] = bytes("\x00" * extra, "ascii")
        pos_end = pos_end + extra
    return pos_end


def parse_osc_packet(data, packet_size):  # pylint: disable=unused-variable
    """Parse OSC packets into OscMsg objects.

    OSC packets contain, in order

      - a string that is the OSC Address (null-terminated), e.g. "/1/faderB"
      - a tag-type string starting with ',' and one or more 'f', 'i', 's' types,
        (optional, null-terminated), e.g. ",ffi" indicates two float32s, one int32
      - zero or more OSC Arguments in binary form, depending on tag-type string

    OSC packet size is always a multiple of 4

    :param bytearray data: a data buffer containing a binary OSC packet
    :param int packet_size: the size of the OSC packet (may be smaller than len(data))
    """
    # examples of OSC packets
    # https://opensoundcontrol.stanford.edu/spec-1_0-examples.html
    # spec: https://opensoundcontrol.stanford.edu/spec-1_0.html#osc-packets

    dpos = 0
    oscaddr, dpos = read_string(data, dpos)
    osctypes, dpos = read_string(data, dpos)
    osctypes = osctypes[1:]  # first element is ',' separator

    # fmt: off
    if DEBUG:
        print("data:", data)
        print("oscaddr:", oscaddr, "osctypes:", osctypes)
    # fmt: on

    args = []
    types = []

    for otype in osctypes:
        if otype == "f":  # osc float32
            arg = struct.unpack(">f", data[dpos : dpos + 4])
            args.append(arg[0])
            types.append("f")
            dpos += 4
        elif otype == "i":  # osc int32
            arg = struct.unpack(">i", data[dpos : dpos + 4])
            args.append(arg[0])
            types.append("i")
            dpos += 4
        elif otype == "s":  # osc string  TODO: find OSC emitter that sends string
            arg, dpos = read_string(data, dpos)
            args.append(arg)
            types.append("s")
        elif otype == "\x00":  # null padding
            pass
        else:
            args.append("unknown type:" + otype)

    return OscMsg(addr=oscaddr, args=args, types=types)


def create_osc_packet(msg, data):
    """
    :param OscMsg msg: OscMsg to convert into an OSC Packet
    :param bytearray data: an empty data buffer to write OSC Packet into

    :return size of actual OSC Packet written into data buffer
    """
    if DEBUG:
        print("create_osc_packet:", msg)

    # create header of OSC addr and OSC types
    pos = pack_string(msg.addr, data, 0)
    pos = pack_string("," + "".join(msg.types), data, pos)

    # if there are OSC Arguments, march through them
    if len(msg.args) > 0:
        for oarg, otype in zip(msg.args, msg.types):
            if otype == "f":
                data[pos : pos + 4] = struct.pack(">f", float(oarg))
                pos += 4
            elif otype == "i":
                data[pos : pos + 4] = struct.pack(">i", int(oarg))
                pos += 4
            elif otype == "s":
                pos = pack_string(oarg, data, pos)

    return pos


class OSCServer:
    """
    In OSC parlance, a "server" is a receiver of OSC messages, usually UDP packets.
    This OSC server is an OSC UDP receiver.
    """

    def __init__(self, socket_source, host, port, dispatch_map=None):
        """
        Create an OSCServer and start it listening on a host/port.

        :param socket socket_source: An object that is a source of sockets.
          This could be a `socketpool` in CircuitPython or the `socket` module in CPython.
        :param str host: hostname or IP address to receive on,
          can use multicast addresses like '224.0.0.1'
        :param int port: port to receive on
        :param dict dispatch_map: map of OSC Addresses to functions,
          if no dispatch_map is specified, a default_map will be used that prints out OSC messages
        """
        self._socket_source = socket_source
        self.host = host
        self.port = port
        self.dispatch_map = dispatch_map or default_dispatch_map
        self._server_start()

    def _server_start(self, buf_size=128, timeout=0.001, ttl=2):
        """ """
        self._buf = bytearray(buf_size)
        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_DGRAM
        )  # UDP
        if self.host.startswith("224"):  # multicast
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


class OSCClient:
    """
    In OSC parlance, a "client" is a sender of OSC messages, usually UDP packets.
    This OSC client is an OSC UDP sender.
    """

    def __init__(self, socket_source, host, port, buf_size=128):
        """
        Create an OSCClient ready to send to a host/port.

        :param socket socket_source: An object that is a source of sockets.
          This could be a `socketpool` in CircuitPython or the `socket` module in CPython.
        :param str host: hostname or IP address to send to,
          can use multicast addresses like '224.0.0.1'
        :param int port: port to send to
        :param int buf_size: size of UDP buffer to use
        """
        self._socket_source = socket_source
        self.host = host
        self.port = port
        self._buf = bytearray(buf_size)
        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_DGRAM
        )
        if self.host.startswith("224"):  # multicast
            ttl = 2  # TODO: make this an arg?
            self._sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)

    def send(self, msg):
        """
        Send an OSC Message.

        :param OscMsg msg: the OSC Message to send
        :return int: return code from socket.sendto
        """

        pkt_size = create_osc_packet(msg, self._buf)
        return self._sock.sendto(self._buf[:pkt_size], (self.host, self.port))

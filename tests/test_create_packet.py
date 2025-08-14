# SPDX-FileCopyrightText: Copyright (c) 2024 Tod Kurt
# SPDX-License-Identifier: MIT

import pytest
import microosc


def test_two_ints():
    packet = bytearray(64)

    msg1 = microosc.OscMsg("/1/xy", [23, 45], ("i", "i"))
    packet_size = microosc.create_osc_packet(msg1, packet)
    msg2 = microosc.parse_osc_packet(packet, packet_size)

    assert str(msg1) == "OscMsg(addr='/1/xy', args=[23, 45], types=('i', 'i'))"
    assert packet_size == 20
    assert msg2.addr == msg1.addr
    assert msg2.args[0] == msg1.args[0]
    assert msg2.args[1] == msg1.args[1]


def test_two_floats():
    packet = bytearray(64)

    msg1 = microosc.OscMsg("/1/xy1", [0.99, 0.3], ("f", "f"))
    packet_size = microosc.create_osc_packet(msg1, packet)
    msg2 = microosc.parse_osc_packet(packet, packet_size)

    assert str(msg1) == "OscMsg(addr='/1/xy1', args=[0.99, 0.3], types=('f', 'f'))"
    assert packet_size == 20
    assert msg2.addr == msg1.addr
    assert msg2.args[0] == pytest.approx(msg1.args[0])
    assert msg2.args[1] == pytest.approx(msg1.args[1])


def test_string():
    packet1 = bytearray(64)
    packet2 = bytearray(64)

    msg1 = microosc.OscMsg("/1/message", ["hello there"], ("s",))
    packet1_size = microosc.create_osc_packet(msg1, packet1)

    msg2 = microosc.OscMsg("/1/message", ["hello there2"], ("s",))
    packet2_size = microosc.create_osc_packet(msg2, packet2)

    print("msg1", packet1_size, packet1, msg1)
    print("msg2", packet2_size, packet2, msg2)


if __name__ == "__main__":
    print("test_construction")

    packet0 = bytearray(64)
    msg1 = microosc.OscMsg("/1/xy", [23, 45], ("i", "i"))

    print("msg1.types:", msg1.types)
    packet0_size = microosc.create_osc_packet(msg1, packet0)

    print("packet0:", packet0, packet0_size)

    # packet1 = bytearray(64)
    # msg1 = microosc.OscMsg("/1/message", ["hello there"], ("s",))
    # packet1_size = microosc.create_osc_packet(msg1, packet1)

    test_string()

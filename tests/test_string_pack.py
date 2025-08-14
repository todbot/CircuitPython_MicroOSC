# SPDX-FileCopyrightText: Copyright (c) 2025 Tod Kurt
# SPDX-License-Identifier: MIT

import microosc

atests = ("hello", "hellothere", "hellotheretod", "hellothereA")

aresults = (
    b"____hello\x00\x00\x00____________________",
    b"____hellothere\x00\x00________________",
    b"____hellotheretod\x00\x00\x00____________",
    b"____hellothereA\x00________________",
)
aresult_lens = (8, 12, 16, 12)


def test_pack_string():
    pos_start = 4
    for i, a in enumerate(atests):
        data = bytearray(32)
        data[:] = [0x5F] * len(data)
        pos = microosc.pack_string(a, data, pos_start)
        assert data == aresults[i]
        assert (pos - pos_start) == aresult_lens[i]


if __name__ == "__main__":
    print("test_pack_string")
    pos_start = 4
    for i, a in enumerate(atests):
        data = bytearray(32)
        data[:] = [0x5F] * len(data)
        pos = microosc.pack_string(a, data, pos_start)
        plen = pos - pos_start
        print(i, a, data, aresults[i], data == aresults[i], plen == aresult_lens[i])

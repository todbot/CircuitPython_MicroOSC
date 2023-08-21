Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-microosc/badge/?version=latest
    :target: https://circuitpython-microosc.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/todbot/CircuitPython_MicroOSC/workflows/Build%20CI/badge.svg
    :target: https://github.com/todbot/CircuitPython_MicroOSC/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Minimal OSC parser, server, and client for CircuitPython and CPython


`Open Sound Control <https://opensoundcontrol.stanford.edu/>`_ is an efficient data transport
encoding/protocol for real-time performance messages for music or other similar endeavors.
The OSC byte encoding is designed to be semi-human readable and efficient enough for
UDP packet transmission.

OSC Messages are defined by an "OSC Address" (e.g. "/1/faderA") and optional "OSC Arguments",
one or more possible of several data types (e.g. float32 or int32). OSC doesn't pre-define
specific OSC Addresses, it is up the the sender and receiver to agree upon them.

This "MicroOSC" library is a minimal UDP receiver ("OSC Server") and parser of OSC packets.
The MicroOSC UDP receiver supports both unicast and multicast UDP on both CircuitPython and CPython.


Requirements
============

To run this library you will need one of:

* CircuitPython board with native ``wifi`` support, like those based on ESP32-S2, ESP32-S3, etc.
* Desktop Python (CPython) computer

To send OSC messages, you will need an OSC UDP sender (aka "OSC client").
Some easy-to-use OSC clients are:

* `TouchOSC <https://hexler.net/touchosc>`_
* `OSCSend for Ableton Live <https://www.ableton.com/en/packs/connection-kit/>`_

To receive OSC messages, you will need an OSC UDP receiver (aka "OSC server").
Some easy-to-use OSC clients are:

* `Protokol for Mac/Win/Linux/iOS/Android <https://hexler.net/protokol>`_

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-microosc/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-microosc

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-microosc

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-microosc

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install microosc

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import time, os, wifi, socketpool
    import microosc

    UDP_HOST = "224.0.0.1"  # multicast UDP
    UDP_PORT = 5000

    ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

    print("connecting to WiFi", ssid)
    wifi.radio.connect(ssid, password)

    socket_pool = socketpool.SocketPool(wifi.radio)

    def fader_handler(msg):
       """Used to handle 'fader' OscMsgs, printing it as a '*' text progress bar
       :param OscMsg msg: message with one required float32 value
       """
       print(msg.addr, "*" * int(20 * msg.args[0]))  # make a little bar chart

    dispatch_map = {
        "/": lambda msg: print("\t\tmsg:", msg.addr, msg.args),  # prints all messages
        "/1/fader": fader_handler,
        "/filter1": fader_handler,
    }

    osc_server = micro_osc.Server(socket_pool, UDP_HOST, UDP_PORT, dispatch_map)

    print("MicroOSC server started on ", UDP_HOST, UDP_PORT)

    last_time = time.monotonic()

    while True:

        osc_server.poll()

        if time.monotonic() - last_time > 1.0:
            last_time = time.monotonic()
            print(f"waiting {last_time:.2f}")


References
==========

* `Open Sound Control Spec 1.0 <https://opensoundcontrol.stanford.edu/spec-1_0.html>`_
* `OSC Message examples <https://opensoundcontrol.stanford.edu/spec-1_0-examples.html>`_
* `OSC info and tools <https://wiki.thingsandstuff.org/OSC>`_
* `TouchOSC apps for Mac/Win/Linux <https://hexler.net/touchosc>`_

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-microosc.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/todbot/CircuitPython_MicroOSC/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

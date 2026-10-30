#!/usr/bin/env python3
"""Dump raw 433 MHz pulses from an RFLink gateway (Arduino Mega, serial).

Stop any other program that holds the port (Domoticz, HA RFLink integration)
before running. No dependencies beyond the Python standard library (Linux).

    python3 rflink_sniff.py [seconds] [/dev/ttyACM0] > capture.txt
"""
import os
import select
import sys
import termios
import time

duration = float(sys.argv[1]) if len(sys.argv) > 1 else 60
port = sys.argv[2] if len(sys.argv) > 2 else '/dev/ttyACM0'

fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
attrs = termios.tcgetattr(fd)
attrs[0] = 0
attrs[1] = 0
attrs[3] = 0
attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
attrs[4] = attrs[5] = termios.B57600
termios.tcsetattr(fd, termios.TCSANOW, attrs)


def out(line):
    print(time.strftime('%H:%M:%S'), line, flush=True)


def send(cmd):
    os.write(fd, (cmd + '\r\n').encode())
    out('>> ' + cmd)


buf = b''
start = time.time()
debug_on = False
while time.time() - start < duration:
    # opening the port resets the Mega; give it time to boot
    if not debug_on and time.time() - start > 4:
        send('10;PING;')
        time.sleep(0.3)
        send('10;VERSION;')
        time.sleep(0.3)
        send('10;RFDEBUG=ON;')
        debug_on = True
    ready, _, _ = select.select([fd], [], [], 0.5)
    if ready:
        buf += os.read(fd, 4096)
        while b'\n' in buf:
            line, buf = buf.split(b'\n', 1)
            out(line.decode(errors='replace').rstrip())
send('10;RFDEBUG=OFF;')

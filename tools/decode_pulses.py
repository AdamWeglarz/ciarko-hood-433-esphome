#!/usr/bin/env python3
"""Decode RFLink RFDEBUG pulse lines into hood frames.

Splits each pulse train on sync pulses (> 1200 us), turns every HIGH/LOW pair
into a bit (long HIGH = 1, short HIGH = 0) and prints average pulse widths.

    python3 decode_pulses.py capture.txt
"""
import re
import sys

PULSES = re.compile(r'Pulses=(\d+);Pulses\(uSec\)=([\d,]+)')

for line in open(sys.argv[1]):
    m = PULSES.search(line)
    if not m or int(m.group(1)) < 60:
        continue
    pulses = list(map(int, m.group(2).split(',')))
    syncs = [(pulses[i], pulses[i + 1]) for i in range(len(pulses) - 1) if 1200 < pulses[i] < 3000]
    frames, cur = [], []
    for v in pulses:
        if v > 1200:
            frames.append(cur)
            cur = []
        else:
            cur.append(v)
    frames.append(cur)
    short = [v for v in pulses if v <= 350]
    long_ = [v for v in pulses if 350 < v <= 1200]
    print(f'{line[:8]} pulses={len(pulses)} long~{sum(long_) // max(1, len(long_))} '
          f'short~{sum(short) // max(1, len(short))} syncs={syncs[:2]}')
    for f in frames:
        if len(f) >= 60:
            bits = ''.join('1' if f[i] > f[i + 1] else '0' for i in range(0, len(f) - 1, 2))
            print(f'    {len(bits):2d} {bits}')

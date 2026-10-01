"""DIY-2: stream a path_gen.py CSV to a Helios USB laser DAC (ILDA output), the simplest galvo driver for a DIY build.
UNTESTED ON HARDWARE. Test with the trap laser OFF first.

Requires the Helios DAC SDK shared library (libHeliosDacAPI.so / HeliosLaserDAC.dll from the vendor's open-source
SDK). This script uses only its documented C calls through ctypes: OpenDevices, GetStatus, WriteFrame, CloseDevices.
X/Y are 12-bit (0..4095). Color channels drive the ILDA colour lines; use them for the illumination laser. The TRAP laser
must be hardware-interlocked and is not controlled from here.

Usage: python3 helios_stream.py path.csv --mm_per_full_scale 30 --pps 20000   (--pps must equal path_gen.py --rate)
"""
import argparse
import ctypes
import time

import numpy as np


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_uint16), ("y", ctypes.c_uint16), ("r", ctypes.c_uint8), ("g", ctypes.c_uint8),
                ("b", ctypes.c_uint8), ("i", ctypes.c_uint8)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--mm_per_full_scale", type=float, default=30.0)
    ap.add_argument("--pps", type=int, default=20000)
    ap.add_argument("--lib", default="./libHeliosDacAPI.so")
    ap.add_argument("--rgb", default="0,180,255", help="illumination colour, e.g. Iron-Man cyan")
    a = ap.parse_args()
    d = np.loadtxt(a.csv, delimiter=",", skiprows=1)
    if len(d) > 4095:   # Helios max frame size (vendor spec: 4095 points)
        raise SystemExit(f"{len(d)} points > 4095 per Helios frame: use a smaller --rate in path_gen.py (and the same --pps here)")
    xy = np.clip(np.round(2048 + d[:, :2] / a.mm_per_full_scale * 4095), 0, 4095).astype(int)
    inten = d[:, 2] if d.shape[1] > 2 else np.ones(len(d))
    r, g, b = (int(c) for c in a.rgb.split(","))
    frame = (Point * len(xy))(*[Point(int(x), int(y), int(r * k), int(g * k), int(b * k), int(255 * k))
                                for (x, y), k in zip(xy, inten)])
    lib = ctypes.cdll.LoadLibrary(a.lib)
    n = lib.OpenDevices()
    if n < 1:
        raise SystemExit("no Helios DAC found")
    try:
        while True:
            while lib.GetStatus(0) != 1:
                time.sleep(0.0005)
            lib.WriteFrame(0, a.pps, 0, ctypes.byref(frame), len(xy))
    except KeyboardInterrupt:
        pass
    finally:
        lib.CloseDevices()


if __name__ == "__main__":
    main()

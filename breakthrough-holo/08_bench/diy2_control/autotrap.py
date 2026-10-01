"""DIY-2a automatic trap tester: capture probability and hold time against laser power (BYU JoVE-style rig, ~200+ trials/h).

Each trial:
  1. the laser is set to power P;
  2. a solenoid taps the particle reservoir above the focus;
  3. the camera watches a small region around the trap point. A bright spot that stays there longer than --min_hold_s
     counts as a capture; a particle falling through is a transient and does not count;
  4. hold time is measured until the spot disappears or --max_hold_s passes;
  5. the laser goes off for --reset_s, so a held particle drops out before the next trial.

Output: one CSV row per trial, and a summary per power (capture probability with a Wilson 95 % interval, median hold).
This data tests predictions P27, P28 and P30 (07_mote_route/PREDICTIONS.md, Addendum B).

SAFETY: this program is NOT a safety device. The hardware interlock (ELECTRONICS.md §1) must cut the laser driver's power
whenever the lid opens. The program also refuses to run if the rig reports its interlock open, never exceeds --max_mW,
and switches the laser off on exit or error.

Hardware (`autotrap_esp32/autotrap_esp32.ino`) speaks a line protocol over USB serial:
  "P <0-255>"  laser analog power code       "L <0|1>"  laser enable (TTL)
  "T <ms>"     tapper pulse                  "I?"       interlock state -> "I 1" (closed, safe) or "I 0"
Camera: any OpenCV camera (--camera 0) or a Raspberry Pi camera via picamera2 (--camera pi).

Usage:
  python3 autotrap.py --selftest
  python3 autotrap.py --port /dev/ttyUSB0 --camera 0 --trap_xy 320 240 --powers 10 15 20 30 --trials 40 \
      --power_cal cal.csv --max_mW 60 --out run1.csv
(power_cal.csv: two columns "code,mW" measured with the thermal power meter at the trap plane.)
"""
import argparse
import csv
import math
import time

import numpy as np


# ------------------------------------------------------------------------------------------------------------ hardware
class SerialRig:
    def __init__(self, port, baud=115200):
        import serial  # pyserial, imported only when real hardware is used
        self.s = serial.Serial(port, baud, timeout=0.5)
        time.sleep(2.0)                                   # ESP32 resets on connect

    def _cmd(self, line):
        self.s.write((line + "\n").encode())
        return self.s.readline().decode().strip()

    def interlock_ok(self):
        return self._cmd("I?") == "I 1"

    def set_code(self, code):
        self._cmd(f"P {int(code)}")

    def laser(self, on):
        self._cmd(f"L {1 if on else 0}")

    def tap(self, ms):
        self._cmd(f"T {int(ms)}")

    def close(self):
        self.laser(False)
        self.set_code(0)
        self.s.close()


class Camera:
    def __init__(self, which):
        if which == "pi":
            from picamera2 import Picamera2
            self.pi = Picamera2()
            self.pi.configure(self.pi.create_video_configuration(main={"format": "YUV420"}))
            self.pi.start()
            self.grab = lambda: self.pi.capture_array()[: self.pi.camera_config["main"]["size"][1]].astype(float)
        else:
            import cv2
            self.cap = cv2.VideoCapture(int(which))
            self.grab = self._grab_cv

    def _grab_cv(self):
        ok, f = self.cap.read()
        if not ok:
            raise RuntimeError("camera read failed")
        return f.mean(axis=2) if f.ndim == 3 else f.astype(float)


# ------------------------------------------------------------------------------------------------------------ analysis
class Detector:
    """Bright-spot detector in a disc of radius r_px around the trap point, against a background learned with the laser
    on and no particle. Threshold: background + k sigma, per pixel (robust to laser glints and the lit trap volume)."""

    def __init__(self, trap_xy, r_px=12, k=6.0):
        self.x0, self.y0 = trap_xy
        self.r = r_px
        self.k = k
        self.mask = None

    def learn(self, frames):
        st = np.stack(frames)
        self.bg = np.median(st, axis=0)
        self.sig = np.maximum(1.4826 * np.median(np.abs(st - self.bg), axis=0), 1.0)
        yy, xx = np.mgrid[: st.shape[1], : st.shape[2]]
        self.mask = (xx - self.x0) ** 2 + (yy - self.y0) ** 2 <= self.r ** 2

    def present(self, frame):
        z = (frame - self.bg) / self.sig
        return bool((z[self.mask] > self.k).sum() >= 2)


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def power_to_code(cal, mW):
    codes, mws = cal
    if mW > mws.max():
        raise ValueError(f"{mW} mW is beyond the calibrated range ({mws.max():.1f} mW)")
    return int(round(np.interp(mW, mws, codes)))


# ------------------------------------------------------------------------------------------------------------- trials
def run_trial(rig, cam, det, code, a, clock=time.monotonic):
    """One tap-and-watch trial. Every second it polls the interlock: this is also the keepalive that stops the
    firmware's 5 s watchdog from switching the laser off during long holds."""
    last_poll = [clock()]

    def poll():
        if clock() - last_poll[0] >= 1.0:
            last_poll[0] = clock()
            if not rig.interlock_ok():
                rig.laser(False)
                raise SystemExit("interlock opened during a trial: stopped")

    rig.set_code(code)
    rig.laser(True)
    rig.tap(a.tap_ms)
    t0 = clock()
    first_seen, held_from = None, None
    while clock() - t0 < a.capture_window_s:              # look for a spot that persists for min_hold_s
        poll()
        if det.present(cam.grab()):
            first_seen = first_seen if first_seen is not None else clock()
            if clock() - first_seen >= a.min_hold_s:
                held_from = first_seen
                break
        else:
            first_seen = None
    hold = 0.0
    if held_from is not None:                             # measure the hold, tolerating a few missed frames
        misses = 0
        while clock() - held_from < a.max_hold_s:
            poll()
            if det.present(cam.grab()):
                misses = 0
            else:
                misses += 1
                if misses >= a.miss_frames:
                    break
        hold = clock() - held_from
    rig.laser(False)
    t1 = clock()
    while clock() - t1 < a.reset_s:                       # let the particle fall out
        cam.grab()
    return held_from is not None, hold


def run(rig, cam, a, cal, clock=time.monotonic, log=print):
    if not rig.interlock_ok():
        raise SystemExit("interlock open: close the lid and press RESET before running")
    for p in a.powers:
        if p > a.max_mW:
            raise SystemExit(f"requested {p} mW exceeds --max_mW {a.max_mW}")
    det = Detector(a.trap_xy, a.roi_px, a.k_sigma)
    rows, summary = [], []
    try:
        rig.set_code(power_to_code(cal, a.powers[0]))
        rig.laser(True)
        det.learn([cam.grab() for _ in range(a.bg_frames)])
        rig.laser(False)
        for p in a.powers:
            code = power_to_code(cal, p)
            got = []
            for i in range(a.trials):
                if not rig.interlock_ok():
                    raise SystemExit("interlock opened during the run: stopped")
                cap, hold = run_trial(rig, cam, det, code, a, clock)
                rows.append(dict(power_mW=p, trial=i, captured=int(cap), hold_s=round(hold, 3)))
                got.append((cap, hold))
            k = sum(c for c, _ in got)
            pr, lo, hi = wilson(k, len(got))
            holds = [h for c, h in got if c]
            summary.append(dict(power_mW=p, n=len(got), captured=k, p=pr, p_lo=lo, p_hi=hi,
                                median_hold_s=float(np.median(holds)) if holds else 0.0,
                                censored=sum(h >= a.max_hold_s - 1e-6 for h in holds)))
            s = summary[-1]
            log(f"{p:6.1f} mW: capture {k}/{len(got)} = {pr:.2f} [{lo:.2f}, {hi:.2f}]  median hold "
                f"{s['median_hold_s']:.1f} s ({s['censored']} reached the {a.max_hold_s:.0f} s cap)")
    finally:
        rig.laser(False)
        rig.set_code(0)
    return rows, summary


# ------------------------------------------------------------------------------------------------------------ selftest
class SimWorld:
    """Synthetic rig + camera on a simulated clock: capture probability is logistic in power, holds are exponential,
    and uncaptured particles fall through the trap region as short transients (which must not count)."""

    def __init__(self, seed=1, fps=100.0, shape=(40, 40), xy=(20, 20)):
        self.rng = np.random.default_rng(seed)
        self.t, self.dt = 0.0, 1 / fps
        self.shape, self.xy = shape, xy
        self.code, self.on, self.state = 0, False, None
        self.p50, self.slope, self.tau = 18.0, 0.25, 3.0     # mW, 1/mW, s
        self.truth = []

    def clock(self):
        return self.t

    # rig interface
    def interlock_ok(self):
        return True

    def set_code(self, c):
        self.code = c

    def laser(self, on):
        self.on = on
        if not on and self.state and self.state[0] == "held":
            self.state = None

    def tap(self, ms):
        mW = self.code / 4.0                                   # synthetic calibration: 4 codes per mW
        pc = 1 / (1 + math.exp(-self.slope * (mW - self.p50)))
        cap = self.rng.random() < pc
        arrive = self.t + 0.05 + 0.05 * self.rng.random()
        hold = self.rng.exponential(self.tau) if cap else 0.0
        self.state = ("held", arrive, arrive + hold) if cap else ("fall", arrive, arrive + 0.02)
        self.truth.append((mW, cap, hold))

    # camera interface
    def grab(self):
        self.t += self.dt
        f = 20 + 3 * self.rng.standard_normal(self.shape)
        if self.on:
            f += 15                                            # the lit trap volume (learned into the background)
        if self.state and self.state[1] <= self.t <= self.state[2] and self.on:
            x, y = self.xy
            f[y - 1:y + 2, x - 1:x + 2] += 120
        return f


def selftest():
    ok = True
    print("autotrap self-test (simulated rig, camera and clock)")
    # 1. detector: a falling transient (4 frames) must not be counted; a held particle must
    w = SimWorld(seed=3)
    a = argparse.Namespace(trap_xy=(20, 20), roi_px=8, k_sigma=6.0, bg_frames=60, tap_ms=30, capture_window_s=1.0,
                           min_hold_s=0.3, max_hold_s=10.0, miss_frames=5, reset_s=0.3, trials=150,
                           powers=[10.0, 18.0, 26.0], max_mW=60.0)
    cal = (np.array([0, 240.0]), np.array([0, 60.0]))
    rows, summ = run(w, w, a, cal, clock=w.clock, log=lambda *_: None)
    truth = np.array([(m, c, h) for m, c, h in w.truth])
    for s in summ:
        sel = truth[:, 0] == s["power_mW"]
        # a capture shorter than min_hold_s is indistinguishable from a fall-through, by design
        p_true = math.exp(-a.min_hold_s / w.tau) / (1 + math.exp(-w.slope * (s["power_mW"] - w.p50)))
        sig = math.sqrt(p_true * (1 - p_true) / s["n"])
        good = abs(s["p"] - p_true) <= 3 * sig                # binomial sampling: a 3-sigma check, not a 95 % one
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'} {s['power_mW']:4.0f} mW: capture {s['p']:.3f} "
              f"[{s['p_lo']:.3f}, {s['p_hi']:.3f}] vs true {p_true:.3f} ({(s['p'] - p_true) / sig:+.1f} sigma)")
        # every simulated capture detected, no falls counted
        det_caps = sum(r["captured"] for r in rows if r["power_mW"] == s["power_mW"])
        # holds within two frames of min_hold_s are borderline (frame timing), so the detected count must lie between
        # the captures that are surely long enough and those that are possibly long enough
        caps = truth[sel][truth[sel, 1] == 1, 2]
        n_sure, n_poss = int((caps >= a.min_hold_s + 2 * w.dt).sum()), int((caps >= a.min_hold_s - 2 * w.dt).sum())
        good = n_sure <= det_caps <= n_poss
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'}   detected captures {det_caps} within [{n_sure}, {n_poss}] true captures "
              f"held ~>= {a.min_hold_s} s (falling transients rejected)")
    holds = np.array([r["hold_s"] for r in rows if r["captured"]])
    true_h = np.minimum(truth[(truth[:, 1] == 1) & (truth[:, 2] >= a.min_hold_s), 2], a.max_hold_s)
    good = abs(np.median(holds) - np.median(true_h)) < 0.05 * np.median(true_h) + 0.1
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'} median hold {np.median(holds):.2f} s vs true {np.median(true_h):.2f} s "
          f"(capped at {a.max_hold_s:.0f} s)")
    # 2. Wilson interval sanity
    p, lo, hi = wilson(0, 20)
    good = p == 0 and lo == 0 and 0.15 < hi < 0.18
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'} Wilson 0/20 upper bound {hi:.3f} (expected ~0.161)")
    # 3. safety refusals
    for name, fn in (("power above --max_mW", lambda: run(w, w, argparse.Namespace(**{**vars(a), "powers": [80.0]}),
                                                           cal, clock=w.clock, log=lambda *_: None)),
                     ("power beyond calibration", lambda: power_to_code(cal, 70.0))):
        try:
            fn()
            good = False
        except (SystemExit, ValueError):
            good = True
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'} refuses {name}")
    good = w.on is False
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'} laser left off after the run")
    # 4. interlock opening mid-trial: the run stops and the laser is off
    w2 = SimWorld(seed=9)
    w2.tau = 1e9                                            # every captured particle would be held to the cap
    w2.p50 = -100.0                                         # always captured
    t_open = 3.0
    w2.interlock_ok = lambda: w2.t < t_open
    try:
        run(w2, w2, argparse.Namespace(**{**vars(a), "powers": [20.0], "trials": 5}), cal, clock=w2.clock,
            log=lambda *_: None)
        good = False
    except SystemExit:
        good = (w2.on is False) and (t_open <= w2.t <= t_open + 1.1)
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'} interlock opened at {t_open:.0f} s: run stopped at {w2.t:.2f} s, laser off")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--port")
    ap.add_argument("--camera", default="0")
    ap.add_argument("--trap_xy", type=int, nargs=2)
    ap.add_argument("--roi_px", type=int, default=12)
    ap.add_argument("--k_sigma", type=float, default=6.0)
    ap.add_argument("--bg_frames", type=int, default=60)
    ap.add_argument("--powers", type=float, nargs="+")
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--max_mW", type=float, default=60.0, help="software cap; the hardware interlock is still required")
    ap.add_argument("--power_cal", help="CSV 'code,mW' measured with the thermal meter at the trap plane")
    ap.add_argument("--tap_ms", type=int, default=30)
    ap.add_argument("--capture_window_s", type=float, default=1.0)
    ap.add_argument("--min_hold_s", type=float, default=0.3)
    ap.add_argument("--max_hold_s", type=float, default=60.0)
    ap.add_argument("--miss_frames", type=int, default=5)
    ap.add_argument("--reset_s", type=float, default=1.0)
    ap.add_argument("--out", default="autotrap.csv")
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(0 if selftest() else 1)
    if not (a.port and a.trap_xy and a.powers and a.power_cal):
        ap.error("--port, --trap_xy, --powers and --power_cal are required")
    c = np.loadtxt(a.power_cal, delimiter=",", skiprows=1)
    cal = (c[:, 0], c[:, 1])
    rig, cam = SerialRig(a.port), Camera(a.camera)
    try:
        rows, summary = run(rig, cam, a, cal)
    finally:
        rig.close()
    with open(a.out, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    with open(a.out.replace(".csv", "_summary.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(summary[0]))
        wr.writeheader()
        wr.writerows(summary)


if __name__ == "__main__":
    main()

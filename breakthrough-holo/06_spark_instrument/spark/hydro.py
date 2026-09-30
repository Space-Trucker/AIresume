"""SPARK hydrodynamics: 1D Lagrangian (spherical or planar) blast + conduction + radiation.

Phase 1 (compressible): von Neumann-Richtmyer staggered scheme with quadratic+linear artificial
viscosity, predictor-corrector PdV work, operator-split implicit conduction (backward Euler on T with
linearised c_v) and radiative losses with per-band escape factors.
Phase 2 (isobaric, low Mach): once the blast has passed the acoustic probe and the kernel pressure is
within 2 % of ambient, the kernel is evolved at constant P0 (enthalpy equation, implicit conduction,
radiation) with volumes from the equilibrium rho(T, P0). This is exact to O(Mach^2) and lets the
conduction/radiation cooling phase (us-ms) run with large time steps.
Records: energy budget, band-resolved radiated energy, lumen-seconds, actinic J, VUV/EUV photon counts,
acoustic energy flux and waveform at a probe radius, shock trajectory, Lagrangian T/P histories.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.linalg import solve_banded

from eos import P0

RAD_BANDS = ["euv", "vuv", "uvc", "uvb", "uva", "vis", "ir"]
KAPPA_PROBE = {"euv": 0, "vuv": 1, "uvc": 2, "uvb": 2, "uva": 2, "vis": 3, "ir": 4}


def make_grid(r0, R_out, n_core=48, core_extent=3.0, growth=1.03, dr_max=None):
    rc = core_extent * r0
    r = list(np.linspace(0.0, rc, n_core + 1))
    dr = rc / n_core
    dr_max = dr_max or R_out / 200
    while r[-1] < R_out:
        dr = min(dr * growth, dr_max)
        r.append(r[-1] + dr)
    return np.array(r)


class Spark:
    def __init__(self, eos, E_abs, r0, rad=None, geometry="spherical", R_out=None, n_core=48, growth=1.03,
                 kappa_fn=None, kappa_mult=1.0, cfl=0.3, rho_amb=None, e_amb=None, r_probe=None,
                 profile="gauss", record_every=40, dr_max=None, isobaric_switch=True, shell_R=None,
                 pulses=None):
        self.eos, self.rad, self.geo = eos, rad, geometry
        self.kfn, self.kmult, self.cfl = kappa_fn, kappa_mult, cfl
        self.rho_amb = rho_amb if rho_amb is not None else eos.rho0
        self.e_amb = e_amb if e_amb is not None else float(eos.e_of(np.array([self.rho_amb]), np.array([300.0]))[0])
        self.rc = (E_abs / P0) ** (1 / 3) if geometry == "spherical" else E_abs / P0
        self.R_out = R_out or 40 * self.rc
        self.r_probe = r_probe or 8 * self.rc
        self.r = make_grid(r0, self.R_out, n_core, growth=growth, dr_max=dr_max or self.rc / 25)
        N = len(self.r) - 1
        self.N = N
        V = self._vol(self.r)
        self.m = self.rho_amb * V
        self.e = np.full(N, self.e_amb)
        rcell = 0.5 * (self.r[1:] + self.r[:-1])
        self.pulses = []
        E_first = E_abs
        if pulses:
            # extra pulses: list of (t, E, r_dep); energies are part of E_abs; deposited into the
            # Lagrangian cells that started within r_dep (the original kernel material)
            for (tp, Ep, rp) in pulses:
                wp = np.exp(-(rcell / rp) ** 2) * V
                self.pulses.append([tp, Ep, wp / wp.sum()])
            E_first = E_abs - sum(p[1] for p in pulses)
        if E_first > 0:
            if profile == "gauss":
                w = np.exp(-(rcell / r0) ** 2) * V
            elif profile == "shell":
                Rs = shell_R
                w = np.exp(-((rcell - Rs) / (0.2 * Rs)) ** 2) * V
            else:
                w = (rcell <= r0) * V
            w = w / w.sum()
            self.e += E_first * w / self.m
        self.u = np.zeros(N + 1)
        self.V_init = V.copy()
        self.P_ext = float(np.atleast_1d(eos.P(np.array([self.rho_amb]), np.array([self.e_amb])))[0])
        self.t = 0.0
        self.E_abs = E_abs
        self.E0 = float((self.m * self.e).sum())
        self.W_out = 0.0                       # work done on the outside (P0 dV at outer boundary)
        self.E_rad = {b: 0.0 for b in RAD_BANDS}
        self.lm_s = self.act_J = self.ph_o2 = self.ph_ion = 0.0
        self.probe_j = int(np.argmin(np.abs(self.r - self.r_probe)))
        self.E_ac = 0.0
        self.probe_t, self.probe_p = [], []
        self.shock = []
        self.hist_t, self.hist_T, self.hist_P = [], [], []
        self.record_every = record_every
        self.phase = 1
        self.isobaric_switch = isobaric_switch
        self.step = 0
        self.dt = 1e-13

    @classmethod
    def from_arrays(cls, eos, r, rho, e, geometry="planar", P_ext=None, **kw):
        obj = cls.__new__(cls)
        obj.eos, obj.rad, obj.geo = eos, kw.get("rad"), geometry
        obj.kfn, obj.kmult, obj.cfl = kw.get("kappa_fn"), kw.get("kappa_mult", 1.0), kw.get("cfl", 0.3)
        obj.r = np.asarray(r, float)
        obj.N = len(r) - 1
        V = obj._vol(obj.r)
        obj.m = np.asarray(rho, float) * V
        obj.e = np.asarray(e, float).copy()
        obj.u = np.zeros(obj.N + 1)
        obj.rho_amb, obj.e_amb = float(rho[-1]), float(e[-1])
        obj.P_ext = P_ext if P_ext is not None else float(np.atleast_1d(eos.P(np.array([rho[-1]]), np.array([e[-1]])))[0])
        obj.t, obj.E_abs, obj.W_out = 0.0, 0.0, 0.0
        obj.E0 = float((obj.m * obj.e).sum())
        obj.E_rad = {b: 0.0 for b in RAD_BANDS}
        obj.lm_s = obj.act_J = obj.ph_o2 = obj.ph_ion = 0.0
        obj.r_probe = kw.get("r_probe", obj.r[-1] / 2)
        obj.probe_j = int(np.argmin(np.abs(obj.r - obj.r_probe)))
        obj.E_ac = 0.0
        obj.probe_t, obj.probe_p, obj.shock = [], [], []
        obj.hist_t, obj.hist_T, obj.hist_P = [], [], []
        obj.record_every, obj.phase, obj.isobaric_switch = 10 ** 9, 1, False
        obj.step, obj.dt = 0, 1e-13
        obj.rc = obj.r[-1]
        return obj

    def total_energy(self):
        V = self._vol(self.r)
        un = 0.5 * (self.u[1:] + self.u[:-1])
        ke = 0.5 * self.m * un ** 2
        return float((self.m * self.e).sum() + ke.sum())

    # ---------------------------------------------------------------- geometry
    def _vol(self, r):
        if self.geo == "spherical":
            return 4.0 / 3.0 * math.pi * (r[1:] ** 3 - r[:-1] ** 3)
        return r[1:] - r[:-1]

    def _area(self, r):
        return 4 * math.pi * r * r if self.geo == "spherical" else np.ones_like(r)

    # ---------------------------------------------------------------- physics pieces
    def _conduction(self, T, rho, dt, isobaric=False):
        if self.kfn is None:
            return np.zeros_like(T)
        rcell = 0.5 * (self.r[1:] + self.r[:-1])
        kap = self.kfn(T, self.kmult)
        kf = 2 * kap[1:] * kap[:-1] / (kap[1:] + kap[:-1])            # harmonic mean at interior faces
        G = self._area(self.r[1:-1]) * kf / (rcell[1:] - rcell[:-1])  # W/K
        dT = np.maximum(0.02 * T, 20.0)
        if isobaric:
            cap = (self.eos.iso_hT(T + dT) - self.eos.iso_hT(T)) / dT
        else:
            cap = (self.eos.e_of(rho, T + dT) - self.eos.e_of(rho, T)) / dT
        cap = np.maximum(cap, 500.0)
        C = self.m * cap / dt
        N = len(T)
        ab = np.zeros((3, N))
        ab[1] = C
        ab[1, :-1] += G
        ab[1, 1:] += G
        ab[0, 1:] = -G
        ab[2, :-1] = -G
        Tn = solve_banded((1, 1), ab, C * T)
        flux = np.zeros(N + 1)
        flux[1:-1] = G * (Tn[1:] - Tn[:-1])                          # W, positive = inward heat flow
        dE = (flux[1:] - flux[:-1]) * dt                              # J gained per cell
        return dE

    def _radiation(self, T, rho, V, dt):
        if self.rad is None:
            return np.zeros_like(T)
        hot = T > 1500.0
        if not hot.any():
            return np.zeros_like(T)
        g = self.rad.get(rho[hot], T[hot])
        dr = (self.r[1:] - self.r[:-1])[hot]
        tau = (g["kappa"] * dr[:, None]).sum(0)                       # radial optical depth per probe
        beta = np.where(tau > 1e-6, -np.expm1(-tau) / np.maximum(tau, 1e-30), 1.0)
        loss = np.zeros(hot.sum())
        Vh = V[hot]
        for b in RAD_BANDS:
            p = g[b] * beta[KAPPA_PROBE[b]] * Vh
            loss += p
            self.E_rad[b] += float(p.sum()) * dt
        bv, bu = beta[3], beta[2]
        self.lm_s += float((g["lm"] * Vh).sum()) * bv * dt
        self.act_J += float((g["act"] * Vh).sum()) * bu * dt
        self.ph_o2 += float((g["ph_o2"] * Vh).sum()) * beta[1] * dt
        self.ph_ion += float((g["ph_ion"] * Vh).sum()) * beta[0] * dt
        out = np.zeros_like(T)
        out[hot] = loss * dt
        return out

    # ---------------------------------------------------------------- phase 1
    def step_compressible(self):
        for p in self.pulses:
            if p[1] > 0 and self.t >= p[0]:
                self.e = self.e + p[1] * p[2] / self.m
                p[1] = 0.0
        r, u, m, e = self.r, self.u, self.m, self.e
        V = self._vol(r)
        rho = m / V
        T, P, cs = self.eos.state(rho, e)
        du = u[1:] - u[:-1]
        q = np.where(du < 0, rho * (2.0 * du * du + 0.25 * cs * np.abs(du)), 0.0)
        dr = r[1:] - r[:-1]
        dt = self.cfl * float(np.min(dr / (cs + np.abs(du) + 1e-12)))
        dt = min(dt, 1.2 * self.dt)
        A = self._area(r)
        Pq = P + q
        a = np.zeros_like(u)
        mn = 0.5 * (m[1:] + m[:-1])
        a[1:-1] = -A[1:-1] * (Pq[1:] - Pq[:-1]) / mn
        a[-1] = -A[-1] * (self.P_ext - Pq[-1]) / (0.5 * m[-1])
        un = u + a * dt
        un[0] = 0.0
        rn = r + un * dt
        Vn = self._vol(rn)
        dV = Vn - V
        e_pred = e - Pq * dV / m
        P_pred = self.eos.P(m / Vn, e_pred)
        en = e - (0.5 * (P + P_pred) + q) * dV / m
        self.W_out += self.P_ext * float(Vn.sum() - V.sum())
        self.r, self.u, self.e = rn, un, en
        rho_n = m / Vn
        Tn = self.eos.T(rho_n, en)
        dEc = self._conduction(Tn, rho_n, dt)
        dEr = self._radiation(Tn, rho_n, Vn, dt)
        self.e = self.e + (dEc - dEr) / m
        self.t += dt
        self.dt = dt
        # probe: acoustic energy flux through the probe sphere
        j = self.probe_j
        pj = 0.5 * (P[j - 1] + P[j]) - P0
        self.E_ac += A[j] * pj * un[j] * dt
        if self.step % 4 == 0:
            self.probe_t.append(self.t)
            self.probe_p.append(pj)
        # shock position: max compression of cells outside kernel
        k = int(np.argmax(rho_n / self.rho_amb * (rho_n > self.rho_amb)))
        self.shock.append((self.t, 0.5 * (rn[k] + rn[k + 1]), float(P[k])))
        if self.step % self.record_every == 0:
            self._record(Tn, self.eos.P(rho_n, self.e))
        self.step += 1
        return T

    def _record(self, T, P):
        self.hist_t.append(self.t)
        self.hist_T.append(T.astype(np.float32).copy())
        self.hist_P.append(np.asarray(P, np.float32).copy())

    def ready_for_isobaric(self):
        if not self.isobaric_switch or any(p[1] > 0 for p in getattr(self, "pulses", [])):
            return False
        rho = self.m / self._vol(self.r)
        T, P, _ = self.eos.state(rho, self.e)
        shock_r = self.shock[-1][1] if self.shock else 0.0
        kernel = T > 400.0
        if not kernel.any():
            return shock_r > 1.3 * self.r_probe
        pk = np.abs(P[kernel] / P0 - 1).max()
        return (shock_r > 1.3 * self.r_probe) and pk < 0.02 and np.abs(self.u).max() < 5.0

    # ---------------------------------------------------------------- phase 2
    def to_isobaric(self):
        rho = self.m / self._vol(self.r)
        T = self.eos.T(rho, self.e)
        self.Tiso = T
        # energy bookkeeping: convert e to h at P0 (difference = P dV work done by kernel on outside,
        # already accounted as acoustic/residual); record the internal-energy excess at the switch
        self.E_switch_internal = float((self.m * (self.e - self.e_amb)).sum())
        V = self._vol(self.r)
        rcell = 0.5 * (self.r[1:] + self.r[:-1])
        inside = rcell < self.r_probe
        un = 0.5 * (self.u[1:] + self.u[:-1])
        self.E_heat_kernel = float((self.m[inside] * (self.e[inside] - self.e_amb)).sum()
                                   + (0.5 * self.m[inside] * un[inside] ** 2).sum()
                                   + self.P_ext * (V[inside].sum() - self.V_init[inside].sum()))
        hot = T > 400.0
        self.dV_hot = float(V[hot].sum() - self.V_init[hot].sum())
        self.dV_inside = float(V[inside].sum() - self.V_init[inside].sum())
        self.E_rad_at_switch = sum(self.E_rad.values())
        self.t_switch = self.t
        self.phase = 2

    def step_isobaric(self, dt):
        T = self.Tiso
        rho = self.eos.iso_rho(T)
        V = self.m / rho
        self.r = np.concatenate([[0.0], np.cbrt(np.cumsum(V) * 3 / (4 * math.pi))]) if self.geo == "spherical" \
            else np.concatenate([[0.0], np.cumsum(V)])
        h0 = self.eos.iso_hT(T)
        dEc = self._conduction(T, rho, dt, isobaric=True)
        dEr = self._radiation(T, rho, V, dt)
        h1 = h0 + (dEc - dEr) / self.m
        self.Tiso = np.maximum(self.eos.iso_T_of_h(h1), 250.0)
        self.t += dt
        if self.step % max(1, self.record_every // 8) == 0:
            self._record(self.Tiso, np.full_like(self.Tiso, P0))
        self.step += 1

    # ---------------------------------------------------------------- driver
    def run(self, t_end=2e-3, T_stop=1200.0, max_steps=3_000_000, verbose=False):
        while self.t < t_end and self.step < max_steps:
            if self.phase == 1:
                T = self.step_compressible()
                if self.step % 200 == 0 and self.ready_for_isobaric():
                    self.to_isobaric()
            else:
                Tmax = float(self.Tiso.max())
                if Tmax < T_stop:
                    break
                # step limited by relative change of hottest cell; implicit conduction is stable
                dt = self.dt_iso if hasattr(self, "dt_iso") else 1e-9
                T_before = self.Tiso.copy()
                self.step_isobaric(dt)
                rel = float(np.max(np.abs(self.Tiso - T_before) / T_before))
                self.dt_iso = dt * (1.3 if rel < 0.01 else (0.7 if rel > 0.03 else 1.0))
        if verbose:
            print(f"  done: t={self.t:.3e} s, steps={self.step}, phase={self.phase}")
        return self.summary()

    def sedov_energy(self, p_ratio=5.0):
        """Blast energy from a Sedov fit to the early (strong-shock) trajectory, as in experiments."""
        sh = np.array(self.shock)
        if len(sh) < 10:
            return float("nan")
        sel = (sh[:, 2] > p_ratio * self.P_ext) & (sh[:, 1] > 2 * (self.r[1] - self.r[0]) * 10)
        if sel.sum() < 5:
            return float("nan")
        t, R = sh[sel, 0], sh[sel, 1]
        E = self.rho_amb * (R / 1.0328) ** 5 / t ** 2
        return float(np.median(E))

    def audible(self):
        """A-weighted audible energy fraction of the probe waveform, and low-frequency monopole check."""
        if len(self.probe_t) < 50:
            return {}
        t = np.array(self.probe_t)
        p = np.array(self.probe_p)
        dt = max(float(np.median(np.diff(t))), 2e-8)
        tu = np.arange(t[0], t[-1], dt)
        pu = np.interp(tu, t, p)
        n = 2 ** int(np.ceil(np.log2(max(len(pu), int(0.02 / dt)))))   # zero-pad to >= 20 ms
        pu = np.concatenate([pu, np.zeros(n - len(pu))])
        F = np.fft.rfft(pu) * dt
        f = np.fft.rfftfreq(len(pu), dt)
        S = np.abs(F) ** 2                                             # Pa^2 s^2 per Hz-bin (one-sided)
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "03_simulations"))
        from display_budget import A_WEIGHT_TABLE
        fa = np.array(list(A_WEIGHT_TABLE)); wa = np.array(list(A_WEIGHT_TABLE.values()))
        Aw = np.where((f >= 900) & (f <= 22400), 10 ** (np.interp(f, fa, wa) / 10), 0.0)
        tot = S.sum()
        aud = (S * Aw).sum()
        out = dict(audible_A_fraction=float(aud / tot) if tot > 0 else 0.0,
                   peak_overpressure_Pa=float(np.max(p)), r_probe=self.r_probe)
        if hasattr(self, "dV_inside"):
            # heat-release monopole prediction |P(f)| = rho 2 pi f dV / (4 pi r) at low f
            band = (f > 2e3) & (f < 1.5e4)
            pred = self.rho_amb * 2 * math.pi * f[band] * self.dV_hot / (4 * math.pi * self.r_probe)
            meas = np.abs(F[band])
            out["monopole_ratio_2_15kHz"] = float(np.median(meas / pred))
        return out

    def summary(self):
        E_rad_tot = sum(self.E_rad.values())
        if self.phase == 2:
            E_res = float((self.m * (self.eos.iso_hT(self.Tiso) - self.eos.iso_hT(np.full_like(self.Tiso, 300.0)))).sum())
        else:
            E_res = float((self.m * (self.e - self.e_amb)).sum())
        return dict(E_abs=self.E_abs, t_end=self.t, steps=self.step, E_rad=dict(self.E_rad), E_rad_total=E_rad_tot,
                    f_rad=E_rad_tot / self.E_abs if self.E_abs else 0.0,
                    f_rad_escaping_gt200nm=(E_rad_tot - self.E_rad["euv"] - self.E_rad["vuv"]) / self.E_abs if self.E_abs else 0.0,
                    E_ac=self.E_ac, f_ac=self.E_ac / self.E_abs if self.E_abs else 0.0,
                    E_residual=E_res, lm_s=self.lm_s, eta_lm_per_W=self.lm_s / self.E_abs if self.E_abs else 0.0,
                    act_J=self.act_J, ph_o2=self.ph_o2, ph_ion=self.ph_ion, phase=self.phase,
                    E_sedov=self.sedov_energy(), f_sedov=self.sedov_energy() / self.E_abs if self.E_abs else 0.0,
                    E_heat_kernel_at_switch=getattr(self, "E_heat_kernel", float("nan")),
                    closure_at_switch=(getattr(self, "E_heat_kernel", float("nan")) + self.E_ac
                                       + getattr(self, "E_rad_at_switch", 0.0)) / self.E_abs if self.E_abs else 0.0,
                    dV_hot=getattr(self, "dV_hot", float("nan")), t_switch=getattr(self, "t_switch", float("nan")),
                    audible=self.audible())

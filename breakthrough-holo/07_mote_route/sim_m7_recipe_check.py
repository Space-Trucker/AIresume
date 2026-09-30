"""M7: independent check of the R9 mote recipes (owner: "validate and confirm").

For each recipe and absorber, compute J1/A, A_trap, k_eff and FOM from first principles.
* Absorber strength. The Cs_xWO3 absorption coefficient is derived from R9's own snippet: 0.9 mg/cm^2 gives 70 % NIR
  shielding, density ~7.1 g/cm^3, so alpha ~ -ln(0.3)/(0.9e-3/7.1 cm) ~ 1e4 cm^-1. It is compared with R9's quoted
  1-5e4 cm^-1, and with ITO nanocrystals (R9: 5.7e5 cm^-1).
* Skin geometry. The absorber is a porous shell from r = a - t to a, with solid-equivalent loading f (volume fraction)
  and dense-material coefficient alpha, so the shell coefficient is f * alpha. The core is transparent aerogel
  (n ~ 1.05, straight rays). The ray march deposits heat wherever the ray crosses the shell (front and back).
  J1 = (3/4) M1 / (P a).
* k_eff. Island or dispersed absorber gives k_eff = k_core (+0.01 for a porous loaded shell). For the core-shell
  recipe, the coated-sphere formula applies.
Writes results/m7_recipe_check.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import physics as ph  # noqa: E402


def shell_j1(a, t, alpha_shell, n_b=600, n_z=1200):
    """A and J1/A for an absorbing shell (r in [a-t, a]) around a transparent core, light along +z."""
    b = (np.arange(n_b) + 0.5) / n_b * a
    P = M1 = 0.0
    for bi in b:
        L = math.sqrt(a * a - bi * bi)
        z = np.linspace(-L, L, n_z)
        dz = z[1] - z[0]
        r = np.sqrt(bi * bi + z * z)
        al = np.where(r >= a - t, alpha_shell, 0.0)
        tau = np.concatenate([[0.0], np.cumsum(al) * dz])
        dP = np.exp(-tau[:-1]) - np.exp(-tau[1:])   # exact absorbed fraction per step (energy-conserving)
        w = 2 * math.pi * bi * (a / n_b)
        P += w * dP.sum()
        M1 += w * (dP * z).sum()
    A = P / (math.pi * a * a)
    return A, -0.75 * M1 / (P * a)


alpha_cwo_snippet = -math.log(0.3) / (0.9e-3 / 7.1)        # cm^-1, from R9's 0.9 mg/cm^2 -> 70 % shielding
ABSORBERS = {  # dense-material alpha at 1550 nm, cm^-1
    "CsWO3 (from R9 snippet)": alpha_cwo_snippet,
    "CsWO3 (R9 upper, 5e4)": 5e4,
    "ITO NC (R9, 5.7e5)": 5.7e5,
}
RECIPES = {
    # name: (a, shell thickness t, absorber volume fraction in the shell, k_eff)
    "A: a=1.5um, islands 0.2um, 60% cover": (1.5e-6, 0.2e-6, 0.6, 0.03 + 0.01),
    "A': a=1.5um, loaded shell 0.4um, 30%": (1.5e-6, 0.4e-6, 0.3, 0.03 + 0.01),
    "B: a=3um, loaded shell 0.6um, 40%": (3.0e-6, 0.6e-6, 0.4, ph.k_coated_sphere(5.0, 0.02, 0.6) + 0.01),
    "B': a=4um, loaded shell 1.0um, 40%": (4.0e-6, 1.0e-6, 0.4, ph.k_coated_sphere(5.0, 0.02, 0.6) + 0.01),
}

if __name__ == "__main__":
    print(f"Cs_xWO3 alpha implied by R9's own snippet: {alpha_cwo_snippet:.2e} cm^-1 (R9 quoted 1-5e4)")
    out = dict(alpha_cwo_snippet=alpha_cwo_snippet, rows=[])
    for rname, (a, t, frac, k_eff) in RECIPES.items():
        for aname, alpha in ABSORBERS.items():
            al_shell = alpha * 100 * frac                       # 1/m
            A, j1A = shell_j1(a, t, al_shell)
            fom = ph.figure_of_merit(j1A, k_eff)
            tau_n = al_shell * t
            out["rows"].append(dict(recipe=rname, absorber=aname, tau_normal=tau_n, A=A, j1A=j1A, k_eff=k_eff, FOM=fom))
            print(f"{rname:40s} {aname:24s} skin tau {tau_n:5.2f}  A {A:.2f}  J1/A {j1A:.3f}  k_eff {k_eff:.3f}  "
                  f"FOM {fom:.2f} {'PASS' if fom >= 4 else ('marginal' if fom >= 3 else 'FAIL')}")
    # 405 nm pump absorptance of the recipe-B core for Eu2+ alpha 1e3 / 5e3 / 1e4 cm^-1
    for a, frac in ((3e-6, 0.6), (4e-6, 0.6)):
        for al in (1e3, 5e3, 1e4):
            print(f"core radius {a * frac * 1e6:.1f} um, alpha_405 {al:.0e} cm^-1 -> pump absorptance "
                  f"{ph.absorptance(al * 100 * a * frac):.2f}")
    json.dump(out, open(os.path.join(HERE, "results", "m7_recipe_check.json"), "w"), indent=1)

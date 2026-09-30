"""Regenerate every simulation result in results/.  Usage: python3 run_all.py [--fast]

--fast skips E6b (multi-listener phase-scheduling optimisation, ~30-60 min on 4 CPUs);
E10 then reuses results/e6b_multilistener.json if present.
"""
import subprocess
import sys

SCRIPTS = [
    "sim_e1_clean_air_bounds.py",
    "sim_e2_acoustooptic_air.py",
    "sim_e5_air_chemistry.py",
    "sim_e5b_nox_speciation.py",
    "sim_e6_acoustic_scheduling.py",
    "sim_e6b_multilistener_phase_scheduling.py",
    "sim_e6c_subsonic_tracing.py",
    "sim_e7_laser_safety.py",
    "sim_e7b_uv_actinic.py",
    "sim_e9_particle_swarm.py",
    "sim_e10_feasibility_map.py",
    "sim_e11_plasma_color.py",
    "sim_e10b_redteam_corrected.py",
    "sim_e12_etendue_budget.py",
    "sim_e13_multi_projector.py",
]

if __name__ == "__main__":
    fast = "--fast" in sys.argv
    for s in SCRIPTS:
        if fast and s.startswith("sim_e6b"):
            print(f"== skipping {s} (--fast)")
            continue
        print(f"== {s}")
        r = subprocess.run([sys.executable, s])
        if r.returncode != 0:
            sys.exit(f"FAILED: {s}")
    print("all simulations completed")

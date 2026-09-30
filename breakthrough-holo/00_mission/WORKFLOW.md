# Lab protocol

This is v1, written at lab setup. It gets revised once the literature review of Anthropic's agent-engineering articles and AI-scientist workflows lands (`01_research/R0_research_workflow_methods.md`).

## Roles
- **PI / engineer (main agent):** owns the goal, theory, simulations, design, and the final verdict.
- **Research agents (parallel subagents):** each owns one literature frontier and writes one cited notes file in `01_research/`. They never edit anything else.
- **Red team (separate agents, run later):** gets the design cold and tries to break it (physics, safety, feasibility). Findings go in `05_reviews/`.

## Rules
1. **Goal first, results second.** `GOAL.md` fixes the definition of "solved" and the grading rule *before* any result exists. Goalposts don't move; if a requirement proves impossible, record NOT MET and why.
2. **Falsify first (strong inference).** For every candidate mechanism, compute the number that could kill it before investing in it. Kill early and write down why in `NOTEBOOK.md`.
3. **Every number has a pedigree:** a citation (in `01_research/`), a derivation (in `02_theory/`), or a simulation (in `03_simulations/`). Estimates are labelled as estimates, with an error band.
4. **Validate every model against at least one published measurement** before using it for design (a "calibration check" printed by the script).
5. **Simulations are reproducible:** one script per question, deterministic, and `python3 run_all.py` regenerates all results. Plots and JSON results live in `03_simulations/results/`.
6. **Log decisions in `NOTEBOOK.md`** (dated): hypothesis → test → result → decision.
7. **Commit and push after every meaningful step.** The container is ephemeral; unpushed work is lost work.
8. **One question at a time.** Finish, validate and log each simulation before starting the next dependent one. Independent research runs in parallel.
9. **When stuck, run a structured idea round:** list physical effects exhaustively (emission, scattering, refraction, nonlinear, acoustic, thermal, electrical, chemical, biological/perceptual), estimate each in one line, and pursue the survivors. Include ideas the literature has not tried.
10. **Report honestly.** The final verdict grades each requirement MET / PARTIAL / NOT MET, with evidence.

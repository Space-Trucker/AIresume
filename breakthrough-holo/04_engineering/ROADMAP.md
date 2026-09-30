# Roadmap: from this research to a first projector

The simulations leave five physical numbers that decide how bright, how quiet and how clean the product can be. Each has an uncertainty band of 3–30× in `display_budget.PARAMS`. **A startup's first money should buy measurements of these five numbers, not a full prototype.**

## Phase 0: bench experiments (≈ 3–6 months, ≈ $150–250k incl. a rented or used ultrafast laser)

| # | Experiment | Setup | Decides |
|---|---|---|---|
| X1 | **Luminous output per absorbed joule** of single micro-sparks vs pulse energy (1–100 µJ), duration (0.3–10 ps, fs-seed + ps-heater pairs), wavelength (1.03 vs 1.55 µm), NA (0.1–0.3) | Calibrated photometer and spectrometer at 0.3 m; energy meter before and after the focus gives absorption | η (lm/W). The model says 0.1–0.4 (band 0.03–1.2). **Every lumen of the product scales with this.** |
| X2 | **O₃ / NO / NO₂ per absorbed joule** at the same settings | Sealed 10 L chamber, ppb analysers, 10⁵–10⁶ sparks | Y (molecules/J), band 3×10¹⁵–1.5×10¹⁷. Sets the chemistry cap. |
| X3 | **Acoustic N-wave** of one spark: shape and duration at 0.1–2 m, and the fraction of energy in the shock | 1/8" microphone to 200 kHz + a Schlieren photo | k_T and f_ac, which set the audible fraction. |
| X4 | **Acoustic phase scheduling** demo: 1–4 microphones as "ears", a 5k-spark frame | FPGA pulse picker plus 2-axis AOD | Validates −26 dB (1 ear) and the multi-ear result (E6b) in real air. |
| X5 | **Capture efficiency** of push–pull airflow around a spark cloud | Tracer gas, then real sparks with an NO analyser at "face" positions | The capture fraction (design assumes 0.9). |
| X6 | **Spark-to-spark absorbed-energy stability** (fs seed + ps heater vs single pulse) | Transmitted-energy monitor, 10⁶ shots | Must be ≤ 10 % rms, or subsonic tracing loses its noise gain (E6c: 5 % → −21 dB, 10 % → −18 dB, 20 % → −14 dB) |
| X7 | **Speciation** (NO : NO₂ : O₃) of 5–30 µJ micro-sparks | Same chamber as X2 with separate NO, NO₂ and O₃ analysers | E5b: the room-safe power budget ranges from ×2.3 (O₃-rich) to ×12.3 (NO-rich). Decides whether film *density* is reachable (P = 0.45–0.81). |

**Go / no-go:** proceed to Phase 1 if X1 × (1/X2) is at least the model's nominal value (≥ 3×10⁻¹⁸ lm·s per reactive molecule) *and* X6 ≤ 10 % rms.

**Product tier is set by X7:**
- **NO-rich products:** film stroke density (15–57 m) at film contrast in a dim lab.
- **O₃-rich products:** a 5–9 m "sketch" tier.

## Phase 1: desk-scale demonstrator "Aether-D" (≈ 9–12 months)

- A 30 × 30 × 30 cm volume, 1 optical head, 2 channels, 5–10 W, 1550 nm.
- Safety kernel on an FPGA with a single depth camera and a hand-only interlock (the head kept out by enclosure geometry: a clear-acrylic hood, open front).
- Glove v1.
- Target: 2–3k points at 60 Hz, visible in a dim room.
- Use: investor and partner demos, safety-certification test article, content-tool development.

## Phase 2: room-scale "Aether-1" ceiling halo (≈ 18–24 months)

The full architecture in `ARCHITECTURE.md`:
- 3 heads, 12 channels, 20–40 W.
- Push–pull air handling.
- Multi-person tracking, acoustic phase scheduling.
- Class 1 by engineering controls (IEC 60825-1), SIL-2 safety kernel, FDA variance (US).
- Target market: showrooms, museums, product-design studios, premium entertainment, and "Iron Man workshop" experiences in dim rooms.

## Product lines the owner asked about

- **Advertising and signage:** feasible only as *night-time or dim-venue* aerial signage (sparse glowing text and logos, all-around visible). Daylight or bright-mall use is outside the physics budget.
- **Iron Man helmet:** inside a helmet the display sits centimetres from the eye, so the right technology is not the plasma projector. It is a visor HUD (holographic waveguide or birdbath combiner), which is proven and cheap and gives full colour and film quality for the wearer. A helmet line is a separate, much easier product. A "no glasses" requirement cannot apply to a helmet, since the visor *is* the eyewear.

## Risks, ranked

1. **X1/X2 come out at the pessimistic end** (efficacy ≤ 0.05 lm/W or ≥ 10¹⁷ molecules/J). The product then shrinks to sparse, dark-room effects.
2. **Regulatory:** a Class 4 source made safe by active interlocks in a consumer space. The route is IEC 60825-1 "Class 1 during operation" + IEC 61508 SIL 2 + an FDA variance. Expect 12–24 months and to start with supervised venues (B2B) before homes.
3. **Cost of 1550 nm ultrafast sources at 20–40 W.** Watch telecom and LIDAR fibre-laser cost curves.
4. **Perception:** points ~2 mm apart look "sparkly", not solid. That is on-brand for the film look, but video panels will look like LED dot matrices.

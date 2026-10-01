# R11: Sourcing guide for the DIY photophoretic bench (DIY-1 to DIY-4)

Compiled 2026-10-01. This guide covers what to buy, where to buy it, what it costs, the minimum spec, and what to avoid, for the staged
private-builder version of the bench program in `BENCH_PLAN.md`:

| DIY stage | Matches | Purpose |
|---|---|---|
| DIY-1 photophoretic velocimetry | B1 (U1) | Measure the force per absorbed watt from the particle drift in a collimated beam |
| DIY-2 BYU-style optical trap display | Smalley et al., *Nature* 553, 486 (2018) | Trap one absorbing particle with a 405 nm aberrated focus, scan it with galvos, draw a ~1 cm POV image |
| DIY-3 phosphor / fluorescent particles | B4 (U4) | Screen particles that glow under 405 nm |
| DIY-4 1550 nm doughnut pair | B3 (U3) | Two opposed LG01 beams at 1–1.5 m from a DFB seed and an EDFA |

**Provenance tags.** [SNIPPET] means a price or spec quoted from a search-engine result snippet or listing summary, which I did not
open. [MEMORY] means model recall that I did not re-verify. [ESTIMATE] means my own calculation or judgement, with the inputs stated.

**Access caveat.** WebFetch was egress-blocked for every page I tried: hackaday.com, jove.com, digitalcommons.calpoly.edu and
alexwhittemore.com. **Every price below comes from search snippets** and is a marketplace snapshot. Listings change weekly, some
snippets may show stale or sale prices, and marketplace "prices" often exclude shipping, VAT and duty. Treat every figure as
±30 % and check it before ordering.

**Main-session validation (owner rule 12), 2026-10-01.** Spot-checked against independent searches and our own calculations:

| Claim | Check | Result |
|---|---|---|
| Helios DAC listed as a "≥16-bit" option (§7.2, BOM DIY-2 row 5) | Vendor spec: standard Helios is **12-bit X/Y**, 65.5 kpps, max **4095 points per frame**. The **HeliosPRO** is 16-bit | **Corrected** below. A 12-bit Helios is fine if the galvo driver's size trim is turned down (see `diy2_control/ELECTRONICS.md`); `helios_stream.py` now enforces the 4095-point frame limit |
| Thorlabs LG3: OD 7+ at 180–532 nm, $191 | Thorlabs and resellers: OD 7+ 180–532 nm, $190.59 | Confirmed. **Added:** its EN 207 LB rating limits use to about **1 W CW at 532 nm** over a 7 mm aperture. Check the LB rating at *your* wavelength against *your* maximum power; a 1.6–2 W 445 nm diode needs eyewear rated for it |
| Basler acA720-520um, 525 fps, $379–433 | Basler and distributors: €349 list, $379–436 | Confirmed |
| 12-bit DAC gives 20–40 µm steps over the image | Our stage calculation: 17.8 µm per step at full scale (f = 100 mm, ±10° mech.); 22 µm at f = 125 mm | Consistent |
| I₀ = 2P/(πw²) sizing table | Recomputed | Confirmed. This also corrected our guide: 10 W/cm² peak needs only 0.63 W in a 4 mm (1/e² diameter) beam |
| Toner binder softens at ~50–65 °C | Adopted in `diy_calcs.py` (max particle temperature 335 K; PS/PMMA 373 K) | Toner's trap window shrinks from ×22 to ×7 |
| Carbon-coated hollow glass not stock | Accepted | DIY-1 reference pair becomes glassy carbon + black PE/PS; hollow low-k particles move to B2 |
| Black anodised aluminium reflects in the NIR | Accepted | Guide's beam-dump line corrected |

---

## 0. Safety preface (read first)

Every laser in this guide above ~5 mW is **Class 3B or Class 4**. DIY-1 and DIY-2 use 0.1–2 W of visible light. DIY-4 uses 1–5 W of
invisible 1550 nm light. The safety rules in `BENCH_PLAN.md` apply in full:

- enclosed beam path with an interlocked lid;
- wavelength-rated eyewear when the enclosure is open;
- a beam dump on every beam;
- alignment at the lowest power the laser allows;
- particles kept sealed.

This guide covers only **buying the safety parts correctly**. It contains no advice on defeating interlocks, enclosures or other
safety features, and none should be followed from any other source. Where a product is sold as a sealed Class 1 machine (for
example the "A1 Pro" engravers, §1.4), the right choice is a bare module made for integration, **not** opening the machine.

---

## 1. Laser sources

### 1.1 What to search for

| Need | Search keywords | Marketplace price [SNIPPET] | Specialist alternative [SNIPPET] |
|---|---|---|---|
| 405 nm, 0.3–1 W, with TTL | "405nm 500mW laser module TTL 12V", "405nm 1W dot laser module TTL analog", "NDV7375" | 500 mW module with separate TTL/PWM driver: **£45** (OdicForce). 405 nm 50–200 mW Laserland 3350 modules: **$22**. Bare Nichia NDV7375 (1.2 W, 405 nm): **$299**. eBay "405 nm 1000 mW dot module + TTL/analog + TEC + PSU": listed, price not captured | Endurance 1.7 W 405 nm module with analog/TTL: **$495**. Edmund 405 nm 1 W fibre-coupled benchtop (TTL + analog to 30 kHz): price not captured. Laser Diode Source turnkey NDV7375 head: **>$5,000** |
| 445/450 nm, 1–7 W | "NDB7875 445nm copper module", "NUBM44 450nm module", "450nm 5.5W optical laser module TTL" | NDB7875 (1.6–2 W, 445 nm) in a copper module with G-2 lens: **$65–96** (driver not included unless stated). Bare NDB7875-E: $129. NUBM44 (6–7 W, 450 nm) in a module: **$54–75**. 4 A "SXD/X-Drive" driver: **$35**. Integrated 450 nm engraver head "5 W optical" with TTL: **~$155** (eBay) | Thorlabs and Laser Diode Source sell traceable diodes and mounts. Thorlabs' L405P150 (150 mW) is discontinued (was $90) |
| 808 nm, ~1 W | "808nm 1W laser module TTL focusable 12V" | **$47–92** (AliExpress OXLasers, Amazon G-L1000, LaserSE). Laserland 3380 808 nm 0.8–2.4 W with TTL: **$80–88**. Bare 808/980 TTL driver boards: ~$4 | – |
| 980 nm, ~1 W | "980nm 1000mW TTL dot laser module" | **~$92** (eBay) | Arktis/Laserglow collimated 980 nm systems: **from ~$4,100** |
| 1064 nm DPSS, 0.1–1 W | "1064nm DPSS laser 1W CW modulation" | 100 mW–1 W: **$555–834** (CivilLaser). Alibaba lists similar | Arktis RA6 1064 nm system (100–1000 mW): **from $2,186** |
| Laser diode driver | "laser diode driver constant current TTL analog soft start 405nm" | **$6–45** for boards. 0–3.2 A 12 V TTL/PWM: £15 (OdicForce). 0–5 A 100 kHz analog/TTL: ~$45 (eBay) | Thorlabs LDC-series controllers: hundreds to >$1k [MEMORY] |

### 1.2 Minimum spec

**DIY-1** (any of 405, 445/450 or 808 nm):

- **0.5–2 W CW** from a **single-emitter** diode, with a constant-current driver offering **TTL on/off and preferably analog power
  control**, plus heatsinking and a fan.
- An **adjustable glass collimating lens** (G-2 or 3-element). Avoid acrylic lenses.

Beam power sizing [ESTIMATE]: the peak intensity is I₀ = 2P/(πw²).

| 1/e² radius w | Power for 10 W/cm² | Power for 100 W/cm² |
|---|---|---|
| 1.0 mm | 0.16 W | 1.6 W |
| 1.5 mm | 0.35 W | 3.5 W |
| 2.0 mm | 0.63 W | 6.3 W |

So a 2 W diode covers the B1 power series to ~100 W/cm² only if w ≈ 1 mm.

**DIY-2:**

- 405 nm, **0.1–1 W**. BYU's test rigs start from a 500 mW 405 nm diode. The lowest successful trap was 18 mW, and minimum hold
  power was <24 mW (`07_mote_route/R5`).
- TTL modulation for blanking. Analog power control is a plus.
- A **separate driver**, so the driver can be switched off by the interlock.

### 1.3 Reliability notes

- Nichia diodes (NDB7875, NUBM44, NDV7375) are the de-facto hobby standard. They are robust when driven within spec by a proper
  constant-current driver. Most "modules" on eBay are a **diode pressed into a copper host with leads and a lens, with no
  driver**. You must add a driver.
- Diodes from salvaged projectors are sold "new" or "low-hours" ($25–55). That is acceptable for DIY-1. Ask for a test photo on a
  power meter.
- 405 nm and 445 nm diodes above ~300 mW are **multimode** in the slow axis. The beam is elongated, with M² of order 5–20
  [MEMORY]. For DIY-1, expand and aperture the beam, then **profile it**. For DIY-2 a non-Gaussian beam is acceptable, since BYU's
  trap is itself an aberration trap.

### 1.4 Red flags: lasers

1. **Electrical versus optical watts.** Engraver modules sold as "20 W" or "40 W" are typically **5–5.5 W optical**, and the
   "40 W" is the electrical input [SNIPPET: Laser Tree, Probots]. Only the optical figure counts. Pointer-style listings claiming
   "10,000 mW" are routinely far below claim on forum power meters [SNIPPET: LaserPointerForums threads]. **Measure every source
   yourself** with the thermal meter (§3).
2. **Engraver heads are not collimated beam sources.** "Compressed-spot / FAC / dual-diode" heads (Snapmaker 10 W, Laser Tree,
   Longer, Elegoo) **combine 2–4 emitters and focus to a ~0.05×0.2 mm spot at 30–50 mm** [SNIPPET: Snapmaker]. You cannot easily
   make a clean collimated 2–4 mm beam from one. Use a single-emitter diode with an adjustable lens for DIY-1.
3. **"A1 Pro".** This is most likely the **Creality Falcon A1 Pro**: a $949–1,099, **Class 1 enclosed** 20 W (455 nm) engraver
   with a lid-open halt and an e-stop [SNIPPET: Creality, Tom's Hardware]. It is a sealed machine, not a beam source. Removing its
   laser defeats its Class 1 protection. **Do not buy it for this bench. Buy a bare module made for integration.**
4. **A module with no driver, or "driver: use a 5 V adapter".** A diode fed from a constant-voltage supply dies on the first
   surge. Require: constant current, a current limit **at or below** the diode's rating, soft start, and reverse/ESD protection.
5. **Missing or ambiguous TTL.** Some cheap boards accept PWM only, or invert TTL logic, or run the laser **when the TTL wire is
   left unconnected**. Test this at the lowest current, with the beam in a dump, before relying on it. For the interlock, always
   **cut the driver's supply as well**, not only TTL (§6.6).
6. **Wavelength drift.** "405 nm" diodes span ~400–410 nm, and "445" spans 440–450 nm. Bad lots are worse. This matters for
   eyewear coverage (§2) and for phosphor excitation (§9).
7. **Cheap 1064 nm DPSS** can leak 808 nm pump light if the IR filter is missing [SNIPPET: LaserPointerForums IR-leakage
   threads]. Eyewear must then cover 808 nm too. For DIY-1 there is no physics reason to choose 1064 over 445 nm.
8. **808, 980, 1064 and 1550 nm are invisible.** The blink reflex does not help. Align with IR viewer cards (§6.7), and expect a
   higher accident risk than with 445 nm.

---

## 2. Laser safety eyewear

### 2.1 Which certifications matter

- **EN 207** (EU, UK, many other countries). The marking reads e.g. `450 D LB5 + 405 D LB6 [maker] CE`. It gives the wavelength
  range, the mode (D = continuous wave, I/R/M = pulsed), and the **LB scale**. LBn means OD ≥ n **and** that the filter and frame
  survive direct exposure at the matching power density for the test time without losing protection [SNIPPET: Wikipedia EN 207,
  Laser 2000]. LB is more meaningful than a bare "OD" because it includes the **damage resistance** that cheap dyed plastic lacks.
  EN 207 conformity needs **third-party type-examination**. Look for the test-house or notified-body mark: Amazon "LaserPair"
  listings cite DIN CERTCO, for example.
- **ANSI Z136.1** (USA). Eyewear must be **labelled with OD at specified wavelengths**, and the user picks the OD for the hazard.
  ANSI Z136 is a use standard, not a certification scheme. In the US you depend on the maker's honesty, so buy from makers that
  publish **transmission curves** (Thorlabs, LaserVision, Kentek, Phillips, Laser Safety Industries).
  ANSI **Z87.1** is impact protection only, not laser protection.
- **OD needed** [ESTIMATE]:
  - 0.5–2 W visible CW, accidental 0.25 s exposure: OD ≈ 3–3.5 already brings power to Class-2-like levels through a 7 mm pupil.
  - Longer accidental exposures at 405–450 nm fall under the blue-light photochemical limits, which push the need to **OD 5+**.
  - Choose **OD ≥ 5 (LB5 under EN 207) at every wavelength in use for ≤ 5 W**.
  - At 1550 nm, OD ≥ 4 is ample at a few W. The MPE at 1.4–4 µm is ~0.1 W/cm² for long exposures, and 5 W in a few mm is
    ~10–60 W/cm².
  - Do the formal calculation with ANSI Z136.1 / EN 207 once powers are fixed.

### 2.2 Reputable, affordable options [SNIPPET]

| Product | Coverage | Price | Note |
|---|---|---|---|
| Thorlabs **LG3** (LG3A/B/C styles) | OD 7+ at 180–532 nm, 48 % VLT, ANSI Z136.1 + EN 207 | **$191** (Thorlabs; $259–285 resellers; ~$150 used) | Covers 405 + 445/450 (+520/532). Blocks the blue RGB illumination too |
| Thorlabs **LG10** | OD 7+ at 190–534 nm and 960–1064 nm; OD 6+ 925–1070; OD 5+ 850–925 | ~$123 used (eBay). New price not captured | Visible + 1064, **not 808, not 1550** |
| Thorlabs **LG11** | OD 4+ at 900–2600 nm, 75 % VLT, clear | **$430** | For DIY-4 (1550 nm) |
| Thorlabs **LG9** | >750–1064 nm, plus 180–400 nm OD 6+ | **$244** | **Does not cover 1550 nm or 405 nm.** Easy to mis-buy |
| LaserVision USA **F18** frame + filter | Depends on filter | **$69–259** | Pick a filter whose datasheet states the LB/OD at your wavelength |
| Kentek KBS-20C / KMT-21F (glass) | Blue/violet | **$285–347** | – |
| Phillips Safety DFIU | OD 7+ at 190–540 nm | **$499** | – |
| Eagle Pair (Survival Laser) | OD 6+ at 190–540 nm, "CE certified", 50 % VLT | **$45–50** | Budget brand from a known hobby vendor. One blogger's spectrophotometer and laser check found 405 nm "reduced to theoretically safe levels (<1 mW)", but **19 mW of IR from a cheap DPSS still got through** [SNIPPET: alexwhittemore.com]. Acceptable as **spares**, not as the only pair at multi-W |
| J Tech Photonics goggles | OD 4+ at 405–455 nm | **$25** | Vendor states it checks each pair with a 445 nm laser and a meter [SNIPPET]. OD 4 is marginal above ~1 W |

**DIY-2 viewing trick.** To see the RGB-lit particle while blocked from the 405 nm trap beam, you need eyewear with
**OD ≥ 5 from ~395 to ≥ 415 nm and high visible transmission** (yellow lens, "190–420/450 nm"-type filters).

- Some "UV" eyewear is rated only to **400 nm**, for example one Thorlabs model listed as OD 5+ at 190–400 nm [SNIPPET]. That
  **does not cover 405 nm**.
- Yellow 405 nm eyewear passes 450 nm. Keep blue illumination at Class 2 / 3R levels, or keep it enclosed.

### 2.3 Why cheap marketplace goggles are risky

- J Tech Photonics reports that **every pair** in one shipment from a Chinese supplier failed its ANSI testing, despite ANSI
  markings printed on the lens. Many such "goggles" are moulded non-optical plastic [SNIPPET: J Tech, "Be careful when buying laser
  safety goggles"].
- LaserPointerForums tests of <$9 orange Uvex general safety goggles, which hobbyists used for violet/blue/green lasers, found
  **2.5 % transmission at 532 nm (OD ≈ 1.6)**. A destructive test of the same type of goggle reported **complete burn-through in
  <5 s** [SNIPPET]. Tinted safety goggles are not laser eyewear.
- Multi-band claims such as "OD 4+ 190–450 & 800–2000 nm" or "OD 7+ 190–540 nm" for $10–30 cannot be checked from a listing. A
  printed OD with no LB rating, no test-house mark and no transmission curve is a red flag.
- DHS published a *Laser Protective Eyewear Market Survey* in July 2024 (dhs.gov). It was not read here. It is a possible source
  of vetted brands.

**Rule: eyewear is a must-buy-reputable item (§12).** If you also own cheap pairs, check them against a known-good pair with your
own laser at low power and a power meter: compare the power behind each filter, never by eye. This is only a rough check, not a
certification.

---

## 3. Thermal laser power meter

### 3.1 Options [SNIPPET]

| Tier | Example | Price | Accuracy / note |
|---|---|---|---|
| Generic marketplace | "LPM-10W laser power meter 1 mW–10 W, 200–10600 nm" | **~$120** new | Claims "±2 %". Sensor maker and calibration traceability unknown. **Treat as uncalibrated** |
| Hobby LPMs | LaserBee II / 2.5 W / 5 W ("Limited Edition" units used real Ophir 20C-A heads) | **$240–360** (LaserBee II); $500–700 for Ophir-head editions | Respected in the hobby community. Calibration age varies |
| Used pro thermopile head | Ophir **3A** (10 µW–3 W, Ø9.5 mm): **$199**; 3A-P: **$262**; Coherent LM-10 HTD (10 W): **$299** (eBay) | **$200–300** + display | ~±3 % when in calibration [MEMORY]. Needs a display or interface |
| Used pro display | Ophir Nova / Nova II / Juno (USB) | **$400–500** (Nova, used); Nova II with head $1,600; Juno USB new $733–752, **Juno+ new $834** | Juno lets a PC log power, which is useful for B1 power series |
| New pro, all-in-one | Thorlabs **PM16-405** (5 W) / **PM16-425** (10 W) USB thermal | **$1,343** (PM16-425) | 190 nm–20 µm, Ø25 mm |
| New pro head + console | Thorlabs **S425C** (10 W, Ø25.4 mm) + PM100-series console | **$987** + console | – |
| New handheld | Gentec PRONTO-250-EZ | **$1,163** | – |
| Not suitable | Sanwa LP1/LP10, Arktis LP1 (photodiode, ≤40 mW) | – | Cannot read W-level beams without a calibrated attenuator |

### 3.2 Minimum spec

- **Thermopile** (broadband, wavelength-flat).
- Range ≥ 3 W (DIY-1/2) or **≥ 10 W** (DIY-4, 1–5 W per beam).
- Aperture ≥ 10 mm.
- A calibration date within ~2 years. Recalibration costs a few hundred dollars [MEMORY].
- Respect the head's **power-density limit**: do not focus a W-level beam onto it.

### 3.3 How accurate it needs to be [ESTIMATE]

- B1 reports F/P_abs. A power error passes **1:1** into C_ph. The G1 window (0.5–1.3) tolerates ±10 %, but ±3–5 % is better.
- The **glassy-carbon / polymer drift ratio** in G1 needs **no power calibration**, because both particles sit in the same beam.
- The **beam radius enters squared** (I₀ = 2P/πw²). A 10 % error in w gives a 20 % error in intensity. **Profile the beam
  carefully.** Knife-edge or camera profiling (§6.4) matters more than the meter's last few percent.

**Red flags:** listings with no sensor model, "±1 %" claims at $100, and "0–100 W" ranges from a tiny head. Unbranded meters may
report the electrical draw of a module instead of its optical power if used wrongly. For used meters, check that the **head and
display are compatible** (Ophir smart heads need a matching display) and that the head's coating is not burned.

---

## 4. Cameras and lenses

### 4.1 What the velocimetry needs [ESTIMATE]

`BENCH_PLAN.md` sets the rule: motion ≤ ~5 px per frame. Drift ranges from 0.2 mm/s (glassy carbon) to 5–10 mm/s (polymer and
hollow particles), plus 0.2–1.2 mm/s of settling.

| Scale | fps needed for 5 mm/s | fps needed for 10 mm/s |
|---|---|---|
| 3.45 µm/px | ~290 | ~580 |
| 6.9 µm/px | ~145 | ~290 |

- Glassy carbon needs ~70 fps at 3.45 µm/px. Its 1.2 mm/s settling, not its 0.23 mm/s drift, sets the rate.
- A 5 µm black particle on a dark background, side-lit, gives a bright blur that can be centroided below one pixel even at
  5–7 µm/px.
- Depth of field at an imaging NA ≈ 0.05 is ~0.2 mm.

### 4.2 Camera options [SNIPPET unless noted]

| Option | Sensor / spec | fps | Price | Fit |
|---|---|---|---|---|
| **Basler ace acA720-520um** | Sony IMX287, 720×540, 6.9 µm px, mono, global shutter, USB3, C-mount | **525 fps** at full frame | **$379–433 new** (Basler list). eBay "new" listings at $1,500+ are overpriced | **Best value for B1.** Hardware timestamps, exposure control, ROI |
| FLIR/Teledyne **Blackfly S BFS-U3-04S2M** | IMX287 | **522 fps** | Price not captured. Used Blackfly S cameras appear at $384–750 | Same sensor, mature SDK (Spinnaker) |
| Visiondatum IMX287 USB3 | IMX287 | 526 fps | Price not captured. Their PYTHON300 815 fps camera is **from $450**; IMX273 250 fps is $544 | Chinese machine-vision brand. Check the SDK and Linux support |
| **Raspberry Pi Global Shutter Camera** | IMX296, 1456×1088, 3.45 µm px, C/CS mount | **60 fps** full; **118 fps** at 720×540; **536 fps** at 128×96 (sensor-level crop, not ISP crop) | ~$50 [MEMORY] + a Pi 5 | Budget path. A **wide, short strip ROI** suits a horizontal beam. My estimate from the row scaling above is ~230–300 fps for 1456×200–270 rows (5 × 0.7–0.9 mm at 1×) [ESTIMATE]. Hermann-SW's crop-tool gist documents the method |
| **Arducam OV9281 USB (B0332)** | 1 MP mono global shutter, 3 µm px, M12 lens | 120 fps at 1280×720; **210 fps at 640×400** | **$39–65** | Cheap but MJPG-compressed, M12 mount (needs an adapter), UVC timing jitter |
| Phone slow-motion | iPhone 8 and later: 1080p at **240 fps** | 240 fps | (owned) | Rolling shutter, compressed, auto-exposure, no macro. **Qualitative only** |
| Sony RX100 IV/V high-frame-rate mode | Real high-frame-rate capture | 960/1000 fps at 1136×384 ("quality priority") or 800×270; **2–4 s buffer** | ~$300–450 used [MEMORY] | Real frames, but upscaled output files and a short buffer |
| Kron **Chronos 1.4** | 1280×1024 | **1,057 fps** full; up to ~21,600 fps cropped | **$2,500–5,600** depending on RAM / era | Overkill for B1. Useful for DIY-2 particle dynamics |

### 4.3 Lenses for ~2–7 µm/px [SNIPPET]

| Lens | Price | Notes |
|---|---|---|
| **C-mount 0.7–4.5× zoom monocular** ("180X/300X industrial microscope lens", ~100 mm WD) | **$60–100** (AliExpress HAYEAR $76 with a 0.5× Barlow; Walmart $99); bare "adapter" versions ~$14–25. Omano OM10K: $294 | Cheap, adjustable. Distortion and calibration vary. Calibrate with a stage micrometer |
| **C-mount telecentric 1× or 2×, 110 mm WD** | ZLKC (AliExpress) **$166–176**; VA Imaging **$341**; Edmund CompactTL **$645 (1×) / $705 (2×)** | Telecentric: magnification does not change with depth, which is ideal for velocimetry across a 10 mm cuvette. The best choice if affordable |
| Long-working-distance infinity objective (2×/5×) + tube lens | – | Not priced here. Mitutoyo-style objectives are common used [MEMORY] |

With IMX287 (6.9 µm px): 1× gives 6.9 µm/px over a 5.0 × 3.7 mm field, and 2× gives 3.45 µm/px over 2.5 × 1.9 mm. With
IMX296 (3.45 µm px): 1× gives 3.45 µm/px over 5.0 × 3.8 mm.

**Also buy:**

- A **stage micrometer** (0.01 mm divisions) to calibrate µm/px. AliExpress ~$10–20 [ESTIMATE].
- A **long-pass or notch filter** to keep the laser line off the sensor if you image with side LED light. Colored glass (GG/OG
  types) costs ~$10–20 on AliExpress. Thorlabs/Edmund interference filters cost ~$100–150 [MEMORY].

**Red flags: cameras**

- "1000 fps" webcams that are really interpolated or rolling-shutter.
- Frame-rate figures quoted only at tiny ROIs.
- USB-2 compressed (MJPG) streams that drop frames silently. **Verify the frame interval** by filming an LED driven at a known
  frequency from the microcontroller.
- Phone "960 fps" modes that capture only ~0.2 s, and are sometimes partly interpolated (unclear from sources).

---

## 5. Particles (microspheres, tracers, toner)

### 5.1 Options [SNIPPET]

| Particle | Product / search | Size | Price | Who can buy |
|---|---|---|---|---|
| **Glassy carbon spheres (skin absorber, k_p ≈ 6)** | Thermo Scientific (ex-Alfa Aesar) **038008** "Glassy carbon spherical powder, 0.4–12 µm, type 2" | 0.4–12 µm (broad) | **$72 / 10 g** | Thermo/Fisher usually require a business account [MEMORY] |
| | Sigma-Aldrich **484164** "Carbon, glassy, spherical powder, 2–12 µm, 99.95 %" | 2–12 µm | **$114 / 10 g; $384–455 / 50 g** (resellers); UK £89 / 10 g | **Sigma does not ship to residential addresses or private individuals** [SNIPPET: Sciencemadness] |
| | SPI Supplies "Sigradur K glassy carbon powder, spherical" | 0.4–12 µm; a **10–20 µm** grade also exists | **$298 / 100 g** (10 g not listed) | Unclear whether they sell to individuals |
| **Black polymer spheres (volume absorber, k_p ≈ 0.25)** | Cospheric **BKPMS** black (paramagnetic) polyethylene, 1.2 g/cc | **10 µm and up** (1–5 µm not offered) | **$142–530** per size / quantity (e.g. 38–45 µm, 5 g = $294) | Online store |
| | Polysciences **Polybead black dyed** polystyrene | 0.2, 1, 3, 6, 10 µm, as **aqueous suspension** | 6 µm (24293-5, 5 mL): **$1,260** quoted by a reseller. Seems high; verify | Distributors |
| | Bangs Labs "Dyed Carboxyl Polystyrene, Basic Black, 5.00 µm" | 5 µm, 5 % solids suspension | Price not captured | Distributors |
| **Carbon-coated hollow glass / hollow silica (k_p ≈ 0.1)** | **Not found as a stock catalog item.** Cospheric sells **nickel-plated** hollow glass 5–30 µm (**$139–148 / 8 g**), silver-coated and TiO₂-coated hollow glass. "Black paramagnetic coated glass" is **solid** glass with a **hemispherical (Janus) coating** (**$991**) | 5–30 µm | – | A custom carbon skin is a B2 (chemistry-lab) task |
| | ACS Material hollow carbon spheres | ~200 nm (too small) | **$375–520** | – |
| **White silica tracer spheres (non-absorbing reference)** | Cospheric monodisperse silica, 0.17–9.2 µm | Monodisperse | **$224–367** | Online store |
| | Whitehouse Scientific 5 µm monodisperse silica set | 5 µm, 5 × 0.2 g | **from £70** | Online |
| | Polysciences dry silica 5.0 µm | 5 µm | **$1,019** | – |
| **Laser printer toner (cheap black)** | Toner refill bottle for a specific printer | **Chemically prepared ("CPT", EA, suspension-polymerised): ~5–7 µm, near-spherical, narrow distribution. Pulverised: ~8–10 µm and up (9–20 µm in patents), irregular, broad** | ~$10–20 per 100 g [ESTIMATE] | Anyone |

### 5.2 Notes on each particle

- **Glassy carbon** is the right reference for the skin-absorber model (`BENCH_PLAN.md` red-team note).
- **Black polymer spheres.** Per `BENCH_PLAN.md`, dyed or loaded polymers absorb through their volume, with J₁/A ≈ 0.02–0.5. They
  are not a skin-absorber reference. Suspensions must be **dried and deagglomerated** before use in air.
- **Hollow particles.** For DIY-1, glassy carbon plus black PE/PS covers the k_p contrast. Hollow, low-k particles wait for B2.
- **Silica tracers** are needed to measure beam-tied convection in the same cuvette.
- **Toner.** Toner is **not a reference particle**:
  - It contains **wax, charge-control agents, surface silica/TiO₂ and often magnetite**. Its binder softens near **~50–65 °C**
    [MEMORY], which a B1 power series at ΔT ≈ 100 K will exceed.
  - Pulverised toner is irregular.
  - Use it only for **DIY-2 trap practice**. BYU's 10-material screen found printer toner trapped ~10 % of the time, versus
    55–75 % for diamond nanoparticles [SNIPPET; source likely the RSI 2021 / JoVE rig papers].

**Other DIY-2 trap particles.** BYU's screen also covered black liquor (powder and paste), tungsten, aluminium powder, graphite and
nigrosin. *Nature* 2018 trapped a **cellulose** particle (~10 µm), and a 2025 SPIE paper used **soot**. Classroom kits trapped
graphite and yeast (`R5`). Graphite powder, carbon black and nigrosin cost $10–30 from art or chemistry hobby suppliers [ESTIMATE].

### 5.3 Red flags: particles

1. **A stated size range is not a size distribution.** "0.4–12 µm" glassy carbon may be mostly <3 µm by number. **Measure the
   distribution yourself** under a microscope with a stage micrometer. Classify by sedimentation in ethanol or IPA, or with sieves,
   if a narrow cut is needed.
2. "Microspheres" on marketplaces (cosmetic PMMA, "glass beads") with **no CV or SEM image**: assume polydisperse and partly
   non-spherical.
3. **Janus / hemispherically coated spheres** (Cospheric "black paramagnetic coated glass") give asymmetric absorption, which adds
   Δα forces and rotation. Avoid them for B1.
4. **Suspension versus dry powder.** Drying gives agglomerates, which read as large particles. Sonicate, then dry thinly and
   gently.
5. **Static.** Dry micro-particles cling to cuvette walls. An anti-static ionizer (e.g. a Zerostat-type gun, ~$100–150 [MEMORY])
   helps. Ionizers based on radioactive sources are regulated in some countries; avoid them.
6. **Inhalation.** All of these particles are respirable. Handle them in a closed box with a **P100/FFP3 mask** ($20–40) and
   nitrile gloves, as `BENCH_PLAN.md` requires.

---

## 6. Cuvettes, mechanics, optics, beam dumps, enclosure

### 6.1 Cuvette [SNIPPET]

**Search:** "10 mm fluorescence quartz cuvette 4 windows PTFE stopper", "macro cuvette 3.5 mL stopper".

| Option | Price |
|---|---|
| eBay generic 10 mm, 3.5 mL quartz with PTFE stopper | **$26** |
| eCuvettes QS29 NIR quartz with PTFE cover | **$20–46** |
| AliExpress 10 mm fluorescence (4–5 windows) | **~$80** |
| Thorlabs CV10Q3500FS (stopper, 2-pack) | **$118** |
| Thorlabs CV10Q35FA (stopper, 4-polished, 2-pack) | **$178** |
| Quark Photonics 21FL | **$316** |

- **Minimum spec:** 10 mm path, **4 polished windows** (beam in and out, camera, side illumination), PTFE stopper, inner 10×10 mm.
- Optical-glass cuvettes (~340–2500 nm) work for 405–1550 nm and are cheaper. Quartz has lower bulk absorption and less
  fluorescence under 405 nm, which matters if you image fluorescence (DIY-3).
- **Red flags:** "2 windows" (the 2 frosted sides block side imaging), "quartz" that is really glass, and chipped seams.

### 6.2 Breadboard or rails

| Option | Price [SNIPPET unless noted] | Note |
|---|---|---|
| **2020 aluminium extrusion** + 3D-printed mounts | ~$30–80 total [ESTIMATE] | Adequate for these low-NA, mm-scale beams. Fasten to a heavy base |
| Thorlabs MB3045U/M (300×450 mm, M6) | **$244** new; **$149–200** used on eBay | Removes most alignment pain |
| AliExpress kinematic 1" mirror mounts | **$28–35** | Pitch drift is common. Lock them after alignment |
| AliExpress posts and post holders | ~$5–15 each [ESTIMATE] | – |
| Thorlabs 30 mm cage parts | Expensive (e.g. CXY1A XY lens mount **$216**) | Buy only the critical pieces |

**Practical split:** cheap mechanics, **specialist key optics**.

### 6.3 Lenses and mirrors [SNIPPET]

- **Thorlabs LA1509-A** (N-BK7, Ø1", f = 100 mm, AR 350–700 nm): **$39** (uncoated LA1509: $25). AliExpress Ø1" N-BK7 PCX:
  **~$32**. Specialist lenses cost **about the same** as marketplace ones, so buy the trap lens and expander lenses from Thorlabs or
  Edmund (traceable focal length and coating). Edmund Ø25 mm f = 100 mm NIR-coated: $47.50.
- **Beam expander:** eBay/AliExpress "X5 beam expander 405–1064 nm": **$71–75** (label-only spec). Alternatively build a Galilean
  pair from Thorlabs lenses (e.g. f = −25 mm + f = 125 mm) for ~$60–100 [ESTIMATE]. Thorlabs fixed achromatic expanders cost
  several hundred dollars [MEMORY].
- **Mirrors:** use **dielectric or protected-aluminium** mirrors rated at your wavelength.
- **Red flags: optics**
  - **Silver mirrors** (and Thorlabs' silver-coated galvo option, rated from 500 nm) reflect poorly at 405 nm.
  - Cheap "laser mirrors" with no reflectance curve.
  - Plastic lenses near W-level beams.
  - **Photographic ND filters** used as laser attenuators: they are uncalibrated at laser lines, often transparent in the NIR, and
    may burn. Use absorptive glass NDs rated for the power.

### 6.4 Beam profiling (most important for B1 accuracy)

- **Camera method:** a bare camera sensor behind calibrated ND glass, at very low power.
- **Knife-edge method:** a razor blade on a micrometer stage (AliExpress XY stage ~$20–40; Thorlabs $100–300 [ESTIMATE]) plus the
  power meter.

### 6.5 Beam dumps [SNIPPET]

| Option | Price | Coverage |
|---|---|---|
| Thorlabs **LB1** | **$63** | 400 nm–2 µm, 10 W, covers 405–1550 |
| Thorlabs **BT610** beam trap | **$376** | 400 nm–2.5 µm, 30 W |

- **Red flag:** **black-anodised aluminium reflects strongly in the NIR**. One study measured ~66 % average NIR reflectance, and
  eevblog users confirm that "black anodize is not black in the SWIR".
- A DIY dump made from black-anodised heatsink fins is **not safe at 808, 980, 1064 or 1550 nm**, and its dye can bleach at
  W-level 405–450 nm. Use rated dumps for every W-level beam.

### 6.6 Enclosure and interlock

- **Enclosure:** opaque panels (aluminium, painted plywood, or black ABS/HDPE). Do not use clear or orange acrylic as a "laser
  window" unless it carries an EN 207 / EN 12254 rating at your wavelength. **Engraver-lid orange acrylic is not certified.**
- **Interlock:** use a **safety-rated door switch**, for example a coded-magnet type such as Schmersal BNS. Lasermet sells
  laser-specific dual-channel switches. Feed it into a safety relay that **removes driver power**, plus a key switch, an e-stop and
  an emission indicator.
- Rough cost: **$50–200** for the interlock parts [ESTIMATE; Pilz/Schmersal-class parts used are cheaper]. Warning signs: $5–15.
- These parts belong on the reputable-vendor list.

### 6.7 IR alignment aids [SNIPPET]

- Thorlabs **VRC2** (400–640 nm and 800–1700 nm) or **VRC4** (790–840 nm, 870–1070 nm, 1500–1590 nm): **$101** each.
- **Red flags:**
  - Cheap "IR viewer" scopes and phone cameras use silicon sensors, which **cannot see 1550 nm**.
  - Generic up-conversion cards ($10–30, eBay) are less sensitive, and some need "charging" with visible light.

---

## 7. Galvo scanners, DACs, software (DIY-2)

### 7.1 ILDA galvo sets [SNIPPET]

**Search:** "20Kpps galvo scanner set ILDA closed loop", "30kpps galvanometer set ILDA", "40K galvo 3D laser printing".

| Class | Price | Notes |
|---|---|---|
| 20 kpps sets ("Wonsung", generic) | **$95–210** | Typical spec: mirror **7 × 11 × 0.6 mm**; **±5 V** differential input; ±15 V supply (+1.0 A / −0.6 A); "20 kpps @ 20°, 22 @ 15°, 25 @ 10°, **30 kpps @ 8°**, 35 @ 5°" |
| 30 kpps | **$94–515** | Higher prices are for larger mirrors |
| 40 kpps | **$355–796** | ±24 V drivers |
| Thorlabs **GVS012** 2-axis (10 mm beam, silver, ±20° mech.) | **$3,785** | Small-angle (±0.2°) step response **400 µs**. Order the coating that covers 405 nm |
| Donor **RGB ILDA projector** ("2–3 W RGB animation laser ILDA") | **$180–220** (eBay) | Includes galvos, RGB diodes, ILDA input. Power claims are typically inflated. Combining a 405 nm trap beam into it needs the enclosure redesigned around it |

**What actually matters for a trap display** [ESTIMATE]:

- A 1 cm image at f = 125 mm needs only **±2.3° optical (±1.15° mechanical)** deflection, which is the small-step regime.
- The particle, not the galvo, limits speed. BYU reports >1.8 m/s and ~2 m/s air-relative control (`R5`). At f = 125 mm, 2 m/s is
  only 16 rad/s of optical sweep.
- So the "kpps" rating barely matters. Choose on:
  1. **mirror aperture** larger than the beam (4–6 mm beam on 7 mm mirrors);
  2. **mirror coating reflective at 405 nm**. Many show galvos are coated for 440–660 nm RGB and are listed as "380–700 nm" or
     "400–700 nm"; ask for the curve;
  3. **low overshoot / ringing**, since jerks can drop the particle;
  4. **low drift and noise**.
- "kpps" is quoted against the ILDA test pattern at a stated angle (e.g. 30 kpps @ 8°). The ILDA test is a visual
  no-deformation criterion, not a bandwidth [SNIPPET: Photonlexicon]. **A kpps figure with no angle is a red flag.**

### 7.2 DACs [SNIPPET]

| DAC | Price | Notes |
|---|---|---|
| **Helios** (USB, open-source hardware and SDK in C++/C#/Python) | **$99–114** | **12-bit X/Y** (validated), 65.5 kpps, ≤4095 points/frame. Python SDK fits a camera-feedback loop. **HeliosPRO** is 16-bit (price not captured) |
| **Ether Dream 4** (Ethernet) | **$229** bare / **$289** cased | – |
| **DIY ESP32** | Parts ~$15–40 [ESTIMATE] | See below |
| **Teensy** | – | Teensy 4.x has **no DAC** and Teensy 3.6 (which had 12-bit DACs) is discontinued [MEMORY]. Use an external SPI DAC |

DIY ESP32 projects:

- **GalvOS** (ESP32-S3, 16-bit **DAC8562**, speaks the Ether Dream and Helios protocols).
- **ILDAWaveX16** (ESP32-S3, 16-bit 8-channel DAC, ILDA DB25, SD playback).
- **bbLaser**, **esp32-galvo**, **OpenILDA** (Raspberry Pi), and the Instructables "Arduino laser show with real galvos" (ESP32 + 3×
  **MCP4922** 12-bit dual DACs).

Notes on DAC design:

- The ESP32's built-in DAC is 8-bit and too coarse. ILDA needs **bipolar ±5 V differential** signals, so an op-amp stage after a
  0–Vref DAC is required.
- **Resolution** [ESTIMATE]: a 1 cm image uses only ~6–12 % of a typical ±20° galvo range. A **12-bit DAC gives ~20–40 µm
  steps** across the image, coarser than BYU's 10 µm image points. **Use 16-bit, or reduce the analog gain** so the 1 cm field
  spans most of the DAC range.

### 7.3 Software [SNIPPET]

- **LaserShowGen**: free tier, or Pro for **$29**. Windows, macOS, Linux. Works with Helios.
- **Laserworld Showeditor FREE**.
- **LZR**: open-source libraries.
- **OpenILDA**: Raspberry Pi.

For a trap display, a **Python script on the Helios SDK** or ESP32 firmware that streams a smoothed (low-jerk) point list is more
useful than show software.

---

## 8. 1550 nm components (DIY-4)

### 8.1 Seed, amplifier and fibre parts [SNIPPET]

| Item | Search | Price | Minimum spec / notes |
|---|---|---|---|
| **DFB seed** | "1550nm DFB butterfly laser 10mW isolator FC/APC", "1550nm DFB laser source benchtop" | Butterfly 10 mW DWDM DFB with isolator and TEC, FC/APC: **from $620** (fiber-mart). AeroDiode 10/20 mW: $1,445. All-inclusive DFB system: **$3,990**. AliExpress butterfly sources and drivers exist, price not captured | Linewidth is irrelevant to photophoresis. A narrow DFB in a W-class EDFA risks **SBS**: check the EDFA's seed requirement |
| **Cheap seed alternative** | "handheld fiber optic light source 1310/1550 FP" | **$150–300** (FS.com FOLS-201 $189, >−6 dBm) | A Fabry–Perot (FP) laser is spectrally broad, so it suppresses SBS. **Check the EDFA's minimum input power** (often ≥ −5 to 0 dBm) [MEMORY] |
| **EDFA 1 W (30 dBm)** | "EYDFA-C-HP-BA-30 desktop", "1W C-band EDFA" | **$2,256** (CivilLaser desktop) | Single output, input/output isolators, power monitor, shutdown on input loss |
| **EDFA 2 W (33 dBm)** | – | **$5,500–7,700** (L-band SM / PM versions seen) | – |
| **EDFA 5 W (37 dBm)** | "37dBm 5W EDFA booster" | **$4,298** module / **$5,764** desktop (CivilLaser); **$4,421** benchtop (Agiltron); LD-PD and Box Optronics on request | – |
| *Marketplace "EDFA"* | Alibaba / AliExpress | **$100–2,500** | Mostly **CATV / FTTH multi-port** amplifiers (e.g. "32×20 dBm" = 32 outputs of 100 mW). The headline dBm is **total power split across ports**. **Not a 1–5 W single beam** unless explicitly single-port |
| **1×2 splitter** (50:50, rated W-level) | "high power fused coupler 1550 2W 50:50" | ~$30–150 [ESTIMATE] | Power rating must exceed the amplifier output |
| **Isolator** | "1550 polarization insensitive isolator 2W", "high power isolator 10W" | **$164** (2 W, WDMQuest); **$319–399** (10 W, oeMarket). Standard isolators are often **0.3 W** (GKER TPI) | One per opposed head, rated above the beam power |
| **Fibre collimator** | "1550 FC/APC collimator high power" | Thorlabs GRIN 50-1550A-APC: **$133**. Aspheric F240APC-1550 (f = 8.18 mm, NA 0.49): **~$262**. Newport F-C5-F2-1550: $255 | Check the **power rating**. Epoxy-bonded GRIN collimators are often rated well below 1 W [MEMORY] |
| **Connectors / cleaning** | "fiber inspection scope", "expanded beam connector high power" | Scopes and cleaners: $20–200 [ESTIMATE] | Standard connectors are **rated ~0.5 W and burn at higher power if dirty**. Expanded-beam connectors are ~5 W [SNIPPET: Agiltron EDFA spec]. Dirty connectors can also start a **fibre fuse**. Prefer fusion splices at the high-power end |

### 8.2 Vortex phase plates (LG01) [SNIPPET]

| Product | 1550 nm? | Price | Polarisation |
|---|---|---|---|
| Zoko Optics **SPP-1550-1-S11** (fused silica, charge 1, 11 mm) | yes | **$846** | Independent (true spiral phase plate) |
| LSO / VIAVI **VPP-m1550** (10×10 mm aperture) | yes | **$2,399** | Independent |
| Thorlabs **WPV10L** m = 1 zero-order vortex half-wave retarder (LCP) | a 1550 version exists | ~**$1,232** for sibling wavelengths; 1550 price not confirmed | **Dependent.** A q-plate-type retarder needs circular input and output polarisation filtering. With a non-PM EDFA chain the output is mixed |
| LBTEK **VR1-1550** polymer vortex retarder | yes | **$880** | Dependent (as above) |
| Edmund diffractive vortex plates | **no** (only 488/515/532 nm and 1030 nm) | 10 mm: **$1,060**; 25.4 mm: **$4,892–4,990** | – |
| Holo/Or polymer-on-glass DOE vortex | catalogue | Quote only | – |

- **Minimum:** 2 plates (one per head), charge 1 at **1550 nm**, aperture larger than the collimated beam. Place them in the
  small (few-mm) beam **before** the large expander.
- Prefer **spiral phase plates** (Zoko or LSO) unless the whole chain is polarisation-maintaining.
- Ask for the **CW damage threshold** at W-level for polymer and LCP parts. Not found.

### 8.3 Large final lenses (100–150 mm aperture)

Sizing [ESTIMATE]: focusing to a ~20–50 µm waist at 1.0–1.5 m needs NA ≈ 0.02–0.05, which is a **~50–125 mm beam** at the lens.
So "100–150 mm lenses" means **aperture**.

| Option | Price [SNIPPET] |
|---|---|
| Ø100 mm, f ≈ 1000 mm BK7 plano-convex from a specialist | **~$325** |
| OptoSigma SLB-100-1000PIR1 (IR-coated) | Listed, price not captured |
| Edmund Ø100 mm f = 1000 PCX | Not found in snippets |
| AliExpress Ø70 mm f = 1000 mm BK7 | $26 |
| AliExpress Ø100 mm condensers | **$12–25**, but **f ≈ 135–150 mm**, uncoated |

- **Red flags:** uncoated large lenses reflect ~8 % back toward the fibre, so isolators are mandatory. Acrylic (PMMA) Fresnel
  lenses have NIR absorption bands and poor wavefronts [MEMORY]. Visible-coated lenses reflect more at 1550 nm.

---

## 9. Phosphor and glow powders (DIY-3) [SNIPPET]

| Material | Sources | Size | Price |
|---|---|---|---|
| **BaSi₂O₂N₂:Eu²⁺ ("cyan" oxynitride, ~495 nm)** | **Stanford Advanced Materials** "Oxynitride LED phosphor powder", peak **490 ± 1 nm**; **Edgetech NO-490** (495 ± 2 nm, "full spectrum"); Yuji International, MSE Supplies | SAM: **D50 15 ± 2 µm** | SAM **from $100**. Alibaba "cyan phosphor" **$39–45 / kg** (MOQ; chemistry unverified) |
| **β-SiAlON:Eu (green, ~535–540 nm)** | Denka **ALONBRIGHT** (e.g. GR-MW540K: an industrial grade, not retail); Chinese makers via Alibaba (unverified) | Patents and specs: **D50 ~7–20 µm**; some commercial grades **20–50 µm** | Not captured for small quantities |
| **CaAlSiN₃:Eu (red, ~630–660 nm)** | AliExpress "1113 structure CaAlSiN₃:Eu nitride 660 nm red phosphor" | – | **$50 / 5 g** |
| | SAM nitride (YG630/YG660) | **D50 7–18 µm** / 13 ± 2 µm | Quote |
| LED phosphor sample kit (Ce:YAG yellow + green + nitride red, 10 g) | AliExpress | – | **~$31** |
| **SrAl₂O₄:Eu,Dy (glow / afterglow)** | Alibaba / made-in-china / Technoglow | Standard grades **~20–100 µm**; finer grades (5–15 µm) are special order and dimmer [SNIPPET + MEMORY] | **$10–50 / kg** (1 kg MOQ) |
| **Fluorescent microspheres** | **Cospheric FM-series** (FMG, FMB, FMY, FMV, FMO, FMCE), 1–5 µm, 1.3 g/cc, amino-formaldehyde, **dry powder, UV-excited**. Cospheric also sells an air-dispersible 2–3 µm fluorescent tracer | 1–5 µm | **$148 / 500 mg** each |

Notes:

- **Glow powder:** ask for a **coated / water-resistant** grade, since uncoated SrAl₂O₄ hydrolyses.
- **Fluorescent microspheres:** **405 nm excitation is not confirmed**. Test before ordering a full set.
- **Excitation and detection kit:**
  - a **true 405 nm** LED or torch ($5–20). Many "UV torches" are 395 nm. **Red flag: no stated peak.**
  - **long-pass filters** (≥420–450 nm, $10–100);
  - optionally a **USB mini spectrometer** (~$150–400 [ESTIMATE]) to confirm emission peaks (cyan ~495, green ~540, red ~630–660)
    and so the **identity** of marketplace powders.

**Red flags: phosphors**

1. A **marketplace label is not a chemistry.** "Cyan phosphor" may be a silicate or a blend. Check the emission peak and FWHM. The
   reference BaSi₂O₂N₂:Eu has a ~495 nm peak and **~32 nm FWHM** [SNIPPET].
2. **LED phosphors are coarse** (D50 10–20+ µm). The 2–10 µm fraction must be **classified** by sedimentation, sieving or an
   ultrasonic sieve. Expect low yield.
3. "Glow-in-the-dark" (afterglow) and "fluorescent" (prompt emission) are different properties. B4 needs prompt emission per
   absorbed watt.
4. **Organic fluorescent pigments** ("UV neon powder") **photobleach** under strong 405 nm light.
5. Inhalation safety applies as for all fine powders.

---

## 10. Hobbyist replications of the BYU optical trap display

**Finding: I found no documented hobbyist (non-university) build of a working photophoretic OTD** on YouTube, Hackaday,
Hackaday.io, GitHub or Reddit search results. Hackaday has an "optical-trap-display" tag, but it was blocked, and its covered
articles appear to be BYU news, e.g. "Projecting Moving Images In Air With Lasers", 17 May 2021.

Related projects that are **not** photophoretic OTDs:

- Ted Yapo's "Mid-air Laser Image Display" on Hackaday.io (air-scatter, simulated, not built).
- Mitxela's POV candle (spinning LEDs).
- ESP32 galvo projectors (bbLaser, GalvOS).
- DVD-pickup optical *tweezers* (liquid-phase, gradient force).

**Closest "accessible" builds are academic but deliberately low-cost** [SNIPPET]:

- **BYU miniature automatic photophoretic trapping rig.** JoVE protocol "Fabrication and Testing of Miniature Automatic
  Photophoretic Trapping Rigs" (Barton et al.; *RSI* 92, 103002, 2021).
  - Rig: **laser-cut ¼" wood**, a **3D-printed holder for a 30 mm lens**, a microcontroller, and an **electromagnet "tapper" that
    drops particles** through the focus.
  - Laser: **500 mW 405 nm diode**, tested at 10–500 mW.
  - Related work: a **125 mm biconvex lens** and a **two-axis galvo with 10 mm Thorlabs mirrors**.
  - Designed to be built "within 2 hours" to democratise trap research.
  - Throughput is ~250 trials/hour (`R5`).
- **Cal Poly (X. Jin group).** Undergraduate senior projects and theses (Ababseh; Childers; Garcia 2025) used an **acrylic
  enclosure, a biconvex lens and an adjustable-focus 405 nm module**. Results:
  - best capture at **f ≈ 80–160 mm**;
  - 405, 532 and 630 nm compared;
  - a **retro-reflector gave ~3× longer trapping times**.
  This confirms that hobby-grade 405 nm modules can trap.
- **BYU "Hunt for the Hologram"** classroom "UFO" trap kits (2023–25) crowdsource particle screening. Parts list not found.
- **BYU *Nature* 2018** (`R5`):
  - a **125 mm** trap lens;
  - x/y galvos;
  - microcontroller drive;
  - a 405 nm trap beam plus collinear RGB lasers;
  - a **cellulose** particle.
  Early prototypes used 3–4 W of 532 nm from a 10 W Verdi.

**Implication for DIY-2** [ESTIMATE]: a $600–1,500 build is plausible (BOM below). Expect to spend most of the effort on
**particle loading and trap reliability**, not on scanning. Start with the JoVE-style static rig (no galvos), then add galvos.

---

## 11. Legal and regulatory notes (brief; not legal advice)

**USA**

- **Federal:** FDA/CDRH regulates **manufacturers, importers and dealers** of laser products (21 CFR 1040.10/1040.11), not private
  possession.
  - Laser products include components intended for incorporation.
  - **"Demonstration" laser products, which include light shows and display devices, are limited to Class IIIa unless a CDRH
    variance is approved.** That requires a product report (Form 3632), a show report (Form 3640) and a variance application (Form
    3147).
  - A DIY-2 display **shown to other people** is arguably a demonstration laser product. Read Laser Notice 51/55 and the "Laser
    Light Shows" pages before demonstrating it publicly.
- **Imports:** FDA **Import Alert 95-04** allows detention without examination of non-compliant laser pointers, light-show
  projectors and similar products from 224 red-listed firms. Indicators include >5 mW output, no certification label and no
  warning logotype. Marketplace shipments of modules or projectors can be **refused at the border** [SNIPPET]. Domestic stock or
  reputable US vendors avoid this.
- **States:** **Texas** (25 TAC §289.301) requires **registration** of persons who possess or use Class 3B/4 lasers in healing
  arts, industrial, academic or R&D settings and laser services. Whether a private hobbyist falls under it is **unclear** from the
  text seen: check. Other states regulate mainly medical lasers and shows.
- **Federal crime:** aiming a laser at an aircraft is a federal crime (18 U.S.C. 39A) [MEMORY].

**EU / UK**

- No general ban on **owning** Class 3B/4 lasers. Consumer products must be **Class 1 or 2** (EN 50689:2021 with
  EN 60825-1/A11, mandatory from 2023).
- Market surveillance (UK OPSS, EU customs) targets high-power "pointers". Workplace use falls under Directive 2006/25/EC.
- The **UK** has no ownership offence. It has the Laser Misuse (Vehicles) Act 2018 and product-safety law on sales.
- **Germany** prohibits selling pointers >5 mW. BfS announced **stricter pointer rules in 2024** [SNIPPET].

**Other countries**

- **Switzerland** (since 1 June 2019, O-NIRSA / V-NISSG art. 22–23) bans **import, possession and use of laser pointers** of
  classes 1M, 2, 2M, 3R, 3B and 4, and of unclassified pointers. Lab modules are not "pointers", but check how a customs officer
  would classify a handheld-looking module.
- **Australia:** handheld lasers >1 mW are **prohibited weapons** in most states. Import of laser pointers >1 mW needs permission
  (ARPANSA / Border Force).
- **New Zealand:** import of "high-power laser pointers" (handheld, battery, >1 mW) needs Director-General of Health consent.

**Practical rule.** Buy **mains-powered, non-handheld modules with class labels**, keep invoices, and do not ship anything that
looks like a pointer into AU, NZ or CH. Have a local laser-safety officer or club review the rig, as `BENCH_PLAN.md` suggests.

---

## 12. MUST buy from a reputable or specialist vendor

1. **Laser safety eyewear.** EN 207 (with a test-house mark) or ANSI Z136-labelled, with a **published transmission curve**,
   covering **every** wavelength in the room: Thorlabs, LaserVision, Kentek, Phillips, Laser Safety Industries, or at minimum a
   vendor that tests (J Tech, Survival Laser). One good pair per person, plus a guest pair.
2. **Thermal power meter.** At least one **calibrated** thermopile (new, or used Ophir/Thorlabs/Coherent with a known calibration
   date). Use cheap meters only for relative checks.
3. **Beam dumps** for W-level and NIR beams (Thorlabs LB1/BT610 or equivalent). **No black-anodised DIY dumps for NIR.**
4. **Interlock components:** safety-rated switch, relay, key switch and e-stop.
5. **Laser diode drivers:** constant current, current-limited, soft start. Hobby-vendor drivers (OdicForce, Laserland, DTR-type
   X-Drive) are acceptable. Unbranded no-spec boards are not.
6. **Quantitative reference particles for B1:** glassy carbon (Thermo/Sigma/SPI) and silica tracers (Cospheric, Whitehouse,
   Polysciences), **with stated size data**. Toner and marketplace "microspheres" are practice material only.
7. **All W-level 1550 nm fibre parts:** EDFA, isolators, couplers, collimators and connectors, from vendors that state **power
   ratings**.
8. **Vortex phase plates** (Zoko, LSO/VIAVI, Thorlabs, LBTEK, Holo/Or). There is no credible cheap source.
9. **Trap and expander lenses.** Thorlabs and Edmund cost about the same as AliExpress at Ø1".
10. **A camera with known frame timing** for quantitative velocimetry (machine-vision class: Basler, FLIR, or Raspberry Pi GS with
    verified intervals).

**Fine to buy cheap** (verify on arrival): mechanics (extrusion, posts, mounts), enclosure panels, LEDs, cuvettes (inspect the
windows), low-power mirrors (with a stated coating), galvos for DIY-2, DIY DACs, toner, phosphor screening kits, and stage
micrometers.

---

## 13. Consolidated red-flag list

| # | Red flag | Where it bites |
|---|---|---|
| 1 | Eyewear with a printed OD but **no LB rating, test-house mark or transmission curve**; multi-band "OD 7+" for $10–30; UV eyewear ending at **400 nm** | DIY-1/2/4 |
| 2 | Laser power quoted as **electrical** W ("40 W" = 5.5 W optical), or impossible mW claims | All |
| 3 | Diode "modules" **without a driver**, or with a constant-voltage supply; drivers whose **TTL logic is unknown** or that lase when TTL floats | DIY-1/2 |
| 4 | **Compressed-spot / FAC engraver heads** used as collimated sources; sealed Class 1 engravers ("A1 Pro") bought as beam sources | DIY-1 |
| 5 | Cheap **DPSS with 808 nm leakage**, and eyewear that does not cover it | DIY-1 |
| 6 | Power meters with no sensor model, calibration or density limit; photodiode meters used at W-level | DIY-1/4 |
| 7 | "High-fps" cameras that are **rolling-shutter, interpolated or compressed**, or quote fps only at tiny ROIs | DIY-1 |
| 8 | **"Microspheres" with a size *range* but no distribution / CV / SEM**; Janus-coated spheres; dried suspensions (agglomerates) | DIY-1 |
| 9 | **Toner as a reference particle** (wax, Tg ~55–65 °C, magnetite, irregular) | DIY-1 |
| 10 | Galvo speed with **no angle** (kpps @ ?°); mirrors **not reflective at 405 nm**; mirror smaller than the beam | DIY-2 |
| 11 | 8-bit DAC (ESP32 internal) for a 1 cm field; no bipolar ±5 V stage | DIY-2 |
| 12 | **Black-anodised "beam dumps"** in the NIR; photographic ND filters as attenuators | All |
| 13 | Marketplace **"EDFA" = multi-port CATV** (total power split over 8–32 ports); no input-loss shutdown; no seed-power spec | DIY-4 |
| 14 | Standard FC/APC connectors and GRIN collimators at **≥ 0.5–1 W**; dirty connectors (fibre fuse) | DIY-4 |
| 15 | **Polarisation-dependent vortex retarders** in a non-PM chain; polymer optics with unknown CW damage threshold | DIY-4 |
| 16 | "IR viewers" that cannot see 1550 nm | DIY-4 |
| 17 | Phosphor "cyan / green / red" labels without an **emission spectrum and D50**; "405 nm" UV torches that are 395 nm | DIY-3 |
| 18 | Suppliers that will not sell to individuals (Sigma-Aldrich; often Fisher/Thermo). Plan an institutional or business route, or SPI/Cospheric | DIY-1 |

---

## 14. BOM tables per stage

Prices are USD, from [SNIPPET]s unless marked [E] (estimate) or [M] (memory). Quantity is 1 unless stated.

### DIY-1: photophoretic velocimetry (B1)

| # | Item | Minimum spec | Where (search keywords) | Price range |
|---|---|---|---|---|
| 1 | Laser diode (pick one) | 445 nm **NDB7875** 1.6–2 W in a copper module, glass G-2 lens | eBay / DTR-type sellers ("NDB7875 copper module G-2") | $65–96 |
| 1a | ...or 405 nm 0.5–1 W | With a separate TTL driver | OdicForce, Laserland, Endurance | £45 (500 mW) – $495 (1.7 W) |
| 1b | ...or 808 nm ~1 W | TTL, focusable | AliExpress OXLasers / Amazon / Laserland 3380 | $47–92 |
| 2 | Driver | Constant current, current limit ≤ diode rating, TTL + analog, soft start | "X-Drive"/SXD, OdicForce 0–3.2 A TTL, Laserland | $15–45 |
| 3 | Heatsink + fan + 12 V PSU | Diode case temperature < 35 °C at full power | Marketplace | $20–40 [E] |
| 4 | Beam expander / collimation | 2×–5× Galilean to a 2–4 mm beam; iris | Thorlabs lens pair (−25/+125 mm) or eBay "X5 beam expander" | $60–100 (Thorlabs pair) [E]; $71–75 (eBay) |
| 5 | Mirrors ×2 + kinematic mounts ×2 | Dielectric for your wavelength, Ø1" | AliExpress / Thorlabs | $28–35 per mount; $10–60 per mirror [E] |
| 6 | Base | Breadboard 300×450 M6, or 2020 extrusion | Thorlabs MB3045U/M; extrusion | $150–244; $30–80 [E] |
| 7 | Posts, holders, lens mounts | Ø1" | AliExpress | $50–120 [E] |
| 8 | **Thermal power meter** | Thermopile ≥3 W, aperture ≥9.5 mm, calibrated | Used Ophir 3A ($199–262) + used Nova/Juno ($300–500) / Juno+ new ($834); or Thorlabs PM16-405 / PM16-425 ($1,343) | **$450–850 used**; $1,000–1,350 new |
| 9 | Beam-profiling aids | Razor + micrometer stage (knife edge); absorptive ND glass | AliExpress stage; Thorlabs ND | $20–40 stage; $60–150 ND [E/M] |
| 10 | **Cuvette** | 10 mm, 4 polished windows, PTFE stopper | eBay ($26), eCuvettes ($20–46), AliExpress ($80), Thorlabs ($118–178 / 2) | $26–180 |
| 11 | **Camera** | Global shutter, ≥200–500 fps at ≥640×400, known frame timing | **Basler acA720-520um** (525 fps); or Raspberry Pi GS + Pi 5 (60–536 fps by ROI); or Arducam OV9281 (210 fps) | $379–433; ~$120–150 [M]; $39–65 |
| 12 | Imaging lens | 1–2× (3.5–7 µm/px), WD ≥ 80 mm, ideally telecentric | ZLKC telecentric 1×/2× ($166–176); 0.7–4.5× zoom ($60–100); Edmund CompactTL ($645–705) | $60–705 |
| 13 | Stage micrometer + filters | 0.01 mm divisions; long-pass or notch for the laser line | AliExpress; Thorlabs/Edmund | $10–20; $10–150 [E/M] |
| 14 | Side illumination | Dim LED, diffuser | Marketplace | $5–20 [E] |
| 15 | **Beam dump** | Rated ≥ laser power and wavelength | Thorlabs LB1 | $63 |
| 16 | **Enclosure + interlock** | Opaque, interlocked lid that removes driver power; key switch; e-stop; sign | Local materials; Schmersal/Lasermet-class switch; safety relay | $100–350 [E] |
| 17 | **Eyewear ×2** | OD ≥5 / LB5 at the laser line (+808 nm if used) | Thorlabs LG3 ($191); LaserVision F18 ($69–259); Eagle Pair ($45) as spares | $140–400 |
| 18 | **Particles** | Glassy carbon 2–12 µm; black PE ≥10 µm or black PS 3–10 µm; white silica tracers; (toner for practice) | Thermo 038008 ($72 / 10 g) or Sigma 484164 ($114 / 10 g, business only) or SPI ($298 / 100 g); Cospheric BKPMS ($142+); Cospheric silica ($224–367) or Whitehouse (£70); toner ($10–20) | $250–700 |
| 19 | Particle-handling PPE | P100/FFP3, nitrile, closed glove box or acrylic box with HEPA bleed | Marketplace | $60–400 [E] |
| 20 | Anti-static ionizer (optional) | Non-radioactive | Zerostat-type | $100–150 [M] |
| | **Total** | Budget path (Pi GS, hobby meter, extrusion, 2× Eagle Pair + 1 LG3) | | **≈ $1,400–2,000** [E] |
| | | Recommended path (Basler + telecentric, used Ophir, breadboard, 2× LG3, glassy carbon + silica + PE) | | **≈ $2,600–3,600** [E] |

### DIY-2: BYU-style optical trap display

| # | Item | Minimum spec | Where (search keywords) | Price range |
|---|---|---|---|---|
| 1 | 405 nm trap laser | 0.1–1 W, separate constant-current driver, TTL + analog | OdicForce 500 mW + TTL driver (£45); Endurance 1.7 W ($495); NDV7375 bare ($299) + driver | $60–500 |
| 2 | Expander | 2–3× to a 4–6 mm beam (fits 7 mm galvo mirrors) | Thorlabs lens pair | $60–100 [E] |
| 3 | **Galvo set** | ILDA, closed loop, mirrors ≥7 mm, **coating reflective at 405 nm**, ±15/24 V PSU included | AliExpress/Amazon "20Kpps galvo scanner set ILDA" | $95–210 (20–30 k); $355–800 (40 k) |
| 4 | Trap lens | Ø1" plano-convex or biconvex, **f = 100–150 mm** (BYU used 125 mm; Cal Poly best 80–160 mm). Aberration from orientation or tilt per the papers | Thorlabs LA1509-A (f100, $39) or f125/f150 equivalents | $25–50 |
| 5 | DAC / controller | ≥16-bit, or 12-bit with reduced galvo gain; bipolar ±5 V | Helios ($99–114, **12-bit**: turn the driver's size trim down); HeliosPRO (16-bit); ESP32-S3 + DAC8562 (16-bit) or MCP4922 (12-bit) + op-amps (~$15–40 [E]); Ether Dream 4 ($229–289) | $15–289 |
| 6 | Illumination | RGB laser modules 5–50 mW with TTL + dichroic combiners; or LEDs | Laserland/AliExpress; Thorlabs dichroics | $30–120 lasers [E]; $10–30 per dichroic (marketplace) [E] |
| 6a | ...or donor RGB ILDA projector | ILDA in; supplies galvos and RGB | eBay "2W RGB animation laser ILDA" | $180–220 |
| 7 | Trap particles | Toner, graphite, carbon black, nigrosin; black PE 10–20 µm | Toner refill; art or chem hobby; Cospheric | $10–150 |
| 8 | Particle delivery | Tapper or sieve above the focus (JoVE uses an electromagnet) | Solenoid, mesh, 3D print | $10–30 [E] |
| 9 | Camera | Long-exposure photos plus video of the trap | Raspberry Pi GS or a phone, with a 405 nm blocking filter | $0–150 |
| 10 | Mechanics | Mounts, posts, base | As DIY-1 | $100–300 [E] |
| 11 | **Enclosure + interlock + dump** | Opaque, or a **certified 405 nm-blocking** viewing window; interlock; LB1 | As DIY-1 | $160–450 [E] |
| 12 | **Eyewear** | OD ≥5 at ~395–415 nm with **high VLT** (to see the image); plus LG3-type for alignment | Thorlabs / LaserVision / Kentek | $70–400 |
| 13 | Power meter | Reuse from DIY-1 | – | $0 |
| | **Total** | Reusing DIY-1 meter, mechanics, eyewear | | **≈ $600–1,500** [E] (with a Thorlabs GVS galvo instead of ILDA: +$3.8k) |

### DIY-3: phosphor / fluorescent particles

| # | Item | Minimum spec | Where | Price range |
|---|---|---|---|---|
| 1 | Cyan BaSi₂O₂N₂:Eu | Peak 490–495 nm, FWHM ~30–40 nm, D50 stated | SAM (from $100, D50 15 ± 2 µm); Edgetech NO-490; Yuji; Alibaba ($39–45 / kg, MOQ) | $40–150 |
| 2 | β-SiAlON:Eu green | Peak ~535–540 nm, D50 ≤ 15 µm | Alibaba makers; Denka (industrial) | $30–150 [E] |
| 3 | CaAlSiN₃:Eu red | Peak 630–660 nm | AliExpress ($50 / 5 g); SAM (D50 7–18 µm) | $50–150 |
| 4 | LED phosphor kit (screening) | YAG + green + nitride red | AliExpress (10 g) | ~$31 |
| 5 | SrAl₂O₄:Eu,Dy glow | Coated / water-resistant, finest grade available | Alibaba / Technoglow ($10–50 / kg, MOQ 1 kg) | $15–60 |
| 6 | Fluorescent microspheres | 1–5 µm dry; **verify 405 nm excitation** | Cospheric FM series ($148 / 500 mg each) | $148–450 |
| 7 | Excitation | True 405 nm LED or torch; or the DIY-2 laser at mW level | Marketplace | $5–20 |
| 8 | Filters / spectrometer | Long-pass ≥420–450 nm; USB mini spectrometer (optional) | AliExpress / Thorlabs; spectrometer modules | $10–100; $150–400 [E] |
| 9 | Size classification | 20 µm sieve, sedimentation glassware, microscope with stage micrometer | Marketplace | $30–150 [E] |
| 10 | PPE / closed box | As DIY-1 | – | reuse |
| | **Total** | | | **≈ $300–1,200** [E] |

### DIY-4: 1550 nm doughnut pair (B3)

| # | Item | Minimum spec | Where | Price range |
|---|---|---|---|---|
| 1 | Seed | DFB 10–20 mW butterfly with isolator, TEC + driver; **or** a broad FP test source if the EDFA allows it (SBS) | fiber-mart ($620+), AeroDiode/LDS ($1.4–4k); FS.com FOLS-201 ($189) | $190–1,500 (+ driver $50–300 [E]) |
| 2 | **EDFA** | Single-port booster, 1–5 W, input/output isolation, shutdown on input loss, rated input range | CivilLaser 1 W desktop ($2,256); 5 W ($4,298–5,764); Agiltron 5 W ($4,421) | **$2,300–5,900** |
| 3 | 1×2 coupler | 50:50, rated above the EDFA output | Fibre-optics vendors | $30–150 [E] |
| 4 | **Isolators ×2** | ≥2–5 W rated, in front of each head (opposed beams) | WDMQuest 2 W ($164); oeMarket 10 W ($319–399) | $330–800 |
| 5 | **Collimators ×2** | 1550 nm FC/APC, **power-rated**; or splice to bare fibre | Thorlabs ($133–262) / high-power types | $270–1,000 [E] |
| 6 | Fibre hygiene | Inspection scope, cleaners; splices at the high-power end | Marketplace / FS.com | $50–300 [E] |
| 7 | **Vortex plates ×2** | Charge 1 at 1550 nm, polarisation-independent preferred | Zoko SPP-1550-1-S11 ($846 each); LSO VPP-m1550 ($2,399) | $1,700–4,800 |
| 8 | Expander + **large focusing lenses ×2** | Ø100–150 mm, f ≈ 1–1.5 m, NIR AR | Specialist (~$325 per Ø100 f1000); OptoSigma SLB-100-1000PIR1 | $700–1,500 [E] |
| 9 | Mechanics | 2 heads 1–1.5 m apart, rigid rail or table | Extrusion / breadboard | $200–600 [E] |
| 10 | **10 W thermal meter** | ≥10 W, Ø ≥16–25 mm | Thorlabs S425C ($987 + console) / PM16-425 ($1,343); used Ophir 10A [E $200–500] | $300–1,350 |
| 11 | **Beam dumps ×2–3** | Rated to 2 µm, ≥10 W | Thorlabs LB1 ($63); BT610 ($376) | $130–750 |
| 12 | IR viewer cards ×2 | Covers 1500–1590 nm | Thorlabs VRC2 / VRC4 ($101 each) | $200 |
| 13 | **Eyewear** | OD ≥4 (preferably 5+) at 1550 nm; multi-band if 405 nm is also present | Thorlabs LG11 ($430) | $430–900 |
| 14 | Enclosure / curtains + interlock | Whole 1–1.5 m path enclosed or in a controlled room | – | $300–1,000 [E] |
| 15 | Cross-flow source + anemometer | Fan or nozzle; hot-wire anemometer | Marketplace | $50–300 [E] |
| 16 | Camera | Reuse Basler / Pi GS. The mote is seen by scattered illumination; silicon cannot see 1550 | – | reuse |
| | **Total** | 1 W EDFA path | | **≈ $7,000–11,000** [E] |
| | | 5 W EDFA path | | **≈ $10,000–17,000** [E] (consistent with `BENCH_PLAN.md`'s 10–20 k$) |

---

## 15. What I could not verify (gaps)

- **No page could be opened.** No datasheet, transmission curve, calibration spec or terms of sale was read in full. All prices
  are **search snippets** and may be stale, discounted or exclude shipping and VAT.
- **Hobbyist OTD builds:** none found. Hackaday's optical-trap-display tag and the JoVE "Table of Materials" were blocked, so the
  BYU mini-rig's exact parts list and cost are **unverified**.
- **Eyewear:** I did not verify the actual OD curves of Eagle Pair, J Tech or Amazon brands, beyond the vendor claims and one
  blogger's spectrophotometer snippet. The LaserVision filter that maps to 405/445 nm at $69–259 was not identified.
- **Micro-particles:** I did not verify the number-weighted size distributions of glassy-carbon powders, whether Cospheric, SPI
  and Thermo sell to private individuals, or the Polybead black 6 µm price ($1,260 / 5 mL looks high).
- **Phosphors:** I did not verify the chemistry of Alibaba "cyan phosphor", the 405 nm excitation of Cospheric FM spheres, retail
  β-SiAlON pricing, or the availability of fine (≤10 µm) SrAl₂O₄ grades.
- **1550 nm:** no AliExpress single-port W-class EDFA price was captured. I did not verify the CW damage thresholds of polymer/LCP
  vortex retarders, the Thorlabs WPV10L-1550 price, high-power collimator ratings, or the EDFA minimum-input and seed-linewidth
  requirements.
- **Cameras:** the Raspberry Pi GS price is from memory. The strip-ROI frame rates for IMX296 are my extrapolation from the
  published crop figures. Used prices for Blackfly S IMX287 were not captured.
- **Galvos:** I found no measured small-step response or 405 nm mirror reflectance for marketplace ILDA sets.
- **Law:** whether Texas registration applies to private hobbyists, and current EU or German rules beyond pointers, are not
  confirmed. This section is orientation, not legal advice.

---

## Sources (search results used; most pages were not openable)

**Lasers**
- [eBay 405–520 nm TTL driver](https://www.ebay.com/itm/127967380477)
- [OdicForce 500 mW 405 nm + TTL](https://odicforce.com/500mW-405nm-Bluray-Focusing-Laser-Module-12V)
- [OdicForce 0–3.2 A driver](https://odicforce.com/External-Driver-for-515nm-and-520nm-Direct-Green-Laser-Diodes-0-200mW-Supports-TTL-Modulation)
- [Endurance 1.7 W 405 nm](https://www.endurance-lasers.com/products/1-7-watt-1700-mw-diode-violet-405-nm-laser-module)
- [NUBM44 module (eBay)](https://www.ebay.com/itm/171841778046)
- [SXD driver (PicClick)](https://picclick.com/4A-SXD-Super-X-Drive-Laser-Driver-NDB7A75-171690251341.html)
- [Barnett NUBM44](https://barnettunlimited.com/product/nubm44u/)
- [NDB7875 module (eBay)](https://www.ebay.com/itm/173770615725)
- [SPW NDB7875-E](https://spwindustrial.com/445nm-450nm-447nm-1-6w-2w-blue-laser-diode-9mm-nichia-ndb7875-e-tinned-pins/)
- [BeamQ NDV7375](https://beamq.com/nichia-violet-laser-diode-405nm-1200mw-ndv7375-p-1489.html)
- [LDS NDV7375 turnkey](https://shop.laserdiodesource.com/shop/405nm-1200mw-high-stability-scientific-laser)
- [Laserland 405 nm 3350](https://www.laserlands.net/diode-laser-module/405nm-laser-module/3350-405d.html)
- [Edmund 405 nm 1 W fibre-coupled](https://www.edmundoptics.com/p/405nm-1w-fiber-coupled-laser/54185/)
- [Thorlabs L405P150](https://www.thorlabs.com/thorproduct.cfm?partnumber=L405P150)
- [Laser Tree 5 W optical](https://lasertree.com/products/laser-tree-5w-optical-power-laser-engraver-module)
- [Probots 20 W = 5.5 W optical](https://probots.co.in/20w-blue-diode-laser-module-5-5w-optical-450nm-cnc.html)
- [Snapmaker 10 W FAC module](https://us.snapmaker.com/products/snapmaker-10w-high-power-laser-module)
- [Creality Falcon A1 Pro](https://www.crealityfalcon.com/products/falcon-a1-pro-20w-dual-laser-engraver)
- [Tom's Hardware A1 Pro review](https://www.tomshardware.com/maker-stem/creality-falcon-a1-pro-20-watt-review)
- [808 nm module (Amazon)](https://www.amazon.com/Focusable-800mW-1W-Infra-red-Module-Supply/dp/B09WKD69J7)
- [Laserland 808 nm](https://www.laserlands.net/diode-laser-module/808nm-laser-module.html?limit=32&mode=list)
- [AliExpress IR driver board](https://www.aliexpress.com/item/1005002882441935.html)
- [980 nm 1 W module (eBay)](https://www.ebay.com/itm/128018775474)
- [CivilLaser 1064 nm DPSS](https://www.civillaser.com/index.php?main_page=index&cPath=42_49)
- [Arktis 1064 nm](https://www.arktislaser.com/product/RA6-N-1064-nm-DPSS-Laser-System)
- [LPF "5.5 W 450 nm very weak"](https://laserpointerforums.com/threads/5-5w-450nm-blue-laser-very-week.102224/)
- [LPF cheap "10000 mW"](https://laserpointerforums.com/threads/cheap-aliexpress-445nm-10000mw.93899/page-2)
- [LPF IR leakage](https://laserpointerforums.com/threads/testing-ir-leakage-from-green-laser-pointers.107987/)

**Eyewear**
- [J Tech warning](https://jtechphotonics.com/?p=1117)
- [J Tech goggles](https://jtechphotonics.com/?product=laser-safety-goggles-for-445nm-lasers)
- [LPF cheap glasses tested](https://laserpointerforums.com/threads/cheap-safety-glasses-tested.71621/)
- [Whittemore sanity check](https://www.alexwhittemore.com/sanity-checking-some-cheap-laser-safety-glasses/)
- [LightBurn forum](https://forum.lightburnsoftware.com/t/paranoid-about-these-goggles/95756)
- [EN 207 (Wikipedia)](https://en.wikipedia.org/wiki/EN_207)
- [Laser 2000 EN 207/208](https://photonics.laser2000.co.uk/blogs/standards-for-laser-safety-eyewear-en207-en208/)
- [Thorlabs certified glasses](https://www.thorlabs.com/certified-laser-safety-glasses)
- [Thorlabs LG3](https://www.thorlabs.com/item/LG3)
- [Thorlabs LG11](https://www.thorlabs.com/item/LG11)
- [Thorlabs LG10](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=762&pn=LG10)
- [Eagle Pair](https://www.survivallaserusa.com/product/eagle-pair-190-540nm-od6-standard-laser-safety-goggles)
- [LaserVision USA F18](https://lasersafety.com/product/f18-p5g04-5000/)
- [Kentek KBS-20C](https://www.kenteklaserstore.com/kbs-20c-laser-safety-glasses)
- [Phillips DFIU](https://phillips-safety.com/product-category/laser/laser-safety-glasses/dfiu/)
- [LaserPair DIN CERTCO](https://www.amazon.com/Laser-Safety-Glasses-800-Wavelength/dp/B00UKL4LR2)
- [DHS eyewear market survey 2024](https://www.dhs.gov/sites/default/files/2024-07/24_07_31_st_laserprotectiveeyewearmsr.pdf)

**Power meters**
- [LPF hobby LPM history](https://laserpointerforums.com/threads/history-of-the-hobbyist-lpm.83412/)
- [LPM-10W](https://www.shadowlasers.com/products/lpm-10w-laser-power-meter)
- [Ophir 3A-P (eBay)](https://www.ebay.com/itm/196121465484)
- [Ophir 3A](https://www.ophiropt.com/en/f/3a-high-sensitivity-thermopile-sensor)
- [Ophir Juno+](https://www.ophiropt.com/en/f/juno-plus-power-meter)
- [Ophir StarBright](https://www.ophiropt.com/en/f/starbright-power-meter)
- [eBay laser power meters](https://www.ebay.com/b/Industrial-Electrical-Laser-Power-Meters/4678/bn_108382150)
- [Thorlabs PM16-425](https://www.thorlabs.com/thorproduct.cfm?partnumber=PM16-425)
- [Thorlabs thermal sensors](https://www.thorlabs.com/thermal-power-sensors-c-series)
- [Gentec PRONTO-250-EZ](https://www.gentec-eo.com/products/pronto-250-ez-y)

**Cameras and lenses**
- [Raspberry Pi GS camera](https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/)
- [IMX296 crop gist](https://gist.github.com/Hermann-SW/e6049fe1a24fc2b5a53c654e0e9f6b9c)
- [RPi forum GS thread](https://forums.raspberrypi.com/viewtopic.php?t=348642)
- [Arducam OV9281 USB](https://www.uctronics.com/arducam-120fps-global-shutter-usb-camera-board-1mp-720p-ov9281-uvc-webcam-module-with-low-distortion-m12-lens.html)
- [Basler acA720-520um](https://www.baslerweb.com/en-us/shop/aca720-imx287/)
- [FLIR Blackfly S USB3](https://www.edmundoptics.com/f/flir-blackfly-s-usb3-cameras/37234/)
- [Visiondatum IMX287](https://shop.visiondatum.com/products/high-speed-0-4mp-imx287-526fps-usb3-global-shutter-vision-camera)
- [Chronos 1.4](https://www.krontech.ca/product/chronos-1-4-high-speed-camera/)
- [RX100 IV high-frame-rate modes](https://www.cameralabs.com/sony-cyber-shot-rx100-iv-review/2/)
- [iPhone 240 fps](https://www.idownloadblog.com/2017/11/22/how-to-shoot-slo-mo-video-1080p-at-240fps-iphone/)
- [AliExpress 0.7–4.5× zoom](https://www.aliexpress.us/item/3256803574034496.html)
- [Omano OM10K](https://www.microscope.com/omano-om10-zoom-microscope-lens.html)
- [ZLKC telecentric](https://www.aliexpress.us/item/3256809023247983.html)
- [Edmund CompactTL 1×](https://www.edmundoptics.com/p/1x-110mm-wd-compacttl-telecentric-lens/18464/)
- [VA Imaging telecentric](https://va-imaging.com/en-us/products/telecentric-lens-1x-wd110-1-5-coaxial-light-c-mount)

**Particles**
- [Thermo 038008](https://www.thermofisher.com/order/catalog/product/038008.09)
- [Sigma 484164](https://www.sigmaaldrich.com/US/en/product/aldrich/484164)
- [Fisher / Sigma 484164](https://www.fishersci.com/shop/products/carbon-glassy-spherical-powde-1/501868387)
- [SPI Sigradur K spherical](https://www.2spi.com/item/z4204gcps/)
- [Sciencemadness on Sigma to individuals](http://www.sciencemadness.org/talk/viewthread.php?tid=72730)
- [Cospheric black PE](https://www.cospheric.com/BKPMS_polymer_black_paramagnetic_microspheres.htm)
- [Cospheric coated glass](https://www.cospheric.com/Paramagnetic_coated_glass_microspheres)
- [Cospheric Ni hollow glass](https://www.cospheric.com/nickel_plated_glass_spheres/metal_coated_microspheres_beads.htm)
- [Cospheric silica](https://www.cospheric.com/silica_microspheres_beads_powders.htm)
- [Whitehouse silica](https://www.whitehousescientific.com/category/silica-microspheres)
- [Polysciences silica 5 µm](https://polysciences.com/products/silica-microspheres-dry-50m)
- [Polybead black 6 µm](https://gen.store/polybead-black-dyed-microspheres-6-00-m-24293-5/)
- [Bangs dyed PS](https://bangslabs.com/product-category/dyed-polystyrene/dyed-carboxyl-polystyrene/)
- [ACS hollow carbon](https://www.acsmaterial.com/hollow-carbon-spheres.html)
- [IS&T toner size paper](https://www.imaging.org/common/uploaded%20files/pdfs/Papers/1997/RP-0-68/2331.pdf)
- [US7323280 chemically produced toner](https://patents.google.com/patent/US7323280)
- [Cospheric fluorescent FMB](https://www.cospheric.com/FMB_blue_fluorescent_polymer_microspheres_1micron.htm)
- [Cospheric dry tracer](https://www.cospheric.com/fluorescent_dry_tracer_microspheres_1-5um.html)

**Cuvettes, optics, mechanics**
- [eBay quartz cuvette](https://www.ebay.com/p/1639787706)
- [Thorlabs cuvettes](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=5943)
- [Quark cuvette](https://quarkphotonics.au/product/fluorescence-quartz-cuvette-with-ptfe-stopper-10-mm/)
- [eCuvettes QS29](https://ecuvettes.com/product/qs29-10mm-nir-standard-quartz-cuvette-with-ptfe-cover/)
- [AliExpress cuvettes](https://www.aliexpress.com/w/wholesale-quartz-cuvette.html)
- [eBay X5 expander](https://www.ebay.com/itm/267337518304)
- [Thorlabs LB1](https://www.thorlabs.com/item/lb1)
- [Thorlabs beam blocks and traps](https://www.thorlabs.com/NewGroupPage9_PF.cfm?ObjectGroup_ID=1449)
- [Thorlabs MB3045U/M](https://www.thorlabs.com/item/MB3045U_M)
- [Thorlabs LA1509-A](https://www.thorlabs.com/thorproduct.cfm?partnumber=LA1509-A)
- [Thorlabs CXY1A](https://www.thorlabs.com/item/CXY1A)
- [AliExpress kinematic mounts](https://www.aliexpress.com/w/wholesale-kinematic-mount.html)
- [Black-material reflectivity (arXiv)](https://arxiv.org/pdf/1407.8265)
- [eevblog on NIR reflection](https://www.eevblog.com/forum/metrology/minimizing-ir-reflection/)
- [Thorlabs VRC2](https://www.thorlabs.com/item/vrc2)
- [Thorlabs VRC4](https://www.thorlabs.com/thorproduct.cfm?partnumber=VRC4)
- [Lasermet interlock switch](https://www.lasermet.com/laser-safety-products/dual-channel-interlock-switch/)

**Galvos, DACs, software**
- [AliExpress 40 k galvo](https://www.aliexpress.com/w/wholesale-galvo-scanner-40kpps.html)
- [20/30 k galvo (PicClick)](https://picclick.com/20KPPS-30KPPS-laser-scanning-galvo-scanner-ILDA-Closed-261517002270.html)
- [Wonsung 20 k (Amazon)](https://www.amazon.com/Generic-Galvanometer-Optical-Scanner-Including/dp/B01IZPMUPO)
- [laser-parts 20 k spec](http://www.laser-parts.com/20kpps-galvanometer-set.html)
- [Photonlexicon ILDA filtering](https://photonlexicon.com/forums/showthread.php/25301-Analogue-Protection-Filtering-for-ILDA-XY-Galvos)
- [Thorlabs GVS012](https://www.thorlabs.com/item/GVS012)
- [Helios DAC](https://bitlasers.com/helios-laser-dac/)
- [Helios on GitHub](https://github.com/Grix/helios_dac)
- [Ether Dream 4](https://www.xlaser.com/products/ether-dream-4)
- [GalvOS](https://github.com/Andre1Becker/GalvOS)
- [ILDAWaveX16](https://github.com/stanleyondrus/ILDAWaveX16)
- [bbLaser](https://github.com/RealCorebb/bbLaser)
- [esp32-galvo](https://github.com/jeffkub/esp32-galvo)
- [OpenILDA](https://github.com/vanvught/OpenILDA)
- [LZR](https://github.com/brendan-w/lzr)
- [LaserShowGen](https://bitlasers.com/lasershowgen-sw/)
- [Laserworld Showeditor FREE](https://www.showeditor.com/en/tutorials-faq/2-uncategorised/270-laserworld-showeditor-free-free-laser-show-software.html)
- [Instructables Arduino laser show](https://www.instructables.com/Arduino-Laser-Show-With-Real-Galvos/)
- [eBay 2 W RGB ILDA projectors](https://www.ebay.com/b/2w-Rgb-Laser/177022/bn_7023286312)

**1550 nm**
- [CivilLaser 5 W EDFA](https://www.civillaser.com/index.php?main_page=product_info&products_id=2966)
- [CivilLaser 1 W EDFA](https://www.civillaser.com/index.php?main_page=product_info&products_id=2959)
- [CivilLaser 2 W L-band](https://www.civillaser.com/index.php?main_page=product_info&products_id=3012)
- [Agiltron EDFA](https://agiltron.com/product/fiber-optical-amplifier-edfa-1540-1565nm-high-power/)
- [Agiltron EDFA spec (connector ratings)](https://agiltron.com/dlc/specs/EDFA.pdf)
- [Alibaba EDFA](https://www.alibaba.com/showroom/1550nm-edfa-price.html)
- [AliExpress EDFA](https://www.aliexpress.com/w/wholesale-edfa-1550nm.html)
- [fiber-mart DFB](https://www.fiber-mart.com/10mw-1550nm-dwdm-dfb-butterfly-laser-diodes-p-706.html)
- [AeroDiode DFB source](https://shop.laserdiodesource.com/shop/1550nm-10mw-dfb-cw-source-aerodiode)
- [FS.com FOLS-201](https://www.fs.com/products/97568.html)
- [Thorlabs 50-1550A-APC](https://www.thorlabs.com/item/50-1550A-APC)
- [Thorlabs FC/APC collimators](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=1696)
- [WDMQuest isolators](https://wdmquest.com/collections/isolator-1)
- [oeMarket high-power isolator](https://www.oemarket.com/catalog/product_info.php/optical-isolator-high-power-1310-1480-1550nm-p-206)
- [Connector damage paper](https://www.researchgate.net/publication/230873750_High-Power_Effects_in_Damaged_and_Contaminated_Optical_Fiber_Connectors)
- [LSO VPPs](https://lso.viavisolutions.com/product-category/vortex-phase-plates/)
- [Zoko VPP](https://www.zokoptics.com/vortex-phase-plate)
- [Edmund vortex 532 nm](https://www.edmundoptics.com/p/532nm-10mm-square-diffractive-vortex-phase-plate/51194/)
- [Thorlabs vortex retarders](https://www.thorlabs.com/zero-order-vortex-half-wave-retarders)
- [LBTEK VR1](https://en.lbtek.com/product/581?path=148%2F371)
- [Holo/Or vortex](https://www.holoor.co.il/application/optical-vortex-phase-plate-application-notes/)
- [AliExpress Ø100 mm lens](https://www.aliexpress.us/item/2251832772232841.html)
- [OptoSigma SLB-100-1000PIR1](https://www.meetoptics.com/lenses/spherical/plano-convex-lens/s/optosigma/p/SLB-100-1000PIR1)

**Phosphors**
- [SAM oxynitride](https://www.samaterials.com/phosphor-materials/2844-oxynitride-led-phosphor-powder.html)
- [SAM nitride](https://www.samaterials.com/phosphor-materials/2863-nitride-phosphor-powder.html)
- [SAM YG660](https://www.samaterials.com/phosphor-materials/2852-red-nitride-phosphor-powder-yg660.html)
- [Edgetech phosphors](https://www.edge-techind.com/category/Phosphors-117-1.html)
- [Yuji phosphors](https://www.yujiintl.com/phosphor.html)
- [AliExpress CaAlSiN₃](https://www.aliexpress.com/item/1005003611580226.html)
- [Alibaba YAG](https://www.alibaba.com/product-detail/rare-earth-YAG-yellow-led-Phosphor_1600519291926.html)
- [Denka ALONBRIGHT](https://www.denka.co.jp/eng/product/detail_00031/)
- [β-SiAlON patent](https://patents.google.com/patent/US20180002601A1/en)
- [Alibaba SrAl₂O₄](https://www.alibaba.com/product-detail/SrAl2O4-Eu-Dy-Water-Resistant-Harmless_60720566636.html)
- [Technoglow](https://www.technoglowproducts.com/strontium-aluminate/)
- [BaSi₂O₂N₂ paper](https://www.sciencedirect.com/science/article/abs/pii/S0272884220320058)

**Replications**
- [JoVE mini rigs](https://www.jove.com/t/63113/fabrication-testing-miniature-automatic-photophoretic-trapping)
- [RSI 2021 trap rig](https://pubs.aip.org/aip/rsi/article/92/10/103002/955132/Photophoretic-trap-testing-rig-for-volumetric)
- [Cal Poly Ababseh](https://digitalcommons.calpoly.edu/eesp/589/)
- [Cal Poly Garcia](https://digitalcommons.calpoly.edu/theses/2947/)
- [*Nature* 2018](https://www.nature.com/articles/nature25176)
- [*Appl. Opt.* 2019](https://par.nsf.gov/servlets/purl/10141807)
- [Hackaday 2021](https://hackaday.com/2021/05/17/projecting-moving-images-in-air-with-lasers/)
- [Hackaday tag](https://hackaday.com/tag/optical-trap-display/)
- [Ted Yapo mid-air display](https://hackaday.io/project/12889-mid-air-laser-image-display)
- [BYU video](https://www.youtube.com/watch?v=qUSiw87mQck)

**Law**
- [FDA laser light shows](https://www.fda.gov/radiation-emitting-products/home-business-and-entertainment-products/laser-light-shows)
- [FDA Laser Notice 51](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/responsibilities-laser-light-show-projector-manufacturers-dealers-and-distributors-laser-notice-51)
- [FDA laser products](https://www.fda.gov/radiation-emitting-products/home-business-and-entertainment-products/laser-products-and-instruments)
- [Import Alert 95-04](https://www.accessdata.fda.gov/cms_ia/importalert_254.html)
- [Texas 25 TAC 289.301](https://www.dshs.texas.gov/sites/default/files/radiation/pdffiles/Rules/289.301%20Radiation%20Requirements%20for%20Lasers%20and%20IPL%20Devices.pdf)
- [Swiss BAG laser pointers](https://www.bag.admin.ch/en/laser-pointers)
- [ARPANSA](https://www.arpansa.gov.au/news/laser-focus-illegal-imports)
- [NZ Ministry of Health](https://www.health.govt.nz/regulation-legislation/high-power-laser-pointers)
- [UK rules](https://www.theukrules.co.uk/rules/legal/police/faq/weapons/laser-pens/)
- [EU laser regulations](https://www.compliancegate.com/laser-device-regulations-european-union/)
- [BfS 2024](https://www.bfs.de/SharedDocs/Pressemitteilungen/BfS/EN/2024/016.html)
- [International laws](https://www.laserpointersafety.com/rules-general/intllaws/intllaws.html)

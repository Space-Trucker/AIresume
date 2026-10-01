# Order list: what to put in the cart (recommended picks)

**Status.**
- Picks come from `R11_sourcing.md` (search-snippet prices, ±30 %) and its validation notes. Re-check every price and spec before paying.
- Items marked **[spec]** have no verified model: choose one whose datasheet shows the stated spec.
- Three orders, in this sequence. **Do not power any laser until Order 1 is installed and its interlock passes the test in `diy2_control/ELECTRONICS.md` §1.**

---

## Order 1: safety kit (DIY-0). About $1.3–2.4k

| ✓ | Item | Pick | Qty | Est. price | Where |
|---|---|---|---|---|---|
| ☐ | Laser safety glasses (alignment, 405/445 nm) | Thorlabs **LG3** (OD 7+ 180–532 nm). Its EN 207 LB rating covers ~1 W CW, so **cap the diode at ≤ 1 W optical** unless your eyewear is rated higher | 2 | $191 each | Thorlabs |
| ☐ | Viewing glasses for the DIY-2 glyph | **[spec]** OD ≥ 5 at 395–415 nm, visible transmission ≥ 50 %, EN 207 marked | 1 | $70–250 | LaserVision / Thorlabs / Kentek |
| ☐ | Safety relay, dual channel, manual reset | Omron G9SA-301, Pilz PNOZ s3, or Phoenix PSR (used is fine if tested) | 1 | $80–250 | Industrial suppliers, eBay |
| ☐ | Lid safety switches | Positive-opening tongue type (Omron D4NS, Schmersal AZ 15) or coded-magnetic. **Not a plain reed or microswitch** | 2 | $30–80 each | Industrial suppliers |
| ☐ | Key switch (key comes out only when OFF), E-stop (positive-opening NC, latching), RESET push button, "LASER ON" lamp | 22 mm panel parts | 1 set | $30–60 | Amazon / AliExpress |
| ☐ | 24 V DC supply for the interlock chain | DIN rail, ≥ 0.5 A | 1 | $20–40 | Amazon |
| ☐ | Beam dumps | Thorlabs **LB1** (400 nm–2 µm, 10 W) | 2 | $63 each | Thorlabs |
| ☐ | Thermal power meter | Used **Ophir 3A** head + Nova/Juno display (check that they are compatible and the head is unburned), or Thorlabs PM16-405 new | 1 | $450–850 used; $1,343 new | eBay / Thorlabs |
| ☐ | Enclosure | 2020 extrusion frame + opaque black ABS or aluminium panels, ~600×400×400 mm | 1 | $80–200 | Amazon / AliExpress / local |
| ☐ | Laser warning sign, P100/FFP3 masks, nitrile gloves | – | 1 set | $30–60 | Amazon |

---

## Order 2: force-law bench (DIY-1). About $1.4–2.1k

| ✓ | Item | Pick | Qty | Est. price | Where |
|---|---|---|---|---|---|
| ☐ | Laser | Nichia **NDB7875** 445 nm copper module with G-2 glass lens. Run ≤ 1 W optical (eyewear LB) | 1 | $65–96 | eBay / DTR-type sellers |
| ☐ | Driver | Constant current, current limit ≤ diode rating, **TTL + analog**, soft start (OdicForce 0–3.2 A, or X-Drive class) | 1 | $15–45 | OdicForce / eBay |
| ☐ | Heatsink + fan + 12 V supply | Diode case < 35 °C at full power | 1 | $20–40 | Amazon |
| ☐ | Iris + Galilean expander lens pair | Thorlabs negative + positive pair (e.g. f −50 / +100 for 2×) | 1 | $60–120 | Thorlabs |
| ☐ | Cuvette | 10 mm path, **4 polished windows**, PTFE stopper (quartz) | 2 | $26–80 each | eBay / eCuvettes / AliExpress |
| ☐ | Camera | **Basler acA720-520um** (525 fps, global shutter; validated $379–436). Budget: Raspberry Pi Global Shutter + Pi 5 | 1 | $379 / ~$150 | Basler distributors / Pi resellers |
| ☐ | Imaging lens | 2× C-mount telecentric, ~110 mm working distance (ZLKC) | 1 | $166–176 | AliExpress |
| ☐ | Stage micrometer, long-pass filter (blocks 445 nm), dim red LED | – | 1 set | $30–60 | AliExpress |
| ☐ | Knife-edge beam profiler | Razor blade on an XY micrometer stage | 1 | $20–40 | AliExpress |
| ☐ | Glassy carbon spheres | Thermo **038008** (0.4–12 µm, 10 g). Sigma 484164 ships only to businesses | 1 | $72 | Thermo / Fisher (business account may be needed) |
| ☐ | Black polymer spheres | Cospheric **BKPMS** black PE, smallest size offered (≥ 10 µm) | 1 | $142+ | Cospheric |
| ☐ | White silica tracers | Whitehouse 5 µm set, or Cospheric silica | 1 | from £70 / $224 | Whitehouse / Cospheric |
| ☐ | Mechanics | Breadboard (Thorlabs MB3045U/M, used $149–200) or extrusion; posts, holders, 2 mirror mounts, lens mounts | 1 set | $150–400 | eBay / AliExpress |

---

## Order 3: trap display (DIY-2a/2b). About $0.6–1.3k

| ✓ | Item | Pick | Qty | Est. price | Where |
|---|---|---|---|---|---|
| ☐ | Trap laser | For the simulated lens pocket: a **single-mode fibre-coupled** 405 nm source (20–100 mW) + fibre collimator (astigmatism ≤ 0.1 wave). For BYU-style empirical trapping: a 300–500 mW multimode module with a **separate** TTL + analog driver (OdicForce class) | 1 | ~$300–1,500 SM [estimate]; ~$60–150 MM | Thorlabs / Lasertack / OdicForce |
| ☐ | Trap lens | Thorlabs **LA1509-A** (f = 100 mm, Ø1"), mounted **flat side toward the laser** | 2 (second for DIY-2c) | $39 each | Thorlabs |
| ☐ | **Zoom** beam expander to a 6.0–6.5 mm (1/e²) beam. **No iris in the trap beam**: clipping destroys the pocket | Variable 2–8× expander (405 nm), or a lens pair with fine-adjustable focal ratio | 1 | $60–300 | Thorlabs / AliExpress |
| ☐ | Controller + tapper | ESP32 (original, with DAC) dev board, AO3400 MOSFET, 5–12 V push solenoid, 1N4007 diode, resistors | 1 set | $20–40 | Amazon / AliExpress |
| ☐ | Camera filter | Long-pass ≥ 450 nm, to block 405 nm | 1 | $10–30 | AliExpress |
| ☐ | Particles to screen | Food-grade activated charcoal powder; graphite powder; nigrosin; a toner refill; plus the DIY-1 spheres as controls | 1 each | $10–20 each | Amazon / art suppliers |
| ☐ | Galvos (for 2b) | ILDA set with **mirrors ≥ 10 mm** (7 mm cuts the pocket contrast from 23 to 5) and a coating that reflects at 405 nm (ask for the curve), ±15 V supply included. Mount the pivot 25–35 mm before the lens | 1 | ~$200–515 (larger mirrors) | AliExpress / Amazon |
| ☐ | DAC (for 2b) | **Helios** (12-bit; turn the galvo size trim down), or the ESP32 + MCP4922 board from `ELECTRONICS.md` | 1 | $99–114 / ~$30 | Helios store / DIY |
| ☐ | Illumination (for 2b) | Cyan LED or a ≤ 5 mW 488–520 nm module, through the enclosure | 1 | $20–60 | AliExpress |

**DIY-2c add-on (optional, estimate, not sourced by R11):**
- a metal-coated **hollow** corner cube (Ø25 mm, beam deviation ≤ 5 arcsec; a TIR cube will not work);
- a 405 nm polarising beam-splitter cube and quarter-wave plate;
- the second LA1509-A.

About $0.3–0.9k.

---

**Totals.**
- Orders 1 + 2: ≈ **$2.7–4.5k**, safety kit included. This is a little above R11's $2.6–3.6k "recommended path" because this list picks two LG3 pairs plus viewing glasses, a full safety-relay interlock, and two dumps.
- Order 3 adds ≈ **$0.6–1.3k**.

Order 1 is not optional, and it is the part that keeps every later step safe.

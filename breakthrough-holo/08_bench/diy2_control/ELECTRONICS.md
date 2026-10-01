# DIY-2 electronics: safety interlock and galvo driver stage

**Status:** a design on paper. It is not built or tested. Have someone with electrical and laser-safety experience review it before you build. Mains wiring (the 230/120 V side of power supplies) is for a qualified person only. Everything below runs on 12–24 V DC.

---

## 1. Hardware laser interlock (required, before any laser is connected)

**Goal.** Laser power must stop in hardware, with no software involved, when any of these happens:
- the lid opens;
- the E-stop is pressed;
- the key is turned off;
- the power fails.

After a stop, the laser must stay off until someone deliberately presses RESET. Closing the lid alone must never restart it. A manual reset is what laser product standards require for Class 4 (IEC 60825-1, 21 CFR 1040.10). It is good practice for 3B too.

**Recommended: a commercial safety relay.** A dual-channel, manual-reset safety relay does all of this properly. It is designed so that one failed contact or wire cannot leave the laser enabled. Examples:
- Pilz PNOZ s3 / X2.8P;
- Omron G9SA-301;
- Phoenix Contact PSR-SCP-24DC/ESAM4;
- Siemens 3SK1.

They cost about $80–250 new and are often cheap used. Wire it as the manual shows for "E-stop plus guard door, dual channel, manual (monitored) reset", with the parts below.

**Budget alternative: two relays with welded-contact check** (24 V DC). Below, "K1 NC aux" and "K2 NC aux" are each relay's own normally-closed contact.

```
 +24V --[E-STOP NC]--[KEY SW]--[LID SW A]--[LID SW B]--+--[RESET NO]--[K1 NC aux]--[K2 NC aux]--+--+--(K1 coil)-- 0V
                                                       |                                        |  |
                                                       +--[K1 NO aux]--[K2 NO aux]--------------+  +--(K2 coil)-- 0V
                                                          (self-hold: both relays must be on)

 Laser driver DC supply:  PSU + --[K1 NO main]--[K2 NO main]--> laser driver +    (both relays in series)
 Warning lamp "LASER ON" wired after K1 and K2, so it lights whenever the driver can emit.
 ESP32 status input: a separate K1 NO contact (dry contact to GPIO 4 and GND). This keeps 24 V away from 3.3 V logic.
```

**Why each part is there:**
- **E-stop:** a red mushroom head with **positive-opening NC** contacts (IEC 60947-5-5). It latches until twisted out.
- **Key switch:** the key comes out only in the OFF position. Keep the key away from the bench.
- **Lid switches A and B:** two **positive-opening** safety interlock switches. Use tongue/actuator types such as Omron D4NS, Schmersal AZ 15, or a coded magnetic safety sensor. A plain microswitch can be defeated by a dropped screwdriver, and its contact can weld. A plain magnet reed switch can be defeated with any magnet. Two switches means one failure is not enough.
- **Two relays in series:** if one relay's contact welds shut, the other still cuts the laser.
- **K1/K2 NC aux contacts in the RESET path:** if either relay is stuck on (welded), RESET cannot start the system. The fault shows up at the next start instead of hiding. This only works with **force-guided (mechanically linked) contact relays**, such as the Omron G7SA or the Phoenix PR1 safety-relay family. With ordinary relays, the NC and NO contacts are not guaranteed to be opposite, so this check is not reliable. If you cannot get force-guided relays, buy the safety relay module above instead.
- **Self-hold:** RESET starts the relays and their own NO contacts keep them on. A break anywhere in the chain drops both relays. They stay off until RESET, which meets the manual-reset rule. A power failure drops them as well.
- **Cutting the laser driver's DC supply:** this is the fail-safe action. If your driver also has a TTL enable input, you may wire that from a third relay contact as well. Do not rely on TTL enable alone.

**Test before every session, with the laser aimed into the beam dump at the lowest power:**
1. Open the lid: the laser goes off.
2. Close the lid: the laser stays off until RESET.
3. Repeat with the E-stop and with the key.
4. Write the date in a log.

---

## 2. Galvo command stage (ESP32 + MCP4922 → ±5 V)

Used only with `galvo_esp32.ino`. A Helios or other ILDA DAC needs none of this: it plugs straight into the galvo driver's DB25 ILDA input.

**DAC side.**
- Power the MCP4922 from the ESP32's **3.3 V**. At 5 V its logic threshold, 0.7·VDD = 3.5 V, is above the ESP32's 3.3 V outputs.
- Feed VREFA and VREFB from a 2.5 V shunt reference: LM4040-2.5 with a ~1 kΩ series resistor from 3.3 V.
- **Unbuffered** VREF mode (the firmware sets BUF = 0), so the output is 0–2.5 V.
- Decouple: 100 nF at VDD and at the reference.
- Pin wiring:

  | MCP4922 | ESP32 |
  |---|---|
  | SCK | GPIO 18 |
  | SDI | GPIO 23 |
  | CS | GPIO 5 |
  | LDAC | GPIO 17 |
  | SHDN | 3.3 V |

**Op-amp stage.** One op-amp per axis, inverting with an offset, using a dual op-amp such as a TL072 or OPA2172 on ±12–15 V rails. Many galvo kits supply ±15 V; if yours supplies ±24 V, use a separate ±12 V module, because many op-amps are limited to 36 V total.

```
             Rf 40.2k  (Cf 470 pF across Rf: ~8 kHz reconstruction filter)
          +---/\/\/---+
 Vdac --/\/\/--+-----|-\         Vout = Vm (1 + Rf/Rin) - (Rf/Rin) Vdac
      Rin 10k      |    >---+--> to galvo driver X+ (or Y+); driver X- to analog ground
 2.5V ref --15k--+--|+/
                 10k            Vm = 2.5 V x 10k / (15k + 10k) = 1.00 V
                 GND
```

**Transfer function.**
- With Rf/Rin = 4.02: Vout = 5.02 − 4.02·Vdac.
  - DAC code 0 (0 V) → **+5.02 V**.
  - Code 2048 (1.25 V) → **0.00 V**, centre.
  - Code 4095 (2.4994 V) → **−5.03 V**.
- The output is inverted. Swap the galvo's X+/X− wires, or mirror the path in software (`x → 4095 − x`).
- **General rule:** for gain G = Rf/Rin, centre code 2048 maps to 0 V when Vm = 1.25·G/(1 + G).
- **±10 V input:** use Rf = 80.6 kΩ (G = 8.06), so Vm = 1.112 V. Divider: 12.7 kΩ (top) over 10.2 kΩ gives 1.114 V (1 % E96 parts). Trim the centre in software or with a 1 kΩ pot in the top leg. Rails must then be ±15 V.
- **Differential ILDA (X+ and X−):** add a unity-gain inverter per axis, two 10 kΩ resistors, giving X− = −X+. That needs a quad op-amp (TL074 / OPA4172).
- **Grounds:** analog ground for the galvo driver input at a single point. Keep the ESP32 USB ground and the driver ground from forming a loop. Power the ESP32 from an isolated supply, or add a USB isolator when debugging with a laptop.

**Resolution and scale (check with `path_gen.py --mm_per_full_scale`).**
- Hobby 20–30 kpps galvos give roughly ±10–12.5° mechanical at ±5 V input. Behind an f = 100 mm lens, that is about ±35 mm at the trap, so a 12-bit step is about 17 µm.
- A 1–2 cm glyph then uses only about 15–30 % of the range.
- Most cheap drivers have a **SCALE/size trimpot**. Reduce it, so ±5 V spans about ±12 mm (≈ 6 µm per step), and recalibrate `--mm_per_full_scale` with a target card.

**Bring-up order (galvos only, trap laser physically disconnected).**
1. Power the op-amp stage without the galvo connected. Measure Vout at codes 0 / 2048 / 4095 with a multimeter: expect ≈ +5 / 0 / −5 V.
2. Connect the galvo driver. Run a slow 1 Hz circle (`path_gen.py circle --v 0.01`).
3. Check with the low-power alignment beam on a card inside the closed enclosure.
4. Only then go to trap tests (DIY-2 milestones), with the interlock tested as in §1.

**Self-check of the stage numbers:** `python3 electronics_check.py`. It recomputes the transfer function, the offset divider, the filter corner and the step size.

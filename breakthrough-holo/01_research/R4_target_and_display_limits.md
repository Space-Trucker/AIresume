# R4: The target (film analysis) and the limits of mid-air displays

Research agent R4 · 2026-09-30 · covers TASKS B1, B2, C4 (part)

## How to read this file

Every claim carries a tag:

| Tag | Meaning |
|---|---|
| **[V]** | Found in a web-search result this session, with the URL given. Quotes marked "verbatim" match the search snippet. Direct page fetches were blocked by the egress proxy, so wording could not be checked against the full page. |
| **[KB]** | From the agent's background knowledge. **Not re-verified this session** because the web-search budget (200 calls) ran out. Treat as "to verify" before a design decision rests on it. |
| **[F]** | Measured by this agent from the owner-supplied frames in `00_mission/ref1…ref5` (method in the appendix). |
| **[D]** | A derivation or calculation done here. |
| **[E]** | ESTIMATE, with its assumptions stated. |

---

# PART A: The target (film analysis)

## A1. Who made the film "holograms"

| Film | Studio / person | Role | Tag / source |
|---|---|---|---|
| Iron Man (2008) | ILM (VFX supervisor John Nelson) | About 410 shots, including the digital Mark II/III. Downey improvised slipping his hand into the armor hologram, and "the vfx were built around his performance" | [V] https://variety.com/2008/film/news/iron-man-vfx-suit-robert-downey-jr-1117984897/ ; https://www.ilm.com/vfx/iron-man/ |
| Iron Man (2008) | Prologue Films (Ilya Abulkhanov) | UI design development and HUD concept development | [V] https://workbyilya.com/filter/prologue-films/Iron-Man-1-2008 |
| Iron Man (2008) | Pixel Liberation Front, The Embassy, The Orphanage | Previs (PLF), plus suit and other VFX shots | [V] https://m.imdb.com/title/tt0371746/fullcredits/visual_effects ; https://www.awn.com/vfxworld/summer-previs-rescue |
| Iron Man 2 (2010) | **Prologue Films**: creative directors Danny Yount, Ilya Abulkhanov, Paul Mitchell; 3D/CG supervisor Zai (Jose) Ortiz | All the holographic and screen interfaces in Stark's lab: "over 20 minutes of shots" (Abulkhanov) and "over 200 shots" of hologram sequences (Ortiz) | [V] https://www.artofvfx.com/iron-man-2-danny-yount-directeur-artistique-prologue/ ; https://projectsbyilya.com/Iron-Man-II-U-I-Holograms ; https://www.behance.net/gallery/570107/IRON-MAN-II-Hologram-Armor-Suit-Development |
| Iron Man 2 (2010) | Perception (NYC) | "Stark Technology" gadget design. Also the Stark Expo keynote video, projected on a 70-ft screen | [V] https://www.experienceperception.com/work/iron-man-2/ ; https://www.maxon.net/en/article/the-making-of-iron-man-2 |
| Iron Man 2 (2010) | Cantina Creative (Stephen Lawes, Sean Cushing) | In-helmet HUD graphics, built in Cinema 4D | [V] https://www.provideocoalition.com/cantina-creative-gives-iron-man-3-a-heads-up-with-maxon-cinema-4d/ |
| Avengers (2012), Iron Man 3 (2013) | Jayse Hansen (working with Cantina) | HUDs and holograms in the *later* films. No credit on IM1 or IM2 was found | [V] https://thenextweb.com/news/jayse-hansen-on-creating-tools-the-avengers-use-to-fight-evil-touch-interfaces-and-project-glass ; https://www.imdb.com/name/nm3701215/ |

Design intent in the makers' own words:

- Abulkhanov (IM2): the challenge was "to build the visual manifestation of J.A.R.V.I.S. itself in a fully immersive holographic environment". The interface should be "as beautiful as it was functional, yet had a considerable amount of impressionistic and artistic flair since Stark is the modern day DaVinci of the digital era." [V, near-verbatim] https://projectsbyilya.com/Iron-Man-II-U-I-Holograms
- Ortiz (IM2): the R&D explored "how and what a real light emission hologram would look in the near future", using "realistic animations demonstrating light fields objects in space." [V, near-verbatim] Behance link above.
- Paul Mitchell (Prologue, the Expo-model sequence): they had to find "the balance between the right level of complexity verses too much confusion" and "make sure we enhanced his performance with holograms matching his eye line and arms reach." [V, verbatim in snippet] Art of VFX link above.
- Production method: Favreau shot plates with nothing in the air. Prologue got the plates plus ILM LIDAR scans of the set for the spatial relationships. A previs company worked out the element-discovery beats. [V] Art of VFX link above.
- Cantina (IM3) on the *earlier* films' language: the IM3 team moved "towards a more 3D photo-real, holographic approach as opposed to the design language of the previous films – 2D graphic elements in 3D space." [V, verbatim in snippet] https://www.maxon.net/en/article/cantina-creative-gives-iron-man-3-a-heads-up-with-maxon-cinema-4d
- Danny Yount (IM3): he built the IM3 holograms on the look established in IM2. [V] https://www.artofvfx.com/iron-man-3-danny-yount-creative-director-prologue-films/

**Takeaway:** IM1 and IM2 holograms are flat, glowing, 2D-style line graphics arranged in 3D space. They are composited in post, placed to match the actor's eye line and arm's reach, and never had to exist physically.

## A2. Scene breakdown

### Iron Man (2008): designing the armor in the Malibu workshop

- At about 52 minutes, Stark designs the suit with "an advanced 3D CAD system that uses volumetric projection and full body gesture recognition and tracking." To delete a part (the head), "he picks it up and throws it into a trashcan." [V] https://scifiinterfaces.com/category/marvel-cinematic-universe/iron-man/iron-man-2008/
- Stark removes parts and drops "the light-based images into a trash can", a stand-in for a computer's recycle bin. He can "put his arm inside the holographic model to see how the Mark II armor will look." [V] https://neverfeltbetter.wordpress.com/2014/09/22/in-detail-iron-man-working-on-something-big-54-14-01-01-11/
- The arm-inside-the-hologram moment was improvised by Downey on set. [V] Variety link above.
- Frame `ref1` (supplied as the IM1 armor frame) [F]:
  - A **life-size** standing wireframe armor. Its helmet is about the size of the actor's head at a similar depth, so scale is about 1:1 and the full figure is about 2 m tall.
  - Cyan wireframe with **orange** mechanical accents and red at the hands. Floating callouts and rings around it.
  - The actor holds a small glowing part at chest height, about 0.4 m from his face.
  - The room is lit: lamps, a painting and furniture are visible.

### Iron Man 2 (2010): the lab

- **Suit hologram with Pepper** (`ref2`) [F]:
  - A roughly 1 m wide holographic rendering of the Mark V "suitcase" suit floats at chest height *between* Tony and Pepper. Both look at it at the same time from different positions.
  - A second, life-size standing armor hologram is at frame left.
  - Pepper's body is visible *through* the hologram. The content is additive and see-through.
- **Stark Expo model to new element** (`ref3`) [F][V]:
  - The 1974 Expo diorama is digitized into a hologram roughly 3 m or more wide at table height: blue ground plan and green wireframe buildings.
  - Tony expands it, removes "unnecessary structures", and turns the layout into an atomic model of a new element. [V] https://marvelcinematicuniverse.fandom.com/wiki/Iron_Man_2 ; https://www.youtube.com/watch?v=Ddk9ci6geSs
  - Expanding the model to room size and walking inside it: [KB, from viewing the film].
- **Periodic-table wall** (`ref4`, Prologue reel) [F][V]:
  - A roughly 2.5 m × 1.6 m grid of translucent teal tiles, each about 10 cm, with one selected tile (Ce) in **red**.
  - A motion test shows Tony "combining 2 elements from a holographic periodic table in order to create a brand new element" (a deleted-scene concept). [V] https://www.cgrecord.net/2010/09/iron-man-ii-molecule-discovery.html
  - The owner lists the holo-wall *form* as not the goal, but the dense UI *content* is.
- **Globe / JARVIS UI** (`ref5`, Prologue reel) [F]:
  - A glowing globe roughly 0.2–0.4 m across, surrounded by about 15 schematic panels and **about 115 green data markers**.
  - These are arranged on a curved shell around the user at arm's length to about 1.5 m.
  - It is the densest frame: 19% of pixels are hologram.

## A3. Measured design language (from the frames) [F]

Method: hologram pixels are those with HSV saturation > 0.35 and value > 0.45. Luminance is computed in *linear* sRGB. The scale (mm per pixel) comes from the actor's head size (crown to chin ≈ 230 mm, or breadth ≈ 155 mm) at the actor's depth. Code is in the appendix.

| Frame | Hologram px | Cyan / blue share | Orange / red share | Green share | Median cyan hue | Hologram ÷ background luminance (median / p95) | Lit components ≥ 4 px | Visible stroke length [E] |
|---|---|---|---|---|---|---|---|---|
| ref1 IM1 armor | 16% | 95% | 1% | 1% | 184° | 5.2× / 9.4× | 154 | ~9 m |
| ref2 IM2 suit + Pepper | 9% | 86% | 11% | 0% | 181° | 6.3× / 13× | 245 | ~14 m |
| ref3 Expo model | 14% | 92% | 0% | 5% | 197° | 6.9× / 17× | 761 | ~57 m |
| ref4 periodic table | 14% | 95% | 1% | 3% | 167° | 12× / 24× | 595 | ~40 m |
| ref5 globe UI | 19% | 90% | 0% | 9% | 199° | 4.5× / 12× | 613 | ~19 m |

Notes on the measurements:

- **Colors.** The mean hologram color is sRGB ≈ (40–85, 130–155, 130–180), a cyan to azure. As a laser-primary target this is roughly a 485–500 nm dominant wavelength [E], or a mix of about 450 nm and about 520 nm. The accents are orange/amber (armor mechanics), red (selection and suit paint) and green (buildings and data points).
- **Line width.** The thinnest strokes are 1 px wide in every frame. At these frame resolutions that is about 1.0–3.3 mm at the actor's depth, so the film lines are **≤ 1–3 mm wide** [E]. The source masters were about 2K, so the true strokes are probably thinner.
- **Translucency.** Fills are faint and glowing. The background shows through everywhere, nothing is black, and there are halos and bloom. The holograms cast no shadows. The hologram's cyan spills onto skin and clothes (ref2, ref4), which is consistent with interactive light added in VFX.
- **Lighting.** The rooms are low-key but not dark. The median frame code value is 0.14–0.32, and practical lamps and windows are visible. In ref3 the window is brighter than the hologram.
- **Layout.** Elements sit in layers and arcs at eye level and arm's reach (see Mitchell's quote in A1). Panels wrap around the user in a partial cylinder (ref4, ref5).

## A4. Interaction verbs seen

| Verb | Scene | What a real display must do |
|---|---|---|
| Rotate / spin (flick) | IM1 armor, IM2 Unisphere | Follow a hand's angular velocity and add inertia |
| Explode view (separate parts) | IM1 armor | Re-lay-out the parts of the model live |
| Grab / pick up a part | IM1, IM2 | Detect a pinch or grasp; attach the part to the hand in 6 degrees of freedom |
| Throw into a bin (delete) | IM1 armor head → trash can | Continue a ballistic path after release, and know where the bin is |
| Arm inside the hologram (try on the gauntlet) | IM1 | Draw points *around and in front of* a real arm; skin must be safe inside the volume |
| Two-hand scale (about 30×, model to room) | IM2 Expo | Rescale the whole scene live; the volume must hold room-scale content |
| Walk inside the model | IM2 Expo [KB] | Viewers inside the image volume |
| Poke / tap a tile; drag and combine | IM2 periodic table | Detect fingertip touches to within about 1 cm |
| Scan a real object into a hologram | IM2 Expo diorama | 3D capture (not a display requirement) |
| Voice ("JARVIS…") | both | Speech interface (not a display requirement) |
| Shared viewing | IM2 Tony + Pepper | Two or more people see the same world-locked content from different sides |

## A5. Derived display requirements (the measurable target)

| ID | Quantity | Film evidence | Target | Tag | GOAL |
|---|---|---|---|---|---|
| DR-1 | Object / volume size | Parts 0.1–0.4 m; armor about 2 m (ref1); suit about 1 m (ref2); Expo model ≥ 3 m, expanded to room size | Core volume **≥ 1 × 1 × 2 m**; stretch 3 × 3 × 2.5 m (room) | [F][E] | R9 |
| DR-2 | Viewing distance | "eye line and arms reach" | Full detail at **0.3–1.5 m** | [V][E] | R9 |
| DR-3 | Line width / addressability | Thinnest strokes ≤ 1–3 mm | **0.5–1 mm lines** (1 mm at 0.5 m ≈ 6.9 arcmin); position jitter ≤ 0.5 mm | [F][E] | R9 |
| DR-4 | Points per volume frame | 9–57 m of visible stroke plus 0.15–0.8 m² of translucent fill per frame | **10⁴–10⁵ line voxels** (1 mm pitch), up to about 10⁶ with fills | [F][E] ±3× | R6 |
| DR-5 | Refresh and voxel rate | Film is 24 fps; motion looks smooth | ≥ 30 Hz content, **≥ 60 Hz volume refresh** (flicker-free persistence of vision [KB]) → **≈ 10⁶–10⁸ voxels/s** | [E] | R6 |
| DR-6 | Separate elements | 150–760 lit components per frame; about 118 tiles; about 115 markers | **≥ 500 independently lit objects**; legible glyphs about 3–5 cm tall (tiles about 10 cm) | [F] | R6 |
| DR-7 | Colors | Cyan is 86–95% of lit pixels; orange 1–11%; red highlight; green 0–9% | **Cyan (~490 nm or 450+520 mix) is required.** Orange (~600 nm), red and green are wanted. A monochrome cyan MVP gets about 90% of the look | [F][E] | R9 |
| DR-8 | Brightness vs room | Hologram is 4.5–12× the background (median) and 9–24× (p95) | In a 50–150 lux lab, background ≈ ρE/π ≈ 5–15 cd/m² (ρ≈0.3), so **~25–180 cd/m² median, peaks ~100–350 cd/m²** | [F][E] | R9 |
| DR-9 | Compositing | Purely additive: see-through, no black, glow | **Emission-only is enough.** No occlusion or black rendering needed (this helps the physics) | [F] | R1 |
| DR-10 | Viewers | Tony and Pepper watch the same hologram from different sides (ref2) | **≥ 2 viewers at once, ≥ 2π sr, goal 4π**; no single-viewer head-tracked rendering | [F] | R2, R5 |
| DR-11 | Hand in the volume | Arm inside the gauntlet; grabbing parts | Skin-safe everywhere in the volume. Points must stay visible when a hand sits between the source and the point | [V][F] | R7, R8 |
| DR-12 | Hand tracking | Pinch, grasp, throw, poke, two-hand scale ≥ 30× | Both hands at finger level in 6 degrees of freedom; tracking volume ≥ display volume | [V][F] | R7 |
| DR-13 | Latency | Response lands in the same film frame (≤ 42 ms at 24 fps) | **≤ 20 ms hand-to-photon** for direct manipulation; ≤ 50 ms for large gestures. Direct-touch studies show latency is noticeable well below 100 ms, down to single-digit ms for dragging (Ng et al., UIST 2012; Jota et al., CHI 2013) | [F]; latency studies [KB] | R7 |
| DR-14 | Room light | Windows and lamps on | Works at **50–150 lux**; stretch 300 lux (office) | [F][E] | R9 |
| DR-15 | Invisibility and silence | No beams, fog, noise or smell; people walk through | Addressing light invisible and non-scattering outside voxels; quiet (≲ 35–40 dBA) [E]; no O₃ or NOx smell | [F][E] | R3, R8 |
| DR-16 | Touch feedback | **None shown**: hands pass through | Goal R7 asks for feel: a glove or mid-air haptics, beyond what the film shows | [F] | R7 |

**Most important conclusion from Part A:** the film look is *thin, additive, cyan line art with sparse fills*. That is the friendliest possible content for a point-emission (volumetric) display. The hard parts are **size** (DR-1), **voxel rate** (DR-5), **all-around shared visibility** (DR-10) and **hands inside the image** (DR-11).

---

# PART B: State of the art and fundamental limits

## B1. The line-of-sight principle ("display frustum") [D]

In clean air, radiance is conserved along every ray: nothing emits, absorbs or scatters in between, apart from Rayleigh scattering at 10⁻⁵ m⁻¹ (B5). Suppose an eye sees an image point P in direction **u**. Then the ray that reaches the eye, traced backward, must end on something that emitted or redirected it.

- If P itself does not emit or scatter (empty air), the ray passes through P and ends on the **display aperture** behind it. A floating "real image" is only a point where rays cross.
- So P is visible only to eyes inside the cone that runs from the aperture, through P, and out the other side. The allowed viewing solid angle is the solid angle the aperture subtends *as seen from P*.
- A single flat aperture therefore gives **less than 2π sr** of viewing. It also always puts the display apparatus directly behind the image in the viewer's line of sight: the "Princess Leia problem".

Viewing solid angle for a point floating on-axis in front of a square aperture of side a, at distance d (Ω = 4·asin(a²/(a²+4d²))):

| Geometry | Ω (sr) | Share of sphere | Edge half-angle |
|---|---|---|---|
| 1 m panel, point 1 m in front | 0.81 | 6.4% | 27° |
| 20 cm plate (ASKA-type), image 20 cm out | 0.81 | 6.4% | 27° |
| 60 cm table, point 30 cm above | 2.09 | 16.7% | 45° |
| 2 m wall, point 1 m in front | 2.09 | 16.7% | 45° |

**Corollaries.**

1. **All-around viewing (4π, DR-10) needs one of two things:** light must *originate or scatter at P* (volumetric emission), or the apertures must *surround* the volume (a cage of displays), which breaks the "one projector" rule R4.
2. **Hand occlusion (DR-11).** In aperture-based displays (holographic, light-field, aerial-imaging), a hand between the aperture and P blocks every ray to P for viewers behind the hand. The image vanishes where the hand's shadow falls in the viewing cone, including points *in front of* the hand. Only emission at P gives the natural, film-like occlusion.
3. **No virtual images for volumetric displays.** A point-emitter display can only show points *inside* its volume. It cannot show a "window" onto a larger scene (Q2, Q3).

## B2. Authoritative statements (quotes)

| # | Statement | Source | Status |
|---|---|---|---|
| Q1 | "Free-space volumetric displays, or displays that create luminous image points in space, … are capable of producing images in 'thin air' that are visible from almost any direction and are not subject to clipping. Clipping restricts the utility of all three-dimensional displays that modulate light at a two-dimensional surface with an edge boundary; these include holographic displays, nanophotonic arrays, plasmonic displays, lenticular or lenslet displays and all technologies in which the light scattering surface and the image point are physically separate." | Smalley et al., "A photophoretic-trap volumetric display", *Nature* 553, 486 (2018). https://www.nature.com/articles/nature25176 | [V] abstract text from search snippets |
| Q2 | "Optical trap displays (OTD) are an emerging display technology with the ability to create full-color images in air, but like all volumetric displays, OTDs lack the ability to show virtual images." | Rogers & Smalley, *Sci. Rep.* 11, 7522 (2021). https://www.nature.com/articles/s41598-021-86495-6 | [V] |
| Q3 | Near-term goals: "(1) to scale the display volume from 1 cm³ to greater than 100 cm³ and (2) to employ parallel traps to address the fundamental incapacity of freespace volumetric displays to create virtual images." | Smalley et al., "Improving photophoretic trap volumetric displays [Invited]", *Appl. Opt.* 58, G363 (2019). https://par.nsf.gov/servlets/purl/10141807 | [V] |
| Q4 | The Princess Leia problem: a real object sends photons in all directions, but R2-D2's projected light travels in straight lines, so "the princess would only be seen by observers if they stared at her from the exact same direction—down the barrel of R2-D2's projector." Also: a hologram scatters light only at a 2D surface, so "you must be looking at the scattering surface to see the image." | Smalley, as reported by *Science* (2018) https://www.science.org/content/article/princess-leia-holograms-one-step-closer-reality and BYU https://news.byu.edu/news/better-hologram-byu-study-produces-3d-images-float-thin-air | [V] **paraphrase from search summaries**; check exact wording |
| Q5 | Light-field displays "generate only a limited number of light rays … 3D content can be shown with high quality only within a narrow depth range, referred to as Depth-of-Field (DoF), around the display screen. Outside this range … image quality degrades proportionally to the distance from the screen." Separately: the "depth of field is proportional to 1/Δv" (the angular Nyquist limit). | DASC, arXiv:2508.08928 (2025) https://arxiv.org/html/2508.08928 ; Zwicker, Matusik, Durand & Pfister, "Antialiasing for automultiscopic 3D displays" (EGSR 2006) | [V] (snippet level) |
| Q6 | "A fundamental problem of all digital holographic displays is the limited space–bandwidth product, or étendue, offered by current spatial light modulators (SLMs)." Also: "étendue … is the product of the area of the SLM and the maximum diffraction angle", which forces a trade-off between image size (or eyebox) and field of view. | Search results on étendue: *Nat. Photon.* 2025 https://www.nature.com/articles/s41566-025-01718-w ; *Nat. Commun.* 15, 2907 (2024) https://www.nature.com/articles/s41467-024-46915-3 ; *Appl. Sci.* 15, 9237 (2025) https://doi.org/10.3390/app15179237 | [V] text; **which paper said it is uncertain** |
| Q7 | MMAP / ASKA3D aerial images "have a limited viewing angle, making them difficult to use in face-to-face interactions"; the ASKA3D-200NT has a **40°** viewing angle. Patents give about ±10–15° for a 20 × 20 cm plate. | *Sensors/PMC* 2025 https://pmc.ncbi.nlm.nih.gov/articles/PMC12111977/ ; USPTO 12526399 | [V] |
| Q8 | Laser-induced plasma "does not require physical matter arranged and suspended in air to emit light." | Ochiai et al., "Fairy Lights in Femtoseconds", *ACM TOG* 35(2) (2016). https://arxiv.org/abs/1506.06668 | [V] |
| Q9 | "Previous displays based on swept-volume surfaces, holography, optophoretics, plasmonics or lenticular lenslets … rely on operating principles that cannot produce tactile and auditive content as well." | Hirayama et al., *Nature* 575 (7782) (2019). https://www.nature.com/articles/s41586-019-1739-5 | [V] |
| Q10 | The radiance / étendue theorem: in a lossless medium, radiance is constant along a ray and étendue cannot decrease. This is the textbook basis of B1. | Standard radiometry (e.g. Born & Wolf; Chaves, *Introduction to Nonimaging Optics*) | [KB] |

## B3. State-of-the-art table

| System | Year | Principle | Volume | Voxels/s | Colors | Touch | Medium needed | Source |
|---|---|---|---|---|---|---|---|---|
| **Optical Trap Display** (Smalley, BYU) | 2018 → 2021 virtual-image simulation → 2023 diffractive multi-trap | Photophoretic trap holds one ~10 µm cellulose particle; the trap is scanned while the particle is lit with RGB (persistence of vision) | ~1 cm³ (goal > 100 cm³) | Not quantified in retrieved text; single particle | Full RGB | No (hands would disturb the trap) | **Yes**: trapped particle | [V] nature25176; s41598-021-86495-6; SPIE 12445 (2023) https://ui.adsabs.harvard.edu/abs/2023SPIE12445E..0IB/abstract ; 2025 review arXiv:2512.09401 |
| **MATD** acoustic trap display (Hirayama, Plasencia, Masuda, Subramanian) | 2019 | 40 kHz phased arrays levitate a bead, which is RGB-lit and scanned; the same arrays give haptics and audio | ~10 cm scale [KB] | Particle speed **8.75 m/s vertical, 3.75 m/s horizontal** (simple outlines at POV rates) | RGB | **Yes**: ultrasound tactile, plus audio | **Yes**: bead(s) | [V] s41586-019-1739-5; OptiTrap arXiv:2203.01987 |
| **Aerial Burton** (Burton Inc., Kimura et al.) | 2006 → 2011 | ns-laser air breakdown dots, galvo + varifocal scanning | **20 × 20 × 20 cm** (2011) | **50,000 dots/s** (2011; 300 in 2006); ~10–15 fps | Bluish-white plasma. One source claims RGB, which is doubtful: plasma emission is set by the gas | No (ns plasma is not skin-safe) [KB] | **None** (ambient air), but makes plasma, noise and O₃/NOx | [V] https://newatlas.com/burton-true-3d-laser-plasma-display/20499/ ; https://dl.acm.org/doi/10.1145/2048259.2048279 |
| **Fairy Lights in Femtoseconds** (Ochiai, Hoshi et al.) | 2015/16 | fs-laser plasma voxels; galvo + varifocal lens + LCOS-SLM hologram addressing several voxels at once | mm to ~1 cm scale [KB] | **4,000** (1 kHz, 7 mJ) and **200,000 dots/s** (200 kHz, 50 µJ) | Monochrome (plasma white/blue) | **Yes**: touchable. fs plasma is felt as a tactile impulse and is "safer than" ns plasma | **None** (ambient air) | [V] https://arxiv.org/abs/1506.06668 |
| **FlexiVol** (Bouzbib et al., UPNA) | 2025 (CHI) | Swept-volume display whose diffuser is **elastic strips**, so a hand can push through | **19 × 19 × 8 cm** | Projector: 2,880 binary slices/s at 1280 × 800 → ≤ ~3×10⁹ voxel slots/s (upper bound, [E]; lit voxels far fewer) | 24-bit RGB at 120 Hz volume rate | **Yes**: reach-through direct manipulation (a user study shows gains over a 3D mouse) | **Yes**: moving strip screen | [V] https://dl.acm.org/doi/10.1145/3706598.3714315 ; https://displaydaily.com/a-new-volumetric-display-allows-reach-through-interaction-with-virtual-floating-content/ |
| **Voxon VX1** | ~2018– | Swept volume: reciprocating screen plus high-speed DLP | ~18 × 18 × 8 cm [KB] | Thousands of binary slices/s [KB] | RGB [KB] | No (enclosed moving screen) | **Yes**: moving screen | [KB] voxon.co, unverified |
| **Looking Glass** (Portrait, Go, 16/32/65-inch) | 2020–2024 | Lenticular horizontal-parallax light field, tens of views | Inside the screen's frustum (Q5 depth-of-field limit) | Panel-limited (60 Hz) | RGB | No | **Yes**: screen | [KB] lookingglassfactory.com, unverified |
| **Sony Spatial Reality Display** ELF-SR1 (15.6″) / SR2 (27″) | 2020 / 2023 | Eye-tracked stereo lenticular, **one viewer** | Inside the frustum | Panel | RGB | No | Screen | [KB] |
| **Light Field Lab SolidLight** | Revealed 2021; $50M raise 2023; shipping 2025 | Emissive holographic / light-field wall. 28″ panels, **2.5 Gpx each, 10 Gpx/m²**; objects "float" in front of the wall | Objects in front of the wall, within the viewing frustum (B1) | Not given | RGB | "Interactive" claimed; no tactile | **Yes**: wall of panels | [V] https://www.livedesignonline.com/news/new-solidlight-panels-produce-holograms-gear-free-audiences ; https://gamesbeat.com/light-field-lab-launches-solidlight-holographic-imagery-systems/ |
| **AIRR** (Yamamoto, Utsunomiya) | 2014 → | Retro-reflector plus beam splitter re-images an LED panel into a floating 2D real image | 2D aerial screen; **life-size with a 96″ LED** | Panel | RGB | Gesture UI via sensors ("AIRR Tablet") | **Yes**: beam splitter and retro-reflector in the room | [V] https://opg.optica.org/osac/fulltext.cfm?uri=osac-4-4-1207&id=449709 ; http://ishikawa-vision.org/perception/AIRR_Tablet/index-e.html |
| **ASKA3D / micromirror array plate** (Asukanet) | 2010s → | A dihedral-corner-reflector plate re-images a display as a floating real image | 2D, plate-sized; **40° viewing angle** | Panel | RGB | Via touch sensors | **Yes**: the plate | [V] PMC12111977 |
| **HaptoMime** (UIST 2014) / **HaptoClone** (CHI 2016), Shinoda lab | 2014 / 2016 | Aerial-imaging plate for the image plus an **ultrasound phased array** for mid-air touch | ~Plate-sized (tens of cm) | Panel | RGB | **Yes**: ultrasonic haptics (mN-scale forces) | **Yes**: plate and enclosure | [KB] |
| **Photoswitch-dye volumetric display** ("3D Light PAD", Patel, Cao & Lippert) | 2017 | A UV light sheet activates the dye; a visible DLP excites fluorescence where they cross | cm-scale cuvette | DLP-limited | Mostly single color | No | **Yes**: a block of dye solution | [KB] *Nat. Commun.* 8, 15239. The "Nature 2020 Hartmann light-sheet" work could not be verified. The Nature 2020 light-sheet photoswitch paper I know of is **Xolography** (Regehly et al., *Nature* 588, 620), which is 3D **printing**, not a display [KB] |
| Acousto-optics in ambient air (DESY) | 2024 | An ultrasound grating in air diffracts high-power laser pulses. **This is a beam-steering building block, not a display** | — | — | — | — | None | [KB] Schrödel et al., *Nat. Photon.* 18 (2024); verify |

### "Touchable hologram" claims, checked against the brief (no screen, no fog, no glasses)

| Claim | What it really is | Passes R1–R3? |
|---|---|---|
| FlexiVol, "interactive 3D hologram you can touch" (press coverage 2025) | A swept-volume display with a moving elastic *screen* | No: it has a screen (R3) |
| Fairy Lights, "touchable plasma" | Real emission in bare air; ~cm scale; monochrome; 2×10⁵ dots/s | **Yes on medium.** Fails size (DR-1) and colour (DR-7) by large factors. Safety is covered by R3/R1 agents |
| MATD, "see, hear and feel" | A levitated bead | No: needs a particle (R3 grey zone) |
| HaptoMime / HaptoClone / AIRR + ultrasound | A 2D aerial image from a plate, plus ultrasound haptics | No: needs a plate, and viewing is limited to the frustum (B1) |
| Light Field Lab, "objects escape the screen" | Real images inside the wall's viewing frustum | No: wall; viewing limited by B1 |

No source retrieved in this session reports a room-scale, all-around, medium-free, touchable mid-air display in 2022–2026. The two "no added medium" mechanisms on record are **laser plasma** (Burton, Fairy Lights) and molecular scattering in plain air (B5, far too weak). Plasma emission is the only one that has actually produced pictures.

## B4. Scale gap: target vs best demonstrated (medium-free only) [D][E]

| Metric | Target (A5) | Best medium-free demo | Gap |
|---|---|---|---|
| Voxel rate | 10⁶–10⁸ /s | 2×10⁵ /s (Fairy Lights), 5×10⁴ /s (Burton) | 5×–2000× |
| Volume | ≥ 2 m³ | 8×10⁻³ m³ (Burton 20 cm cube) | ~250× |
| Colors | Cyan plus accents | Plasma white/blue only | Needs a new mechanism (e.g. colour from N₂/O₂ lines, or phosphor-free tricks) |
| Touch-safe | Hands in the volume | fs plasma only, at ~cm scale | Open question (R3 safety) |

## B5. Air optics numbers (532 nm and ~1 µm)

Rayleigh values come from the repo's `holo_common.rayleigh_sigma` (Peck–Reeder dispersion, King factor 1.05). They agree with Bucholtz (1995, *Appl. Opt.* 34, 2765 [KB]), which gives σ ≈ 5.1×10⁻²⁷ cm² at 532 nm. Raman values are scaled from the N₂ cross-section 3.5×10⁻³⁰ cm² sr⁻¹ at 337.1 nm (Measures, *Laser Remote Sensing*, 1984 [KB]) using the ν_s⁴ law.

| Quantity | 532 nm | 1000 nm | 1064 nm | Tag / note |
|---|---|---|---|---|
| Rayleigh σ per molecule | 5.17×10⁻²⁷ cm² | 4.02×10⁻²⁸ cm² | 3.14×10⁻²⁸ cm² | [D] (355 nm: 2.75×10⁻²⁶) |
| Rayleigh extinction β, 20 °C, 1 atm (N = 2.50×10²⁵ m⁻³) | **1.30×10⁻⁵ m⁻¹** (0.0129 km⁻¹) | 1.01×10⁻⁶ m⁻¹ | 7.85×10⁻⁷ m⁻¹ | [D]; 15 °C: 0.0132 km⁻¹ at 532 nm |
| 1/e path length | 77 km | 990 km | 1,270 km | [D] |
| dσ/dΩ at 90° (unpolarized) = 3σ/16π | 3.1×10⁻²⁸ cm² sr⁻¹ | 2.4×10⁻²⁹ | 1.9×10⁻²⁹ | [D] |
| Fraction of 1 W scattered in a 1 mm voxel (βℓ) | **1.3×10⁻⁸** (13 nW, all directions) | 1.0×10⁻⁹ | 7.9×10⁻¹⁰ | [D]. The E1 simulation turns this into ~20 W per voxel for 10 cd/m² |
| N₂ vibrational Raman (Q branch, 2331 cm⁻¹), dσ/dΩ | **4.6×10⁻³¹ cm² sr⁻¹**, Stokes line at **607 nm** | 2.2×10⁻³² (→ 1304 nm) | 1.6×10⁻³² (→ 1415 nm) | [D] from [KB] reference; ~1/1300 of Rayleigh at 532 nm |
| N₂ vibrational Raman total σ (×8π/3) | 3.9×10⁻³⁰ cm² | 1.8×10⁻³¹ | 1.3×10⁻³¹ | [D] |
| Rotational Raman (N₂ + O₂), share of total molecular scattering | **≈ 3.4%** (within about ±100 cm⁻¹ of the laser line) | same | same | [D] = ¾(F−1)/F, with F = 1.048 from depolarization ρ = 0.0279 (Bates 1984 [KB]) |
| Real room-air aerosol extinction (Koschmieder β = 3.912 / visibility) | 0.04–0.4 km⁻¹ for 100–10 km visibility, i.e. **3–30× Rayleigh**, highly variable | Lower (Mie falls off more slowly than λ⁻⁴) | — | [D] from the standard relation [KB]. Dust is real but uncontrolled |
| Kerr nonlinear index n₂ of air | ~3×10⁻¹⁹ cm²/W (the widely used filamentation value at 800 nm). The instantaneous electronic part is ~1×10⁻¹⁹; the rest is delayed rotational response (fs–ps) | Similar (weak dispersion) | Similar | [KB] Couairon & Mysyrowicz, *Phys. Rep.* 441, 47 (2007); Wahlstrand et al., *PRA* 85, 043820 (2012). Repo uses 2.9×10⁻¹⁹ |
| χ⁽³⁾ = (4/3) n₀² ε₀ c n₂ | **1.1×10⁻²⁵ m² V⁻²** (≈ 7.6×10⁻¹⁸ esu) for n₂ = 3×10⁻¹⁹ | — | — | [D] |
| Δn = n₂I | 3×10⁻⁷ at 10¹² W/cm²; 1.5×10⁻⁵ at the ~5×10¹³ W/cm² filament clamping intensity | — | — | [D]; clamping value [KB] |
| Critical power for self-focusing, P_cr = 3.77λ²/(8πn₀n₂) | ≈ 1.4 GW | ≈ 5 GW | ≈ 5.7 GW (800 nm: 3.2 GW) | [D], assuming n₂ does not change with λ |
| Third-harmonic generation in air | Plane focus in bulk air: **THG from a focused Gaussian beam cancels in the tight-focus limit** (Gouy phase, normal dispersion; Boyd, *Nonlinear Optics* §2.10). In fs filaments, conversion is ~10⁻³ (order 0.1%) | 1 µm → 333–355 nm (**UV, invisible and an eye/skin hazard**); 1.6 µm → ~533 nm visible | — | [KB] Akozbek et al., *PRL* 89, 143901 (2002); Boyd (textbook) |

**What the numbers mean for R3 (no added medium):**

- Elastic scattering in clean air is β ≈ 10⁻⁵ m⁻¹ at 532 nm and falls as λ⁻⁴. That is about 10⁻⁸ of the beam per millimetre voxel, in all directions, and it also lights up the *whole beam path*, not just the voxel. Rayleigh scattering cannot confine light to a voxel. The one exception would be two crossed beams whose *combined* effect is nonlinear.
- The χ⁽³⁾ processes that could confine light to a crossing point (four-wave mixing, THG) need ~10¹²–10¹³ W/cm². That is at or above the plasma-onset regime, and B5 shows tight-focus THG cancels anyway. This is why the literature's medium-free displays all ended up using plasma.

## B6. Implications for the lab (hand-off to D1 / D2 / E-series)

1. **D1 (radiance theorem):** B1 plus Q1–Q4 are the published and derived basis. The film's "floating, all-around, shared" look (DR-10) cannot be produced by any aperture display. It needs emission at the voxel.
2. **D2 (touch-occlusion lemma):** B1, corollary 2. Aperture displays lose the image for points whose back-projected cone hits the hand. Volumetric emitters do not.
3. **E1:** the Rayleigh/Raman/Kerr table (B5) sets the calibration numbers. Rayleigh is already validated in `results/e1_clean_air_bounds.json` (β₅₃₂ = 1.29×10⁻⁵ m⁻¹ at 20 °C), which matches this table.
4. **E8 content budget:** plan for 10⁴–10⁵ line voxels per frame at ≥ 60 Hz, cyan first. DR-4 and DR-5 are the numbers to hit.

## Sources (all URLs cited above)

- Film and VFX: artofvfx.com (Iron Man 2 and Iron Man 3, Danny Yount/Prologue) · projectsbyilya.com and workbyilya.com (Abulkhanov) · behance.net/gallery/570107 (Zai Ortiz) · experienceperception.com/work/iron-man-2 · maxon.net ("The Making of Iron Man 2"; Cantina IM3) · provideocoalition.com (Cantina IM3) · variety.com (2008, Iron Man VFX) · ilm.com/vfx/iron-man · scifiinterfaces.com (Iron Man 2008) · neverfeltbetter.wordpress.com (2014/09/22) · cgrecord.net (2010/09, Molecule Discovery) · thenextweb.com (Jayse Hansen) · imdb.com VFX credits
- Limits: nature.com/articles/nature25176 · nature.com/articles/s41598-021-86495-6 · par.nsf.gov/servlets/purl/10141807 · science.org (Princess Leia article) · news.byu.edu · arxiv.org/html/2508.08928 · nature.com/articles/s41566-025-01718-w · nature.com/articles/s41467-024-46915-3 · doi.org/10.3390/app15179237 · pmc.ncbi.nlm.nih.gov/articles/PMC12111977
- Systems: nature.com/articles/s41586-019-1739-5 · arxiv.org/abs/2203.01987 · arxiv.org/abs/1506.06668 · newatlas.com (Burton) · dl.acm.org/doi/10.1145/2048259.2048279 · dl.acm.org/doi/10.1145/3706598.3714315 · displaydaily.com (FlexiVol) · livedesignonline.com and gamesbeat.com (Light Field Lab) · opg.optica.org (AIRR spheres) · ishikawa-vision.org (AIRR Tablet) · arxiv.org/abs/2512.09401 (photophoretic review 2025) · ui.adsabs.harvard.edu (SPIE 12445, 2023)

**Open verification items [KB]:**
- Voxon, Looking Glass and Sony specifications
- HaptoMime and HaptoClone details
- Patel 2017, Xolography 2020, and the requested "Hartmann 2020" paper
- The DESY 2024 acousto-optics paper
- The Measures Raman reference value
- n₂ and THG literature values
- The latency studies (Ng 2012, Jota 2013)
- Whether the Expo model is expanded to room scale

## Appendix: frame-analysis method (reproducible) [F]

```python
# run from breakthrough-holo/00_mission ; numpy, scipy, matplotlib, PIL
import numpy as np, matplotlib.colors as mc; from PIL import Image; from scipy import ndimage as ndi
lin = lambda c: np.where(c<=0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
mm_per_px = {'ref1':230/130,'ref2':230/70,'ref3':230/85,'ref4':155/70,'ref5':155/150}  # head-size scale (E)
for f in sorted(__import__('glob').glob('ref*')):
    a = np.asarray(Image.open(f).convert('RGB'))/255.; hsv = mc.rgb_to_hsv(a)
    m = (hsv[...,1]>0.35)&(hsv[...,2]>0.45)                      # hologram-like pixels
    L = lin(a); Y = L@[0.2126,0.7152,0.0722]                      # linear luminance
    ratio = np.median(Y[m])/np.median(Y[~m]); p95 = np.percentile(Y[m],95)/np.median(Y[~m])
    lab,n = ndi.label(m); ncomp = (ndi.sum(m,lab,range(1,n+1))>=4).sum()
    stroke_px = (m & ~ndi.binary_erosion(m)).sum()/2              # thin-line length approximation
    print(f[:4], m.mean(), ratio, p95, ncomp, stroke_px*mm_per_px[f[:4]]/1000, 'm')
```

Limits of the method:
- The frames are compressed, low-resolution grabs.
- The threshold misses dim lines, so element counts and stroke length are *lower bounds* with about ±3× uncertainty.
- The head-size scale holds only at the actor's depth.
- The luminance ratios are display-referred values after color grading, not scene photometry.

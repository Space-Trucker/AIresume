# Hardware Unit Economics for a Small-Volume AR/HUD Skydiving Wearable (Goggles + Smart Helmet)

Method note: 25 web searches run (the shared budget). Nearly every full-text fetch was blocked by the egress proxy: TechInsights, Bolt blog, mobiledevmemo, ChutingStar, Gembah, Glencoyne, Panox Display, and Dragon Innovation (DNS failure). So most findings come from **search-result snippets and summaries**, not full articles. Labels used: **[Published]** = a figure stated by the source. **[Vendor/marketing]** = a figure from a seller or lab blog, likely self-serving. **[Estimate]** = my own inference, not from a source. Status as of Sept 2026.

---

## 1. BOM costs for AR/HUD wearable components at low volume (1k–10k units)

### Takeaway
No public source gives a full BOM for a low-volume sports HUD. The best published anchor is TechInsights' teardown of the Meta Ray-Ban Display: display-related parts are **50.8% of the BOM**. So the display and optics engine is the line item that matters. Single-unit retail prices for small micro-OLED panels (~$56–$169 bare) and dual-band GNSS eval boards suggest a monocular sports HUD BOM of roughly $120–$300 at 1k–10k units. That range is my estimate.

### Cited Findings
- **Meta Ray-Ban Display ($799 with Neural Band) BOM mix [Published, snippet]:**
  - Display-related components are **50.8% of total BOM**, the largest cost category.
  - It uses a single **OmniVision LCoS** display in the right lens.
  - Qualcomm parts, including the Snapdragon AR1 Gen 1, are **15.7%** of BOM.
  - The Neural Band is **~7.2%** of BOM.
  - Sources: [TechInsights teardown](https://www.techinsights.com/blog/meta-ray-ban-display-teardown-reveals-more-meets-eye); [TechInsights summary](https://www.techinsights.com/blog/summary-meta-ray-ban-display-neural-band-deep-dive-teardown).
  - The absolute BOM dollar total was not visible in snippets.
- **Other teardowns exist but their contents were not viewable:**
  - Ray-Ban Meta Wayfarer (non-display): [Reverse Costing / System Plus teardown](https://www.reverse-costing.com/teardowns/meta-ray-ban-wayfarer-smart-glasses/) (paid report).
  - EDN "pseudo-teardown" of Ray-Ban Meta: [EDN](https://www.edn.com/ray-ban-metas-ai-glasses-a-transparency-enabled-pseudo-teardown-analysis/).
  - iFixit found the Ray-Ban Display very hard to repair: [Android Authority](https://www.androidauthority.com/meta-ray-ban-display-teardown-ifixit-3605921/).
- **Micro-OLED prices [Vendor, small-quantity retail]:**
  - Basic 0.39" 1024x768 panels cost about **$56–$169**. Small panels (0.23–0.39") generally cost under $150.
  - A 0.39" 1024x768 panel lists at $149.
  - With a driver/controller board: $360 for 0.39" 1024x768, and $495 for 0.39" 1920x1080 with a USB-C board.
  - Sources: [Panox Display](https://www.panoxdisplay.com/knowledge/what-is-the-typical-price-of-a-micro-oled-display.html); [Tindie Sony ECX334C listing](https://www.tindie.com/products/oled-modules/sony-ecx334c-micro-039-inch-oled-display-1024x768/).
- **MicroLED (JBD):** JBD aims for ≥70% yield, which would bring prices to **~$10–$20 per display**. This is a forward-looking target, not a current price. [MicroLED-Info](https://www.microled-info.com/jbd). No current per-unit price was found.
- **Optics:**
  - Birdbath uses molded plastic optics plus off-the-shelf Sony micro-OLED that many brands share.
  - Waveguides need diamond-cut micro-mirror stacks or nano-imprinted gratings plus a custom high-nit light engine.
  - Retail proxy: in-stock birdbath glasses run $199–$700 (median $399). Waveguide models run $499–$1,099 (median $649).
  - Source: [AR Compare](https://www.arcompare.com/guides/birdbath-vs-waveguide/). No per-unit component prices were found.
- **Multi-band GNSS:**
  - A u-blox ZED-F9P (L1/L2 RTK) breakout paired with a NEO-D9S costs $175 on sale ($319.95 list). That is a dev board, not a module price. [SparkFun](https://www.sparkfun.com/sparkfun-gnss-combo-breakout-zed-f9p-neo-d9s-qwiic.html)
  - u-blox lists some ZED-F9P variants as no longer available. [u-blox](https://www.u-blox.com/en/product/zed-f9p-module)
  - The bare-module distributor price was not found.
- **Market context:**
  - The global average retail price of AI smart glasses was ~**$360** in H2 2025, up from $347 in H1. Meta had 82% shipment share. [Counterpoint](https://counterpointresearch.com/en/insights/Global-Smart-Glasses-Shipments-Grew-139-Percent-YoY-in-H2-2025)
  - Counterpoint flags rising memory prices as a headwind for 2026.
- **Price points of comparable sports HUD products:**
  - Engo 2 (ActiveLook micro-OLED HUD, cycling/running): **$329.95**. [road.cc](https://road.cc/content/review/engo-eyewear-engo-2-sport-smartglasses-300417); [Engo](https://us.engoeyewear.com/products/engo-2)
  - Everysight Maverick: Sony colour micro-OLED, 43 g, 10 h with display on, IP55. Price not captured. [Everysight](https://www.everysight.com/maverick)
  - FORM Smart Swim 2 goggles: $249 / £229 / €249. [Triathlete](https://www.triathlete.com/gear/swim/triathlete-tests-the-new-form-smart-swim-2-heads-up-display-goggles/); [DC Rainmaker](https://www.dcrainmaker.com/2025/07/form-smart-swim-2-pro-in-depth-review-swim-goggles.html)
  - Forcite MK1S smart motorcycle helmet (carbon shell, LED HUD, camera, Harman Kardon audio): **$1,099.99** at US launch via Tucker Powersports. A 2024 source cites $1,399. [webBikeWorld](https://www.webbikeworld.com/forcite-mk1s-smart-helmet-review/); [Rider Magazine](https://ridermagazine.com/2024/01/12/forcite-mk1s-smart-helmet-review-gear/)

### Inferences
- **[Estimate] Illustrative BOM, standard goggle** (monochrome or low-res micro-OLED or microLED, birdbath/prism optic, single-band GNSS, IMU plus barometer, BLE MCU, ~300–500 mAh cell, USB-C, polycarbonate goggle lens and frame), at 1k–5k units:
  - Display plus optics module: $40–$90
  - GNSS: $5–$15
  - IMU and barometer: $3–$8
  - MCU/BLE: $3–$8
  - Battery: $3–$8
  - PCBA and passives: $15–$30
  - Enclosure, lens and strap: $15–$35
  - Packaging and cable: $5–$10
  - **Total ≈ $90–$200.**
- **[Estimate] Premium tier:**
  - Higher-res colour micro-OLED: an extra $50–$150, since the panel with driver retails at $149–$495.
  - Multi-band L1/L5 GNSS: an extra ~$10–$40.
  - Larger battery, and a coated or photochromic lens.
  - **Total BOM ≈ $200–$350.**
- **[Estimate] Helmet version:** add the certified shell, EPS liner and comfort liner. A carbon shell likely adds $60–$200 at low volume. Forcite's $1,100–$1,400 price suggests helmets carry a much higher price ceiling.
- Following the Meta finding, the display and optics subsystem is likely **40–55% of BOM**. Buying a pre-built display engine concentrates cost there.

### Gaps
- Absolute BOM dollar totals for Ray-Ban Meta, Ray-Ban Display, Xreal, Vuzix, Everysight, Engo, FORM and Forcite were not visible (paywalled or fetch-blocked).
- No volume-tier (1k/10k) pricing was found for micro-OLED, LCoS, microLED, waveguides, or bare u-blox F9/F10 modules.
- No IMU, barometer or battery prices were collected; these are commodity parts to check on Digi-Key or Mouser.

---

## 2. Gross margins, retail markups, dealer margins, warranty/returns

### Takeaway
A DTC hardware business should target **~65–75% DTC gross margin**, which means pricing at roughly **2.5–4x BOM**. Garmin, the closest incumbent, runs **57–66% gross margin** in its Fitness and Outdoor segments. Skydiving gear dealers work on slim, manufacturer-set pricing with rare discounts, so the reseller discount must be set explicitly. Plan for electronics return rates around 8–20% and warranty claims around 1.5–5% of revenue.

### Cited Findings
- **Pricing rules of thumb:**
  - Consumer electronics often charge **2.5–4x BOM**. Below 2.5x you likely lose money. Leaders price on value. [Bolt "Hardware by the Numbers pt 4"](https://blog.bolt.io/hardware-retail-exits/) (snippet via search summary)
  - For DTC, plan **65–75% gross margin** (a 2.86–4x cost multiplier). A 50% margin gets eaten by CAC, returns and promos. [Eightx](https://eightx.co/blog/what-is-keystone-markup) [Vendor/agency blog]
  - Retail channel margins of **30–35%** are reasonable, and can exceed 40% depending on category. [Bolt](https://blog.bolt.io/hardware-retail-exits/) (snippet) — see also [Dragon Innovation](https://blog.dragoninnovation.com/blog/2016/05/26/understanding-gross-margin-hardware) (unreachable)
- **Garmin, the incumbent benchmark [Published, SEC filings]:**
  - Fitness segment FY2025 gross margin **60%**. Quarters: Q1 57%, Q2 60%, Q4 57%.
  - Outdoor segment gross margin **64–66%**. Operating margin rose from 29% (Q1) to 37% (Q4 2025).
  - Sources: [Garmin Q4/FY2025 press release](https://www.garmin.com/en-US/newsroom/wp-content/uploads/2026/02/2025_Q4_Earnings_Press_Release.pdf); [SEC 8-K](https://www.sec.gov/Archives/edgar/data/1121788/000095017025099874/grmn-ex99_1.htm)
- **Skydiving retail:**
  - Manufacturers set prices, and dealers get no volume discount (e.g., the same altimeter price for 1 or 10 units).
  - Gear is "already priced at a very slim margin", and discounts are rare. [ChutingStar "The Truth on Skydiving Gear Pricing"](https://www.chutingstar.com/blog/the-truth-on-skydiving-gear-equipment-pricing/) (snippet; a dealer's own statement)
- **Returns:**
  - Electronics e-commerce return rates are quoted at **8–10%** by one source and **15–20%** by another. The sources conflict. [ShipNetwork](https://www.shipnetwork.com/post/return-rates-by-industry); [Claimlane](https://www.claimlane.com/resources/blog/electronics-returns-warranty-claims)
- **Warranty:**
  - US consumer electronics averaged a **1.52% claims rate** (SD 0.94%) and a **1.46% accrual rate** over 21 years. [Warranty Week](https://www.warrantyweek.com/archive/ww20240711.html) [Published]
  - Vendor benchmarks quote 1–5% or 3–8%. [Claimlane](https://www.claimlane.com/resources/blog/returns-and-warranty-kpis)

### Inferences
- **[Estimate] Dealer discount:** skydiving and outdoor electronics dealers typically buy at **25–40% off MSRP** (keystone is rare). Model 30% as the base case, and 40–50% for distributors who re-sell to dropzones in other regions. This is unverified; see Gaps.
- **[Estimate] Blended margin:** at a 4x BOM-to-MSRP multiple with 30% of sales through dealers at 30% off, blended gross margin before returns and warranty is ≈ 70%. After freight, duties, payment fees, 10% returns and a 3% warranty accrual, a realistic contribution is 55–60%.
- **[Estimate] Warranty reserve:** a first-generation, low-volume product in a harsh environment (wind, impact, rain, cold at altitude) should reserve toward the high end, 3–5%, rather than the 1.5% industry mean.

### Gaps
- No published dealer or distributor discount percentages were found for skydiving manufacturers (L&B altimeters, Cookie helmets, UPT, Sun Path). Recommend asking a dealer directly.
- No wearable-specific return rate was found; the figures are for electronics broadly.

---

## 3. NRE, development and certification costs; time-to-market

### Takeaway
Certification for a BLE/GNSS wearable costs in the low tens of thousands of dollars:
- FCC with a pre-certified module: $3k–$10k
- CE RED: ≥$750 and up; realistic cost is higher
- UN38.3: $2k+
- Budgeting pre-compliance testing ($3k–$8k) avoids first-pass failures that cost $5k–$30k.

Soft aluminium tooling ($3k–$15k per part) fits 1k–10k units. Hard steel ($15k–$80k per part) is for larger volumes. No price lists were found for helmet impact testing (EN 1077/EN 966) or eyewear standards (ANSI Z87/EN 166).

### Cited Findings
- **FCC:**
  - Simple digital device (SDoC): $1.5k–$5k.
  - Product using a **pre-certified Wi-Fi/BLE module: $3k–$10k**.
  - Custom RF: from $8k.
  - A first-pass failure adds **$5k–$30k and 4–12 weeks**. **Pre-compliance testing ($3k–$8k)** cuts the failure rate from ~50% to <10%.
  - Source: [MarkReady](https://markready.io/learn/fcc-certification-cost) [Vendor]
  - A Chinese lab quotes FCC ID from ~$850. [JJR Lab](https://www.jjrlab.com/news/how-much-does-product-certification-cost-fcc-ce.html) [Vendor, low-end]
- **CE:** LVD plus EMC runs "approximately $750 or more". RED (radio) is additional. [Sunfire Testing](https://www.sunfiretesting.com/What-Are-the-CE-Certification-Costs/) [Vendor]
- **Battery:**
  - A UN38.3 test set costs at least **$2,000**. Battery certification broadly runs **$2k–$20k+**. It takes ~3 weeks: 2 weeks of testing plus 1 week for the report. [Ufine Battery](https://www.ufinebattery.com/blog/essential-guide-to-battery-certification-types-costs-timeframes-and-standards/); [Experior Labs](https://experiorlabs.com/un38-3-lithium-battery-test/)
  - A Chinese lab quotes $300–$930 per report. [JJR Lab](https://www.jjrlab.com/news/how-much-does-un383-testing-cost.html)
  - Buying cells that already have a UN38.3 report from the supplier is common.
- **Helmet standard technical content:** EN 1077 caps peak deceleration at ≤250 g on a flat anvil at 89 J, with hot, cold and UV-aged conditioning. [SATRA EN 1077](https://www.satra.com/ppe/EN1077.php). No test prices were found.
- **Tooling:**
  - Aluminium molds cost **$3k–$12k** and last 500–10k shots. Hard P20/H13 steel costs **$15k–$80k** and runs millions of shots.
  - A simple enclosure top in aluminium costs $2.8k–$4.5k. With side actions, undercuts and an optical-polish window it costs $9k–$15.5k.
  - Each side action or lifter adds $1.2k–$3.5k. Optical finish adds $1.8k–$4.2k.
  - Sources: [Xinyang MFG](https://xinyangmfg.com/low-volume-injection-molding-cost-hardware-startups/); [Xometry](https://www.xometry.com/resources/injection-molding/injection-molding-cost/) [Vendor]
  - Tooling is usually the largest single one-time cost. [RapidDirect](https://www.rapiddirect.com/blog/injection-molding-costs/)

### Inferences
- **[Estimate] NRE budget, goggle using an off-the-shelf display engine:**

  | Item | Estimated cost |
  |---|---|
  | Industrial design and mechanical design | $50k–$150k |
  | Electronics design and layout | $40k–$100k |
  | Firmware plus companion app (iOS/Android/desktop, USB-C sync) | $100k–$250k |
  | Optics integration | $20k–$80k with a module; $250k–$1M+ for custom optics |
  | Tooling (4–8 soft-tool parts) | $25k–$80k |
  | Certification (FCC/ISED, CE RED/EMC/LVD, UKCA, UN38.3, IP test, EN 166/ISO 12312 or ANSI Z87 for lens) | $25k–$60k |
  | Prototypes, EVT/DVT/PVT builds | $40k–$100k |
  | **Total** | **≈ $300k–$800k** |

- **[Estimate] Helmet NRE:** shell and liner tooling plus impact certification, likely EN 1077/ASTM F2040 or similar, since there is no skydiving-specific helmet standard (EN 966 covers air sports). This probably adds $100k–$300k.
- **[Estimate] Time to market:** 12–24 months from concept to shipping with a module-based approach.

### Gaps
- No published price lists for EN 1077, EN 966, ASTM F2040, ANSI Z87.1, EN 166 or ISO 12312 testing.
- No IP67/IPX rating test costs.
- ID and firmware day-rate benchmarks were not retrieved (Gembah page blocked).

---

## 4. Off-the-shelf HUD modules and ODMs

### Takeaway
Several module and ODM routes exist:
- **ActiveLook (Microoled)**: a 9 g see-through micro-OLED HUD module already used in Engo 2 ($330 retail).
- **Vuzix**: OEM waveguides and display engines, plus Quanta-built reference designs.
- **Chinese birdbath/LCoS/micro-OLED module vendors.**

None publish OEM pricing; all require direct quotes.

### Cited Findings
- **ActiveLook:**
  - A lightweight (~9 g) HUD module built on Microoled's low-power micro-OLED. OEM pricing requires contacting the company. [Ubergizmo](https://www.ubergizmo.com/2021/01/activelook-head-up-display-smartglass/); [ActiveLook tech](https://www.activelook.net/pages/the-tech)
  - ActiveLook sells Engo 2 sample units and an "Enterprise" platform. [ActiveLook shop](https://shop.activelook.net/products/engo-2-standard-sample-unit)
  - It has an open SDK/app ecosystem: Engo 2 works through the ActiveLook app. [Engo](https://us.engoeyewear.com/products/engo-2)
- **Vuzix:**
  - Sells OEM waveguides and display engines that support DLP, LCoS, laser LCoS and microLED.
  - Its Ultralite Pro/Audio OEM reference designs were co-developed with **Quanta Computer**, which invested $20M total.
  - Offers monocular and binocular options with 30–40° FOV and a 1.0 mm full-colour waveguide.
  - Sources: [Vuzix IR](https://ir.vuzix.com/news-events/press-releases/detail/2149/vuzix-achieves-waveguide-production-milestones-and-receives); [Vuzix CES 2025](https://ir.vuzix.com/news-events/press-releases/detail/2109/vuzix-to-unveil-cutting-edge-ultralite-odmoem-reference); [Vuzix OEM](https://www.vuzix.com/pages/oem)
- **Chinese module vendors** sell micro-OLED modules with controller boards ($360–$495 at unit retail), FLCoS 0.38" 720p modules, and birdbath/waveguide AR modules. [Panox](https://www.panoxdisplay.com/micro-display/sony-0-5-inch-1024x768-micro-oled.html); [YX Microdisplay](https://www.yxmicrodisplay.com/products/flcos-micro-display-module-0-38-inch-1280rgbx720-for-ar-vr); [DisplayModule](https://www.displaymodule.com/collections/ar-vr)
- Lumus and DigiLens: not researched within budget.

### Inferences
- **[Estimate]** Licensing or buying an ActiveLook-class engine is the fastest route for a goggle. It removes optics NRE (possibly $250k+) at the cost of a higher per-unit module price, likely $60–$150 at 1k–5k units (unverified). It also constrains the form factor: ActiveLook is designed for sunglasses, and skydiving goggles need a lens-offset/visor integration.
- **[Estimate]** For a helmet, a visor-projected or chin-bar LED/micro-OLED combiner like Forcite's is cheaper than a waveguide.

### Gaps
- No OEM price quotes for ActiveLook, Vuzix, Lumus or DigiLens modules.
- No ODM MOQ data.

---

## 5. Financing: MOQs, working capital, crowdfunding, subscriptions

### Takeaway
Contract manufacturers usually require **30–50% deposit** (30/70 is the most common split). The cash cycle from deposit to customer cash can exceed **8 months**. Kickstarter Technology projects fund at only **~20%**, and **61–84% of funded projects ship late**, with a median delay of ~2 months. Hardware-plus-subscription models range from Whoop (hardware bundled, ~85% of revenue from subscription) to Garmin Connect+ ($6.99/mo add-on) and FORM (~$99–$180/yr).

### Cited Findings
- **CM payment terms:**
  - Deposits run 30–50% of the first run, with 30% upfront / 70% before shipment the most common. The full deposit-to-customer-cash cycle can exceed 8 months. CMs rarely give startups credit terms. [Berkeley Sourcing Group](https://www.berkeleysg.com/cash-flow-is-a-hardware-startup-killing-business/); [Promise Legal](https://blog.promise.legal/hardware-startup-manufacturing-agreement/)
  - Negotiate rolling forecasts instead of hard MOQs. [Promise Legal](https://blog.promise.legal/hardware-startup-manufacturing-agreement/)
- **Kickstarter success and delivery:**
  - Technology category success rate is **~20%**, against **~40%** overall. A warmed email list converts 3–5x better. [BoostYourCampaign](https://www.boostyourcampaign.com/blog/crowdfunding-success-rate-by-category-2026); [Kickstarter stats](https://www.kickstarter.com/help/stats)
  - **84%** of the top 50 funded projects missed delivery dates. [CNNMoney 2012](https://money.cnn.com/2012/12/18/technology/innovation/kickstarter-ship-delay/index.html)
  - Mollick found **75%** of 471 tech/design projects late. Another study found **61%** of 288 late. The median delay was ~2 months. [Kickstarter blog "Is lateness failure?"](https://www.kickstarter.com/blog/is-lateness-failure)
  - About **9%** of funded projects never deliver (range 5–14%). [Kickstarter / Mollick-UPenn study, via Kickstarter updates](https://updates.kickstarter.com/why-kickstarter-campaigns-fail-after-funding-and-how-to-avoid-it/)
- **Whoop:**
  - Hardware is bundled "free" with membership. About **85% of revenue is subscription**, ~10% accessories/apparel, ~5% enterprise.
  - Tiers are $199, $239 and $359 per year, with a $149/yr plan on older hardware.
  - Annualized bookings reached **$1.1B in 2025 (+103% YoY)**. Whoop was cash-flow positive with 2.5M+ members.
  - Sources: [Sacra](https://sacra.com/c/whoop/); [Whoop membership](https://www.whoop.com/us/en/membership/) (Sacra figures are estimates)
- **Garmin Connect+:** $6.99/mo or $69.99/yr, sold on top of hardware. It drew user backlash. [Tom's Guide](https://www.tomsguide.com/wellness/smartwatches/garmin-launches-a-paywall-here-are-all-the-premium-connect-features-that-will-cost-you-usd6-99-a-month); [DC Rainmaker](https://www.dcrainmaker.com/2025/03/garmin-connect-plus-subscription-walkthrough.html)
- **FORM:**
  - Goggles cost $249. Membership prices vary by source and date: **$15/mo or $99/yr** in one, **$19.99/mo or $179.99/yr** in another.
  - Core metrics work without membership. The subscription unlocks coaching, the open-water compass and workouts.
  - Sources: [FORM membership](https://www.formswim.com/collections/membership); [Triathlete](https://www.triathlete.com/gear/swim/triathlete-tests-the-new-form-smart-swim-2-heads-up-display-goggles/)

### Inferences
- **[Estimate] First production run working capital.** Example: 2,000 units at a $180 landed COGS = $360k inventory.
  - 30% deposit ($108k) about 3–4 months before shipment, then 70% ($252k) before ex-works.
  - Add freight and duties (~5–10%), a buffer for yield loss and spares (~5%), and 3–6 months of opex.
  - Pre-orders or crowdfunding at ~20–40% of the first run can offset the deposit.
- **[Estimate] Subscription economics for skydiving.** A FORM or Garmin-style optional plan ($5–$10/mo, or $50–$100/yr) could fund jump logbook, analytics and cloud features. Examples: canopy-pattern analysis, freefall trajectory, logbook export for licence progression.
  - At 20–30% attach and ~70% annual retention, LTV rises by roughly $40–$120 per hardware buyer.
  - Keep core HUD functions free to avoid Garmin-style backlash. USB-C cable sync lowers cloud cost but weakens the "connected" value of a subscription.
- **[Estimate]** Skydiving is a small market (tens of thousands of active jumpers), so crowdfunding reach is limited. Dropzone and dealer pre-orders may beat Kickstarter.

### Gaps
- No skydiving-specific crowdfunding data.
- No published churn or attach rates for FORM or Garmin Connect+.
- HAX guides were not reviewed.

---

## 6. Premium vs standard tier differentiation and price ratios

### Takeaway
Wearable brands tier on display, GNSS, materials and battery. Observed ratios between premium and base prices cluster around **1.3–2x**. Examples: Whoop Life/One is 1.8x, Birdbath/waveguide medians are 1.6x, and the Forcite price moved from $1,099 to $1,399.

### Cited Findings
- **Whoop:** One $199/yr, Peak $239, Life $359. Life is **1.8x** One. [Whoop membership](https://www.whoop.com/us/en/membership/); [Sacra](https://sacra.com/c/whoop/)
- **AR glasses:** median in-stock waveguide model is $649 vs birdbath $399, about **1.6x**. [AR Compare](https://www.arcompare.com/guides/birdbath-vs-waveguide/)
- **FORM:** Smart Swim 1 at $179 vs Smart Swim 2 at $249, about **1.4x**. [YourSwimLog](https://www.yourswimlog.com/form-2-smart-swim-goggles-review-worth-the-upgrade/)
- **Engo 2:** Standard and Photochromic variants are sold, i.e. tiering by lens material. [Engo Photochromic](https://us.engoeyewear.com/products/engo-2-photochromic)
- **Everysight:** Maverick Sport vs AI/AI Pro variants use the same colour micro-OLED and add features. [Everysight](https://www.everysight.com/maverick)
- **Garmin:** Outdoor-segment gross margin (64–66%) runs above Fitness (57–60%), consistent with premium rugged/outdoor devices carrying higher margins. [Garmin Q4 FY2025](https://www.garmin.com/en-US/newsroom/wp-content/uploads/2026/02/2025_Q4_Earnings_Press_Release.pdf)

### Inferences
- **[Estimate] Suggested tiering for modelling:**
  - **Standard goggle:** monochrome/green HUD, single-band GNSS, ~8 h battery, PC lens. MSRP ≈ **$349–$449** (Engo/FORM comps). BOM ≈ $100–$150.
  - **Premium goggle:** colour micro-OLED, dual-band L1/L5 GNSS, 12 h+ battery, photochromic/anti-fog coated lens, premium frame. MSRP ≈ **$599–$799**. BOM ≈ $200–$300.
  - **Helmet:** certified shell plus integrated HUD, benchmarked to Forcite at $1,100–$1,400. MSRP ≈ **$999–$1,499**, with a carbon premium tier. BOM ≈ $300–$500.
  - All tiers price at ~3–4x BOM, and the premium/standard ratio is ~1.6–1.8x.
- Premium tiers usually carry higher percentage margins, because the extra feature cost is smaller than the price step (Garmin Outdoor vs Fitness pattern).

### Gaps
- Everysight Maverick and Xreal prices were not captured.
- No published BOM deltas between tiers for any wearable.

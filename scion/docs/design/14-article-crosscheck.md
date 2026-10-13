# 14. Cross-check against the article

This is a word-by-word cross-check of the design package against [*Redesigning source control at Anthropic*](https://www.anthropic.com/engineering/redesigning-source-control), in both directions:

1. **Article → package:** every sentence (so every word) of the article is accounted for, and every distinct term is checked for presence.
2. **Package → article:** every quotation, every number and every section citation that the package attributes to the article is verified against the article's exact text.

The article was re-downloaded for this check. The page HTML is byte-identical to the copy the package was written from (SHA-256 `fd24ca716476bcbd…`). The article is split into **182 units** (title, metadata, headings, figure captions, sentences, credits, footnote) holding **3,780 words**. A token-by-token comparison proves the units contain exactly the article's words, with none dropped or added. To avoid republishing the article, this report shows only the opening words of each sentence. Use the IDs to find the full sentence in the article.

## 14.1 Summary

| Check | Result |
|---|---|
| Sentences mapped (A) | 182 of 182 units mapped, each exactly once |
| Verdicts | Covered 110 · Context recorded 14 · **Fixed in this pass 25** · Partial 6 · Not applicable 27 |
| Term coverage (B) | content terms present in the package: 783 of 1,023 before this pass, **825 of 1024 after**. The remaining 199 were each reviewed: 14 names/credits, 49 present in other words, 136 narrative wording with no design content |
| Quotations (C) | 54 quoted spans in the package: 35 verbatim in the article; the other 19 are diagram labels, code examples or the package's own phrases. **4 misquotes found and fixed** |
| Numbers (C) | 16 figures attributed to the article: all match. **4 wording errors found and fixed** |
| Section citations (D) | 110 requirement citations, all using the 7 defined labels (00 conventions); each verified by at least one mapped sentence in the cited section. **2 invalid labels and 15 incomplete mappings found and fixed** |
| Requirements traced to article text | 133 of 158 map to at least one article sentence. The other 25 are labelled 'Derived' (engineering additions) or 'Project constraint', never attributed to the article |

## 14.2 What the cross-check changed

**Misquotes and wording errors (corrected)**
- 03 FR-LD-02 quoted "haven't been able to replicate … a global repository lock", which dropped "effectively". It now quotes the full sentence.
- 03 FR-MG-06 quoted "Scion only answered these metadata queries" without the article's quotation marks around *metadata*. It is now paraphrased with the marks.
- FEATURES.md put "30,000 merges per day" in quotation marks. The article says "we merged over 30,000 per day".
- FEATURES.md titled §5 "Contributing to the ecosystem". The heading is "Contributing to the wider ecosystem".
- 01 said history is "about 100 GB". The article says "almost 100 GB".
- 01 said "from about 2,500 to more than 30,000 … in four months", an inference. It now gives the article's dates (May 2026 and September).
- 01 listed "shallow, sparse and promisor clones". The article lists "shallow clones, sparse checkouts, and promisor remotes".
- NFR-02 gave 25M checkouts per day without noting that this is CI alone, before developer environments, agent sandboxes and research jobs.
- FEATURES.md called the CI result a "25% CPU saving". The article says "a 25% CPU capacity win".
- "§Introduction" (5 uses) named a heading that doesn't exist; the opening section is untitled, so it is now "§Opening". "§Rethinking priors" was a paragraph, not a section. The shorthands "§Growing" and "§Scaling" were normalized. Section labels are now defined in 00.

**Article content that was missing from the package (added)**
- 01 §1.1: the 'more than tenfold' framing; seeds falling behind the tip; history operations on partial clones; mirrors' disk *or* memory limits.
- 01 §1.4: builds and CI systems as explicit non-goals (Scion integrates with CI as a client and through post-merge testing).
- 01 G-3: the 25% CPU capacity win; G-4: 'cheap, programmatic access' instead of local copies or vendor-specific APIs.
- 03 NFR-05: rebase and merge must also be fast, not only commits ('each of those operations needs to be fast').
- 03 FR-OP-03: the three superfans the article names. New **FR-OP-08**: superfans read logs as well as telemetry (a gap in the prototype, GAP-14).
- 07 §7.2: prior art (Google's Piper, Meta's Sapling) and the ecosystem ideas the design embodies; 07 §7.11: the ADRs record the human-owned design-level tradeoffs.
- 02: GitHub, GitLab and the OSS community as named ecosystem partners. 08: 'safety, security, and compliance'. 13: refs are 'pointers to commits, such as branches and tags'.
- 12 §12.5/§12.6/§12.8: the process lessons. Engineers tell agents 'no'; agents may violate core constraints (the linear commit-log scan example); adversarial review can be myopic and must not drive over-engineering; reviewers examine intent rather than every line.

**Items flagged for your decision**
- **FR-OBJ-04** (hash verification at the daemon and client) is not stated in the article. Given the article's warning about over-defensive validation (A135), it is flagged; it is kept because a hash check is cheap.
- **BR-06** goes beyond footnote 1: lines and files taken verbatim from another parent keep their original history. The article calls first-parent storage 'a stylistic choice' and says people only care about main-line history.
- **Partial items:** distributed data (A053, single-host metadata store in the prototype), lower CPU than git servers (A094, not measured), resumability (A098, GAP-01), superfans as Claude agents in Slack (A148–A149, out of scope), and superfan access to logs (A152, new FR-OP-08, GAP-14).

## 14.3 Sentence-by-sentence map (A)

Categories:
- **REQ:** describes system behavior
- **FACT:** a number or fact
- **CTX:** context or narrative
- **PROC:** a process lesson
- **HEAD / CAP / META / CRED:** heading, figure caption, page metadata, credits


### Opening

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A000 | Redesigning source control at Anthropic | META | README; FEATURES title | Covered | Article title; the package links the article URL. |
| A001 | Published Oct 13, 2026 | META | 00 conventions (source URL) | Not applicable | Publication date, not a requirement. |
| A002 | As our merges per day grew more than tenfold, … | FACT | 01 §1.1; G-1; NFR-01 | Fixed in this pass | Was paraphrased; 01 §1.1 now states 'more than tenfold' and 'biggest development bottleneck' explicitly. |
| A003 | Here, we share how we migrated to an in-house … | FACT | 01 §1.1; FEATURES §6; 12 M4–M5 | Context recorded | Five-month migration timeline is context; migration itself is FR-MG-*. |
| A004 | At Anthropic, coding is no longer the bottleneck to … | CTX | 01 §1.1 | Context recorded |  |
| A005 | Claude is able to autonomously iterate on research loops, … | CTX | 01 §1.1 | Context recorded | Paraphrased as 'AI agents write and merge code faster…'. |
| A006 | The bottleneck, now, is all of the developer infrastructure … | CTX | 01 §1.1; 01 §1.4 out of scope | Fixed in this pass | Builds and CI systems themselves were not stated as out of scope; now listed explicitly (Scion integrates with CI as a client and via post-merge testing). |
| A007 | In May 2026, Anthropic averaged around 2,500 code changes … | FACT | 01 §1.1; NFR-01 | Fixed in this pass | 01 said '2,500 to more than 30,000 in four months' (an inference); now quotes the dates: around 2,500/day in May 2026, over 30,000/day as of September. |
| A008 | We don’t expect this rate of growth to slow … | FACT | 01 §1.1; NFR-01 (10× headroom) | Covered |  |
| A009 | Changes merged to our monorepo per day, from January … | CAP | — | Not applicable | Chart image; its data points are not in the text. |
| A010 | In order to support this growth, we built Scion, … | FACT | 01 §1.2; 12 §12.1 | Covered |  |
| A011 | We also built and shipped a code review surface … | REQ | F-27…F-31 (Antique), F-39/F-45 (code search), F-22…F-26 (IAM), F-30 (landing); FR-RV-*, FR-SR-*, FR-IAM-*, FR-LD-* | Covered | The article names these systems but does not specify them; their detailed requirements are marked 'Derived' in 03. |
| A012 | In this post, we’ll focus on how we built … | CTX | 03 source column ('Derived') | Context recorded | Explains why Antique/IAM/search requirements are mostly derived. |
| A013 | It makes for an interesting case study: Claude’s ability … | CTX | — | Not applicable | Narrative. |

### Growing our monorepo

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A014 | Growing our monorepo | HEAD | §Growing our monorepo | Covered | Cited as a source section. |
| A015 | Before we explore what we built, we should acknowledge … | CTX | 01 AS-03 | Context recorded |  |
| A016 | Unsurprisingly, Anthropic uses Claude to write software far more … | CTX | 01 §1.1 | Context recorded |  |
| A017 | Source control is just one example of this. | CTX | — | Not applicable | Narrative. |
| A018 | While we don’t expect many organizations to have these … | CTX | 02 stakeholders (wider ecosystem) | Context recorded |  |
| A019 | Git is a decentralized system: every clone is a … | CTX | 01 §1.1 | Covered |  |
| A020 | For the vast majority of repositories, this is the … | CTX | 01 §1.4 (not a general git replacement) | Covered |  |
| A021 | As our monorepo grows, it increasingly doesn’t fit that … | CTX | 01 §1.1 | Covered |  |
| A022 | The history of our main branch alone is almost … | FACT | 01 §1.1; NFR-03 | Fixed in this pass | 01 said 'about 100 GB'; corrected to 'almost 100 GB'. |
| A023 | We perform on the order of 25 million code … | FACT | 01 §1.1; NFR-02; 02 actors (CI, agent sandbox, research job); 06 §6.3 | Fixed in this pass | NFR-02 now says 25M/day is CI alone, before developer environments, agent sandboxes and research jobs. |
| A024 | Fetched naively, that would be over 600 PB of … | FACT | 01 §1.1; 07 §7.8 (25M × 25 GB ≈ 625 PB) | Covered | Arithmetic re-checked: 25×10⁶ × 25×10⁹ B = 625 PB. |
| A025 | Git offers tools for working with a slice of … | CTX | 01 §1.1 | Fixed in this pass | 01 said 'shallow, sparse and promisor clones'; corrected to 'shallow clones, sparse checkouts, and promisor remotes'. |
| A026 | Beyond these, there are standard workarounds for large monorepos, … | CTX | 01 §1.1; FR-TIER-03 (Scion's own snapshots) | Covered |  |
| A027 | We’ve used all of them—at our peak, we operated … | FACT | 01 §1.1 | Covered |  |
| A028 | This bought us time, but they became harder to … | CTX | 01 §1.1 | Covered |  |
| A029 | Seeds fell further from the tip of main between … | CTX | FR-TIER-03 (periodic refresh); FR-QRY-06/07 (history server-side) | Fixed in this pass | Requirements already answered both problems; 01 §1.1 now states the seed-staleness and partial-clone history problems explicitly. |
| A030 | The typical setup for scaling git checkouts. | CAP | — | Not applicable | Diagram image of the old git setup; the package models only the new architecture. |
| A031 | Taking a step back, we noticed that, like most … | CTX | AS-01; ADR-01 | Covered |  |
| A032 | The properties that make git excellent for distributed, offline … | CTX | 01 §1.1 | Covered |  |
| A033 | So we asked ourselves: if we designed source control … | CTX | 01 §1.2 vision | Covered |  |

### Principles for agent-scale source control

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A034 | Principles for agent-scale source control | HEAD | §Principles | Covered | Cited as a source section. |
| A035 | With agentic coding, many common assumptions about how software … | CTX | — | Not applicable | Narrative. |
| A036 | We embraced these changes when building Scion, which allowed … | CTX | 07 §7.2 | Covered |  |
| A037 | Source control for huge monorepos has prior art, notably … | CTX | 07 §7.2 | Fixed in this pass | Prior art (Google's Piper, Meta's Sapling) was missing from the architecture; added. |
| A038 | Our principles are: | HEAD | — | Not applicable |  |
| A039 | Clients are always online. | REQ | AS-01; ADR-01; FR-CS-01 | Covered |  |
| A040 | Git assumes that clients work offline and need a … | CTX | 01 §1.1 | Covered |  |
| A041 | Since nearly all of our clients are agents and … | REQ | AS-01; FR-FP-01…04; FR-CL-10 | Covered |  |
| A042 | Client-server asymmetry. | REQ | ADR-01 | Covered |  |
| A043 | In git, every client is capable of being a … | CTX | 01 §1.1 | Covered |  |
| A044 | In Scion, the server answers questions about file history … | REQ | FR-QRY-06, FR-QRY-07, FR-CS-01, FR-WR-02, FR-WR-03 | Covered |  |
| A045 | The client maintains a bounded local object cache, lays … | REQ | FR-CL-02, FR-CL-03, FR-CL-04, FR-CL-05, FR-CL-11 | Covered |  |
| A046 | It can compute very little on its own but, … | REQ | FR-CS-01; FR-QRY-10; FR-OBJ-05 | Covered |  |
| A047 | A comprehensive source control service can power many novel … | REQ | G-4 | Covered |  |
| A048 | With git, a CI job or tool that needs … | CTX | G-4 | Fixed in this pass | G-4 now names the alternative the article rejects: a local copy or vendor-specific APIs. |
| A049 | With Scion, all of the source control queries the … | REQ | FR-QRY-10; FR-QRY-* | Covered |  |
| A050 | Many internal tools, such as our automated bisect and … | REQ | FR-AUT-01, FR-AUT-02, FR-WR-04; UC-20, UC-21 | Covered |  |
| A051 | Everything must be horizontally scalable. | REQ | NFR-07 | Covered |  |
| A052 | At our peak, we ran several hundred git mirrors, … | FACT | 01 §1.1 | Covered |  |
| A053 | In Scion, the repository’s data is distributed, and every … | REQ | NFR-07; FR-OBJ-05 | Partial | Design covers it; the prototype's metadata store is single-host (ADR-10, R-02, WP-15). |
| A054 | There is no equivalent of packfiles (git’s compressed bundles … | REQ | FR-OBJ-02, FR-OBJ-03, NFR-14 | Covered |  |
| A055 | Commits must be cheap, incremental, and lock-free. | REQ | FR-CS-05, FR-CS-09, NFR-05 | Covered |  |
| A056 | In git, you commit locally and then push to … | CTX | FR-CL-06 | Covered |  |
| A057 | In Scion, every commit, rebase, or merge happens on … | REQ | FR-CS-01, FR-WR-02, FR-WR-03, FR-CL-06, FR-CL-08, NFR-05 | Fixed in this pass | 'each of those operations needs to be fast' — NFR-05 covered commits only; extended to rebase and merge. |
| A058 | The cost of creating a commit and updating its … | REQ | FR-CS-09, NFR-05 | Covered |  |
| A059 | The development lifecycle in Scion discourages refs (pointers to … | REQ | FR-REF-01, FR-REF-03, FR-REF-05, FR-RV-01; glossary 'Ref' | Fixed in this pass | Glossary now uses the article's definition: pointers to commits, such as branches and tags. |
| A060 | The working copy is optional, and sparse by design. | REQ | FR-CL-01, FR-QRY-04, FR-WR-01 | Covered |  |
| A061 | Because our monorepo is so large, and because we … | FACT | NFR-02; G-4 | Covered |  |
| A062 | With Scion, a CI job that needs the diff … | REQ | FR-QRY-04; UC-10 | Covered |  |
| A063 | The same goes for writes: many write workloads can … | REQ | FR-WR-01; UC-07 | Covered |  |
| A064 | Scion’s protocol is centered around sparse checkouts, which only … | REQ | FR-CL-01, FR-CL-10, FR-FP-04; UC-01, UC-02 | Covered |  |

### How Scion works

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A065 | How Scion works | HEAD | — | Covered | Parent heading of 'Data structures' and 'Scaling Scion'. |
| A066 | It’s helpful to understand how these principles came together … | CTX | — | Not applicable | Narrative. |
| A067 | These insights can apply to other source control systems … | CTX | FEATURES §5 (ecosystem ideas) | Context recorded |  |

### Data structures

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A068 | Data structures | HEAD | §Data structures | Covered | Cited as a source section. |
| A069 | In Scion, the unit of work is a “changeset,” … | REQ | FR-CS-05; glossary 'Changeset', 'Write-ahead log' | Covered |  |
| A070 | A changeset stores most of what you’d expect from … | REQ | FR-CS-02 | Covered |  |
| A071 | But where a git commit stores a pointer to … | REQ | FR-CS-02, FR-CS-03; BR-06 | Covered |  |
| A072 | Changesets are created server-side and are available everywhere, instantly. | REQ | FR-CS-01, FR-CS-06 | Covered |  |
| A073 | The shape of a changeset in Scion. | CAP | 06 §6.1 domain model; 07 §7.6 | Covered | Image not in text; the package models the shape as a class diagram and an encoding. |
| A074 | This structure lets us accept changesets with very high … | REQ | FR-CS-05; NFR-01 | Covered |  |
| A075 | Scion does technically support refs, but since neither creating … | REQ | FR-REF-02, FR-LD-01, NFR-12; ADR-10 (SQLite stand-in for Spanner) | Covered |  |
| A076 | A changeset records only what’s changed, so on its … | CTX | FR-DD-08, FR-DD-09 | Covered |  |
| A077 | To answer those, Scion builds additional data structures from … | REQ | FR-DD-08, FR-DD-09, FR-DD-10, FR-QRY-06, FR-QRY-07 | Covered |  |
| A078 | We call everything that isn’t directly part of the … | REQ | FR-DD-01 | Covered |  |
| A079 | Each type of derived data is defined recursively, so … | REQ | FR-DD-02 | Covered |  |
| A080 | This mechanism has three benefits. | CTX | FR-DD-03, FR-DD-04 | Covered |  |
| A081 | First, we can easily add a new type of … | REQ | FR-DD-04; F-06; DERIVED_DATA.md | Covered |  |
| A082 | Second, for each type, we can choose whether to … | REQ | FR-DD-03 | Covered |  |
| A083 | And third, because the client never sees the internals … | REQ | FR-DD-04 | Covered |  |
| A084 | We’ve added new types of derived data many times … | REQ | FR-DD-11, FR-DD-12, FR-SR-01 | Covered |  |

### Scaling Scion

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A085 | Scaling Scion | HEAD | §Scaling Scion | Covered | Cited as a source section. |
| A086 | A small fleet of Scion servers provides source control … | REQ | FR-QRY-01, FR-QRY-03, FR-QRY-05, FR-FP-05; 06 §6.3 | Covered |  |
| A087 | All source control data is content-addressed, so a piece … | REQ | FR-OBJ-01; NFR-12; AS-05 | Covered |  |
| A088 | As a result, the servers are horizontally scalable and … | REQ | NFR-07 | Covered |  |
| A089 | They are essentially large caches that can also compute … | REQ | FR-DD-05 | Covered |  |
| A090 | Scion’s many consumers no longer need to maintain local … | REQ | G-4; FR-QRY-10 | Covered |  |
| A091 | Fetching and maintaining the repository used to be a … | CTX | FR-QRY-05, FR-QRY-07 | Covered |  |
| A092 | Early in the migration, before we had our own … | REQ | FR-MG-06; F-34 | Covered |  |
| A093 | Fetching file contents and materializing working copies are far … | CTX | FR-FP-*, FR-TIER-* | Covered |  |
| A094 | Scion’s scn client deviates from git’s fetch protocols in … | REQ | FR-FP-01…06; ADR-04; NFR-17 | Partial | Lower CPU than git servers is a design goal (NFR-17) but is not measured against git (status P). |
| A095 | Scion’s negotiation doesn’t tell the server what the client … | REQ | FR-FP-01 | Covered |  |
| A096 | Starting from a root tree, the client checks its … | REQ | FR-FP-02, FR-DD-07 | Covered |  |
| A097 | Every request is for a specific object that never … | REQ | FR-FP-05, FR-FP-06; FR-TIER-* | Covered |  |
| A098 | The process is also efficient and resumable, because there … | REQ | FR-FP-03 | Partial | Required by the design; the prototype cannot resume an interrupted clone in place (GAP-01). |
| A099 | Sparse and even virtualized checkouts don’t need special support, … | REQ | FR-FP-04 | Covered |  |
| A100 | In the fleet, the client talks over a socket … | REQ | FR-TIER-01, FR-CL-12 | Covered |  |
| A101 | Most of our nodes need access to the monorepo, … | REQ | FR-TIER-01 (rationale) | Covered |  |
| A102 | Each daemon starts from a periodically refreshed snapshot, then … | REQ | FR-TIER-03, FR-TIER-04, FR-TIER-11, FR-AD-02 | Covered |  |
| A103 | These cache servers stream objects directly from memory, in … | REQ | FR-TIER-05, FR-FP-06 | Covered |  |
| A104 | When a cache is missing an object, it asks … | REQ | FR-TIER-06 | Covered |  |
| A105 | The scion-daemon, scion-cache, and scion-server all respond to identical … | REQ | FR-FP-05, FR-CL-12 | Covered |  |
| A106 | Any tier could theoretically talk to any other, but … | REQ | FR-TIER-07; NFR-08 | Covered |  |
| A107 | We want to avoid a situation where a failure … | REQ | NFR-08; 07 §7.9 | Covered |  |
| A108 | Scion’s checkout architecture. | CAP | 06 §6.2, §6.3 | Covered | Image not in text; reconstructed as component and deployment diagrams. |
| A109 | Each tier of this system maintains a cache hit … | REQ | NFR-02; FR-TIER-08; FR-OP-02 | Covered |  |
| A110 | Our Scion infrastructure footprint is now 200x smaller than … | FACT | G-3; NFR-17 | Covered | Recorded as a target; not measurable in a single-host prototype. |
| A111 | CI and research jobs check out code two orders … | FACT | G-2; NFR-04; G-3 | Fixed in this pass | The 25% CPU capacity win is now in G-3, worded as the article words it. |
| A112 | Neither clients nor caches need to perform repository maintenance, … | REQ | FR-OBJ-03 | Covered |  |

### What we learned building Scion

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A113 | What we learned building Scion | HEAD | §What we learned | Covered | Cited as a source section. |
| A114 | We started building Scion around the same time as … | CTX | FEATURES §6 | Context recorded |  |
| A115 | Both of these releases simultaneously amplified the need for … | CTX | — | Not applicable | Narrative. |
| A116 | Here’s a particularly striking example. | CTX | — | Not applicable | Narrative. |
| A117 | Earlier in the year, we had largely handwritten the … | REQ | FR-MG-01 | Covered |  |
| A118 | We thought it was good—until we got our hands … | CTX | — | Not applicable | Narrative. |
| A119 | We asked it to rewrite the whole thing, and … | REQ | FR-MG-02, FR-MG-04; FEATURES §6 | Covered | Memory and speed ratios are context; the ordering invariant is FR-MG-02. |
| A120 | Merged changes to the Scion and Antique codebases per … | CAP | — | Not applicable | Chart image; data not in the text. |
| A121 | What we learned building and operating Scion offers some … | CTX | — | Not applicable | Narrative. |
| A122 | Rapid development with a small team will become more … | CTX | CON-05; 12 §12.8 | Context recorded |  |
| A123 | A team of seven people built both Scion and … | FACT | FEATURES §6; CON-05 | Covered | 'Half a dozen related systems' are unnamed in the article; the package's related systems are its own choice. |
| A124 | We did all this while the volume of code … | FACT | 01 §1.1 | Covered |  |
| A125 | In the past, developing and deploying a source control … | CTX | — | Not applicable | Narrative. |
| A126 | We think this sort of fast, nimble migration will … | CTX | — | Not applicable | Narrative. |
| A127 | Engineers are no less valuable, but their work is … | PROC | 12 §12.8 roles | Context recorded |  |
| A128 | All of the engineers who worked on this system … | CTX | — | Not applicable | Narrative. |
| A129 | But our engineers still supplied the invaluable understanding of … | PROC | 07 §7.11 ADRs; 12 §12.8 | Fixed in this pass | 07 now states that ADRs record the design-level tradeoffs that humans own. |
| A130 | Very often, we found that the role of the … | PROC | 12 §12.5 DoD #1; 12 §12.6 | Covered | Definition of Done: implement exactly the referenced requirements, nothing more. |
| A131 | Agents will sometimes violate core system constraints to satisfy … | PROC | 12 §12.6; R-14 | Fixed in this pass | 12 §12.6 now names this risk and the guard: changes must cite requirement IDs and respect ADRs. |
| A132 | This was particularly common in our migration. | PROC | — | Context recorded |  |
| A133 | For example, there were multiple systems that tried to … | REQ | FR-LD-05; UC-17 | Covered |  |
| A134 | Anthropic also makes extensive use of adversarial review, and, … | PROC | 12 §12.5 | Fixed in this pass | Added to the DoD: findings from adversarial or automated review are weighed against the requirements; hypothetical concerns do not justify extra complexity. |
| A135 | For example, one such review was overly defensive about … | PROC | 12 §12.5; FR-OBJ-04 note | Fixed in this pass | Flags FR-OBJ-04 (hash verification at daemon and client) as a 'Derived' requirement the article does not state; kept because a hash check is cheap, but listed for your review. |
| A136 | Our team members still review every change request for … | PROC | 12 §12.8 reviewer role | Fixed in this pass | The reviewer role now says it reviews intent against requirements rather than every line. |
| A137 | We were able to substantially improve optimization and quality. | CTX | NFR-15 | Context recorded |  |
| A138 | By virtue of Claude’s ability to write immense amounts … | REQ | NFR-15 | Covered |  |
| A139 | Even on our tight timeline, we were able to … | REQ | NFR-15; FR-OP-06; T-SIM-01; T-FUZZ-01 | Covered |  |
| A140 | Claude also casually found significant optimizations—for example, an algorithmic … | REQ | FR-DD-10; NFR-06; ADR-12 | Covered | The article does not describe the optimization; the skip-list design is the package's own (Derived). |
| A141 | Observed performance improvements on native Scion repos. | CAP | T-PERF-01 | Not applicable | Chart image; data not in the text. The package measures its own benchmarks. |
| A142 | We laid the groundwork for new forms of monorepo … | REQ | F-22…F-26; 08 | Covered |  |
| A143 | Managing safety, security, and compliance in a massive monorepo … | CTX | 02; 08 §8.1 | Fixed in this pass | 08 now names safety, security and compliance together, as the article does. |
| A144 | We built Scion with these in mind from the … | CTX | 08 | Covered |  |
| A145 | It supports rich access control on repositories, as well … | REQ | FR-IAM-01, FR-IAM-02, FR-IAM-03, NFR-10 | Covered | FR-IAM-02 (multiple repositories) is a gap in the prototype (GAP-06). |
| A146 | Furthermore, the code review tooling we built can express … | REQ | FR-RV-05, FR-RV-06, FR-RV-07; BR-03 | Covered |  |
| A147 | A new level of operational excellence is possible. | CTX | G-7 | Covered |  |
| A148 | Our team uses Claude Tag heavily, which has helped … | REQ | FR-OP-03, NFR-16; 01 §1.4 | Partial | Superfan telemetry watcher is in scope; the Claude agent itself is out of scope (01 §1.4). |
| A149 | For example, we created Slack channels where we tasked … | REQ | FR-OP-03, FR-OP-05 | Partial | Findings go to a Slack-compatible webhook; an agent in the channel is a deployment concern. |
| A150 | We call these Claudes “superfans.” | REQ | FR-OP-03; glossary 'Superfan' | Covered |  |
| A151 | We have a scion-daemon superfan, a scion-cache superfan, an … | REQ | FR-OP-03 | Fixed in this pass | FR-OP-03 now names the three components the article lists; the Antique landing queue is watched through the server's Antique counters. |
| A152 | They have access to our telemetry and logs, and … | REQ | FR-OP-01, FR-OP-02, FR-OP-03, FR-OP-08 | Partial | Superfans read /stats telemetry; access to logs is not specified. Added to FR-OP-03 as a Should. |
| A153 | We also have traditional alerts for all of our … | REQ | FR-OP-04, FR-OP-03 | Covered |  |
| A154 | We’re completely rethinking our priors. | CTX | ADR-07, ADR-08 | Covered |  |
| A155 | This project prompted us to take a very hard … | CTX | — | Not applicable | Narrative. |
| A156 | A proper merge queue, for example, doesn’t make much … | REQ | FR-LD-02; ADR-07 | Covered |  |
| A157 | What does CI even mean when hundreds or even … | CTX | ADR-08 | Covered |  |
| A158 | We haven’t been able to effectively replicate the industry … | REQ | FR-LD-01, FR-LD-02, FR-LD-07; FR-PM-01…05 | Fixed in this pass | 03 quoted this as 'haven't been able to replicate … a global repository lock' (dropped 'effectively'); now quoted exactly. |
| A159 | This does mean that concurrent changes can conflict, but … | REQ | FR-LD-04; UC-16 | Covered |  |

### Contributing to the wider ecosystem

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A160 | Contributing to the wider ecosystem | HEAD | §Contributing to the wider ecosystem | Fixed in this pass | FEATURES.md called it 'Contributing to the ecosystem'; corrected. |
| A161 | We see Scion as just one part of the … | CTX | — | Not applicable | Narrative. |
| A162 | We’re sharing these details as an example of how … | CTX | 01 §1.4 | Covered |  |
| A163 | Scion is by no means a suitable replacement for … | CTX | 01 §1.4; README | Covered | Quoted verbatim in README and 01. |
| A164 | The concepts we’ve outlined here really only make sense … | CTX | 01 §1.4; README | Covered |  |
| A165 | Plus, Anthropic is unique in that our ability to … | CTX | — | Not applicable | Business context. |
| A166 | We do this both to address our own software … | CTX | — | Not applicable | Business context. |
| A167 | Practically speaking, it’s difficult to offer Scion in a … | CTX | 01 §1.4 (no productization) | Covered |  |
| A168 | It diverges significantly from git, meaning companies would need … | CTX | 01 §1.3–1.4 | Fixed in this pass | Scope includes its own code review and code search; a CI system is now listed as out of scope (Scion provides post-merge testing hooks). |
| A169 | Our internal versions of these components are highly bespoke, … | CTX | — | Not applicable | Narrative. |
| A170 | However, we anticipate that this class of problems will … | CTX | 02 (wider ecosystem) | Context recorded |  |
| A171 | Given that, we think the most impactful thing we … | CTX | FEATURES §5; docs/API.md | Covered |  |
| A172 | A git server doesn’t have to work the same … | CTX | FEATURES §5 (E1); 07 §7.2 | Fixed in this pass | 07 now records the ecosystem ideas the design embodies (server unlike client, standard server RPCs, want-only negotiation, composable sparse/shallow). |
| A173 | Git platforms can provide comprehensive server-side RPCs like Scion, … | CTX | FEATURES §5 (E2); docs/API.md | Covered |  |
| A174 | The negotiation protocol doesn’t have to look exactly like … | CTX | FEATURES §5 (E3, E4); ADR-04 | Covered |  |
| A175 | Lastly, we want to acknowledge that the git community … | CTX | — | Not applicable | Narrative. |
| A176 | Our contribution is far narrower: sharing our early view … | CTX | 02 (wider ecosystem) | Fixed in this pass | 02 now names GitHub, GitLab and the OSS community, as the article does. |
| A177 | We’re all in it together as the software development … | CTX | — | Not applicable | Narrative. |

### Acknowledgements

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A178 | Acknowledgements | HEAD | — | Not applicable |  |
| A179 | Written by Nick G. and the source control team: … | CRED | — | Not applicable | Credits. |

### Footnotes

| ID | Opening words | Cat | Maps to | Verdict | Note |
|---|---|---|---|---|---|
| A180 | Footnotes | HEAD | — | Not applicable |  |
| A181 | Storing changed files relative to the first parent of … | REQ | FR-CS-02; AS-04; BR-06 | Fixed in this pass | BR-06 extends the footnote: lines and files taken verbatim from another parent keep their original history. 03 now says explicitly that this is an extension beyond the article's 'stylistic choice', for your review. |

## 14.4 Every term (B)

Every distinct word of the article (1,024 content terms after removing function words) was searched for in the package, including inflections. 825 are present. Each of the remaining 199 was reviewed by hand:

| Term | Classification | Where the concept lives | Article units |
|---|---|---|---|
| 10x | Present in other words | 10× (NFR-01, 01 §1.1) | A124 |
| ability | Narrative wording (reviewed: no design content) | — | A013, A032, A138, A145 |
| accelerated | Narrative wording (reviewed: no design content) | — | A115 |
| achieve | Narrative wording (reviewed: no design content) | — | A129 |
| acknowledge | Narrative wording (reviewed: no design content) | — | A015, A175 |
| acknowledgements | Credits / names | — | A178 |
| actively | Narrative wording (reviewed: no design content) | — | A032 |
| actually | Narrative wording (reviewed: no design content) | — | A064, A169 |
| additional | Present in other words | FR-DD-08…10 | A077 |
| adopt | Narrative wording (reviewed: no design content) | — | A169 |
| agentic | Narrative wording (reviewed: no design content) | — | A035, A176 |
| ambitious | Credits / names | — | A179 |
| amir | Credits / names | — | A179 |
| among | Narrative wording (reviewed: no design content) | — | A138 |
| amplified | Narrative wording (reviewed: no design content) | — | A115 |
| anticipate | Narrative wording (reviewed: no design content) | — | A170 |
| anytime | Narrative wording (reviewed: no design content) | — | A008 |
| autonomously | Narrative wording (reviewed: no design content) | — | A005 |
| away | Narrative wording (reviewed: no design content) | — | A134 |
| benefits | Present in other words | FR-DD-03/04 | A080, A145 |
| better | Narrative wording (reviewed: no design content) | — | A128, A152 |
| blog | Narrative wording (reviewed: no design content) | — | A123 |
| bought | Narrative wording (reviewed: no design content) | — | A028 |
| brings | Narrative wording (reviewed: no design content) | — | A107 |
| bundles | Present in other words | packfiles (FR-OBJ-02) | A054 |
| burden | Narrative wording (reviewed: no design content) | — | A091 |
| capable | Narrative wording (reviewed: no design content) | — | A043, A161 |
| casually | Narrative wording (reviewed: no design content) | — | A140 |
| centered | Present in other words | FR-CL-01, FR-FP-04 | A064 |
| challenges | Narrative wording (reviewed: no design content) | — | A162, A170 |
| charts | Present in other words | FR-OP-03 (telemetry) | A152 |
| codebases | Present in other words | chart caption; NFR-15 | A120, A138 |
| colin | Credits / names | — | A179 |
| commonplace | Narrative wording (reviewed: no design content) | — | A170 |
| companies | Narrative wording (reviewed: no design content) | — | A031, A168 |
| company | Narrative wording (reviewed: no design content) | — | A016, A125, A170 |
| considerations | Narrative wording (reviewed: no design content) | — | A162 |
| dan | Credits / names | — | A179 |
| data-intensive | Present in other words | FR-FP-*, FR-TIER-* | A093 |
| deal | Narrative wording (reviewed: no design content) | — | A013, A027 |
| decades | Narrative wording (reviewed: no design content) | — | A175 |
| dedicated | Present in other words | FR-DD-08/09 | A077 |
| departing | Narrative wording (reviewed: no design content) | — | A171 |
| differentiate | Present in other words | FR-RV-05 | A146 |
| difficult | Narrative wording (reviewed: no design content) | — | A167, A169 |
| dozen | Narrative wording (reviewed: no design content) | — | A123 |
| easily | Present in other words | FR-DD-04 | A081, A123 |
| embraced | Narrative wording (reviewed: no design content) | — | A036 |
| encountered | Narrative wording (reviewed: no design content) | — | A139 |
| enormous | Narrative wording (reviewed: no design content) | — | A164 |
| equivalent | Present in other words | FR-OBJ-02 (no packfiles) | A054 |
| everyone | Narrative wording (reviewed: no design content) | — | A169 |
| evolving | Narrative wording (reviewed: no design content) | — | A035 |
| examine | Present in other words | 12 §12.8 (reviewing intent) | A136 |
| excellent | Narrative wording (reviewed: no design content) | — | A032 |
| excessive | Present in other words | 12 §12.5 (extra validation) | A135 |
| exchange | Narrative wording (reviewed: no design content) | — | A046 |
| exclusively | Present in other words | FR-FP-01 (only the objects wanted) | A095 |
| experience | Narrative wording (reviewed: no design content) | — | A018 |
| experienced | Present in other words | FR-OP-03 | A152 |
| expert | Narrative wording (reviewed: no design content) | — | A140 |
| explore | Narrative wording (reviewed: no design content) | — | A015 |
| extensive | Present in other words | 12 §12.5 (adversarial review) | A134 |
| face | Narrative wording (reviewed: no design content) | — | A170 |
| fact | Narrative wording (reviewed: no design content) | — | A033 |
| fit | Narrative wording (reviewed: no design content) | — | A021 |
| full-fledged | Present in other words | 01 §1.1 (every clone is a full repository) | A043 |
| fundamentally | Narrative wording (reviewed: no design content) | — | A036 |
| furthermore | Narrative wording (reviewed: no design content) | — | A146 |
| garrett | Credits / names | — | A179 |
| given | Narrative wording (reviewed: no design content) | — | A171 |
| grateful | Credits / names | — | A179 |
| ground | Narrative wording (reviewed: no design content) | — | A005 |
| groundwork | Present in other words | F-22…F-26 | A142 |
| grown | Present in other words | FR-DD-04 (new types added over time) | A084 |
| half | Narrative wording (reviewed: no design content) | — | A123 |
| handwritten | Present in other words | Mythos anecdote (FEATURES §6) | A117 |
| heavily | Present in other words | FR-OP-03 | A148 |
| helpful | Narrative wording (reviewed: no design content) | — | A066 |
| high-level | Present in other words | 07 §7.11 (design-level tradeoffs) | A129 |
| high-quality | Narrative wording (reviewed: no design content) | — | A013 |
| however | Narrative wording (reviewed: no design content) | — | A170 |
| identify | Present in other words | FR-LD-04 | A159 |
| immense | Narrative wording (reviewed: no design content) | — | A138 |
| impactful | Narrative wording (reviewed: no design content) | — | A171 |
| improve | Narrative wording (reviewed: no design content) | — | A137 |
| improvements | Narrative wording (reviewed: no design content) | — | A141, A172 |
| in-house | Present in other words | 01 §1.2 | A003, A010 |
| increase | Narrative wording (reviewed: no design content) | — | A008 |
| increased | Narrative wording (reviewed: no design content) | — | A028, A124 |
| increasingly | Narrative wording (reviewed: no design content) | — | A021, A161 |
| incredibly | Narrative wording (reviewed: no design content) | — | A134 |
| indices | Present in other words | indexes (FR-DD-11/12) | A084 |
| inefficient | Narrative wording (reviewed: no design content) | — | A170 |
| insights | Narrative wording (reviewed: no design content) | — | A067 |
| instructions | Present in other words | Mythos anecdote | A119 |
| inter-system | Present in other words | 07 §7.11 | A129 |
| intersects | Narrative wording (reviewed: no design content) | — | A177 |
| invaluable | Narrative wording (reviewed: no design content) | — | A129 |
| invested | Present in other words | FR-PM-* | A158 |
| involves | Present in other words | FR-REF-02 | A075 |
| iterate | Narrative wording (reviewed: no design content) | — | A005 |
| iterative | Narrative wording (reviewed: no design content) | — | A125 |
| january | Present in other words | chart captions (not in the text) | A009, A120 |
| joe | Credits / names | — | A179 |
| journey | Credits / names | — | A179 |
| knew | Narrative wording (reviewed: no design content) | — | A129 |
| laid | Present in other words | F-22…F-26 | A142 |
| lends | Present in other words | FR-FP-* (scalable architecture) | A094 |
| looming | Present in other words | FR-REF-01 (refs discouraged: global state) | A059 |
| made | Narrative wording (reviewed: no design content) | — | A174 |
| majority | Narrative wording (reviewed: no design content) | — | A020 |
| making | Narrative wording (reviewed: no design content) | — | A129 |
| meaningfully | Narrative wording (reviewed: no design content) | — | A115 |
| micro-optimize | Narrative wording (reviewed: no design content) | — | A005 |
| myopic | Present in other words | 12 §12.5 (weighing adversarial review) | A134 |
| neither | Narrative wording (reviewed: no design content) | — | A075, A112 |
| nick | Credits / names | — | A179 |
| nimble | Narrative wording (reviewed: no design content) | — | A126 |
| noticed | Narrative wording (reviewed: no design content) | — | A031 |
| one-dimensional | Present in other words | FR-OP-04 vs FR-OP-03 | A153 |
| opposed | Narrative wording (reviewed: no design content) | — | A136 |
| ourselves | Narrative wording (reviewed: no design content) | — | A033, A138 |
| outlined | Narrative wording (reviewed: no design content) | — | A164 |
| over-engineering | Present in other words | 12 §12.5 (no extra complexity for hypothetical concerns) | A134 |
| overall | Narrative wording (reviewed: no design content) | — | A058, A171 |
| overwhelms | Present in other words | NFR-08 (no overload of the tier above) | A107 |
| past | Narrative wording (reviewed: no design content) | — | A125 |
| perhaps | Narrative wording (reviewed: no design content) | — | A173 |
| please | Narrative wording (reviewed: no design content) | — | A169 |
| possible | Narrative wording (reviewed: no design content) | — | A147 |
| power | Narrative wording (reviewed: no design content) | — | A047 |
| practice | Narrative wording (reviewed: no design content) | — | A066, A181 |
| prolifically | Narrative wording (reviewed: no design content) | — | A164 |
| prompted | Narrative wording (reviewed: no design content) | — | A155 |
| r.k | Credits / names | — | A179 |
| rapid | Narrative wording (reviewed: no design content) | — | A122 |
| realistically | Narrative wording (reviewed: no design content) | — | A165 |
| resembles | Present in other words | tiered caches (FR-TIER-*) | A097 |
| s.g | Credits / names | — | A179 |
| seem | Narrative wording (reviewed: no design content) | — | A153 |
| self-contained | Present in other words | 01 §1.1 | A019 |
| sense | Narrative wording (reviewed: no design content) | — | A156, A164 |
| sergiu | Credits / names | — | A179 |
| setup | Narrative wording (reviewed: no design content) | — | A030 |
| shipped | Present in other words | F-27…F-45 | A011 |
| significant | Narrative wording (reviewed: no design content) | — | A091, A140, A172 |
| significantly | Narrative wording (reviewed: no design content) | — | A052, A094, A168 |
| simple | Present in other words | FR-RV-05 (comment-only changes) | A146 |
| simultaneously | Narrative wording (reviewed: no design content) | — | A115 |
| sizable | Narrative wording (reviewed: no design content) | — | A111 |
| skilled | Narrative wording (reviewed: no design content) | — | A134 |
| software | Narrative wording (reviewed: no design content) | — | A016, A035, A067, A121 |
| solution | Narrative wording (reviewed: no design content) | — | A162 |
| space | Narrative wording (reviewed: no design content) | — | A021 |
| speed | Narrative wording (reviewed: no design content) | — | A005 |
| stages | Narrative wording (reviewed: no design content) | — | A067 |
| steer | Narrative wording (reviewed: no design content) | — | A134 |
| strain | Narrative wording (reviewed: no design content) | — | A016 |
| strained | Narrative wording (reviewed: no design content) | — | A052 |
| strange | Present in other words | FR-OP-03 (novel findings) | A152 |
| striking | Narrative wording (reviewed: no design content) | — | A116 |
| substantially | Narrative wording (reviewed: no design content) | — | A137 |
| successful | Narrative wording (reviewed: no design content) | — | A171 |
| supplied | Narrative wording (reviewed: no design content) | — | A129 |
| suspect | Narrative wording (reviewed: no design content) | — | A018 |
| tackle | Narrative wording (reviewed: no design content) | — | A162 |
| taking | Narrative wording (reviewed: no design content) | — | A031 |
| technically | Present in other words | FR-REF-02 | A075 |
| theoretically | Present in other words | FR-TIER-07 (strict tiering) | A106 |
| thing | Narrative wording (reviewed: no design content) | — | A119, A171 |
| things | Narrative wording (reviewed: no design content) | — | A146 |
| though | Narrative wording (reviewed: no design content) | — | A162 |
| thought | Narrative wording (reviewed: no design content) | — | A118 |
| tight | Narrative wording (reviewed: no design content) | — | A139 |
| timeline | Narrative wording (reviewed: no design content) | — | A139 |
| together | Narrative wording (reviewed: no design content) | — | A066, A177 |
| tried | Narrative wording (reviewed: no design content) | — | A133 |
| tries | Narrative wording (reviewed: no design content) | — | A169 |
| truly | Narrative wording (reviewed: no design content) | — | A164 |
| tuning | Narrative wording (reviewed: no design content) | — | A140 |
| undermining | Narrative wording (reviewed: no design content) | — | A032 |
| unsurprisingly | Narrative wording (reviewed: no design content) | — | A016 |
| unusual | Narrative wording (reviewed: no design content) | — | A015 |
| useful | Narrative wording (reviewed: no design content) | — | A167, A169 |
| valuable | Narrative wording (reviewed: no design content) | — | A127 |
| various | Narrative wording (reviewed: no design content) | — | A174 |
| vast | Narrative wording (reviewed: no design content) | — | A020 |
| vilas | Credits / names | — | A179 |
| virtue | Narrative wording (reviewed: no design content) | — | A138 |
| week | Present in other words | chart caption | A120 |
| weeks | Narrative wording (reviewed: no design content) | — | A140 |
| well-defended | Present in other words | NFR-15 | A138 |
| well-tested | Present in other words | NFR-15 | A138 |
| worry | Narrative wording (reviewed: no design content) | — | A169 |
| wouldn't | Narrative wording (reviewed: no design content) | — | A050, A169 |
| year | Present in other words | Mythos anecdote (FEATURES §6) | A117 |
| years | Narrative wording (reviewed: no design content) | — | A125 |
| you'd | Narrative wording (reviewed: no design content) | — | A070 |

## 14.5 Quotations attributed to the article (C)

| File:line | Quoted text | Result |
|---|---|---|
| README.md:137 | is by no means a suitable replacement for git for general use | Verbatim in the article |
| docs/API.md:7 | : ...}`. Errors return `{ | Code / format example (not an article quote) |
| docs/DERIVED_DATA.md:19 |  else -1 if c.op ==  | Code / format example (not an article quote) |
| docs/FEATURES.md:1 | Redesigning source control at Anthropic | Verbatim in the article |
| docs/FEATURES.md:79 | What we learned | Verbatim in the article |
| docs/FEATURES.md:100 | Contributing to the wider ecosystem | Verbatim in the article |
| docs/design/00-process.md:51 | Growing our monorepo | Verbatim in the article |
| docs/design/00-process.md:52 | Growing our monorepo | Verbatim in the article |
| docs/design/00-process.md:53 | Principles for agent-scale source control | Verbatim in the article |
| docs/design/00-process.md:54 | How Scion works | Verbatim in the article |
| docs/design/00-process.md:55 | How Scion works | Verbatim in the article |
| docs/design/00-process.md:56 | What we learned building Scion | Verbatim in the article |
| docs/design/00-process.md:57 | Contributing to the wider ecosystem | Verbatim in the article |
| docs/design/01-vision-and-scope.md:68 | is by no means a suitable replacement for git for general use | Verbatim in the article |
| docs/design/01-vision-and-scope.md:73 | requires its own … CI | Verbatim in the article |
| docs/design/03-requirements.md:18 | available everywhere, instantly | Verbatim in the article |
| docs/design/03-requirements.md:68 | finding merge bases | Verbatim in the article |
| docs/design/03-requirements.md:79 | many write workloads can also skip the checkout | Verbatim in the article |
| docs/design/03-requirements.md:123 | ergonomic way to work with the server | Verbatim in the article |
| docs/design/03-requirements.md:128 | materialize files on demand | Verbatim in the article |
| docs/design/03-requirements.md:137 | access control on repositories | Verbatim in the article |
| docs/design/03-requirements.md:157 | complex semantic constraints | Verbatim in the article |
| docs/design/03-requirements.md:159 | a code review surface | Verbatim in the article |
| docs/design/03-requirements.md:168 | We haven't been able to effectively replicate the industry standard of a global repository lock on the merge q | Verbatim in the article |
| docs/design/03-requirements.md:170 | Claude can typically fix these conflicts | Verbatim in the article |
| docs/design/03-requirements.md:171 | asking our code review tool | Verbatim in the article |
| docs/design/03-requirements.md:206 | implicit invariants around ingestion ordering | Verbatim in the article |
| docs/design/03-requirements.md:208 | 20x less memory | Verbatim in the article |
| docs/design/03-requirements.md:220 | access to our telemetry and logs | Verbatim in the article |
| docs/design/03-requirements.md:223 | sophisticated rate limiting | Verbatim in the article |
| docs/design/03-requirements.md:245 | each of those operations needs to be fast | Verbatim in the article |
| docs/design/03-requirements.md:271 | a stylistic choice | Verbatim in the article |
| docs/design/03-requirements.md:271 | only care about history or blame for commits on the main line | Verbatim in the article |
| docs/design/04-feature-list.md:59 | When did this change land? | The package's own phrase (not an article quote) |
| docs/design/05-use-cases.md:15 | Scion: working with code | Diagram label (not an article quote) |
| docs/design/05-use-cases.md:45 | Antique: review and landing | Diagram label (not an article quote) |
| docs/design/05-use-cases.md:67 | Scion: automation and release | Diagram label (not an article quote) |
| docs/design/05-use-cases.md:88 | Scion: administration and operations | Diagram label (not an article quote) |
| docs/design/05-use-cases.md:353 |  findings for large deviations and  | Diagram label (not an article quote) |
| docs/design/06-uml.md:153 | Client side (developer machine, CI node, agent sandbox) | Diagram label (not an article quote) |
| docs/design/06-uml.md:172 | Server fleet: scion-server | Diagram label (not an article quote) |
| docs/design/06-uml.md:210 | Compute node x thousands | Diagram label (not an article quote) |
| docs/design/06-uml.md:222 | Server fleet (small) | Diagram label (not an article quote) |
| docs/design/07-architecture.md:88 | <kind> <id> <name>\n | Code / format example (not an article quote) |
| docs/design/07-architecture.md:161 | the design-level tradeoffs | Verbatim in the article |
| docs/design/07-architecture.md:173 | We're completely rethinking our priors | Verbatim in the article |
| docs/design/08-security.md:20 | Less trusted: job / agent sandbox | Diagram label (not an article quote) |
| docs/design/08-security.md:33 | TB1: unix socket, user identity | Diagram label (not an article quote) |
| docs/design/08-security.md:34 | TB2: network, service identity + on-behalf-of | Diagram label (not an article quote) |
| docs/design/08-security.md:35 | TB3: network, service identity + on-behalf-of | Diagram label (not an article quote) |
| docs/design/08-security.md:36 | TB4: network, user identity | Diagram label (not an article quote) |
| docs/design/12-project-plan.md:88 | overly defensive about trusting another internal service | Verbatim in the article |
| docs/design/13-glossary.md:13 | set X to new if X still equals expected | The package's own phrase (not an article quote) |
| docs/design/13-glossary.md:30 | pointers to commits, such as branches and tags | Verbatim in the article |

## 14.6 Numbers attributed to the article (C)

| Claim | Where in the package | Article unit | Status |
|---|---|---|---|
| Merges per day grew more than tenfold | 01 §1.1 | A002 | Matches |
| Around 2,500 changes merged per day in May 2026 | 01 §1.1 | A007 | Matches (fixed: was 'in four months', an inference) |
| Over 30,000 per day as of September | 01 §1.1; NFR-01; 07 §7.8 | A007 | Matches |
| Volume increased by 10x during the build | 01 §1.1 (tenfold) | A124 | Matches |
| Main-branch history almost 100 GB | 01 §1.1; NFR-03 | A022 | Matches (fixed: was 'about 100 GB') |
| Compressed working copy over 25 GB | 01 §1.1; NFR-03; 07 §7.8 | A022 | Matches |
| On the order of 25 million checkouts per day for CI | 01 §1.1; NFR-02; 07 §7.8 | A023 | Matches (fixed: NFR-02 now says CI alone) |
| Over 600 PB per day if fetched naively | 01 §1.1; 07 §7.8 (25M × 25 GB = 625 PB) | A024 | Matches; arithmetic re-checked |
| Several hundred internal git mirrors | 01 §1.1; FEATURES §6 | A027, A052 | Matches |
| Cache hit rate over 99% on each tier | G-2; NFR-02; FR-OP-02; FEATURES S17 | A109 | Matches |
| Footprint 200x smaller (CPU and memory) | G-3; FEATURES §6 | A110 | Matches |
| Checkouts two orders of magnitude faster (seconds, not minutes) | G-2; FEATURES §6 | A111 | Matches |
| CI realized a 25% CPU capacity win | G-3; FEATURES §6 | A111 | Matches (fixed: was 'CPU saving') |
| A team of seven people | FEATURES §6 | A123 | Matches |
| Fully migrated in five months | FEATURES §6 | A003, A010, A123 | Matches |
| Rewrite used 20x less memory and was 4x faster | FEATURES §6; FR-MG-04 source | A119 | Matches |

The package's own figures are engineering estimates, labelled as such in 07 §7.8, and not claimed as article facts. Examples: 10× headroom, 3.5 landings/s, a 20 MB sparse checkout, per-tier traffic.

## 14.7 Section citations (D)

| Label | Uses |
|---|---|
| §Principles | 31 |
| §Scaling Scion | 30 |
| §What we learned | 28 |
| §Data structures | 18 |
| §Growing our monorepo | 7 |
| §Opening | 6 |
| §Contributing to the wider ecosystem | 2 |

Every requirement that cites a section was checked automatically: at least one sentence in that section must map to the requirement. All 110 pass.

## 14.8 How to re-run

The checks are scripted (sentence segmentation, token-identity proof, term search, quote/number/citation verification). Like T-DOC-01/02, the scripts will be committed with WP-03 after M0, because code is frozen until the baseline is approved.

# 2. Stakeholders and actors

## 2.1 Stakeholders

| Stakeholder | Interest | Concerns | Success for them |
|---|---|---|---|
| Engineering leadership | developer throughput, cost | source control limiting merge rate; infrastructure spend | merge rate keeps growing without source control in the way |
| Human developers | fast, familiar workflows | learning a new tool; losing local history and offline work | checkout in seconds; status, commit and land feel like git or Sapling |
| Agent platform owners | agents work unattended | brittle or slow tooling; ambiguous errors | machine-readable APIs; no checkout needed for most tasks |
| CI and research infrastructure | cheap checkouts at very high volume | fleet CPU spent fetching repositories | node-local cache hits; sparse checkouts by default |
| Reviewers and code owners | spend attention where it matters | rubber-stamping noise; missing sensitive changes | trivial changes need little review; sensitive areas require owners |
| Security and compliance | protect sensitive code | leaks through caches, search or diffs | directory ACLs enforced on every path, including caches |
| SRE / operators | reliability with a tiny team | cascading failures; maintenance toil | stateless tiers; isolated failure domains; no gc or repack |
| Release managers | ship known-good revisions | broken main after lock-free landing | post-merge results and a deploy gate |
| Migration team | move off git safely | divergence between git and Scion | streaming, incremental, verifiable ingestion |
| Wider ecosystem (GitHub, GitLab, the OSS community, other git forges) | learn from the design; the article hopes to partner with them | — | the design ideas are documented (article §Contributing to the wider ecosystem) |

## 2.2 Actors

Primary actors start use cases. Supporting actors are systems the use cases depend on.

| ID | Actor | Type | Goals | Interfaces |
|---|---|---|---|---|
| ACT-01 | Developer | primary, human | check out, edit, commit, review, land | `scn` CLI, Antique UI |
| ACT-02 | Coding agent | primary, automated | same as a developer, at volume, often without a checkout | `scn`, RPC API |
| ACT-03 | CI / research job | primary, automated | check out a revision quickly; query diffs and ancestry | `scn` via the node daemon, RPC API |
| ACT-04 | Reviewer | primary, human | understand and approve changes | Antique UI, `scn review` |
| ACT-05 | Code owner | primary, human | approve changes to owned directories | Antique |
| ACT-06 | Repository administrator | primary, human | configure repositories, policies, protected refs; backfill data | policy files, `scion-admin` |
| ACT-07 | Security officer | primary, human | define and audit access restrictions | policy, ref logs, audit |
| ACT-08 | Operator (SRE) | primary, human | run, scale and fail over tiers; publish snapshots | `scion-server/cache/daemon`, `scion-admin` |
| ACT-09 | Release manager | primary, human | pick a deployable revision | `scion-admin deploy-gate` |
| ACT-10 | Migration engineer | primary, human | ingest and sync git history, verify it | `scion-admin ingest` |
| ACT-11 | Post-merge test runner | primary, system | test landed changes and revert failures | Antique post-merge API |
| ACT-12 | Bisect / revert pipeline | primary, system | find and undo culprits automatically | RPC API |
| ACT-13 | Superfan monitor | primary, system | watch one component and raise findings | `/stats`, `/logs`, webhook |
| ACT-19 | Superfan agent (Claude) | primary, system | investigate each finding and explain it in chat | read-only tools over `/stats` and `/logs`; the Claude Messages API; webhook |
| ACT-14 | Metadata store (Cloud Spanner; SQLite on one host) | supporting | durable changeset log, refs, derived values, reviews, queues, audit | `MetaStore` (Spanner REST API) |
| ACT-15 | Blob storage | supporting | durable compressed objects | `ObjectStore` |
| ACT-16 | git repository | supporting | migration source | `git` CLI |
| ACT-17 | Chat / alerting system | supporting | receive findings | webhook |
| ACT-18 | Identity provider | supporting | authenticate principals | tokens (prototype) |
| ACT-20 | Claude API | supporting | run the superfan agent's model | HTTPS Messages API |

## 2.3 Actor generalization

* **Coding agent** behaves as a **Developer**, and also uses API-only write paths.
* **CI job** behaves as a read-only **Developer** for checkouts and queries.
* **Code owner** behaves as a **Reviewer** with extra authority over the directories it owns.
* **Post-merge test runner** and **bisect / revert pipeline** are service principals. They may
  act on behalf of users, and may land without review when the policy allows it.

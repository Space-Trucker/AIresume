# 12. Project plan

## 12.1 Lifecycle

| Phase | Goal | Exit milestone | Status |
|---|---|---|---|
| Inception | vision, scope, stakeholders | M0a: 01–02 approved | approved 2026-10-13 |
| Elaboration | requirements, use cases, UML, architecture, risks, test plan, traceability, article cross-check | **M0: design baseline approved** | approved 2026-10-13, with the decisions in 12.7 |
| Construction | rebuild every requirement from this baseline, test-first, one traced work package at a time | B1–B5 | done (B5: every requirement **I**) |
| Transition | migration pilot, cut-over, operations | M4–M5 | not started |

> **Note on order.** A prototype was built before elaboration. At M0 the project lead decided to
> delete it and rebuild from this baseline (decision 2). It stays in git history (commits
> `31ab393`–`5914fad`), and its lessons are carried forward as findings D-01 to D-04 (11 §11.4).

## 12.2 Work breakdown

Each work package (WP) lists the requirements it delivers and the tests that prove them (10 §10.4).
A WP is done when its tests pass and its rows in 11 read **I** (12.5).

| WP | Milestone | Work | Requirements | Tests |
|---|---|---|---|---|
| WP-B1.1 | B1 | objects, storage, metadata store | FR-OBJ-01…05, FR-CS-03 | T-CORE-01/02 |
| WP-B1.2 | B1 | changesets, refs, revisions | FR-CS-01…08, FR-REF-01/02/04 | T-CORE-03…07 |
| WP-B1.3 | B1 | incremental trees and diffs | FR-CS-09, FR-QRY-03, NFR-05 | T-CORE-08/09/10 |
| WP-B1.4 | B1 | derived-data engine and the six types (main-line history and blame) | FR-DD-01…12, BR-06 | T-DD-01…08, T-FUZZ-01 |
| WP-B1.5 | B1 | queries, ancestry, merge, rebase, revert | FR-QRY-01…09, FR-WR-02…04, NFR-06, NFR-12 | T-DD-06, T-WR-01, T-FUZZ-01 |
| WP-B2.1 | B2 | RPC layer, deployment of many repositories, TLS and mutual TLS, rate limiting | FR-IAM-02, FR-IAM-07/08, FR-OP-01/02/06, NFR-20 | T-MR-01, T-TLS-01, T-OPS-01 |
| WP-B2.2 | B2 | server API and checkout-less writes; upload limit | FR-QRY-10, FR-WR-01/05/06/07 | T-CL-10, T-LIM-01 |
| WP-B2.3 | B2 | object protocol, daemon, cache, snapshots, strict tiering | FR-FP-01…07, FR-TIER-01…11 | T-TIER-01…08 |
| WP-B2.4 | B2 | `scn` client: full, sparse, virtual; resumable clone; fsmonitor; CLI | FR-CL-01…12, FR-FP-03 | T-CL-01…13 |
| WP-B3.1 | B3 | IAM: repository and directory rules, protected refs, release branches, re-index, audit log | FR-IAM-01/03…06/09…11, FR-REF-03/05, FR-AD-05, NFR-10 | T-IAM-01…10, T-AUD-01, T-REF-01, T-ADM-01 |
| WP-B3.2 | B3 | Antique: change requests, classification, semantic rules | FR-RV-01…08 | T-RV-01…06 |
| WP-B3.3 | B3 | landing: group commit, `landing` state, conflicts, landing index | FR-LD-01…07 | T-LD-01…03, T-SIM-01 |
| WP-B3.4 | B3 | interactive review UI and notifications | FR-RV-09/10 | T-RV-07/08 |
| WP-B4.1 | B4 | git ingestion | FR-MG-01…07 | T-MG-01…05 |
| WP-B4.2 | B4 | post-merge testing, deploy gate, bisect, revert pipeline | FR-PM-01…05, FR-AUT-01/02 | T-PM-01/02/04, T-AUT-01/02 |
| WP-B4.3 | B4 | code search: path index, grep, content index | FR-SR-01…04 | T-SR-01/02 |
| WP-B4.4 | B4 | superfans, alerts, logs; admin toolkit; backup and restore; the end-to-end demo | FR-OP-03…05/07/08, FR-AD-01…04/06 | T-OPS-02…04, T-BAK-01, T-PERF-01, T-ADM-02, T-E2E-01 |
| WP-B5.1 | B5 | system verification: stress, end to end, benchmarks, docs and traceability | NFR-01…04, NFR-13, NFR-15, NFR-17 | T-SIM-01, T-SYS-01…03, T-E2E-01, T-PERF-01, T-DOC-01/02 |
| WP-X | later | metadata-store adapter for a distributed database (Spanner) | R-02, NFR-07 | needs infrastructure |

## 12.3 Milestones

| Milestone | Contents | Exit criteria |
|---|---|---|
| **M0: design baseline** | documents 00–14 | approved 2026-10-13 (12.7) |
| **B1: core** | WP-B1.* | B1 rows in 11 read **I**; core and fuzz tests green |
| **B2: service and checkout** | WP-B2.* | B2 rows **I**; tier, client, multi-repository and TLS tests green |
| **B3: security, review, landing** | WP-B3.* | B3 rows **I**; 32×5 stress simulation green |
| **B4: migration, automation, operations** | WP-B4.* | B4 rows **I**; end-to-end demo green |
| **B5: system verification** | WP-B5.1 | every requirement **I**, or **P** with a recorded reason; docs checks green |
| **M4: migration pilot** | ingest a real repository; a metadata-only service for CI | verify reports zero mismatches |
| **M5: cut-over** | daemons on the nodes, caches per region, landing through Antique | git becomes read-only; 01 §1.7 measured |

Each milestone ends with a commit and push, and an update to 11 §11.3.

## 12.4 Definition of Ready (a work item may start when)

1. It references approved requirement IDs, and each has an acceptance criterion.
2. The use cases and diagrams affected are identified, or updated first.
3. The test cases are designed (IDs added to 10).
4. Risks and security impact are noted (08, 09).

## 12.5 Definition of Done

1. The code implements exactly the referenced requirements, nothing more. The article's lesson:
   the engineer's job is often to tell the agent "no".
2. Findings from adversarial or automated review are weighed against the requirements and ADRs.
   Hypothetical concerns do not justify extra validation or complexity. The article's example is a
   review that was "overly defensive about trusting another internal service".
3. New and updated automated tests pass, along with the full suite, the 32×5 stress simulation, and the docs checks (T-DOC-01 rendering, T-DOC-02 cross-references).
4. The traceability matrix (11) is updated: status, design element, tests.
5. User-facing docs are updated (README, API, FEATURES).
6. Committed with a message that names the work package and requirement IDs.

## 12.6 Change control

* **Requirement changes:** edit 03 with a new or changed ID; record why in the commit; update 04, 05 and 11 in the same change; T-DOC-02 must pass.
* **Architecture changes:** a new ADR row in 07 §7.11 (never edit an accepted ADR; supersede it).
* **Agents and core constraints:** the article reports that agents sometimes "violate core system
  constraints to satisfy a pattern that should never have been allowed in the first place".
  For example, systems found when a change merged by linearly reading the commit log instead of
  asking the code review tool. A change that bypasses an ADR or an indexed API (such as FR-LD-05) is
  rejected in review.
* **Code changes without a work item:** not allowed after M0, except fixes for severity-1 defects, which get a work item retroactively within the day.

## 12.7 Decisions at M0 (2026-10-13)

| # | Question | Decision |
|---|---|---|
| 1 | What is the project for? | **Everything in the plan**: required items, production hardening (TLS, audit, backup, upload limits) and every Should (multiple repositories, content index, interactive review UI, notifications, superfan logs) |
| 2 | Keep the prototype code or rebuild? | **Delete and rebuild** from this baseline |
| 3 | Keep hash verification of every object (FR-OBJ-04)? | **Keep** |
| 4 | Blame through merges (BR-06)? | **Main line only**, as the article describes (ADR-19) |
| 5 | Is multi-repository hosting a Must? | stays **Should**, and is in scope through decision 1 (default, not objected to) |
| 6 | D-02: a `landing` CR state? | **Yes**, as designed (default, not objected to) |

## 12.8 Roles

| Role | Responsibility | Who |
|---|---|---|
| Project lead / product owner | approves the baseline, prioritizes the gap list | you |
| Architect / implementer | maintains the package; implements work items | Claude |
| Reviewer | reviews every change request for the intent of the change against its requirements, rather than reading every line (as the article describes) | you, or a delegate |

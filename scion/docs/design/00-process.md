# Scion design package: the steps before code

The work behind this package was done in the wrong order: code was written first. This package
puts it right. It is written **from the article and from engineering analysis, not from the
code**, so the existing code can be checked against it instead of shaping it.

From here on, no code changes until this package is reviewed and approved. The gap list in
[11-traceability.md](11-traceability.md) then becomes the work queue.

## The pre-code steps, in order

| # | Step | Question it answers | Output | Exit criteria | Status |
|---|---|---|---|---|---|
| 1 | Vision and scope | Why build this, for whom, and what is out of scope? | [01-vision-and-scope.md](01-vision-and-scope.md) | problem, goals, measurable success criteria, non-goals, constraints and assumptions agreed | Draft for review |
| 2 | Stakeholders and actors | Who uses, operates, funds or is affected by it? | [02-stakeholders-and-actors.md](02-stakeholders-and-actors.md) | every actor has goals and a primary interface; no use case has an unnamed actor | Draft for review |
| 3 | Requirements (SRS) | What must the system do, and how well? | [03-requirements.md](03-requirements.md) | every requirement is atomic, testable, prioritized (MoSCoW) and traced to a source | Draft for review |
| 4 | Feature list | Which user-visible capabilities do we ship, and in which release? | [04-feature-list.md](04-feature-list.md) | every feature maps to requirements; every Must requirement maps to a feature | Draft for review |
| 5 | Use cases | How does each actor reach each goal, including failures? | [05-use-cases.md](05-use-cases.md) | use case diagrams plus a fully dressed use case for every actor goal, with extensions | Draft for review |
| 6 | UML models | What are the concepts, components, deployments, interactions and states? | [06-uml.md](06-uml.md) | domain, component, deployment, class, sequence, state, activity and ER diagrams, all rendering without errors | Draft for review |
| 7 | Architecture and decisions | How is it structured, and why this way? | [07-architecture.md](07-architecture.md) | architectural drivers, views, data model, protocols, capacity estimate, ADRs | Draft for review |
| 8 | Security and threat model | What can go wrong on purpose? | [08-security.md](08-security.md) | STRIDE per trust boundary, with mitigations mapped to requirements | Draft for review |
| 9 | Risks | What can go wrong by accident? | [09-risks.md](09-risks.md) | each risk has likelihood, impact, owner, mitigation and trigger | Draft for review |
| 10 | Verification and test plan | How will we know each requirement is met? | [10-test-plan.md](10-test-plan.md) | test levels, environments, acceptance criteria, and a test approach per requirement | Draft for review |
| 11 | Traceability and gap analysis | Is everything covered, and how does the existing code measure up? | [11-traceability.md](11-traceability.md) | requirement → use case → design → test matrix; gaps listed and prioritized | Draft for review |
| 12 | Project plan | In what order do we build it, and when are we done? | [12-project-plan.md](12-project-plan.md) | work breakdown, milestones, Definition of Ready/Done, change control | Draft for review |
| — | Glossary | What do the words mean? | [13-glossary.md](13-glossary.md) | every domain term used in the package is defined | Draft for review |
| 14 | Cross-check against the article | Does every word of the article land somewhere, and does every claim attributed to it match it exactly? | [14-article-crosscheck.md](14-article-crosscheck.md) | every sentence mapped; every term reviewed; every quote, number and section citation verified; discrepancies fixed | Done (this pass) |

## How to review

1. Read 01 → 04 first. If the vision, scope or requirements are wrong, everything downstream is wrong.
2. Each requirement has an ID (for example `FR-LD-02`). Use the ID to approve, reject or change it.
3. Use cases (05) and UML (06) should read as a consequence of 03. If something appears there
   that is not in 03, it is a defect in the package.
4. Look at 11 for the honest status of the current code against each requirement.
5. Approval gate: once 01–12 are signed off, the gap list in 11 is turned into work items (12)
   and code changes resume, one traced work item at a time.

## Conventions

* **Requirement IDs:** `FR-<area>-NN` (functional), `NFR-NN` (non-functional), `CON-NN` (constraint), `AS-NN` (assumption).
* **Other IDs:** `F-NN` (feature), `UC-NN` (use case), `ADR-NN` (decision), `R-NN` (risk), `T-<area>-NN` (test).
* **Priority (MoSCoW):** Must, Should, Could, Won't (this release).
* **Sources:** "Article §…" points to a section of
  [the article](https://www.anthropic.com/engineering/redesigning-source-control).
  "Derived" means engineering analysis needed to make an article statement work.
  The section labels are:

  | Label | Article section |
  |---|---|
  | §Opening | the untitled introduction, before "Growing our monorepo" |
  | §Growing our monorepo | "Growing our monorepo" |
  | §Principles | "Principles for agent-scale source control" |
  | §Data structures | "How Scion works" › "Data structures" |
  | §Scaling Scion | "How Scion works" › "Scaling Scion" |
  | §What we learned | "What we learned building Scion" |
  | §Contributing to the wider ecosystem | "Contributing to the wider ecosystem" |
  | footnote 1 | "Footnotes" |
* **Diagrams:** Mermaid, so they render on GitHub and are checked by a renderer before commit.

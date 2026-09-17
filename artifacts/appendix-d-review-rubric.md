# Appendix D — Expert review rubric (human gate 2)

Companion artefact to *Playable Assessment: Generative-AI-Authored Games and Micro-Simulators as
Automatically Graded, Integrity-Resilient Activities in Moodle*.

Completed by the subject-matter expert before deployment, after stage-4 automated validation has passed.
The completed rubric is archived in the activity bundle (Section 4.5) and is the record produced for
moderation and external examination.

**Decision rule.** Any single **Blocking** finding prevents deployment. Three or more **Major** findings
return the activity to stage 2 (specification) rather than stage 3 (regeneration), because a cluster of
major findings usually indicates the specification, not the generation, is at fault.

| # | Criterion | What the reviewer checks | Severity if failed |
|---|---|---|---|
| **Construct and domain validity** ||||
| D1 | Domain correctness | The model's behaviour is physically/logically correct across the parameter space, not only at the demonstrated point. Reviewer independently checks at least two instances by hand. | **Blocking** |
| D2 | Construct alignment | Score is driven by the specified outcomes, not by dexterity, reading speed, reaction time or visual acuity. | **Blocking** |
| D3 | Outcome coverage | Every specified outcome is reachable from at least one graded observable; no graded observable is unmapped. | Major |
| D4 | Misconception targeting | Each targeted misconception is genuinely provoked and genuinely addressed by feedback; distractors are principled, not arbitrary. | Major |
| **Parameterisation** ||||
| D5 | Semantic invariance | All instances assess the same construct at the same difficulty. Reviewer inspects the extremes of the parameter space, not the centre. | **Blocking** |
| D6 | Cardinality | Effective cardinality after constraint filtering meets the floor for the intended stakes (≥10⁴ formative, ≥10⁶ summative). | Major |
| D7 | Answer separation | Joint separation rate reported by stage 4 is ≥99%. Reviewer confirms the tolerance used matches the deployed question. | Major |
| D8 | Reachability | Every randomised variable moves at least one graded answer beyond tolerance. *(This is the check that rejected the first version of the Appendix C question.)* | Major |
| **Pedagogical design** ||||
| D9 | Scaffold ladder | At least three levels with sensible triggers; a novice who stalls is supported rather than left to flounder. | Major |
| D10 | Cognitive load | Within the load budget. No decorative animation, gratuitous narrative or split-attention layout. *The reviewer may reject on this ground alone.* | Major |
| D11 | Feedback quality | Task-focused, specific, actionable; not praise, not a bare "incorrect", not the answer handed over on the first try. | Major |
| D12 | Time budget | A competent student completes within the specified time; reviewer times one full pass. | Minor |
| **Integrity and security** ||||
| D13 | Grade channel | The client cannot assert a grade except through an authenticated channel. No summative component is `client_scored`. | **Blocking** |
| D14 | Seed integrity | Seed is keyed with a course secret, bound to user and attempt, and not predictable or replayable. | **Blocking** |
| D15 | Instance reconstructability | Staff can reconstruct any student's exact instance for regrading and appeals. | Major |
| D16 | No leaked answer key | The answer key is not present, derivable or logged in anything the client receives. | **Blocking** |
| **Accessibility and equity** ||||
| D17 | WCAG 2.2 AA | Automated scan clean; manual keyboard pass and screen-reader pass completed. | **Blocking** |
| D18 | Equivalent-task pathway | A non-interactive equivalent of identical construct and weight exists for approved accommodations. | **Blocking** |
| D19 | Device and bandwidth | Operable on a mid-range laptop and a small screen; no large asset downloads. | Major |
| D20 | Contextual neutrality | The scenario does not assume a particular national, professional, gendered or cultural context without reason. | Minor |
| **Data protection** ||||
| D21 | Observable minimisation | Only observables named in the specification are collected. | **Blocking** |
| D22 | Retention | A retention period is set for each observable and is no longer than the appeals window plus one academic cycle. | Major |
| D23 | Transparency notice | The activity tells students what is recorded, why, who sees it, how long it is kept, and how it affects their grade. | **Blocking** |
| **Sustainability** ||||
| D24 | Dependency freedom | No external runtime dependencies; the artefact opens and runs from the archive. | Major |
| D25 | Provenance complete | Model identifier, generation parameters, specification hash, validation report and this rubric are all archived together. | Major |

---

## Reviewer declaration

> I have reviewed this activity against the criteria above. I have independently verified the domain
> correctness of at least two instances. I understand that approving this activity makes me academically
> accountable for its content in the same way as for any other assessment material I set, and that this
> accountability is not transferred to the model that generated it.

**Reviewer:** ______________________  **Date:** ____________  **Outcome:** approved / approved with changes / rejected

**Findings:** ____________________________________________________________________

**Recorded in bundle as:** `review/<activity_id>-<date>.md`

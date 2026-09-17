# Appendix B — Authoring prompt template (pipeline stages 2 and 3)

Companion artefact to *Playable Assessment: Generative-AI-Authored Games and Micro-Simulators as
Automatically Graded, Integrity-Resilient Activities in Moodle*.

Generation in GAIMS is **specification-driven, not conversational** (Section 4.2, L1). The two prompts
below are templates, versioned alongside the activity specification, so that a regeneration can be
reproduced, diffed and audited. A chat transcript cannot serve this purpose.

---

## B.1 Stage 2 — Blueprint to specification

> You are assisting an academic to specify an interactive micro-simulation for automatic grading in Moodle.
> Produce **only** a JSON document conforming to the GAIMS Activity Specification v1.0 schema supplied below.
> Do not produce prose, code, or an artefact at this stage.
>
> **Blueprint**
> - Learning outcomes (max 3): `<outcomes>`
> - Prior knowledge the learner is assumed to have: `<prerequisites>`
> - Misconceptions to target: `<misconceptions>`
> - Time budget: `<minutes>` minutes
> - Domain and level: `<domain>`, `<level>`
> - Constraints the department imposes: `<constraints>`
>
> **Requirements**
> 1. Every outcome must be reachable from at least one observable or grading component.
> 2. Every misconception must be addressed by at least one feedback string, distractor or induced fault.
> 3. Parameterisation must state validity constraints that preserve semantic invariance — every instance must
>    assess the same construct at the same difficulty. State the rationale for each constraint.
> 4. Propose a `cardinality_target` and justify it against the ≥10⁴ formative / ≥10⁶ summative floors.
> 5. Every grading component must name a **native Moodle object** that performs the grading. If you cannot
>    name one, the component is out of scope: say so explicitly rather than inventing a grading service.
> 6. Specify a scaffold ladder of at least three levels with explicit triggers. An unguided sandbox is not
>    an acceptable design.
> 7. Respect the load budget: no more controls or displayed quantities than the budget allows.
> 8. `external_dependencies` must be empty.
>
> **Schema**
> `<paste appendix-a-activity-spec.schema.json>`
>
> Where the blueprint is under-determined, make the minimal defensible choice and record it in a
> `"_assumptions"` comment field rather than asking a follow-up question.

**Human gate 1** follows: the academic reviews the specification for construct validity — are these
the right outcomes, are the misconceptions the real ones, is the parameterisation semantically invariant?
Nothing is generated until the specification is approved.

---

## B.2 Stage 3 — Specification to artefact

Issued as **three independent generations** that must not see each other's output. Independence is the
whole point: it is what makes the stage-4 cross-check informative rather than self-confirming.

### B.2.1 Artefact generation

> Generate a single self-contained HTML5 file implementing the activity specified in the attached JSON.
>
> Hard requirements:
> - One file. No external scripts, stylesheets, fonts, network calls or CDN references of any kind.
> - The instance parameters are read from a seed supplied by the host page; never generate them from
>   `Math.random()` and never embed a fixed instance.
> - Never compute, assert or transmit a grade. Emit only the observables named in the specification.
> - Implement every level of the scaffold ladder with the stated trigger.
> - Implement every immediate-feedback string with its stated trigger.
> - WCAG 2.2 AA: full keyboard operability, visible focus, no information by colour alone, labelled
>   controls, `prefers-reduced-motion` respected, all state also available as text.
> - Stay inside the load budget. Do not add decorative animation, narrative, sound or scoring flourishes
>   that the specification does not ask for.
>
> Output the file and nothing else.

### B.2.2 Reference solver generation (independent)

> Given **only** the physical/logical description below and the parameter space, write a reference solver
> in Python that computes the graded quantities from the instance parameters.
>
> Use a derivation route that is *structurally different* from a stepwise interactive implementation —
> prefer a closed-form or first-principles derivation, and state the derivation in comments.
> Include explicit unit arithmetic for every derived quantity.
> Do not consult, import or reproduce any simulator code.
>
> Also emit: physical bounds that every valid instance must satisfy, at least two limiting cases with
> their expected analytic values, and a conservation or balance identity that must close to numerical
> precision.

### B.2.3 Moodle import artefacts

> Produce the Moodle question XML that grades the derived quantities named in the specification's
> `grading.components`, using the `Formulas` question type.
> - `varsrandom` must reproduce the specification's parameter space exactly, including step sizes.
> - `varsglobal` must define the answer key in terms of the random variables so that the correct answer
>   recomputes per instance.
> - One part per graded component, each with `answermark`, per-part feedback naming the misconception it
>   addresses, and a relative-error `correctness` rule at the specification's `separation_tolerance`.
> - Unit-graded parts must declare `postunit`.
> - Supply question-level hints, ordered from orienting to specific, for `interactive with multiple tries`.

---

## B.3 Stage 4 — Automated validation (no LLM)

Stage 4 is deterministic code, not a model call. Asking a model to check its own output is not verification.
The validator cross-checks the artefact against the independently generated reference solver over a Monte
Carlo sample of the constrained parameter space, and runs the checks enumerated in `validate_rankine.py`:
physical bounds, balance closure, dimensional consistency, limiting cases, effective cardinality, per-part
and joint answer separation, and parameter reachability. A failure returns the pipeline to stage 2 or 3
with the failing check named; it does not return a request to "try again".

---

## B.4 Regeneration prompt (stage 4 failure)

> The following stage-4 check failed for the attached activity:
>
> `<verbatim validator output>`
>
> Diagnose the cause in one paragraph, then emit only the corrected artefact(s). Do not change anything
> the failing check did not implicate. If the fix requires a change to the **specification** rather than
> to the generated artefact, say so and stop — a specification change requires human gate 1 again.

> **Worked instance of this loop.** Check 7 (parameter reachability) rejected the first version of the
> Appendix C question: the randomised pump isentropic efficiency `eta_p` moved no graded answer by more
> than the 1% grading tolerance, because pump work is roughly 1% of net work in this cycle. The variable
> varied the question's *appearance* without varying its *assessment*. The corrected version adds a fifth
> graded part — actual pump specific work — which `eta_p` moves by about 20% across the class, and which
> also happens to target misconception M4 (treating pump work as automatically negligible). Joint answer
> separation rose from 99.63% to 99.94%. This is the ordinary operation of the gate, and it is the kind of
> defect that a human reviewer reading a plausible-looking question is unlikely to catch.

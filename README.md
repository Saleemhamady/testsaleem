# Playable Assessment — research paper and companion artefacts

**Generative-AI-Authored Games and Micro-Simulators as Automatically Graded, Integrity-Resilient Activities in Moodle**

A conceptual and design-science paper arguing that generative AI, which degraded the validity of
product-based online assessment, is also the technology that makes process-based interactive assessment
affordable — and specifying how to close that loop using Moodle's existing native grading machinery.

## Contents

| Path | What it is |
|---|---|
| `paper/main.md` | The paper (~13,700 words, 66 references). |
| `paper/references.bib` | BibTeX for all cited works. |
| `artifacts/appendix-a-activity-spec.schema.json` | Appendix A — JSON Schema for the GAIMS activity specification. |
| `artifacts/example-rankine-activity.json` | A conforming specification instance for the Rankine-cycle vignette. |
| `artifacts/appendix-b-authoring-prompt.md` | Appendix B — stage-2/3 authoring prompt templates and the independent-generation protocol. |
| `artifacts/appendix-c-rankine-formulas.xml` | Appendix C — importable Moodle `Formulas` question (5 parts, per-instance randomisation). |
| `artifacts/validate_rankine.py` | Stage-4 reference solver and validator. |
| `artifacts/appendix-d-review-rubric.md` | Appendix D — 25-criterion expert review rubric for human gate 2. |

## The argument in brief

1. Generative AI did not create the assessment validity gap; it made it impossible to ignore. The
   observable (a finished document or number) had always been weak evidence for the claim (the student
   possesses the competence).
2. The fix — authentic, interactive, process-rich assessment — was always blocked by production cost.
   That is the constraint generative AI removes.
3. Moodle already contains the grading machinery: `Formulas`/STACK randomised questions, the question
   engine's multi-try behaviours, H5P with xAPI, LTI 1.3 AGS, gradebook calculations, restrict-access
   chains and the Workshop module. No bespoke server-side grading is required.
4. The integrity claim is bounded and stated as propositions P1–P6 and conclusion C1: per-student
   parameterisation defeats sharing but not solving; interaction cost and process evidence raise the cost
   of outsourcing; immediate feedback lowers the cost of honesty. A determined adversary with a
   computer-use agent is **not** mitigated by design alone, which is why the framework requires
   programme-level secured anchor points.

## Reproducing the reported results

```bash
python3 artifacts/validate_rankine.py     # exits 0; prints the statistics quoted in §6.1
python3 -c "import xml.dom.minidom as d; d.parse('artifacts/appendix-c-rankine-formulas.xml')"
pip install jsonschema && python3 -c "
import json, jsonschema
jsonschema.validate(json.load(open('artifacts/example-rankine-activity.json')),
                    json.load(open('artifacts/appendix-a-activity-spec.schema.json')))
print('spec validates')"
```

The validator is deterministic under its fixed seed. It reports effective cardinality of 134,850,
energy-balance closure to 1.8e-16, the ideal-component limiting case at eta_th = 0.3915, and joint
answer separation of 99.94%.

## A note on the Appendix C question

The four-part version of that question **failed** stage-4 validation: the randomised pump isentropic
efficiency moved no graded answer beyond the 1% grading tolerance, so it varied the question's appearance
without varying its assessment. The deployed version adds a fifth part (actual pump specific work) that
is sensitive to it. The episode is reported in §6.1 rather than quietly fixed, because it is the evidence
for the paper's methodological claim: verification of generated assessment content has to be mechanical
and adversarial.

## Status

Preprint draft v1.0, 2026-09-17. No empirical results are reported; §8 specifies the pre-registerable
study that would generate them. Author, affiliation and acknowledgement fields in `paper/main.md` are
placeholders.

**Before submission:** verify every reference against the publisher record. Entries were compiled without
live database access and DOIs were deliberately omitted rather than risk transcription error; volume,
issue, page and article-number fields should be confirmed.

---
title: "Playable Assessment: Generative-AI-Authored Games and Micro-Simulators as Automatically Graded, Integrity-Resilient Activities in Moodle"
short_title: "Playable Assessment in Moodle"
keywords: [generative artificial intelligence, Moodle, serious games, simulation-based learning, automated assessment, academic integrity, stealth assessment, learning analytics, engineering education]
date: 2026-09-17
status: preprint draft v1.0
---

# Playable Assessment: Generative-AI-Authored Games and Micro-Simulators as Automatically Graded, Integrity-Resilient Activities in Moodle

**Author(s):** *[Author name], [Department], [Institution], [email]*
*[Co-authors]*

---

## Abstract

Generative artificial intelligence (GenAI) has simultaneously produced two effects on higher education that are usually discussed in isolation. First, it has degraded the inferential validity of the text-based, product-oriented assessments that dominate learning management systems (LMS): essays, short-answer questions, problem sets and take-home reports can now be produced at expert-plausible quality in seconds, with no reliable post hoc detection. Second, and less discussed, it has collapsed the marginal cost of authoring interactive learning objects — games, micro-simulators, scenario engines and parameterised problem worlds — from days of specialist developer time to minutes of prompt-and-review time by a subject teacher.

This paper argues that the second effect is the appropriate response to the first, and specifies how the pairing can be operationalised inside Moodle, the most widely deployed open-source LMS in higher education. We present **GAIMS** (Generative-AI-authored Interactive Micro-Simulations), a design framework in which an instructor specifies a learning objective and a constraint set; an LLM-based authoring pipeline generates a playable, parameterised artefact; and Moodle's existing native machinery — the question engine with `interactive-with-multiple-tries` and adaptive behaviours, calculated/`Formulas`/STACK question types, the gradebook with calculated categories, activity completion with conditions, restrict-access chains, the Workshop module, and the standard logging/analytics store — performs grading, feedback, progression and monitoring without bespoke server-side code.

The framework's lightest-weight and most immediately deployable integration is what we call the **Cloze answer-field bridge**: the generated game runs inside the text of a standard Moodle *Embedded answers (Cloze)* question and writes its score, and a compact record of the learner's trajectory, into hidden Cloze answer fields, which the question engine then grades as ordinary responses. This requires no plugin, no H5P, no external tool and no server-side code, and can therefore be deployed by an individual teacher without institutional permission — a property we argue matters more for adoption than any technical elegance. We give a complete, browser-tested worked example.

The framework's integrity claim is deliberately narrow and defensible. We do not claim that GenAI-authored games are un-cheatable; multimodal agents can operate interfaces. We claim instead that they shift the economics and the evidentiary basis of assessment in three specific ways: (i) **per-student parameterisation** makes answer-sharing and solution-bank harvesting structurally ineffective rather than merely prohibited; (ii) **process evidence** (sequence, latency, exploration path, revision pattern, resource use) is captured natively and cannot be supplied by a text-generating model asked for a final answer; and (iii) **outsourcing cost inversion** means that delegating a 25-minute interactive diagnostic task to an agent is more effortful, more detectable and less rewarding than simply doing it. We develop a threat model with an explicit attack/mitigation matrix, including the case of a student driving a computer-use agent, and we state residual risks plainly.

We contribute: (1) a theoretical synthesis linking evidence-centred design, stealth assessment, cognitive load theory and assessment-security theory to LMS-native implementation; (2) the GAIMS reference architecture and its six layers; (3) four concrete Moodle grading-integration patterns with worked engineering examples, including an importable Moodle `Formulas` XML artefact and a machine-readable activity specification schema; (4) a quality-assurance protocol addressing LLM hallucination, physical-model validity, accessibility and psychometric soundness; and (5) a pre-registerable, mixed-methods evaluation design with power analysis, outcome measures and validity threats, intended to make the framework empirically falsifiable rather than merely advocated.

The paper is a conceptual and design-science contribution. No empirical results are reported; Section 8 specifies the study that would generate them.

**Keywords:** generative AI; Moodle; serious games; simulation-based learning; automated assessment; academic integrity; stealth assessment; learning analytics; engineering education

---

## 1. Introduction

### 1.1 Two consequences of one technology

The public release of instruction-tuned large language models (LLMs) in late 2022 created an assessment crisis in higher education that was immediate, well-documented and — importantly — asymmetric. Within months, studies demonstrated that a general-purpose LLM could pass or approach passing thresholds on professional licensing examinations (Kung et al., 2023), produce work that graders could not reliably distinguish from student work (Susnjak, 2024), and outperform median students on substantial portions of engineering assessment (Nikolic et al., 2023). The institutional response bifurcated into two strategies, both of which have known weaknesses: *detection*, which has been shown to be unreliable and systematically biased against non-native English writers (Liang et al., 2023; Weber-Wulff et al., 2023), and *surveillance*, which imposes equity, privacy and wellbeing costs that are increasingly difficult to justify (Dawson, 2021; Slade & Prinsloo, 2013).

A third strategy — assessment redesign — is widely endorsed in policy (Lodge et al., 2023; TEQSA, 2023) and in the scholarly literature (Bearman et al., 2024; Swiecki et al., 2022). It is, however, chronically under-operationalised. Telling a lecturer with 180 students and a 14-week semester to "redesign assessment for authenticity and process" without giving them tooling is advice, not a solution. The practical constraint has always been production cost: authentic, interactive, process-rich assessment historically required instructional designers, developers and budgets that most departments do not have. Vlachopoulos and Makri's (2017) systematic review of games and simulations in higher education is explicit that development effort is a primary adoption barrier, notwithstanding consistently positive learning effects.

This is precisely the constraint that GenAI removes. The same model class that can write a student's essay can also write a parameterised heat-exchanger simulator, a fault-injection circuit game, a titration bench, an epidemiological policy sandbox or a branching clinical triage scenario — as self-contained HTML5 with instrumented state, in a single generation pass, from a teacher's specification. Evidence from computing education already shows LLMs producing usable programming exercises, test cases and explanations at scale (Sarsa et al., 2022; Leinonen et al., 2023), extending a longer tradition of automatic item generation (Gierl & Lai, 2013; von Davier, 2018; Kurdi et al., 2020).

The argument of this paper is therefore simple to state and non-trivial to implement: **the technology that broke product-based assessment is the technology that makes process-based assessment affordable, and the LMS already contains the grading machinery to close the loop.**

### 1.2 Why Moodle specifically

The choice of Moodle is not incidental. Three properties make it the appropriate substrate for this framework rather than an arbitrary implementation target.

First, **installed base and institutional control**. Moodle (Dougiamas & Taylor, 2003) is deployed at tens of thousands of institutions worldwide and is the subject of a large applied literature (Gamage et al., 2022). Because it is open source and typically self- or institution-hosted, process data generated by the activities described here remains under institutional data governance rather than being exported to a vendor — a material consideration given the privacy analysis in Section 10.

Second, **a mature, underused automatic grading engine**. Moodle's question engine already supports per-attempt randomisation through calculated and dataset-backed question types; algebraic and semantic grading through `Formulas` and STACK (Sangwin, 2013; Sangwin & Köcher, 2016); multi-try scoring with penalty regimes through the `interactive` and `adaptive` question behaviours; multi-part questions with partial credit; and rubric/marking-guide grading for artefacts. Most institutions use a fraction of this. The framework proposed here does not require new grading infrastructure; it requires connecting a generated artefact to the grading infrastructure that already exists.

Third, **native instrumentation and orchestration hooks**. H5P is bundled in core Moodle and reports xAPI statements into Moodle's grade and log stores (ADL Initiative, 2017; Joubel, 2024). External tools integrate via LTI 1.3 with Assignment and Grade Services (1EdTech, 2019). Activity completion, restrict-access rules and the gradebook's calculated categories provide a declarative progression engine. Moodle's standard logging schema supports learning-analytics queries without additional middleware (Gašević et al., 2015).

In short, Moodle supplies the *assessment substrate*; GenAI supplies the *content generation* that the substrate has always been starved of.

### 1.3 Research questions

This paper addresses four questions. RQ1–RQ2 are answered conceptually and by design here; RQ3–RQ4 are operationalised into a testable protocol in Section 8.

- **RQ1 (Architecture).** What reference architecture allows GenAI-authored interactive artefacts to be automatically graded by Moodle's native features, without bespoke server-side development per activity?
- **RQ2 (Integrity).** Under an explicit adversary model that includes AI-assisted students and computer-use agents, which properties of such activities meaningfully raise the cost of illegitimate outsourcing, and which do not?
- **RQ3 (Learning).** Do GAIMS activities produce learning gains, engagement and self-regulation outcomes that differ from matched conventional Moodle quiz and problem-set assessment?
- **RQ4 (Feasibility).** What are the authoring time, defect rate, human-review burden and maintenance costs of the pipeline in routine departmental use?

### 1.4 Contributions and structure

Section 2 reviews the four literatures the paper joins. Section 3 develops the theoretical framing, including the *outsourcing cost inversion* argument that carries the integrity claim. Section 4 specifies the GAIMS framework, its layers and its authoring pipeline. Section 5 gives the Moodle grading-integration patterns. Section 6 presents three worked examples with concrete artefacts. Section 7 gives the threat model and attack/mitigation matrix. Section 8 specifies the evaluation study. Sections 9–11 cover discussion, limitations and ethics, and Section 12 concludes. Appendices provide the activity specification schema, the authoring prompt template, an importable Moodle `Formulas` question, and a review rubric.

---

## 2. Background and Related Work

### 2.1 Games and simulations as learning environments

The claim that well-designed games and simulations support learning is one of the better-evidenced propositions in educational technology, though with important qualifications about *which* designs and *under what conditions*. The advocacy literature that opened the field (Prensky, 2001; Gee, 2003) argued from the learning principles embedded in commercial game design; the empirical literature that followed has been more discriminating, and it is the latter that constrains the present framework.

Meta-analytic evidence is broadly positive but heterogeneous. Sitzmann (2011) found computer-based simulation games associated with higher declarative knowledge, procedural knowledge and retention relative to comparison instruction, with effects strongly moderated by whether learners were *active* rather than passive and whether the game supplemented rather than replaced instruction. Wouters et al. (2013) similarly found serious games more effective than conventional instruction for learning and retention, but — notably — found no significant advantage for motivation, cautioning against the assumption that games motivate by default. Clark et al. (2016), in a systematic review and meta-analysis of digital games, found positive effects on cognitive and intrapersonal outcomes and emphasised that *design variation within games* accounted for more outcome variance than the game/non-game contrast. Sailer and Homner's (2020) meta-analysis of gamification found small-to-moderate positive effects on cognitive, motivational and behavioural outcomes, again design-dependent.

For simulations specifically, de Jong and van Joolingen's (1998) foundational review established that discovery learning with simulations is effective only when scaffolded — unguided exploration reliably underperforms. Rutten et al. (2012) reached compatible conclusions for science education, and D'Angelo et al. (2014) reported positive aggregate effects for STEM simulations. The PhET program demonstrated at scale that carefully designed, interactively constrained simulations produce conceptual gains when embedded in structured tasks (Wieman et al., 2008).

Two design lessons follow and are built into GAIMS as constraints rather than options: **games and simulations must be scaffolded, not merely provided**, and **motivational benefit must not be assumed**. This is consistent with the broader finding that minimal-guidance instruction underperforms for novices (Kirschner et al., 2006), and with cognitive load theory's warning that extraneous interface complexity consumes working memory that should be spent on the target schema (Sweller, 1988; Mayer, 2009).

### 2.2 Automated assessment in Moodle

Moodle's assessment capability is best understood as a set of composable primitives rather than a single feature.

The **question engine** separates a question's *definition* from its *behaviour*. The `interactive with multiple tries` behaviour gives per-try feedback with configurable penalty; `adaptive` mode scores continuously; `deferred feedback` supports summative use. This separation is what allows a single generated item bank to serve both formative play and summative assessment.

**Randomisation primitives** include the `calculated` and `calculated multichoice` types backed by shared datasets, `random` questions drawn from a category, and — most powerfully — the `Formulas` question type and STACK. `Formulas` (Lau & Védrine, 2023) supports random and global variable declarations, multi-part questions with independent grading, unit-aware numerical answers and algebraic grading criteria; STACK (Sangwin, 2013) adds full computer-algebra-backed grading with answer tests and potential response trees, and has been shown capable of automating substantial portions of university mathematics examinations (Sangwin & Köcher, 2016). Both make *every student receiving a structurally identical but numerically distinct task* a configuration choice rather than a development project.

The **Embedded answers (Cloze)** question type deserves separate mention because it is the least glamorous and, for the present purpose, the most useful. A Cloze question's text is arbitrary HTML containing inline answer-field declarations such as `{1:NUMERICAL:...}` or `{1:SHORTANSWER:...}`, each of which Moodle renders as a form input and grades independently. The question text is therefore a general-purpose container into which arbitrary markup and script can be placed alongside gradable fields — which, as Section 5.5 develops, makes it a complete delivery and grading channel for a generated interactive artefact with no additional infrastructure whatsoever.

**H5P**, bundled in Moodle core since 3.8, provides interactive content types that emit xAPI statements consumed by Moodle's grade and log stores (Joubel, 2024; Singleton & Charlton, 2020). Critically for this paper, Moodle's H5P integration will grade an arbitrary custom H5P content type that reports a score, which makes H5P a general-purpose delivery envelope for generated interactive artefacts.

**Orchestration primitives** — activity completion with condition sets, restrict-access chains, the gradebook's calculated grade items and categories, and the Workshop module's rubric-based peer assessment — allow multi-stage assessment designs (play → justify → peer-review → reflect) to be expressed declaratively.

Applied Moodle research has concentrated on adoption, engagement and blended-learning outcomes (Gamage et al., 2022) rather than on the assessment-design affordances catalogued above. The gap this paper addresses is not that Moodle lacks capability; it is that the capability is not connected to interactive content because interactive content has been too expensive to make.

### 2.3 Academic integrity under generative AI

Integrity problems in online assessment predate GenAI. Contract cheating prevalence estimates have been contested but non-trivial (Newton, 2018; Bretag et al., 2019), and file-sharing/homework-help platforms were documented as vectors for STEM assessment leakage well before 2022 (Lancaster & Cotarlan, 2021). At scale, answer-copying and multiple-account harvesting were measurable in MOOCs (Northcutt et al., 2016; Alexandron et al., 2017), and copying in online homework was shown to predict examination underperformance (Palazzo et al., 2010) — a reminder that the harm of integrity failure is primarily *to learning*, not merely to certification fairness.

GenAI changed the parameters rather than the nature of the problem: it removed cost, removed delay, and removed the third party whose existence made contract cheating detectable. Empirical work documents strong LLM performance across assessment genres (Kung et al., 2023; Nikolic et al., 2023) and questions the viability of unsupervised online examination (Susnjak, 2024; Rudolph et al., 2023; Perkins, 2023). Evidence on whether *overall* cheating rates rose is more nuanced — Lee et al. (2024) found rates broadly stable in a secondary-school sample, suggesting substitution of method rather than expansion of population — but the validity threat is independent of prevalence: an assessment whose output can be produced without the targeted cognition is invalid regardless of how many students exploit that.

Dawson (2021) provides the conceptual correction that this paper adopts: **assessment security** (the extent to which we can be confident an assessment result reflects the student's own competence) is distinct from **detection**, and is better achieved by design than by policing. Bearman et al. (2024) extend this toward developing students' evaluative judgement as a first-class outcome. Swiecki et al. (2022) map the space of AI-era assessment including process-data approaches.

### 2.4 AI-assisted generation of assessment and learning content

Automatic item generation has a substantial psychometric pedigree: template- and model-based generation (Gierl & Lai, 2013), neural generation with calibrated difficulty (von Davier, 2018), and a systematic review of automatic question generation for education by Kurdi et al. (2020) that catalogues both the promise and the persistent quality-control problem. LLM-era work in computing education has shown that models can generate programming exercises with tests and explanations of usable quality, while consistently reporting a non-trivial defect rate that requires human review (Sarsa et al., 2022; Finnie-Ansley et al., 2022; Leinonen et al., 2023). The general hallucination literature (Ji et al., 2023) supplies the mechanism: fluent, confident, locally plausible and factually wrong output is the expected failure mode, not an anomaly.

Consequently, **no serious framework may treat LLM output as deployable without verification**, and GAIMS builds verification in as a pipeline stage with explicit gates (Section 4.6), rather than as an exhortation.

### 2.5 The gap

Each literature is mature in isolation. What is absent is an integrated, implementable specification that (a) uses GenAI as an *authoring* technology rather than a tutoring or grading oracle, (b) targets an LMS's *existing* automatic grading primitives rather than proposing new infrastructure, (c) treats integrity as an economic and evidentiary design problem with an explicit adversary model rather than a detection problem, and (d) is stated precisely enough to be evaluated and refuted. GAIMS is offered as that specification.

---

## 3. Theoretical Framing

GAIMS rests on four established theoretical pillars and one argument specific to the GenAI condition.

### 3.1 Evidence-centred design: assessment as an argument

Evidence-centred design (ECD) models assessment as a chain of inference from *observables* to *claims* about a student, mediated by task models and evidence models (Mislevy et al., 2003). ECD is the correct frame here because it makes the GenAI threat precise: the crisis is not that students use AI, it is that the **observable** (a finished text or numeric answer) has become weakly diagnostic of the **claim** (the student possesses the competence). The evidentiary link, not the student, is what broke.

ECD also supplies the remedy. If the observable set is widened to include *how* a solution was reached — which parameter the student varied first, whether they recognised an infeasible operating point, how they recovered from an induced fault, how their estimates converged — then the inference chain is restored, because that evidence is generated by interaction with a task instance that did not exist before the student opened it. Mislevy et al. (2014) extended ECD explicitly to game-based assessment, establishing the psychometric vocabulary GAIMS adopts.

### 3.2 Stealth assessment: measurement without interruption

Shute's stealth assessment programme (Shute, 2011; Shute & Ventura, 2013) demonstrated that competency estimates can be maintained continuously from in-game behaviour, via Bayesian networks linking observable actions to competency nodes, without stopping play to administer a test. Shute et al. (2016) validated the approach for problem-solving skill in a commercial physics puzzle game, finding in-game estimates correlated with external problem-solving measures.

GAIMS deliberately adopts a **reduced-fidelity** version of stealth assessment. Full Bayes-net competency modelling is beyond what a departmental teaching team can author and maintain. Instead, GAIMS specifies a small set of **indicator observables** per activity (typically 3–7), each mapped to a scored Moodle grade item or completion condition. This is a pragmatic trade: less psychometric elegance, far greater sustainability, and — crucially — grading that Moodle can already perform natively.

### 3.3 Cognitive load and the guidance requirement

Cognitive load theory (Sweller, 1988) and the multimedia learning principles derived from it (Mayer, 2009) impose hard design constraints on interactive artefacts. Interface complexity, decorative animation, unnecessary narrative and split-attention layouts consume working memory without contributing to schema construction. The unguided-discovery critique (Kirschner et al., 2006) and the simulation-scaffolding literature (de Jong & van Joolingen, 1998; Rutten et al., 2012) converge on the same requirement: **the artefact must constrain the problem space and provide staged support**, especially for novices.

This is a real risk for GenAI authoring specifically. Models generate visually elaborate output readily; elaboration is cheap and therefore over-supplied. GAIMS counters with explicit *load budget* constraints in the activity specification (Appendix A) and a review gate that rejects artefacts on extraneous-load grounds (Section 4.6).

### 3.4 Motivation: self-determination, not points

Self-determination theory (Ryan & Deci, 2000) predicts that autonomy, competence and relatedness support intrinsic motivation, whereas controlling contingencies can undermine it. This matters because the gamification literature — understood in Deterding et al.'s (2011) sense of game *elements* imported into non-game contexts, which is a weaker intervention than a designed game — reports positive but modest effects (Hamari et al., 2014; Sailer & Homner, 2020) and the absence of a motivational advantage in Wouters et al. (2013) indicate that points, badges and leaderboards are not reliably motivating. GAIMS therefore specifies motivational design in SDT terms — meaningful choice within the simulator, calibrated difficulty with immediate competence feedback, optional collaborative variants — and treats Moodle badges as an optional, non-load-bearing element.

### 3.5 Feedback as the mechanism of learning gain

The learning value of an automatically graded interactive activity comes primarily from feedback, not from grading. Hattie and Timperley (2007) and Shute (2008) establish that effective formative feedback is timely, specific, task-focused rather than self-focused, and actionable. Sadler (1989) adds the requirement that the learner be able to perceive the gap between current and desired performance. Retrieval-practice and desirable-difficulty research (Roediger & Karpicke, 2006; Bjork & Bjork, 2011) establishes that effortful, repeated attempts with feedback outperform passive review, and Black and Wiliam (1998) established the aggregate case for formative assessment.

Moodle's `interactive with multiple tries` behaviour, combined with per-response specific feedback and per-try hints, is a direct implementation of this evidence base — which is why GAIMS routes generated activities through the question engine wherever possible rather than inventing a parallel feedback mechanism. Freeman et al.'s (2014) meta-analysis of active learning in STEM provides the outcome expectation against which Section 8's effect-size assumptions are set.

### 3.6 The outsourcing cost inversion argument

The four pillars above are established. The following argument is specific to the present condition and is the paper's central integrity claim. It is stated as a set of propositions so that it can be attacked precisely.

Let an assessment task *T* produce a submission *S*. Define the **outsourcing ratio** ρ(T) = C_legit(T) / C_outsource(T), where C_legit is the student's cost of completing *T* by the intended cognition, and C_outsource is the total cost of obtaining an acceptable *S* by illegitimate means — including acquisition, adaptation, coordination and perceived risk.

- **P1.** For conventional text and numeric-answer assessment post-2022, C_outsource collapsed toward the cost of typing a prompt, so ρ ≫ 1. Rational effort-minimising behaviour follows, independently of student values, and this is why the genre is compromised (Susnjak, 2024; Nikolic et al., 2023).

- **P2.** ρ can be reduced by raising C_outsource or lowering C_legit. Detection raises *perceived risk* only, and unreliable detection raises it weakly while imposing false-accusation costs (Weber-Wulff et al., 2023; Liang et al., 2023). Proctoring raises C_outsource substantially but at institutional, equity and privacy cost (Dawson, 2021). Design is the remaining lever.

- **P3 (Instance uniqueness).** If every student receives a numerically and structurally distinct instance of *T*, the *shared-artefact* term of C_outsource — obtaining someone else's finished solution, or a solution bank entry — goes to zero utility. This defeats the historically dominant cheating vector (Lancaster & Cotarlan, 2021; Northcutt et al., 2016; Alexandron et al., 2017) but *not* a per-instance LLM solver. Parameterisation is necessary and insufficient.

- **P4 (Interaction cost).** If *S* is not a document but a *trajectory through a stateful artefact* — n interface actions over t minutes, where intermediate states depend on the student's own prior actions — then outsourcing requires either (a) a human proxy operating the interface, which restores the cost and detectability of classical contract cheating, or (b) a computer-use agent driving the interface, which is technically feasible but requires setup, supervision and per-instance operation time that scales with t rather than being amortised. C_outsource therefore scales with task interactivity, whereas for text tasks it is approximately constant.

- **P5 (Evidentiary residue).** The trajectory itself is recorded. A legitimate trajectory has characteristic properties — exploratory variance, error-and-recovery, non-uniform inter-action latency, partial dead ends — that differ from both a proxy-operated and an agent-operated trajectory. This does not yield reliable individual-level detection, and we explicitly do not propose it as such (see §7.4); it yields *cohort-level anomaly signal* usable for programme monitoring and for triggering non-punitive follow-up such as a short oral check.

- **P6 (Legitimate-cost reduction).** Because the artefact provides immediate, specific feedback and unlimited low-stakes retries (Hattie & Timperley, 2007; Shute, 2008; Roediger & Karpicke, 2006), C_legit falls: doing the task honestly becomes faster, more pleasant and more obviously useful than arranging its evasion. This is the half of the ratio that punitive approaches cannot touch, and we regard it as the more durable half.

- **C1 (Conclusion).** GAIMS activities reduce ρ by simultaneously raising C_outsource (P3, P4) and lowering C_legit (P6), while generating evidence that supports validity claims (P5). They do **not** make ρ < 1 for a determined, technically capable adversary with agent tooling, and any claim that they do should be rejected.

This bounded claim is what distinguishes the present proposal from the "AI-proof assessment" genre. The realistic goal is a defence-in-depth posture in which the cheapest path through the course is learning, and the residual adversary is handled by a small number of secured anchor points (Section 7.5).

---

## 4. The GAIMS Framework

### 4.1 Definition and scope

A **GAIMS activity** is a learning activity satisfying all six of the following criteria:

1. **Generated.** Its interactive artefact is authored primarily by an LLM from a machine-readable specification, under human review.
2. **Interactive and stateful.** The learner manipulates a model or narrative whose state evolves in response to their actions; it is not a rendered animation or a styled quiz.
3. **Parameterised.** Every learner receives an instance drawn from a defined parameter space, seeded deterministically from their user identity and attempt number.
4. **Instrumented.** A defined set of observables is emitted during interaction.
5. **LMS-gradable.** Every graded observable maps to a native Moodle grade item, question response or completion condition — no bespoke server-side grading service.
6. **Feedback-closing.** The learner receives specific, actionable feedback within the activity or immediately after it, before the next attempt.

Criteria 5 and 6 are what separate GAIMS from the large body of standalone educational-game work: sustainability requires that grading and feedback live in infrastructure the institution already runs and already supports.

We use **"micro-simulation"** deliberately. The target unit is 10–30 minutes of learner time addressing 1–3 learning outcomes — not a semester-long virtual laboratory. This scale is what makes generation, verification, replacement and psychometric review tractable, and it matches the granularity at which Moodle's gradebook and completion machinery operate naturally.

### 4.2 Reference architecture

GAIMS is organised as six layers. The separation matters practically: it allows the generated artefact to be replaced or regenerated without disturbing grading, and allows grading configuration to change without regenerating the artefact.

```
┌──────────────────────────────────────────────────────────────────────┐
│ L6  ANALYTICS & GOVERNANCE                                           │
│     Moodle logs + xAPI store → item stats, integrity anomaly signal, │
│     outcome mapping, retention & privacy controls                    │
├──────────────────────────────────────────────────────────────────────┤
│ L5  FEEDBACK                                                         │
│     In-artefact immediate feedback; question-level specific feedback │
│     and hints; gradebook feedback; Workshop rubric feedback          │
├──────────────────────────────────────────────────────────────────────┤
│ L4  GRADING (native Moodle)                                          │
│     Question engine (Formulas / STACK / calculated / multipart)      │
│     H5P → xAPI → grade item; LTI 1.3 AGS; gradebook calculations;    │
│     completion conditions; Workshop peer + rubric                    │
├──────────────────────────────────────────────────────────────────────┤
│ L3  INSTRUMENTATION                                                  │
│     Observable schema; trajectory log; seeded instance manifest;     │
│     integrity token binding instance ↔ user ↔ attempt                │
├──────────────────────────────────────────────────────────────────────┤
│ L2  ARTEFACT                                                         │
│     Self-contained HTML5/JS micro-simulator, packaged as H5P,        │
│     Moodle page/file resource, or LTI-delivered tool                 │
├──────────────────────────────────────────────────────────────────────┤
│ L1  AUTHORING                                                        │
│     Learning-outcome blueprint → activity spec (JSON) → LLM          │
│     generation → automated validation → human review → deployment    │
└──────────────────────────────────────────────────────────────────────┘
```

**L1 Authoring.** The instructor writes a blueprint (outcome, misconception targets, prerequisite knowledge, time budget) which is expanded into a formal activity specification (Appendix A). The LLM generates artefact code, the parameter-space definition, the answer-key generator, the feedback bank and the Moodle import artefacts from that specification. Generation is specification-driven rather than conversational, because a specification can be versioned, diffed, re-run and audited; a chat transcript cannot.

**L2 Artefact.** A single-file HTML5 artefact with no external runtime dependencies is the default, for three reasons: it can be packaged as a custom H5P content type, it can be archived for reproducibility and moderation, and it can be reviewed in full by a human in minutes. Dependence on CDNs or external APIs is treated as a defect, since it breaks offline review, long-term archiving and institutional data control.

**L3 Instrumentation.** The artefact emits observables defined in the specification. Two design rules are load-bearing. First, **deterministic seeding**: the instance parameters are derived as `seed = H(activity_id ‖ user_id ‖ attempt_no ‖ course_secret)`, so the instance is reproducible by staff for regrading and appeals, but not predictable by students. Second, **grade-carrying is one-directional**: the artefact never asserts a grade to Moodle directly except through a channel Moodle authenticates (H5P xAPI within the Moodle session, or LTI 1.3 AGS with signed messages). Any design where the browser can POST an arbitrary score is rejected at review.

**L4 Grading.** Detailed in Section 5.

**L5 Feedback.** Feedback exists at three timescales: *immediate* in-artefact response to an action (e.g. an infeasible operating point flagged as it is selected); *per-try* feedback from the question engine when the learner submits a derived answer; and *post-hoc* gradebook or rubric feedback. The specification requires that every distractor and every anticipated misconception has an authored feedback string — a requirement that also functions as a quality gate, because a model that cannot articulate the misconception a distractor targets has usually generated an arbitrary distractor.

**L6 Analytics and governance.** Standard Moodle logs plus the observable stream support item analysis (facility, discrimination), outcome attainment mapping, and the cohort-level integrity signals of §7.4 — under the data-protection constraints of Section 10.

### 4.3 Parameterisation: the core integrity primitive

Parameterisation is the mechanism that makes P3 operative, and it must be designed rather than assumed. Four properties are required:

1. **Semantic invariance.** All instances must assess the same construct at the same difficulty. Randomising a pipe diameter is safe; randomising it into a regime where the flow becomes turbulent for some students and laminar for others is not, unless the regime transition *is* the construct. The specification therefore requires explicit *validity constraints* on the parameter space, and the validation stage rejects parameter draws violating them (Appendix A, `constraints`).
2. **Sufficient cardinality.** The instance space must be large enough that collision within a cohort is improbable and enumeration is infeasible. We recommend effective cardinality ≥ 10⁴ for formative use and ≥ 10⁶ for summative use, computed *after* applying validity constraints, not before.
3. **Answer non-transferability.** Numeric answers must differ across instances by more than grading tolerance. The validation stage checks pairwise answer separation across a Monte Carlo sample of instances and flags parameters that fail to propagate to the answer — a common and easily missed generation defect where a randomised variable cancels out.
4. **Structural variation where affordable.** Beyond numbers, varying which component fails, which constraint binds, or which of several equivalent formulations is presented raises the cost of sharing *method* as well as *answer*. This is cheap for LLM authoring (generate k structural variants) and expensive for manual authoring, and is thus a place where the technology genuinely changes what is feasible.

This is the same principle underlying calculated questions and STACK's randomisation (Sangwin, 2013), and the same principle behind automatic item generation's item models (Gierl & Lai, 2013). The contribution here is applying it to *interactive artefacts and their embedded narratives*, not only to symbolic items.

### 4.4 The authoring pipeline

The pipeline has seven stages with two mandatory human gates.

| # | Stage | Actor | Output | Gate |
|---|-------|-------|--------|------|
| 1 | Blueprint | Instructor | Outcome, misconceptions, prerequisites, time budget, load ceiling | — |
| 2 | Specification | Instructor + LLM | `activity.json` conforming to Appendix A schema | **Human gate 1: construct validity** |
| 3 | Generation | LLM | Artefact HTML5, parameter generator, reference solver, feedback bank, Moodle import files | — |
| 4 | Automated validation | CI | Schema conformance, solver/artefact agreement over N instances, constraint satisfaction, answer separation, accessibility scan, dependency scan | Automated: fail → regenerate |
| 5 | Expert review | Instructor/SME | Annotated review against Appendix D rubric | **Human gate 2: deployment approval** |
| 6 | Deployment | Instructor | Moodle activity + question bank import + gradebook/completion configuration | — |
| 7 | Monitoring | Instructor + CI | Item statistics, defect reports, integrity signals, scheduled regeneration | Triggers return to 2 or 3 |

Stage 4 deserves emphasis because it is what makes the approach defensible against the hallucination problem (Ji et al., 2023; Kurdi et al., 2020). The key technique is **independent redundant derivation**: the reference solver is generated *separately* from the simulator, ideally in a different representation (e.g. closed-form analytic solution versus the simulator's numerical integration), and the two are cross-checked over a Monte Carlo sample of the parameter space. Agreement within tolerance across thousands of instances is meaningful evidence; agreement on a single worked example the model produced for itself is not. Disagreement localises the defect, which is more useful than a global "verify the output" instruction.

For engineering domains, validation additionally includes **dimensional analysis** (unit consistency of every derived quantity), **physical plausibility bounds** (efficiencies in [0,1], temperatures above absolute zero, mass and energy balances closing to tolerance), and **limiting-case checks** (does the simulator reproduce known analytic limits?). These are mechanically checkable and catch the majority of plausible-but-wrong generated physics in our design experience.

### 4.5 Reproducibility and archiving

Every deployed activity is archived as a version-controlled bundle: specification, generated artefact, reference solver, validation report, review record, model identifier and generation parameters, and the Moodle import files. This is required for three reasons: appeals (a student disputing a grade must be able to have their exact instance reconstructed), moderation (external examiners must be able to inspect what was assessed), and research reproducibility. Treating generated teaching artefacts as disposable chat output is incompatible with all three.

### 4.6 Quality assurance and failure modes

Generated activities fail in characteristic ways. The review rubric (Appendix D) targets them explicitly:

- **Physics/domain error.** Plausible but wrong model behaviour. *Control:* independent redundant derivation, dimensional analysis, limiting cases, SME review.
- **Degenerate parameterisation.** Randomisation that does not reach the answer, or that violates validity constraints in part of the space. *Control:* Monte Carlo constraint and separation testing.
- **Extraneous cognitive load.** Elaborate interfaces, gratuitous narrative, split attention. *Control:* load ceiling in the specification; reviewer authority to reject on this ground alone (Sweller, 1988; Mayer, 2009).
- **Under-scaffolding.** Open sandbox with no staged support, which the discovery-learning literature predicts will fail for novices (de Jong & van Joolingen, 1998; Kirschner et al., 2006). *Control:* specification requires a scaffold ladder with at least three levels.
- **Construct irrelevance.** Score driven by manual dexterity, reading speed, reaction time or visual acuity rather than the target competence. *Control:* reviewer check; no timed twitch mechanics for non-speed constructs; accessibility testing.
- **Accessibility failure.** Colour-only encoding, keyboard-inaccessible controls, missing labels, motion without reduced-motion handling. *Control:* automated WCAG 2.2 AA scan plus manual keyboard and screen-reader pass (W3C, 2023).
- **Grade-channel weakness.** Client-asserted scores, guessable seeds, replayable completion tokens. *Control:* architectural rule in §4.2 (L3); security review.
- **Cultural or contextual narrowness.** Scenarios assuming a specific national, professional or gendered context. *Control:* review; parameterise context where possible.

---

## 5. Moodle Grading-Integration Patterns

The framework's fifth criterion — no bespoke server-side grading — is satisfied by five patterns. Each is characterised by where evidence is produced, what carries it into Moodle, and what Moodle does with it.

Pattern E, the Cloze answer-field bridge (§5.5), is presented last but is in practice the entry point: it is the only pattern deployable by a single teacher with no plugin, no institutional approval and no infrastructure, and it is the one we recommend starting with. Patterns A and B are the natural next steps; C and D address tamper-resistance at scale and higher-order outcomes respectively.

### 5.1 Pattern A — Simulator-as-instrument, question-engine-as-grader

**Shape.** The generated artefact is an *instrument* the student must operate to obtain data; the graded submission is a set of derived quantities entered into a Moodle `Formulas` (or STACK, or calculated) question in the same course page or an adjacent quiz.

**Why it is the default.** It requires no trust in the artefact at all. The artefact can be a static file resource; all grading, tolerance handling, unit checking, partial credit, multi-try penalties and feedback are performed by Moodle's question engine, which is mature, auditable, and already integrated with the gradebook and with the institution's moderation processes. The `Formulas` type is particularly well-suited because it supports multi-part questions with independent grading, unit-aware numerical answers, per-part feedback and randomised variables declared directly in the question (Lau & Védrine, 2023); STACK extends this to algebraic responses with potential response trees (Sangwin, 2013).

**Instance binding.** The question's random variables and the artefact's seed must produce the *same* instance. Two implementations work in practice: (i) the question displays a short *instance code* which the student enters into the simulator to configure it; or (ii) the simulator derives its seed from the Moodle user and attempt context and displays the derived parameters, which the student enters into the question, with the question's grading criteria written as a function of those entered parameters. Implementation (i) is simpler and is used in the worked example of §6.1; implementation (ii) removes the transcription step but requires the question to grade conditionally on student-supplied parameters, which `Formulas` supports through its variable and grading-criteria facilities.

**Evidence captured.** Final and intermediate derived quantities; number of tries; per-part correctness; time in the quiz. Trajectory evidence inside the simulator is not captured in this pattern — the trade for its simplicity.

**Pedagogical note.** Setting the question behaviour to `interactive with multiple tries` with a modest penalty per try (e.g. 25–33%) and authoring hint text per try implements the formative-feedback evidence base directly (Hattie & Timperley, 2007; Shute, 2008), while retrieval-with-feedback across repeated attempts supports retention (Roediger & Karpicke, 2006).

### 5.2 Pattern B — Instrumented H5P activity reporting via xAPI

**Shape.** The artefact is packaged as an H5P content type (or wraps one) and reports completion and score through xAPI statements, which Moodle's core H5P integration consumes and writes to a grade item and the log store (ADL Initiative, 2017; Joubel, 2024).

**When to use it.** When the *trajectory* is the assessed evidence — fault-finding sequence, exploration strategy, recovery from induced error — rather than a derived number. This is the pattern that implements reduced-fidelity stealth assessment (§3.2): indicator observables are computed inside the artefact and reported as a scaled score plus structured statement extensions.

**Security considerations.** The client computes the score, so the score is only as trustworthy as the client. This is acceptable for formative and low-stakes summative use and is the same trust model as all existing H5P grading. For higher stakes, Pattern B is combined with Pattern A (the trajectory score is formative and gates access; the derived-quantity score is summative), or moved to Pattern C.

**Configuration.** The H5P activity's grade item feeds a gradebook category; `restrict access` on the subsequent activity is conditioned on a minimum grade or on activity completion, producing a declarative mastery ladder without code.

### 5.3 Pattern C — External tool via LTI 1.3 with Assignment and Grade Services

**Shape.** The artefact is hosted as an LTI 1.3 tool; Moodle launches it with a signed, user-identified message; the tool posts scores back through AGS (1EdTech, 2019).

**When to use it.** When server-side state is genuinely required: server-computed seeds that the client never sees, server-side solution checking, multi-session persistence, collaborative or multi-player variants, or higher-stakes summative use where client-side scoring is unacceptable. Also when a single artefact is shared across institutions.

**Cost.** This is the only pattern that requires operating a service, and therefore the only one with ongoing hosting, security-patching and availability obligations. Departments should adopt it deliberately, not by default. The framework's position is that most learning value is obtainable at Pattern A/B cost.

### 5.4 Pattern D — Generated artefact plus Workshop peer assessment

**Shape.** Students play the simulation, then submit a short justification, design decision or interpretation to Moodle's Workshop module, which distributes submissions for rubric-based peer assessment with grading-of-grading.

**Why it belongs in an "automatic grading" framework.** Higher-order outcomes — judgement, justification, critique of a model's assumptions — resist automatic scoring. Workshop does not automate the *judgement*, but it automates the *logistics* of distributed judgement and, through grading-grade computation, produces a second, automatically computed grade for the quality of a student's evaluation. This directly targets evaluative judgement, which Bearman et al. (2024) argue is the key capability for a GenAI-saturated environment, and it exploits the fact that peer review of *one's own unique instance's solution* is not outsourceable in the same way a generic essay is.

**Pairing.** Pattern D is always paired with A or B: the simulation grade is automatic, the justification grade is peer-assessed, and the gradebook combines them with a calculated category.

### 5.5 Pattern E — the Cloze answer-field bridge

**Shape.** The generated artefact is placed *directly in the question text* of a standard Moodle **Embedded answers (Cloze)** question, together with one or more Cloze answer-field declarations wrapped in hidden elements. The artefact's JavaScript locates those rendered inputs and writes to them as the learner plays: the score into a `NUMERICAL` field, and optionally a compact trajectory record into a `SHORTANSWER` field. When the learner submits, Moodle grades those responses exactly as it grades any other Cloze response, and the mark flows to the gradebook, the response report and the question statistics with no special handling.

```
generated game (HTML/JS in the question text)
        │  setScore(n) / logStep(tag)
        ▼
hidden {1:NUMERICAL:…} and {1:SHORTANSWER:…} inputs
        │  ordinary form submission
        ▼
Moodle question engine → gradebook, reports, item statistics
```

**Why it matters more than its simplicity suggests.** Patterns A–D each require something from someone other than the teacher: a plugin installed (`Formulas`, STACK), H5P enabled, a tool registered, or a Workshop configured across a cohort. Pattern E requires *nothing*. A teacher with permission to author a question can deploy a generated, automatically graded interactive activity the same afternoon, on an unmodified Moodle. Given that institutional Moodle estates are conservatively managed and that the adoption record of proposals requiring new server components is poor (§9.4), this property is worth more than the technical advantages of the other patterns. It is also the pattern that makes the framework available to school teachers and to under-resourced institutions, which is where the affordability argument of §1.1 has the most force.

**Grading correctly.** A subtlety here is consequential and easy to get wrong. A `NUMERICAL` Cloze answer is graded **right or wrong against a tolerance**; it does not scale the mark with the submitted value. A field declared as `{1:NUMERICAL:=7:2}` therefore awards full marks for any score between 5 and 9 and zero for everything else, including a perfect score — which for a ten-point game inverts the intended grading. Proportional autograding requires one accepted answer per attainable score, each carrying its own percentage:

```
{1:NUMERICAL:=10:0~%90%9:0~%80%8:0~%70%7:0~%60%6:0~%50%5:0~%40%4:0~%30%3:0~%20%2:0~%10%1:0~%0%0:0}
```

This is mechanically generable from the game's maximum score, and Appendix E supplies the generator. We record the error because it is silent: the question imports, previews, plays and submits without complaint, and produces wrong marks.

**Recording process, not only outcome.** A second hidden field declared as `{1:SHORTANSWER:=*}` accepts any value and therefore records rather than grades. Writing a short trajectory tag to it at each meaningful step — which question, what the learner did, whether it was right — puts process evidence into Moodle's ordinary response report, where an instructor already looks. This is the cheapest available implementation of the reduced-fidelity stealth assessment of §3.2, and it is what makes Pattern E an evidentiary improvement over a bare score rather than merely a convenient one. The wildcard subquestion still carries weight, so the question's maximum grade must be set with that in mind.

**Security: what hiding the field does and does not do.** The answer fields are hidden with `display:none`. This removes them from the learner's view and prevents accidental editing. It provides no protection against deliberate editing: anyone who opens a browser console can assign the field a value directly, and no amount of client-side JavaScript can prevent this, because the code enforcing the rule is code the learner controls. A checksum or an obfuscated token raises the cost from *type a number* to *read the JavaScript*; that is a genuine increase against a ten-year-old and no obstacle whatever to a motivated undergraduate.

We state this plainly because the temptation to describe a hidden field as tamper-proof is strong and the claim is false. The correct inference is not that the pattern is unusable but that its stakes must match its assurance: Pattern E is well suited to formative practice, mastery gating and low-weight continuous assessment, and unsuited to carrying high-stakes marks unaided. Where marks matter, Pattern E pairs with Pattern A (the game is formative and gates a tamper-resistant question) or gives way to Pattern C. The trajectory field supplies a secondary signal — a forged maximum score with an empty or incoherent trace is visible in the response report — which is useful for a conversation and, per §7.3, is not evidence for a misconduct case.

**Additional failure modes.** Beyond the grading error above, the pattern has several sharp edges that recur across generated artefacts and are therefore worth enumerating as prompt constraints rather than rediscovering per activity: a `<button>` inside Moodle's question form defaults to `type="submit"` and will submit the attempt when pressed; `document.currentScript` is null if the script is ever re-inserted rather than parsed with the page, so an unguarded `.closest()` call makes the game silently fail to appear; a `NaN` written to the answer field submits as a blank response and scores zero; and if the answer field is absent — which is how some review states render — a naive read-only test leaves the game live while every point the learner earns goes nowhere. Appendix E's hardened template addresses each of these, and the accompanying browser test asserts the resulting contract.

**Applicability limits.** Pattern E carries whatever the artefact can express as a response value, so it suits scores, counts, derived quantities and short trajectory digests. It is not suited to long trajectories (the response is a single text value), to artefacts requiring server-side state, or to anything needing tamper-resistant scoring. Sites also vary in whether `<script>` in question text survives filtering, which is a deployment prerequisite to test once rather than a per-activity concern.

### 5.6 Selecting a pattern

| Requirement | A | B | C | D | E |
|---|---|---|---|---|---|
| No server to operate | ✔ | ✔ | ✘ | ✔ | ✔ |
| No plugin or admin action required | ✘ | ✔ | ✘ | ✔ | ✔ |
| Deployable by one teacher, unaided | ✘ | partial | ✘ | ✘ | ✔ |
| Trajectory/process evidence | ✘ | ✔ | ✔ | partial | ✔ (short) |
| Tamper-resistant scoring | ✔ | ✘ | ✔ | ✔ | ✘ |
| Algebraic / unit-aware grading | ✔ | ✘ | ✔ | ✘ | ✘ |
| Higher-order judgement | ✘ | ✘ | ✘ | ✔ | ✘ |
| Authoring effort | low | medium | high | low | low |
| Suitable for summative use | ✔ | with care | ✔ | ✔ | low weight only |

A pragmatic default for a course unit: **start with E to get something real in front of students this week; A for summative marks; B for formative mastery gating where the trajectory is richer than a Cloze field can hold; D once per semester for judgement outcomes; C only where the others genuinely cannot serve.** The ordering is deliberate: the most common failure of educational technology proposals is not choosing the wrong architecture but never deploying one, and E is the pattern with no gatekeeper between the teacher and a working activity.

---

## 6. Worked Examples

Three vignettes illustrate the framework across domains. Each states the outcome, the parameterisation, the observables, the Moodle configuration and the integrity properties. Complete machine-readable artefacts for Vignette 1 are provided in the repository accompanying this paper (`artifacts/`), including the activity specification and an importable Moodle `Formulas` question.

### 6.1 Vignette 1 — "Plant Operator": a Rankine-cycle power-plant simulator (mechanical/energy engineering)

**Outcome.** Given plant operating conditions, compute cycle thermal efficiency and specific work; predict and explain the effect of boiler pressure, superheat temperature and condenser pressure on efficiency and on turbine-exit quality; identify operating points that violate the turbine-exit moisture limit.

**Targeted misconceptions.** (i) That raising condenser pressure improves output; (ii) that higher boiler pressure always improves efficiency, ignoring the moisture constraint; (iii) conflating thermal efficiency with isentropic efficiency; (iv) neglecting pump work as always negligible without checking.

**Artefact.** A single-file HTML5 simulator with three sliders (boiler pressure, superheat temperature, condenser pressure) and one input (turbine isentropic efficiency). It displays a live T–s diagram, a state-point table, and computed efficiency, specific work and turbine-exit quality, with an explicit warning region when exit quality falls below the specified limit. Steam properties are implemented from a tabulated dataset embedded in the file, with the tabulation itself validated against reference values at stage 4 of the pipeline.

**Parameterisation.** Per student: turbine isentropic efficiency η_t ∈ [0.78, 0.92]; pump isentropic efficiency η_p ∈ [0.70, 0.85]; required net power output Ẇ_net ∈ [40, 180] MW; minimum permissible turbine-exit quality x_min ∈ {0.86, 0.87, 0.88, 0.89, 0.90}; plus a structural variant selecting whether the binding design constraint is the moisture limit, a condenser cooling-water temperature limit, or a boiler material temperature limit. At the step sizes used in the accompanying artefact, effective cardinality after constraint filtering is **134,850** for the continuous and discrete parameters, and the structural variant multiplies it by three.

**Validity constraints.** All draws must admit at least one feasible operating point satisfying all limits; the efficiency difference between the optimal feasible point and the naive (constraint-ignoring) point must exceed 1.5 percentage points, so that the constraint is consequential; the required mass flow must be physically reasonable.

**Observables.** O1 number of operating points evaluated before submission; O2 whether the student ever entered and then left the infeasible-moisture region (evidence of constraint discovery); O3 monotonic versus random search pattern in the pressure sweep; O4 time to first feasible point; O5 final submitted design point; O6 derived answers.

**Moodle configuration (Pattern A + B + D).**
- The simulator is delivered as an H5P activity reporting O1–O4 as a formative "engineering process" grade item (Pattern B), used only to gate the next activity via `restrict access`.
- A `Formulas` question in a quiz grades the derived quantities as five independently graded parts with per-part feedback, under `interactive with multiple tries` with a one-third per-try penalty and three authored hints (Appendix C provides the importable XML).
- A Workshop activity (Pattern D) asks for a 250-word justification of the chosen design point with explicit reference to the binding constraint, peer-assessed against a four-criterion rubric.
- A gradebook calculated category combines the quiz (70%) and Workshop submission+assessment grades (30%).

**Validation, and a defect the gate caught.** The stage-4 validator (Appendix C companion, `artifacts/validate_rankine.py`) implements the independent redundant derivation of §4.4. It confirmed that the energy balance closes to a relative residual of 1.8 × 10⁻¹⁶, that the ideal-component limit (η_t = η_p = 1) reproduces the textbook ideal-cycle efficiency of 0.3915 for 8 MPa/480 °C/10 kPa, that degenerate low-efficiency draws are correctly rejected as infeasible, and that no instance in a 6,000-sample constrained draw violates the physical bounds.

It also *rejected the first version of the question*. The reachability check (D8 in Appendix D) found that the randomised pump isentropic efficiency η_p moved no graded answer by more than the 1% grading tolerance, because pump work is approximately 1% of net work in this cycle: η_p was varying the question's appearance without varying its assessment. This is precisely the degenerate-parameterisation failure mode of §4.6, it is invisible on inspection of a plausible-looking question, and it would have been deployed. The regenerated version adds a fifth graded part — actual feed-pump specific work — which η_p moves by roughly 20% across the cohort and which additionally targets misconception (iv). Per-part separation beyond the 1% tolerance is 89.9% (η_th), 89.7% (w_net), 77.1% (x₄), 98.7% (ṁ) and 90.6% (w_p); **joint separation — the probability that a wholesale copy of another student's answer set fails on at least one part — rose from 99.63% to 99.94%.**

We report this episode rather than a clean result because it is the evidence for the paper's methodological claim: verification of generated assessment content has to be mechanical and adversarial, and "the model checked its own work" is not verification.

**Integrity properties.** A student who obtains a peer's final answer obtains a wrong answer (P3). A student who asks an LLM for "the efficiency of a Rankine cycle" without operating the simulator cannot supply the instance-specific constraint values or a defensible justification of the binding constraint. The observables O2–O3 provide cohort-level signal: a submission with a correct constrained-optimal design point but zero recorded exploration of the infeasible region is anomalous, though not by itself evidence of misconduct (§7.4).

### 6.2 Vignette 2 — "Fault Bay": a circuit fault-finding escape room (electrical engineering)

**Outcome.** Diagnose a fault in a DC network from terminal measurements; apply systematic bisection rather than random substitution; justify measurement choice on information-gain grounds.

**Artefact.** A schematic with virtual instruments (DMM probes, at a small "cost" per measurement) and a component-replacement action. The student must localise an injected fault within a measurement budget. The budget is the game mechanic; the information economics are the learning objective.

**Parameterisation.** Fault type (open, short, drift) × fault location (12 candidate components) × component values × measurement budget. Structural variation includes a small number of topologies. Effective cardinality is large, and — significant here — *the identity of the faulty component differs per student*, so the single most shareable piece of information is useless.

**Observables.** Measurement sequence; whether each measurement halves the remaining candidate set (a computable information-gain measure); budget consumed; number of unnecessary replacements; final diagnosis.

**Moodle configuration (Pattern B primary).** H5P activity reports a composite score: 50% correct diagnosis, 30% measurement efficiency versus an optimal-bisection baseline computed by the reference solver, 20% budget adherence. A follow-up `Formulas` question asks the student to compute the expected value of a specified measurement, restoring a tamper-resistant summative component (Pattern A). Completion of the H5P activity at ≥ 60% is a `restrict access` condition for the summative quiz — a mastery ladder.

**Integrity note.** This vignette illustrates P4 clearly: the assessed competence is a *search policy*, which only exists as a trajectory. There is no artefact for a third party to hand over that constitutes evidence of the competence, because the evidence *is* the sequence.

### 6.3 Vignette 3 — "Ledger Lab": a concurrency and correctness game (computing)

**Outcome.** Identify race conditions in a concurrent account-ledger scenario; select and justify a correct synchronisation strategy; distinguish a genuine fix from one that merely reduces failure probability.

**Artefact.** A visual scheduler in which the student interleaves operations from two or more threads to *provoke* a failing interleaving, then applies a synchronisation primitive and demonstrates that the failure is no longer reachable within the explored space. The game inverts the usual task: the student is rewarded for *finding* the bug, which is pedagogically preferable to being told it exists.

**Parameterisation.** Operation sets, initial balances, number of threads, which invariant is violated, and which of several candidate "fixes" is the correct one versus superficially plausible. Distractor fixes are generated per instance, targeting documented misconceptions.

**Observables.** Whether the student found a failing interleaving unaided or after hints; number of interleavings explored; whether the selected fix is correct; whether the student's post-fix exploration was adequate to justify the claim.

**Moodle configuration.** Pattern B for the game score; Pattern A for a short `Formulas`/multi-choice set on the reasoning; Pattern D for a written justification of why the chosen primitive is sufficient, peer-assessed. This vignette also connects to the LLM-generated-exercise literature in computing education (Sarsa et al., 2022; Finnie-Ansley et al., 2022), where generation quality for programming artefacts is best documented.

### 6.4 Vignette 4 — "Fraction Shading": a primary-school fractions game (Pattern E, fully worked)

The first three vignettes are university engineering and computing. This one is deliberately not: it is a fractions game for ten-year-olds, and it is included because it is the case where the framework's affordability claim is most consequential and its assurance claim least demanding. It is also the only vignette supplied as a complete, browser-tested artefact rather than a design.

**Outcome.** Given a target fraction and a shape divided into equal parts, shade the correct number of parts; recognise that the *count* of parts determines the fraction irrespective of which parts are chosen; recognise equivalent fractions presented in different denominators.

**Targeted misconceptions.** (i) That the shaded parts must be adjacent or must start from a particular position; (ii) reading the denominator as the number of *unshaded* parts; (iii) failing to recognise 2/6 and 4/6 as equivalent to 1/3 and 2/3 when the shape is cut differently.

**Artefact.** A single self-contained HTML/JavaScript game rendered inside the Cloze question text. It presents ten fixed questions of increasing difficulty, alternating between a circle cut into slices and a bar cut into segments. The learner clicks or keyboard-activates parts to shade them, sees a running count ("you have shaded 2 of 3 parts"), and presses *Check*. A correct count scores one point; an incorrect one scores nothing, applies no penalty, and shades the correct answer on the shape so the learner sees the target rather than only being told it. Question order is fixed rather than random, so that a child describing "question 4" and an adult looking over their shoulder see the same thing.

**Accessibility.** Every part is a focusable control with an accessible name, operable with Enter or Space; shading is signalled by a hatch pattern as well as a fill colour, so it survives colour-blindness and monochrome printing; the browser's default focus ring, which for a pie wedge is drawn as a rectangle across neighbouring slices, is replaced with an outline following the actual shape; status messages are announced through an `aria-live` region; and there is no timer, because a learner using a screen reader or simply thinking must not lose points to a clock.

**Moodle configuration (Pattern E alone).** One Embedded answers (Cloze) question. A hidden `NUMERICAL` field carrying the partial-credit answer list of §5.5 grades the score proportionally out of ten; a hidden `SHORTANSWER` field records the trajectory. Question penalty zero. Deferred feedback behaviour. Nothing else — no plugin, no H5P, no external tool.

**Verification.** The artefact was exercised in a headless browser against a simulated Moodle Cloze DOM (Appendix E). The test plays all ten questions, deliberately failing one, and asserts that the hidden field and the visible score agree at every step; that the single wrong answer costs exactly one point and applies no penalty; that the final field value is the mark Moodle will grade; that review mode restores the saved score and renders no interactive controls; that every shape part is focusable and toggles with Enter and Space; and that the score display element is never destroyed by the game appending to its container. All checks pass.

The same test suite contains one deliberately passing check labelled a known limitation: a single console statement sets the score field to ten without playing. It is written as a test rather than a footnote so that the limitation is recorded in the same place as the guarantees, and cannot quietly be forgotten when someone later proposes using this pattern for marks that matter.

**Integrity properties, proportionately.** This activity carries no meaningful integrity requirement, and it would be a mistake to engineer one. A ten-year-old who edits the hidden field has forgone the practice, which is the entire value on offer; there is no credential, no ranking and no scarce good being competed for. The framework's position is that assurance should be matched to stakes rather than maximised, and that the cost of over-engineering integrity in primary education — surveillance of children, complexity that teachers cannot maintain — is real and is usually larger than the harm being prevented.

### 6.5 What the vignettes have in common

Each moves the assessed observable from *a producible artefact* to *a trajectory through a per-student instance*, keeps all grading inside Moodle's native features, and closes the feedback loop within the activity. None of them requires the instructor to write application code; all of them require the instructor to exercise domain judgement at the two human gates.

They differ in one respect worth making explicit: the assurance each needs. Vignette 1 carries summative engineering marks and is built accordingly, with parameterisation, tamper-resistant grading and a validated answer key. Vignette 4 carries a child's fraction practice and is built accordingly, with none of that. Treating these as the same problem — which a framework claiming to solve "AI cheating" is under constant pressure to do — would make the primary-school case unbuildable and the university case complacent. That division of labour — the model does production, the academic does validation and judgement — is the framework's central practical claim about sustainability.

---

## 7. Integrity Analysis: Adversary Model and Mitigations

Claims about cheating resistance are only meaningful relative to a stated adversary. This section states one, evaluates the framework against it honestly, and identifies what remains unmitigated.

### 7.1 Adversary model

We consider five adversary classes, ordered by capability:

- **A1 — Opportunistic sharer.** Obtains a peer's final answers through a group chat or file-sharing site. Low effort, high historical prevalence (Lancaster & Cotarlan, 2021; Northcutt et al., 2016).
- **A2 — Prompt-only LLM user.** Pastes the visible task text into a chatbot and transcribes the answer. Near-zero effort; the dominant post-2022 vector (Susnjak, 2024).
- **A3 — Multimodal LLM user.** Screenshots the artefact, asks a vision-capable model to interpret it and to recommend actions, and operates the interface manually. Moderate effort, growing prevalence.
- **A4 — Agent operator.** Runs a computer-use agent that drives the artefact autonomously. Currently non-trivial setup, per-instance runtime, and supervision; capability is improving.
- **A5 — Human proxy (contract cheating).** Pays a person to complete the activity, typically via credential sharing. High cost; the classical vector (Newton, 2018; Bretag et al., 2019).

### 7.2 Attack–mitigation matrix

| Attack | Effect on conventional Moodle quiz / essay | Effect on a GAIMS activity | Residual risk |
|---|---|---|---|
| A1 share final answers | Fully effective | **Defeated**: peer's answers are wrong for this instance (P3) | Sharing of *method*, which is a legitimate learning behaviour we do not aim to prevent |
| A1 solution-bank harvesting | Fully effective over time | **Defeated** if cardinality ≥ 10⁶ and structural variants rotate per cohort | Bank of *worked methods*; acceptable |
| A2 prompt-only LLM | Fully effective for text/numeric items | **Substantially degraded**: the model lacks instance parameters, live state and the trajectory; a student must at minimum operate the artefact to obtain the data | A2 remains effective for the *conceptual justification* component if written asynchronously; mitigate via Pattern D and oral checks |
| A3 multimodal LLM assistance | Effective | **Partially effective**: the model can advise on actions, but the student must still operate, observe and iterate — which is itself much of the target cognition | This is arguably legitimate tool-assisted practice for many outcomes; declare it in the AI-use policy rather than pretending it is prevented |
| A4 agent operation | Effective | **Feasible but costly**: per-instance runtime, supervision, brittle UI interaction, and trajectory artefacts (uniform latencies, no exploratory error) | **Not mitigated.** Requires secured anchor points (§7.5) |
| A5 human proxy | Effective | **Cost restored to classical contract cheating**: proxy must operate a 20-minute interactive task per instance, cannot batch | Unchanged in kind; unchanged in low prevalence at high cost |
| Client tampering (score forging) | N/A | Blocked for Patterns A/C/D; **present by construction for Patterns B and E** — a hidden answer field is invisible, not protected, and a console statement sets it | Keep B and E formative or low-weight; pair with A; move to C where marks matter |
| Seed prediction | N/A | Blocked by keyed seed derivation with a course secret | Secret leakage; rotate per cohort |
| Replay of another user's session | N/A | Blocked by binding instance to user and attempt | Credential sharing = A5 |

### 7.3 What the framework does *not* claim

Three explicit disclaimers, offered because the literature in this area is prone to overclaiming:

1. **GAIMS activities are not AI-proof.** A4 is unmitigated by design alone. Any assessment delivered to an unsupervised networked device is, in the limit, delegable.
2. **Trajectory anomaly is not proof of misconduct.** Unusual process data has many innocent explanations: prior domain expertise, an interrupted session, assistive technology, a slow connection, or simply an efficient learner. Using it as evidence in a misconduct case would be an error of the same class as relying on AI-text detectors (Weber-Wulff et al., 2023).
3. **Parameterisation alone is insufficient.** It defeats sharing, not solving (P3). Frameworks that stop at randomisation and declare the problem solved are mistaken.
4. **A hidden answer field is not a secured answer field.** Hiding an input with `display:none` prevents accidental editing and nothing else. No client-side measure can prevent a learner from setting a value in code they control, and describing such a field as tamper-proof — a claim this pattern invites — is false. The remedy is to match stakes to assurance (§5.5), not to obfuscate.

### 7.4 Legitimate use of process signal

If trajectory data cannot be used punitively, what is it for? Three defensible uses:

- **Validity evidence.** Demonstrating, for programme accreditation and internal quality assurance, that the grade is supported by observed process, not only by a final answer. This is an ECD argument (Mislevy et al., 2003), not a policing one.
- **Formative intervention.** Identifying students whose process indicates a specific misconception (e.g. never varying more than one parameter, never testing a constraint) and delivering targeted support — the actual pedagogical value of learning analytics (Gašević et al., 2015).
- **Non-punitive triggering.** Where a pattern is anomalous, the appropriate response is an *ordinary, universally available* mechanism — a two-minute oral check on the student's own instance, offered to a random sample of the cohort as standard practice, not to flagged individuals. This preserves due process, avoids the false-accusation harms documented for detectors (Liang et al., 2023), and is consistent with assessment-security reasoning (Dawson, 2021).

### 7.5 Defence in depth: the anchor-point principle

Because A4 is unmitigated, GAIMS must be embedded in a programme-level design, not deployed as a standalone solution. We adopt the widely argued position that a programme needs a small number of **secured anchor points** — assessments conducted under conditions where identity and authorship are assured — whose function is to *validate* the much larger body of unsecured continuous assessment (Dawson, 2021; Lodge et al., 2023).

The role of GAIMS in this architecture is specific and, we argue, more important than its role as a graded activity: a student who has genuinely completed a semester of interactive, feedback-rich, per-instance activities will perform at the anchor point; a student who has outsourced them will not. Continuous GAIMS grades and anchor-point performance should correlate; systematic divergence at cohort level is a programme-quality signal, and at individual level is a reason for supportive follow-up. The interactive activities thus serve simultaneously as learning, as formative evidence, and as a *consistency baseline* — which is a stronger integrity architecture than any single secured examination, because it makes sustained deception expensive across a semester rather than risky for two hours.

---

## 8. Proposed Evaluation

The framework is offered as a testable proposition. This section specifies the study we intend to run, at sufficient detail to be pre-registered. We state it as a protocol rather than reporting results, and we specify in advance what would count as disconfirmation.

### 8.1 Design

A two-semester, multi-cohort **quasi-experimental study with a within-subjects crossover** in an undergraduate engineering programme, supplemented by qualitative strands.

- **Setting.** Two second-year engineering courses (thermodynamics; circuits), each with n ≈ 120 students per cohort, delivered through Moodle.
- **Conditions.** *GAIMS* (interactive parameterised activity with Pattern A+B grading) versus *Control* (matched conventional Moodle quiz with calculated questions, identical learning outcomes, identical time-on-task allocation, identical feedback timing). The control is deliberately strong: it is randomised and feedback-rich, so that the contrast isolates *interactivity and process evidence*, not *randomisation* or *feedback*, both of which are already known to work.
- **Crossover.** Topic blocks are counterbalanced: each student experiences GAIMS for half the topics and Control for the other half, with block-to-condition assignment counterbalanced across two cohorts to separate condition from topic difficulty.

### 8.2 Measures

**Learning (RQ3, primary).**
- Pre/post concept-inventory scores on validated instruments where available for the domain, administered under invigilated conditions to remove the confound of AI-assisted testing.
- Performance on invigilated end-of-semester anchor items, blocked by topic and thus by condition.
- Transfer items: novel problems not isomorphic to either treatment.

**Engagement and motivation (RQ3, secondary).**
- Intrinsic Motivation Inventory subscales (interest/enjoyment, perceived competence, pressure/tension), interpreted within self-determination theory (Ryan & Deci, 2000).
- Behavioural engagement from Moodle logs: attempts per activity, voluntary re-attempts, session duration, distribution of activity across the week.

**Integrity-relevant indicators (RQ2, exploratory, cohort level only).**
- Answer-similarity statistics adapted from copy-detection work (Palazzo et al., 2010; Alexandron et al., 2017), applied at cohort level.
- Divergence between continuous-assessment grade and invigilated anchor performance, by condition.
- Anonymous self-report of AI use and outsourcing behaviour, collected under an amnesty protocol with no individual identification.

**Feasibility (RQ4).**
- Authoring wall-clock time per activity, split by pipeline stage.
- Defect counts by category at automated validation and at expert review (Appendix D categories), yielding a defect-per-activity rate and a human-review-minutes-per-activity figure.
- Post-deployment defect reports from students.
- Staff workload perception via interviews.

### 8.3 Analysis plan

Mixed-effects models with students as random effects and topic block as a crossed random effect, condition as the fixed effect of interest, and prior attainment as a covariate. Pre-registered primary outcome: post-test performance on invigilated anchor items, with the null hypothesis of no condition difference. Motivational outcomes analysed separately with correction for multiple comparisons. Qualitative strands (student focus groups; staff interviews) analysed thematically and used to interpret, not to corroborate, quantitative findings.

**Power.** Taking the active-learning literature as the outcome expectation (Freeman et al., 2014; Sitzmann, 2011; Wouters et al., 2013), we assume a realistic target effect of d ≈ 0.3 against a strong control. With a within-subjects crossover and n ≈ 240 across two cohorts, power exceeds 0.8 at α = 0.05 for d = 0.3, assuming a moderate within-student correlation across blocks. We pre-register the sample and the analysis to avoid the optional-stopping and outcome-switching problems endemic to educational technology evaluation.

### 8.4 Threats to validity

- **Novelty effect.** The crossover and the two-semester span partially address it; a third-semester follow-up is specified.
- **Instructor enthusiasm / allegiance bias.** Both conditions are authored and delivered by the same staff, and the control is designed to be genuinely good rather than a straw man. Blinding is not possible.
- **Time-on-task confound.** Controlled by design allocation and checked against log data.
- **Selection.** Quasi-experimental at cohort level; the within-subject crossover is the main defence.
- **Construct validity of the integrity measures.** Self-report of misconduct is unreliable even under amnesty; grade-divergence analysis is confounded by examination anxiety and by topic difficulty. These measures are explicitly exploratory, and we will not draw causal integrity conclusions from them.
- **Generalisability.** Two engineering courses at one institution. Replication in non-quantitative disciplines is necessary before general claims, and the framework's parameterisation mechanism is plainly easier in quantitative domains.

### 8.5 Falsification conditions

The framework should be considered disconfirmed, in whole or part, if: (a) invigilated anchor performance does not differ between conditions and motivational measures also show no benefit, indicating the added complexity buys nothing; (b) authoring plus review time per activity exceeds that of conventional item authoring for equivalent coverage, indicating the sustainability claim fails; (c) expert-review defect rates remain high after pipeline hardening, indicating the verification approach is inadequate; or (d) grade-divergence analysis shows *no* reduction relative to control, indicating the integrity mechanism does not operate as argued. We regard (b) and (c) as the most likely failure modes.

---

## 9. Discussion

### 9.1 Reframing the problem

The dominant institutional framing treats GenAI as a threat to be contained. This paper's framing is that GenAI exposed a pre-existing weakness: much of what was assessed online was assessed through *products* that were always weak evidence of the *processes* we care about. Copying in online homework was measurable and harmful to learning long before 2022 (Palazzo et al., 2010); solution banks were already undermining STEM problem sets (Lancaster & Cotarlan, 2021). GenAI did not create the validity gap; it made it impossible to ignore.

Read that way, the appropriate response is not restoration of the previous state but a shift in what counts as evidence — from artefact to trajectory, from single-instance to per-student-instance, from one-shot grading to feedback-rich iteration. All three of those shifts were previously blocked by production economics. That is the barrier this technology removes.

### 9.2 The division of labour that makes it sustainable

The framework's practical viability rests on a specific allocation: **the model does production; the academic does construct definition and validation.** This is the opposite of the "AI tutor" and "AI grader" proposals, which place the model in the judgement role where its failure modes (confident fabrication; opaque reasoning; inconsistency across equivalent responses) are most damaging and least detectable.

Placing generation, not judgement, in the model's hands has three consequences. Errors surface at authoring time, when a human is looking, rather than at grading time distributed across 200 students. Verification is mechanisable through independent redundant derivation, which has no analogue for judgement tasks. And accountability remains with the academic who approved the activity, which is the only arrangement compatible with existing quality-assurance and moderation processes.

### 9.3 Implications for practice

For a department adopting this, the realistic sequence is: (1) start with Pattern E on one topic, because it can be deployed this week by one person with no permission from anyone, and a working activity in front of students settles more design arguments than a term of discussion; (2) move the same activity to Pattern A once it matters for marks, since that requires no new infrastructure and no trust in the artefact; (3) build the validation harness before scaling, since it is what makes the second and subsequent activities cheap; (4) treat the activity bundle as version-controlled teaching infrastructure with the same review discipline as any other assessment material; (5) add Pattern B once the validation harness is trusted; (6) revise the course AI-use policy to state what tool assistance is permitted *during* these activities, since A3 is partly legitimate practice and pretending otherwise produces incoherent rules; and (7) establish the anchor points (§7.5) before relying on GAIMS grades summatively.

### 9.4 Relationship to existing Moodle practice

Pattern E requires nothing at all beyond a core Moodle question type. Nothing else in the framework requires plugins beyond `Formulas` and (optionally) STACK, both mature and widely deployed, plus core H5P. This is deliberate: institutional Moodle estates are conservatively managed, and proposals requiring new server components have a poor adoption record. The framework should be readable as "use what your Moodle already does, with content you could not previously afford to make."

### 9.5 Equity considerations

Three cut in favour and one against. In favour: unlimited low-stakes retries with immediate feedback advantage students who lack access to tutoring or study groups; per-instance tasks remove the advantage held by students with access to solution banks or well-resourced peer networks; and simulation-based tasks can reduce the penalty on students whose written English is weaker than their engineering reasoning. Against: interactive artefacts can introduce accessibility barriers that a text question does not, and can disadvantage students on low-bandwidth connections, shared devices or small screens. The accessibility gate (§4.6) and a mandatory non-interactive equivalent-task pathway for students with approved accommodations are therefore not optional extras but requirements of the framework.

---

## 10. Limitations

**Conceptual, not empirical.** The paper presents no outcome data. Section 8 specifies what would test it; until that is run, the learning claims rest on the transfer of prior evidence about games, simulations and feedback (Sitzmann, 2011; Wouters et al., 2013; Clark et al., 2016; Shute, 2008) to a delivery mechanism those studies did not examine, and that transfer may not hold.

**Domain asymmetry.** Parameterisation with semantic invariance is natural in quantitative and procedural domains and considerably harder in interpretive ones. We do not claim the framework generalises to, say, literary analysis without substantial adaptation, and structural variation there may not preserve difficulty.

**Generation quality is a moving and unmeasured target.** Defect rates depend on model, prompt, domain and reviewer stringency. The computing-education literature documents usable but imperfect generation (Sarsa et al., 2022; Leinonen et al., 2023); we have no equivalent measured baseline for interactive simulators, and RQ4 exists precisely because we do not.

**The A4 gap is real and widening.** Capability improvements in computer-use agents work against P4 over time. The framework's response is architectural (anchor points), not technical, and it should be honestly presented as such.

**Maintenance and drift.** Generated artefacts are software, with the maintenance obligations of software: browser changes, accessibility regressions, curriculum drift. A department that generates 40 activities has acquired 40 artefacts to maintain. The archiving requirement (§4.5) manages this but does not eliminate it.

**Model dependence and reproducibility.** Regenerating an activity with a different model version may yield materially different output. The bundle records model identity and generation parameters, but exact reproducibility is not achievable, which has implications for longitudinal research using these activities as instruments.

**Institutional prerequisites.** The framework assumes a Moodle estate where staff can install `Formulas`, enable H5P, and version-control teaching artefacts. Where central IT does not permit this, the pipeline stalls at deployment regardless of its merits.

---

## 11. Ethical and Data-Protection Considerations

**Process data is personal data.** Trajectory logs are behavioural records of identifiable individuals and, under GDPR-equivalent regimes, require a lawful basis, purpose limitation, data minimisation and defined retention. The framework's position: collect only the observables named in the specification (which is why the specification enumerates them), retain trajectory detail no longer than the appeals window plus one academic cycle, and aggregate or delete thereafter. Slade and Prinsloo's (2013) analysis of learning-analytics ethics — students as agents rather than data sources, transparency, and the obligation to act on what is learned — is adopted as the governing frame.

**Transparency over covertness.** "Stealth" in stealth assessment refers to non-interruption, not concealment. Students must be told, in the activity and in the course information, what is recorded, why, who can see it, how long it is kept, and how it affects their grade. Covert behavioural monitoring of students is not defensible merely because it is technically convenient.

**Due process.** Process data must not be used as evidence in misconduct proceedings (§7.3, §7.4). Institutions adopting the framework should state this in policy *before* deployment, because the temptation to use it punitively will arise the first time an anomalous trajectory appears.

**Accessibility as an ethical requirement.** WCAG 2.2 AA conformance (W3C, 2023) plus an equivalent-task pathway is a condition of deployment, not a refinement. An assessment a disabled student cannot operate is not a valid assessment for that student.

**Academic accountability for generated content.** The academic who approves an activity is responsible for its correctness, exactly as for a textbook chapter they assign. Provenance recording (§4.5) supports this; it does not transfer it.

**Environmental and cost considerations.** Generation has non-zero energy and financial cost. The micro-simulation scale and the archiving requirement both work in favour of generate-once-and-maintain rather than regenerate-per-use, which is the more responsible pattern and also the cheaper one.

---

## 12. Conclusion

Generative AI made product-based online assessment difficult to defend and, at the same time, made process-based interactive assessment affordable for the first time. This paper has argued that the second fact is the answer to the first, and has specified how the answer can be implemented on infrastructure most institutions already run.

The GAIMS framework contributes a reference architecture separating authoring, artefact, instrumentation, grading, feedback and analytics; four Moodle-native grading-integration patterns that require no bespoke server-side development; a parameterisation discipline with explicit validity constraints; a verification pipeline built on independent redundant derivation rather than on trusting model output; an adversary model with an honest account of what is and is not mitigated; and a pre-registerable evaluation design with stated falsification conditions.

The integrity argument is deliberately modest. GAIMS activities do not make cheating impossible; they make the honest path the cheapest path for most students most of the time, they defeat the historically dominant sharing vectors outright, and they produce evidence that supports a genuine validity argument. That is a better objective than an unachievable guarantee, and it has the advantage of being consistent with what is actually known about assessment security (Dawson, 2021) and about the unreliability of detection (Weber-Wulff et al., 2023).

The strongest claim we make is not about cheating at all. It is that an assessment regime in which students spend their time operating models, discovering constraints, recovering from induced failures and justifying decisions — with immediate feedback and unlimited retries on a task that is theirs alone — is a better education than one in which they submit documents. The integrity benefit is a consequence of that, not the reason for it.

---

## References

1EdTech Consortium. (2019). *Learning Tools Interoperability (LTI) core specification v1.3 and LTI Advantage services*. 1EdTech (formerly IMS Global Learning Consortium).

ADL Initiative. (2017). *Experience API (xAPI) specification, version 1.0.3*. Advanced Distributed Learning Initiative.

Alexandron, G., Ruipérez-Valiente, J. A., Chen, Z., Muñoz-Merino, P. J., & Pritchard, D. E. (2017). Copying@Scale: Using harvesting accounts for collecting correct answers in a MOOC. *Computers & Education*, 108, 96–114.

Bearman, M., Tai, J., Dawson, P., Boud, D., & Ajjawi, R. (2024). Developing evaluative judgement for a time of generative artificial intelligence. *Assessment & Evaluation in Higher Education*, 49(6), 893–905.

Bjork, E. L., & Bjork, R. A. (2011). Making things hard on yourself, but in a good way: Creating desirable difficulties to enhance learning. In M. A. Gernsbacher et al. (Eds.), *Psychology and the real world* (pp. 56–64). Worth Publishers.

Black, P., & Wiliam, D. (1998). Assessment and classroom learning. *Assessment in Education: Principles, Policy & Practice*, 5(1), 7–74.

Bretag, T., Harper, R., Burton, M., Ellis, C., Newton, P., Rozenberg, P., Saddiqui, S., & van Haeringen, K. (2019). Contract cheating: A survey of Australian university students. *Studies in Higher Education*, 44(11), 1837–1856.

Clark, D. B., Tanner-Smith, E. E., & Killingsworth, S. S. (2016). Digital games, design, and learning: A systematic review and meta-analysis. *Review of Educational Research*, 86(1), 79–122.

D'Angelo, C., Rutstein, D., Harris, C., Bernard, R., Borokhovski, E., & Haertel, G. (2014). *Simulations for STEM learning: Systematic review and meta-analysis*. SRI International.

Dawson, P. (2021). *Defending assessment security in a digital world: Preventing e-cheating and supporting academic integrity in higher education*. Routledge.

de Jong, T., & van Joolingen, W. R. (1998). Scientific discovery learning with computer simulations of conceptual domains. *Review of Educational Research*, 68(2), 179–201.

Deterding, S., Dixon, D., Khaled, R., & Nacke, L. (2011). From game design elements to gamefulness: Defining "gamification". In *Proceedings of the 15th International Academic MindTrek Conference* (pp. 9–15). ACM.

Dougiamas, M., & Taylor, P. (2003). Moodle: Using learning communities to create an open source course management system. In *Proceedings of EdMedia: World Conference on Educational Media and Technology 2003* (pp. 171–178). AACE.

Finnie-Ansley, J., Denny, P., Becker, B. A., Luxton-Reilly, A., & Prather, J. (2022). The robots are coming: Exploring the implications of OpenAI Codex on introductory programming. In *Proceedings of the 24th Australasian Computing Education Conference (ACE '22)* (pp. 10–19). ACM.

Freeman, S., Eddy, S. L., McDonough, M., Smith, M. K., Okoroafor, N., Jordt, H., & Wenderoth, M. P. (2014). Active learning increases student performance in science, engineering, and mathematics. *Proceedings of the National Academy of Sciences*, 111(23), 8410–8415.

Gamage, S. H. P. W., Ayres, J. R., & Behrend, M. B. (2022). A systematic review on trends in using Moodle for teaching and learning. *International Journal of STEM Education*, 9, 9.

Gašević, D., Dawson, S., & Siemens, G. (2015). Let's not forget: Learning analytics are about learning. *TechTrends*, 59(1), 64–71.

Gee, J. P. (2003). *What video games have to teach us about learning and literacy*. Palgrave Macmillan.

Gierl, M. J., & Lai, H. (2013). Instructional topics in educational measurement (ITEMS) module: Using automated processes to generate test items. *Educational Measurement: Issues and Practice*, 32(3), 36–50.

Hamari, J., Koivisto, J., & Sarsa, H. (2014). Does gamification work? A literature review of empirical studies on gamification. In *Proceedings of the 47th Hawaii International Conference on System Sciences* (pp. 3025–3034). IEEE.

Hattie, J., & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1), 81–112.

Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), 1–38.

Joubel. (2024). *H5P documentation: Content types, xAPI integration and authoring*. H5P.org.

Kirschner, P. A., Sweller, J., & Clark, R. E. (2006). Why minimal guidance during instruction does not work: An analysis of the failure of constructivist, discovery, problem-based, experiential, and inquiry-based teaching. *Educational Psychologist*, 41(2), 75–86.

Kung, T. H., Cheatham, M., Medenilla, A., Sillos, C., De Leon, L., Elepaño, C., Madriaga, M., Aggabao, R., Diaz-Candido, G., Maningo, J., & Tseng, V. (2023). Performance of ChatGPT on USMLE: Potential for AI-assisted medical education using large language models. *PLOS Digital Health*, 2(2), e0000198.

Kurdi, G., Leo, J., Parsia, B., Sattler, U., & Al-Emari, S. (2020). A systematic review of automatic question generation for educational purposes. *International Journal of Artificial Intelligence in Education*, 30(1), 121–204.

Lancaster, T., & Cotarlan, C. (2021). Contract cheating by STEM students through a file sharing website: A Covid-19 pandemic perspective. *International Journal for Educational Integrity*, 17, 3.

Lau, H. W., & Védrine, J.-M. (2023). *Formulas question type for Moodle: Documentation*. Moodle plugins directory.

Lee, V. R., Pope, D., Miles, S., & Zárate, R. C. (2024). Cheating in the age of generative AI: A high school survey study of cheating behaviors before and after the release of ChatGPT. *Computers and Education: Artificial Intelligence*, 7, 100253.

Leinonen, J., Denny, P., MacNeil, S., Sarsa, S., Bernstein, S., Kim, J., Tran, A., & Hellas, A. (2023). Comparing code explanations created by students and large language models. In *Proceedings of the 2023 Conference on Innovation and Technology in Computer Science Education (ITiCSE '23)* (pp. 124–130). ACM.

Liang, W., Yuksekgonul, M., Mao, Y., Wu, E., & Zou, J. (2023). GPT detectors are biased against non-native English writers. *Patterns*, 4(7), 100779.

Lodge, J. M., Howard, S., Bearman, M., & Dawson, P. (2023). *Assessment reform for the age of artificial intelligence*. Tertiary Education Quality and Standards Agency (TEQSA).

Mayer, R. E. (2009). *Multimedia learning* (2nd ed.). Cambridge University Press.

Mislevy, R. J., Steinberg, L. S., & Almond, R. G. (2003). Focus article: On the structure of educational assessments. *Measurement: Interdisciplinary Research and Perspectives*, 1(1), 3–62.

Mislevy, R. J., Oranje, A., Bauer, M. I., von Davier, A., Hao, J., Corrigan, S., Hoffman, E., DiCerbo, K., & John, M. (2014). *Psychometric considerations in game-based assessment*. GlassLab Research, Institute of Play.

Newton, P. M. (2018). How common is commercial contract cheating in higher education and is it increasing? A systematic review. *Frontiers in Education*, 3, 67.

Nikolic, S., Daniel, S., Haque, R., Belkina, M., Hassan, G. M., Grundy, S., Lyden, S., Neal, P., & Sandison, C. (2023). ChatGPT versus engineering education assessment: A multidisciplinary and multi-institutional benchmarking and analysis of this generative artificial intelligence tool to investigate assessment integrity. *European Journal of Engineering Education*, 48(4), 559–614.

Northcutt, C. G., Ho, A. D., & Chuang, I. L. (2016). Detecting and preventing "multiple-account" cheating in massive open online courses. *Computers & Education*, 100, 71–80.

Palazzo, D. J., Lee, Y.-J., Warnakulasooriya, R., & Pritchard, D. E. (2010). Patterns, correlates, and reduction of homework copying. *Physical Review Special Topics — Physics Education Research*, 6(1), 010104.

Perkins, M. (2023). Academic integrity considerations of AI large language models in the post-pandemic era: ChatGPT and beyond. *Journal of University Teaching & Learning Practice*, 20(2), 07.

Prensky, M. (2001). *Digital game-based learning*. McGraw-Hill.

Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*, 17(3), 249–255.

Rudolph, J., Tan, S., & Tan, S. (2023). ChatGPT: Bullshit spewer or the end of traditional assessments in higher education? *Journal of Applied Learning and Teaching*, 6(1), 342–363.

Rutten, N., van Joolingen, W. R., & van der Veen, J. T. (2012). The learning effects of computer simulations in science education. *Computers & Education*, 58(1), 136–153.

Ryan, R. M., & Deci, E. L. (2000). Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being. *American Psychologist*, 55(1), 68–78.

Sadler, D. R. (1989). Formative assessment and the design of instructional systems. *Instructional Science*, 18(2), 119–144.

Sailer, M., & Homner, L. (2020). The gamification of learning: A meta-analysis. *Educational Psychology Review*, 32(1), 77–112.

Sangwin, C. (2013). *Computer aided assessment of mathematics*. Oxford University Press.

Sangwin, C. J., & Köcher, N. (2016). Automation of mathematics examinations. *Computers & Education*, 94, 215–227.

Sarsa, S., Denny, P., Hellas, A., & Leinonen, J. (2022). Automatic generation of programming exercises and code explanations using large language models. In *Proceedings of the 2022 ACM Conference on International Computing Education Research (ICER '22)* (pp. 27–43). ACM.

Shute, V. J. (2008). Focus on formative feedback. *Review of Educational Research*, 78(1), 153–189.

Shute, V. J. (2011). Stealth assessment in computer-based games to support learning. In S. Tobias & J. D. Fletcher (Eds.), *Computer games and instruction* (pp. 503–524). Information Age Publishing.

Shute, V. J., & Ventura, M. (2013). *Stealth assessment: Measuring and supporting learning in video games*. MIT Press.

Shute, V. J., Wang, L., Greiff, S., Zhao, W., & Moore, G. (2016). Measuring problem solving skills via stealth assessment in an engaging video game. *Computers in Human Behavior*, 63, 106–117.

Singleton, R., & Charlton, A. (2020). Creating H5P content for active learning. *Pacific Journal of Technology Enhanced Learning*, 2(1), 13–14.

Sitzmann, T. (2011). A meta-analytic examination of the instructional effectiveness of computer-based simulation games. *Personnel Psychology*, 64(2), 489–528.

Slade, S., & Prinsloo, P. (2013). Learning analytics: Ethical issues and dilemmas. *American Behavioral Scientist*, 57(10), 1510–1529.

Susnjak, T. (2024). ChatGPT: The end of online exam integrity? *Education Sciences*, 14(6), 656.

Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*, 12(2), 257–285.

Swiecki, Z., Khosravi, H., Chen, G., Martinez-Maldonado, R., Lodge, J. M., Milligan, S., Selwyn, N., & Gašević, D. (2022). Assessment in the age of artificial intelligence. *Computers and Education: Artificial Intelligence*, 3, 100075.

Vlachopoulos, D., & Makri, A. (2017). The effect of games and simulations on higher education: A systematic literature review. *International Journal of Educational Technology in Higher Education*, 14, 22.

von Davier, M. (2018). Automated item generation with recurrent neural networks. *Psychometrika*, 83(4), 847–857.

W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. World Wide Web Consortium Recommendation.

Weber-Wulff, D., Anohina-Naumeca, A., Bjelobaba, S., Foltýnek, T., Guerrero-Dib, J., Popoola, O., Šigut, P., & Waddington, L. (2023). Testing of detection tools for AI-generated text. *International Journal for Educational Integrity*, 19, 26.

Wieman, C. E., Adams, W. K., & Perkins, K. K. (2008). PhET: Simulations that enhance learning. *Science*, 322(5902), 682–683.

Wouters, P., van Nimwegen, C., van Oostendorp, H., & van der Spek, E. D. (2013). A meta-analysis of the cognitive and motivational effects of serious games. *Journal of Educational Psychology*, 105(2), 249–265.

---

## Appendices

All appendix artefacts are machine-readable and are provided in the `artifacts/` directory of the repository accompanying this paper. They are not illustrative pseudocode: the specification validates against the schema, the question XML parses and imports, the validator runs and reports the figures quoted in §6.1, and the Pattern E game is exercised in a real browser by the test suite of Appendix E.

### Appendix A — GAIMS Activity Specification schema v1.0

`artifacts/appendix-a-activity-spec.schema.json` — JSON Schema (2020-12) for the stage-2 specification document. It encodes the framework's design constraints as validation rules rather than as advice:

- `outcomes` is capped at three items, enforcing micro-simulation scale.
- `artefact.external_dependencies` has `maxItems: 0`, making a CDN or third-party runtime dependency a schema violation.
- `artefact.scaffold_ladder` has `minItems: 3`, making an unguided sandbox unrepresentable.
- `parameterisation.seed_policy.keyed` is `const: true`, making an unkeyed seed unrepresentable.
- `parameterisation.cardinality_target` has `minimum: 10000`.
- `parameterisation.constraints` requires a stated `rationale` for every validity constraint, which is where semantic invariance is argued.
- `observables` is capped at seven and every observable requires a `retention_days` value, tying instrumentation to the data-protection obligations of Section 11.
- Every `grading.components[]` entry must name a `moodle_target`, enforcing criterion 5 of §4.1.
- `accessibility.equivalent_task_pathway` is required, making the accommodation pathway a condition of a valid specification.

`artifacts/example-rankine-activity.json` is a complete conforming instance for Vignette 1.

### Appendix B — Authoring prompt templates

`artifacts/appendix-b-authoring-prompt.md` — the stage-2 and stage-3 prompt templates, including the three-way **independent generation** protocol (artefact, reference solver, Moodle import artefacts, generated without sight of one another) that makes the stage-4 cross-check informative, and the stage-4 regeneration prompt. The templates are versioned with the activity so that a regeneration is reproducible and auditable.

### Appendix C — Importable Moodle `Formulas` question

`artifacts/appendix-c-rankine-formulas.xml` — a five-part, five-point `Formulas` question implementing the summative component of Vignette 1, ready for import into a Moodle question bank. It demonstrates: randomised variables declared in `varsrandom` with step sizes yielding effective cardinality of 1.35 × 10⁵; an answer key defined in `varsglobal` in terms of those variables so that the correct answer recomputes per instance; relative-error grading at 1% tolerance; unit-graded parts using `postunit` for kJ/kg and kg/s; per-part feedback naming the misconception it addresses; and three question-level hints ordered from orienting to specific for `interactive with multiple tries`.

`artifacts/validate_rankine.py` — the stage-4 reference solver and validator. Running it reproduces the figures reported in §6.1 and exits non-zero on any failed gate. Its header documents the reachability failure that rejected the four-part version of the question.

### Appendix D — Expert review rubric (human gate 2)

`artifacts/appendix-d-review-rubric.md` — 25 criteria across construct validity, parameterisation, pedagogical design, integrity and security, accessibility and equity, data protection, and sustainability, each classified Blocking / Major / Minor, with the decision rule that a cluster of major findings returns the activity to specification rather than to regeneration. The rubric ends with a reviewer declaration that makes the point of the framework explicit: approving a generated activity carries the same academic accountability as setting any other assessment, and that accountability is not transferred to the model.

### Appendix E — Cloze answer-field bridge: template, worked game and browser test

`artifacts/cloze-pattern/` — the complete Pattern E toolkit, and the only part of this paper that a reader can deploy without reading the rest of it.

- `template-hardened.html` — the question-text template. Provides `setScore()` and `logStep()` to the generated game, scopes all DOM queries to the enclosing `.que` so that several such questions can coexist on one page, and fixes eight failure modes enumerated in §5.5 and in the accompanying README.
- `fractions-game.html` — Vignette 4 complete and ready to paste into a Cloze question: ten fraction-shading questions on pies and bars, keyboard-operable, hatch-patterned rather than colour-only, no timer.
- `make-cloze-field.js` — generates the partial-credit `NUMERICAL` field for a game of any maximum score, which is the fix for the silent grading error of §5.5.
- `prompt-template.md` — the authoring prompt, with the constraints that prevent the recurring generation defects (submit-type buttons, mouse-only interaction, colour-only state, auto-advancing timers, non-deterministic question order).
- `test/harness.js` — builds a page imitating the DOM Moodle renders for a Cloze question, including the read-only variant used in attempt review.
- `test/play-test.js` — drives the game in Chromium and asserts the pattern's contract, as reported in §6.4. It also contains one passing check labelled a known limitation, demonstrating that a console statement can set the score field without playing.

The toolkit is the paper's response to its own sustainability argument: the claim that a teacher can deploy a generated, automatically graded interactive activity unaided is only worth making if the thing they would deploy is supplied, tested, and honest about what it does not do.

---

## Data and materials availability

All artefacts described in the appendices are available in the repository accompanying this paper. The validator is deterministic under its fixed seed and reproduces the reported statistics exactly. No human-subjects data is reported; the study specified in Section 8 has not been conducted, and would require ethics approval prior to any data collection.

## Declaration on the use of generative AI

Generative AI was used in the preparation of this work, in two distinct roles which we distinguish because the distinction is the paper's own argument. First, as the object of study: the framework specifies AI as an authoring technology, and the appendix artefacts were produced through the pipeline the paper describes, including the stage-4 defect and regeneration episode reported verbatim in §6.1. Second, in drafting and editing the manuscript. The authors are responsible for the argument, the interpretation of the cited literature, the correctness of the artefacts, and any errors.

## Conflict of interest

The authors declare no conflict of interest. No funding body had any role in the design of the framework or the preparation of this manuscript.

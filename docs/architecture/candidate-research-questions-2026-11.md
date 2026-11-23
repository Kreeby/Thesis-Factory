# Candidate research questions (2026-11-23)

Status: **PROPOSED — for the owner's decision (ideally with the supervisor). Not approved.**
Topic (approved, unchanged): *A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring.*
Input: stage 3 gap review, refutation and Codex second review (`CURRENT_STATE.md`, Update 2026-11-23;
data in `.thesis-corpus/gaps/review.json`, gitignored).

Epistemic labels follow `PROJECT.md` §5.3. Everything under "Why open" is a bounded search result,
not proof of a gap. A round-2 refutation (re-score corpus papers against the chosen question, then
targeted search) is required before adoption.

## Legal anchors (VERIFIED, primary texts saved in `.thesis-corpus/gaps/sources/`)

* CJEU C-203/22 *Dun & Bradstreet Austria*, 27 Feb 2025 (CURIA press release No 22/25): the controller
  "must describe the procedure and principles actually applied in such a way that the data subject can
  understand which of his or her personal data have been used, and how they have been used"; "it could in
  particular be appropriate to inform the data subject of the extent to which a variation in the personal
  data taken into account would have led to a different result"; "the mere communication of an algorithm
  does not constitute a sufficiently concise and intelligible explanation"; allegedly protected trade
  secrets go to the supervisory authority or court, which balances.
* CJEU C-634/21 *SCHUFA*, 7 Dec 2023: a score is an automated decision under GDPR Art. 22 when lenders
  give it a determining role.
* Regulation (EU) 2024/1689: credit scoring of natural persons is high-risk (Annex III 5(b)); Art. 86
  right to "clear and meaningful explanations of the role of the AI system ... and the main elements of
  the decision taken". Regulation (EU) 2026/1744 defers Annex III high-risk obligations to 2 Dec 2027
  (verified on EUR-Lex via the Codex review).
* Caveat (RISK-006): the C-203/22 wording above is from the press release ("not binding on the Court").
  The judgment's operative text must be read before criteria are fixed. Turning legal wording into
  metrics is an interpretation that needs explicit justification in the thesis.

## Q1 (recommended): Do common XAI methods meet the C-203/22 explanation standard in credit scoring?

**RQ.** To what extent do feature-attribution (SHAP, LIME) and counterfactual explanations of credit
models satisfy measurable proxies of the C-203/22 / Art. 86 explanation standard, compared with an
inherently interpretable baseline (scorecard / logistic regression)?

**Legal criterion → measurable test (proposal):**

| Legal wording | Test | Metric family |
|---|---|---|
| which personal data were used and how | attribution correctness | faithfulness (deletion/insertion, infidelity); ground truth on synthetic credit-like data with known structure |
| extent to which a variation would have led to a different result | counterfactual validity and actionability | validity after applying the change, proximity, sparsity, immutable/actionable features |
| concise and intelligible, not the mere algorithm | complexity | number of features shown, rule length; optional small user study |
| explanation of *this* decision, reliably | stability | agreement across retraining seeds and near-equivalent models |

**Why open (DERIVED from bounded searches):** XAI evaluation metrics, toolkits and robust-counterfactual
methods exist (crowded: gaps Q0006, Q0011, Q0013). A 2025 paper states that the AI Act "specifies
obligations without concrete technical requirements" (verified quote). A corpus keyword query found
no paper turning C-203/22 into evaluation criteria for credit (5 hits, none doing it; two predate the
judgment). Codex pointed to two related works that could not be fetched (UNKNOWN).

**Feasibility:** high; public data and existing libraries; no human subjects required (user study optional).
**Risks:** legal-to-metric mapping is contestable; synthetic ground truth is not real-world truth;
dataset choice and licensing UNKNOWN (candidates must be checked: German Credit, Taiwan default, HELOC, HMDA).

## Q2: Are the explanations a rejected applicant receives stable when the lender retrains or swaps equally accurate models?

**RQ.** How much do reason codes and counterfactual recourse for the same applicant change across
retraining runs and among near-equally accurate credit models, and what does that imply for an
explanation of "the procedure and principles actually applied" (C-203/22) and of "the main elements of
the decision" (Art. 86)?

**Why open / not:** robust counterfactuals and recourse under model change are a crowded area
(Q0013, Q0077; surveys 2021 and 2024 verified). A 2026 credit study reports that "fairness gaps vary"
across five retraining seeds (verified quote). The novel part would be the legal framing and the credit
setting, not the robustness methods. **Novelty: medium.**

## Q3: Does the explanation the court suggests leak the trade secret it protects?

**RQ.** How much of a credit model can be reconstructed from counterfactual ("what change would have
altered the result") explanations at the level C-203/22 suggests, and which explanation forms meet the
standard with less leakage?

**Why open / not:** model extraction from counterfactual explanations is established
(2020 "Model extraction from counterfactual explanations", DualCF 2022, AUTOLYCUS 2023/24; in the corpus).
The candidate contribution is linking it to the C-203/22 trade-secret balancing (gap Q0086, not crowded)
and measuring it on credit models. Whether this link already exists after Feb 2025 is UNKNOWN
(no corpus hit; not yet searched on the web). **Novelty: possibly high; risk: narrower, more security than XAI evaluation.**

## Relation between the three

Q1 is the core of the approved topic. Q2 and Q3 can be its extensions (stability and leakage as two
further criteria), which keeps scope controllable if Q1 is chosen.

## Decision needed (owner)

1. Choose Q1, Q2, Q3 or a combination (e.g. Q1 with a Q3 chapter).
2. Then: round-2 refutation for the chosen question; read the full C-203/22 judgment; dataset selection.

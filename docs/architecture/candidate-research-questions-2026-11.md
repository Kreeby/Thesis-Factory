# Candidate research questions (2026-11-23)

Status: **Direction chosen by the owner on 2026-11-23 (see "Owner decision" below). The final
research-question wording is NOT yet fixed; round-2 refutation is still pending. Supervisor: not consulted (UNKNOWN).**
Topic (approved, unchanged): *A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring.*

## Owner decision (2026-11-23)

**DECIDED by the owner** (chat, 2026-11-23; owner's words, Russian, verbatim):

* Instruction: «сделай комбинацию (то что главами г2 и г3)» — i.e. Q1 as the core, Q2 and Q3 as chapters.
* Q1 is the basis: «г1 (то что я тебе отправил и то что ты мне походу это одно и то же) должен быть звеном скажем основой вопроса» — the owner treats their own description (below) and Q1 as the same thing, and Q1 is the foundation of the research question.
* Essence: «Суть - сравнить модели оценки кредитного риска и методы объяснения их решений: насколько они точны, понятны и обоснованны.»
* Practical result: «Практический результат - прототип, который оценивает кредитный риск человека и объясняет, какие факторы повлияли на оценку и что можно улучшить.»

**How the orchestrator maps it (PROPOSED by the orchestrator in chat; the owner asked to record it — «запиши все это» — not final wording):**

| Owner's term | Operational meaning in this thesis | Measured by |
|---|---|---|
| models accurate (точны) | predictive quality of credit-risk models | AUC, calibration (e.g. ECE/Brier), several datasets, statistical tests |
| explanations accurate | explanations faithful to the model and stable | faithfulness metrics; synthetic data with known structure; stability across retraining (Q2) |
| understandable (понятны) | **only proxies** (number of factors, rule length) unless a user study is run | complexity metrics; user study OPEN (see below) |
| justified (обоснованны) | **defined as**: meets measurable proxies of C-203/22 / AI Act Art. 86 + counterfactual validity | the criterion→test table under Q1 |
| prototype: factors that influenced the score | feature attributions / reason codes | — (demonstrator, not an experiment) |
| prototype: what can be improved | actionable counterfactuals respecting immutable features | counterfactual validity, proximity, actionability |

Structure: Q1 = core experiment; Q2 (stability) and Q3 (leakage vs trade secrets) = chapters / additional
criteria; the prototype is built from the best model + explanation configuration found by the experiment.

**Constraints the orchestrator stated and the owner did not dispute (record, not decisions):**

* "What can be improved" is a change that would alter **the model's** decision, not advice that lowers
  real-world risk. VERIFIED quote (Karimi et al. 2020, S2 abstract): "it is impossible to guarantee recourse
  without access to the true structural equations". The prototype must word it that way.
* Comparing models + SHAP alone is a crowded area (corpus pass 2026-11-23 surfaced many 2025–26 credit
  papers, often German Credit only; exact number not counted). Novelty must come from the legal evaluation
  criteria, rigour (several datasets, tests) and Q2/Q3 — not from the prototype.
* The prototype uses public datasets only, no real applicants' data.

**OPEN (not decided; do not treat as settled in later sessions):**

1. Final wording of the research question(s) and hypotheses.
2. User study for "understandable": yes/no (needs time and probably ethics approval; university policy UNKNOWN).
3. Datasets and their licences (candidates only: German Credit, Taiwan default, HELOC, HMDA — none checked).
4. Which models and explanation methods exactly (candidates only: logistic regression/scorecard, tree ensembles; SHAP, LIME, counterfactual generators).
5. Whether the AI Act research exemption covers the prototype — NOT checked.
6. Full C-203/22 judgment text — NOT read (only the CURIA press release).
7. Round-2 refutation for the combined question — NOT done; Q3's legal link not searched on the web.
8. Supervisor's view — UNKNOWN.
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

## Next steps (after the owner decision of 2026-11-23)

1. Round-2 refutation for the combined question (Q1 core + Q2 + Q3), including a web search for the Q3 legal link.
2. Read the full C-203/22 judgment; fix the criterion→test table only after that.
3. Draft the research question(s) and hypotheses for the owner's approval.
4. Dataset selection with licence check (owner approval).

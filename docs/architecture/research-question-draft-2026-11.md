# Research question and hypotheses — DRAFT (2026-11-23)

Status: **PROPOSED by the orchestrator for the owner's approval. Not approved. Supervisor not consulted (UNKNOWN).**
Basis: owner decision and round-2 refutation in `candidate-research-questions-2026-11.md` (read that first).
Every literature claim below cites a quote verified on 2026-11-23 against a saved source
(`.thesis-corpus/gaps/sources/`, corpus abstracts, or `codex_review_*.checked.json`). Labels: VERIFIED /
DERIVED / ASSUMPTION / UNKNOWN (`PROJECT.md` §5.3). No numeric threshold in this file is a finding;
all thresholds are to be fixed before any experiment is run.

## Positioning (one sentence)

An executed, EU-law-grounded version of the finance-specific XAI benchmark that Xie, Liu & Ning (IJFS 2026,
Table 8) propose but do not run, extended with the explanation standard of CJEU C-203/22 and AI Act Art. 86
(neither is used as a benchmark criterion there; Art. 86 is not mentioned), a chapter on recourse stability
after retraining (Q2) and a chapter on model leakage through explanations (Q3), plus a prototype.

## Main research question (draft)

How do credit-risk models and explanation methods compare in **predictive accuracy**, **explanation
faithfulness and stability**, **intelligibility**, and **fulfilment of the EU explanation standard for
automated credit decisions** (CJEU C-203/22; AI Act Art. 86) when evaluated in an executed finance-specific
XAI benchmark?

Mapping to the owner's words («точны, понятны и обоснованны»): accurate → RQ1 + RQ2; understandable → the
complexity part of RQ3 (proxies only unless a user study is approved); justified → RQ3.

## Sub-questions

**RQ1 — models (accuracy).** How do the models of the IJFS Table 8 ladder (regularised logistic regression,
sparse risk score, EBM, unconstrained gradient boosting, monotonic gradient boosting) compare in
discrimination and calibration across the chosen datasets? Is the best inherently interpretable model
non-inferior to unconstrained gradient boosting?

**RQ2 — explanations (faithfulness, stability).** How faithful are feature-attribution (SHAP, LIME) and
counterfactual explanations to each model — on semi-synthetic credit data with a known decision mechanism
and on real data — and how stable are they under resampling and immaterial input changes?

**RQ3 — legal standard (justified, understandable).** To what extent do the explanation outputs meet
measurable proxies of the C-203/22 / Art. 86 standard?

| Legal source | Status | Proxy test (to be fixed before running) |
|---|---|---|
| C-203/22 ruling 1, para 61: which data were used, in what way | requirement | reason-code / attribution accuracy against the known mechanism (semi-synthetic data) |
| ruling 1, paras 58–59: concise, intelligible; not the formula or all steps | requirement | complexity bound (number of factors shown, rule length) |
| ruling 1: procedure and principles **actually applied** | requirement | stability of the explanation for the same applicant under immaterial changes |
| para 62: extent to which a variation would change the result | **example only** | counterfactual validity, proximity, actionability (immutable features respected) |
| AI Act Art. 86: role of the AI system and main elements of the decision | right (applies to Annex III systems; obligations deferred to 2 Dec 2027 by Reg. 2026/1744) | presence of the main decision factors in the output — operationalisation OPEN |

**RQ4 — chapter Q2 (recourse stability).** What share of counterfactual recourse that is valid for the
current model remains valid after scheduled retraining or for a near-equally accurate alternative model,
and does it differ by counterfactual generator? (IJFS lists "recourse validity after scheduled retraining"
as a benchmark criterion, not executed.)

**RQ5 — chapter Q3 (leakage vs trade secrets).** How accurately can a credit model be reconstructed from
counterfactual explanations disclosed one per applicant, as the number of applicants grows, and which
explanation forms meet the RQ3 proxies with less leakage? Relevance: C-203/22 ruling 2 (trade-secret
balancing); the SAFE White Paper's intermediary would "generate explanations without disclosing the raw
model or source code" without discussing extraction.

## Hypotheses (draft)

| ID | Hypothesis | Type | Basis |
|---|---|---|---|
| H1 | On each dataset, the AUC of the best inherently interpretable model is within a non-inferiority margin Δ of unconstrained gradient boosting (Δ fixed before running). | confirmatory, weak prior | Mixed VERIFIED evidence: on German Credit (n=1000) "Logistic Regression achieves the highest AUC (0.804)"; on HMDA the boosted models' "paired AUC difference was 0.000179". Direction is dataset-dependent → non-inferiority, not superiority. |
| H2 | SHAP feature-importance rankings are more stable than LIME rankings under resampling. | confirmatory (replication in our setting) | VERIFIED: a 2026 credit study reports "SHAP is the most stable in terms of global ranking" and that for LIME "the fluctuation is obvious" (deep-network setting); EJOR 2025 measured SHAP/LIME stability on four credit datasets. |
| H3 | — no directional hypothesis: which attribution method best recovers the known mechanism on semi-synthetic credit data. | exploratory | No verified result in the collected material. |
| H4 | Post-hoc explanations of unconstrained gradient boosting pass the "which data, in what way" proxy less often than the native explanations of inherently interpretable models. | confirmatory, partly by construction | DERIVED: native explanations of interpretable models are the model, so they pass by construction; the informative quantity is the size of the gap for post-hoc methods. |
| H5 | A measurable share of counterfactuals valid before retraining becomes invalid after scheduled retraining; the share differs between generators. | confirmatory | VERIFIED: robust-CE survey — "recent work has exposed severe issues related to the robustness of state-of-the-art methods for obtaining CEs"; IJFS — "a generated counterfactual reaching the target class establishes only model-internal case validity". |
| H6 | Surrogate fidelity rises with the number of disclosed counterfactual explanations and reaches a pre-defined "high fidelity" level at a number of applicants plausible for one lender or intermediary. | confirmatory in a new setting | VERIFIED (Aïvodji et al. 2020 abstract): counterfactual-based attacks "can achieve high-fidelity and high-accuracy extraction even under low query budgets". New part: credit models, one-explanation-per-applicant disclosure, C-203/22 framing. |
| — | "Understandable": no hypothesis unless a user study is approved; complexity proxies are reported descriptively. | — | OPEN decision. |

## Prototype (deliverable, not a hypothesis test)

Built from the best model + explanation configuration found in RQ1–RQ3. Acceptance criteria (proposed):
scores one applicant from a public dataset; shows the main factors (attributions or reason codes);
shows counterfactual changes worded as **changes that would alter the model's decision**, not advice
(VERIFIED basis: "it is impossible to guarantee recourse without access to the true structural equations",
Karimi et al. 2020); respects immutable features; fully reproducible from the repository; no real
applicants' data. Not novel by itself (SciTePress 2026 built XGBoost + SHAP + DiCE on HELOC).

## Data (candidates only — none selected, no licence checked)

South German Credit (corrected; IJFS recommends it over Statlog German Credit, which "used an incorrect
code table"), Taiwan/UCI default, Lending Club, Home Credit (licence permitting), HELOC, HMDA, plus
semi-synthetic data with a known mechanism (required for RQ2/RQ3 faithfulness and H4).

## Scope risk (DERIVED; decision for the owner)

Five sub-questions are a lot for an MSc thesis due end of May 2027 (deadline from `CURRENT_STATE.md`).
Proposed priority if time runs short: RQ1–RQ3 core → RQ4 → RQ5. Cutting RQ5 removes the most novel part;
cutting RQ4 removes the part IJFS already flags as a priority.

## Threats to validity (known now)

* Legal-to-metric mapping is an interpretation (RISK-006); must be argued, ideally reviewed by someone with legal expertise.
* Semi-synthetic ground truth is not real-world truth.
* Public datasets are not representative of a specific lender (RISK-007).
* IJFS authors or others may publish an execution of Table 8 before the thesis is finished.

## Decisions needed from the owner

1. Approve, change or reject the main RQ and RQ1–RQ5.
2. Priority order / scope cut (above).
3. User study yes/no.
4. Then: dataset selection with licence check; non-inferiority margin Δ and other thresholds fixed before running.

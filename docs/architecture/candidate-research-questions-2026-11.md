# Research direction and candidate research questions (2026-11-23)

Status: **Direction chosen by the owner on 2026-11-23 (see "Owner decision"). Final research-question
wording and hypotheses are NOT fixed. Round-2 refutation done (bounded; see its section). Supervisor:
not consulted (UNKNOWN).**
Topic (approved, unchanged): *A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring.*
Inputs: stage 3 gap review, refutation and Codex second review (`CURRENT_STATE.md`, Update 2026-11-23;
data in `.thesis-corpus/gaps/review.json`, gitignored). Saved primary texts: `.thesis-corpus/gaps/sources/`.
Epistemic labels follow `PROJECT.md` §5.3. "Not found" always means "not found in the stated bounded
search", never "does not exist".

## Owner decision (2026-11-23)

**DECIDED by the owner** (chat, 2026-11-23; owner's words, Russian, verbatim):

* Instruction: «сделай комбинацию (то что главами г2 и г3)» — Q1 as the core, Q2 and Q3 as chapters.
* «г1 (то что я тебе отправил и то что ты мне походу это одно и то же) должен быть звеном скажем основой вопроса» — Q1 is the foundation of the research question.
* Essence: «Суть - сравнить модели оценки кредитного риска и методы объяснения их решений: насколько они точны, понятны и обоснованны.»
* Practical result: «Практический результат - прототип, который оценивает кредитный риск человека и объясняет, какие факторы повлияли на оценку и что можно улучшить.»
* Asked the orchestrator to record everything precisely and to work from facts and the collected material.

### Owner's description vs the orchestrator's Q1 — NOT identical (orchestrator's correction, 2026-11-23)

The owner said the two "seem to be the same". The orchestrator had first agreed too readily; the accurate
comparison is:

| Aspect | Owner's description | Orchestrator's Q1 as first proposed |
|---|---|---|
| Comparing credit-risk **models** on accuracy | central | secondary (an interpretable model only as a baseline) |
| Comparing **explanation methods** | yes | yes (shared) |
| "justified" (обоснованны) | stated, not defined | defined by the orchestrator via the C-203/22 / Art. 86 standard — an interpretation |
| "understandable" (понятны) | a stated goal | only complexity proxies |
| Prototype | the practical result | absent (owner's addition) |
| Legal criteria | not mentioned | the core |
| Q2, Q3 | absent | orchestrator's proposals; now chapters by owner instruction |

**Working frame (PROPOSED by the orchestrator, recorded at the owner's request, not final wording):**
the owner's description is the frame (models × explanation methods × {accurate, understandable,
justified} + prototype); "justified" is operationalised with the legal criteria below. Reason (DERIVED
from the round-2 results): the frame without the legal criteria is a crowded area; the legal criteria
are the part not found in prior work.

| Owner's term | Operational meaning | Measured by |
|---|---|---|
| models accurate (точны) | predictive quality of credit-risk models | AUC, calibration (e.g. ECE/Brier), several datasets, statistical tests |
| explanations accurate | faithful to the model, stable | faithfulness metrics; synthetic data with known structure; stability (Q2 chapter) |
| understandable (понятны) | **proxies only** (number of factors, rule length) unless a user study is run | complexity metrics; user study OPEN |
| justified (обоснованны) | meets measurable proxies of the C-203/22 / Art. 86 standard (table below) + counterfactual validity | criterion→test table |
| prototype: factors that influenced the score | attributions / reason codes | demonstrator, not an experiment |
| prototype: what can be improved | actionable counterfactuals respecting immutable features | validity, proximity, actionability |

**Constraints stated by the orchestrator, not disputed by the owner (record, not decisions):**

* "What can be improved" = a change that would alter **the model's** decision, not advice that lowers
  real-world risk. VERIFIED (Karimi et al. 2020, S2 abstract): "it is impossible to guarantee recourse
  without access to the true structural equations". The prototype must word it that way.
* The prototype is not a contribution by itself: an XGBoost + SHAP + DiCE counterfactual framework on
  HELOC already exists (SciTePress 2026, see round 2).
* Public datasets only; no real applicants' data. **Corrected 2026-11-23:** the licensed public datasets
  contain de-identified records of real people; the precise rule is "licensed, public, de-identified data
  only; the prototype shows generated profiles screened against source rows" (`datasets-2026-11.md`).

## Legal anchors (VERIFIED; full judgment texts read 2026-11-23)

* **CJEU C-203/22 *Dun & Bradstreet Austria*, judgment of 27 Feb 2025** (CURIA full text, saved as
  `curia-judgment-C-203-22.txt`).
  * **Ruling, point 1 (binding interpretation):** the data subject may require the controller to explain,
    "by means of relevant information and in a concise, transparent, intelligible and easily accessible
    form, the procedure and principles actually applied" in using their personal data by automated means
    to obtain a specific result, "such as a credit profile".
  * **Para 61 (reasoning):** the information "must describe the procedure and principles actually applied
    in such a way that the data subject can understand which of his or her personal data have been used
    in what way in the automated decision-making at issue"; complexity does not relieve the controller of
    the duty.
  * **Para 59:** the requirements "cannot be satisfied either by the mere communication of a complex
    mathematical formula, such as an algorithm, or by the detailed description of all the steps in
    automated decision-making".
  * **Para 62 — an EXAMPLE, not a requirement:** "the referring court could, inter alia, find that it is
    sufficiently transparent and intelligible to inform the data subject of the extent to which a variation
    in the personal data taken into account would have led to a different result". Commentators read this
    differently (per a web-search summary, not verified, one law-firm note calls a counterfactual
    sufficient for scoring); that is interpretation.
  * **Ruling, point 2:** allegedly protected information (third-party data, trade secrets) goes to the
    supervisory authority or court, which balances the interests and decides the extent of access.
* **CJEU C-634/21 *SCHUFA*, 7 Dec 2023:** a score is an Art. 22 GDPR automated decision when lenders give
  it a determining role (CURIA press release and full text saved).
* **Regulation (EU) 2024/1689:** credit scoring of natural persons is high-risk (Annex III 5(b)); Art. 86
  right to "clear and meaningful explanations of the role of the AI system ... and the main elements of
  the decision taken". Regulation (EU) 2026/1744 defers Annex III high-risk obligations to 2 Dec 2027
  (EUR-Lex, verified via the Codex review).
* Caveat (RISK-006): turning legal wording into metrics is an interpretation and must be argued in the thesis.

## Q1 (foundation): models and explanation methods — accurate, understandable, justified

**Draft RQ (PROPOSED, not final):** How do credit-risk models and explanation methods (feature attribution,
counterfactuals) compare in predictive accuracy, explanation faithfulness and stability, intelligibility
proxies, and fulfilment of measurable proxies of the C-203/22 / Art. 86 explanation standard, against an
inherently interpretable baseline?

**Legal criterion → measurable test (PROPOSED; revised after reading the full judgment):**

| Source | Status in law | Test | Metric family |
|---|---|---|---|
| Ruling 1 / para 61: which data were used and in what way | requirement | attribution correctness | faithfulness (deletion/insertion, infidelity); synthetic data with known structure |
| Ruling 1 / paras 58–59: concise, intelligible; not the formula or all steps | requirement | complexity | number of factors shown, rule length; user study optional |
| Ruling 1: procedure and principles **actually applied** | requirement | explanation reflects the deployed model reliably | stability across retraining / near-equivalent models (Q2) |
| Para 62: extent to which a variation would change the result | **example only** | counterfactual validity and actionability | validity, proximity, sparsity, immutable features |

## Q2 (chapter): stability of the explanations a rejected applicant receives

**Round-2 finding (VERIFIED quotes):** stability of SHAP/LIME **attributions** in credit scoring is
already studied — EJOR 2025 evaluates "the stability of ... (LIME) and ... (SHAP) when applied to IDCS
models. Using four publicly available credit scoring datasets"; a 2026 conference paper "compares SHAP,
LIME and attention-based interpretation methods" on stability and consistency. **Consequence (DERIVED):**
attribution stability alone is not new. What remains: stability of **counterfactual recourse** across
retraining / near-equivalent credit models, read against "procedure and principles actually applied".
General robust-counterfactual methods exist (Q0013, Q0077), so the contribution is the credit + legal
reading. Q2 is best a criterion/chapter inside Q1, not a standalone claim.

## Q3 (chapter): does the court's example explanation leak the trade secret it protects?

**Draft RQ:** How much of a credit model can be reconstructed from counterfactual explanations of the kind
para 62 mentions, and which explanation forms meet the standard with less leakage — relevant to the
balancing in ruling point 2.

**Round-2 finding:** model extraction from counterfactual explanations is established (2020 "Model
extraction from counterfactual explanations", DualCF 2022, AUTOLYCUS 2023/24; in the corpus). Wachter,
Mittelstadt and Russell (2017) argued counterfactuals are less likely to infringe trade secrets (reported
by a web search summary; not quote-verified). No work linking extraction risk to the C-203/22 balancing
was found (corpus query + 2 web searches, 2026-11-23). Status: not found in bounded search.

## Round-2 refutation for the combined question (2026-11-23)

Searches: 3 corpus keyword queries (credit + ≥2 XAI methods + explanation-quality metric: 82 hits;
credit + XAI evaluation + legal terms: 40; evidence map: 2), abstracts of the closest papers read,
2 web searches (C-203/22 + XAI evaluation; counterfactual extraction + trade secrets + C-203/22),
competitor abstracts fetched and quotes matched. Closest prior work (all quotes VERIFIED):

* **IJFS 2026, "Explainable Artificial Intelligence in Credit Risk: A Systematic Evidence Map for Regulated
  Credit Decisions"** — of the core map, "1.3–1.5% contained strict or broad explanation-quality evaluation
  signals"; "Its contribution is a reproducible reporting map and task-specific validation agenda, not a
  comparative ranking of explanation methods." Its TAMV framework links explanations to adverse-action
  reasons and recourse. **Full text read 2026-11-23** (PDF supplied by the owner; Xie, Liu, Ning; published
  24 Oct 2026; text saved as `ijfs-14-00292-2026.txt`, PDF SHA-256 prefix 33903a7929d20b88). VERIFIED quotes:
  * §7.4: "The field still lacks the standardised benchmarks expected of a maturing measurement discipline";
    "Tabular financial data remain under-represented".
  * §9.2 research priorities: "Research should first translate Articles 9–15 of the EU AI Act into concrete
    explanation artefacts and validation tests supported by reconstructible logs"; "A shared
    finance-specific explanation benchmark is equally important"; "Further work should optimise fairness
    together with explainability and test recourse after model refits against real applicant outcomes."
  * **Table 8, "Minimum specification for a finance-specific XAI benchmark" — a proposal, not executed.**
    Datasets: "Version-pinned Taiwan/UCI card-default and Lending Club data, with Home Credit added where
    licences permit", plus semi-synthetic data with a known decision mechanism. Models: "Regularised
    logistic regression; optimised sparse risk score; EBM; unconstrained gradient-boosted ensemble; its
    monotonic counterpart." Regulatory-task criteria: "Reason-code accuracy against the known mechanism;
    stability under immaterial changes; recourse validity after scheduled retraining; disparity in recourse
    cost across protected groups."
  * Datasets: "German credit is retained only as a legacy comparison because the widely circulated Statlog
    version used an incorrect code table"; "Interpretability research should prefer the corrected South
    German Credit data" (Grömping 2019).
  * Law: C-203/22 appears in the regulatory background (§2.3) and a table; **AI Act Art. 86 is not
    mentioned (0 occurrences)**. Regulatory criteria are framed around AI Act Arts 9–15 and US adverse action.
  * **Consequence (DERIVED):** the IJFS paper proposes, but does not run, a benchmark that overlaps strongly
    with Q1's design (model ladder, faithfulness + stability, semi-synthetic known mechanism) and names
    recourse validity after retraining (our narrowed Q2). Q1's design is therefore not novel as a design;
    the contribution would be (a) executing such a benchmark, (b) adding EU individual-rights criteria
    (C-203/22 "which data, in what way", Art. 86), (c) Q3. Risk: the authors or others may publish an
    execution soon; the thesis should cite Table 8 and position itself as an EU-law-grounded execution of it.
* **FinRegLab 2023** (US policy report, found by Codex, quote verified): "We can systematically evaluate the
  performance of explainability techniques and model diagnostic tools without having “ground truth”
  explanations" — empirical evaluation of explainability for credit underwriting under US rules.
* **EJOR 2025; ICDEIS 2026** — attribution stability in credit (see Q2).
* **SciTePress 2026, "Actionable Explainable AI for Credit Risk"** — XGBoost + SHAP + DiCE on HELOC, to
  "generate counterfactual explanations with DiCE to indicate feasible changes capable of reversing
  unfavorable outcomes" (matched ignoring the page's broken spacing). Equivalent to the prototype idea.
* **arXiv 2608.07452 (Aug 2026), "Against Explainable AI in Law: Why Justifiable AI Matters. A Credit
  Scoring Example"** — conceptual/legal; argues the right to explanation "encompasses not only a technical
  explanations but also a legal justification". No experiment. Relevant to defining "justified".
* **Bauer, Gill, Langenbucher, Franke, "Explaining Explainability: On Credit Scoring, AI, and Consumer
  Agency", SAFE White Paper No. 116, December 2025** (inner title "Institutionalizing Explainability: ...";
  policy paper, not peer-reviewed; PDF supplied by the owner, read in full 2026-11-23; text saved as
  `safe-white-paper-116-2025.txt`, PDF SHA-256 prefix 64c49de0eed27227). Quotes VERIFIED:
  * **Not empirical:** legal analysis of SCHUFA and Dun & Bradstreet, an overview of SHAP and DiCE with
    toy examples, and a policy proposal ("suggesting to treat explanations as a public good and designing
    an intermediary institution"). The terms "experiment" and "benchmark" do not occur. The earlier
    web-search summary ("compares SHAP and counterfactuals") was inaccurate: it describes them, it does
    not compare them empirically. → Not a competitor for Q1; it supports it: "it is pivotal to gauge the
    feasibility of such a form of explanation both from a purely technical ..." perspective.
  * Its reading of the court is interpretation: "from its ruling it seems that it is this kind of local,
    counterfactual explanation that the European Court of Justice in Dun & Bradstreet had in mind" (the
    judgment's para 62 frames it as an example).
  * **Q3 positioning:** the proposed intermediary "would generate explanations without disclosing the raw
    model or source code to the requester, thus protecting trade secrets while ensuring transparency".
    The paper does not discuss model extraction from explanations (0 occurrences of extract/leak/steal).
    Q3 would test exactly this assumption.

**Result (DERIVED, bounded):** each component exists separately (model comparison + SHAP: crowded;
attribution stability in credit: done; actionable counterfactual prototype: done; legal-justification
argument: conceptual only). An empirical comparison of credit models and explanation methods against the
C-203/22 / Art. 86 standard was not found. Q1 as the foundation survives round 2; Q2 narrowed to recourse
stability; Q3 survives (not found).

## OPEN (not decided; do not treat as settled)

1. Final wording of the research question(s) and hypotheses.
2. User study for "understandable": yes/no (time; probably ethics approval; university policy UNKNOWN).
3. Datasets and licences. Candidates only, none checked: South German Credit (corrected version; Statlog German Credit only as a legacy baseline, per IJFS 2026), Taiwan/UCI default, Lending Club, Home Credit (licence permitting), HELOC, HMDA, plus semi-synthetic data with a known mechanism.
4. Exact models and explanation methods (candidates only).
5. Whether the AI Act research exemption covers the prototype — NOT checked.
6. Supervisor's view — UNKNOWN.

## Next steps

1. Draft RQ and hypotheses for the owner's approval, positioned as an EU-law-grounded execution of the
   IJFS 2026 Table 8 benchmark plus Q2 (recourse stability) and Q3 (leakage) chapters.
2. Dataset selection with licence check (owner approval).

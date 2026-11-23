# Datasets — recommendation (2026-11-23, revised after Codex review)

Status: **PROPOSED by the orchestrator for the owner's approval. Not approved.**
Basis: approved RQ1–RQ5 (`research-question-draft-2026-11.md`). Licence facts: checked on official pages by
the orchestrator and independently by Codex (`.thesis-corpus/datasets/codex_datasets.json`); every licence
quote below was re-fetched and matched by the orchestrator. Second review of this recommendation by Codex:
`.thesis-corpus/datasets/codex_dataset_review.json` (13 issues; its quotes checked by fetching: 27 verified,
3 not matched due to formatting, 6 unreadable — `codex_dataset_review.checked.json`). Raw UCI files:
`.thesis-corpus/datasets/raw/` (gitignored; zip SHA-256 prefixes: Taiwan 56c885f84457f668, South German 0b40d40eb7321693).

## What the research questions require (DERIVED)

| Need | Why |
|---|---|
| real credit data with a default/repayment label | RQ1–RQ3 are about credit **risk** |
| licence allowing academic use and publishing results | thesis + public code |
| licence allowing redistribution | public prototype; reproducible examples |
| time index | RQ4: recourse validity after *scheduled* retraining |
| protected attributes | IJFS criterion "disparity in recourse cost across protected groups" (optional) |
| data with a known decision mechanism | RQ2/RQ3 faithfulness, H4 — semi-synthetic only |
| a dataset for RQ5 | extraction experiments (was missing in the first version — Codex) |

## Facts per candidate (VERIFIED unless marked)

| Dataset | Licence / terms | Label | Time index | Protected attributes | Notes |
|---|---|---|---|---|---|
| Taiwan default (UCI 350) | CC BY 4.0 | default payment next month (22.1% positive: 6,636 / 30,000, counted) | none — one snapshot; payment history Apr–Sep 2005 | sex, age, marital status | **existing cardholders**, behavioural scoring, not applicants (Codex, accepted) |
| South German Credit (UCI 522) | CC BY 4.0 | contract complied with (good) or not (bad); 300 bad / 700 good (counted) | none | age, foreign worker; UCI: "sex cannot be recovered from the variable" | UCI: "Stratified sample from actual credits with bad credits heavily oversampled"; amount transformed ("actual data and type of transformation unknown") |
| Statlog German Credit (UCI 144) | CC BY 4.0 | good/bad | none | as above, coding errors | **same underlying cases as South German** — not an independent replication |
| Freddie Mac SFLLD | academic/research use; results public only if noncommercial and they "cannot be used to derive or recreate any part of the" dataset; no redistribution; registration | to be constructed from monthly performance | origination quarter; monthly performance | none in public data (Codex) | user guide: "50,000 loans selected from each full vintage year" (sample files → feasible on 16 GB); acquired 30-year-type fixed-rate mortgages, not a through-the-door population |
| HMDA | public domain (CFPB) | lender action (multi-category), not default | activity year | race, ethnicity, sex, age bands | denial reasons are downstream of the action (leakage) |
| LendingClub | UNKNOWN (official page redirects to Happen Bank) | status field mixes ongoing and terminal states (Codex, source unreadable here) | issue month | — | grade/rate are LendingClub's own risk outputs (Codex) |
| Home Credit, Give Me Some Credit, FICO HELOC | UNKNOWN (rules/terms unreadable) | different labels and horizons | none | Home Credit: gender, age | HELOC label "90 days past due or worse at least once over a period of 24 months" (AIX360 docs) |
| SAS HMEQ (Codex suggestion) | UNKNOWN — Codex cites the Apache-style licence of a SAS GitHub repo; the quote did not match the rendered page; provenance of the data itself not checked | default on home-equity loan | none | — | candidate only |
| SBA 7(a) FOIA (Codex suggestion) | "U.S. Government Works" per Codex (page unreadable here) | charge-off | approval date | — | **business** loans — outside "consumer credit"; not recommended |

## Data-quality facts that change the design (VERIFIED on the data and UCI documentation)

* **Taiwan undocumented codes.** UCI documents repayment status as "-1 = pay duly; 1 = payment delay for one
  month; ... 9 = payment delay for nine months and above", education 1–4, marital status 1–3. The data contain
  repayment codes **-2 and 0** in all six months (e.g. September: -2 = 2,759 rows, 0 = 14,737), education
  **0, 5, 6** (14 / 280 / 51 rows) and marital status **0** (54 rows). Treating them as ordinary numbers would
  give SHAP values, counterfactuals and monotonic constraints an invented meaning. Rule: keep them as explicit
  categories; no monotonic constraint on them; never propose them as counterfactual targets.
* **Taiwan is behavioural scoring of existing accounts.** Bills and payments for Apr–Sep 2005 are history at
  the scoring date. Rule: counterfactuals may not change past months (immutable); the prototype is framed as
  "existing-account risk", not loan-application approval. The six months are not six retraining cohorts.
* **South German: oversampled bad credits.** The 30% bad rate is not a portfolio default rate; calibration is
  conditional on the sample. n = 1,000 → H1 non-inferiority may end inconclusive (allowed outcome). No
  sex-specific analysis; no currency-denominated recourse (amount transformed).

## Recommendation (PROPOSED)

1. **Taiwan default — main real dataset** for RQ1–RQ3, **RQ5**, the fairness analysis and the public
   prototype (licence allows redistribution), with the data-quality rules above.
2. **South German Credit — second real dataset** (comparability with the German-credit literature; corrected
   version; counted once; Statlog only for a named legacy replication).
3. **Freddie Mac SFLLD — time-indexed dataset for RQ4**, using the annual 50,000-loan sample files. Before any
   modelling, a written protocol must fix (Codex issues accepted): the endpoint (candidate: first observed 90+
   days delinquency within a common horizon; REO/foreclosure/charge-off handling; prepayment as a competing
   event); censoring and delayed entry; that each simulated fit date uses only cohorts whose outcome window has
   elapsed (and, where available, releases published by then; otherwise label it a retrospective simulation);
   predictor availability at origination (no servicing/performance fields); linked mortgage inputs constrained
   in counterfactuals. Publication: aggregate, disclosure-reviewed metrics only; no models, row-level
   explanations or data. Not in the prototype. Requires **the owner to register**.
4. **Semi-synthetic credit data — built by us**, preserving joint feature dependencies (not marginals only),
   with interactions and correlated proxies, and **three separate tests**: a known scoring rule, recovery of
   the label-generating mechanism, and fidelity to each fitted model (a fitted model can use different logic
   than the generator; a stable explanation can be consistently wrong). Dated synthetic cohorts with declared
   drift serve as the controlled RQ4 setting; also used for RQ5 (known target model).
5. **Not used:** HMDA (not a risk label), LendingClub, Home Credit, Give Me Some Credit, HELOC, HMEQ while
   their terms are UNKNOWN; SBA 7(a) (business credit).

**Correction to an earlier constraint:** the owner-decision record said "no real applicants' data". Taiwan and
South German contain records of real (de-identified) people under CC BY 4.0, and CC BY notes that "other rights
such as publicity, privacy, or moral rights may limit how you use the material" (VERIFIED via Codex review).
Precise rule instead: only licensed, public, de-identified datasets; the prototype shows **generated
demonstration profiles** screened to not exactly match any source row; no attempt to identify anyone.

Fallback for RQ4 if Freddie Mac is infeasible: dated semi-synthetic cohorts with declared drift plus
bootstrap retraining on Taiwan — weaker, because it is not real calendar time.

## Decisions needed from the owner

1. Approve / change the dataset set.
2. Register for the Freddie Mac dataset (account in the owner's name), or choose the fallback.
3. Optional: read the Kaggle rules for Home Credit while logged in, if it should be reconsidered.

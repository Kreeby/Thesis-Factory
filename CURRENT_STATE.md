# Current Project State

Last updated: 2026-11-23

## Update (2026-11-23) — start here

* **Deep reading complete on all 386 `fetched` texts** (qwen3:8b, Windows RTX 3060). 42,147 proposed claims → **32,711 verified as exact quotes (78%)**, 9,436 rejected, 1 failed chunk of ~3,000. ~17 h of model time, mean 161 s/paper. Verified claims by kind: FINDING 8,360 · XAI_METHOD 4,638 · MODEL 4,569 · LEGAL_CLAIM 3,480 · LIMITATION 2,935 · **OPEN_QUESTION 2,616** · DATASET 2,553 · EVALUATION_METRIC 1,957 · RESEARCH_QUESTION 1,603. VERIFIED by local count over `.thesis-corpus/cards/`. Only the quote is verified; statement and kind are model interpretation.
* **Root cause of the 2026-11-22 PC freeze (VERIFIED):** llama-server's host-RAM prompt cache (`--cache-ram`, llama.cpp default 8192 MiB) grew ~330 MB per model call; Ollama's own log showed `cache state: 9 prompts, 3098 MiB (limits: 8192 MiB)`, and Ollama does not count it in `ollama ps`. Fix per ollama/ollama#17351: `LLAMA_ARG_CACHE_RAM=0` in the server environment. **On Windows the tray app does not pass it through** (limit stayed 8192 after restart); `ollama serve` started directly with the variable logs "prompt cache is disabled". With it, llama-server stayed at ~1 GB over a full paper (was +330 MB/call). Also from the log: Ollama disables mmap for llama-server on Windows CUDA, so ~5.5 GB is committed at load (not resident).
* **Windows run procedure for local-model jobs:** stop the Ollama tray app, start `ollama serve` with `LLAMA_ARG_CACHE_RAM=0`; run a guard that stops the job and unloads the model if available RAM < 2.5 GB, the GPU is ≥ 85 °C for 30 s (driver: target 83 °C, max operating 93 °C, slowdown 95 °C) or thermal slowdown is active. The guard is a local script, not in the repository. Under load: GPU 97%, 65 °C, 167/170 W.
* Fetcher restarted after the reboot (it died with it); outside `./scripts/uv`, `.env` must be loaded into the environment by hand (`OPENALEX_API_KEY`). Index: 386 fetched, 164 `no_grobid`, 29 `no_doi`; ~64 reading-list-v2 papers still unchecked, waiting for the daily allowance.
* Owner view (2026-11-23): ~400 papers is enough for one MSc thesis; no new full-text sources (CORE, S2ORC) for now. Planned check instead: rank the missing (`no_grobid`/`no_doi`) papers by citations from the read set and obtain only the important ones individually.
* **Stage 3, gap analysis (started 2026-11-23, owner go-ahead).**
  * Grouping (`scripts/gap_candidates.py`, `reading/gaps.py`): 2,628 verified `OPEN_QUESTION` quotes embedded locally with `qwen3-embedding:0.6b` (Ollama, new local model), agglomerative clustering (cosine, average linkage, threshold 0.3) → 1,962 clusters, **80 recur in ≥3 distinct texts**. TF-IDF was tried first and grouped by shared words, not by question. Threshold chosen by inspecting top clusters at 0.25/0.3/0.35/0.4; not a validated optimum.
  * Failure found: 5 texts sit under two `paper_id`s each (386 cards, 381 distinct texts), which inflated recurrence (88 → 80 recurring clusters). Recurrence now counts distinct artifact SHA-256; regression test added. VERIFIED BY TEST.
  * Review of the 88 clusters (before the fix; mapped by member quotes) by the orchestrator: 23 `SPECIFIC_GAP`, 17 `MIXED`, 35 `VAGUE`, 13 `NOT_OPEN_QUESTION`, stored in `.thesis-corpus/gaps/review.json` (gitignored) with supporting quotes and addresses. Specific gaps fall into ~14 themes; the largest: XAI evaluation metrics/ground truth, joint performance-fairness-explainability evaluation in credit, counterfactual quality and robustness, fairness-metric choice, GDPR Art. 22 scope / right to explanation. Verdicts and gap statements are interpretation (single reviewer, no second review yet).
  * **Refutation attempt done for all 23 `SPECIFIC_GAP`s (2026-11-23, orchestrator, single reviewer): 6 SURVIVED, 15 CONTESTED, 2 REFUTED.** Stored in `review.json` (`refutation`, `crowded`, `refutation_note`, `refutation_evidence`; backup `review.before-refutation.json`). Sources: Semantic Scholar papers citing each gap's support papers (same year or later, theme keywords; first ≤1000 citations per seed, 3 seeds failed), verified quotes in local cards of other papers, 6 web searches, and primary legal texts. **Every one of the 43 evidence quotes is verified verbatim** by `apply_refutation.py` against an S2 abstract (API or local corpus) or a saved, hashed primary text (a changed quote aborts the merge; checked). 4 web-search leads are marked unverified.
    * Corpus pass (same day, after the owner copied `corpus.sqlite` and `reading_priority.json` from the Mac; integrity_check ok; 53,178 papers, 467,703 citation edges): full local citation graph plus SPECTER2 nearest neighbours of each gap's support-paper centroid (`corpus_candidates.py`). It found dozens of 2025–26 credit papers that jointly report accuracy, fairness and explainability, mostly single-dataset (often German Credit, n=1000) and low-venue. Q0012, Q0080 and Q0039 are now marked crowded; Q0020 gained partial evidence.
    * **Failure found and corrected:** the first-pass note on Q0012 said joint evaluation with recourse was "not found". In fact one of Q0012's own support papers does it (J-INTECH 2026: AUC, calibration, demographic parity / equalized odds, reweighing and counterfactual recourse on German Credit). Its quote was a methodological prescription ("a credible study must evaluate ... together") read as an open question. Safeguard: Part A of the Codex package now asks, per gap, whether a support paper itself already does what its quote calls for. Not yet automated.
    * Legal texts used (VERIFIED by download): CURIA press releases No 186/23 (C-634/21 SCHUFA: a score is an Art. 22 decision when lenders give it a determining role) and No 22/25 (C-203/22 Dun & Bradstreet Austria: the controller must explain the procedure and principles actually applied; trade secrets go to the authority or court for balancing). Regulation (EU) 2024/1689 from the Commission's AI Act Service Desk (consolidated text as at 27 July 2026): Annex III 5(b), Art. 6(3), Art. 14(4)(b), Art. 86. EUR-Lex refused automated download; the judgments' full texts were not read, only CURIA press releases (marked "not binding on the Court").
    * REFUTED: Q0045 (whether the GDPR gives an explanation of automated credit decisions: answered by C-203/22, plus AI Act Art. 86) and Q0025 (criticism of the 2021 AI Act proposal, superseded by the adopted Regulation). SURVIVED, all but one "crowded" (real but busy research areas): XAI evaluation standards (Q0006, Q0019, Q0073), definition of explainability in credit (Q0046), sparse human evaluation (Q0015); not crowded: co-optimisation of performance, fairness and explainability (Q0020). CONTESTED and not crowded: only Member State Art. 22 exceptions (Q0082) and trade-secret balancing in practice (Q0086). CONTESTED and crowded after the corpus pass: joint performance+calibration+fairness+recourse evaluation in credit (Q0012; still open at scale and rigour, not as a combination), performance-explainability trade-off (Q0080; measured, dataset-dependent), credit bias-mitigation benchmark (Q0039; several comparisons, no standard protocol). Total: 19 of 23 gaps are crowded.
    * Interpretation, not evidence: verdicts, `crowded` flags and notes. Survival of one bounded search is not proof of a gap.
    * Local scripts (gitignored, next to the data in `.thesis-corpus/gaps/`): `refutation_candidates.py`, `corpus_candidates.py`, `apply_refutation.py`, `make_codex_package.py`, `verify_codex_quotes.py`, `compare_reviews.py`. Whether to move them into `scripts/` is open.
  * **Codex second-review package ready:** `.thesis-corpus/gaps/codex_package/part_A_blind.md` (gaps and support quotes only, no first-review verdicts) and `part_B_compare.md` (first-review verdicts and evidence, to open after A is saved). Codex has not been run.
  * Two new texts fetched (388 `fetched`) and read with qwen3 under the RAM/thermal guard; `ollama serve` with `LLAMA_ARG_CACHE_RAM=0` logged "prompt cache is disabled" (VERIFIED).
  * **Second review by Codex done (2026-11-23, owner instruction "run the whole thing").** `codex exec` (codex-cli 0.166.0, GPT-6, `model_reasoning_effort=high`, `--search`, read-only sandbox). On Windows the read-only sandbox blocked Codex from reading even the task file, so each part was passed on stdin from an empty directory (Part A could not see `review.json`). Raw output: `codex_review_A.json`, `codex_review_B.json`.
    * Part A (blind): same verdict as the first review on 14/23; Codex rated none SURVIVED. Part B (after seeing first-review verdicts): agreed on 20/23. The jump from 14 to 20 looks like anchoring, so Part A carries more weight.
    * Codex logged 104 (A) and ~52+ (B) web actions against a stated budget of 40 searches and reported `searches_used: 40`; its budget self-report is not reliable (page opens may count as actions).
    * **Every Codex quote was fetched and matched** by `verify_codex_quotes.py`: A 34 VERIFIED, 2 not matched in arXiv PDFs (all words present; layout), 12 unreadable (bot-challenge pages at MDPI/AAAI/Springer, HTTP 403 at ResearchGate/Academia/ISO). B 52/1/15. No quote was contradicted by a page that could be read. Verified via Codex: **Regulation (EU) 2026/1744 defers Annex III high-risk obligations to 2 December 2027** (EUR-Lex), plus the full CJEU judgments' texts on CURIA.
    * **Reconciled (rule: change a verdict only on reviewer evidence that matched verbatim):** Q0006, Q0015, Q0046, Q0020 SURVIVED → CONTESTED; Q0025 REFUTED → CONTESTED (first review overstated it). Kept despite Codex: Q0019 and Q0073 SURVIVED (Codex sources unreadable; Q0073 flagged for human check of ISO/IEC TS 6254:2025). **Final: 20 CONTESTED, 2 SURVIVED, 1 REFUTED (Q0045); 19 of 23 crowded.** 49 quotes verified in `review.json`, which now carries `second_review` per gap.
    * Second instance of the failure "a support paper already addresses its own gap": Q0046 (TAX4CS framework proposed by a support paper), after Q0012.
    * Open and not crowded: Q0020 (co-optimisation of performance, fairness and explainability), Q0025 (post-adoption AI Act clarification for credit scoring), Q0082 (Member State Art. 22 exceptions), Q0086 (trade-secret balancing in practice). Interpretation, not evidence.
  * **Candidate research questions proposed (2026-11-23; see the owner decision below):** `docs/architecture/candidate-research-questions-2026-11.md`. All three sit inside the approved topic (the owner confirmed it is the same topic): **Q1 (recommended)** turn the C-203/22 / Art. 86 explanation standard into measurable tests (attribution faithfulness, counterfactual validity/actionability, complexity, stability) and evaluate SHAP, LIME and counterfactuals against an interpretable baseline on credit data; **Q2** stability of explanations across retraining / near-equivalent models (robustness methods crowded, legal framing new); **Q3** model leakage from court-suggested counterfactual explanations vs the C-203/22 trade-secret balancing (extraction attacks known; legal link not found, web not yet searched). Basis: corpus keyword queries (Q1: 5 hits, none operationalises C-203/22) and the verified legal anchors; bounded, not proof.
  * **Owner decision (2026-11-23): research direction = combination, Q1 as the foundation, Q2 and Q3 as chapters, plus a prototype.** Owner's own description (verbatim, Russian) and the decided/proposed/open split are recorded in `docs/architecture/candidate-research-questions-2026-11.md` § "Owner decision". In short: compare credit-risk models and explanation methods on how accurate, understandable and justified they are; prototype scores a person's credit risk and explains which factors mattered and what could be improved. **Not decided:** final RQ wording and hypotheses, user study (so "understandable" is proxy-only for now), datasets, exact models/methods, AI Act research exemption for the prototype (not checked); supervisor not consulted. "What can be improved" means a change that would alter the model's decision, not real-world advice.
  * **Correction recorded:** the owner's description and the orchestrator's Q1 are NOT identical (the orchestrator first said they were). Differences table in the direction doc: the owner's frame centres on comparing models and explanation methods plus a prototype; the legal criteria are the orchestrator's proposed definition of "justified".
  * **Full C-203/22 and C-634/21 judgments read** (CURIA, saved in `.thesis-corpus/gaps/sources/`). Binding ruling point 1: explain "the procedure and principles actually applied" in "a concise, transparent, intelligible and easily accessible form"; para 61: the person must understand which data were used in what way. **Para 62 (counterfactual-style "variation" explanation) is an example the referring court "could" accept, not a requirement**; the earlier wording from the press release overstated it. Criterion→test table revised accordingly.
  * **Round-2 refutation (2026-11-23, bounded: 3 corpus queries, 2 web searches, competitor abstracts fetched, all quotes matched):** closest prior work is an IJFS 2026 evidence map (only 1.3–1.5% of credit-XAI records show explanation-quality evaluation; explicitly "not a comparative ranking of explanation methods"), FinRegLab 2023 (US), EJOR 2025 and a 2026 paper on SHAP/LIME stability in credit, a SciTePress 2026 XGBoost+SHAP+DiCE framework on HELOC (equivalent to the planned prototype), and a conceptual arXiv 2026 paper arguing for legal justification beyond technical explanation. Result: an empirical comparison against the C-203/22 / Art. 86 standard was not found → Q1 survives; Q2 narrowed to counterfactual-recourse stability (attribution stability is done); Q3 not found; the prototype is not novel by itself. "Explaining Explainability" was read afterwards (next bullet).
  * **"Explaining Explainability" read (2026-11-23; PDF supplied by the owner):** Bauer, Gill, Langenbucher, Franke, SAFE White Paper No. 116, Dec 2025 — a policy paper, **not empirical** (legal analysis of SCHUFA and Dun & Bradstreet, SHAP/DiCE overview with toy examples, proposal of an intermediary institution). The web-search summary calling it a comparison of SHAP and counterfactuals was inaccurate. Not a Q1 competitor; it supports Q1 (technical feasibility "pivotal to gauge"). For Q3: its intermediary would "generate explanations without disclosing the raw model or source code", while model extraction from explanations is not discussed — Q3 would test that assumption. Quotes verified.
  * **IJFS 2026 evidence map read in full (2026-11-23; PDF supplied by the owner; Xie, Liu, Ning, published 24 Oct 2026).** Its Table 8 is a **proposed, not executed** "minimum specification for a finance-specific XAI benchmark" that overlaps strongly with Q1's design: public credit data + semi-synthetic data with a known mechanism; model ladder (regularised LR, sparse risk score, EBM, gradient boosting and its monotonic version); faithfulness + stability; regulatory-task criteria incl. reason-code accuracy and "recourse validity after scheduled retraining" (our narrowed Q2). It recommends the corrected South German Credit over Statlog German Credit (incorrect code table). C-203/22 appears only in its background; AI Act Art. 86 is not mentioned. Consequence (derived): Q1 is not novel as a design; the contribution would be executing such a benchmark with EU individual-rights criteria (C-203/22, Art. 86) plus Q3. Quotes verified.
  * **RQ and hypotheses drafted (PROPOSED, not approved):** `docs/architecture/research-question-draft-2026-11.md`. Main RQ: compare credit-risk models and explanation methods on accuracy, faithfulness/stability, intelligibility and fulfilment of the C-203/22 / Art. 86 standard in an executed finance-specific benchmark (IJFS 2026 Table 8). Sub-questions RQ1 models, RQ2 explanations, RQ3 legal proxies, RQ4 recourse stability (Q2), RQ5 leakage (Q3); hypotheses H1–H6 each with a verified basis or marked exploratory/derived; no thresholds fixed; prototype acceptance criteria proposed. Scope risk flagged (five sub-questions; deadline end of May 2027).
  * **Owner decision (2026-11-23): main RQ, RQ1–RQ5 and the priority order (RQ1–RQ3 → RQ4 → RQ5) APPROVED;** the owner expects all five to be done. **No user study now**; not required to start; may be added later as a supplement. Verbatim quotes in the RQ draft § "Owner approval". This resolves PROJECT.md §8 "final research question" at the level of the approved draft; thresholds, datasets and operationalisations remain open. Owner's working rules: think and do as much as each task needs; use Codex as second reviewer and as developer.
  * **Next:** dataset selection with licence check (orchestrator research + Codex independent check, then owner approval); fix thresholds before any run.

## Update (2026-11-22)

* PR #19 merged into `main` (owner instruction, CI green).
* **Owner decision (2026-11-22): deep reading runs on the Windows RTX 3060 PC.** Setup VERIFIED there: Ollama 0.40.17 + `qwen3:8b` (fully on GPU, 6.6 GB VRAM), uv 0.13.9, `./scripts/uv run pytest` → 243 passed on Windows, relevance eval 6/7 (same as the Mac).
* Windows fix: `runtime/stage.py` called the POSIX-only `os.killpg` on a stage timeout and crashed; on Windows it now kills the process tree with `taskkill /T`. VERIFIED BY TEST (`test_logged_wrapper_timeout` failed on Windows before, passes after).
* **Owner decision (2026-11-22): the Project Proposal DOCX is unavailable; do not use it as an input.** No binding objectives from it are assumed.
* Full texts copied from the Mac to this PC on 2026-11-22: `index.json` has 458 entries — 289 `fetched` (all files present, 285 distinct TEI files), 140 `no_grobid`, 28 `no_doi`, 1 pending. VERIFIED by local check.
* Commit `8bc6230` (fetcher waits for the allowance reset by wall clock) was pushed to `phase2/corpus-and-screening` after PR #19 was merged; it is cherry-picked here so it reaches `main`.
* `scripts/read_papers.py` reads every `fetched` entry in its own `fulltext/index.json` (not the reading list) and skips papers that already have a card. Cards go to `.thesis-corpus/cards/`; the code includes `OPEN_QUESTION` claims (`2307c1c`).
* **Owner decision (2026-11-22): the full-text fetch moved from the Mac to this PC.** Running here since 2026-11-22 under `track.py` (log `.thesis-runs/logs/fetch.log`, `--max-downloads 95 --days 6`); the Mac fetch must stay stopped (two fetchers would each keep their own `index.json` and share one daily allowance). First pass: 1 download, then waiting for the allowance reset.
* Windows run notes (VERIFIED): `track.py` cannot exec the `./scripts/uv` shell wrapper or a relative `venv/Scripts/python.exe`; pass the absolute venv `python.exe` as the child command. uv refused `.env` with CRLF and a value that was a single space (the whole file was ignored); whitespace normalized.
* Fix: `scripts/progress.py` probed liveness with `os.kill(pid, 0)`, which on Windows **terminates** the process; it now uses `tasklist` there. VERIFIED by running it next to two tracked tasks (both still running).
* **Trial deep reading (5 papers, qwen3:8b on RTX 3060, 2026-11-22):** 53–175 s per paper (8 min 45 s total, ~105 s mean); 271 of 321 proposed claims verified as exact quotes (84%), 0 failed chunks. Spot check of the claim layer: 7/271 statements were the prompt's question echoed back → now rejected by software (`statement is a question`, regression test added). `OPEN_QUESTION` kind is noisy: in a sample of 5, 2 were contributions or literature-gap sentences, not author-stated future work. Statements and kinds are model interpretation; only the quote is verified. **Gap analysis must re-check each `OPEN_QUESTION` against its quote.**
* **Full deep reading started 2026-11-22** on all 290 `fetched` texts (trial cards deleted and redone with the fixed code); log `.thesis-runs/logs/deep-reading-qwen3-windows.log`; estimated ~8–9 h from the trial rate. New texts from the fetcher are read by rerunning the same command.
* Live panes (pipeline + PC health) and a status line entry are a local Claude Code mod outside the repository (`thesis-live`).

## Session handoff (2026-11-19)

**VERIFIED (local run, branch `phase2/corpus-and-screening`, PR #19 open, not merged):** `./scripts/uv run pytest` → **243 passed**. Running on the Mac: the full-text fetch for reading list v2 (idle until the daily OpenAlex allowance resets).

* **Backward snowballing (2026-11-19):** the citation graph is complete (references for all 50,641 original papers, 467,703 edges), so no S2 key was needed. Papers outside the corpus cited by ≥5 included papers (2,538; S2 knew 2,537) were added under the tag `snowball:backward`, which is a broad query, so they were screened by qwen3 (abstract, then title-only; 0 errors) and are **never citation-rescued** (all of them are cited by construction). `scripts/build_corpus.py --snowball`, `scripts/screen_corpus.py --only-query`. Library: **27,681 included** (+870), including Rudin 2019, Doshi-Velez & Kim, Hardt et al. 2016 and Goodman & Flaxman, none of which was in the corpus before. 6,002 broad-only tail papers remain deliberately unscreened. Backup before the change: `.thesis-corpus/backups/corpus-before-snowball-20261119.sqlite` (integrity ok).
* **Graded reading priority (2026-11-19):** `scripts/reading_priority.py` scores all 51,418 papers that have SPECTER2 vectors (included, dropped and unscreened) as percentiles: relevance (max cosine to the five facet centroids) 0.5, influence (citations from included papers) 0.25, momentum (the same per year since publication) 0.25. The weights are hand-set (`shortcut:` in `corpus/priority.py`). Output: `.thesis-corpus/reading_priority.json`. Discovery artifact, not evidence.
* **Failure mode found, with a safeguard:** qwen3 screening dropped landmark general-XAI and legal papers that score in the top 1% (Arrieta et al. 2019 XAI survey, "The Disagreement Problem", "The right to explanation, explained", TreeSHAP "From Local Explanations to Global Understanding", the "Should This Loan be Approved or Denied?" dataset paper). Safeguard: reading-list selection ignores the screen verdict and records it per paper (27 of 450 in v2 were dropped by the screen). The library inclusion policy is unchanged. A regression eval case for these is still TODO.
* **Reading list v1 showed recency bias:** 44 of 447 papers are from 2025–26, although 23% of the included papers are. Owner question (2026-11-19): how can we know what to read before a research question exists? Answer adopted by the orchestrator: two rounds. **Round 1 = field map** (no research question yet): `config/reading/credit_xai_reading_list_v2.json`, 450 papers, built deterministically by `reading_priority.py --round1-out`: per facet the top 15 surveys and 35 frontier papers (2024+, ranked by relevance + momentum), then the top 200 by overall score (minimum score 96.6). 148 papers overlap with v1. **Round 2 (after candidate gaps exist):** re-score every paper against each candidate gap and read those papers, including ones the screen dropped; an agent then searches for an existing answer to try to refute each gap.
* Full text: the fetcher and the progress pane now use v2. 194 fetched, 82 have no GROBID text, 16 have no DOI. About 300 v2 papers are pending, roughly 4 days within the free allowance. Restart after a reboot (resumable, free tier only, needs `OPENALEX_API_KEY` in `.env`):
  `caffeinate -i ./scripts/uv run python scripts/track.py --name "Full text fetch v2 (OpenAlex, free tier)" -- ./scripts/uv run python scripts/fetch_fulltext.py --max-downloads 95 --days 6`
* Deep reading (L3 cards) is **not started**. Owner decision (2026-11-18): run it on the Windows RTX 3060 PC. On 2026-11-19 the orchestrator recommended the Mac instead (estimate from public benchmarks, not measured: Mac ~1 day vs Windows ~10 h for ~300 papers, ±2×; the Mac needs no setup). **Superseded 2026-11-22: Windows.** Planned addition before reading: an "open question / future work" claim type in the cards (the main source of candidate gaps). A trial `scripts/read_papers.py --limit 5` comes before the full run.
* **Research question: not chosen** (`PROJECT.md`). Agreed path: deep reading → open questions anchored in verified quotes → recurrence counts → an attempt to refute each gap (corpus + web) → Codex as second reviewer → 2–3 candidates → the owner (ideally with the supervisor) chooses → only then datasets/models/metrics. The Project Proposal DOCX submitted in autumn is not on disk; owner says it is unavailable (2026-11-22); not an input.
* Waiting on the owner (as of 2026-11-22): confirm the Mac fetch is stopped; later, study-design approval.

## Current state (2026-11-16) — authoritative summary

**VERIFIED (repository, local run):** PR #16 and PR #17 are merged into `main` (head `1065fd8` before this branch). On the earlier branch `./scripts/uv run pytest` reported **225 passed** (219 before that change); now 240, see the handoff above. Everything below the line "Historical checkpoint" is a historical record; where it says PR #16 is "under review / unmerged", that is superseded.

**Direction decided by the project owner (2026-11-16):**

* One thesis first (approved topic unchanged), with layers reusable for future theses (corpus, embeddings, per-paper appraisal cache).
* Target reading scale: thousands to hundreds of thousands of papers via a reading pyramid (metadata/graph → local screening → deep reading of hundreds → synthesis), not tens.
* Repository code should not call remote LLMs by default; bulk tasks move to local models (Ollama). Heavy reasoning is done by the orchestrating agent session. See **ADR-0003 (ACCEPTED)**.
* Owner wants minimal involvement by the end of the project; decisions are made by agent panels with recorded rationale and an owner veto window. A defense-preparation role is required because the owner must defend the thesis.
* Deadline: end of May 2027. Thesis language: English. Institution profile: `config/requirements/elte_ik_msc.json`.

**This branch (`phase2/local-llm-runtime`):**

* `OllamaStructuredReasoner` (`integrations/ollama/client.py`): schema-constrained, temperature 0, truncation is an explicit error. VERIFIED BY TEST (mock transport) and by live local eval.
* `AnthropicStructuredReasoner` now uses `messages.create` and raises on `stop_reason == "max_tokens"`. Root cause of the earlier Critic EOF: SDK `parse()` validated JSON before the stop reason could be inspected. VERIFIED BY TEST (fake client); NOT EXECUTED against the live API.
* `scripts/eval_relevance.py --ollama-model <name>`. Relevance eval, 7 cases: `qwen3:8b` 6/7, `llama3.1:8b` 5/7. Sample too small for adoption decisions.
* CI workflow `tests.yml` runs pytest on PRs (previously only the Current State Gate ran). NOT EXECUTED on GitHub yet.

**Corpus and screening (branch `phase2/corpus-and-screening`, 2026-11-16):**

* Local reusable corpus (`.thesis-corpus/corpus.sqlite`, gitignored, rebuildable with `scripts/build_corpus.py --queries config/corpus/credit_xai.json`): **50,641 Semantic Scholar papers** from 13 queries, SPECTER2 embeddings for 49,030, citation graph collection in progress (320k+ edges at time of writing). Built without an S2 key on the shared pool, zero LLM tokens. VERIFIED by local run.
* Deterministic field map (`scripts/map_corpus.py`): KMeans on SPECTER2, TF-IDF labels, PageRank. Discovery artifact only.
* Screening eval `evals/relevance/corpus_silver_v1.json`: 180 papers in two strata, labelled independently by Claude and Codex (κ = 0.81 core stratum, κ = 0.60 broad stratum), disagreements → UNCERTAIN. **SILVER**, no human expert labels; texts not stored (publisher copyright).
* Measured local screening (`qwen3:8b`): naive topic prompt kept only 27/59 RELEVANT (unusable); "any one facet" prompt 51/59. Adopted recall-first policy: papers from core queries kept without LLM; only broad-method-query papers (26.5k) are screened. On the eval the policy keeps 59/59 RELEVANT and 87/88 RELEVANT|UNCERTAIN in the core stratum; in the broad stratum it keeps 1/1 RELEVANT, drops 5/9 UNCERTAIN (generic non-tabular XAI methods) and removes 50/50 NOT_RELEVANT. **Limitation:** the broad stratum contains only one RELEVANT case, so recall for explanation-quality literature is not yet estimated.
* Throughput: ~5 s per abstract on M4 (qwen3:8b) → screening all broad-only papers ≈ 1.5 days of local compute.
* Priority screening (owner-approved 2026-11-17): after 14,570 papers screened in citation order, the remaining 11,951 broad-only papers are screened in predicted-relevance order. A logistic regression on SPECTER2 vectors is trained on qwen's own verdicts: 12,722 labels, 5-fold CV AUC 0.948, CV recall 0.971 at the top 40%. Plan in `.thesis-corpus/screening_priority_plan.json`. Papers without an abstract (1,442) are decided by rule with no LLM call. The top 40% (4,201) are screened. A random audit of 300 tail papers measures what the cut leaves. The other 6,002 tail papers stay **unscreened and reported**, not dropped silently. Caveats: CV was measured on the higher-cited half, the tail is lower-cited, so the audit is the real recall estimate. The classifier inherits qwen's narrow view of general XAI.
* Priority screening result (2026-11-18): completed with 0 errors. Top 4,201 → 552 RELEVANT, 28 UNCERTAIN. Tail audit 3/300 RELEVANT by qwen; manual reading suggests 2 of the 3 are false positives (medical). Estimated qwen-positive papers left in the 6,002 unscreened tail: ~63 (Wilson 95% CI 21–183). Estimated recall of the cut over the remaining papers: 0.90 (0.76–0.96). Over all broad-only papers: ~0.96. Library now 28,999 included papers, with 6,002 tail papers reported as unscreened.
* Screening gap and fix (2026-11-18): qwen rejected foundational general-XAI and recourse work (DARPA XAI, algorithmic recourse surveys, "Are Explanations Helpful?"). A re-screen with a widened prompt was measured on a 50-case silver stratum (Claude and Codex: κ 0.68, keep/drop agreement 44/50) and **rejected**: it kept only 8/23 keep-worthy papers. **Adopted rule:** a broad-only paper rejected or left unscreened is kept when ≥2 included papers cite it (`policy_included`). Measured: 23/23 keep-worthy kept at 23/50 precision. This rescues 225 papers.
* No-abstract papers (3,271 broad-only) are screened by title only (`--title-only`, recall-first prompt). On 300 abstract-screened papers it kept 147/150 of the abstract-positive ones and dropped 112/150 of the abstract-negative ones. The 3 losses were bank-fraud papers. Verdicts are stored under the model key `<model>:title-only`. Finished on 2026-11-18: 3,271 screened, 0 errors (2,412 NOT_RELEVANT dropped, 326 RELEVANT, 530 UNCERTAIN, 3 INSUFFICIENT_EVIDENCE kept). Library after title-only drops: 26,811 included (224 citation-rescued); 6,002 broad-only tail papers remain unscreened by design. Field map rebuilt: 25,278 papers with embeddings, 24 clusters. About 4 clusters (~2,700 papers: clinical, cognitive bias, perception, general social science) are off-topic noise from loose S2 matches on core queries, which are kept by policy; the reading pool ranks them out.
* Field map of included papers (before title-only drops): 27,613 papers, 24 clusters, `map_corpus.py --included`; rebuilt after them (see the title-only line above). Residual noise comes from loose S2 matches on the core query "fairness/bias + lending" (~480 medical titles). The reading pool handles the latter by ranking.
* Deep-reading list v1: `config/reading/credit_xai_reading_list_v1.json`, 447 papers in 5 facets: XAI-in-credit 115, XAI methods/evaluation 160, legal 74, credit ML 60, fairness in lending 38. The candidate pool comes from `scripts/reading_pool.py`: title-pattern facets ranked by citations from other included papers. The orchestrator selected from titles, years, venues and counts, with a rationale per facet. This is a discovery decision, not evidence.
* Full text: `scripts/fetch_fulltext.py` downloads OpenAlex GROBID TEI. A DOI lookup is free; a download costs USD 0.01 of the **free** USD 1/day allowance, and the account has no prepaid balance, so nothing can be charged. The fetcher stops before the allowance runs out and resumes across daily resets for at most 7 days. Artifacts are stored by SHA-256 in `.thesis-corpus/fulltext/`.
* Deep reading (L3, code done, evaluation pending): `src/thesis_factory/reading/cards.py` and `scripts/read_papers.py`. qwen3:8b (num_ctx 8192, ~6k-char paragraph chunks) proposes typed claims (research question, dataset, model, XAI method, metric, finding, limitation, legal claim), each with a verbatim quote. Software keeps only exact substrings of the cited paragraph and addresses them as an EvidenceAddress. Rejections are counted. Cards carry no appraisal; critique is a separate interpretive step. Parsed GROBID papers average ~40k characters, about 8 chunks each.

**Known gaps:**

* Live research JSON artifacts from the proposal run (`proposal_*.json`) are not present in the repository or the documented sibling directory; location UNKNOWN.
* No study design, experiments, analysis, thesis chapters, Claim Ledger, orchestrator or demo exist yet.
* Recall on explanation-quality (broad-query) literature is not yet estimated; needs a targeted eval stratum.
* Subscription limits for headless `claude -p` / `codex exec` are UNKNOWN until measured.

**Next actions:** full deep reading moves to the Windows RTX 3060 PC (owner decision 2026-11-18; needs Ollama + qwen3:8b there and a copy of `.thesis-corpus/fulltext`); first evaluate card extraction there on ~5 papers (verification rate, my spot-check of claim quality, minutes per paper) before the full run; critical appraisal over verified cards (orchestrator plus Codex as second reviewer); citation snowballing; then gap analysis → study design (owner approval). ADR-0002 and ADR-0003 ACCEPTED (owner approved PR #18).

---

# Historical checkpoint

## Post-merge continuation (2026-10-09)

PR #16 has been merged into `main`. The user reported **207 passing local
pytest tests** on its final head. Earlier references below to PR #16 being
unmerged and its pre-merge test status are historical review snapshots.

The long-term product objective is a single bounded, auditable run that can
research the approved credit-scoring XAI topic, perform reproducible thesis
experiments, prepare a complete draft, and independently critique its claims.
It must preserve all intermediate evidence and permit explicit human gates.
**A ten-hour end-to-end thesis orchestrator is not yet implemented.**

Next incremental slice: offline research JSON checkpointing, stage-level
append-only logging, model-usage event API, and human-reviewable intermediate
PR preparation. See `docs/architecture/autonomous-thesis-workflow.md`.

Last updated: 2026-10-09

## Current Phase

**Phase 1 — Evidence Acquisition and Proposal Research — PR #16 under review (unmerged)**

Phase 0 — Project Foundation — is complete.

The approved thesis topic is:

`A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring`

The retrieval architecture comparison cycle is complete for the current Phase 1 scope. Voyage `voyage-4` remains the selected default semantic retriever for evidence acquisition, with BM25 retained as the deterministic lexical baseline and diagnostic comparator.

The system now supports bounded proposal-oriented research from an approved topic through discovery, verification, exact evidence extraction, research synthesis, adversarial critique, and proposal writing.

The immediate objective is to review and integrate PR #16 safely. A Project Proposal DOCX has already been generated outside the repository through a deadline-specific direct writer invocation; formal university submission is not confirmed. The normal Critic-to-Writer production pipeline was not completed.

The governing rule remains:

**LLM proposes. Software verifies. Evidence proves. Human approves.**

---

## Current Objective

Complete an engineering review of [PR #16](https://github.com/Kreeby/Thesis-Factory/pull/16), branch `phase1/evidence-acquisition` targeting `main`, before merging. This PR currently consists of 3 commits, 67 changed files and about 12,657 added lines. The branch contains source implementations and unit tests for acquisition, scholarly and primary source verification, research synthesis, Critic and Writer. It already contains a `CURRENT_STATE.md` change, but its existing content incorrectly describes the proposal as unfinished and some gates as passed.

1. Run the **full local deterministic test suite on the exact PR head**; current GitHub Actions only verifies that `CURRENT_STATE.md` changed, not test success.
2. Review new source trust boundaries, exact span claims, error handling, bounded API cost and coverage.
3. Preserve the actual proposal artifacts and the history of merged Phase 1 retrieval benchmarks without pretending the deadline-specific proposal was produced through a fully validated end-to-end pipeline.
4. Address merge blockers; retain later research improvements as explicit next steps rather than expanding this PR indefinitely.

The governing rule remains **LLM proposes. Software verifies. Evidence proves. Human approves.**

---

## Approved Thesis Topic

**A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring**

Topic selection is complete for the current proposal workflow.

Dataset, model, XAI-method, metric, legal-criterion, and experiment choices remain research decisions and must not be silently inherited from earlier manual drafts.

---

## Completed Capabilities

### Project Foundation

* Python 3.12 runtime managed through `uv`.
* `./scripts/uv` is the canonical project runner.
* Pydantic validates domain artifacts.
* `PROJECT.md`, `AGENTS.md`, `ARCHITECTURE.md`, and `CURRENT_STATE.md` are established.
* ADR process exists under `docs/decisions/`.
* Claude is the default LLM family for autonomous reasoning agents.
* Repository state is canonical project memory.
* Branch → pull request → human review → merge is the default workflow.
* Pull requests targeting `main` must update `CURRENT_STATE.md`.
* `.github/workflows/current-state-gate.yml` enforces that invariant.

### Scholarly Discovery and Verification

* OpenAlex scholarly discovery integration is implemented.
* Crossref and DataCite DOI lookup are available behind a provider-independent registry boundary.
* Bibliographic identity verification is implemented.
* Verification states preserve conflict and insufficient-data outcomes.
* OpenAlex lexical and semantic search modes exist.
* Search planning is bounded.
* Discovery provenance is preserved.
* Discovery candidates are not treated as evidence.

### Source Text and Artifact Acquisition

* Full-text location resolution is separate from source identity.
* OpenAlex GROBID XML, cached PDF, original OA PDF, and scholarly landing locations are represented.
* GROBID XML is preferred when available.
* Artifact downloads are bounded and validated.
* Raw artifact bytes receive SHA-256 identity.
* OpenAlex content API authentication is supported.
* Credentials are not stored in provenance.

### Scholarly Document Normalization

* `NormalizedDocument`, `NormalizedSection`, and `NormalizedParagraph` are implemented.
* Scholarly normalization is versioned.
* GROBID TEI parsing is deterministic.
* Section structure and paragraph ordinals are stable within a normalization version.
* Upstream ambiguity is preserved rather than silently repaired.

### Exact Evidence Addressing

* `EvidenceAddress` and `EvidenceSpan` are implemented.
* Evidence identity includes artifact SHA-256, normalization version, paragraph ordinal, start offset, and exclusive end offset.
* Evidence text is re-resolved deterministically.
* Invalid artifact identity, normalization version, paragraph, or offset is rejected.
* LLMs never compute canonical evidence offsets.

### Retrieval

* One normalized paragraph is one canonical `RetrievalUnit`.
* BM25 is implemented as deterministic lexical retrieval.
* Semantic retrieval is implemented behind a provider-independent embedding boundary.
* Voyage `voyage-4` is the selected semantic retriever for evidence acquisition.
* Semantic ranking uses cosine similarity.
* Retrieval and evidence extraction are separate concerns.
* Context expansion does not change retrieval-hit identity.
* Reciprocal Rank Fusion was evaluated and is retained only as an audited negative experiment.
* Existing development and held-out benchmarks remain frozen.

### Evidence Acquisition Core

* `EvidenceRequirement` is implemented.
* Requirement kinds cover literature, legal, dataset, baseline, method, metric, feasibility, and contribution needs.
* Evidence-query planning is bounded.
* Context expansion is deterministic and bounded.
* Claude-backed extraction operates only over supplied bounded context.
* Evidence support states are:
  * `SUPPORTED`;
  * `PARTIAL`;
  * `NOT_SUPPORTED`;
  * `INSUFFICIENT_EVIDENCE`.
* Supporting proposals require exact quote candidates.
* Unsupported and insufficient proposals cannot fabricate supporting evidence.
* Exact quote verification is deterministic.
* Character offsets are computed by software.
* Verified evidence preserves exact provenance.

### Proposal Research Domain

* Proposal research dimensions include:
  * problem;
  * research gap;
  * research question;
  * dataset;
  * baseline;
  * method;
  * metric;
  * feasibility;
  * contribution;
  * risk;
  * deliverable.
* Research epistemic states are:
  * `SUPPORTED`;
  * `DERIVED`;
  * `ASSUMPTION`;
  * `UNKNOWN`.
* Supported and derived findings must reference evidence requirements.
* Assumptions and unknowns cannot masquerade as evidence-backed findings.
* Proposal research synthesis may use only the approved topic, supplied requirements, and verified evidence.
* Proposal research synthesis performs no new research.

### Proposal Critic

* An adversarial proposal critic is implemented.
* Critique severities are `BLOCKER`, `MAJOR`, and `MINOR`.
* Verdicts are `PASS`, `REVISE`, and `FAIL`.
* The critic checks unsupported claims about novelty, law, datasets, methods, baselines, metrics, feasibility, and contribution.
* `PASS` requires no remaining critique issues.
* `FAIL` requires at least one blocker.

### Proposal Writer

* Proposal writing is separate from research.
* The writer performs no new research.
* The writer requires critic approval.
* Proposal paragraphs distinguish evidence-backed material, proposed work, and limitations.
* Assumptions and unknowns cannot be presented as established facts.

---

## Proposal Research Completed

### Live Discovery

A bounded discovery pass was completed across five research objectives:

* legal and problem framing;
* dataset candidates;
* baselines and methods;
* evaluation metrics;
* feasibility, contribution, and limitations.

The discovery artifact contains 39 research leads from 97 provider citations.

These citations are discovery provenance only and are not verified research evidence.

The discovery stage should not be rerun before the current proposal unless a concrete blocker later requires it.

### Deterministic Verification Plan

Verification planning is deterministic and local.

The current plan contains 18 bounded verification tasks:

* 5 official legal / regulatory primary-source tasks;
* 3 dataset-primary tasks;
* 10 scholarly tasks.

Twenty-one lower-priority discovered leads were intentionally deferred.

### Scholarly Verification

The scholarly verification lane reuses the existing stack:

`OpenAlex`

→ bibliographic identity verification

→ full-text acquisition

→ GROBID normalization

→ BM25 prefilter

→ Voyage semantic retrieval

→ bounded context

→ Claude evidence proposal

→ deterministic exact-span verification

All ten planned scholarly tasks completed.

The current scholarly artifact contains seven `PARTIAL` results and three `INSUFFICIENT_EVIDENCE` results.

The scholarly lane is sufficient for the first proposal pass and should not be rerun before synthesis.

### Official EU Primary-Law Verification

Known EU legal instruments and CJEU cases are resolved deterministically by CELEX rather than using LLM web search for source location.

Preferred path:

`verification requirement`

→ deterministic CELEX resolution

→ Publications Office / Cellar primary content

→ deterministic normalization

→ SHA-256 artifact identity

→ BM25 / Voyage retrieval

→ Claude evidence proposal

→ deterministic exact-span verification

InfoCuria search/list shells are not accepted as evidence sources.

The five planned legal tasks now resolve to official EU primary sources and currently produce `PARTIAL` evidence rather than overstated full support.

Current verified legal coverage includes:

* SCHUFA / C-634/21 treatment of creditworthiness scores under Article 22;
* the condition that a third party draws strongly on the score;
* Dun & Bradstreet Austria / C-203/22 explanation content;
* Article 15(1)(h) explanation rights read with Article 22(3);
* CCD2 explanation and human-review language;
* the AI Act profiling carve-back for Annex III systems.

The legal lane is sufficient for the current proposal pass.

### Dataset Primary-Source Verification

Current seeded candidates are:

* FICO HELOC;
* UCI Statlog German Credit / South German Credit correction;
* Kaggle Home Credit Default Risk.

The first full primary-source pass left all three as `INSUFFICIENT_EVIDENCE`.

That result established a verification gap, not dataset unsuitability.

A bounded dataset-primary retry capability has now been implemented.

Known dataset families use deterministic canonical routes where possible:

* FICO-controlled challenge / newsroom sources for HELOC;
* UCI canonical pages for German Credit and the South German Credit correction;
* Kaggle canonical competition data / evaluation / rules pages for Home Credit.

Primary-source retrieval now searches both the verification question and the explicit `why_needed` criteria before semantic ranking.

The bounded dataset retry completed. Final primary results: 5 legal tasks PARTIAL, German Credit dataset task PARTIAL (2 exact spans), FICO HELOC and Home Credit INSUFFICIENT_EVIDENCE. Legal verification had 11 exact spans; scholarly verification had 16. Across 18 verification tasks: 13 PARTIAL, 5 INSUFFICIENT_EVIDENCE and 29 exact spans. These statuses are not evidence of full support for each broad requirement.

No additional broad dataset-landscape stage is required before the current Project Proposal.

---

## Current Research Artifacts

The recorded proposal workflow uses:

* `proposal_discovery.json`
* `proposal_verification_plan.json`
* `proposal_scholarly_evidence_v2.json`
* `proposal_primary_evidence_v3.json`

These are machine-readable inputs to proposal synthesis.

They are not themselves trusted prose.

---

## PR #16 — Verified Implementation and Research Checkpoint

**PR facts as observed on GitHub, 2026-10-09:** `main` base `26701a0`; head `e2b2775`; 3 commits (`2bd80bb`, `c79866f`, `e2b2775`); 67 changed files; open and unmerged. The PR does include `CURRENT_STATE.md`. The GitHub Actions `Current State Gate` ran successfully and checks only that this file was changed. Full suite status on the exact head remains unknown.

### Code implemented in the branch

* **Evidence requirements and extraction:** `domain/evidence_acquisition.py`, `evidence/context.py`, `evidence/extraction.py`. Typed evidence states, bounded queries and contexts, quote proposals, exact source spans and deterministic address verification. A citation reference is not proof of semantic entailment.
* **Research roles:** `domain/proposal_research.py`, `research/proposal_research.py`, `research/proposal_critique.py`, `research/proposal_writing.py`. SUPPORTED, DERIVED, ASSUMPTION and UNKNOWN are epistemically distinct. Critic supports PASS/REVISE/FAIL. The writer's normal API requires PASS.
* **Web discovery and planning:** Anthropic web research, lead extraction, bounded deterministic verification planning and scripts. Web citations are discovery provenance only.
* **Scholarly acquisition:** OpenAlex bibliographic identity and GROBID full text, BM25/Voyage retrieval, exact verified extraction and bounded scholarly verification executor.
* **Primary source acquisition:** deterministic legal CELEX candidate routing; Publications Office/Cellar primary-source content, HTML/XHTML/XML normalization, source authority host policy, source audit and SHA-256 identities. Canonical dataset URLs for FICO HELOC, UCI German/South German Credit and Kaggle Home Credit are seeded candidates, **not a landscape search**.
* **Checkpointed CLI scripts:** research discovery, verification planner, scholarly verification, primary verification and dataset retry. Dataset retry preserves previous primary task results and replaces insufficient dataset tasks.
* **Tests:** domain, context, extraction, model integration, legal source routing, fetch and normalization, planners, scholarly and primary executors, proposal research, Critic and Writer have test files in the PR. Earlier local reports: 153 passed after evidence core, 162 passed after research contracts; another later development run reported 201 passed / 1 stale assertion failed and a focused correction test. These are historical snapshots, not proof that the final head's full test suite passes.

### Real research artifacts — live run outcomes, outside this PR

* **Discovery:** 5 bounded objectives, 97 citations, 39 leads. Citations were discovery-only.
* **Plan:** 18 tasks (5 official legal, 3 dataset-primary, 10 scholarly), 21 leads deferred.
* **Scholarly:** 10 task results, 7 PARTIAL / 3 INSUFFICIENT_EVIDENCE, 30 usable full texts and 16 exact spans. Outstanding specific gaps include HELOC baseline performance, preprocessing details and out-of-time validation.
* **Official legal:** 5 PARTIAL, 11 exact spans from SCHUFA C-634/21, Dun & Bradstreet Austria C-203/22, GDPR discussion, CCD2 recital and AI Act profiling text. Other aspects (CCD2 operative Art. 18(8), Annex III 5(b) and fraud exclusion, broad legal extension claims) are not verified by the selected spans.
* **Datasets:** German Credit PARTIAL with two exact UCI snippets distinguishing original categorical `german.data` and edited indicator-file; FICO HELOC and Home Credit INSUFFICIENT_EVIDENCE. No final dataset selection is justified.
* **Aggregate:** 18 tasks; 13 PARTIAL, 5 INSUFFICIENT_EVIDENCE, 29 verified exact spans. These numbers do not mean all legal/dataset questions were answered.
* **Synthesizer:** `proposal_research_draft.json` produced and structurally validated, acknowledging unproven research gap, provisional model choices, no final dataset and non-compliance claims.
* **Critic:** live response truncated into invalid JSON; no validated verdict or critique artifact. Human explicitly skipped Critic rather than fabricating findings or PASS.
* **Document:** direct one-off structured writer call, document structural validation and external DOCX render succeeded. Not reproducible through an integrated renderer in PR #16. University submission remains unconfirmed.

### Engineering review findings (require prioritization, not fabricated fixes)

1. `validate_research_draft` checks evidence IDs/status/spans but **does not guarantee semantic support** for generated claims. `validate_proposal_document` checks finding references and paragraph class, not external truth, complete citation bibliographies or legal compliance.
2. Critic's large structured output can truncate and cause parsing errors. Never spend more API tokens on blind retries; add local fake-client/size tests before a future targeted fix.
3. Primary executor's bounded `max_documents` and ranking of a **single best result** can omit complementary partial evidence across sources. PARTIAL and INSUFFICIENT_EVIDENCE must remain visible.
4. Host allowlists establish authority of domain but do not establish that the fetched content proves the requirement. HTTP 503, HTML shells and rate limits can cause legitimate verification gaps.
5. Seeded three-dataset canonical routing cannot be treated as a comprehensive autonomous search and evaluation of all candidate datasets.
6. Preserving the old `CURRENT_STATE.md` evaluation history matters: earlier abbreviated replacement removed many exact historical retrieval benchmark measurements. This document keeps current capabilities and the decision not to retune frozen benchmarks, but that earlier detailed historical measurement record remains retrievable from `main` before merge and should be preserved durably.
7. `PROJECT.md` still contains older phase/unknowns language; align after the feature PR is reviewed. Do not silently invent or rewrite ADRs.

### Outstanding decisions after integration

Final research gap; dataset and licence strategy; feature provenance and representativeness; model/baseline/XAI selection; preprocessing and split; technical explanation-quality and calibration metrics; legal-to-metric mapping without compliance claims; empirical evaluation and statistical design; Claim Ledger; provenance storage and end-to-end artifact generation; scalable but bounded agent exploration; formal university AI policy. None of these are complete just because a proposal draft exists.

---

## In Progress

**PR #16 review and merge readiness.** No new source discovery or Anthropic/Voyage calls are necessary to complete this checkpoint.

The recorded live research run produced `proposal_research_draft.json` with 31 findings and passed the structural validator. The Critic call failed because the generated JSON was truncated (Pydantic EOF while parsing around column 8160). **No valid Critic result or verdict was produced**. The beginning of the invalid output mentioned `REVISE`, but this is not a parsed/validated verdict.

The human expressly rejected fabricating a critique or a fake `PASS` and authorized skipping Critic for the immediate deadline. An isolated direct call to `AnthropicStructuredReasoner.generate` produced `proposal_document_draft.json`; `validate_proposal_document` passed. A DOCX Project Proposal was then generated separately from the repository. **Normal `ProposalWriter.write` still requires a genuine Critic `PASS`, and PR #16 contains no integrated human-override workflow or DOCX exporter.**

Formal proposal submission is not confirmed. Dataset selection, novelty, research gap and experimental feasibility remain provisional. No empirical thesis experiments have been conducted.

---

## Deferred Until After the Project Proposal

Unless required to resolve a true blocker, defer:

* broad dataset-landscape discovery beyond the seeded candidates;
* full empirical comparison across many datasets;
* final thesis dataset lock;
* model training;
* XAI execution;
* experiment implementation;
* statistical result analysis;
* final Claim Ledger population from experiment results;
* long-term provenance persistence;
* vector database selection;
* orchestration framework selection;
* experiment-tracking platform selection;
* execution sandbox design;
* observability stack;
* deployment architecture;
* PDF-only scholarly normalization improvements not needed by the current evidence set;
* first-class table, figure, and equation evidence nodes.

The proposal may describe these as planned work. It must not claim they are already complete.

---

## Active Decisions

### Confirmed

* Approved topic: `A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring`.
* Claude is the default LLM family for autonomous reasoning agents.
* LLM output is not factual evidence.
* Web search and provider citations are discovery, not evidence.
* Discovery, verification, retrieval, extraction, synthesis, criticism, and writing remain separate concerns.
* Researcher, Critic, and Writer are separate roles.
* Writer performs no new research.
* Missing evidence remains explicit.
* Evidence support states and research epistemic states are separate concepts.
* Raw artifacts use SHA-256 identity.
* Normalization algorithms are versioned.
* Exact evidence spans are deterministically verifiable.
* LLMs do not compute canonical evidence offsets.
* BM25 remains the deterministic lexical baseline.
* Voyage `voyage-4` remains the selected semantic retriever for evidence acquisition.
* Existing retrieval benchmarks remain frozen.
* Context expansion remains separate from ranking and retrieval identity.
* Agent fan-out, retries, searches, and provider calls remain bounded.
* Proposal verification planning is deterministic.
* Official EU legal sources are resolved deterministically when possible.
* A downloadable primary source does not by itself establish evidentiary support.
* Partial evidence remains `PARTIAL`.
* The proposal may contain explicit limitations and unknowns.
* The current proposal should be completed from the evidence already collected instead of opening a new broad research cycle.
* Dataset choice for final thesis experiments remains revisable after the proposal.
* German Credit is not automatically selected as the primary dataset merely because it is a seeded candidate.
* Human approval remains required for consequential research decisions.
* Every pull request targeting `main` updates `CURRENT_STATE.md`.

### Not Yet Decided

* final primary dataset for thesis experiments;
* whether companion datasets will be used;
* final predictive baseline set;
* final predictive model set;
* final XAI method set;
* final quantitative explanation-quality metric set;
* final experiment design;
* final statistical-analysis plan;
* exact thesis Claim Ledger schema;
* long-term provenance persistence representation;
* vector persistence;
* orchestration framework;
* experiment-tracking system;
* deployment architecture;
* final university policy position on generative-AI assistance and disclosure.

---

## Current Risks

### RISK-001 — Deadline-driven architecture expansion

The earlier proposal deadline exposed the risk that every incomplete research facet triggers a new subsystem.

**Mitigation:** scope new architecture against measured blockers, preserve provenance, and treat existing proposal output as a historical checkpoint.

### RISK-002 — Model-generated false certainty

LLMs may make stronger claims than the evidence supports.

**Mitigation:** exact spans, explicit support states, deterministic validation, adversarial criticism, and human review.

### RISK-003 — Discovery/evidence confusion

Search results or provider citations may be mistaken for verified evidence.

**Mitigation:** only deterministically verified source artifacts may support evidence-backed findings.

### RISK-004 — Full-text availability

Relevant scholarly sources may not expose usable full text.

**Mitigation:** preserve `INSUFFICIENT_EVIDENCE`; do not chase providers without a bounded reason.

### RISK-005 — Primary-source access variability

Official and dataset-provider sites may return redirects, shells, rate limits, or inconsistent content formats.

**Mitigation:** deterministic authority policy, bounded retries, canonical endpoints, artifact hashes, and explicit fetch failures.

### RISK-006 — Legal overclaiming

A judgment or regulation may support only part of a broad requirement.

**Mitigation:** preserve `PARTIAL`; proposal prose may use only the supported facet.

### RISK-007 — Dataset representativeness

A benchmark may be old, small, synthetic, weakly documented, or unrepresentative of modern consumer credit.

**Mitigation:** keep final dataset selection provisional where evidence does not justify a lock.

### RISK-008 — German Credit age and coding history

German Credit is historically important but old, small, and associated with coding/version issues.

**Mitigation:** distinguish original Statlog from the South German Credit correction and do not equate historical benchmark popularity with modern representativeness.

### RISK-009 — External API cost and instability

Anthropic, Voyage, OpenAlex, and other providers may fail or consume paid quota.

**Mitigation:** classify remote runs explicitly, run local preflight before paid retries, checkpoint long runs, and avoid blind reruns.

### RISK-010 — Documentation drift

Repository prose may lag behind runtime state.

**Mitigation:** runtime and tests are authoritative; update `CURRENT_STATE.md` at checkpoints.

### RISK-011 — Proposal over-specification

The proposal may present planned experiments or dataset choices as if they had already been empirically validated.

**Mitigation:** separate completed research, proposed methodology, expected contribution, and limitations.

---

## Known Unknowns

1. Final primary dataset or dataset combination.
2. Final predictive baselines and model families.
3. Final XAI methods.
4. Final quantitative explanation-quality metrics.
5. Exact translation from legal explanation requirements to measurable empirical criteria.
6. Final experimental design.
7. Final statistical-analysis plan.
8. Availability and appropriateness of sensitive attributes for fairness-oriented analysis.
9. Exact dataset limitations around provenance, licensing, age, and representativeness.
10. Current formal university policy for generative-AI assistance and disclosure.
11. Final thesis research questions after synthesis and critique.
12. Final contribution scope.
13. Final implementation and reproducibility plan.
14. Final Claim Ledger schema.

These unknowns do not all need to be eliminated before the Project Proposal.

---

## Next Actions

1. Review [PR #16](https://github.com/Kreeby/Thesis-Factory/pull/16) at head `e2b277528dbeeb671f6e8f82797333c47376c808` and verify full `./scripts/uv run pytest` result locally (**FREE / LOCAL**). Earlier checkpoint test counts are not a current-head test result.
2. Inspect the complete diff for correctness, provenance, unsafe secret handling and unintended checked-in research artifacts. The only GitHub Actions run observed for the PR is the passing `Current State Gate`; it does **not** run pytest.
3. Update `CURRENT_STATE.md` in the same feature branch; do not make fictional audit results or claim an integrated Critic-bypass implementation.
4. Keep canonical run artifacts (`proposal_discovery.json`, `proposal_verification_plan.json`, `proposal_scholarly_evidence_v2.json`, `proposal_primary_evidence_v3.json`, `proposal_research_draft.json`, `proposal_document_draft.json`) and the DOCX under controlled provenance if storage/versioning is explicitly chosen; they are not currently part of PR #16.
5. Preserve the existing held-out retrieval benchmark and `voyage-4` decision from PR #14 without retrospective tuning.
6. After human review and approval, merge the PR. Then consider a durable proposal workflow and careful dataset landscape comparison as **future** work, not accomplished PR functionality.

---

## Current Milestone Exit Criteria

**For this PR**, acceptance requires accurate documentation, a current full local test report, reviewed code and bounded provider calls, no accidental credentials/runtime outputs committed, known gaps clearly recorded, and explicit human review. A passing documentation gate alone is not sufficient.

The Project Proposal draft and DOCX were generated under an explicit deadline-specific decision to skip Critic. The integrated Critic→Writer PASS-gated path remains unverified, and formal submission has not been established.

---

## Runtime Authority

Repository documentation is project memory, but executable behavior and tests are authoritative.

Before committing this checkpoint:

1. run the full deterministic suite with `./scripts/uv run pytest`;
2. record no exact passing-test count unless it comes from the current runtime;
3. inspect `git status --short`;
4. verify that secrets or credentials are not staged;
5. commit `CURRENT_STATE.md` together with the implementation changes that produced this state.

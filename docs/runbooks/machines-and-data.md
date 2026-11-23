# Working on the Mac or the Windows PC

Last updated: 2026-11-23. What is in git, what must be copied by hand, and how to start on either machine.

## In git (clone/pull is enough)

* Code: `src/`, tests, `scripts/` (incl. stage-3 gap/refutation scripts `scripts/gap_*.py`,
  `scripts/data_manifest.py`) and Windows run scripts in `scripts/windows/`.
* Canonical state and decisions: `PROJECT.md`, `ARCHITECTURE.md`, `CURRENT_STATE.md`, `docs/decisions/`,
  research direction `docs/architecture/candidate-research-questions-2026-11.md`, approved research question
  `docs/architecture/research-question-draft-2026-11.md`.
* Data manifest: `docs/runbooks/data-manifest.json` (sizes and SHA-256 of the local data below).

## NOT in git — copy by hand (`.thesis-corpus/` is gitignored: size, publisher rights)

| Path | What | Where it was produced |
|---|---|---|
| `.thesis-corpus/corpus.sqlite` | 53,178-paper corpus, SPECTER2 vectors, citation graph | Mac (copied to the PC 2026-11-23) |
| `.thesis-corpus/reading_priority.json` | reading-priority scores | Mac |
| `.thesis-corpus/fulltext/` | GROBID TEI full texts + `index.json` | PC (fetcher runs here) |
| `.thesis-corpus/cards/` | deep-reading cards (verified quotes) | PC |
| `.thesis-corpus/gaps/` | clusters, `review.json` (gap verdicts, refutation, second review), Codex inputs/outputs, saved legal and paper texts in `sources/` | PC |
| `.thesis-corpus/datasets/` | dataset licence checks (Codex output) | PC |
| `.env` | API keys (OpenAlex etc.) | each machine; never commit |

Copy the whole `.thesis-corpus/` folder (USB or network), then verify on the target machine:

```
./scripts/uv run python scripts/data_manifest.py --check docs/runbooks/data-manifest.json
```

Every line must say `OK`. `fulltext/` changes while the fetcher is running; if only `fulltext` and
`fulltext/index.json` differ, check whether the fetcher downloaded more since the manifest was written.
Regenerate the manifest after a deliberate change: `--write docs/runbooks/data-manifest.json`.

## Rules that prevent damage

* **Only one full-text fetcher at a time.** Each machine keeps its own `fulltext/index.json` but they share
  one daily OpenAlex allowance. As of 2026-11-23 the fetcher runs on the PC; keep the Mac fetcher stopped.
* After copying, decide which machine is the writer for `.thesis-corpus/`; do not edit it on both and
  copy back and forth without re-checking the manifest.

## Starting on the Mac

```
git pull
./scripts/uv run pytest            # expect all tests to pass
./scripts/uv run python scripts/data_manifest.py --check docs/runbooks/data-manifest.json
```
Then read `CURRENT_STATE.md` ("Update (2026-11-23)").

## Starting on the Windows PC (local-model work)

1. `scripts\windows\start_ollama_serve.ps1` — starts `ollama serve` with `LLAMA_ARG_CACHE_RAM=0`
   (the tray app does not pass it; root cause of the 2026-11-22 freeze). After a model loads,
   `.thesis-runs\logs\ollama-serve.log` must contain "prompt cache is disabled".
2. `. .\scripts\windows\load_env.ps1` — loads `.env` into the session without printing it.
3. Full-text fetch: `scripts\windows\start_fetch.cmd` (resumable; waits for the free daily allowance).
   Do not start it from PowerShell with `>>`: PowerShell 5.1 writes UTF-16 and corrupts the log.
4. Local-model jobs (e.g. reading new texts): `scripts\windows\start_reading.cmd`, then immediately
   `powershell -File scripts\windows\ram_guard.ps1` (stops the job at free RAM < 2.5 GB, GPU ≥ 85 °C for
   30 s, or thermal slowdown). Afterwards `ollama stop qwen3:8b`.
5. Codex on Windows: the read-only sandbox cannot read files; pass the task on stdin, e.g.
   `codex --search exec -s read-only --skip-git-repo-check -c model_reasoning_effort=high -C <empty dir> -o out.json "..." < task.md`.
   Verify every Codex quote with `scripts/gap_verify_codex_quotes.py`.

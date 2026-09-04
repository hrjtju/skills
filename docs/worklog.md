# Worklog — skills repo

## 2026-09-03 — Merge six LaTeX skills into `latex-academic` + fold in package manuals

### Task
1. Read `~/Downloads/cleveref.pdf` and add a working reference on customising `\cref` behaviour.
2. Merge the LaTeX skills into one: `latex-paper-en` + `latex-fmt` + `latex-polish` + `latex-rescue`
   + `latex-document-skill` + `pdf2tex`.
3. Fold in today's downloaded LaTeX helper PDFs (`pgfmanual.pdf`, `tikz-3dplot_documentation.pdf`,
   `tikz-cd-doc.pdf`) into the merged skill.

Decisions (confirmed with user): merge all six (a); new dir + update paper-audit path (b); unified routing
SKILL.md preserving all sub-files (a); reference the most-used latex-document scripts (4).

### What I did
- **Base:** `git mv latex-paper-en latex-academic` (keeps ~60 refs, 24 scripts, 5 venue templates, examples,
  evals, agents, and all internal relative paths — scripts use `Path(__file__).parent`, refs are relative to the
  skill dir, so nothing broke).
- **Absorbed foreign references** (all content preserved, no collisions):
  - `latex-fmt` → `references/formatting/formatting-rules.md`, `references/venues/venue-guide.md`
  - `latex-polish` → `references/writing/{academic-phrasebank,chinglish-patterns,section-anatomy,style-guardrails}.md`
  - `latex-rescue` → `references/latex/{error-catalog,package-conflicts,debug-workflow}.md`
  - `pdf2tex` → `references/pdf2tex/{pdf-extraction-guide,structure-detection,math-reconstruction,table-reconstruction}.md`
  - `latex-document` (curated "most-used"): 18 refs → `references/tooling/`; 14 scripts →
    `scripts/` (`compile_latex.sh`, `validate_latex.py`, `convert_document.sh`, `latex_diff.sh`,
    `latex_wordcount.sh`, `latex_package_check.sh`, `latex_citation_extract.sh`, `latex_lint.sh`,
    `latex_analyze.sh`, `csv_to_latex.py`, `generate_chart.py`, `mermaid_to_image.sh`, `graphviz_to_pdf.sh`,
    `plantuml_to_pdf.sh`).
- **New knowledge references:**
  - `references/latex/cleveref.md` — full `\cref`/`\Cref`/`\crefrange`/multi-ref/page-ref command set, package
    options (`capitalise`, `nameinlink`, `noabbrev`, `sort`/`compress`), and the **three-tier customisation**
    (global components → per-type `\crefname`/`\creflabelformat`/`\crefrangelabelformat` → low-level
    `\crefformat`/`\crefrangeformat`/`\crefmultiformat` + `\labelcrefformat`), `\crefstripprefix`, type
    override, babel/polyglossia, `cleveref.cfg`, load-order gotchas, known incompatibles.
  - `references/latex/tikz.md` — TikZ/PGF core cheat-sheet + `tikz-3dplot` (frames,
    `\tdplotsetmaincoords`, rotated coords, `\tdplotsetcoord`, `\tdplotdrawarc`, spherical surface) + `tikz-cd`
    (commutative diagrams, arrow tips, labels, `row sep`/`column sep`).
- **SKILL.md:** `name: latex-academic`, broadened description/`when_to_use`/`triggers` (`/latex`,
  `/latex-fmt`, `/latex-polish`, `/latex-rescue`, `/pdf2tex` kept as aliases), added modules `polish`, `rescue`,
  `pdf2tex`, `document`, `tikz`, `cleveref` to the router; updated Reference Map + Routing Rules + tags
  (v7.0.0). Added `agents/config.yaml`.
- **Dependency fix:** `paper-audit/scripts/audit.py` `SCRIPTS_EN` → `latex-academic/scripts`; updated
  `TROUBLESHOOTING.md`, vendored `parsers.py`/`tex_loader.py`/`check_references.py` comments, and
  `paper-read/SKILL.md` cross-skill `/latex-*` suggestions.
- **Deleted** the five old skill dirs (`latex-fmt`, `latex-polish`, `latex-rescue`, `latex-document`, `pdf2tex`);
  `latex-paper-en` was consumed by the rename.

### Verification
- SKILL.md YAML parses; `name: latex-academic`, 25 tags, v7.0.0.
- All `scripts/*.py` pass `py_compile`; `tex_loader` + `parsers` import OK from the new path.
- `paper-audit.audit.py` now resolves scripts via `latex-academic/scripts`.

### Notes / open items
- Pre-existing dangling paths in `paper-audit/scripts/audit.py` (not introduced here): `SCRIPTS_ZH` →
  `latex-thesis-zh/scripts` and `SCRIPTS_TYPST` → `typst-paper/scripts`, neither of which exists in this repo.
- `latex-thesis-zh` (referenced in the skill description) is not in this repo — pointer kept, but the script
  path remains dangling; reconcile in a follow-up.
- `references/tooling/` carries only the curated latex-document content; the rest of the old
  `latex-document-skill` (e.g. PDF form-fill scripts) was intentionally not carried per decision (4).
- The merged skill's reference to `paper-audit`/`nature-*`/`paper2ppt` is intended delegation.

### Reflection
- **Why rename-as-base:** `latex-paper-en` was already a clean module-router skill with the richest reference/script
  set and is the hardest-external-dependency target (`paper-audit` reads its scripts). Renaming the directory
  (not copying) preserved every internal relative path, so 24 scripts + ~60 refs kept working with zero edits.
- **Why curated latex-document:** it's a broad generic-tooling skill (forms, mail-merge, encrypted PDFs) largely
  orthogonal to academic editing; folding all of it would bloat the `\cref`-focused paper skill. Only the
  most-used production/diagram tools were carried.
- **Gotcha caught:** an early `edit` accidentally dropped the `adapt` router row + `## Routing Rules` heading;
  repaired by re-inserting the row/header and appending the new modules in one replacement. A relative-path
  `cp` failed (wrong `../../..`) — switched to absolute paths. Both were cheap to recover because the changes
  were still uncommitted and each step was checked before proceeding.

## 2026-09-03 (follow-up) — Reconcile `latex-thesis-zh` / `typst-paper` pointers (option B)

User chose B: those sibling skills don't exist in this repo, so neutralise the dangling references instead of
pointing them elsewhere.

- `paper-audit/scripts/audit.py`: removed `SCRIPTS_ZH` / `SCRIPTS_TYPST`; `_resolve_script` now unifies on
  `[SCRIPTS_EN]` for all formats/languages (this also matches prior effective behaviour: `zh` already fell
  through to EN, and `.typ` always returned None because the dir never existed).
- Removed the `latex-thesis-zh` delegation note from `latex-academic/SKILL.md` description.
- Renamed stale `latex-paper-en` references in `latex-academic` docstrings/comments and fixtures
  (`tex_loader.py`, `analyze_abstract.py`, evals fixture README, `routing-rules.md`, `ai-disclosure.md`),
  and in `paper-audit` docs/comments (TROUBLESHOOTING.md list, `check_references.py`, `tex_loader.py`).
- Kept the `/latex-fmt`, `/latex-polish`, `/latex-rescue` aliases (deliberate; they route to `latex-academic`).

### Reflection
- The first leftover-scan was missing matches: a `grep -v "latex-academic"` filter hid lines whose file *path*
  contained `latex-academic` (git prints `path:line`). Re-scanned without that filter to find the real stale names.
- Reconcile is purely text/path except `audit.py`, which is functional; verified it still imports/compiles.

## 2026-09-04 — Install official PyTRIO skill + fill doc gaps

### Task
User wants the official `SwanHubX/pytrio-skill` installed here, diffed against the official docs
(https://docs.pytrio.com/docs), with missing parts filled in.

### What I did
- Copied the official skill (cloned from github.com/SwanHubX/pytrio-skill @ v0.2.1) into `pytrio-skill/`
  (SKILL.md + 14 references + 11 examples), onto a new branch `feat/pytrio-skill`.
- **Diff vs official docs.** Crawled all 30 sitemap pages; read the API refs (ServiceClient/TrainingClient/
  SamplingClient/RestClient/Datum/ModelInput/AdamParams/SamplingParams), the guides (train/sample/save/resume/
  download/loss_fn/custom_loss/async/vision), and the advanced pages (configuration/datasets/openai/
  compute_logprobs). Found 4 concrete content gaps + 1 doc-index URL bug.
- **Gap 1 — doc-index link bug:** every `docs.pytrio.cn/...` link 301-redirects; the content path
  `https://docs.pytrio.com/docs/content/<route>/content.md` returns 200. Standardised all core/API/example
  table links to `.com` (38 links), corrected the URL-rule example block, fixed 3 leftover `.cn` links in
  `chat-huanhuan.md`/`opsd.md`/`search-r1.md`, and added the missing `环境变量配置` page to the core table.
- **Gap 2 — env/config:** added `references/config.md` (env vars PYTRIO_API_KEY/BASE_URL/ENV/LOG_LEVEL,
  `pytrio.configure(...)`, load order, client config snapshot).
- **Gap 3 — logprobs:** added `references/logprobs.md` (sample() vs compute_logprobs(), return shapes
  `list[float|None]`, first token None, include_prompt_logprobs/topk_prompt_logprobs, OPD teacher-logprob
  alignment).
- **Gap 4 — OpenAI endpoint:** added `references/openai.md` (base_url `https://pytrio.com/api/openai/v1`,
  chat/stream/completions, image-only-Base64 restriction).
- **Gap 5 — RestClient / download weights:** added `references/rest-api.md` (get_checkpoint_archive_url +
  requests download, list checkpoints/runs/sessions, delete_checkpoint).
- Wired the new refs into `SKILL.md` (a new "进阶：配置、logprobs、下载与 OpenAI 部署" section + extra
  routing rows) and into `references/doc-index.md` (capability table + reading notes).

### Notes / open items
- The engine-internal `prefill-cache` and `clock-cycle` pages are conceptual (token/cost accounting); left as
  doc-index pointers rather than dedicated refs, since `dapo.md` already covers token/cost accounting.
- Not pushed; left on `feat/pytrio-skill` for review.

### Reflection
- The official skill's design is "thin references + fetch remote Markdown at runtime". The real gaps are
  where a topic is core enough that relying on a live fetch is fragile (config, OpenAI endpoint, download,
  logprobs semantics) — exactly what agents misread. The `.cn`→`.com` bug was the most silently damaging fix
  (every URI the skill told the agent to open redirected).

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
- The merged skill's reference to `paper-audit`/`latex-thesis-zh`/`nature-*`/`paper2ppt` is intended delegation.

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

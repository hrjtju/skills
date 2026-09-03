# cleveref — 智能交叉引用（\cref 全指南）

> Source: `cleveref.pdf` (v0.21.4, 2018/03/27, Toby Cubitt). This file is the working reference for
> customising `\cref` behaviour in any paper. It lives under `references/latex/`. Load `\usepackage{cleveref}` **last**.

## 1. Why cleveref

Standard \LaTeX\ forces you to hand-write `Eq.~(\ref{eq1})`, `Theorems~\ref{thm1} to~\ref{thm3}`, and every
change (abbrev vs full, "eq"→"equation", theorem→lemma, reorder, range vs list) means editing every reference.
cleveref defines the format **once**, in the preamble, per reference **type**, and applies it automatically. It
also handles multiple labels, sorting, compressing consecutive labels into ranges, and page references.

## 2. Loading & load order

```latex
\usepackage{cleveref}          % put LAST in the preamble
```

- Must be loaded **after** every package that touches the referencing system.
- The only packages loaded **after** cleveref: `hypdvips`, `autonum`.
- With `varioref` + `hyperref` the order must be: `varioref` → `hyperref` → `cleveref`. Wrong order
  silently breaks references (no warning).
- Load `cleveref` **after** all `\newtheorem` definitions are needed for theorem-type inference — but actually
  cleveref auto-detects theorem names from `\newtheorem` only if `ntheorem` or `amsthm` is loaded, so load those too.

## 3. Core commands

| Command | Output (example) | Purpose |
|---|---|---|
| `\cref{eq1}` | `eq. (1)` | Auto name + label, type-aware |
| `\Cref{eq1}` | `Eq. (1)` | The same, capitalised / no abbreviation (start of sentence) |
| `\crefrange{eq1}{eq5}` | `eqs. (1) to (5)` | Reference range |
| `\Crefrange{a}{b}` | `Eqs. (1) to (5)` | Capitalised range |
| `\cref{eq2,eq1,eq3,eq5,thm2,def1}` | `eqs. (1) to (3) and (5), theorem 5, and definition 1` | Multi-reference (auto sort + compress) |
| `\cpageref{lab}` | `page 3` | Page reference |
| `\Cpageref{lab}` | `Page 3` | Capitalised page reference |
| `\cpagerefrange{a}{b}` | `pages 3 to 5` | Page range |
| `\cpageref{a,b,c}` | `pages 1, 3 and 5` | Multiple pages |
| `\namecref{sec1}` / `\nameCref` | `section` / `Section` | Just the reference name (no label). `\namecrefs`/`\nameCrefs` plural; `\lcnamecref` forces lowercase. Single label only. |
| `\labelcref{lab}` | `(1)` | Label without the name (for declensional languages). Accepts multi-refs of same type. `\labelcpageref` = page number only. |

**Starred variants** (`\cref*`, `\Cref*`, `\crefrange*`, `\Crefrange*`): only with `hyperref` — typeset the same
text but **without** creating a hyperlink.

cleveref does **not** touch the standard `\ref` / `\pageref` — you still use them for bare numbers.

**Label restriction:** label names must **not** contain commas `,` (commas separate labels in a multi-reference).

## 4. Package options

| Option | Effect |
|---|---|
| `capitalise` (= `capitalize`) | Always capitalise first letter of names (`Theorem 1` not `theorem 1`). Still use `\Cref` at sentence start (abbrevs shouldn't start sentences). |
| `nameinlink` | Include the cross-reference name inside the hyperlink target (default: label only). Discouraged: multi-refs only the first name can be in the link → non-uniform. Control precisely via `#2…#3`. |
| `noabbrev` | Use full names (`equation (1)` not `eq. (1)`). Start-of-sentence variants never abbreviate by default. |
| `sort` / `compress` / `nosort` / `sort&compress` | List sorting/compression. Default is `sort&compress`. |
| `poorman` | Write a `.sed` script that rewrites your document to plain `\ref` (for venues that can't install cleveref). Run `sed -fname.sed name.tex > new.tex`. Loses hyperlink customisation. |

**Prevent compression of one range:** insert an empty reference where you want the break:
```latex
\cref{eq1,eq2,eq3,,eq4}    % → eqs. (1) to (3) and (4)
```
The empty ref is "attached" to the preceding reference; it forces that reference to appear explicitly even after sort.

## 5. Customising `\cref` — three tiers

Formats are built from **components** (name + label format + conjunctions). Three levels, from coarse to full control.

### 5.1 Level 1 — Global (all types)

```latex
\crefdefaultlabelformat{[#2#1#3]}        % label counter format; #2...#3 = hyperlink span
\newcommand{\crefrangeconjunction}{ and~}   % between start & end of a range (default varies)
\newcommand{\crefrangepreconjunction}{}     % before first label in range (Italian uses "da")
\newcommand{\crefrangepostconjunction}{}    % after second label in range (Italian uses "a")
\newcommand{\crefpairconjunction}{ and~}    % between 2-ref lists
\newcommand{\crefmiddleconjunction}{, }     % between middle refs (default: ", ")
\newcommand{\creflastconjunction}{ and~}    % between penultimate & last
% group variants for lists mixing different types:
\newcommand{\crefpairgroupconjunction}{...}
\newcommand{\crefmiddlegroupconjunction}{...}
\newcommand{\creflastgroupconjunction}{...}
```

**`#1 #2 #3` semantics:** `#1` = formatted label counter (e.g. `\theequation`); `#2`/`#3` = start/end of the
hyperlink region (in that order). Leaving `#2#3` out means no hyperlink target is marked when `hyperref` is loaded.

### 5.2 Level 2 — Per-type (high level)

```latex
\crefname{equation}{eq.}{eqs.}            % singular, plural (for \cref)
\Crefname{equation}{Eq.}{Eqs.}            % capitalised (for \Cref)
\creflabelformat{equation}{(#2#1#3)}       % label format for this type (overrides default)
\crefrangelabelformat{equation}{(#3#1#4) to~(#5#2#6)}   % range format: 6 args
```

- `⟨type⟩` is usually the **counter name** (`equation`, `chapter`, `section`, …). Exceptions: **appendices**
  use `appendix`/`subappendix`/`subsubappendix`; **explicitly overridden** types (see §6); **theorem-like
  environments** use the **environment name** (`lemma`, `corollary`, `definition`) when `ntheorem`/`amsthm` is loaded.
- If `\Crefname` is undefined when you call `\crefname`, cleveref auto-defines it as an upper-cased version
  (`\MakeUppercase`); and vice-versa (`\MakeLowercase`). Only works if the name starts with a letter; wrap accented
  letter constructs in braces. If the first char isn't a letter (a command), define both variants explicitly.
- **Inheritance:** if not customised, `subsection` inherits from `section`, `subsubsection` from `subsection`; and
  `enumii`→`enumi`, `subfigure`→`figure`, `subtable`→`table`, `subequation`→`equation`. If you customise only some
  components, the rest inherit from the parent **as components**; a fully low-level customised parent format is **not** inherited.
- **`\crefrangelabelformat`** (6 args): `#1 #2` = two label counters; `#3 #4` = hyperlink span of first ref;
  `#5 #6` = hyperlink span of second ref.

### 5.3 Level 3 — Low level / full control

```latex
\crefformat{equation}{Eq.~(#2#1#3)}         % single ref (cref); \Crefformat for \Cref
\crefrangeformat{equation}{eqs.~(#3#1#4) to~(#5#2#6)}   % range
\crefmultiformat{equation}{eqs.~(#2#1#3)}%
  { and~(#2#1#3)}{, (#2#1#3)}{ and~(#2#1#3)}           % multi: first/second/middle/last
\crefrangemultiformat{equation}{...}{...}{...}{...}     % multi ranges
```

- Single formats use `#1 #2 #3` (as §5.1). Range formats use `#1–#6`. Multi formats take **five** arguments:
  `⟨first⟩{second}{middle}{last}`; the first/second/middle/last code snippets are concatenated with **no**
  space between them, so put spaces at fragment edges as wanted.
- If the capitalised variant is missing, cleveref auto-defines it; **only the first letter** of `⟨first⟩` is
  upper/lower-cased (the other args stay identical). If `#2` leads the format (hyperlink-span first), auto-caps
  fails — define `\crefformat` and `\Crefformat` both explicitly.
- Formats are real macro bodies → arbitrary TeX processing of the labels (Turing-complete).

**`\labelcref` companion formats** — if you use low-level formats AND want `\labelcref`, also define
`\labelcrefformat`, `\labelcrefrangeformat`, `\labelcrefmultiformat`, `\labelcrefrangemultiformat` (same syntax;
typically identical to `\cref*` but `⟨first⟩` drops the name).

### 5.4 Stripping common prefixes (ranges like `eqs. (1.2.1–3)`)

```latex
\crefrangelabelformat{equation}%
  {(#3#1#4--#5\crefstripprefix{#1}{#2}#6)}
\crefrangelabelformat{subequation}%
  {(#3#1#4--#5\crefstripprefix{#1}{#2}#6)}
```
`\crefstripprefix{strA}{strB}` returns `strB` minus the common prefix (keeping the last run of digits/letters).
For multi-refs, carry the first component's prefix through an auxiliary macro (`\crefstripprefixinfo`).

## 6. Overriding the reference type

```latex
\crefalias{mycounter}{section}      % make mycounter use section's format
\label[specialtype]{mylab}          % one-off type override
```
- `\label[type]{label}` lets you invent a type, then `\crefname{type}...`/`\crefformat{type}...` for just those labels.
- `aliascnt` package: define one counter as alias of another (two names, different formats). Load `aliascnt` **before**
  `cleveref`; put `\newaliascnt` after cleveref.

## 7. Component macros (name + language-switching)

- Names are stored in `\cref@⟨type⟩@name`, `\Cref@⟨type⟩@name`, `\cref@⟨type⟩@name@plural`,
  `\Cref@⟨type⟩@name@plural`. Use `\makeatletter`/`\makeatother`. Use these **in** low-level formats if you want
  babel/polyglossia `\selectlanguage` to still retranslate, e.g.:
  ```latex
  \makeatletter
  \crefformat{equation}{#2\cref@equation@name~(#1)#3}
  \makeatother
  ```
- An **empty** `\crefname{type}{}{}` is retained across language switches (handy to suppress a name).

## 8. Automatic `\newtheorem` names

`\newtheorem` gives enough to auto-name a new theorem-like environment (singular). cleveref uses it **only** if no
cleveref default and no explicit `\crefname`/`\Crefname` exist. It cannot derive the plural — if a plural is needed
you get "reference type undeﬁned" + `?? \ref{…}`; add an explicit `\crefname`/`\Crefname` with both forms.
This is unrelated to auto-detecting the **type** of theorem environments (needs `ntheorem`/`amsthm`).

## 9. Language / babel / polyglossia

- Pass language via cleveref option **or** (recommended) global `\documentclass[lang]{...}` option (auto-propagates).
  Passing to babel **alone** is not enough — cleveref still needs the option.
- **polyglossia:** ignores package options; set `\setdefaultlanguage` **before** loading cleveref. Don't pass options.
- Language switching modifies components only; low-level formats are out of its control (use the component macros of §7).

## 10. cleveref.cfg

Any `cleveref.cfg` found in the TeX search path is auto-loaded → store cross-document format customisations there.

## 11. Gotchas

- Using `\cref` redefines `ntheorem`'s `\thref` → alias of `\cref`; `varioref`'s `\vref`/`\vrefrange`/`\fullref`
  re-delegated to cleveref formatting (still keeps varioref page magic; fixed the `\vref` spacing; `*` variants now
  suppress hyperlinks).
- Unknown type → "reference type undeﬁned" warning, typeset as `?? \ref{label}`; define the type.
- Cleveref checks whether `\crefformat` **definitions** match (identical TeX code) to decide grouping for
  sort/compress — not whether the produced text matches.
- `mathtools` `showonlyrefs` is **incompatible**; use `autonum` instead.
- Broken with `euq`—actually **`eqnarray`** doesn't work properly — use `amsmath` (`gather`/`align`/`multline`/`split`).
- **beamer** redefines `\label` and breaks cleveref's optional arg.
- **subfloat** unsupported — use `\ref` for sub-figures.
- `\label[type]{label}` inside another command's optional arg fails (TeX arg parsing) — wrap in braces:
  `{\label[type]{label}}` (crops up in `memoir` sub-captions).

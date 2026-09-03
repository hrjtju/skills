# TikZ / PGF — 论文插图速查（含 tikz-3dplot、tikz-cd）

> Sources: `pgfmanual.pdf` (PGF/TikZ reference), `tikz-3dplot_documentation.pdf`, `tikz-cd-doc.pdf` (all
> downloaded together). This is a working cheat-sheet for drawing publication figures; for the full command
> catalogue open the `pgfmanual.pdf`. It lives under `references/latex/`.

## 1. Loading

```latex
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc, shapes, decorations.pathmorphing, backgrounds}
```

## 2. Core TikZ (from pgfmanual)

A picture = a set of paths to draw. Every `\draw`/`\path` is one path.

```latex
\begin{tikzpicture}[<options>]
  \draw[<style>] <path spec>;
  \node[<style>] (name) at (<coord>) {<text>};
  \fill[<style>] <path spec>;
\end{tikzpicture}
```

- **Coordinates:** `(0,0)`, `(1.5cm,2)`, polar `(30:1)`, `(1,2) -- (3,4)`, relative `+(1,0)`, `++(1,0)`,
  named `(A)` / `(A |- B)` (intersection).
- **Styles:** line width/shape/color/arrowhead. `[->]`, `[<->]`, `[-stealth]`, `[ultra thick]`, `[dashed]`,
  `[dotted]`, `[blue!50]`, `[rounded corners]`, `[->, >=Stealth]`.
- **Common draws:**
  ```latex
  \draw[->] (0,0) -- (2,0);                  % arrow
  \draw (0,0) rectangle (2,1);               % box
  \draw (0,0) circle (0.5);                  % circle
  \draw (0,0) ellipse (1 and 0.6);           % ellipse
  \draw (0,0) to[out=45,in=135] (1,1);       % bezier curve
  \draw[->] (0,0) .. controls (1,1) .. (2,0);% control points
  ```
- **Nodes & labels:** `\node[circle,draw,fill=blue] (v) at (0,0) {$v$};`
  `\node[above=2pt, anchor=south] {label};`, text along a line with `node[midway,above]{...}`.
- **Scopes & reuse:** wrap in `\begin{scope}[shift={(1,0)}, scale=0.5] ... \end{scope}`.
- **Colors:** named/pgf `/pgf/declare`; mixing `red!30!blue`; `\definecolor`.
- **Libraries to reach for:** `arrows.meta` (arrow tips), `positioning` (`below=of X`), `calc`
  (`($(A)!0.5!(B)$)`), `shapes.geometric`, `decorations.pathmorphing` (snake, brace), `fit`, `matrix`,
  `patterns`, `3d`, `backgrounds`.
- **Math in tikz:** text is math-free by default; wrap in `$...$` for math nodes. Set
  `every node/.style={...}` to style all nodes.
- **Sub-figures in a paper:** one `tikzpicture` per sub-figure (or `\tdplotsetmaincoords` + scope), label then
  `\includegraphics` the compiled PDF, or use standalone `.tex` with `standalone` class +
  `--shell-escape` for `\includegraphics`.

> The pgfmanual is authoritative for every key. For a 3D-looking figure use `tikz-3dplot` (§3); for commutative
> diagrams use `tikz-cd` (§4); for graphs/flow use `graphviz`/`mermaid`/`plantuml` tooling (see `references/tooling/`).

## 3. tikz-3dplot — 3D coordinate systems

`\usepackage{tikz-3dplot}`. Two frames: **main** (defined by `\tdplotsetmaincoords{θd}{φd}`) and **rotated**
(defined by Euler angles). Inside a picture start with a `[tdplot_main_coords]` style.

| Command | Purpose |
|---|---|
| `\tdplotsetmaincoords{θd}{φd}` | Orient main frame (θd = rotation about x, φd = about z). Use as `\begin{tikzpicture}[tdplot_main_coords]`. |
| `\tdplotsetrotatedcoords{α}{β}{γ}` | Euler z(α)y(β)z(γ) rotated frame → `tdplot_rotated_coords` style. |
| `\tdplotsetrotatedcoordsorigin{(P)}` / `\tdplotresetrotatedcoordsorigin` | Move / reset the rotated-origin. |
| `\tdplotsetthetaplanecoords{φ}` | A rotated frame whose x′y′ plane is coplanar to the θ-plane (TikZ draws arcs in the xy plane); auto-resets any origin. `\tdplotsetrotatedthetaplanecoords{φ′}` does it in the current rotated frame. |
| `\tdplotsetcoord{P}{r}{θ}{φ}` | Predefine point `P` in spherical coords + projections `Px,Py,Pz,Pxy,Pxz,Pyz`. **Main frame only** — literal points in rotated frame. |
| `\tdplotgetpolarcoords{x}{y}{z}` | Store `\tdplotresrho,\tdplotrestheta,\tdplotresphi`. |
| `\tdplotcrossprod(ax,ay,az)(bx,by,bz)` | Cross product → `\tdplotresx,\tdplotresy,\tdplotresz`. |
| `\tdplotdefinepoints(v)(a)(b)` | Define vector `v` from points `a`→`b`. |
| `\tdplotdrawarc[coords, styles]{center}{r}{a-start}{a-end}{label opts}{label}` | Draw 3D arcs. Use `[tdplot_rotated_coords]` for rotated frame. |
| `\tdplotdrawpolytopearc[...]{center}{r}{a1}{a2}{a3}` | Arc through multiple points. |
| `\tdplotsphericalsurfaceplot[fillstyle]{θsteps}{φsteps}{function}{line}{fill}{xax}{yax}{zax}` | Parametric spherical surface; `\tdplotsetpolarplotrange{θ0}{θ1}{φ0}{φ1}` / `\tdplotresetpolarplotrange`; `\tdplotshowargcolorguide`. |

**Example — axes + a vector:**
```latex
\tdplotsetmaincoords{70}{110}
\begin{tikzpicture}[tdplot_main_coords]
  \draw[thick,->] (0,0,0) -- (1,0,0) node[anchor=north east]{$x$};
  \draw[thick,->] (0,0,0) -- (0,1,0) node[anchor=north west]{$y$};
  \draw[thick,->] (0,0,0) -- (0,0,1) node[anchor=south]{$z$};
  \tdplotsetcoord{P}{.8}{55}{60}
  \draw[-stealth, color=red] (0,0,0) -- (P);          % vector to P
  \draw[dashed, color=red] (0,0,0) -- (Pxy) (P) -- (Pxy); % projection
\end{tikzpicture}
```

**Known issues:** predefined points don't work in a rotated frame; `node ... shift=(P)` can misfire; PGF's own `xyz spherical` differs.

## 4. tikz-cd — commutative diagrams

`\usepackage{tikz-cd}` and `\begin{tikzcd}[<opts>] ... \end{tikzcd}`. Everything inside is math mode. Define
nodes `A & B \\ C & D` (cells), arrows `\arrow[<opts>]` (= `\ar`).

```latex
\begin{tikzcd}
  A \arrow[r, "\phi"] \arrow[d, red] & B \arrow[d, "\psi", red] \\
  C \arrow[r, red, "\eta", blue]     & D
\end{tikzcd}
```

- **Directions:** `r,l,u,d` and diagonals `dr,ru,lu,ld` etc. `&` / `\\` separate cells (or `\NC`/`\NR`).
- **Labels:** `"text"` (wrap in `{}` if it has commas); options like `'` (opposite side),
  `near start`, `near end`, `description` (breaks the line). Multiple labels by repeating `"..."`.
- **Arrow tips** (named like TikZ or after TeX arrows, no backslash): `rightarrow`, `leftrightarrow`,
  `Rightarrow`, `Leftrightarrow`, `mapsto`, `Mapsto`, `hook`, `hook'`, `hookrightarrow`, `hookleftarrow`,
  `rightarrowtail`, `twoheadrightarrow`, `twoheadleftarrow`, `dashed`, `dashrightarrow`, `dashleftarrow`, `dash`.
  Compose: `\arrow[r, tail, two heads, dashed]`.
- **Keys:** `bend left`, `bend right`, `bend left=20`, `dotted`, `dashed`, `color=...`, `line width=...`,
  `loop`, `in=`/`out=`, `shorten`, `phantom` (spacing only).
- **Spacing:** `\begin{tikzcd}[row sep=..., column sep=...]`; global via `\tikzcdset{row sep/normal=1cm}`.
  Available sizes: `tiny`, `small`, `normal`, `large`, `huge`. `row sep=huge` etc.
- **Big examples:** pushdown / pullback corners with `\arrow[drr, bend left, "x"]`, `\arrow[ddr, bend right]`.

## 5. Where each tool fits

| Task | Use |
|---|---|
| Scatter/line/bar of data | `references/tooling/python-charts.md` / `references/tooling/charts-and-graphs.md` (matplotlib → pgf) |
| Pure schematic / architecture | TikZ core (§2) |
| 3D axes / vectors / spherical surfaces | tikz-3dplot (§3) |
| Commutative / category diagrams | tikz-cd (§4) |
| Flowchart / graph layout | graphviz / plantuml (`references/tooling/graphviz-plantuml.md`) |
| Mind-map / sequence (web-scale) | mermaid (`references/tooling/mermaid-diagrams.md`) |

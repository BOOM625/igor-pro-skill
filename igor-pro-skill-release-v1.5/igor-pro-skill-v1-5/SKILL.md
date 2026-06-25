---
name: igor-pro-skill-v1-5
description: General-purpose Igor Pro automation for data handling, wave/table workflows, command/procedure generation, editable graphs/layouts, Nature-style publication figures, PieChart/category/stacked plots, ErrorBars/SHADE bands, common scientific figure smoke tests, PXP/ITX deliverables, high-DPI exports, and troubleshooting. Use when Codex needs to call Igor Pro or help users import/export data, build or debug Igor commands, manipulate waves, create publication-ready editable figures, save experiments, verify outputs, search local Igor help, or avoid Igor automation issues with Windows paths, wave conflicts, graph traces, annotations, layouts, SavePICT, SaveExperiment, and modal/license UI.
---

# Igor Pro Skill v1.5

Use this as a general-purpose Igor Pro automation skill. It covers data
handling, wave/table/data-folder workflows, command and procedure generation,
file import/export, editable graphs and layouts, publication figure styling,
ITX/PXP handoffs, high-DPI graphics export, and debugging.

Plotting is a first-class workflow, but it is not the only workflow. For
version-sensitive syntax, use the local Igor help corpus as the source of truth
before writing unfamiliar commands.

## Quick Workflow

1. Classify the Igor task: data import/export, wave/table/data-folder work,
   command/procedure generation, graph/layout creation, PXP/ITX deliverable,
   graphics export, or error debugging.
2. Inspect user-provided inputs first. For Excel, list sheets and columns; for
   CSV, inspect headers and numeric validity. If data is absent, simulate clearly
   labeled data only when the user asks or when it is necessary for a demo.
3. For manuscript or Nature-style figures, define the figure contract before
   plotting: one-sentence conclusion, evidence hierarchy, archetype, panel map,
   final size/export bundle, statistics/source-data needs, and reviewer risks.
   Drop panels that do not support a unique piece of evidence.
4. Search the local help corpus before writing unfamiliar Igor syntax:
   `scripts/igor_ref_search.py "<query>"`.
5. Choose the file format: use `.itx` for data plus commands; use `.ipf` for
   reusable procedures/functions; use `.pxp` for saved experiments; use native
   Igor waves/tables/graphs/layouts for editable deliverables. For repeatable
   automation that may run in an existing Igor session, prefer `Make/O` command
   wave creation over `WAVES/D ... BEGIN` blocks to avoid modal name conflicts.
6. Use standard safe Igor object names: letters, digits, underscores; start with
   a letter. Avoid names such as `Time` that collide with Igor functions.
7. For graph tasks, choose the data model: waveform plots with `SetScale` for
   uniformly spaced X; XY plots (`Y vs X`) for explicit or irregular X values;
   text waves for native category plots; and the bundled `<PieChart>` package for
   standard editable 2D pie charts. If the user asks for a final layout or
   separate panels, create real graph windows first and append those graph
   objects into a `NewLayout`; do not simulate multiple panels by drawing axes in
   one dummy graph unless the user explicitly wants a single hand-drawn graph.
8. Apply the default graph style unless the user specifies otherwise: outward
   ticks (`tick=0`; Igor's `tick` values are `0=Outside`, `1=Crossing`,
   `2=Inside`, `3=None`), font size 12 (`fSize=12`), and axis thickness 2
   (`axThick(left)=2, axThick(bottom)=2`). Do not create a title text box by
   default; add an editable legend unless the user asks to hide it.
9. For Nature-style layouts, override the generic style with smaller final-size
   typography, left/bottom axes only where appropriate, frameless/shared legends
   or direct labels, restrained semantic palettes, and one hero panel plus
   quieter support panels when the evidence hierarchy calls for it.
10. Launch `.itx` files using Windows short paths or a no-space temporary path.
   Avoid passing long Windows paths with spaces to Igor startup arguments. Also
   use short-path Igor colon paths for `SavePICT` and `SaveExperiment`; startup
   safety alone does not make later save commands safe.
11. Verify the requested artifact: table/waves exist, procedures compile, graphs
   are editable, experiments save, or exported images have the requested format,
   DPI, dimensions, and nonblank pixels. For layouts, inspect a preview image for
   cropping, panel overlap, missing graph objects, and non-rendered helpers.
12. For smoke tests or broad plotting QA, generate ten small native figure
    windows first, then assemble them in a layout: line+band, scatter+fit,
    bar+error, grouped bar, stacked bar, histogram, box+jitter, heatmap,
    contour, and PieChart package pie.

## Local Help References

Read these only when needed:

- `references/igor-help-map.md`: how to search Igor's installed `.ihf` help
  files and task routing for common Igor topics.
- `references/igor-automation-notes.md`: distilled rules for commands, waves,
  graphs, category plots, annotations, layouts, files, and export.
- `references/nature-style-igor.md`: use when the target is Nature-style,
  high-impact, manuscript, SCI, or journal-ready figures in Igor Pro.

Search helper:

```powershell
python "<skill-dir>\scripts\igor_ref_search.py" "Stacked Bar Charts" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "Annotation Text Escape Codes" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "Saving as a Packed Experiment File" --limit 8
```

The search helper auto-detects help files in this order: `--ref-dir`,
`IGOR_REF_DIR`, a bundled/local `igor ref` directory near the skill or current
workspace, then the Igor installation discovered from `IGOR_EXE`, PATH, the
Windows uninstall registry, common `Program Files\WaveMetrics` locations, or
drive-root Igor installation folders. If discovery fails, ask the user to
set `IGOR_REF_DIR` to the Igor install root or its `Igor Help Files` folder.

Use the search helper before writing unfamiliar `ModifyGraph`, category plot,
layout, HDF5, data import/export, or experiment-save syntax.

## General Igor Pro Tasks

- For command or procedure requests, prefer a small `.itx` command runner for
  one-off work and an `.ipf` file for reusable functions or menus. Keep procedure
  code minimal and compile-friendly.
- For data work, preserve raw waves when possible and create derived waves with
  clear names. Use data folders for larger workflows instead of piling unrelated
  waves into `root:`.
- For table deliverables, create editable Igor tables with `Edit/N=<tableName>`.
- For debugging, reproduce the smallest failing command, search the exact error
  text or command name in local help, then patch the command/procedure.
- Do not force a graph when the user asks for non-plot Igor work such as data
  conversion, wave manipulation, procedure creation, experiment saving, or help
  lookup.

## Helper Script

For a simple Excel/CSV X/Y line plot and TIFF export, use the copied helper:

```powershell
& "<python.exe>" "<skill-dir>\scripts\igor_xy_plot.py" `
  --input "C:\path\data.xlsx" `
  --x-col Time `
  --y-col Signal `
  --fallback-x-col X `
  --fallback-y-col Y `
  --x-label "Time (s)" `
  --y-label "Intensity (a.u.)" `
  --output "C:\path\figure.tif" `
  --dpi 600
```

The helper finds Igor, reads Excel/CSV, creates a self-contained `.itx`, launches
Igor by safe path, exports TIFF, and verifies image metadata. Use `--sheet` for
multi-sheet workbooks and `--no-sort-x` when row order is meaningful.

## Manual Plot ITX Pattern

Use `.itx` for robust command/data transfer:

```igor
IGOR
WAVES/D PlotXWave, PlotYWave
BEGIN
0    1.0
1    1.7
2    1.2
END
X DoWindow/K PlotFigure
X Display/N=PlotFigure PlotYWave vs PlotXWave
X ModifyGraph/W=PlotFigure mode(PlotYWave)=0,lsize(PlotYWave)=2,rgb(PlotYWave)=(0,0,0)
X ModifyGraph/W=PlotFigure mirror=2,tick=0,axThick(left)=2,axThick(bottom)=2,standoff=0
X ModifyGraph/W=PlotFigure fSize=12,font="Arial"
X Label/W=PlotFigure bottom "Time (s)"
X Label/W=PlotFigure left "Intensity (a.u.)"
X Legend/C/N=legend0/J/F=0/A=RT "\s(PlotYWave) Signal"
X SetAxis/W=PlotFigure/A
```

Launch by short path, for example:

```powershell
$env:IGOR_EXE="C:\Program Files\WaveMetrics\Igor Pro 10 Folder\IgorBinaries_x64\Igor64.exe"
& "$env:IGOR_EXE" "C:\SHORTPATH\PLOT_F~1.ITX"
```

The helper scripts try to find Igor automatically from `--igor-exe`,
`IGOR_EXE`, PATH, the Windows uninstall registry, common WaveMetrics install
locations, and drive-root Igor installation folders.

## Repeatable ITX Data Builds

Use command-created waves when an `.itx` may be opened more than once in the
same Igor session or when automation is generating many editable waves. `WAVES/D
... BEGIN` blocks are compact, but Igor can show a modal name-conflict dialog
while loading incoming waves, before cleanup commands can run.

Prefer a data folder plus `Make/O` for rerunnable automation:

```igor
IGOR
X SetDataFolder root:
X NewDataFolder/O/S root:PackageName
X Make/O/D/N=(4) PlotX
X Make/O/D/N=(4) PlotY
X PlotX[0]=0.1; PlotY[0]=0.08
X PlotX[1]=1;   PlotY[1]=0.7
X PlotX[2]=10;  PlotY[2]=7
X PlotX[3]=100; PlotY[3]=80
```

Rules for repeatable generated figures:

- Put task-specific waves in a named data folder rather than piling everything
  into `root:`.
- Use `Make/O` or `Duplicate/O` for generated waves. Avoid relying on
  `KillWaves` to prevent loader conflicts from incoming `WAVES` blocks.
- Close same-named windows before recreating them:
  `DoWindow/K PanelA; DoWindow/K FinalLayout`.
- If a previously opened Igor experiment prevents a rerun from consuming a new
  `.itx`, stop only the Igor process started for this task and relaunch from the
  no-space copy. Do not kill unrelated user Igor sessions.
- Keep raw data waves and display-helper waves separate so the user can edit
  source data without reverse-engineering geometry helpers.

## Editable Native Figures

Use native waves/traces when the user wants to adjust the graph in Igor.

- Unless the user requests different styling, every generated graph should use
  outward ticks, 12-point text, and 2-point axes:
  `ModifyGraph/W=<window> tick=0,fSize=12,axThick(left)=2,axThick(bottom)=2`.
- Add a named editable legend by default, for example
  `Legend/C/N=legend0/J/F=0/A=RT "\s(traceName) Label"`, executed while
  the target graph is active.
  Do not add an in-graph `TextBox` title by default. Use titles, panel labels,
  or other text boxes only when the user requests them or the figure layout
  requires labels such as `(a)`, `(b)`, `(c)`.
- Create graph windows with `Display/N=<window>` and append traces with
  `AppendToGraph/W=<window>`.
- Open an edit table when useful:
  `Edit/N=<tableName> wave1, wave2, wave3`.
- Use named annotations (`Legend/C/N=...`, `TextBox/C/N=...`) so generated text
  can be replaced.
- Treat `TextBox /G=(r,g,b)` as text color in generated annotations, not as a
  safe background-fill instruction. Use it deliberately, for example white panel
  letters on a dark image/contour panel; do not apply it to every panel label.
- A PXP containing only an imported PNG/TIFF is not an editable Igor graph. Use
  native waves/graphs first, then let Igor save the experiment or provide the
  `.itx` for the user to open and save.

## Nature-Style Manuscript Figures

Use `references/nature-style-igor.md` for Nature-style or high-impact journal
figures. Apply the figure logic before Igor syntax:

- Write the core conclusion and panel evidence map before generating waves or
  graph windows.
- Classify the layout as `quantitative grid`, `schematic-led composite`,
  `image plate + quant`, or `asymmetric mixed-modality figure`.
- Prefer one dominant hero panel plus smaller validation/control panels when the
  evidence hierarchy is asymmetric. Do not force equal-sized panels.
- Keep charts on white backgrounds; use black only inside microscopy/image
  plate regions.
- Use one neutral family, one signal family, and one accent family. Keep the same
  condition/method color across all panels.
- Prefer direct labels or one shared legend strip over repeated legends inside
  every panel.
- Treat `n`, error-bar definitions, statistical tests, source data, and image
  integrity notes as part of the figure QA, not as caption cleanup.
- Save editable Igor deliverables (`.itx`/`.pxp`) plus raster/vector exports
  requested by the user. Igor's PXP is the editable source; TIFF/PNG is only the
  preview/export.

For editable stacked bars, prefer native category plots first. If the figure
needs precise rectangle geometry, keep the original data waves separate from
display-helper waves. Build each segment from descriptive boundary waves, expand
each category into `left, left, right, right, NaN`, repeat each boundary value,
set `gaps=1`, and fill each upper boundary trace to the next lower trace:

```igor
X Display/N=StackedBarFigure TreatmentTop vs CategoryX
X AppendToGraph/W=StackedBarFigure ControlTop vs CategoryX
X AppendToGraph/W=StackedBarFigure Baseline vs CategoryX
X ModifyGraph/W=StackedBarFigure mode(TreatmentTop)=7,toMode(TreatmentTop)=1,hbFill(TreatmentTop)=2,lsize(TreatmentTop)=0
X ModifyGraph/W=StackedBarFigure mode(ControlTop)=7,toMode(ControlTop)=1,hbFill(ControlTop)=2,lsize(ControlTop)=0
X ModifyGraph/W=StackedBarFigure lsize(Baseline)=0,rgb(Baseline)=(65535,65535,65535),gaps=1
```

In final user-facing explanations, describe the relationship in domain terms
such as "original data waves" and "display-helper boundary waves"; avoid exposing
temporary helper names unless the user needs to edit those specific waves.

## Layouts And Multi-Panel Figures

When the user asks for separate panels assembled into one final figure, create
real Igor graph windows first, then place those graph objects into a layout.
This keeps each panel and all underlying waves editable.

```igor
X DoWindow/K PanelA
X Display/N=PanelA PlotY_A vs PlotX_A
X ModifyGraph/W=PanelA log(bottom)=1,log(left)=1

X DoWindow/K PanelB
X Display/N=PanelB PlotY_B vs PlotX_B
X ModifyGraph/W=PanelB log(bottom)=1,log(left)=1

X DoWindow/K FinalLayout
X NewLayout/N=FinalLayout/W=(25,25,835,855) as "Final editable layout"
X AppendLayoutObject/F=0/T=0/R=(20,18,252,238) Graph PanelA
X AppendLayoutObject/F=0/T=0/R=(278,18,510,238) Graph PanelB
```

Layout rectangle coordinates are page points, not export inches. If exporting
with `SavePICT/I/W=(0,0,7.2,7.2)`, the page is about `7.2*72 = 518.4` points
wide and tall. Rectangles such as `R=(530,...,775,...)` will crop out of that
export. Keep layout objects inside the page bounds or increase the `SavePICT`
width and height. Always `DoWindow/F <layout>` before `SavePICT`, then inspect a
preview image for cropped panels, overlap, missing objects, and unexpectedly
blank margins.

Do not recreate multi-panel scientific figures by drawing axes, labels, and
points into one dummy graph unless the user explicitly asks for a purely drawn
mockup. Drawn objects are hard to edit as data and usually do not satisfy
"editable Igor figure" requests.

## ErrorBars SHADE Comparison Bands

For 1:1 comparison bands on log-log scatter plots, prefer a central 1:1 trace
with `ErrorBars ... SHADE` envelopes. This creates smooth editable bands tied to
data waves and avoids many diagonal helper traces or thick drawn lines.

For a central line `BandY = BandX`:

- A 5:1 outer band uses upper error `4*BandY` and lower error `0.8*BandY`.
- A 2:1 inner band uses upper error `1*BandY` and lower error `0.5*BandY`.
- Use dense log-spaced samples for `BandX`/`BandY` so the shaded band is smooth.

Use the Igor 9.02-compatible ordering shown below. The `SHADE={...}` clause
comes directly after the trace name, before `wave=(...)`:

```igor
X AppendToGraph/W=PanelA OuterBand_Y vs Band_X
X AppendToGraph/W=PanelA InnerBand_Y vs Band_X
X ErrorBars/W=PanelA/T=0/L=3 OuterBand_Y SHADE={0,0,(0,0,0,0),(0,0,0,0)},wave=(OuterPlus_Yerr,OuterMinus_Yerr)
X ErrorBars/W=PanelA/T=0/L=3.2 InnerBand_Y SHADE={0,0,(0,0,0,0),(0,0,0,0)},wave=(InnerPlus_Yerr,InnerMinus_Yerr)
```

The trace should normally be styled as the middle line, while the shaded error
area supplies the comparison band:

```igor
X ModifyGraph/W=PanelA rgb(OuterBand_Y)=(36000,36000,36000),lsize(OuterBand_Y)=1.8
X ModifyGraph/W=PanelA rgb(InnerBand_Y)=(36000,36000,36000),lsize(InnerBand_Y)=0
```

Avoid forms such as `ErrorBars trace shade=...` or moving `Y,wave=(...)` after
`SHADE`; Igor Pro 9.02 can report `ErrorBars Error: unknown keyword`. If the
installed Igor version or graph context still rejects `SHADE`, fall back to a
plain `ErrorBars` command with dense samples and no caps, or use a small number
of native filled helper traces, and state the fallback clearly.

## Standard 2D Pie Charts

When the user asks for a standard editable pie chart, use Igor's bundled
`<PieChart>` package rather than importing a bitmap or manually approximating
wedges in an unrelated graph. The package draws wedges and labels in an Igor
graph window using the PieChart procedure, stores pie metadata in the graph, and
keeps the numeric data wave, label wave, and color wave editable in Igor.

Search local help before changing this pattern:

```powershell
python "<skill-dir>\scripts\igor_ref_search.py" "PieChartForProgrammers" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "ModifyPieChart" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "2D Pie Chart Procedure" --limit 8
```

For `.itx` automation, insert and compile the package, then queue the module
calls with `Execute/P/Q/Z`. Do not call `PieChartForProgrammers()` directly in
the same ITX command stream before the package has compiled.

```igor
IGOR
X SetDataFolder root:
X NewDataFolder/O/S root:PieFigure
X Make/O/D/N=(3) PieValues
X Make/O/T/N=(3) PieLabels
X Make/O/U/W/N=(3,3) PieColors
X PieValues[0]=40; PieLabels[0]="40%"
X PieValues[1]=35; PieLabels[1]="35%"
X PieValues[2]=25; PieLabels[2]="25%"
X PieColors[0][0]=60000; PieColors[0][1]=20000; PieColors[0][2]=20000
X PieColors[1][0]=20000; PieColors[1][1]=50000; PieColors[1][2]=20000
X PieColors[2][0]=20000; PieColors[2][1]=20000; PieColors[2][2]=60000
X DoWindow/K PieGraph
X Display/N=PieGraph/W=(40,40,500,520)
X Execute/P/Q/Z "INSERTINCLUDE <PieChart>"
X Execute/P/Q/Z "COMPILEPROCEDURES "
X Execute/P/Q/Z "WMPieChart#PieChartForProgrammers(\"PieGraph\", root:PieFigure:PieValues, \"_wave_\", root:PieFigure:PieLabels, pieRadius=0.31, labelRadius=0.20, centerX=0.5, centerY=0.5, startAngleDegrees=270, ccw=1, fontName=\"Arial\", fontSize=14, quiet=1)"
X Execute/P/Q/Z "WMPieChart#ModifyPieChart(\"PieGraph\",\"customColors\",stringValue=\"root:PieFigure:PieColors\",numValue=1)"
X Execute/P/Q/Z "Edit/N=PieData root:PieFigure:PieValues, root:PieFigure:PieLabels, root:PieFigure:PieColors"
```

Useful programmer interface facts:

- `#include <PieChart>` creates the regular module `WMPieChart`; use qualified
  names such as `WMPieChart#PieChartForProgrammers(...)` and
  `WMPieChart#ModifyPieChart(...)`.
- `PieChartForProgrammers(graphName, dataWave, labelsMethod, labelsTextWave,
  ...)` accepts label methods such as `_wave_`, `_value_`, `_percent_`,
  `_percent_and_tenths_`, and `_none_`.
- `ModifyPieChart` controls custom colors, stroke, label font, label color,
  wedge radius, center, explosion distance, outlines, and background.
- Custom color waves are `N x 3` unsigned 16-bit waves with RGB values in
  Igor's 0-65535 range.
- The official 2D PieChart package uses the `ProgFront` drawing layer and named
  annotations. That is still an editable Igor pie chart, not a pasted bitmap.
  Tell the user they can edit waves/tables and also use drawing mode to select
  wedge objects or annotation text.

Rules for reproducible editable pie charts:

- Keep source values, uncertainties, source names, inner labels, and colors in
  named waves, and open an editable table with `Edit/N=...`.
- Use the PieChart package for wedges, and use named `TextBox` annotations for
  external labels, panel letters, and total-value callouts. Named annotations
  are easier to adjust later.
- Queue `TextBox`, `SavePICT`, and `SaveExperiment` after PieChart creation
  when they depend on the package output.
- For annotation text inside an `Execute/P` string, escape Igor backslashes and
  quotes: write `\"\\Z12\\f01Label\\rLine2\"` in the ITX so Igor ultimately sees
  `"\Z12\f01Label\rLine2"`.
- Avoid raw non-ASCII text such as `±` in `.itx` unless the encoding is known and
  verified. Use ASCII `+/-`, or generate/verify a UTF-8 procedure if exact
  symbols are required.
- Verify the export with a raster preview and confirm the PXP contains the data
  waves and PieChart graph. A TIFF/PNG preview is only the export; the PXP/ITX is
  the editable deliverable.

## Category Plots

For simple bars with category labels, prefer native category plots: numeric wave
versus text wave. Keep numeric waves on identical point scaling unless deliberate
offsetting is required. When category plots look wrong, search:

```powershell
python "<skill-dir>\scripts\igor_ref_search.py" "Category Plot Pitfalls" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "Stacked Bar Charts" --limit 8
```

Category label strings can use annotation escape codes such as `\r` for
multiline labels.

## Common Figure Smoke Tests

For broad skill validation, make a compact native-graph suite with simulated
data. Keep every panel editable and assemble real graph windows into a layout:

1. Line plot with `ErrorBars ... SHADE` uncertainty band.
2. XY scatter plot with `CurveFit line ... /D`.
3. Category bar plot using a text wave plus `ErrorBars`.
4. Grouped category bars with two traces and separate SEM waves.
5. Stacked bars from cumulative boundary waves, not a bitmap.
6. Histogram-like bars from editable bin-boundary waves.
7. Box-and-jitter plot from source points plus helper boundary waves.
8. Heatmap using `AppendImage` on a scaled matrix wave.
9. Contour plot using `AppendMatrixContour` plus optional image underlay.
10. Standard pie chart using `<PieChart>` and `Execute/P/Q/Z` package calls.

For this smoke test, also save a PXP and a raster overview. Verify the overview
with an external image reader for format, pixel size, DPI, and nonblank extrema,
then inspect the PNG preview for missing panels, axis clipping, unreadable panel
letters, and legends that show literal escape text.

## Annotations And Escapes

Igor annotation and legend text uses backslash escapes such as `\Z`, `\f`,
`\s(trace)`, and `\r`. When writing `.itx`, escape quotes but do not double-escape
Igor backslashes. Double escaping makes Igor display literal `\r` or `\s(...)`.
For sub-10 point annotation sizes, use two digits such as `\Z08` and `\Z07`;
Igor 9 can render one-digit forms such as `\Z8` as literal escape residue.
Exception: when an annotation command is itself inside an `Execute/P` string, the
outer string consumes one escape layer. In that case write doubled backslashes in
the ITX command text, for example
`Execute/P/Q/Z "TextBox/W=Graph/C/N=Label \"\\Z12\\f01Line1\\rLine2\""`.

If a generated legend displays visible `\r` or `\s(...)` markers, simplify the
legend to one line or regenerate the `.itx` with the correct escape layer. When
layout space is tight, short single-line legends are usually more robust than
multi-line legends.

## Export And PXP

- For TIFF export, use `SavePICT/E=-7/RES=<dpi>/I/W=(0,0,<width>,<height>)/O as "<igor-colon-path>"`.
- Build `<igor-colon-path>` from a Windows short path when the workspace or file
  parent contains spaces. A safe startup path does not protect later save
  commands from long paths with spaces.
- If `SavePICT` is unreliable with a long leaf name, export to a short temporary
  name in a short-path folder, verify, then rename outside Igor.
- For packed experiments, use `SaveExperiment as "<igor-colon-path>"` with a
  short temporary output name. Do not use `SaveExperiment/O`. Do not use
  `SaveExperiment/F=1`; `/F` expects a brace argument and normal packed PXP save
  does not need it.
- If Igor shows license or modal UI that blocks automation, stop and provide the
  `.itx`/data files instead of trying to bypass the dialog.

## Error Avoidance

- `Error -43 trying to open a file specified in start-up command`: Igor split a
  path with spaces or saw a malformed colon path. Relaunch with a short path.
- Export succeeds in an old run but not after regenerating `.itx`: check whether
  the new `SavePICT`/`SaveExperiment` paths are short-path Igor colon paths, and
  whether an existing Igor process is ignoring or blocking the startup file.
- `name "Time" already exists as a string function`: rename the internal wave;
  keep `Time (s)` only as a label.
- Modal `Name Conflict` while loading a generated `.itx`: the incoming wave name
  already exists or is illegal. Rebuild the ITX with a task-specific data folder
  and `Make/O` command-created waves instead of `WAVES/D ... BEGIN` blocks, or
  use unique wave names. Avoid repeatedly opening data-block ITX files into
  `root:` during automation.
- `SetDrawEnv Error: expected number between 0 and 10`: a drawing attribute such
  as `linethick` is out of range. Do not fake wide comparison bands with one
  oversized drawn line. Use native traces plus `ErrorBars ... SHADE` or
  bounded-width helper traces.
- `ErrorBars Error: unknown keyword`: check the local help and command ordering.
  In Igor Pro 9.02, `ErrorBars/W=<graph>/T=0/L=<n> <trace> SHADE={...},wave=(plus,minus)`
  is safer than variants that put `shade=` or `Y,wave=(...)` in different
  positions.
- `got "PieChartForProgrammers" instead of a string variable or string function
  name`: Igor has not resolved the PieChart procedure module in the current ITX
  command context. Insert and compile `<PieChart>`, then call the function as
  `WMPieChart#PieChartForProgrammers(...)` through `Execute/P/Q/Z`.
- `unknown/inappropriate name or symbol` after switching to
  `WMPieChart#PieChartForProgrammers`: the direct command was parsed before the
  included module was compiled, or the module function was used without proper
  queued execution. Queue `INSERTINCLUDE <PieChart>`, `COMPILEPROCEDURES`, the
  PieChart calls, dependent `TextBox` annotations, `SavePICT`, and
  `SaveExperiment` in order with `Execute/P/Q/Z`.
- A "standard pie chart" request is not satisfied by a pasted preview image.
  Use the 2D PieChart package with editable data waves and a PXP/ITX handoff.
  The package draws on `ProgFront`; that is editable in Igor drawing mode and is
  linked to PieChart metadata, unlike a bitmap.
- `.ipf` plus `/I` plus `/X` context can be unreliable. Prefer a self-contained
  `.itx`, or pass one complete `/X` command only for very small tasks.
- If a graph is not editable, inspect whether it is a bitmap, drawing object, or
  layout picture. Regenerate as waves/traces when editability matters.
- If panel labels vanish after adding `/G`, remember that `/G` changes text
  color for annotations. Remove it on light backgrounds or use it only where a
  contrasting text color is required.
- If Igor automation fails to produce the expected files, inspect whether a
  modal dialog or hidden Igor process is blocking execution. Stop only the Igor
  process started for this task, relaunch from a no-space temporary path, and
  keep the generated `.itx` available for manual opening.

## Completion Checklist

- Output `.itx`, `.ipf`, `.pxp`, data file, table, graph/layout, and/or image
  exists at the requested path.
- Editable deliverables use native Igor waves/tables/traces/layout objects when
  useful.
- Exported images are verified for format, DPI, dimensions, and nonblank pixels.
- Layout previews are checked for clipped axes/traces, missing panels, invisible
  panel labels, visible annotation escape text, and legends covering data.
- Final response states where the files are and any important relationship
  between original data waves and display-helper waves in user-facing terms.

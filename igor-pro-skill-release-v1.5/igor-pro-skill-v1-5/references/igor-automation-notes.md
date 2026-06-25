# Igor Automation Notes

These notes distill the local Igor Pro help corpus for Igor automation. Search
the source files when exact syntax is uncertain.

## Command And Name Safety

- Igor commands can be typed interactively or executed from notebooks/procedures.
  Long generated commands are fragile; split complex work into multiple commands.
- Standard Igor object names should start with a letter and use letters, digits,
  and underscores. Prefer standard names for automation.
- Liberal wave and folder names can contain spaces but must be quoted with single
  straight quotes in Igor commands. Avoid them in generated code unless the user
  already has such objects.
- Refer to waves in other folders with explicit paths such as
  `root:folder:wave` or `root:'Background Curves':wave`.
- The graph/window name is the command target; the window title is only display
  text. Use stable `DoWindow/K <name>` and `Display/N=<name>`.

## Waves And Data Models

- Use the waveform model (`Display yWave`) for uniformly spaced X values. Set X
  scaling with `SetScale` so Igor knows the physical X values and units.
- Use the XY model (`Display yWave vs xWave`) when X values are irregular or when
  the user provides explicit X data. X scaling is ignored for XY pairs.
- If X and Y waves have different lengths in an XY plot, Igor plots the shorter
  paired length; validate lengths before graphing.
- `Make/O` overwrites the wave and does not preserve old values. Use it only when
  regenerating known waves; use `Duplicate` or `Redimension` when preserving data
  matters.
- Text waves (`Make/T`) are required for native category plots.

## Graphs And Traces

- Igor graphs are data-linked: when a wave changes, graphs using the wave update.
  This is the main reason to prefer native waves/traces over bitmaps.
- Graphs can contain waveform plots, XY plots, category plots, image plots,
  contour plots, axes, annotations, drawing objects, controls, and cursors.
- A trace is the visual representation of a wave or XY pair. Default trace names
  follow the Y wave name; repeated instances become `wave#1`, `wave#2`, etc.
- Create a blank graph with `Display` when appending traces later.
- Use `AppendToGraph` for more traces and `RemoveFromGraph` to remove traces.
- Axes are tied to traces. Removing the last trace that uses an axis can remove
  the axis. Use named/free axes only when needed, and avoid spaces in axis names.
- Use `SetAxis/A` for autoscaling and explicit `SetAxis left min,max` or
  `SetAxis bottom min,max` for deterministic exports.
- Default generated graph styling should use outward ticks (`tick=0`; Igor's
  `tick` keyword uses `0=Outside`, `1=Crossing`, `2=Inside`, `3=None`),
  12-point text (`fSize=12`), and 2-point axes
  (`axThick(left)=2, axThick(bottom)=2`) unless the user specifies otherwise.
- Add a named legend by default, for example
  `Legend/C/N=legend0/J/F=0/A=RT "\s(traceName) Label"`. Do not add a graph
  title text box by default.

## Category And Bar Plots

- A category plot is numeric Y data versus a text wave. The category axis labels
  come from the text wave.
- The text wave X scaling is ignored. The numeric value waves' X scaling controls
  category positions, so keep numeric waves on identical point scaling unless a
  deliberate offset is needed.
- Category label strings can use the same escape codes as annotation text; `\r`
  makes multiline labels.
- Stacked bar charts depend on trace drawing order and each trace's relation to
  the next trace. When bars look wrong after reordering, revisit grouping modes.
- Native category plot grouping modes include none/side-by-side, draw to next,
  add to next, and stack on next. Prefer true category plots for simple grouped
  bars. For highly controlled editable stacked rectangles, the trace-boundary
  technique in `SKILL.md` is more deterministic.
- Use `AppendToGraph/NCAT` only when intentionally combining numeric traces with
  an existing category plot.

## Annotations, Legends, And Escape Codes

- Use `TextBox`, `Legend`, `Tag`, and `ColorScale` for annotations that remain
  editable in Igor.
- Use named annotations (`/N=<name>`) so they can be replaced or modified.
- Igor annotation text uses backslash control codes such as `\Z` for size, `\f`
  for font style, `\s(trace)` for a legend symbol, and `\r` for a new line.
- When writing `.itx`, escape quotes but do not double-escape Igor backslashes.
  Double escaping turns `\r` or `\s(trace)` into literal text.
- When an annotation command is queued inside `Execute/P`, the outer string
  consumes one escape layer; double the Igor backslashes in that queued string.
- Treat `TextBox /G=(r,g,b)` as annotation text color, not as a general
  background-fill setting. Use it only when the text color needs to contrast
  with the panel background.
- Avoid in-graph `TextBox` titles by default. Add them only when explicitly
  requested or when a panel label such as `(a)` is part of a multi-panel figure.

## Layouts And Multi-Panel Figures

- Use page layouts for multi-panel publication figures, combining graphs, tables,
  annotations, pictures, and drawing elements.
- Graph/table/layout objects in a layout can update when their source windows
  change. This is useful for editable deliverables.
- Use layout export when multiple graph windows need exact placement. Use a
  single graph window with subwindows only when interactivity or shared axes make
  that preferable.
- For Nature-style manuscript figures, read `nature-style-igor.md` before
  composing the layout. Define the core conclusion, evidence hierarchy, final
  size, and reviewer risks before placing graph objects.

## Files, Paths, Experiments

- Prefer self-contained `.itx` files for automation because they can include
  waves and graph commands together and are easy for the user to inspect.
- Avoid long Windows paths with spaces in Igor startup arguments. Launch `.itx`
  via Windows short paths or copy to a temporary no-space path.
- For Igor file operations, use Igor symbolic paths or valid Igor colon paths.
  Do not pass a raw Windows path into an Igor command unless the command expects
  that syntax.
- Save paths need the same care as startup paths. Build `SavePICT` and
  `SaveExperiment` colon paths from short Windows paths when any parent folder
  contains spaces.
- Packed experiments (`.pxp`) preserve graphs, tables, waves, data folders, and
  windows. A PXP containing only an imported bitmap is not an editable graph.
- Autosave is a recovery aid, not a substitute for explicit saving and backups.
  Modal dialogs can interfere with automation; stop and hand off files rather
  than trying to bypass blocking UI.

## Export And Verification

- Use native graph export (`SavePICT`) for image deliverables and verify with an
  external image library when possible.
- For fixed physical output, specify export size and resolution rather than
  relying on the current on-screen window.
- For TIFF deliverables, verify format, pixel dimensions, DPI metadata, and that
  pixel extrema are nonblank.
- For multi-panel composition, consider exporting a page layout rather than
  combining rasterized panels outside Igor.
- For smoke tests, inspect the rendered PNG/TIFF for clipped traces, invisible
  panel labels, missing graph objects, and literal annotation escape text.

## Source Lookup Recipes

Use these search examples before inventing syntax:

```powershell
python "<skill-dir>\scripts\igor_ref_search.py" "Display yWave vs xWave"
python "<skill-dir>\scripts\igor_ref_search.py" "Stacked Bar Charts"
python "<skill-dir>\scripts\igor_ref_search.py" "Annotation Text Escape Codes"
python "<skill-dir>\scripts\igor_ref_search.py" "Saving as a Packed Experiment File"
python "<skill-dir>\scripts\igor_ref_search.py" "X Scaling Causes Bars to Move"
```

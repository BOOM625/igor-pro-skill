# Igor Help Corpus Map

Igor ships local help files (`.ihf`) plus `IgorMan.pdf` inside the install
folder. The `.ihf` files mix text with binary resources, so use
`scripts/igor_ref_search.py` or `rg -a` rather than plain text readers.

`scripts/igor_ref_search.py` auto-detects the help corpus from `--ref-dir`,
`IGOR_REF_DIR`, a bundled/local `igor ref` folder, or the installed Igor
directory discovered from `IGOR_EXE`, PATH, the Windows uninstall registry,
common WaveMetrics install locations, and drive-root Igor installation folders.

## Search First

Use this helper when exact Igor syntax or a less-common plot type is needed:

```powershell
python "<skill-dir>\scripts\igor_ref_search.py" "SavePICT" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "Stacked Bar Charts" --limit 8
python "<skill-dir>\scripts\igor_ref_search.py" "Annotation Escape Codes" --limit 8
```

Fallback raw search:

```powershell
# Use the directory printed by igor_ref_search.py --print-ref-dir, or IGOR_REF_DIR.
$ref = "C:\Path\To\Igor Help Files"
rg -a -n -C 3 "ModifyGraph|AppendToGraph|SavePICT" "$ref"
```

Use `--include-pdf` only when the `.ihf` files do not answer the question because
PDF extraction is slower.

## Task Routing

- Basic command syntax and command-line limitations: `Commands.ihf`, `Igor Reference.ihf`
- Waves, wave names, waveform versus XY model, `Make`, `SetScale`: `Waves.ihf`
- Standard graphs, traces, axes, styles, graph recreation: `Graphs.ihf`
- Bars, grouped bars, stacked bars, text category axes: `Category Plots.ihf`
- Text boxes, legends, tags, color scales, escape codes: `Annotations.ihf`
- Drawing objects and when not to use them for editable data: `Drawing.ihf`
- Graphics export and format choices: `Graphics.ihf`, `Page Layouts.ihf`
- Multi-panel figures and page composition: `Page Layouts.ihf`, `Subwindows.ihf`
- Data import/export, delimited text, Excel-like workflows: `Importing and Exporting Data.ihf`
- Experiments, packed/unpacked saves, symbolic paths, autosave: `Experiments, Files and Folders.ihf`
- Data folder paths and root-relative wave references: `Data Folders.ihf`
- Tables and table windows: `Tables.ihf`
- Image plots and matrix-as-image workflows: `Image Plots.ihf`, `Image Processing.ihf`
- Contour and XYZ/matrix plots: `Contour Plots.ihf`
- HDF5 import/export: `Igor HDF5 Guide.ihf`
- Error explanations and recovery: `Errors.ihf`, `Debugging.ihf`
- Platform-specific file/path issues: `Platform-Related Issues.ihf`
- Procedure files, macros, menus, UI controls: `Programming.ihf`, `Programming Techniques.ihf`, `Procedure Windows.ihf`, `Macros.ihf`, `Controls.ihf`, `User-Defined Menus.ihf`
- Available WaveMetrics procedures and XOPs: `WM Procedures Index.ihf`, `XOP Index.ihf`

## Files Covered

- `3D Graphics.ihf`
- `Advanced Topics.ihf`
- `Analysis of Functions.ihf`
- `Analysis.ihf`
- `Annotations.ihf`
- `Category Plots.ihf`
- `Commands.ihf`
- `Contour Plots.ihf`
- `Controls.ihf`
- `Curve Fitting.ihf`
- `Data Folders.ihf`
- `Debugging.ihf`
- `Dependencies.ihf`
- `Dialog Help.ihf`
- `Drawing.ihf`
- `Errors.ihf`
- `Experiments, Files and Folders.ihf`
- `Getting Started.ihf`
- `Graphics.ihf`
- `Graphs.ihf`
- `Igor Filter Design Laboratory.ihf`
- `Igor HDF5 Guide.ihf`
- `Igor Reference.ihf`
- `Igor Shortcuts.ihf`
- `IgorMan.pdf`
- `Image Plots.ihf`
- `Image Processing.ihf`
- `Importing and Exporting Data.ihf`
- `Interacting with the User.ihf`
- `Macros.ihf`
- `Multidimensional Waves.ihf`
- `Notebooks.ihf`
- `Page Layouts.ihf`
- `Platform-Related Issues.ihf`
- `Procedure Windows.ihf`
- `Programming Techniques.ihf`
- `Programming.ihf`
- `Signal Processing.ihf`
- `Statistics.ihf`
- `Subwindows.ihf`
- `Tables.ihf`
- `Text Encodings.ihf`
- `User-Defined Menus.ihf`
- `Using Igor.ihf`
- `Variables.ihf`
- `WM Procedures Index.ihf`
- `Waves.ihf`
- `What's Changed Since Igor Pro 9.00.ihf`
- `What's New In Igor Pro 9.ihf`
- `XOP Index.ihf`

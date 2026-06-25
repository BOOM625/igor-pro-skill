# Igor Pro Skill for Codex

General-purpose Codex skill for Igor Pro automation: data workflows, editable
scientific figures, exports, and debugging.

This repository contains a reusable Codex skill for working with Igor Pro. It
helps Codex create and debug Igor commands, manipulate waves and tables, build
editable graphs and multi-panel layouts, export high-DPI figures, save PXP/ITX
deliverables, and avoid common automation pitfalls on Windows.

## Features

- General Igor Pro command and procedure workflows.
- Data import/export, wave creation, tables, and data-folder organization.
- Editable native Igor graphs, layouts, and saved experiments.
- Nature-style publication figure guidance for restrained, manuscript-ready
  scientific plots.
- Support patterns for line plots, scatter plots, category bars, grouped bars,
  stacked bars, histograms, box/jitter plots, heatmaps, contours, and standard
  2D PieChart package figures.
- Local Igor help search through the bundled `igor_ref_search.py` helper.
- Export and verification guidance for TIFF/PNG/PXP/ITX outputs.
- Guardrails for Windows paths, wave-name conflicts, annotations, `SavePICT`,
  `SaveExperiment`, `ErrorBars ... SHADE`, and PieChart module timing.

## Installation

Copy the skill folder into your Codex skills directory.

Windows:

```powershell
Copy-Item .\igor-pro-skill-v1-5 "$env:USERPROFILE\.codex\skills\" -Recurse
```

macOS/Linux:

```bash
cp -R ./igor-pro-skill-v1-5 ~/.codex/skills/
```

Restart Codex or refresh local skills if needed. Then invoke the skill with:

```text
$igor-pro-skill-v1-5
```

The slash menu description is:

```text
General-purpose Igor Pro automation for data, figures, exports, and debugging.
```

## Requirements

- Codex with local skill support.
- Igor Pro installed locally when you want Codex to execute Igor workflows.
- Python for the bundled helper scripts.
- Igor help files are recommended for exact local syntax lookup. The helper
  script attempts to auto-detect common Igor installation and help-file paths.

This repository does not include Igor Pro, licenses, or WaveMetrics help files.

## Example Prompts

```text
Use $igor-pro-skill-v1-5 to create an editable Igor Pro line plot from this CSV
and export a 600 DPI TIFF.
```

```text
Use $igor-pro-skill-v1-5 to build a Nature-style multi-panel Igor figure with
editable waves and a saved PXP.
```

```text
Use $igor-pro-skill-v1-5 to debug this Igor command and search the local Igor
help for the correct syntax.
```

## Repository Layout

```text
igor-pro-skill-v1-5/
  SKILL.md
  agents/
    openai.yaml
  references/
    igor-automation-notes.md
    igor-help-map.md
    nature-style-igor.md
  scripts/
    igor_ref_search.py
    igor_xy_plot.py
```

## Version

Current release: `v1.5`

The v1.5 release emphasizes public-facing clarity and general-purpose Igor Pro
coverage, while keeping the Nature-style publication figure workflow.

## License

MIT License. See `LICENSE`.

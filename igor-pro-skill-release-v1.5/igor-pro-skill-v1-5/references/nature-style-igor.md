# Nature-Style Igor Figure Rules

Use this reference when making Nature-style, high-impact, manuscript, SCI, or
journal-ready figures in Igor Pro. These rules adapt the publication-figure
logic from `nature-figure` to Igor-native waves, graph windows, layouts, PXP
experiments, and `SavePICT` exports.

## Figure Contract

Before writing Igor commands, write a short working contract:

```text
Core conclusion:
Figure archetype:
Target journal/output:
Final size:
Panel map:
  a:
  b:
  c:
Evidence hierarchy:
  hero evidence:
  validation evidence:
  controls/robustness:
Statistics needed:
Source data needed:
Image-integrity notes:
Reviewer risk:
```

Rules:

- Start from the claim, not from a favorite plot template.
- Each panel must answer a unique scientific question. Remove or merge panels
  that repeat evidence.
- Give the primary evidence the largest panel, clearest axis, or first reading
  position.
- Use supporting panels for validation, controls, sensitivity, or mechanism.
- If the user provides data but no claim, infer a provisional claim and ask for
  confirmation before final styling.

## Archetypes

- `quantitative grid`: mainly numerical comparisons. Use shared axes, aligned
  scales, compact legends, and a restrained palette.
- `schematic-led composite`: workflow, mechanism, device, or experimental
  design leads the story. If using Igor only, approximate schematics sparingly
  with editable annotations/drawing objects and keep quantitative panels quieter.
- `image plate + quant`: microscopy, histology, blots, spatial overlays, or
  segmentation lead the evidence. Use black only inside the image plate region,
  direct channel labels, and calibrated scale bars.
- `asymmetric mixed-modality figure`: combine schematic/image/heatmap/quant
  panels. Let one hero panel span rows or columns; do not force equal sizes.

## Igor Style Defaults

For ordinary exploratory or standalone Igor figures, the main skill default
(`fSize=12`, axis thickness 2) is acceptable. For Nature-style final layouts,
use smaller final-size typography and quieter axes:

```igor
X ModifyGraph/W=PanelA tick=0,mirror=0,standoff=0
X ModifyGraph/W=PanelA fSize=8,font="Arial"
X ModifyGraph/W=PanelA axThick(left)=1,axThick(bottom)=1
X ModifyGraph/W=PanelA btLen=3
```

Use `mirror=0` for left/bottom-only axes when appropriate. If a specific Igor
version interprets `mirror` differently, search local help for `ModifyGraph
mirror`.

Line and marker defaults:

```igor
X ModifyGraph/W=PanelA lsize(MainTrace)=1.4
X ModifyGraph/W=PanelA mode(DataTrace)=3,marker(DataTrace)=19,msize(DataTrace)=2.5
```

Uncertainty bands:

```igor
X ErrorBars/W=PanelA/T=0/L=0 MeanTrace SHADE={0,0,(15000,30000,50000,12000),(15000,30000,50000,12000)},wave=(PlusErr,MinusErr)
```

Avoid grids by default. Use sparse ticks or light reference lines only when they
carry interpretation.

## Palette

Igor RGB values use 0-65535 per channel. Convert hex to Igor RGB with
`channel_igor = channel_8bit * 257`.

Core semantic palette:

| Role | Hex | Igor RGB |
|---|---:|---:|
| key method blue | `#0F4D92` | `(3855,19789,37522)` |
| secondary blue | `#3775BA` | `(14135,30069,47802)` |
| positive green | `#8BCF8B` | `(35723,53199,35723)` |
| contrast red | `#B64342` | `(46774,17219,16962)` |
| neutral light | `#CFCECE` | `(53199,52942,52942)` |
| neutral mid | `#767676` | `(30326,30326,30326)` |
| neutral dark | `#4D4D4D` | `(19789,19789,19789)` |
| teal accent | `#42949E` | `(16962,38036,40606)` |
| violet accent | `#9A4D8E` | `(39578,19789,36494)` |

NMI-style low-saturation family:

| Role | Hex | Igor RGB |
|---|---:|---:|
| baseline dark | `#484878` | `(18504,18504,30840)` |
| baseline mid | `#7884B4` | `(30840,33924,46260)` |
| baseline soft | `#B4C0E4` | `(46260,49344,58596)` |
| method base | `#E4CCD8` | `(58596,52428,55512)` |
| method large | `#F0C0CC` | `(61680,49344,52428)` |
| delta up | `#2E9E44` | `(11822,40606,17476)` |
| delta down | `#E53935` | `(58853,14649,13621)` |

Image plate accents:

| Role | Hex | Igor RGB |
|---|---:|---:|
| cyan | `#22D7E6` | `(8738,55255,59110)` |
| magenta | `#FF2AD4` | `(65535,10794,54484)` |
| grey context | `#B8B8B8` | `(47288,47288,47288)` |

Rules:

- Keep one neutral family, one signal family, and one accent family per figure.
- Keep the same condition/method color across all panels.
- Reserve green/red for direction, thresholds, gains, drops, or real biological
  meaning; do not use red/green as the only encoding.
- Reduce saturation before adding more unrelated hues.
- For related ablations or time progressions, use one hue family with changing
  intensity or alpha.

## Layout In Igor

Create real graph windows first, then assemble them in a `NewLayout`.

Nature-style page sizes:

- Single column: about 89 mm wide (`3.5 in`).
- Double column: about 183 mm wide (`7.2 in`).
- Full composite page: often `7.0-7.4 in` wide and `5.5-7.8 in` high.

Igor layout object rectangles are page points. A `7.2 in` wide export is about
`518.4` points wide. Keep every `AppendLayoutObject/R=(...)` rectangle inside
the exported page bounds.

Composition rules:

- Use one hero panel when the evidence hierarchy is asymmetric.
- Put shared legend strips above a row or in a small legend-only graph/layout
  region when repeated legends waste space.
- Prefer direct labels for fixed line identities, image channels, regions, or
  stable categories.
- Keep gutters tight but real; increase spacing when dark image panels touch
  white plot panels.
- Avoid decorative panel boxes. Alignment and whitespace should carry structure.

Panel labels:

```igor
X TextBox/W=PanelA/C/N=Panel/F=0/B=1/A=LT/X=1/Y=1 "\Z08\f01a"
```

Use small bold lowercase letters for final Nature-style figures. Remember that
`TextBox /G=(r,g,b)` changes text color; use white text on dark image plates and
omit `/G` on ordinary white plot panels.

For Igor 9 annotation text, use two digits for sub-10 point `\Z` sizes such as
`\Z08` or `\Z07`. One-digit forms such as `\Z8` can render as literal escape
residue in exported images.

## Plot-Type Guidance

- Bars: use error bars with clear `n`, center, and spread definitions. Use
  hatching or luminance-safe colors when print-safe grayscale matters.
- Lines: use `ErrorBars ... SHADE` for uncertainty bands with low alpha. Keep
  line widths modest and use direct labels or one shared legend.
- Heatmaps: avoid rainbow for manuscript heatmaps unless the scale is not
  quantitative. Prefer diverging red/blue for signed deviations and neutral
  masks for missing cells.
- Stacked/composition panels: use them for overview; add a deviation heatmap or
  relationship scatter if the same data need a second panel.
- Image plates: keep scale bars, crops, channel labels, and contrast settings
  consistent and traceable.
- Pie charts: use only when composition is genuinely part-to-whole and category
  count is small. For manuscript figures, stacked bars often compare groups more
  defensibly than repeated pies.

## Export Bundle

For Nature-style Igor deliverables, prefer:

- Editable source: `.itx` and/or `.pxp`.
- Raster preview/submission: TIFF or PNG with explicit physical size and DPI.
- Source data: CSV/XLSX or open Igor table/waves.
- QA notes in response: size, DPI, nonblank check, and any caveats.

Igor may not preserve editable SVG/PDF text the same way matplotlib/R does.
When editable text is required, keep the PXP/ITX as the editable source of
truth and export raster/vector previews as requested.

TIFF example:

```igor
X DoWindow/F FinalLayout
X SavePICT/E=-7/RES=600/I/W=(0,0,7.2,6.0)/O as "C:SHORTP~1:figure.tif"
```

Always verify export externally for:

- file format;
- pixel dimensions;
- DPI metadata;
- nonblank extrema;
- readable final-size text;
- no clipped traces, axes, panel labels, legends, or layout objects.

## Reviewer-Risk Checklist

Before finalizing a Nature-style figure, check:

- Does every panel map to the core conclusion?
- Could the conclusion survive if one panel is removed? If yes, merge/drop it.
- Are comparable panels using comparable axes and limits?
- Are `n`, biological/technical replicate definitions, center statistic,
  spread/interval, statistical test, correction, and p-value display defined?
- Are quantitative panels traceable to source waves/tables/files?
- Are representative images quantified or linked to quantification panels?
- Are crop, contrast, pseudo-color, stitching, and scale calibration documented
  for image panels?
- Does the preview remain readable at the requested final width?

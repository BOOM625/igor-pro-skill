#!/usr/bin/env python3
"""Create an Igor Pro XY plot and export a high-DPI TIFF."""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


SAFE_X_WAVE = "PlotXWave"
SAFE_Y_WAVE = "PlotYWave"
SAFE_GRAPH = "PlotFigure"


def short_path(path: Path) -> str:
    """Return a Windows 8.3 short path when available."""
    path = path.resolve()
    if os.name != "nt":
        return str(path)

    get_short = ctypes.windll.kernel32.GetShortPathNameW
    size = get_short(str(path), None, 0)
    if size == 0:
        return str(path)
    buffer = ctypes.create_unicode_buffer(size)
    result = get_short(str(path), buffer, size)
    if result == 0:
        return str(path)
    return buffer.value


def has_space(text: str) -> bool:
    return any(ch.isspace() for ch in text)


def windows_to_igor_path(path: Path | str) -> str:
    """Convert C:\\dir\\file.tif to C:dir:file.tif for Igor."""
    p = Path(path).resolve()
    if not p.drive:
        raise ValueError(f"Igor output path must include a drive letter: {p}")
    parts = p.parts
    drive = p.drive.rstrip(":")
    return drive + ":" + ":".join(parts[1:])


def unique_paths(paths):
    seen = set()
    for path in paths:
        if not path:
            continue
        p = Path(path).expanduser()
        try:
            key = str(p.resolve()).casefold()
        except OSError:
            key = str(p).casefold()
        if key in seen:
            continue
        seen.add(key)
        yield p


def windows_drive_roots() -> list[Path]:
    if os.name != "nt":
        return []
    if hasattr(os, "listdrives"):
        return [Path(drive) for drive in os.listdrives()]
    return [Path(f"{letter}:\\") for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{letter}:\\").exists()]


def install_root_from_exe(exe: Path) -> Path | None:
    if exe.parent.name in {"IgorBinaries_x64", "IgorBinaries_Win32"}:
        return exe.parent.parent
    return exe.parent if exe.exists() else None


def registry_install_roots() -> list[Path]:
    if os.name != "nt":
        return []
    roots: list[Path] = []
    try:
        import winreg
    except Exception:
        return roots

    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    subkeys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for hive in hives:
        for subkey in subkeys:
            try:
                key = winreg.OpenKey(hive, subkey)
            except OSError:
                continue
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    child_name = winreg.EnumKey(key, i)
                    child = winreg.OpenKey(key, child_name)
                    display = str(winreg.QueryValueEx(child, "DisplayName")[0])
                except OSError:
                    continue
                if "Igor" not in display:
                    continue
                try:
                    install_location = str(winreg.QueryValueEx(child, "InstallLocation")[0]).strip()
                except OSError:
                    continue
                if install_location:
                    roots.append(Path(install_location))
    return roots


def common_install_roots() -> list[Path]:
    roots: list[Path] = []
    for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(env_name)
        if not base:
            continue
        base_path = Path(base)
        roots.extend(base_path.glob("WaveMetrics/Igor Pro*"))
        roots.extend(base_path.glob("Igor Pro*"))
    for drive in windows_drive_roots():
        roots.extend(drive.glob("Igor Pro*"))
    return roots


def igor_exes_from_root(root: Path) -> list[Path]:
    return [
        root / "IgorBinaries_x64" / "Igor64.exe",
        root / "IgorBinaries_Win32" / "Igor.exe",
        root / "Igor64.exe",
        root / "Igor.exe",
    ]


def find_igor_exe(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if p.exists():
            return p
        raise FileNotFoundError(f"--igor-exe does not exist: {p}")

    env = os.environ.get("IGOR_EXE")
    if env:
        p = Path(env)
        if p.exists():
            return p
        raise FileNotFoundError(f"IGOR_EXE is set but does not exist: {p}")

    candidates: list[Path] = []
    for exe_name in ("Igor64.exe", "Igor.exe"):
        found = shutil.which(exe_name)
        if found:
            candidates.append(Path(found))
    for root in registry_install_roots() + common_install_roots():
        candidates.extend(igor_exes_from_root(root))

    for candidate in unique_paths(candidates):
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not find Igor Pro. Pass --igor-exe or set IGOR_EXE."
    )


def resolve_column(columns, requested: str | None) -> str | None:
    if requested is None:
        return None
    names = [str(c).strip() for c in columns]
    if requested in names:
        return requested
    lowered = {name.lower(): name for name in names}
    return lowered.get(requested.lower())


def numeric_pairs_from_dataframe(df, x_col: str, y_col: str, sort_x: bool):
    import pandas as pd

    x = pd.to_numeric(df[x_col], errors="coerce")
    y = pd.to_numeric(df[y_col], errors="coerce")
    mask = x.notna() & y.notna()
    pairs = [(float(a), float(b)) for a, b in zip(x[mask], y[mask])]
    pairs = [(a, b) for a, b in pairs if math.isfinite(a) and math.isfinite(b)]
    if sort_x:
        pairs.sort(key=lambda item: item[0])
    return pairs


def load_xy_data(args):
    import pandas as pd

    source = Path(args.input)
    ext = source.suffix.lower()
    candidates = []

    def try_sheet(sheet_name, label):
        df = pd.read_excel(source, sheet_name=sheet_name) if ext in {".xls", ".xlsx"} else pd.read_csv(source)
        cols = [str(c).strip() for c in df.columns]
        df.columns = cols
        x_actual = resolve_column(cols, args.x_col)
        y_actual = resolve_column(cols, args.y_col)
        if x_actual and y_actual:
            return df, x_actual, y_actual, "requested", label
        x_actual = resolve_column(cols, args.fallback_x_col)
        y_actual = resolve_column(cols, args.fallback_y_col)
        if x_actual and y_actual:
            return df, x_actual, y_actual, "fallback", label
        numeric_cols = []
        for col in cols:
            numeric = pd.to_numeric(df[col], errors="coerce")
            if numeric.notna().sum() > 0:
                numeric_cols.append(col)
        if len(numeric_cols) == 2:
            return df, numeric_cols[0], numeric_cols[1], "two_numeric_columns", label
        return None

    if ext in {".xls", ".xlsx"}:
        xl = pd.ExcelFile(source)
        sheets = [args.sheet] if args.sheet else xl.sheet_names
        for sheet in sheets:
            result = try_sheet(sheet, sheet)
            if result:
                candidates.append(result)
                if result[3] == "requested":
                    break
    else:
        result = try_sheet(None, source.name)
        if result:
            candidates.append(result)

    if not candidates:
        raise ValueError(
            f"Could not resolve X/Y columns. Requested {args.x_col!r}/{args.y_col!r}; "
            f"fallback {args.fallback_x_col!r}/{args.fallback_y_col!r}."
        )

    df, x_actual, y_actual, selection_reason, sheet_label = candidates[0]
    pairs = numeric_pairs_from_dataframe(df, x_actual, y_actual, args.sort_x)
    if not pairs:
        raise ValueError(f"No numeric X/Y rows found in {sheet_label}: {x_actual}/{y_actual}")
    return {
        "pairs": pairs,
        "sheet": sheet_label,
        "x_column": x_actual,
        "y_column": y_actual,
        "selection_reason": selection_reason,
    }


def fmt_num(value: float) -> str:
    return format(value, ".15g")


def igor_string(text: str) -> str:
    return str(text).replace('"', "'")


def build_itx(args, pairs, igor_output_path: str) -> str:
    legend_label = args.legend_label or args.y_label
    lines = [
        "IGOR",
        f"WAVES/D {SAFE_X_WAVE}, {SAFE_Y_WAVE}",
        "BEGIN",
    ]
    lines.extend(f"{fmt_num(x)}\t{fmt_num(y)}" for x, y in pairs)
    lines.extend(
        [
            "END",
            f"X DoWindow/K {SAFE_GRAPH}",
            f"X Display/N={SAFE_GRAPH} {SAFE_Y_WAVE} vs {SAFE_X_WAVE}",
            f"X ModifyGraph mode=0, lsize({SAFE_Y_WAVE})={args.line_size}, rgb({SAFE_Y_WAVE})=(0,0,0)",
            f"X ModifyGraph mirror=2, tick=0, axThick(left)={args.axis_thick}, axThick(bottom)={args.axis_thick}, standoff=0",
            f'X ModifyGraph fSize={args.font_size}, font="{igor_string(args.font)}"',
            f'X Label bottom "{igor_string(args.x_label)}"',
            f'X Label left "{igor_string(args.y_label)}"',
            f'X Legend/C/N=legend0/J/F=0/A=RT "\\s({SAFE_Y_WAVE}) {igor_string(legend_label)}"',
            "X SetAxis/A",
            f'X SavePICT/E=-7/RES={args.dpi}/I/W=(0,0,{args.width},{args.height})/O as "{igor_output_path}"',
        ]
    )
    return "\n".join(lines) + "\n"


def verify_image(path: Path, expected_dpi: int):
    from PIL import Image, ImageStat

    with Image.open(path) as image:
        dpi = image.info.get("dpi")
        dpi_values = tuple(float(value) for value in dpi) if dpi else None
        gray = image.convert("L")
        extrema = ImageStat.Stat(gray).extrema[0]
        summary = {
            "format": image.format,
            "mode": image.mode,
            "size": list(image.size),
            "dpi": list(dpi_values) if dpi_values else None,
            "gray_extrema": list(extrema),
        }
    if extrema[0] == extrema[1]:
        raise ValueError(f"Export appears blank: gray extrema {extrema}")
    if dpi_values and any(abs(value - expected_dpi) > 2 for value in dpi_values[:2]):
        raise ValueError(f"Export DPI {dpi_values} does not match requested {expected_dpi}")
    return summary


def choose_work_dir(output: Path) -> tuple[Path, bool]:
    output.parent.mkdir(parents=True, exist_ok=True)
    parent_short = short_path(output.parent)
    if not has_space(parent_short):
        return output.parent, False
    temp_dir = Path(tempfile.mkdtemp(prefix="codex_igor_"))
    if has_space(short_path(temp_dir)):
        raise RuntimeError(f"Could not create a no-space working directory: {temp_dir}")
    return temp_dir, True


def launch_and_wait(igor_exe: Path, itx_path: Path, output_path: Path, timeout: int):
    itx_short = short_path(itx_path)
    if has_space(itx_short):
        raise RuntimeError(f"ITX short path still contains spaces: {itx_short}")
    proc = subprocess.Popen([str(igor_exe), itx_short])
    deadline = time.time() + timeout
    while time.time() < deadline:
        if output_path.exists() and output_path.stat().st_size > 0:
            time.sleep(0.75)
            return proc
        time.sleep(0.5)
    raise TimeoutError(f"Igor did not create {output_path} within {timeout} seconds")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Excel or CSV input file")
    parser.add_argument("--sheet", help="Excel sheet name")
    parser.add_argument("--x-col", required=True, help="Requested X column")
    parser.add_argument("--y-col", required=True, help="Requested Y column")
    parser.add_argument("--fallback-x-col", default="X", help="Fallback X column")
    parser.add_argument("--fallback-y-col", default="Y", help="Fallback Y column")
    parser.add_argument("--x-label", required=True)
    parser.add_argument("--y-label", required=True)
    parser.add_argument("--legend-label", help="Legend text. Defaults to --y-label.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--igor-exe", help="Path to Igor64.exe or Igor.exe")
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--width", type=float, default=4.0, help="Export width in inches")
    parser.add_argument("--height", type=float, default=3.0, help="Export height in inches")
    parser.add_argument("--line-size", type=float, default=2.0)
    parser.add_argument("--axis-thick", type=float, default=2.0)
    parser.add_argument("--font", default="Arial")
    parser.add_argument("--font-size", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--no-sort-x", dest="sort_x", action="store_false")
    parser.add_argument("--keep-itx", action="store_true")
    parser.add_argument("--keep-igor-open", action="store_true")
    args = parser.parse_args(argv)

    output = Path(args.output).resolve()
    igor_exe = find_igor_exe(args.igor_exe)
    data = load_xy_data(args)

    work_dir, remove_work_dir = choose_work_dir(output)
    safe_output = work_dir / "__codex_igor_output.tif"
    safe_itx = work_dir / "__codex_igor_plot.itx"
    if safe_output.exists():
        safe_output.unlink()
    safe_output.touch()
    igor_output_path = windows_to_igor_path(short_path(safe_output))
    safe_output.unlink()

    safe_itx.write_text(
        build_itx(args, data["pairs"], igor_output_path),
        encoding="utf-8",
        newline="\n",
    )

    proc = None
    try:
        proc = launch_and_wait(igor_exe, safe_itx, safe_output, args.timeout)
        if output.exists():
            output.unlink()
        shutil.move(str(safe_output), str(output))
        verification = verify_image(output, args.dpi)
        if args.keep_itx:
            shutil.copy2(safe_itx, output.with_suffix(".itx"))
        summary = {
            "output": str(output),
            "igor_exe": str(igor_exe),
            "sheet": data["sheet"],
            "x_column": data["x_column"],
            "y_column": data["y_column"],
            "selection_reason": data["selection_reason"],
            "points": len(data["pairs"]),
            "verification": verification,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    finally:
        if proc and not args.keep_igor_open and proc.poll() is None and output.exists():
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        if remove_work_dir:
            shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

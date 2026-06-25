#!/usr/bin/env python3
"""Search local Igor Pro help files with readable snippets.

Igor .ihf help files contain mixed binary resources and text. This helper
extracts printable text runs and searches them so agents can quickly confirm
Igor syntax or concepts from the local help corpus.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


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
    parts = exe.parts
    if len(parts) >= 2 and exe.parent.name in {"IgorBinaries_x64", "IgorBinaries_Win32"}:
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
                    roots.append(Path(winreg.QueryValueEx(child, "InstallLocation")[0]))
                except OSError:
                    continue
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


def candidate_igor_install_roots() -> list[Path]:
    roots: list[Path] = []
    env_exe = os.environ.get("IGOR_EXE")
    if env_exe:
        root = install_root_from_exe(Path(env_exe))
        if root:
            roots.append(root)
    for exe_name in ("Igor64.exe", "Igor.exe"):
        found = shutil.which(exe_name)
        if found:
            root = install_root_from_exe(Path(found))
            if root:
                roots.append(root)
    roots.extend(registry_install_roots())
    roots.extend(common_install_roots())
    return list(unique_paths(path for path in roots if path.exists()))


def has_help_files(ref_dir: Path) -> bool:
    if not ref_dir.exists() or not ref_dir.is_dir():
        return False
    try:
        return any(ref_dir.rglob("*.ihf")) or any(ref_dir.rglob("IgorMan.pdf"))
    except OSError:
        return False


def resolve_ref_dir(explicit: str | None) -> Path:
    if explicit:
        ref_dir = Path(explicit).expanduser()
        if has_help_files(ref_dir):
            return ref_dir
        raise SystemExit(f"Reference directory contains no .ihf files or IgorMan.pdf: {ref_dir}")

    env_ref = os.environ.get("IGOR_REF_DIR")
    if env_ref:
        ref_dir = Path(env_ref).expanduser()
        if has_help_files(ref_dir):
            return ref_dir
        raise SystemExit(f"IGOR_REF_DIR contains no .ihf files or IgorMan.pdf: {ref_dir}")

    local_candidates = [
        Path.cwd() / "igor ref",
        SKILL_DIR / "igor ref",
        SKILL_DIR / "references" / "igor ref",
        SKILL_DIR / "references" / "igor-help",
        SKILL_DIR / "assets" / "igor ref",
    ]
    for candidate in unique_paths(local_candidates):
        if has_help_files(candidate):
            return candidate

    install_candidates: list[Path] = []
    for root in candidate_igor_install_roots():
        install_candidates.extend(
            [
                root / "Igor Help Files",
                root,
            ]
        )
    for candidate in unique_paths(install_candidates):
        if has_help_files(candidate):
            return candidate

    raise SystemExit(
        "Could not find Igor help files. Set IGOR_REF_DIR or pass --ref-dir. "
        "Typical locations include '<Igor install>/Igor Help Files' or the Igor install root."
    )


def extract_printable_text(path: Path) -> str:
    data = path.read_bytes()
    pieces = re.findall(rb"[\x09\x0a\x0d\x20-\x7e]{4,}", data)
    text = "\n".join(piece.decode("latin-1", errors="ignore") for piece in pieces)
    return re.sub(r"[ \t\r\f\v]+", " ", text)


def extract_pdf_text(path: Path, max_pages: int) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""

    try:
        reader = PdfReader(str(path))
    except Exception:
        return ""

    parts: list[str] = []
    for page in reader.pages[:max_pages]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def iter_files(ref_dir: Path, include_pdf: bool) -> list[Path]:
    files = list(ref_dir.rglob("*.ihf"))
    if include_pdf:
        files.extend(ref_dir.rglob("*.pdf"))
        if ref_dir.name == "Igor Help Files":
            manual = ref_dir.parent / "Manual" / "IgorMan.pdf"
            if manual.exists():
                files.append(manual)
    return sorted(unique_paths(p for p in files if p.is_file()))


def snippets(text: str, pattern: re.Pattern[str], context: int) -> list[str]:
    out: list[str] = []
    for match in pattern.finditer(text):
        start = max(0, match.start() - context)
        end = min(len(text), match.end() + context)
        snippet = text[start:end]
        snippet = re.sub(r"\s+", " ", snippet).strip()
        out.append(snippet)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Search local Igor Pro help files.")
    parser.add_argument("query", help="Plain text query or regex pattern.")
    parser.add_argument("--ref-dir", help="Directory containing Igor .ihf files, or an Igor install root.")
    parser.add_argument("--regex", action="store_true", help="Treat query as a regular expression.")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--include-pdf", action="store_true", help="Also search IgorMan.pdf.")
    parser.add_argument("--pdf-pages", type=int, default=40, help="Max PDF pages to scan when --include-pdf is used.")
    parser.add_argument("--context", type=int, default=220, help="Characters of context around each match.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum snippets to print.")
    parser.add_argument("--print-ref-dir", action="store_true", help="Print the resolved reference directory before searching.")
    args = parser.parse_args()

    ref_dir = resolve_ref_dir(args.ref_dir)
    if args.print_ref_dir:
        print(f"Reference directory: {ref_dir}")

    flags = 0 if args.case_sensitive else re.IGNORECASE
    query = args.query if args.regex else re.escape(args.query)
    pattern = re.compile(query, flags)

    printed = 0
    for path in iter_files(ref_dir, args.include_pdf):
        if path.suffix.lower() == ".pdf":
            text = extract_pdf_text(path, args.pdf_pages)
        else:
            text = extract_printable_text(path)
        if not text:
            continue
        hits = snippets(text, pattern, args.context)
        for hit in hits:
            print(f"## {path.name}")
            print(hit)
            print()
            printed += 1
            if printed >= args.limit:
                return 0

    if printed == 0:
        print(f"No matches for {args.query!r} in {ref_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

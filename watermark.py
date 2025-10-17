#!/usr/bin/env python3
"""
watermark.py
Menyisipkan watermark/penanda unik ke file teks (mis. .py, .js, .m3u, .md).
Gunakan ini di repo Anda untuk menambahkan SIGNATURE ke file-file penting.
Konfigurasi:
- SIGNATURE env var, contoh: OWNER:maywho5454:SIG:20251017-abc123
- TARGET_EXTS env var, contoh: .py,.m3u,.js,.md
- DRY_RUN=1 untuk hanya menampilkan aksi tanpa menulis file
"""
import os
import sys
from pathlib import Path

SIGNATURE = os.getenv("SIGNATURE")
TARGET_EXTS = os.getenv("TARGET_EXTS", ".py,.m3u,.md")
DRY_RUN = os.getenv("DRY_RUN", "") != ""

if not SIGNATURE:
    print("Error: set SIGNATURE environment variable.")
    sys.exit(1)

exts = set([e.strip() for e in TARGET_EXTS.split(",") if e.strip()])

def is_text_file(path: Path):
    return any(path.name.endswith(e) for e in exts)

def has_signature(text):
    return SIGNATURE in text

def make_header_for_ext(path: Path):
    # komentar sesuai tipe file
    name = path.name.lower()
    if name.endswith(".py") or name.endswith(".m3u") or name.endswith(".sh"):
        return f"# {SIGNATURE}\n"
    if name.endswith(".js") or name.endswith(".ts") or name.endswith(".jsx"):
        return f"// {SIGNATURE}\n"
    if name.endswith(".md"):
        return f"<!-- {SIGNATURE} -->\n"
    # fallback
    return f"/* {SIGNATURE} */\n"

def process_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if has_signature(text):
        print(f"SKIP (sudah ada signature): {path}")
        return False
    header = make_header_for_ext(path)
    new_text = header + text
    if DRY_RUN:
        print(f"DRY RUN: akan menambahkan signature ke {path}")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"DITAMBAH signature ke {path}")
    return True

def main(root="."):
    p = Path(root)
    counters = 0
    for f in p.rglob("*"):
        if f.is_file() and is_text_file(f):
            try:
                if process_file(f):
                    counters += 1
            except Exception as e:
                print(f"Error membaca/menulis {f}: {e}")
    print(f"Selesai. File yang diberi watermark: {counters}")

if __name__ == "__main__":
    main()

#!/bin/bash
# Simpel pre-commit hook (letakkan di .git/hooks/pre-commit dan chmod +x)
# Hook ini menjalankan watermark.py sebelum commit (opsional).
# Pastikan environment SIGNATURE sudah diset di environment CI/dev machine.
python3 ./watermark.py
git add .

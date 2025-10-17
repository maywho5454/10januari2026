```markdown
# Monitor & Watermark untuk mendeteksi penyalinan repo/public files

Panduan singkat:

1) Konsep
- Sisipkan signature unik (watermark) ke file penting Anda. Contoh:
  OWNER:maywho5454:SIG:20251017-abc123
  Ini dapat berupa komentar di bagian atas file.
- Jalankan script monitor (cron lokal / GitHub Action) yang mencari files publik yang mengandung signature.
- Bila ditemukan, script akan membuat issue di repo Anda dan/atau mengirim notifikasi via webhook.

2) Cara pakai (lokal)
- Buat token GitHub (PAT) minimal scope: "repo" (jika ingin membuat issue di private repo) atau "public_repo" & "repo:status" cukup untuk public. Untuk search API cukup "public_repo" + "repo" jika perlu menulis issue.
- Export env vars:
  export GITHUB_TOKEN="ghp_..."
  export SIGNATURE="OWNER:maywho5454:SIG:20251017-abc123"
  export OUTPUT_REPO="maywho5454/10januari2026"
  export ALERT_WEBHOOK="https://discord.com/api/webhooks/..."  # optional

- Tambahkan watermark ke file Anda:
  export SIGNATURE="OWNER:maywho5454:SIG:20251017-abc123"
  python3 watermark.py

- Jalankan monitor (dapat di-cron setiap 1 jam):
  python3 monitor.py

3) Cara pakai (GitHub Actions)
- Anda bisa membuat workflow yang menjalankan monitor.py secara berkala (mis. daily/hourly).
- Pastikan repository secrets: GITHUB_TOKEN (Action memiliki GITHUB_TOKEN otomatis), SIGNATURE, OUTPUT_REPO, ALERT_WEBHOOK (opsional).

4) Tindakan ketika menemukan salinan
- Periksa repositori target.
- Jika pelanggaran serius: ajukan permintaan penghapusan DMCA via GitHub.
- Jika sekadar sinkronisasi tanpa izin: hubungi pemilik repositori.

5) Pencegahan tambahan
- Jangan pernah hardcode PAT di repo. Pakai GitHub Secrets atau environment variables.
- Aktifkan secret scanning jika memungkinkan.
- Pertimbangkan membuat license yang jelas (mis. LICENSE + README) sehingga pelanggaran lebih mudah dibuktikan.

6) Catatan teknis
- GitHub Search API memiliki rate limit. Untuk volume besar, pertimbangkan throttling dan penjadwalan lebih longgar.
- Signature harus cukup unik; gunakan UUID atau kombinasi tanggal/username untuk mengurangi false positives.

```

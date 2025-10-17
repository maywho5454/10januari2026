#!/usr/bin/env python3
"""
monitor.py
Pemantauan publik untuk mencari tanda unik (watermark) dari repo Anda di repositori publik lain
- Gunakan GITHUB_TOKEN (env) dengan akses public search + repo (untuk membuat issue di repo Anda)
- KONFIGURASI lewat environment variables:
  - GITHUB_TOKEN: GitHub PAT
  - OWNER_REPO_TO_TRACK: repo Anda, contoh "maywho5454/10januari2026" (digunakan hanya untuk reference)
  - SIGNATURE: teks unik yang Anda sisipkan ke file (contoh: "OWNER:maywho5454:SIG:12345-xyz")
  - OUTPUT_REPO: repo Anda tempat membuat issue ketika ditemukan (contoh: "maywho5454/10januari2026")
  - ALERT_WEBHOOK (opsional): URL webhook (Discord/Slack) untuk notifikasi
"""
import os
import sys
import json
import time
import requests
from github import Github, GithubException
from urllib.parse import quote_plus

# Konfigurasi via env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
SIGNATURE = os.getenv("SIGNATURE")  # wajib: text unik yang disisipkan ke file Anda
OUTPUT_REPO = os.getenv("OUTPUT_REPO")  # repo Anda untuk membuat issue notifikasi
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK")  # optional webhook URL (Discord/Slack)
STATE_FILE = os.getenv("STATE_FILE", "monitor_state.json")
SEARCH_PER_PAGE = 50  # jumlah hasil per page (max 100)

if not GITHUB_TOKEN or not SIGNATURE or not OUTPUT_REPO:
    print("Error: Pastikan environment variables GITHUB_TOKEN, SIGNATURE, OUTPUT_REPO sudah di-set.")
    sys.exit(1)

search_headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
gh = Github(GITHUB_TOKEN)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"seen": []}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def search_code(signature, per_page=SEARCH_PER_PAGE):
    """
    Pakai REST Search API untuk mencari signature secara eksak di file publik.
    Returns list of dict {html_url, repository_full_name, path, score}
    """
    q = f'"{signature}" in:file'
    url = f"https://api.github.com/search/code?q={quote_plus(q)}&per_page={per_page}"
    results = []
    page = 1
    while True:
        r = requests.get(url + f"&page={page}", headers=search_headers, timeout=30)
        if r.status_code == 422:
            # query cannot be processed (misalnya terlalu pendek)
            print("Search API rejected the query (422). Pastikan SIGNATURE cukup unik/eksak.")
            return results
        r.raise_for_status()
        data = r.json()
        for item in data.get("items", []):
            results.append({
                "html_url": item.get("html_url"),
                "repository": item.get("repository", {}).get("full_name"),
                "path": item.get("path"),
                "score": item.get("score"),
            })
        # paging
        if "next" in r.links:
            page += 1
            time.sleep(1)  # be nice to API
        else:
            break
    return results

def notify_webhook(webhook_url, payload):
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        r.raise_for_status()
        print("Webhook notified.")
    except Exception as e:
        print(f"Gagal mengirim webhook: {e}")

def create_issue_in_output_repo(title, body):
    try:
        repo = gh.get_repo(OUTPUT_REPO)
        issue = repo.create_issue(title=title, body=body)
        return issue.html_url
    except GithubException as e:
        print(f"Gagal membuat issue di {OUTPUT_REPO}: {e}")
        return None

def main():
    state = load_state()
    seen = set(state.get("seen", []))

    print(f"Mencari signature: {SIGNATURE} ...")
    found = search_code(SIGNATURE)

    new_found = []
    for item in found:
        key = f'{item["repository"]}:{item["path"]}'
        if key not in seen:
            new_found.append(item)
            seen.add(key)

    if not new_found:
        print("Tidak ada salinan baru yang terdeteksi.")
    else:
        print(f"Ditemukan {len(new_found)} salinan baru:")
        for it in new_found:
            print(f' - {it["repository"]}/{it["path"]} -> {it["html_url"]}')

        # Buat issue ringkasan di repo Anda
        title = f"[Auto-alert] Ditemukan salinan kode ({len(new_found)} item) yang mengandung signature Anda"
        body_lines = [
            f"Monitor menemukan sekitar {len(new_found)} file publik yang mengandung signature Anda: `{SIGNATURE}`",
            "",
            "Daftar temuan (repo / path / url):",
        ]
        for it in new_found:
            body_lines.append(f"- {it['repository']}/{it['path']} — {it['html_url']}")
        body_lines.append("")
        body_lines.append("Langkah selanjutnya: silakan cek repositori di atas. Jika harus, ajukan permintaan penghapusan (DMCA) atau hubungi pemilik repository.")
        body = "\n".join(body_lines)

        issue_url = create_issue_in_output_repo(title, body)
        if issue_url:
            print(f"Issue dibuat: {issue_url}")

        # Kirim ke webhook (opsional)
        if ALERT_WEBHOOK:
            payload = {
                "content": f"Found {len(new_found)} repos containing your signature `{SIGNATURE}`. See issue: {issue_url}"
            }
            notify_webhook(ALERT_WEBHOOK, payload)

    # simpan state
    save_state({"seen": list(seen)})
    print("Selesai.")

if __name__ == "__main__":
    main()

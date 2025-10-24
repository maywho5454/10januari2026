# scripts/sync_guard.py
import os
import sys
import json
import urllib.request

ALLOWED_USERS = {"maywho5454"}     # hanya pemilik asli
DENY_LIST     = {"Novantama"}      # blokir spesifik

def _gh_api(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "sync-guard"
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def _who_am_i_via_token(token: str) -> str | None:
    try:
        data = _gh_api("https://api.github.com/user", token)
        return data.get("login")
    except Exception:
        return None

def ensure_only_owner_can_sync():
    actor  = os.getenv("GITHUB_ACTOR", "").strip()
    repo   = os.getenv("GITHUB_REPOSITORY", "").strip()
    token  = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("GITHUB_PAT")

    # 1) Blokir daftar hitam dulu
    if actor in DENY_LIST:
        sys.stderr.write(f"❌ Akses ditolak: actor '{actor}' diblokir.\n")
        sys.exit(99)

    # 2) Wajib: actor harus pemilik
    if actor not in ALLOWED_USERS:
        sys.stderr.write(f"❌ Akses ditolak: hanya {ALLOWED_USERS} yang boleh auto-sync. Actor sekarang: '{actor}'.\n")
        sys.exit(98)

    # 3) Validasi tambahan via token
    if token:
        token_user = _who_am_i_via_token(token)
        if token_user and token_user not in ALLOWED_USERS:
            sys.stderr.write(
                f"❌ Token milik '{token_user}', bukan {ALLOWED_USERS}. Tidak boleh menjalankan auto-sync di {repo}.\n"
            )
            sys.exit(97)
    else:
        ci = os.getenv("GITHUB_ACTIONS", "")
        if ci == "true":
            sys.stderr.write("❌ Tidak ada token GitHub pada lingkungan Actions. Gagal.\n")
            sys.exit(96)

    print(f"✅ Guard OK. Actor '{actor}' berhak menjalankan auto-sync pada {repo}.")

if __name__ == "__main__":
    ensure_only_owner_can_sync()

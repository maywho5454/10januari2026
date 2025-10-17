import os
import requests
from github import Github, GithubException
from datetime import datetime

# --- KONFIGURASI ---
GITHUB_TOKEN = os.getenv("GITHUB_PAT")
SOURCE_OWNER = "maywho5454"
SOURCE_REPO = "10januari2026"
BLOCKLIST = ["Novantama"]
ISSUE_LABEL = "anti-mirror"
REPORT_ENDPOINT = "https://github.com/contact/dmca/takedown"

def send_dmca_report(offender, repo_url):
    """Kirim draft laporan ke GitHub DMCA endpoint"""
    print(f"📩 Menyiapkan laporan DMCA untuk {offender} ...")
    report = f"""
    Kepada GitHub DMCA Team,

    Saya, pemilik akun '{SOURCE_OWNER}', melaporkan pelanggaran hak cipta:
    Repo pelanggar: {repo_url}
    Pemilik: {offender}
    Repo ini menyalin dan mensinkronisasi otomatis dari:
    https://github.com/{SOURCE_OWNER}/{SOURCE_REPO}

    Mohon tindak lanjut sesuai ketentuan DMCA.

    Hormat saya,
    {SOURCE_OWNER}
    """
    with open("dmca_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ Draft laporan DMCA tersimpan: dmca_report.txt")


def block_user(user_obj, username):
    try:
        user_obj.block(username)
        print(f"🚫 User @{username} berhasil diblokir.")
    except GithubException as e:
        print(f"⚠️ Gagal blokir @{username}: {e}")


def main():
    if not GITHUB_TOKEN:
        print("❌ Environment variable GITHUB_PAT belum diatur.")
        return

    g = Github(GITHUB_TOKEN)
    me = g.get_user()
    print(f"🔐 Login sebagai: {me.login}")

    try:
        repo = g.get_repo(f"{SOURCE_OWNER}/{SOURCE_REPO}")
    except GithubException as e:
        print(f"❌ Gagal akses repo: {e}")
        return

    forks = repo.get_forks()
    print(f"🔍 Ditemukan {forks.totalCount} fork.")

    for f in forks:
        owner = f.owner.login
        if owner == SOURCE_OWNER:
            continue

        if owner in BLOCKLIST or owner != SOURCE_OWNER:
            print(f"⚠️ Repo mencurigakan: {f.full_name} ({owner})")

            # 1️⃣ Blok user
            block_user(me, owner)

            # 2️⃣ Buat issue di repo kamu
            title = f"🚨 Deteksi Penyalinan Otomatis oleh @{owner}"
            body = f"""
**Repo pelanggar:** [{f.full_name}]({f.html_url})
**Pemilik:** @{owner}
**Waktu:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Repo ini tampak menyalin otomatis konten dari `{SOURCE_REPO}` tanpa izin.
Telah dilakukan blokir otomatis terhadap pengguna tersebut.

🛑 Tindakan selanjutnya: ajukan laporan ke GitHub DMCA jika tidak dihapus dalam 48 jam.
👉 {REPORT_ENDPOINT}
"""

            try:
                repo.create_issue(title=title, body=body, labels=[ISSUE_LABEL])
                print("✅ Issue laporan dibuat.")
            except GithubException as e:
                print(f"⚠️ Gagal buat issue: {e}")

            # 3️⃣ Kirim peringatan ke repo pelanggar
            try:
                if f.has_issues:
                    f.create_issue(
                        title="Peringatan Pelanggaran Otomatis",
                        body="Repo ini menyalin konten dari repo pribadi tanpa izin. Mohon segera hapus."
                    )
                    print(f"📢 Peringatan dikirim ke {f.full_name}")
            except GithubException:
                print(f"⚠️ Tidak bisa kirim peringatan ke {f.full_name}")

            # 4️⃣ Siapkan laporan DMCA
            send_dmca_report(owner, f.html_url)

    print("✅ Pemeriksaan selesai.")


if __name__ == "__main__":
    main()

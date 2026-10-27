"""
E-CV — Static version, no iframes.
Uses only: st.tabs, st.columns, st.markdown(unsafe_allow_html=True).
"""

import html as html_lib
import json
from pathlib import Path

import streamlit as st

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="E-CV", page_icon="📄", layout="wide")

# ── Data (auto-created on first run) ──────────────────────────
DATA_FILE = Path(__file__).parent / "data" / "users.json"
DATA_FILE.parent.mkdir(exist_ok=True)

SEED = {
    "users": [
        {
            "id": "user1", "name": "Ahmad Fauzi", "nim": "221001001",
            "email": "ahmad.fauzi@example.com", "phone": "+62 812-3456-7890",
            "bio": "Mahasiswa Teknik Informatika yang berfokus pada pengembangan web dan mobile.",
            "education": [
                {"degree": "S1 Teknik Informatika", "institution": "Universitas Indonesia", "year": "2022 - Sekarang"},
                {"degree": "SMA IPA", "institution": "SMA Negeri 1 Jakarta", "year": "2019 - 2022"},
            ],
            "experience": [
                {"role": "Web Developer Intern", "company": "PT Teknologi Maju", "year": "2024",
                 "description": "Membangun dashboard admin menggunakan React dan Node.js."},
                {"role": "Freelance Web Developer", "company": "Mandiri", "year": "2023 - Sekarang",
                 "description": "Mengerjakan berbagai proyek landing page dan e-commerce untuk UMKM."},
            ],
            "skills": ["JavaScript", "Python", "React", "Node.js", "MySQL", "Git"],
            "mainProject": {"name": "Sistem Informasi Akademik", "url": "https://github.com/ahmad/siakad"},
            "otherProjects": [
                {"name": "Aplikasi Kasir Sederhana", "url": "https://github.com/ahmad/kasir"},
                {"name": "Portfolio Website", "url": "https://github.com/ahmad/portfolio"},
            ],
            "files": [],
        },
        {
            "id": "user2", "name": "Siti Rahma", "nim": "221001002",
            "email": "siti.rahma@example.com", "phone": "+62 813-9876-5432",
            "bio": "Mahasiswi Sistem Informasi yang tertarik pada analisis data dan UI/UX design.",
            "education": [
                {"degree": "S1 Sistem Informasi", "institution": "Institut Teknologi Bandung", "year": "2022 - Sekarang"},
            ],
            "experience": [
                {"role": "UI/UX Design Intern", "company": "Startup Kreatif", "year": "2024",
                 "description": "Merancang user flow dan wireframe untuk aplikasi mobile."},
            ],
            "skills": ["Figma", "UI Design", "UX Research", "SQL", "Tableau", "Python"],
            "mainProject": {"name": "Dashboard Analitik Penjualan", "url": "https://github.com/siti/dashboard"},
            "otherProjects": [
                {"name": "Redesign Aplikasi OVO", "url": "https://github.com/siti/ovo-redesign"},
            ],
            "files": [],
        },
        {
            "id": "user3", "name": "Budi Santoso", "nim": "221001003",
            "email": "budi.santoso@example.com", "phone": "+62 857-1111-2222",
            "bio": "Mahasiswa Teknik Komputer yang berfokus pada embedded systems dan IoT.",
            "education": [
                {"degree": "S1 Teknik Komputer", "institution": "Universitas Gadjah Mada", "year": "2021 - Sekarang"},
            ],
            "experience": [
                {"role": "IoT Engineer Intern", "company": "PT Smart Device", "year": "2024",
                 "description": "Mengembangkan firmware perangkat IoT berbasis ESP32."},
            ],
            "skills": ["C++", "Arduino", "Raspberry Pi", "Python", "MQTT", "Linux"],
            "mainProject": {"name": "Sistem Monitoring Suhu IoT", "url": "https://github.com/budi/iot-monitor"},
            "otherProjects": [
                {"name": "Smart Home Controller", "url": "https://github.com/budi/smarthome"},
            ],
            "files": [],
        },
    ]
}

if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps(SEED, indent=2, ensure_ascii=False), encoding="utf-8")

users = json.loads(DATA_FILE.read_text(encoding="utf-8"))["users"]

# ── Helper ────────────────────────────────────────────────────
def esc(s):
    return html_lib.escape(str(s if s is not None else ""))


# ── Global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }

    .logo { font-size: 26px; font-weight: 800; margin-bottom: 18px; color: #1a2233; }
    .logo span { color: #3b6fd4; }

    .profile-card {
        background: #fff; border: 1px solid #e3e8f0; border-radius: 16px;
        padding: 26px 22px; text-align: center;
        box-shadow: 0 2px 10px rgba(20,30,60,0.05);
    }
    .avatar {
        width: 100px; height: 100px; border-radius: 50%;
        background: #d4e2f7; color: #3b6fd4;
        display: flex; align-items: center; justify-content: center;
        font-size: 38px; font-weight: 700; margin: 0 auto 16px;
    }
    .p-name { font-size: 20px; font-weight: 700; color: #1a2233; margin: 0 0 4px; }
    .p-nim  { font-size: 13px; color: #6b7a92; margin-bottom: 16px; }
    .p-bio  { font-size: 13px; color: #46536b; line-height: 1.55; margin-bottom: 16px; text-align: left; }
    .p-contact { font-size: 13px; color: #6b7a92; margin: 5px 0; text-align: left; word-break: break-word; }

    .card {
        background: #fff; border: 1px solid #e3e8f0; border-radius: 16px;
        padding: 22px; margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(20,30,60,0.05);
    }
    .card h3 {
        margin: 0 0 14px; font-size: 12px; text-transform: uppercase;
        letter-spacing: 1.2px; color: #6b7a92; font-weight: 700;
    }

    .item { border-left: 3px solid #3b6fd4; padding: 2px 0 2px 14px; margin-bottom: 14px; }
    .item:last-child { margin-bottom: 0; }
    .item .t { font-weight: 600; font-size: 14px; color: #1a2233; }
    .item .s { font-size: 12px; color: #6b7a92; margin-top: 3px; }
    .item .d { font-size: 12px; color: #46536b; margin-top: 6px; line-height: 1.5; }

    .chip {
        display: inline-block; padding: 5px 12px; margin: 3px;
        border-radius: 100px; background: #e8eefb; color: #2a4a80;
        font-size: 12px; font-weight: 500;
    }

    .link-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 14px; margin-bottom: 8px;
        border-radius: 10px; background: #f5f8fd; border: 1px solid #e3e8f0;
        color: #1a2233 !important; text-decoration: none !important; font-size: 13px;
    }
    .link-row:hover { background: #e8eefb; }

    .project-main {
        display: block; padding: 14px; border-radius: 10px;
        background: #e8eefb; color: #2a4a80 !important;
        text-decoration: none !important; font-weight: 600;
        text-align: center; font-size: 14px;
    }
    .project-main:hover { background: #d4e2f7; }

    .empty { font-size: 13px; color: #98a4b8; font-style: italic; padding: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown('<div class="logo">E-<span>CV</span></div>', unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────
tabs = st.tabs([u["name"] for u in users])

for tab, u in zip(tabs, users):
    with tab:
        col_left, col_right = st.columns([1, 2.4], gap="large")

        # ── LEFT: Profile ───────────────────────────────────
        with col_left:
            initials = esc((u["name"] or "?")[0])
            st.markdown(f"""
                <div class="profile-card">
                    <div class="avatar">{initials}</div>
                    <div class="p-name">{esc(u['name'])}</div>
                    <div class="p-nim">NIM {esc(u['nim'])}</div>
                    <div class="p-bio">{esc(u['bio'])}</div>
                    <div class="p-contact">📧 {esc(u['email'])}</div>
                    <div class="p-contact">📱 {esc(u['phone'])}</div>
                </div>
            """, unsafe_allow_html=True)

        # ── RIGHT: Content ──────────────────────────────────
        with col_right:
            # Pendidikan
            edu_html = "".join(
                f'<div class="item"><div class="t">{esc(e.get("degree", ""))}</div>'
                f'<div class="s">{esc(e.get("institution", ""))} · {esc(e.get("year", ""))}</div></div>'
                for e in (u.get("education") or [])
            ) or '<div class="empty">Belum ada data pendidikan.</div>'
            st.markdown(f'<div class="card"><h3>Pendidikan</h3>{edu_html}</div>',
                        unsafe_allow_html=True)

            # Pengalaman
            exp_html = "".join(
                f'<div class="item"><div class="t">{esc(e.get("role", ""))}</div>'
                f'<div class="s">{esc(e.get("company", ""))} · {esc(e.get("year", ""))}</div>'
                f'<div class="d">{esc(e.get("description", ""))}</div></div>'
                for e in (u.get("experience") or [])
            ) or '<div class="empty">Belum ada pengalaman.</div>'
            st.markdown(f'<div class="card"><h3>Pengalaman</h3>{exp_html}</div>',
                        unsafe_allow_html=True)

            # Keahlian
            skill_html = "".join(
                f'<span class="chip">{esc(s)}</span>'
                for s in (u.get("skills") or [])
            ) or '<div class="empty">Belum ada keahlian.</div>'
            st.markdown(f'<div class="card"><h3>Keahlian</h3>{skill_html}</div>',
                        unsafe_allow_html=True)

            # Proyek Utama
            mp = u.get("mainProject") or {}
            mp_name = esc(mp.get("name", "—"))
            mp_url = esc(mp.get("url", "#"))
            st.markdown(
                f'<div class="card"><h3>Proyek Utama</h3>'
                f'<a class="project-main" href="{mp_url}" target="_blank" rel="noopener">{mp_name}</a>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Proyek Lainnya
            proj_html = "".join(
                f'<a class="link-row" href="{esc(p.get("url", "#"))}" target="_blank" rel="noopener">'
                f'<span>🔗 {esc(p.get("name", ""))}</span><span>↗</span></a>'
                for p in (u.get("otherProjects") or [])
            ) or '<div class="empty">Belum ada proyek lain.</div>'
            st.markdown(f'<div class="card"><h3>Proyek Lainnya</h3>{proj_html}</div>',
                        unsafe_allow_html=True)

            # Berkas
            files_html = "".join(
                f'<a class="link-row" href="{esc(f.get("url", "#"))}" target="_blank" rel="noopener">'
                f'<span>{"📄" if f.get("type") == "pdf" else "🖼️"} {esc(f.get("name", ""))}</span>'
                f'<span>⬇️</span></a>'
                for f in (u.get("files") or [])
            ) or '<div class="empty">Belum ada berkas.</div>'
            st.markdown(f'<div class="card"><h3>Berkas</h3>{files_html}</div>',
                        unsafe_allow_html=True)
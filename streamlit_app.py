"""
E-CV — Minimal static version.
No custom component, no wave, no dark mode, no bridge.
Just: load JSON → render HTML via components.html().
"""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="E-CV", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    "<style>"
    "#MainMenu, header, footer {visibility:hidden;}"
    ".block-container {padding:0 !important; max-width:100% !important;}"
    "iframe {display:block; width:100%; border:none;}"
    "</style>",
    unsafe_allow_html=True,
)

# ── Load data (auto-create from seed) ────────────────────────
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
            ],
            "skills": ["JavaScript", "Python", "React", "Node.js", "MySQL", "Git"],
            "mainProject": {"name": "Sistem Informasi Akademik", "url": "https://github.com/ahmad/siakad"},
            "otherProjects": [
                {"name": "Aplikasi Kasir Sederhana", "url": "https://github.com/ahmad/kasir"},
            ],
            "files": [],
        },
        {
            "id": "user2", "name": "Siti Rahma", "nim": "221001002",
            "email": "siti.rahma@example.com", "phone": "+62 813-9876-5432",
            "bio": "Mahasiswi Sistem Informasi yang tertarik pada analisis data dan UI/UX.",
            "education": [
                {"degree": "S1 Sistem Informasi", "institution": "ITB", "year": "2022 - Sekarang"},
            ],
            "experience": [
                {"role": "UI/UX Intern", "company": "Startup Kreatif", "year": "2024",
                 "description": "Merancang user flow dan wireframe aplikasi mobile."},
            ],
            "skills": ["Figma", "UI Design", "SQL", "Tableau", "Python"],
            "mainProject": {"name": "Dashboard Analitik", "url": "https://github.com/siti/dashboard"},
            "otherProjects": [{"name": "Redesign OVO", "url": "https://github.com/siti/ovo"}],
            "files": [],
        },
        {
            "id": "user3", "name": "Budi Santoso", "nim": "221001003",
            "email": "budi.santoso@example.com", "phone": "+62 857-1111-2222",
            "bio": "Mahasiswa Teknik Komputer yang berfokus pada embedded systems dan IoT.",
            "education": [
                {"degree": "S1 Teknik Komputer", "institution": "UGM", "year": "2021 - Sekarang"},
            ],
            "experience": [
                {"role": "IoT Intern", "company": "PT Smart Device", "year": "2024",
                 "description": "Mengembangkan firmware perangkat IoT berbasis ESP32."},
            ],
            "skills": ["C++", "Arduino", "Raspberry Pi", "Python", "MQTT"],
            "mainProject": {"name": "Monitoring Suhu IoT", "url": "https://github.com/budi/iot"},
            "otherProjects": [{"name": "Smart Home", "url": "https://github.com/budi/smarthome"}],
            "files": [],
        },
    ]
}

if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps(SEED, indent=2, ensure_ascii=False), encoding="utf-8")

data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
users = data["users"]

# ── Build static HTML ────────────────────────────────────────
users_json = json.dumps(users, ensure_ascii=False)

html = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 24px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #1a2233;
    background: #eef2f8;
  }
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px; margin-bottom: 24px;
  }
  .logo { font-size: 22px; font-weight: 800; }
  .logo span { color: #3b6fd4; }
  .tabs { display: flex; gap: 8px; flex-wrap: wrap; }
  .tab {
    padding: 9px 18px; border-radius: 100px;
    border: 1px solid #d4dbe6; background: #fff;
    color: #1a2233; cursor: pointer; font-weight: 500; font-size: 14px;
  }
  .tab:hover { border-color: #3b6fd4; }
  .tab.active { background: #3b6fd4; color: #fff; border-color: #3b6fd4; }

  .dash {
    display: grid; grid-template-columns: 300px 1fr; gap: 20px;
    max-width: 1100px; margin: 0 auto;
  }
  @media (max-width: 800px) { .dash { grid-template-columns: 1fr; } }

  .card {
    background: #fff; border: 1px solid #e3e8f0; border-radius: 16px;
    padding: 22px; box-shadow: 0 2px 10px rgba(20, 30, 60, 0.05);
  }
  .card h3 {
    margin: 0 0 14px; font-size: 12px; text-transform: uppercase;
    letter-spacing: 1.2px; color: #6b7a92; font-weight: 700;
  }

  .profile { text-align: center; }
  .avatar {
    width: 100px; height: 100px; border-radius: 50%;
    background: #d4e2f7; color: #3b6fd4;
    display: flex; align-items: center; justify-content: center;
    font-size: 38px; font-weight: 700; margin: 0 auto 14px;
  }
  .profile h2 { margin: 0 0 4px; font-size: 19px; }
  .profile .nim { font-size: 13px; color: #6b7a92; margin-bottom: 14px; }
  .profile .bio { font-size: 13px; color: #46536b; line-height: 1.5; margin-bottom: 14px; }
  .contact { font-size: 13px; color: #6b7a92; margin: 4px 0; word-break: break-word; }

  .stack { display: flex; flex-direction: column; gap: 16px; }

  .item {
    border-left: 3px solid #3b6fd4;
    padding: 2px 0 2px 14px; margin-bottom: 14px;
  }
  .item:last-child { margin-bottom: 0; }
  .item .t { font-weight: 600; font-size: 14px; }
  .item .s { font-size: 12px; color: #6b7a92; margin-top: 2px; }
  .item .d { font-size: 12px; margin-top: 6px; line-height: 1.5; }

  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip {
    padding: 5px 12px; border-radius: 100px;
    background: #e8eefb; color: #2a4a80; font-size: 12px; font-weight: 500;
  }

  .link-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px; border-radius: 10px;
    background: #f5f8fd; border: 1px solid #e3e8f0;
    color: #1a2233; text-decoration: none; font-size: 13px; margin-bottom: 8px;
  }
  .link-row:hover { background: #e8eefb; }

  .project-main {
    display: block; padding: 14px; border-radius: 10px;
    background: #e8eefb; color: #2a4a80;
    text-decoration: none; font-weight: 600; text-align: center; font-size: 14px;
  }

  .empty { font-size: 13px; color: #98a4b8; font-style: italic; text-align: center; padding: 12px; }
</style>
</head>
<body>

<div class="topbar">
  <div class="logo">E-<span>CV</span></div>
  <div class="tabs" id="tabs"></div>
</div>

<div class="dash" id="content"></div>

<script>
const USERS = __USERS_JSON__;
let activeId = USERS[0].id;

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function render() {
  // Tabs
  document.getElementById('tabs').innerHTML = USERS.map(u =>
    `<button class="tab ${u.id === activeId ? 'active' : ''}" onclick="setUser('${u.id}')">${esc(u.name)}</button>`
  ).join('');

  // Content
  const u = USERS.find(x => x.id === activeId);
  const initials = (u.name || '?')[0];

  const eduHtml = (u.education || []).length
    ? u.education.map(e => `<div class="item">
        <div class="t">${esc(e.degree)}</div>
        <div class="s">${esc(e.institution)} · ${esc(e.year)}</div>
      </div>`).join('')
    : '<div class="empty">Belum ada data pendidikan.</div>';

  const expHtml = (u.experience || []).length
    ? u.experience.map(e => `<div class="item">
        <div class="t">${esc(e.role)}</div>
        <div class="s">${esc(e.company)} · ${esc(e.year)}</div>
        <div class="d">${esc(e.description)}</div>
      </div>`).join('')
    : '<div class="empty">Belum ada pengalaman.</div>';

  const skillHtml = (u.skills || []).length
    ? u.skills.map(s => `<span class="chip">${esc(s)}</span>`).join('')
    : '<div class="empty">Belum ada keahlian.</div>';

  const projHtml = (u.otherProjects || []).length
    ? u.otherProjects.map(p =>
        `<a class="link-row" href="${p.url}" target="_blank" rel="noopener">
          <span>🔗 ${esc(p.name)}</span><span>↗</span>
        </a>`).join('')
    : '<div class="empty">Belum ada proyek lain.</div>';

  const fileHtml = (u.files || []).length
    ? u.files.map(f =>
        `<a class="link-row" href="${f.url}" target="_blank" rel="noopener">
          <span>${f.type === 'pdf' ? '📄' : '🖼️'} ${esc(f.name)}</span><span>⬇️</span>
        </a>`).join('')
    : '<div class="empty">Belum ada berkas.</div>';

  document.getElementById('content').innerHTML = `
    <div class="card profile">
      <div class="avatar">${esc(initials)}</div>
      <h2>${esc(u.name)}</h2>
      <div class="nim">NIM ${esc(u.nim)}</div>
      <div class="bio">${esc(u.bio)}</div>
      <div class="contact">📧 ${esc(u.email)}</div>
      <div class="contact">📱 ${esc(u.phone)}</div>
    </div>

    <div class="stack">
      <div class="card"><h3>Pendidikan</h3>${eduHtml}</div>
      <div class="card"><h3>Pengalaman</h3>${expHtml}</div>
      <div class="card"><h3>Keahlian</h3><div class="chips">${skillHtml}</div></div>
      <div class="card"><h3>Proyek Utama</h3>
        <a class="project-main" href="${u.mainProject?.url || '#'}" target="_blank" rel="noopener">
          ${esc(u.mainProject?.name || '—')}
        </a>
      </div>
      <div class="card"><h3>Proyek Lainnya</h3>${projHtml}</div>
      <div class="card"><h3>Berkas</h3>${fileHtml}</div>
    </div>
  `;

  // Auto-resize the iframe
  if (window.Streamlit && window.Streamlit.setFrameHeight) {
    window.Streamlit.setFrameHeight(document.body.scrollHeight + 32);
  }
}

function setUser(id) { activeId = id; render(); }

render();
</script>
</body>
</html>
""".replace("__USERS_JSON__", users_json)

# ── Render ───────────────────────────────────────────────────
components.html(html, height=1400, scrolling=True)
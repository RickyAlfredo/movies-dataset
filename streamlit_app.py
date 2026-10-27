"""
E-CV — Single-file Streamlit app.
All HTML / CSS / JS lives in this file as Python strings.
The component directory is created at runtime before declare_component().

Run:
    streamlit run app.py
Deploy:
    Just upload this one file (plus secrets). Done.
"""

import json
import hashlib
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="E-CV | Digital Portfolio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    "<style>"
    "#MainMenu, header, footer {visibility: hidden;}"
    ".block-container {padding: 0 !important; max-width: 100% !important;}"
    "iframe {border: none; display: block;}"
    "</style>",
    unsafe_allow_html=True,
)

# ════════════════════════════════════════════════════════════════════
# 2. PATHS
# ════════════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "users.json"
COMP_DIR = BASE_DIR / "_ecv_component"
DATA_DIR.mkdir(exist_ok=True)


# ════════════════════════════════════════════════════════════════════
# 3. HELPERS
# ════════════════════════════════════════════════════════════════════
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def is_hash(s: str) -> bool:
    return bool(re.fullmatch(r"[a-f0-9]{64}", s or ""))


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_data() -> dict:
    if not DATA_FILE.exists():
        save_data(SEED)
        data = json.loads(json.dumps(SEED))
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    changed = False
    if not is_hash(data.get("masterPassword", "")):
        data["masterPassword"] = sha256(data["masterPassword"])
        changed = True
    for u in data.get("users", []):
        if not is_hash(u.get("password", "")):
            u["password"] = sha256(u["password"])
            changed = True
    if changed:
        save_data(data)
    return data


# ════════════════════════════════════════════════════════════════════
# 4. SEED DATA (used only on first run)
# ════════════════════════════════════════════════════════════════════
SEED = {
    "masterPassword": "capstone12",
    "users": [
        {
            "id": "user1", "name": "Ahmad Fauzi", "nim": "221001001",
            "email": "ahmad.fauzi@example.com", "phone": "+62 812-3456-7890",
            "bio": "Mahasiswa Teknik Informatika yang berfokus pada pengembangan web dan mobile. Suka belajar hal baru dan membangun proyek open-source.",
            "profilePicture": "", "password": "password123",
            "education": [
                {"degree": "S1 Teknik Informatika", "institution": "Universitas Indonesia", "year": "2022 - Sekarang"},
                {"degree": "SMA IPA", "institution": "SMA Negeri 1 Jakarta", "year": "2019 - 2022"},
            ],
            "experience": [
                {"role": "Web Developer Intern", "company": "PT Teknologi Maju", "year": "2024", "description": "Membangun dashboard admin menggunakan React dan Node.js."},
                {"role": "Freelance Web Developer", "company": "Mandiri", "year": "2023 - Sekarang", "description": "Mengerjakan berbagai proyek landing page dan e-commerce untuk UMKM."},
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
            "bio": "Mahasiswi Sistem Informasi yang tertarik pada analisis data dan UI/UX design. Senang bekerja dalam tim dan berbagi pengetahuan.",
            "profilePicture": "", "password": "password123",
            "education": [
                {"degree": "S1 Sistem Informasi", "institution": "Institut Teknologi Bandung", "year": "2022 - Sekarang"},
            ],
            "experience": [
                {"role": "UI/UX Design Intern", "company": "Startup Kreatif", "year": "2024", "description": "Merancang user flow dan wireframe untuk aplikasi mobile."},
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
            "bio": "Mahasiswa Teknik Komputer yang berfokus pada embedded systems dan IoT. Suka bereksperimen dengan Raspberry Pi dan Arduino.",
            "profilePicture": "", "password": "password123",
            "education": [
                {"degree": "S1 Teknik Komputer", "institution": "Universitas Gadjah Mada", "year": "2021 - Sekarang"},
            ],
            "experience": [
                {"role": "IoT Engineer Intern", "company": "PT Smart Device", "year": "2024", "description": "Mengembangkan firmware perangkat IoT berbasis ESP32."},
            ],
            "skills": ["C++", "Arduino", "Raspberry Pi", "Python", "MQTT", "Linux"],
            "mainProject": {"name": "Sistem Monitoring Suhu IoT", "url": "https://github.com/budi/iot-monitor"},
            "otherProjects": [
                {"name": "Smart Home Controller", "url": "https://github.com/budi/smarthome"},
            ],
            "files": [],
        },
    ],
}

# ════════════════════════════════════════════════════════════════════
# 5. COMPONENT CONTENT — HTML / CSS / JS as strings
# ════════════════════════════════════════════════════════════════════
COMPONENT_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>E-CV</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div id="root"></div>
  <svg id="wave" preserveAspectRatio="none"></svg>
  <script src="https://unpkg.com/streamlit-component-lib@1.4.3/dist/index.js"></script>
  <script src="index.js"></script>
</body>
</html>
"""

COMPONENT_CSS = """:root {
  --bg: linear-gradient(135deg, #f5f7fa 0%, #e9eef5 100%);
  --card-bg: rgba(255, 255, 255, 0.7);
  --card-border: rgba(255, 255, 255, 0.6);
  --text: #1a2233;
  --text-muted: #5b6b83;
  --accent: hsl(210, 70%, 85%);
  --accent-strong: hsl(210, 60%, 55%);
  --wave-1: rgba(120, 160, 255, 0.35);
  --wave-2: rgba(180, 120, 255, 0.30);
  --wave-3: rgba(90, 200, 220, 0.25);
  --shadow: 0 8px 32px rgba(20, 30, 60, 0.10);
  --radius: 20px;
}
body.dark {
  --bg: linear-gradient(135deg, #0e1422 0%, #182338 100%);
  --card-bg: rgba(30, 40, 60, 0.65);
  --card-border: rgba(120, 150, 200, 0.18);
  --text: #eaf0f8;
  --text-muted: #9db0c9;
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
  --wave-1: rgba(60, 90, 180, 0.25);
  --wave-2: rgba(120, 70, 200, 0.22);
  --wave-3: rgba(50, 130, 160, 0.20);
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0; min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text); background: var(--bg);
  transition: background 0.4s, color 0.4s; overflow-x: hidden;
}
#root { padding: 24px 24px 200px; min-height: 100vh; position: relative; z-index: 2; }
#wave { position: fixed; bottom: 0; left: 0; width: 100%; height: 240px; z-index: 0; pointer-events: none; }
.topbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }
.logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
.logo span { color: var(--accent-strong); }
.tabs-bar { display: flex; gap: 8px; flex-wrap: wrap; }
.tab-btn {
  padding: 9px 18px; border-radius: 100px; border: 1px solid var(--card-border);
  background: var(--card-bg); color: var(--text); cursor: pointer; font-weight: 500; font-size: 14px;
  backdrop-filter: blur(10px); transition: all 0.25s;
}
.tab-btn:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
.tab-btn.active { background: var(--accent-strong); color: #fff; border-color: transparent; }
.topbar-actions { display: flex; gap: 8px; align-items: center; }
.icon-btn {
  width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--card-border);
  background: var(--card-bg); cursor: pointer; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(10px); transition: transform 0.2s;
}
.icon-btn:hover { transform: scale(1.08); }
.dashboard { display: grid; grid-template-columns: 320px 1fr; gap: 24px; max-width: 1200px; margin: 0 auto; }
@media (max-width: 880px) { .dashboard { grid-template-columns: 1fr; } }
.card {
  background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius);
  box-shadow: var(--shadow); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  padding: 24px; transition: transform 0.25s, box-shadow 0.25s;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(20,30,60,0.14); }
.card h3 {
  margin: 0 0 16px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1.2px;
  color: var(--text-muted); font-weight: 600;
}
.profile-card { text-align: center; position: sticky; top: 24px; height: fit-content; }
.avatar {
  width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto 16px;
  display: block; background: var(--accent); border: 4px solid var(--card-bg); box-shadow: var(--shadow);
}
.avatar-placeholder {
  width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 16px;
  background: var(--accent); display: flex; align-items: center; justify-content: center;
  font-size: 44px; color: var(--text); font-weight: 700;
}
.profile-card h2 { margin: 0 0 4px; font-size: 20px; }
.profile-card .nim { color: var(--text-muted); font-size: 14px; margin-bottom: 16px; }
.profile-card .bio { font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 16px; }
.contact-line { font-size: 13px; color: var(--text-muted); margin: 6px 0; word-break: break-word; }
.content-col { display: flex; flex-direction: column; gap: 20px; }
.timeline-item { border-left: 3px solid var(--accent-strong); padding: 4px 0 4px 16px; margin-bottom: 16px; }
.timeline-item:last-child { margin-bottom: 0; }
.timeline-item .title { font-weight: 600; font-size: 15px; }
.timeline-item .sub { color: var(--text-muted); font-size: 13px; }
.timeline-item .desc { margin-top: 6px; font-size: 13px; line-height: 1.5; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 14px; border-radius: 100px; background: var(--accent); color: var(--text); font-size: 13px; font-weight: 500; }
.file-list { display: flex; flex-direction: column; gap: 10px; }
.file-link {
  display: flex; align-items: center; justify-content: space-between; padding: 12px 16px;
  border-radius: 12px; background: rgba(255,255,255,0.4); border: 1px solid var(--card-border);
  color: var(--text); text-decoration: none; font-size: 14px; transition: background 0.2s;
}
body.dark .file-link { background: rgba(60,80,120,0.25); }
.file-link:hover { background: var(--accent); }
.project-main {
  display: block; padding: 16px; border-radius: 12px; background: var(--accent);
  color: var(--text); text-decoration: none; font-weight: 600; text-align: center; transition: transform 0.2s;
}
.project-main:hover { transform: scale(1.02); }
.btn { padding: 10px 22px; border-radius: 100px; border: none; cursor: pointer; font-size: 14px; font-weight: 600; transition: transform 0.15s, opacity 0.15s; }
.btn:hover { transform: translateY(-1px); opacity: 0.92; }
.btn-primary { background: var(--accent-strong); color: #fff; }
.btn-ghost { background: transparent; border: 1px solid var(--card-border); color: var(--text); }
.btn-danger { background: #e5484d; color: #fff; }
.btn-sm { padding: 6px 14px; font-size: 12px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-muted); }
.form-group input, .form-group textarea, .form-group select {
  width: 100%; padding: 10px 14px; border-radius: 10px; border: 1px solid var(--card-border);
  background: rgba(255,255,255,0.5); color: var(--text); font-family: inherit; font-size: 14px;
  outline: none; transition: border-color 0.2s, background 0.2s;
}
body.dark .form-group input, body.dark .form-group textarea, body.dark .form-group select { background: rgba(40,55,85,0.5); }
.form-group input:focus, .form-group textarea:focus { border-color: var(--accent-strong); }
.form-group textarea { min-height: 90px; resize: vertical; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 640px) { .row2 { grid-template-columns: 1fr; } }
.dyn-row { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 8px; margin-bottom: 8px; align-items: center; }
.dyn-row-2 { grid-template-columns: 1fr 1fr auto; }
.dyn-row input { padding: 8px 12px; font-size: 13px; }
.toast {
  position: fixed; top: 20px; right: 20px; padding: 14px 22px; border-radius: 12px;
  font-size: 14px; font-weight: 500; box-shadow: var(--shadow); z-index: 1000;
  animation: slideIn 0.3s ease; max-width: 320px;
}
.toast.success { background: #22c55e; color: #fff; }
.toast.error { background: #e5484d; color: #fff; }
@keyframes slideIn { from { transform: translateX(120%); } to { transform: translateX(0); } }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(10, 15, 30, 0.45); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center; z-index: 500;
}
.modal {
  background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius);
  box-shadow: var(--shadow); padding: 36px 32px; width: 100%; max-width: 400px; backdrop-filter: blur(20px);
}
.modal h2 { margin: 0 0 6px; font-size: 22px; }
.modal .sub { color: var(--text-muted); font-size: 13px; margin-bottom: 24px; }
.admin-shell { max-width: 1100px; margin: 0 auto; }
.admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.admin-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.empty { text-align: center; color: var(--text-muted); font-size: 14px; padding: 20px; font-style: italic; }
"""

COMPONENT_JS = """/* E-CV Streamlit Custom Component — full frontend */
const ROOT = document.getElementById('root');

const state = {
  users: [],
  session: { loggedInAs: null, isMaster: false, message: null },
  view: localStorage.getItem('ecv_view') || 'public',
  activeUserId: localStorage.getItem('ecv_activeUser') || '',
  adminTab: 'edit-data',
  adminTargetId: '',
  darkMode: localStorage.getItem('ecv_darkMode') === 'true',
  lastMessageId: '',
};

function sendAction(obj) {
  obj.actionId = Date.now() + Math.random();
  Streamlit.setComponentValue(obj);
}

function escapeHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function paletteFor(userId) {
  let hash = 0;
  for (let i = 0; i < userId.length; i++) hash = userId.charCodeAt(i) + ((hash << 5) - hash);
  const h = Math.abs(hash) % 360;
  return {
    accent: `hsl(${h}, 70%, 85%)`,
    accentStrong: `hsl(${h}, 60%, 55%)`,
    wave1: `hsla(${h}, 70%, 65%, 0.35)`,
    wave2: `hsla(${(h + 40) % 360}, 70%, 65%, 0.30)`,
    wave3: `hsla(${(h + 80) % 360}, 70%, 65%, 0.25)`,
  };
}

function applyPalette(userId) {
  if (!userId) return;
  const p = paletteFor(userId);
  const r = document.documentElement;
  r.style.setProperty('--accent', p.accent);
  r.style.setProperty('--accent-strong', p.accentStrong);
  r.style.setProperty('--wave-1', p.wave1);
  r.style.setProperty('--wave-2', p.wave2);
  r.style.setProperty('--wave-3', p.wave3);
}

function currentUser() {
  return state.users.find(u => u.id === state.activeUserId) || state.users[0] || null;
}

function buildWave() {
  const svg = document.getElementById('wave');
  svg.setAttribute('viewBox', '0 0 1440 240');
  svg.innerHTML = `
    <path fill="var(--wave-1)" d="M0,120 C240,40 480,200 720,140 C960,80 1200,200 1440,140 L1440,240 L0,240 Z">
      <animate attributeName="d" dur="14s" repeatCount="indefinite"
        values="M0,120 C240,40 480,200 720,140 C960,80 1200,200 1440,140 L1440,240 L0,240 Z;
                M0,140 C240,200 480,60 720,120 C960,180 1200,40 1440,160 L1440,240 L0,240 Z;
                M0,120 C240,40 480,200 720,140 C960,80 1200,200 1440,140 L1440,240 L0,240 Z"/>
    </path>
    <path fill="var(--wave-2)" d="M0,160 C240,100 480,240 720,180 C960,120 1200,240 1440,180 L1440,240 L0,240 Z">
      <animate attributeName="d" dur="18s" repeatCount="indefinite"
        values="M0,160 C240,100 480,240 720,180 C960,120 1200,240 1440,180 L1440,240 L0,240 Z;
                M0,180 C240,240 480,120 720,160 C960,220 1200,100 1440,200 L1440,240 L0,240 Z;
                M0,160 C240,100 480,240 720,180 C960,120 1200,240 1440,180 L1440,240 L0,240 Z"/>
    </path>
    <path fill="var(--wave-3)" d="M0,200 C240,160 480,260 720,220 C960,180 1200,280 1440,220 L1440,240 L0,240 Z">
      <animate attributeName="d" dur="22s" repeatCount="indefinite"
        values="M0,200 C240,160 480,260 720,220 C960,180 1200,280 1440,220 L1440,240 L0,240 Z;
                M0,220 C240,260 480,160 720,200 C960,240 1200,140 1440,240 L1440,240 L0,240 Z;
                M0,200 C240,160 480,260 720,220 C960,180 1200,280 1440,220 L1440,240 L0,240 Z"/>
    </path>
  `;
}

let keyBuffer = '';
document.addEventListener('keydown', (e) => {
  if (e.key.length === 1) {
    keyBuffer = (keyBuffer + e.key.toLowerCase()).slice(-20);
    if (keyBuffer.includes('capstone12') && state.view !== 'admin-panel') {
      keyBuffer = '';
      setView('admin-login');
    }
  }
});

function render() {
  document.body.classList.toggle('dark', state.darkMode);
  if (state.view === 'public') renderPublic();
  else if (state.view === 'admin-login') renderAdminLogin();
  else if (state.view === 'admin-panel') renderAdminPanel();

  const msg = state.session.message;
  if (msg && msg.text && msg.text !== state.lastMessageId) {
    state.lastMessageId = msg.text;
    const t = document.createElement('div');
    t.className = `toast ${msg.type || 'success'}`;
    t.textContent = msg.text;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  }
  Streamlit.setFrameHeight(document.body.scrollHeight + 40);
}

function setView(v) {
  state.view = v;
  localStorage.setItem('ecv_view', v);
  render();
}

function setActiveUser(id) {
  state.activeUserId = id;
  localStorage.setItem('ecv_activeUser', id);
  applyPalette(id);
  render();
}

function renderPublic() {
  const u = currentUser();
  if (!u) { ROOT.innerHTML = `<div class="empty">Data pengguna belum tersedia.</div>`; return; }
  applyPalette(u.id);
  const tabs = state.users.map(x => `
    <button class="tab-btn ${x.id === u.id ? 'active' : ''}" onclick="setActiveUser('${x.id}')">
      ${escapeHtml(x.name)}
    </button>`).join('');
  const edu = (u.education || []).map(e => `
    <div class="timeline-item">
      <div class="title">${escapeHtml(e.degree)}</div>
      <div class="sub">${escapeHtml(e.institution)} · ${escapeHtml(e.year)}</div>
    </div>`).join('') || '<div class="empty">Belum ada data pendidikan.</div>';
  const exp = (u.experience || []).map(e => `
    <div class="timeline-item">
      <div class="title">${escapeHtml(e.role)}</div>
      <div class="sub">${escapeHtml(e.company)} · ${escapeHtml(e.year)}</div>
      <div class="desc">${escapeHtml(e.description)}</div>
    </div>`).join('') || '<div class="empty">Belum ada pengalaman.</div>';
  const skills = (u.skills || []).map(s => `<span class="chip">${escapeHtml(s)}</span>`).join('');
  const files = (u.files || []).map(f => `
    <a class="file-link" href="${f.url}" target="_blank" rel="noopener">
      <span>${f.type === 'pdf' ? '📄' : '🖼️'} ${escapeHtml(f.name)}</span>
      <span>⬇️</span>
    </a>`).join('') || '<div class="empty">Belum ada berkas.</div>';
  const otherProjects = (u.otherProjects || []).map(p => `
    <a class="file-link" href="${p.url}" target="_blank" rel="noopener">
      <span>🔗 ${escapeHtml(p.name)}</span>
      <span>↗</span>
    </a>`).join('') || '<div class="empty">Belum ada proyek lain.</div>';
  const avatar = u.profilePicture
    ? `<img class="avatar" src="${u.profilePicture}" alt="${escapeHtml(u.name)}" />`
    : `<div class="avatar-placeholder">${escapeHtml((u.name || '?')[0])}</div>`;

  ROOT.innerHTML = `
    <div class="topbar">
      <div class="logo">E-<span>CV</span></div>
      <div class="tabs-bar">${tabs}</div>
      <div class="topbar-actions">
        <button class="icon-btn" id="toggle-dark" title="Mode Gelap">${state.darkMode ? '☀️' : '🌙'}</button>
      </div>
    </div>
    <div class="dashboard">
      <div class="card profile-card">
        ${avatar}
        <h2>${escapeHtml(u.name)}</h2>
        <div class="nim">NIM ${escapeHtml(u.nim)}</div>
        <div class="bio">${escapeHtml(u.bio)}</div>
        <div class="contact-line">📧 ${escapeHtml(u.email)}</div>
        <div class="contact-line">📱 ${escapeHtml(u.phone)}</div>
      </div>
      <div class="content-col">
        <div class="card"><h3>Pendidikan</h3>${edu}</div>
        <div class="card"><h3>Pengalaman</h3>${exp}</div>
        <div class="card"><h3>Keahlian</h3><div class="chips">${skills || '<div class="empty">Belum ada keahlian.</div>'}</div></div>
        <div class="card"><h3>Proyek Utama</h3>
          <a class="project-main" href="${u.mainProject?.url || '#'}" target="_blank" rel="noopener">
            ${escapeHtml(u.mainProject?.name || 'Belum ada proyek utama')}
          </a>
        </div>
        <div class="card"><h3>Proyek Lainnya</h3><div class="file-list">${otherProjects}</div></div>
        <div class="card"><h3>Berkas</h3><div class="file-list">${files}</div></div>
      </div>
    </div>`;

  document.getElementById('toggle-dark').onclick = () => {
    state.darkMode = !state.darkMode;
    localStorage.setItem('ecv_darkMode', state.darkMode);
    render();
  };
}

function renderAdminLogin() {
  ROOT.innerHTML = `
    <div class="topbar">
      <div class="logo">E-<span>CV</span> · Admin</div>
      <div class="topbar-actions"><button class="btn btn-ghost" id="back-btn">← Kembali</button></div>
    </div>
    <div class="modal-overlay" style="position:static; background:transparent; backdrop-filter:none; padding:40px 0;">
      <div class="modal">
        <h2>Login Admin</h2>
        <div class="sub">Masukkan NIM + sandi Anda, atau <b>master</b> + sandi master.</div>
        <div class="form-group"><label>NIM / Username</label><input id="username" type="text" placeholder="Contoh: 221001001 atau master" /></div>
        <div class="form-group"><label>Sandi</label><input id="password" type="password" placeholder="••••••••" /></div>
        <button class="btn btn-primary" id="login-btn" style="width:100%">Masuk</button>
      </div>
    </div>`;
  document.getElementById('back-btn').onclick = () => setView('public');
  document.getElementById('login-btn').onclick = () => {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    if (!username || !password) return;
    sendAction({ action: 'login', username, password });
  };
  document.getElementById('password').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('login-btn').click();
  });
}

function renderAdminPanel() {
  if (!state.session.loggedInAs) { setView('admin-login'); return; }
  const isMaster = state.session.isMaster;
  const target = isMaster
    ? (state.users.find(u => u.id === state.adminTargetId) || state.users[0])
    : (state.users.find(u => u.id === state.session.loggedInAs) || state.users[0]);
  if (!target) { setView('admin-login'); return; }
  if (!state.adminTargetId) state.adminTargetId = target.id;

  const tabsHtml = ['edit-data', 'files', 'change-password']
    .concat(isMaster ? ['reset-password'] : [])
    .map(t => {
      const labels = { 'edit-data': 'Edit Data', 'files': 'Berkas', 'change-password': 'Ubah Sandi', 'reset-password': 'Reset Sandi (Master)' };
      return `<button class="tab-btn ${state.adminTab === t ? 'active' : ''}" data-admintab="${t}">${labels[t]}</button>`;
    }).join('');

  const userSelector = isMaster ? `
    <div class="form-group"><label>Pilih Pengguna</label>
      <select id="admin-user-select">
        ${state.users.map(u => `<option value="${u.id}" ${u.id === target.id ? 'selected' : ''}>${escapeHtml(u.name)} (${escapeHtml(u.nim)})</option>`).join('')}
      </select>
    </div>` : '';

  let body = '';
  if (state.adminTab === 'edit-data') body = renderEditDataForm(target);
  else if (state.adminTab === 'files') body = renderFilesManager(target);
  else if (state.adminTab === 'change-password') body = renderChangePassword();
  else if (state.adminTab === 'reset-password') body = renderResetPassword(target);

  ROOT.innerHTML = `
    <div class="admin-shell">
      <div class="admin-header">
        <div class="logo">E-<span>CV</span> · Admin Panel</div>
        <div class="topbar-actions">
          <button class="btn btn-ghost" id="view-public">Lihat Publik</button>
          <button class="btn btn-danger" id="logout">Keluar</button>
        </div>
      </div>
      <div class="card">
        ${userSelector}
        <div class="admin-tabs">${tabsHtml}</div>
        <div id="admin-body">${body}</div>
      </div>
    </div>`;

  document.getElementById('view-public').onclick = () => setView('public');
  document.getElementById('logout').onclick = () => sendAction({ action: 'logout' });
  document.querySelectorAll('[data-admintab]').forEach(btn => {
    btn.onclick = () => { state.adminTab = btn.dataset.admintab; render(); };
  });
  const sel = document.getElementById('admin-user-select');
  if (sel) sel.onchange = () => { state.adminTargetId = sel.value; render(); };

  if (state.adminTab === 'edit-data') wireEditData(target);
  else if (state.adminTab === 'files') wireFiles(target);
  else if (state.adminTab === 'change-password') wireChangePassword();
  else if (state.adminTab === 'reset-password') wireResetPassword(target);
}

function renderEditDataForm(u) {
  const eduRows = (u.education || []).map(e => eduRowHtml(e)).join('');
  const expRows = (u.experience || []).map(e => expRowHtml(e)).join('');
  const projRows = (u.otherProjects || []).map(p => projRowHtml(p)).join('');
  return `
    <div class="row2">
      <div class="form-group"><label>Nama Lengkap</label><input id="f-name" type="text" value="${escapeHtml(u.name)}" /></div>
      <div class="form-group"><label>NIM</label><input id="f-nim" type="text" value="${escapeHtml(u.nim)}" /></div>
    </div>
    <div class="row2">
      <div class="form-group"><label>Email</label><input id="f-email" type="email" value="${escapeHtml(u.email)}" /></div>
      <div class="form-group"><label>Telepon</label><input id="f-phone" type="text" value="${escapeHtml(u.phone)}" /></div>
    </div>
    <div class="form-group"><label>Bio</label><textarea id="f-bio">${escapeHtml(u.bio)}</textarea></div>
    <div class="form-group"><label>Keahlian (pisahkan dengan koma)</label><input id="f-skills" type="text" value="${escapeHtml((u.skills || []).join(', '))}" /></div>
    <div class="form-group">
      <label>Foto Profil</label>
      <input id="f-avatar" type="file" accept="image/png,image/jpeg" />
      <div style="font-size:12px; color:var(--text-muted); margin-top:6px;">Maksimal 5 MB · format .png / .jpeg</div>
    </div>
    <div class="form-group"><label>Pendidikan</label><div id="edu-list">${eduRows}</div><button class="btn btn-ghost btn-sm" id="add-edu" type="button">+ Tambah Pendidikan</button></div>
    <div class="form-group"><label>Pengalaman</label><div id="exp-list">${expRows}</div><button class="btn btn-ghost btn-sm" id="add-exp" type="button">+ Tambah Pengalaman</button></div>
    <div class="row2">
      <div class="form-group"><label>Nama Proyek Utama</label><input id="f-mainproj-name" type="text" value="${escapeHtml(u.mainProject?.name || '')}" /></div>
      <div class="form-group"><label>URL Proyek Utama</label><input id="f-mainproj-url" type="text" value="${escapeHtml(u.mainProject?.url || '')}" /></div>
    </div>
    <div class="form-group"><label>Proyek Lainnya</label><div id="proj-list">${projRows}</div><button class="btn btn-ghost btn-sm" id="add-proj" type="button">+ Tambah Proyek</button></div>
    <button class="btn btn-primary" id="save-profile" style="width:100%; margin-top:12px;">Simpan Perubahan</button>`;
}

function eduRowHtml(e = {}) {
  return `<div class="dyn-row" data-edu-row>
    <input type="text" placeholder="Gelar / Jenjang" value="${escapeHtml(e.degree || '')}" data-field="degree" />
    <input type="text" placeholder="Institusi" value="${escapeHtml(e.institution || '')}" data-field="institution" />
    <input type="text" placeholder="Tahun" value="${escapeHtml(e.year || '')}" data-field="year" />
    <button class="btn btn-danger btn-sm" data-remove-edu type="button">✕</button>
  </div>`;
}
function expRowHtml(e = {}) {
  return `<div class="dyn-row" data-exp-row style="grid-template-columns:1fr 1fr 1fr; margin-bottom:4px;">
    <input type="text" placeholder="Peran" value="${escapeHtml(e.role || '')}" data-field="role" />
    <input type="text" placeholder="Perusahaan" value="${escapeHtml(e.company || '')}" data-field="company" />
    <input type="text" placeholder="Tahun" value="${escapeHtml(e.year || '')}" data-field="year" />
  </div>
  <div class="dyn-row" data-exp-row style="grid-template-columns:1fr auto; margin-bottom:12px;">
    <input type="text" placeholder="Deskripsi" value="${escapeHtml(e.description || '')}" data-field="description" />
    <button class="btn btn-danger btn-sm" data-remove-exp type="button">✕</button>
  </div>`;
}
function projRowHtml(p = {}) {
  return `<div class="dyn-row" data-proj-row style="grid-template-columns:1fr 1fr auto;">
    <input type="text" placeholder="Nama Proyek" value="${escapeHtml(p.name || '')}" data-field="name" />
    <input type="text" placeholder="URL" value="${escapeHtml(p.url || '')}" data-field="url" />
    <button class="btn btn-danger btn-sm" data-remove-proj type="button">✕</button>
  </div>`;
}

function wireEditData(u) {
  document.getElementById('add-edu').onclick = () => {
    document.getElementById('edu-list').insertAdjacentHTML('beforeend', eduRowHtml());
    bindRemoveButtons();
  };
  document.getElementById('add-exp').onclick = () => {
    document.getElementById('exp-list').insertAdjacentHTML('beforeend', expRowHtml());
    bindRemoveButtons();
  };
  document.getElementById('add-proj').onclick = () => {
    document.getElementById('proj-list').insertAdjacentHTML('beforeend', projRowHtml());
    bindRemoveButtons();
  };
  bindRemoveButtons();

  document.getElementById('f-avatar').onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { alert('Ukuran berkas melebihi 5 MB.'); e.target.value = ''; return; }
    const reader = new FileReader();
    reader.onload = () => {
      sendAction({
        action: 'upload-file', userId: u.id, kind: 'avatar',
        filename: file.name, fileType: file.type,
        fileBase64: String(reader.result).split(',')[1],
      });
    };
    reader.readAsDataURL(file);
  };

  document.getElementById('save-profile').onclick = () => {
    const payload = {
      name: document.getElementById('f-name').value,
      nim: document.getElementById('f-nim').value,
      email: document.getElementById('f-email').value,
      phone: document.getElementById('f-phone').value,
      bio: document.getElementById('f-bio').value,
      skills: document.getElementById('f-skills').value.split(',').map(s => s.trim()),
      education: [...document.querySelectorAll('[data-edu-row]')].map(row => ({
        degree: row.querySelector('[data-field="degree"]').value,
        institution: row.querySelector('[data-field="institution"]').value,
        year: row.querySelector('[data-field="year"]').value,
      })),
      experience: (() => {
        const rows = [...document.querySelectorAll('[data-exp-row]')];
        const out = [];
        for (let i = 0; i < rows.length; i += 2) {
          out.push({
            role: rows[i].querySelector('[data-field="role"]')?.value || '',
            company: rows[i].querySelector('[data-field="company"]')?.value || '',
            year: rows[i].querySelector('[data-field="year"]')?.value || '',
            description: rows[i + 1]?.querySelector('[data-field="description"]')?.value || '',
          });
        }
        return out;
      })(),
      mainProject: {
        name: document.getElementById('f-mainproj-name').value,
        url: document.getElementById('f-mainproj-url').value,
      },
      otherProjects: [...document.querySelectorAll('[data-proj-row]')].map(row => ({
        name: row.querySelector('[data-field="name"]').value,
        url: row.querySelector('[data-field="url"]').value,
      })),
    };
    sendAction({ action: 'update-profile', userId: u.id, data: payload });
  };
}

function bindRemoveButtons() {
  document.querySelectorAll('[data-remove-edu]').forEach(b => b.onclick = () => b.closest('[data-edu-row]').remove());
  document.querySelectorAll('[data-remove-exp]').forEach(b => b.onclick = () => {
    const descRow = b.closest('[data-exp-row]');
    const mainRow = descRow?.previousElementSibling;
    if (mainRow?.hasAttribute('data-exp-row')) mainRow.remove();
    descRow?.remove();
  });
  document.querySelectorAll('[data-remove-proj]').forEach(b => b.onclick = () => b.closest('[data-proj-row]').remove());
}

function renderFilesManager(u) {
  const rows = (u.files || []).map(f => `
    <div class="file-link" style="margin-bottom:8px;">
      <span>${f.type === 'pdf' ? '📄' : '🖼️'} ${escapeHtml(f.name)}</span>
      <div style="display:flex; gap:8px;">
        <a href="${f.url}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm" style="text-decoration:none;">Lihat</a>
        <button class="btn btn-danger btn-sm" data-del-url="${f.url}">Hapus</button>
      </div>
    </div>`).join('') || '<div class="empty">Belum ada berkas.</div>';
  return `
    <div class="form-group">
      <label>Unggah Berkas Baru (.pdf, .png, .jpeg · maks 5 MB)</label>
      <input id="f-upload" type="file" accept=".pdf,image/png,image/jpeg" />
    </div>
    <hr style="border-color:var(--card-border); margin:20px 0;" />
    <div class="file-list">${rows}</div>`;
}

function wireFiles(u) {
  document.getElementById('f-upload').onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!['application/pdf', 'image/png', 'image/jpeg'].includes(file.type)) {
      alert('Hanya .pdf, .png, .jpeg yang diizinkan.'); e.target.value = ''; return;
    }
    if (file.size > 5 * 1024 * 1024) { alert('Ukuran berkas melebihi 5 MB.'); e.target.value = ''; return; }
    const reader = new FileReader();
    reader.onload = () => {
      sendAction({
        action: 'upload-file', userId: u.id, kind: 'file',
        filename: file.name, fileType: file.type,
        fileBase64: String(reader.result).split(',')[1],
      });
    };
    reader.readAsDataURL(file);
  };
  document.querySelectorAll('[data-del-url]').forEach(btn => {
    btn.onclick = () => {
      if (!confirm('Hapus berkas ini?')) return;
      sendAction({ action: 'delete-file', userId: u.id, url: btn.dataset.delUrl });
    };
  });
}

function renderChangePassword() {
  return `
    <div class="form-group"><label>Sandi Lama</label><input id="old-pwd" type="password" /></div>
    <div class="form-group"><label>Sandi Baru (min 6 karakter)</label><input id="new-pwd" type="password" /></div>
    <button class="btn btn-primary" id="save-pwd" style="width:100%;">Ubah Sandi</button>`;
}
function wireChangePassword() {
  document.getElementById('save-pwd').onclick = () => {
    const oldPassword = document.getElementById('old-pwd').value;
    const newPassword = document.getElementById('new-pwd').value;
    if (!oldPassword || !newPassword) return;
    sendAction({ action: 'change-password', oldPassword, newPassword });
  };
}

function renderResetPassword(target) {
  return `
    <div class="form-group">
      <label>Reset sandi untuk: <b>${escapeHtml(target.name)}</b> (${escapeHtml(target.nim)})</label>
      <input id="reset-pwd" type="password" placeholder="Sandi baru (min 6 karakter)" />
    </div>
    <button class="btn btn-primary" id="do-reset" style="width:100%;">Reset Sandi</button>`;
}
function wireResetPassword(target) {
  document.getElementById('do-reset').onclick = () => {
    const newPassword = document.getElementById('reset-pwd').value;
    if (!newPassword || newPassword.length < 6) { alert('Minimal 6 karakter.'); return; }
    if (!confirm(`Reset sandi ${target.name}?`)) return;
    sendAction({ action: 'reset-password', userId: target.id, newPassword });
  };
}

function onRender(event) {
  const args = event.detail.args || {};
  state.users = args.users || [];
  state.session = args.session || { loggedInAs: null, isMaster: false, message: null };
  if (state.session.loggedInAs) {
    if (state.view !== 'admin-panel') setView('admin-panel');
  } else if (state.view === 'admin-panel') {
    setView('admin-login');
  }
  if (!state.activeUserId || !state.users.find(u => u.id === state.activeUserId)) {
    if (state.users.length) {
      state.activeUserId = state.users[0].id;
      localStorage.setItem('ecv_activeUser', state.activeUserId);
    }
  }
  render();
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();

buildWave();
render();
"""


# ════════════════════════════════════════════════════════════════════
# 6. WRITE COMPONENT FILES AT RUNTIME + DECLARE COMPONENT
# ════════════════════════════════════════════════════════════════════
def ensure_component_files() -> Path:
    """Create the component folder on disk if it isn't there yet."""
    COMP_DIR.mkdir(exist_ok=True)
    files = {
        "index.html": COMPONENT_HTML,
        "style.css": COMPONENT_CSS,
        "index.js": COMPONENT_JS,
    }
    for name, content in files.items():
        f = COMP_DIR / name
        if not f.exists() or f.read_text(encoding="utf-8") != content:
            f.write_text(content, encoding="utf-8")
    return COMP_DIR


ensure_component_files()
_ecv = components.declare_component("ecv", path=str(COMP_DIR))


# ════════════════════════════════════════════════════════════════════
# 7. CLOUDINARY SETUP
# ════════════════════════════════════════════════════════════════════
CLOUDINARY_READY = False
try:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=st.secrets["cloudinary"]["cloud_name"],
        api_key=st.secrets["cloudinary"]["api_key"],
        api_secret=st.secrets["cloudinary"]["api_secret"],
        secure=True,
    )
    CLOUDINARY_READY = True
except Exception:
    CLOUDINARY_READY = False


# ════════════════════════════════════════════════════════════════════
# 8. SESSION STATE
# ════════════════════════════════════════════════════════════════════
if "session" not in st.session_state:
    st.session_state.session = {"loggedInAs": None, "isMaster": False, "message": None}
if "lastActionId" not in st.session_state:
    st.session_state.lastActionId = 0


# ════════════════════════════════════════════════════════════════════
# 9. ACTION HANDLER
# ════════════════════════════════════════════════════════════════════
def process_action(act: dict, data: dict) -> bool:
    action = act.get("action")
    session = st.session_state.session

    if action == "login":
        username = (act.get("username") or "").strip()
        pwd_hash = sha256(act.get("password") or "")
        if username.lower() == "master" and pwd_hash == data["masterPassword"]:
            st.session_state.session = {
                "loggedInAs": "master", "isMaster": True,
                "message": {"type": "success", "text": "Login Master berhasil."},
            }
            return True
        for u in data["users"]:
            if u["nim"] == username and u["password"] == pwd_hash:
                st.session_state.session = {
                    "loggedInAs": u["id"], "isMaster": False,
                    "message": {"type": "success", "text": f"Selamat datang, {u['name']}."},
                }
                return True
        session["message"] = {"type": "error", "text": "NIM atau sandi salah."}
        st.session_state.session = session
        return True

    if action == "logout":
        st.session_state.session = {"loggedInAs": None, "isMaster": False, "message": None}
        return True

    if action == "clear-message":
        session["message"] = None
        st.session_state.session = session
        return False

    if not session.get("loggedInAs"):
        return False

    target_id = session["loggedInAs"]
    if session.get("isMaster"):
        target_id = act.get("userId") or target_id

    user = next((u for u in data["users"] if u["id"] == target_id), None)
    if not user and action != "reset-password":
        return False

    if action == "update-profile":
        payload = act.get("data") or {}
        for field in ("name", "nim", "email", "phone", "bio"):
            if field in payload:
                user[field] = str(payload[field]).strip()
        if "skills" in payload:
            user["skills"] = [s.strip() for s in payload["skills"] if s.strip()]
        if "education" in payload:
            user["education"] = payload["education"]
        if "experience" in payload:
            user["experience"] = payload["experience"]
        if "mainProject" in payload:
            user["mainProject"] = payload["mainProject"]
        if "otherProjects" in payload:
            user["otherProjects"] = payload["otherProjects"]
        save_data(data)
        st.session_state.session["message"] = {"type": "success", "text": "Data berhasil diperbarui."}
        return True

    if action == "upload-file":
        if not CLOUDINARY_READY:
            st.session_state.session["message"] = {"type": "error", "text": "Cloudinary belum dikonfigurasi."}
            return True
        filename = act.get("filename") or "file"
        file_type = act.get("fileType") or ""
        file_b64 = act.get("fileBase64") or ""
        kind = act.get("kind") or "file"
        if "pdf" not in file_type and not file_type.startswith("image/"):
            st.session_state.session["message"] = {"type": "error", "text": "Hanya .pdf, .png, .jpeg yang diizinkan."}
            return True
        try:
            resource_type = "raw" if "pdf" in file_type else "image"
            res = cloudinary.uploader.upload(
                f"data:{file_type};base64,{file_b64}",
                resource_type=resource_type,
                folder="ecv",
                public_id=f"{user['id']}_{filename.rsplit('.', 1)[0]}",
            )
            url = res["secure_url"]
            if kind == "avatar":
                user["profilePicture"] = url
            else:
                user["files"].append({
                    "name": filename, "url": url,
                    "type": "pdf" if "pdf" in file_type else "image",
                })
            save_data(data)
            st.session_state.session["message"] = {"type": "success", "text": "Berkas berhasil diunggah."}
        except Exception as e:
            st.session_state.session["message"] = {"type": "error", "text": f"Gagal unggah: {e}"}
        return True

    if action == "delete-file":
        url = act.get("url")
        user["files"] = [f for f in user["files"] if f["url"] != url]
        save_data(data)
        st.session_state.session["message"] = {"type": "success", "text": "Berkas dihapus."}
        return True

    if action == "change-password":
        old = act.get("oldPassword") or ""
        new = act.get("newPassword") or ""
        if sha256(old) != user["password"]:
            st.session_state.session["message"] = {"type": "error", "text": "Sandi lama salah."}
            return True
        if len(new) < 6:
            st.session_state.session["message"] = {"type": "error", "text": "Sandi baru minimal 6 karakter."}
            return True
        user["password"] = sha256(new)
        save_data(data)
        st.session_state.session["message"] = {"type": "success", "text": "Sandi berhasil diubah."}
        return True

    if action == "reset-password":
        if not session.get("isMaster"):
            return False
        uid = act.get("userId")
        new = act.get("newPassword") or ""
        u = next((x for x in data["users"] if x["id"] == uid), None)
        if not u or len(new) < 6:
            st.session_state.session["message"] = {"type": "error", "text": "Gagal reset sandi."}
            return True
        u["password"] = sha256(new)
        save_data(data)
        st.session_state.session["message"] = {"type": "success", "text": f"Sandi {u['name']} direset."}
        return True

    return False


# ════════════════════════════════════════════════════════════════════
# 10. MAIN RENDER
# ════════════════════════════════════════════════════════════════════
data = load_data()

component_value = _ecv(
    users=data["users"],
    session=st.session_state.session,
    key="ecv_main",
)

if isinstance(component_value, dict):
    aid = component_value.get("actionId")
    if aid and aid != st.session_state.lastActionId:
        st.session_state.lastActionId = aid
        if process_action(component_value, data):
            st.rerun()
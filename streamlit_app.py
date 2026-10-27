"""
E-CV — Final Layout matching Node.js UI.
"""

import hashlib
import html as html_lib
import json
from io import BytesIO
from pathlib import Path
import time

import pandas as pd
import streamlit as st

# ════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="E-CV Kelompok",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# ════════════════════════════════════════════════════════════════════
# 2. CLOUDINARY
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

MAX_FILE_BYTES = 5 * 1024 * 1024
ALLOWED_MIMES = {"application/pdf", "image/png", "image/jpeg"}

def upload_bytes(file_bytes: bytes, filename: str, resource_type: str):
    if not CLOUDINARY_READY: return None
    base = filename.rsplit(".", 1)[0].replace(" ", "_")[:60]
    unique_id = f"ecv_{int(time.time())}_{base}"
    try:
        result = cloudinary.uploader.upload(
            BytesIO(file_bytes), resource_type=resource_type, folder="ecv", public_id=unique_id
        )
        return {"url": result["secure_url"], "public_id": result["public_id"]}
    except Exception:
        return None

def destroy_on_cloudinary(public_id: str, resource_type: str) -> None:
    if not CLOUDINARY_READY or not public_id: return
    try: cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception: pass

def validate_upload(uploaded) -> tuple[bool, str]:
    if uploaded is None: return False, "Tidak ada berkas."
    if uploaded.size > MAX_FILE_BYTES:
        return False, f"Ukuran berkas {uploaded.size / (1024 * 1024):.1f} MB melebihi batas 5 MB."
    if uploaded.type not in ALLOWED_MIMES:
        return False, "Hanya berkas .pdf, .png, atau .jpeg yang diizinkan."
    return True, ""

# ════════════════════════════════════════════════════════════════════
# 3. HELPERS
# ════════════════════════════════════════════════════════════════════
def sha256(s: str) -> str: return hashlib.sha256(s.encode("utf-8")).hexdigest()
def is_hash(s: str) -> bool: return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)
def esc(s) -> str: return html_lib.escape(str(s) if s is not None else "")
def save_data(data: dict) -> None: DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def df_to_records(df, columns: list) -> list:
    if df is None or df.empty: return []
    records = []
    for _, row in df.iterrows():
        rec = {}
        for col in columns:
            v = row.get(col)
            rec[col] = "" if pd.isna(v) else str(v).strip()
        if any(rec.values()): records.append(rec)
    return records

# ════════════════════════════════════════════════════════════════════
# 4. SEED + PERSISTENCE
# ════════════════════════════════════════════════════════════════════
DATA_FILE = Path(__file__).parent / "data" / "users.json"
DATA_FILE.parent.mkdir(exist_ok=True)

SEED = {
    "masterPassword": "capstone12",
    "users": [
        {
            "id": "user1", "name": "Nama User 1", "role": "Frontend Developer", "nim": "220010001",
            "email": "email@example.com", "phone": "08123456789", "location": "Jakarta",
            "linkedin": "linkedin.com/in/user1", "github": "github.com/user1",
            "bio": "Deskripsi profil singkat untuk User 1.",
            "password": "password123", "profilePicture": "",
            "education": [
                {"degree": "S1 Teknik Informatika", "institution": "Universitas Indonesia", "year": "2022 - Sekarang"},
            ],
            "experience": [
                {"role": "Web Developer", "company": "PT Teknologi", "year": "2024", "description": "Membangun UI."},
            ],
            "skills": ["HTML", "CSS", "JavaScript", "React"],
            "mainProject": {"name": "Portfolio Website", "url": "https://github.com/user1"},
            "otherProjects": [{"name": "Aplikasi Kasir", "url": "https://github.com/user1"}],
            "files": [],
        },
        {
            "id": "user2", "name": "Nama User 2", "role": "Backend Developer", "nim": "220010002",
            "email": "user2@example.com", "phone": "08123456780", "location": "Bandung",
            "linkedin": "", "github": "",
            "bio": "Deskripsi profil singkat untuk User 2.",
            "password": "password123", "profilePicture": "",
            "education": [{"degree": "S1 Sistem Informasi", "institution": "ITB", "year": "2021 - Sekarang"}],
            "experience": [], "skills": ["Python", "Django", "PostgreSQL"], "mainProject": {"name": "", "url": ""},
            "otherProjects": [], "files": [],
        },
        {
            "id": "user3", "name": "Nama User 3", "role": "UI/UX Designer", "nim": "220010003",
            "email": "user3@example.com", "phone": "08123456781", "location": "Surabaya",
            "linkedin": "", "github": "",
            "bio": "Deskripsi profil singkat untuk User 3.",
            "password": "password123", "profilePicture": "",
            "education": [{"degree": "S1 Desain", "institution": "ITS", "year": "2020 - Sekarang"}],
            "experience": [], "skills": ["Figma", "Adobe XD"], "mainProject": {"name": "", "url": ""},
            "otherProjects": [], "files": [],
        },
    ],
}

def load_and_migrate() -> dict:
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(SEED, indent=2, ensure_ascii=False), encoding="utf-8")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    changed = False
    if "masterPassword" not in data:
        data["masterPassword"] = "capstone12"
        changed = True
    if not is_hash(data["masterPassword"]):
        data["masterPassword"] = sha256(data["masterPassword"])
        changed = True
    for u in data.get("users", []):
        if "password" not in u:
            u["password"] = "password123"
            changed = True
        if not is_hash(u["password"]):
            u["password"] = sha256(u["password"])
            changed = True
        u.setdefault("profilePicture", "")
        u.setdefault("files", [])
        u.setdefault("role", "")
        u.setdefault("location", "")
        u.setdefault("linkedin", "")
        u.setdefault("github", "")
    if changed:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data

# ════════════════════════════════════════════════════════════════════
# 5. SESSION STATE
# ════════════════════════════════════════════════════════════════════
for key, default in [
    ("logged_in_as", None), ("is_master", False), ("save_version", 0),
    ("flash", None), ("file_upload_version", 0), ("avatar_upload_version", 0)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ════════════════════════════════════════════════════════════════════
# 6. THEME & CSS
# ════════════════════════════════════════════════════════════════════
def build_css() -> str:
    return """
<style>
/* Main Background and Layout */
.stApp {
    background: #0f172a !important;
    background-attachment: fixed !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
    position: relative;
    z-index: 10;
}
html, body, [class*="css"] { color: #e2e8f0 !important; }

/* Hide Streamlit elements */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stStatusWidget"] { display: none !important; }

/* Typography */
h1, h2, h3, h4, h5, h6 { color: #e2e8f0 !important; }
.title-main {
    text-align: center; font-size: 2.5rem; font-weight: 800;
    background: -webkit-linear-gradient(45deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.subtitle-main {
    text-align: center; color: #94a3b8; font-size: 1rem; margin-bottom: 2rem;
}

/* Cards (glassmorphism) */
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.card-header {
    font-size: 0.85rem; font-weight: 700; color: #cbd5e1;
    text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}
.card-header::before {
    content: ''; display: inline-block; width: 4px; height: 16px;
    background: #8b5cf6; border-radius: 2px;
}

/* Profile Sidebar */
.profile-img-container {
    width: 120px; height: 120px; border-radius: 50%;
    background: #86efac; display: flex; align-items: center; justify-content: center;
    font-size: 3rem; font-weight: bold; color: #064e3b;
    margin: 0 auto 20px; overflow: hidden;
    border: 2px solid rgba(255, 255, 255, 0.1);
}
.profile-img { width: 100%; height: 100%; object-fit: cover; }
.profile-name { font-size: 1.5rem; font-weight: 700; text-align: center; color: #f8fafc; margin-bottom: 4px; }
.profile-role { text-align: center; color: #8b5cf6; font-size: 0.9rem; font-weight: 600; margin-bottom: 16px; }
.profile-nim {
    display: block; text-align: center; background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255,255,255,0.05); border-radius: 20px;
    padding: 6px 12px; font-size: 0.8rem; color: #94a3b8;
    width: fit-content; margin: 0 auto 24px;
}
.contact-item {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 12px; font-size: 0.9rem; color: #94a3b8;
    text-decoration: none !important;
}
.contact-item:hover { color: #e2e8f0; }
.contact-icon {
    width: 24px; height: 24px; background: rgba(139, 92, 246, 0.15);
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
    color: #a78bfa; font-size: 0.8rem;
}

/* Lists inside cards */
.list-item { margin-bottom: 16px; position: relative; padding-left: 16px; border-left: 2px solid rgba(139, 92, 246, 0.3); }
.list-item::before {
    content: ''; position: absolute; left: -5px; top: 6px;
    width: 8px; height: 8px; border-radius: 50%; background: #a78bfa;
}
.list-title { font-weight: 600; color: #f8fafc; font-size: 0.95rem; }
.list-sub { color: #94a3b8; font-size: 0.85rem; margin-top: 2px; }
.list-desc { color: #cbd5e1; font-size: 0.85rem; margin-top: 8px; line-height: 1.5; }

/* Skills */
.skill-chip {
    display: inline-block; padding: 6px 12px; margin: 4px;
    background: rgba(139, 92, 246, 0.15); border-radius: 8px;
    font-size: 0.8rem; font-weight: 500; color: #c4b5fd;
}

/* Links */
.btn-link {
    display: inline-flex; align-items: center; gap: 8px;
    color: #a78bfa !important; text-decoration: none !important;
    font-weight: 500; font-size: 0.9rem; margin-bottom: 8px;
    padding: 8px 12px; border-radius: 8px; background: rgba(139, 92, 246, 0.1);
    transition: background 0.2s;
}
.btn-link:hover { background: rgba(139, 92, 246, 0.2); }
.btn-link.download { color: #f8fafc !important; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255,255,255,0.1); }

/* Tabs */
div[data-testid="stTabs"] { justify-content: center; }
div[data-testid="stTabs"] > div > div { background: transparent !important; gap: 8px; }
div[data-testid="stTabs"] button {
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.9rem !important;
    color: #94a3b8 !important; background: transparent !important; border: 1px solid transparent !important;
    padding: 8px 24px !important; transition: all 0.2s !important;
}
div[data-testid="stTabs"] button:hover { color: #e2e8f0 !important; }
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
}

/* Forms */
div[data-testid="stForm"] {
    background: rgba(30, 41, 59, 0.4) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important; padding: 24px !important; backdrop-filter: blur(10px);
}
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
    background: #0f172a !important; color: #f8fafc !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}
div[data-testid="stForm"] button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; padding: 8px 24px !important;
}
.stButton > button {
    border-radius: 8px !important; font-weight: 600 !important;
}

/* Wave Background */
.ecv-wave-bg {
    position: fixed !important; bottom: 0; left: 0;
    width: 100vw; height: 50vh; z-index: -1 !important; pointer-events: none;
}
</style>
"""

def build_wave() -> str:
    return """
<svg class="ecv-wave-bg" viewBox="0 0 1440 240" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
    <path fill="rgba(56, 189, 248, 0.05)" d="M0,120 C240,40 480,200 720,140 C960,80 1200,200 1440,140 L1440,240 L0,240 Z">
        <animate attributeName="d" dur="14s" repeatCount="indefinite"
            values="M0,120 C240,40 480,200 720,140 C960,80 1200,200 1440,140 L1440,240 L0,240 Z;
                    M0,140 C240,200 480,60 720,120 C960,180 1200,40 1440,160 L1440,240 L0,240 Z;
                    M0,120 C240,40 480,200 720,140 C960,80 1200,200 1440,140 L1440,240 L0,240 Z" />
    </path>
    <path fill="rgba(56, 189, 248, 0.03)" d="M0,160 C240,100 480,240 720,180 C960,120 1200,240 1440,180 L1440,240 L0,240 Z">
        <animate attributeName="d" dur="18s" repeatCount="indefinite"
            values="M0,160 C240,100 480,240 720,180 C960,120 1200,240 1440,180 L1440,240 L0,240 Z;
                    M0,180 C240,240 480,120 720,160 C960,220 1200,100 1440,200 L1440,240 L0,240 Z;
                    M0,160 C240,100 480,240 720,180 C960,120 1200,240 1440,180 L1440,240 L0,240 Z" />
    </path>
</svg>
"""

# ════════════════════════════════════════════════════════════════════
# 7. PUBLIC VIEW
# ════════════════════════════════════════════════════════════════════
def render_public_view(users: list):
    st.markdown('<h1 class="title-main">E-CV Kelompok</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-main">Silakan pilih tab di bawah untuk melihat profil dan mengunduh berkas.</p>', unsafe_allow_html=True)

    tabs = st.tabs([u["name"] for u in users])

    for tab, u in zip(tabs, users):
        with tab:
            col_left, col_right = st.columns([1, 2.2], gap="large")

            with col_left:
                # Avatar
                if u.get("profilePicture"):
                    avatar_html = f'<img class="profile-img" src="{esc(u["profilePicture"])}" alt="avatar" />'
                else:
                    initial = esc((u["name"] or "?")[0].upper())
                    avatar_html = f'<div class="profile-img-container">{initial}</div>'

                # Contact Links
                contacts = []
                if u.get("email"): contacts.append(f'<a href="mailto:{esc(u["email"])}" class="contact-item"><div class="contact-icon">✉</div> {esc(u["email"])}</a>')
                if u.get("phone"): contacts.append(f'<a href="tel:{esc(u["phone"])}" class="contact-item"><div class="contact-icon">📞</div> {esc(u["phone"])}</a>')
                if u.get("location"): contacts.append(f'<div class="contact-item"><div class="contact-icon">📍</div> {esc(u["location"])}</div>')
                if u.get("linkedin"): contacts.append(f'<a href="https://{esc(u["linkedin"])}" target="_blank" class="contact-item"><div class="contact-icon">in</div> LinkedIn</a>')
                if u.get("github"): contacts.append(f'<a href="https://{esc(u["github"])}" target="_blank" class="contact-item"><div class="contact-icon">🐙</div> GitHub</a>')
                
                contact_html = "".join(contacts) or '<div class="text-muted">Belum ada kontak.</div>'

                st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        {avatar_html}
                        <div class="profile-name">{esc(u['name'])}</div>
                        <div class="profile-role">{esc(u.get('role', 'Siswa'))}</div>
                        <div class="profile-nim">NIM: {esc(u['nim'])}</div>
                        <div style="text-align: left;">
                            <div class="card-header" style="font-size: 0.75rem;">KONTAK</div>
                            {contact_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with col_right:
                # Profil
                st.markdown(f'''
                    <div class="glass-card">
                        <div class="card-header">PROFIL</div>
                        <div class="list-desc">{esc(u.get('bio', 'Belum ada deskripsi profil.'))}</div>
                    </div>
                ''', unsafe_allow_html=True)

                # Pendidikan
                edu_html = "".join(
                    f'<div class="list-item"><div class="list-title">{esc(e.get("degree", ""))}</div>'
                    f'<div class="list-sub">{esc(e.get("institution", ""))} • {esc(e.get("year", ""))}</div></div>'
                    for e in (u.get("education") or [])
                ) or '<div class="list-sub">Belum ada data.</div>'
                st.markdown(f'<div class="glass-card"><div class="card-header">PENDIDIKAN</div>{edu_html}</div>', unsafe_allow_html=True)

                # Pengalaman
                exp_html = "".join(
                    f'<div class="list-item"><div class="list-title">{esc(e.get("role", ""))}</div>'
                    f'<div class="list-sub">{esc(e.get("company", ""))} • {esc(e.get("year", ""))}</div>'
                    f'<div class="list-desc">{esc(e.get("description", ""))}</div></div>'
                    for e in (u.get("experience") or [])
                ) or '<div class="list-sub">Belum ada data.</div>'
                st.markdown(f'<div class="glass-card"><div class="card-header">PENGALAMAN</div>{exp_html}</div>', unsafe_allow_html=True)

                # Keahlian
                skill_html = "".join(f'<span class="skill-chip">{esc(s)}</span>' for s in (u.get("skills") or [])) or '<div class="list-sub">Belum ada data.</div>'
                st.markdown(f'<div class="glass-card"><div class="card-header">KEAHLIAN</div><div>{skill_html}</div></div>', unsafe_allow_html=True)

                # Proyek Utama
                mp = u.get("mainProject") or {}
                if mp.get("url"):
                    st.markdown(f'''
                        <div class="glass-card">
                            <div class="card-header">PROYEK UTAMA</div>
                            <a href="{esc(mp.get('url'))}" target="_blank" class="btn-link">🔗 {esc(mp.get('name', 'Lihat Proyek'))}</a>
                        </div>
                    ''', unsafe_allow_html=True)

                # Proyek Lainnya
                proj_html = "".join(
                    f'<a href="{esc(p.get("url", "#"))}" target="_blank" class="btn-link">↗ {esc(p.get("name", ""))}</a><br>'
                    for p in (u.get("otherProjects") or [])
                ) or '<div class="list-sub">Belum ada proyek lain.</div>'
                st.markdown(f'<div class="glass-card"><div class="card-header">PROYEK LAINNYA</div>{proj_html}</div>', unsafe_allow_html=True)

                # Berkas
                files_html = "".join(
                    f'<a href="{esc(f.get("url", "#"))}" target="_blank" class="btn-link download">📄 Unduh {esc(f.get("name", ""))}</a><br>'
                    for f in (u.get("files") or [])
                ) or '<div class="list-sub">Belum ada berkas.</div>'
                st.markdown(f'<div class="glass-card"><div class="card-header">BERKAS</div>{files_html}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 8. LOGIN VIEW
# ════════════════════════════════════════════════════════════════════
def render_login_page(data: dict):
    st.markdown('<h1 class="title-main">Panel Admin</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p style="text-align: center; color: #94a3b8; margin-bottom: 2rem;">Masuk sebagai Master</p>', unsafe_allow_html=True)
        
        if st.button("← Kembali ke Beranda", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        tab1, tab2 = st.tabs(["Login Pengguna", "Login Master"])
        
        with tab1:
            with st.form("login_user"):
                selected_user = st.selectbox("PILIH PENGGUNA", options=[u["name"] for u in data["users"]])
                pwd = st.text_input("KATA SANDI", type="password")
                if st.form_submit_button("Masuk", use_container_width=True):
                    user = next((u for u in data["users"] if u["name"] == selected_user), None)
                    if user and sha256(pwd) == user["password"]:
                        st.session_state.logged_in_as = user["id"]
                        st.session_state.is_master = False
                        st.session_state.flash = f"✅ Selamat datang, {user['name']}."
                        st.rerun()
                    else:
                        st.error("❌ Sandi salah.")
                        
        with tab2:
            with st.form("login_master"):
                pwd = st.text_input("KATA SANDI MASTER", type="password")
                if st.form_submit_button("Masuk", use_container_width=True):
                    if sha256(pwd) == data["masterPassword"]:
                        st.session_state.logged_in_as = "master"
                        st.session_state.is_master = True
                        st.session_state.flash = "✅ Selamat datang, Master Admin."
                        st.rerun()
                    else:
                        st.error("❌ Sandi master salah.")

# ════════════════════════════════════════════════════════════════════
# 9. ADMIN PANEL
# ════════════════════════════════════════════════════════════════════
def render_admin_panel(data: dict):
    st.markdown('<h1 class="title-main">Panel Admin</h1>', unsafe_allow_html=True)
    is_master = st.session_state.is_master
    current_user_id = st.session_state.logged_in_as

    # Top Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<p style="text-align: center; color: #94a3b8; margin-bottom: 1rem;">Masuk sebagai {"Master" if is_master else "Pengguna"}</p>', unsafe_allow_html=True)
        if st.button("← Kembali ke Beranda", use_container_width=True):
            st.query_params.clear()
            st.session_state.logged_in_as = None
            st.rerun()

    # Master Badge
    if is_master:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown('<div style="font-weight: 600; font-size: 1.1rem;">👑 Admin Master</div>', unsafe_allow_html=True)
        with c2:
            if st.button("Keluar", use_container_width=True):
                st.session_state.logged_in_as = None
                st.session_state.is_master = False
                st.query_params.clear()
                st.rerun()
        st.write("")

    # User Selector (Master only)
    if is_master:
        options = {f"{u['name']} ({u['nim']})": u["id"] for u in data["users"]}
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown('<div style="font-weight: 600; font-size: 0.9rem; margin-top: 8px;">Kelola Pengguna:</div>', unsafe_allow_html=True)
        with c2:
            selected_label = st.selectbox("Pilih Pengguna", list(options.keys()), label_visibility="collapsed")
            target_user_id = options[selected_label]
    else:
        target_user_id = current_user_id

    target_user = next(u for u in data["users"] if u["id"] == target_user_id)

    if st.session_state.flash:
        st.success(st.session_state.flash)
        st.session_state.flash = None

    # Tabs
    tab_edit, tab_files, tab_pwd = st.tabs(["Edit Data", "Kelola Berkas", "Ubah Sandi"])

    with tab_edit:
        render_edit_data_tab(target_user, data)
    with tab_files:
        render_files_tab(target_user, data)
    with tab_pwd:
        if is_master:
            render_reset_password_tab(target_user, data)
        else:
            render_change_password_tab(target_user, data)


def render_edit_data_tab(u: dict, data: dict):
    version = st.session_state.save_version
    key_base = f"{u['id']}_{version}"

    with st.form(f"edit_form_{key_base}"):
        # Foto Profile
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px;">Foto Profil</div>', unsafe_allow_html=True)
        av_col1, av_col2 = st.columns([1, 3])
        with av_col1:
            if u.get("profilePicture"):
                st.image(u["profilePicture"], width=100)
            else:
                st.markdown('<div class="profile-img-container" style="width: 100px; height: 100px; font-size: 2rem;">?</div>', unsafe_allow_html=True)
        with av_col2:
            av_key = f"avatar_uploader_{u['id']}_{st.session_state.avatar_upload_version}"
            avatar_file = st.file_uploader("Pilih file", type=["png", "jpeg", "jpg"], key=av_key, disabled=not CLOUDINARY_READY, label_visibility="collapsed")
            if avatar_file is not None:
                ok, msg = validate_upload(avatar_file)
                if ok:
                    if st.form_submit_button("Unggah Foto", type="secondary"):
                        result = upload_bytes(avatar_file.getvalue(), avatar_file.name, "image")
                        if result:
                            u["profilePicture"] = result["url"]
                            save_data(data)
                            st.session_state.avatar_upload_version += 1
                            st.session_state.flash = "✅ Foto profil diperbarui."
                            st.rerun()
        
        st.divider()

        # Row 1
        c1, c2, c3 = st.columns(3)
        with c1: nim = st.text_input("NIM", value=u.get("nim", ""), key=f"nim_{key_base}")
        with c2: name = st.text_input("NAMA LENGKAP", value=u.get("name", ""), key=f"name_{key_base}")
        with c3: role = st.text_input("POSISI / PERAN", value=u.get("role", ""), key=f"role_{key_base}")

        # Row 2
        bio = st.text_area("PROFIL SINGKAT", value=u.get("bio", ""), key=f"bio_{key_base}", height=100)

        # Row 3 (Contact)
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-top: 8px; margin-bottom: 8px;">Kontak</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: email = st.text_input("EMAIL", value=u.get("email", ""), key=f"email_{key_base}")
        with c2: phone = st.text_input("TELEPON", value=u.get("phone", ""), key=f"phone_{key_base}")
        with c3: location = st.text_input("LOKASI", value=u.get("location", ""), key=f"loc_{key_base}")
        with c4: linkedin = st.text_input("LINKEDIN", value=u.get("linkedin", ""), key=f"li_{key_base}")
        with c5: github = st.text_input("GITHUB", value=u.get("github", ""), key=f"gh_{key_base}")

        st.divider()

        # Lists (using data_editor for simplicity and cleaner UI within a form)
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px;">Pendidikan</div>', unsafe_allow_html=True)
        edu_df = pd.DataFrame(u.get("education") or [], columns=["degree", "institution", "year"])
        edited_edu = st.data_editor(edu_df, num_rows="dynamic", use_container_width=True, key=f"edu_{key_base}")

        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px;">Pengalaman</div>', unsafe_allow_html=True)
        exp_df = pd.DataFrame(u.get("experience") or [], columns=["role", "company", "year", "description"])
        edited_exp = st.data_editor(exp_df, num_rows="dynamic", use_container_width=True, key=f"exp_{key_base}")

        st.divider()

        # Skills & Projects
        skills_text = st.text_input("KEAHLIAN (PISAHKAN DENGAN KOMA)", value=", ".join(u.get("skills") or []), key=f"skills_{key_base}")
        
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-top: 8px; margin-bottom: 8px;">Proyek</div>', unsafe_allow_html=True)
        mp = u.get("mainProject") or {}
        c1, c2 = st.columns(2)
        with c1: mp_name = st.text_input("LINK PROYEK UTAMA (NAMA)", value=mp.get("name", ""), key=f"mpname_{key_base}")
        with c2: mp_url = st.text_input("LINK PROYEK UTAMA (URL)", value=mp.get("url", ""), key=f"mpurl_{key_base}")

        proj_df = pd.DataFrame(u.get("otherProjects") or [], columns=["name", "url"])
        edited_proj = st.data_editor(proj_df, num_rows="dynamic", use_container_width=True, key=f"proj_{key_base}")

        # Save Button
        submitted = st.form_submit_button("Simpan Perubahan", type="primary", use_container_width=True)

    if submitted:
        u["nim"] = nim.strip()
        u["name"] = name.strip()
        u["role"] = role.strip()
        u["bio"] = bio.strip()
        u["email"] = email.strip()
        u["phone"] = phone.strip()
        u["location"] = location.strip()
        u["linkedin"] = linkedin.strip()
        u["github"] = github.strip()
        u["skills"] = [s.strip() for s in skills_text.split(",") if s.strip()]
        u["education"] = df_to_records(edited_edu, ["degree", "institution", "year"])
        u["experience"] = df_to_records(edited_exp, ["role", "company", "year", "description"])
        u["mainProject"] = {"name": mp_name.strip(), "url": mp_url.strip()}
        u["otherProjects"] = df_to_records(edited_proj, ["name", "url"])
        
        save_data(data)
        st.session_state.save_version += 1
        st.session_state.flash = "✅ Data berhasil disimpan."
        st.rerun()

def render_files_tab(u: dict, data: dict):
    st.markdown("### Unggah Berkas")
    st.caption("Hanya `.pdf`, `.png`, `.jpeg` · maksimal 5 MB.")

    fu_key = f"file_uploader_{u['id']}_{st.session_state.file_upload_version}"
    new_file = st.file_uploader("Pilih berkas", type=["pdf", "png", "jpeg", "jpg"], key=fu_key, disabled=not CLOUDINARY_READY)

    if new_file is not None:
        ok, msg = validate_upload(new_file)
        if not ok: st.error(f"❌ {msg}")
        else:
            if st.button("⬆️ Unggah Berkas", type="primary"):
                resource_type = "raw" if new_file.type == "application/pdf" else "image"
                result = upload_bytes(new_file.getvalue(), new_file.name, resource_type)
                if result:
                    u["files"].append({
                        "name": new_file.name, "url": result["url"],
                        "public_id": result["public_id"],
                        "type": "pdf" if new_file.type == "application/pdf" else "image",
                    })
                    save_data(data)
                    st.session_state.file_upload_version += 1
                    st.session_state.flash = f"✅ Berkas '{new_file.name}' berhasil diunggah."
                    st.rerun()

    st.divider()
    st.markdown(f"#### Berkas Terdaftar ({len(u.get('files') or [])})")
    
    files = u.get("files") or []
    if not files:
        st.info("Belum ada berkas.")
        return

    for i, f in enumerate(files):
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1: st.markdown(f"📄 **{esc(f.get('name'))}**")
        with c2: st.link_button("Lihat", f.get("url", "#"), use_container_width=True)
        with c3:
            if st.button("Hapus", key=f"del_{i}_{f.get('public_id')}", type="primary"):
                destroy_on_cloudinary(f.get("public_id", ""), "raw" if f.get("type") == "pdf" else "image")
                u["files"].remove(f)
                save_data(data)
                st.session_state.flash = f"✅ Berkas dihapus."
                st.rerun()

def render_change_password_tab(u: dict, data: dict):
    st.markdown("### Ubah Sandi")
    with st.form(f"change_pwd_{u['id']}"):
        old = st.text_input("Sandi lama", type="password")
        new1 = st.text_input("Sandi baru", type="password")
        new2 = st.text_input("Konfirmasi sandi baru", type="password")
        if st.form_submit_button("Ubah Sandi", type="primary"):
            if sha256(old) != u["password"]: st.error("❌ Sandi lama salah.")
            elif len(new1) < 6: st.error("❌ Sandi baru minimal 6 karakter.")
            elif new1 != new2: st.error("❌ Konfirmasi tidak cocok.")
            else:
                u["password"] = sha256(new1)
                save_data(data)
                st.session_state.flash = "✅ Sandi berhasil diubah."
                st.rerun()

def render_reset_password_tab(u: dict, data: dict):
    st.markdown(f"### Reset Sandi: {u['name']}")
    with st.form(f"reset_pwd_{u['id']}"):
        new1 = st.text_input("Sandi baru", type="password")
        new2 = st.text_input("Konfirmasi sandi baru", type="password")
        if st.form_submit_button("Reset Sandi", type="primary"):
            if len(new1) < 6: st.error("❌ Minimal 6 karakter.")
            elif new1 != new2: st.error("❌ Konfirmasi tidak cocok.")
            else:
                u["password"] = sha256(new1)
                save_data(data)
                st.session_state.flash = f"✅ Sandi {u['name']} berhasil direset."
                st.rerun()

# ════════════════════════════════════════════════════════════════════
# 10. ROUTING
# ════════════════════════════════════════════════════════════════════
data = load_and_migrate()

st.markdown(build_css(), unsafe_allow_html=True)
st.markdown(build_wave(), unsafe_allow_html=True)

if st.session_state.logged_in_as:
    render_admin_panel(data)
elif st.query_params.get("admin") == "1":
    render_login_page(data)
else:
    render_public_view(data["users"])
import hashlib
import html as html_lib
import json
import base64
from io import BytesIO
from pathlib import Path
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
# 2. ANTI-INSPECT & UI TWEAKS
# ════════════════════════════════════════════════════════════════════
components.html("""
<script>
    // ── 1. ANTI-INSPECT (Rickroll) ──
    setInterval(function() {
        const widthThreshold = window.parent.outerWidth - window.parent.innerWidth > 160;
        const heightThreshold = window.parent.outerHeight - window.parent.innerHeight > 160;
        if (widthThreshold || heightThreshold) {
            window.top.location.href = "https://youtu.be/lpiB2wMc49g?si=sPGfx6kDv3SWNbE1";
        }
    }, 1000);

    document.addEventListener('contextmenu', event => event.preventDefault());
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12' || 
            (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) || 
            (e.ctrlKey && e.key === 'U')) {
            e.preventDefault();
            window.top.location.href = "https://youtu.be/lpiB2wMc49g?si=sPGfx6kDv3SWNbE1";
        }
    });

    // ── 2. QOL: GREEN BUTTON & TAB PERSISTENCE ──
    const doc = window.parent.document;
    
    function applyUI() {
        // Green Save Button
        const buttons = doc.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.innerText.includes("Simpan Perubahan")) {
                btn.style.background = "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)";
                btn.style.border = "none";
                btn.style.boxShadow = "0 4px 12px rgba(34, 197, 94, 0.4)";
            }
        });

        // Tab Persistence (Admin Panel only)
        const tabs = doc.querySelectorAll('button[data-baseweb="tab"]');
        let isAdmin = false;
        if (tabs.length === 3 && tabs[0].innerText.includes("Edit Data")) {
            isAdmin = true;
        }
        
        if (isAdmin) {
            tabs.forEach((tab, index) => {
                if (!tab.dataset.listenerAdded) {
                    tab.addEventListener('click', () => {
                        window.parent.localStorage.setItem('ecv_admin_tab', index);
                    });
                    tab.dataset.listenerAdded = "true";
                }
            });
            const savedTab = window.parent.localStorage.getItem('ecv_admin_tab');
            if (savedTab !== null && tabs[savedTab] && tabs[savedTab].getAttribute('aria-selected') !== 'true') {
                tabs[savedTab].click();
            }
        }
    }

    setInterval(applyUI, 500);
</script>
""", height=0, width=0)

# ════════════════════════════════════════════════════════════════════
# 3. CLOUDINARY & FILE STORAGE
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

# Set path specifically to the workspace folder
BASE_DIR = Path("/workspaces/movies-dataset")
if not BASE_DIR.exists():
    BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "users.json"
DATA_FILE.parent.mkdir(exist_ok=True, parents=True)

def upload_bytes(file_bytes: bytes, filename: str, user_id: str, resource_type: str):
    # 1. Save Locally
    user_dir = DATA_FILE.parent / user_id
    user_dir.mkdir(exist_ok=True, parents=True)
    file_path = user_dir / filename
    
    try:
        file_path.write_bytes(file_bytes)
    except Exception as e:
        st.error(f"Gagal menyimpan file lokal: {e}")
        return None

    local_path = str(file_path.relative_to(DATA_FILE.parent))
    
    # 2. Also save to Cloudinary if ready (optional)
    if CLOUDINARY_READY:
        base = filename.rsplit(".", 1)[0].replace(" ", "_")[:60]
        unique_id = f"ecv_{int(time.time())}_{base}"
        try:
            result = cloudinary.uploader.upload(
                BytesIO(file_bytes), resource_type=resource_type, folder="ecv", public_id=unique_id
            )
            return {
                "url": result["secure_url"], 
                "public_id": result["public_id"], 
                "local_path": local_path
            }
        except Exception:
            pass # Fallback to local only if Cloudinary fails
            
    return {"url": "#", "public_id": "", "local_path": local_path}

def get_file_data_url(path_str):
    if not path_str: return "#"
    full_path = DATA_FILE.parent / path_str
    if not full_path.exists(): return "#"
    try:
        b64 = base64.b64encode(full_path.read_bytes()).decode()
        return f"data:application/octet-stream;base64,{b64}"
    except Exception:
        return "#"

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
# 4. HELPERS
# ════════════════════════════════════════════════════════════════════
def sha256(s: str) -> str: return hashlib.sha256(s.encode("utf-8")).hexdigest()
def is_hash(s: str) -> bool: return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)
def esc(s) -> str: return html_lib.escape(str(s) if s is not None else "")

def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(exist_ok=True, parents=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ════════════════════════════════════════════════════════════════════
# 5. SEED + PERSISTENCE
# ════════════════════════════════════════════════════════════════════
SEED = {
    "masterPassword": "capstone12",
    "users": [
        {
            "id": "user1", "name": "Ahmad Fauzi", "role": "Frontend Developer", "nim": "221001001",
            "email": "ahmad.fauzi@example.com", "phone": "+62 812-3456-7890", "location": "Jakarta",
            "bio": "Mahasiswa Teknik Informatika yang berfokus pada pengembangan web dan mobile.",
            "password": "password123", "profilePicture": "",
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
            "id": "user2", "name": "Siti Rahma", "role": "Backend Developer", "nim": "221001002",
            "email": "siti.rahma@example.com", "phone": "+62 813-9876-5432", "location": "Bandung",
            "bio": "Mahasiswi Sistem Informasi yang tertarik pada analisis data dan UI/UX design.",
            "password": "password123", "profilePicture": "",
            "education": [{"degree": "S1 Sistem Informasi", "institution": "Institut Teknologi Bandung", "year": "2022 - Sekarang"}],
            "experience": [{"role": "UI/UX Design Intern", "company": "Startup Kreatif", "year": "2024", "description": "Merancang user flow dan wireframe untuk aplikasi mobile."}],
            "skills": ["Figma", "UI Design", "UX Research", "SQL", "Tableau", "Python"],
            "mainProject": {"name": "Dashboard Analitik Penjualan", "url": "https://github.com/siti/dashboard"},
            "otherProjects": [{"name": "Redesign Aplikasi OVO", "url": "https://github.com/siti/ovo-redesign"}],
            "files": [],
        },
        {
            "id": "user3", "name": "Budi Santoso", "role": "IoT Engineer", "nim": "221001003",
            "email": "budi.santoso@example.com", "phone": "+62 857-1111-2222", "location": "Yogyakarta",
            "bio": "Mahasiswa Teknik Komputer yang berfokus pada embedded systems dan IoT. Suka bereksperimen dengan Raspberry Pi dan Arduino.",
            "password": "password123", "profilePicture": "",
            "education": [{"degree": "S1 Teknik Komputer", "institution": "Universitas Gadjah Mada", "year": "2021 - Sekarang"}],
            "experience": [{"role": "IoT Engineer Intern", "company": "PT Smart Device", "year": "2024", "description": "Mengembangkan firmware perangkat IoT berbasis ESP32."}],
            "skills": ["C++", "Arduino", "Raspberry Pi", "Python", "MQTT", "Linux"],
            "mainProject": {"name": "Sistem Monitoring Suhu IoT", "url": "https://github.com/budi/iot-monitor"},
            "otherProjects": [{"name": "Smart Home Controller", "url": "https://github.com/budi/smarthome"}],
            "files": [],
        },
    ],
}

def load_and_migrate() -> dict:
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(SEED, indent=2, ensure_ascii=False), encoding="utf-8")
    
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        # Fallback if user corrupted the JSON manually
        data = SEED
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

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
    if changed:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data

# ════════════════════════════════════════════════════════════════════
# 6. SESSION STATE
# ════════════════════════════════════════════════════════════════════
for key, default in [
    ("logged_in_as", None), ("is_master", False), ("save_version", 0),
    ("flash", None), ("file_upload_version", 0), ("avatar_upload_version", 0),
    ("scroll_to_top", False), ("view_user_id", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.scroll_to_top:
    components.html("<script>window.parent.scrollTo({ top: 0, behavior: 'smooth' });</script>", height=0)
    st.session_state.scroll_to_top = False

# ════════════════════════════════════════════════════════════════════
# 7. THEME & CSS
# ════════════════════════════════════════════════════════════════════
def build_css() -> str:
    return """
<style>
/* Main Background and Layout */
body { background-color: #0f172a !important; }
.stApp { background: transparent !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
.block-container {
    padding-top: 2rem !important; padding-bottom: 3rem !important;
    max-width: 1100px !important; position: relative; z-index: 10;
}
html, body, [class*="css"] { color: #e2e8f0 !important; }

/* Hide Streamlit elements */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stFileUploadDropzone"] small { display: none !important; } /* Hide 200MB text */

/* Typography */
h1, h2, h3, h4, h5, h6 { color: #e2e8f0 !important; }
.title-main {
    text-align: center; font-size: 2.5rem; font-weight: 800;
    background: -webkit-linear-gradient(45deg, #6366f1, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.subtitle-main { text-align: center; color: #94a3b8; font-size: 1rem; margin-bottom: 2rem; }

/* Glass Cards */
.glass-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px; padding: 24px; margin-bottom: 20px;
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
.profile-name { font-size: 1.5rem; font-weight: 700; text-align: center; color: #f8fafc; margin-bottom: 4px; word-break: break-word; }
.profile-role { text-align: center; color: #8b5cf6; font-size: 0.9rem; font-weight: 600; margin-bottom: 16px; }
.profile-nim {
    display: inline-block; text-align: center; background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255,255,255,0.05); border-radius: 20px;
    padding: 6px 12px; font-size: 0.8rem; color: #94a3b8;
    margin: 0 auto 24px;
}
.contact-item {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 12px; font-size: 0.9rem; color: #94a3b8;
    text-decoration: none !important; word-break: break-word;
}
.contact-item:hover { color: #e2e8f0; }
.contact-icon {
    min-width: 24px; height: 24px; background: rgba(139, 92, 246, 0.15);
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

/* Streamlit Tabs - Force Centering and Glass Card */
div[data-testid="stTabs"] { width: 100%; }
div[data-testid="stTabs"] > div > div:first-child { display: flex; justify-content: center; width: 100%; }
div[data-baseweb="tab-list"] {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    backdrop-filter: blur(12px) !important;
    display: flex !important;
    gap: 8px !important;
    border-bottom: none !important;
    width: fit-content !important;
    margin: 0 auto 24px auto !important;
}
div[data-baseweb="tab-highlight"] { background: transparent !important; }
div[data-baseweb="tab-border"] { display: none !important; }
div[data-testid="stTabs"] button[role="tab"] {
    color: #94a3b8 !important; font-weight: 600 !important;
    padding: 8px 24px !important; border-radius: 8px !important;
    border: none !important; background: transparent !important;
    transition: all 0.2s !important;
}
div[data-testid="stTabs"] button[role="tab"]:hover { color: #e2e8f0 !important; }
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
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

/* All Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 8px 24px !important; transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2) !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important; }

/* Link Buttons */
.stLinkButton > a {
    background: rgba(30, 41, 59, 0.8) !important; color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 8px 24px !important; text-decoration: none !important;
    display: inline-flex; align-items: center; justify-content: center;
}
.stLinkButton > a:hover { background: rgba(30, 41, 59, 1) !important; }

/* File Uploader */
[data-testid="stFileUploadDropzone"] {
    background-color: rgba(30, 41, 59, 0.4) !important;
    border: 1px dashed rgba(139, 92, 246, 0.5) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #8b5cf6 !important;
    background-color: rgba(30, 41, 59, 0.6) !important;
}
[data-testid="stFileUploadDropzone"] button {
    background: rgba(139, 92, 246, 0.2) !important;
    color: #c4b5fd !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
}

/* Wave Background */
.ecv-wave-bg {
    position: fixed !important; bottom: 0; left: 0;
    width: 100vw; height: 50vh; z-index: 0 !important; pointer-events: none;
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
# 8. PUBLIC VIEW (GRID & DETAILS)
# ════════════════════════════════════════════════════════════════════
def render_public_grid(users: list):
    st.markdown('<h1 class="title-main">E-CV Kelompok</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-main">Silakan pilih profil di bawah ini untuk melihat detail.</p>', unsafe_allow_html=True)

    cols = st.columns(3, gap="large")
    for idx, u in enumerate(users):
        with cols[idx]:
            if u.get("profilePicture"):
                avatar_html = f'<img class="profile-img" src="{esc(u["profilePicture"])}" alt="avatar" />'
            else:
                initial = esc((u["name"] or "?")[0].upper())
                avatar_html = f'<div class="profile-img-container">{initial}</div>'

            contacts = []
            if u.get("email"): contacts.append(f'<div class="contact-item"><div class="contact-icon">✉</div> {esc(u["email"])}</div>')
            if u.get("phone"): contacts.append(f'<div class="contact-item"><div class="contact-icon">📞</div> {esc(u["phone"])}</div>')
            
            contact_html = "".join(contacts)

            st.markdown(f"""
                <div class="glass-card" style="text-align: center; height: 100%;">
                    {avatar_html}
                    <div class="profile-name">{esc(u['name'])}</div>
                    <div class="profile-role">{esc(u.get('role', 'Siswa'))}</div>
                    <div class="profile-nim">NIM: {esc(u['nim'])}</div>
                    <div style="text-align: left; margin-top: 16px;">
                        <div class="card-header" style="font-size: 0.75rem;">KONTAK</div>
                        {contact_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("Lihat Profil Lengkap", key=f"btn_view_{u['id']}", use_container_width=True):
                st.session_state.view_user_id = u['id']
                st.rerun()

def render_public_detail(u: dict):
    if st.button("← Kembali ke Dashboard", use_container_width=False):
        st.session_state.view_user_id = None
        st.rerun()

    st.markdown('<h1 class="title-main" style="margin-top: -10px;">Profil Lengkap</h1>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 2], gap="large")

    with col_left:
        if u.get("profilePicture"):
            avatar_html = f'<img class="profile-img" src="{esc(u["profilePicture"])}" alt="avatar" />'
        else:
            initial = esc((u["name"] or "?")[0].upper())
            avatar_html = f'<div class="profile-img-container">{initial}</div>'

        contacts = []
        if u.get("email"): contacts.append(f'<a href="mailto:{esc(u["email"])}" class="contact-item"><div class="contact-icon">✉</div> {esc(u["email"])}</a>')
        if u.get("phone"): contacts.append(f'<a href="tel:{esc(u["phone"])}" class="contact-item"><div class="contact-icon">📞</div> {esc(u["phone"])}</a>')
        if u.get("location"): contacts.append(f'<div class="contact-item"><div class="contact-icon">📍</div> {esc(u["location"])}</div>')
        
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
        files_html = ""
        for f in (u.get("files") or []):
            data_url = get_file_data_url(f.get("local_path"))
            if data_url != "#":
                files_html += f'<a href="{data_url}" download="{esc(f.get("name", ""))}" class="btn-link download">📄 Unduh {esc(f.get("name", ""))}</a><br>'
            elif f.get("url") and f.get("url") != "#":
                files_html += f'<a href="{esc(f.get("url"))}" target="_blank" class="btn-link download">📄 Unduh {esc(f.get("name", ""))}</a><br>'
                
        files_html = files_html or '<div class="list-sub">Belum ada berkas.</div>'
        st.markdown(f'<div class="glass-card"><div class="card-header">BERKAS</div>{files_html}</div>', unsafe_allow_html=True)

def render_public_view(users: list):
    if st.session_state.view_user_id is None:
        render_public_grid(users)
    else:
        u = next((x for x in users if x["id"] == st.session_state.view_user_id), None)
        if u:
            render_public_detail(u)
        else:
            st.session_state.view_user_id = None
            st.rerun()

# ════════════════════════════════════════════════════════════════════
# 9. LOGIN VIEW
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
# 10. ADMIN PANEL
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

    # Initialize lists in session state for the form
    if f"edu_list_{u['id']}" not in st.session_state:
        st.session_state[f"edu_list_{u['id']}"] = list(u.get("education") or [])
    if f"exp_list_{u['id']}" not in st.session_state:
        st.session_state[f"exp_list_{u['id']}"] = list(u.get("experience") or [])
    if f"proj_list_{u['id']}" not in st.session_state:
        st.session_state[f"proj_list_{u['id']}"] = list(u.get("otherProjects") or [])

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
                        result = upload_bytes(avatar_file.getvalue(), avatar_file.name, u['id'], "image")
                        if result:
                            u["profilePicture"] = result.get("url") if result.get("url") != "#" else get_file_data_url(result.get("local_path"))
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
        c1, c2, c3 = st.columns(3)
        with c1: email = st.text_input("EMAIL", value=u.get("email", ""), key=f"email_{key_base}")
        with c2: phone = st.text_input("TELEPON", value=u.get("phone", ""), key=f"phone_{key_base}")
        with c3: location = st.text_input("LOKASI", value=u.get("location", ""), key=f"loc_{key_base}")

        st.divider()

        # Custom CRUD for Pendidikan
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px;">Pendidikan</div>', unsafe_allow_html=True)
        edu_list = st.session_state[f"edu_list_{u['id']}"]
        for i, edu in enumerate(edu_list):
            cols = st.columns([3, 3, 2, 1])
            edu["degree"] = cols[0].text_input(f"Gelar_{i}", value=edu.get("degree", ""), label_visibility="collapsed", placeholder="Gelar / Jenjang", key=f"edu_deg_{i}")
            edu["institution"] = cols[1].text_input(f"Institusi_{i}", value=edu.get("institution", ""), label_visibility="collapsed", placeholder="Institusi", key=f"edu_inst_{i}")
            edu["year"] = cols[2].text_input(f"Tahun_{i}", value=edu.get("year", ""), label_visibility="collapsed", placeholder="Tahun", key=f"edu_year_{i}")
            with cols[3]:
                if st.form_submit_button("✕", key=f"del_edu_{i}"):
                    edu_list.pop(i)
                    st.rerun()
        
        if st.form_submit_button("+ Tambah Pendidikan"):
            edu_list.append({"degree": "", "institution": "", "year": ""})
            st.rerun()

        st.divider()

        # Custom CRUD for Pengalaman
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px;">Pengalaman</div>', unsafe_allow_html=True)
        exp_list = st.session_state[f"exp_list_{u['id']}"]
        for i, exp in enumerate(exp_list):
            cols = st.columns([3, 3, 2, 1])
            exp["role"] = cols[0].text_input(f"Peran_{i}", value=exp.get("role", ""), label_visibility="collapsed", placeholder="Peran / Posisi", key=f"exp_role_{i}")
            exp["company"] = cols[1].text_input(f"Perusahaan_{i}", value=exp.get("company", ""), label_visibility="collapsed", placeholder="Perusahaan", key=f"exp_comp_{i}")
            exp["year"] = cols[2].text_input(f"Tahun_{i}", value=exp.get("year", ""), label_visibility="collapsed", placeholder="Tahun", key=f"exp_year_{i}")
            with cols[3]:
                if st.form_submit_button("✕", key=f"del_exp_{i}"):
                    exp_list.pop(i)
                    st.rerun()
            
            # Description on a new row
            desc_cols = st.columns([9, 1])
            exp["description"] = desc_cols[0].text_area(f"Deskripsi_{i}", value=exp.get("description", ""), label_visibility="collapsed", placeholder="Deskripsi", height=68, key=f"exp_desc_{i}")
        
        if st.form_submit_button("+ Tambah Pengalaman"):
            exp_list.append({"role": "", "company": "", "year": "", "description": ""})
            st.rerun()

        st.divider()

        # Skills & Projects
        skills_text = st.text_input("KEAHLIAN (PISAHKAN DENGAN KOMA)", value=", ".join(u.get("skills") or []), key=f"skills_{key_base}")
        
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-top: 8px; margin-bottom: 8px;">Proyek</div>', unsafe_allow_html=True)
        mp = u.get("mainProject") or {}
        c1, c2 = st.columns(2)
        with c1: mp_name = st.text_input("LINK PROYEK UTAMA (NAMA)", value=mp.get("name", ""), key=f"mpname_{key_base}")
        with c2: mp_url = st.text_input("LINK PROYEK UTAMA (URL)", value=mp.get("url", ""), key=f"mpurl_{key_base}")

        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px;">Proyek Lainnya</div>', unsafe_allow_html=True)
        proj_list = st.session_state[f"proj_list_{u['id']}"]
        for i, proj in enumerate(proj_list):
            cols = st.columns([4, 5, 1])
            proj["name"] = cols[0].text_input(f"Nama Proyek_{i}", value=proj.get("name", ""), label_visibility="collapsed", placeholder="Nama Proyek", key=f"proj_name_{i}")
            proj["url"] = cols[1].text_input(f"URL_{i}", value=proj.get("url", ""), label_visibility="collapsed", placeholder="URL Proyek", key=f"proj_url_{i}")
            with cols[2]:
                if st.form_submit_button("✕", key=f"del_proj_{i}"):
                    proj_list.pop(i)
                    st.rerun()
        
        if st.form_submit_button("+ Tambah Proyek Lainnya"):
            proj_list.append({"name": "", "url": ""})
            st.rerun()

        # Save Button
        st.divider()
        submitted = st.form_submit_button("Simpan Perubahan", type="primary", use_container_width=True)

    if submitted:
        u["nim"] = nim.strip()
        u["name"] = name.strip()
        u["role"] = role.strip()
        u["bio"] = bio.strip()
        u["email"] = email.strip()
        u["phone"] = phone.strip()
        u["location"] = location.strip()
        u["skills"] = [s.strip() for s in skills_text.split(",") if s.strip()]
        
        u["education"] = [e for e in edu_list if any(e.values())]
        u["experience"] = [e for e in exp_list if any(e.values())]
        u["otherProjects"] = [p for p in proj_list if any(p.values())]
        u["mainProject"] = {"name": mp_name.strip(), "url": mp_url.strip()}
        
        save_data(data)
        
        # Clear state to force reload from saved data
        del st.session_state[f"edu_list_{u['id']}"]
        del st.session_state[f"exp_list_{u['id']}"]
        del st.session_state[f"proj_list_{u['id']}"]
        
        st.session_state.save_version += 1
        st.session_state.flash = "✅ Data berhasil disimpan."
        st.session_state.scroll_to_top = True
        st.rerun()


def render_files_tab(u: dict, data: dict):
    st.markdown("### Unggah Berkas")
    st.caption("Hanya `.pdf`, `.png`, `.jpeg` · maksimal 5 MB.")

    fu_key = f"file_uploader_{u['id']}_{st.session_state.file_upload_version}"
    new_files = st.file_uploader(
        "Pilih berkas", 
        type=["pdf", "png", "jpeg", "jpg"], 
        accept_multiple_files=True, 
        key=fu_key, 
        disabled=False # Disable only if neither Cloudinary nor local is ready, but local is always ready
    )

    if new_files:
        if st.button("⬆️ Unggah Semua Berkas", type="primary"):
            success_count = 0
            for new_file in new_files:
                ok, msg = validate_upload(new_file)
                if not ok: 
                    st.error(f"❌ {new_file.name}: {msg}")
                    continue
                
                resource_type = "raw" if new_file.type == "application/pdf" else "image"
                result = upload_bytes(new_file.getvalue(), new_file.name, u['id'], resource_type)
                if result:
                    u["files"].append({
                        "name": new_file.name, 
                        "url": result.get("url"),
                        "public_id": result.get("public_id"),
                        "local_path": result.get("local_path"),
                        "type": "pdf" if new_file.type == "application/pdf" else "image",
                    })
                    success_count += 1
            
            if success_count > 0:
                save_data(data)
                st.session_state.file_upload_version += 1
                st.session_state.flash = f"✅ {success_count} berkas berhasil diunggah."
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
        with c2: 
            link = get_file_data_url(f.get("local_path"))
            if link == "#" and f.get("url"):
                link = f.get("url")
            st.link_button("Lihat", link, use_container_width=True)
        with c3:
            if st.button("Hapus", key=f"del_{i}_{f.get('name')}", type="primary"):
                if f.get("public_id"):
                    destroy_on_cloudinary(f.get("public_id"), "raw" if f.get("type") == "pdf" else "image")
                
                # Remove local file
                if f.get("local_path"):
                    local_file = DATA_FILE.parent / f["local_path"]
                    if local_file.exists():
                        try: local_file.unlink()
                        except Exception: pass

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
    st.caption("Sebagai Master Admin, Anda dapat mengganti sandi pengguna tanpa perlu sandi lama.")
    with st.form(f"reset_pwd_{u['id']}"):
        new1 = st.text_input("Sandi baru", type="password")
        if st.form_submit_button("Reset Sandi", type="primary"):
            if len(new1) < 6: st.error("❌ Minimal 6 karakter.")
            else:
                u["password"] = sha256(new1)
                save_data(data)
                st.session_state.flash = f"✅ Sandi {u['name']} berhasil direset."
                st.rerun()

# ════════════════════════════════════════════════════════════════════
# 11. ROUTING
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
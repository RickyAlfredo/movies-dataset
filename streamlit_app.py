"""
E-CV — Step 3: Original color theme + 5 MB file limit enforced.
Access admin via URL param:   ?admin=1
Default credentials:
    Master:  master / capstone12
    User 1:  221001001 / password123
    User 2:  221001002 / password123
    User 3:  221001003 / password123
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
st.set_page_config(page_title="E-CV", page_icon="📄", layout="wide")


# ════════════════════════════════════════════════════════════════════
# 2. CLOUDINARY SETUP
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


# ── 5 MB limit (Streamlit UI will still say "200MB", but code enforces 5 MB) ──
MAX_FILE_BYTES = 5 * 1024 * 1024          # 5 MB
ALLOWED_MIMES = {"application/pdf", "image/png", "image/jpeg"}


def upload_bytes(file_bytes: bytes, filename: str, resource_type: str):
    if not CLOUDINARY_READY:
        st.error("❌ Cloudinary belum dikonfigurasi. Periksa `.streamlit/secrets.toml`.")
        return None
    base = filename.rsplit(".", 1)[0].replace(" ", "_")[:60]
    unique_id = f"ecv_{int(time.time())}_{base}"
    try:
        result = cloudinary.uploader.upload(
            BytesIO(file_bytes),
            resource_type=resource_type,
            folder="ecv",
            public_id=unique_id,
        )
        return {"url": result["secure_url"], "public_id": result["public_id"]}
    except Exception as e:
        st.error(f"❌ Gagal mengunggah ke Cloudinary: {e}")
        return None


def destroy_on_cloudinary(public_id: str, resource_type: str) -> None:
    if not CLOUDINARY_READY or not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception:
        pass


def validate_upload(uploaded) -> tuple[bool, str]:
    if uploaded is None:
        return False, "Tidak ada berkas."
    if uploaded.size > MAX_FILE_BYTES:
        mb = uploaded.size / (1024 * 1024)
        return False, f"Ukuran berkas {mb:.1f} MB melebihi batas 5 MB."
    if uploaded.type not in ALLOWED_MIMES:
        return False, "Hanya berkas .pdf, .png, atau .jpeg yang diizinkan."
    return True, ""


# ════════════════════════════════════════════════════════════════════
# 3. HELPERS
# ════════════════════════════════════════════════════════════════════
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def is_hash(s: str) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)


def esc(s) -> str:
    return html_lib.escape(str(s) if s is not None else "")


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def df_to_records(df, columns: list) -> list:
    if df is None or df.empty:
        return []
    records = []
    for _, row in df.iterrows():
        rec = {}
        for col in columns:
            v = row.get(col)
            rec[col] = "" if pd.isna(v) else str(v).strip()
        if any(rec.values()):
            records.append(rec)
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
            "id": "user1", "name": "Ahmad Fauzi", "nim": "221001001",
            "email": "ahmad.fauzi@example.com", "phone": "+62 812-3456-7890",
            "bio": "Mahasiswa Teknik Informatika yang berfokus pada pengembangan web dan mobile.",
            "password": "password123", "profilePicture": "",
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
            "password": "password123", "profilePicture": "",
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
            "password": "password123", "profilePicture": "",
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
    if changed:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data


# ════════════════════════════════════════════════════════════════════
# 5. SESSION STATE
# ════════════════════════════════════════════════════════════════════
for key, default in [
    ("logged_in_as", None),
    ("is_master", False),
    ("save_version", 0),
    ("flash", None),
    ("file_upload_version", 0),
    ("avatar_upload_version", 0),
    ("dark_mode", False),          # placeholder for later
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════════
# 6. GLOBAL CSS — palette from RickyAlfredo/ecv-project
# ════════════════════════════════════════════════════════════════════
CSS = """
<style>
/* ----- ORIGINAL PALETTE (light) ----- */
:root {
    --bg-base: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    --surface: rgba(255, 255, 255, 0.7);
    --surface-hover: rgba(255, 255, 255, 0.9);
    --border: rgba(200, 214, 229, 0.5);
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-muted: #475569;
    --shadow-glow: 0 8px 32px rgba(30, 41, 59, 0.08);
    --shadow-card: 0 4px 16px rgba(30, 41, 59, 0.04);
    --link-color: #4f46e5;
    --link-hover: #4338ca;
    --gradient-header: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    --gradient-tab: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Streamlit theme overrides */
.stApp {
    background: var(--bg-base) !important;
    background-attachment: fixed !important;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

/* Typography */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    color: var(--text-primary) !important;
}

/* Logo */
.logo {
    font-size: 26px; font-weight: 800;
    margin-bottom: 18px;
    color: var(--text-primary);
}
.logo span { color: #3b82f6; }

/* Profile card */
.profile-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 22px;
    text-align: center;
    box-shadow: var(--shadow-glow);
    backdrop-filter: blur(12px);
}
.avatar, .avatar-img {
    width: 100px; height: 100px; border-radius: 50%;
    margin: 0 auto 16px; display: block;
}
.avatar {
    background: #dbeafe; color: #2563eb;
    display: flex; align-items: center; justify-content: center;
    font-size: 38px; font-weight: 700;
}
.avatar-img { object-fit: cover; border: 3px solid #dbeafe; }
.p-name { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0 0 4px; }
.p-nim  { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.p-bio  { font-size: 13px; color: var(--text-muted); line-height: 1.55; margin-bottom: 16px; text-align: left; }
.p-contact { font-size: 13px; color: var(--text-secondary); margin: 5px 0; text-align: left; word-break: break-word; }

/* Content cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(12px);
}
.card h3 {
    margin: 0 0 14px; font-size: 12px; text-transform: uppercase;
    letter-spacing: 1.2px; color: var(--text-secondary); font-weight: 700;
}

/* Timeline items */
.item { border-left: 3px solid #667eea; padding: 2px 0 2px 14px; margin-bottom: 14px; }
.item:last-child { margin-bottom: 0; }
.item .t { font-weight: 600; font-size: 14px; color: var(--text-primary); }
.item .s { font-size: 12px; color: var(--text-secondary); margin-top: 3px; }
.item .d { font-size: 12px; color: var(--text-muted); margin-top: 6px; line-height: 1.5; }

/* Chips */
.chip {
    display: inline-block; padding: 5px 12px; margin: 3px;
    border-radius: 100px;
    background: rgba(102, 126, 234, 0.12);
    color: #4f46e5;
    font-size: 12px; font-weight: 500;
}

/* File / project rows */
.link-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px; margin-bottom: 8px;
    border-radius: 10px;
    background: var(--surface-hover);
    border: 1px solid var(--border);
    color: var(--text-primary) !important;
    text-decoration: none !important;
    font-size: 13px;
    transition: background 0.2s;
}
.link-row:hover { background: var(--surface); }

/* Main project button */
.project-main {
    display: block; padding: 14px; border-radius: 10px;
    background: var(--gradient-tab);
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 600; text-align: center; font-size: 14px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    transition: transform 0.2s;
}
.project-main:hover { transform: scale(1.02); }

/* Empty state */
.empty { font-size: 13px; color: #94a3b8; font-style: italic; padding: 8px 0; }

/* Streamlit native element tweaks */
div[data-testid="stTabs"] button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: var(--text-secondary) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: var(--gradient-tab) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    border: none !important;
}
div[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.2rem;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(12px);
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 7. PUBLIC VIEW
# ════════════════════════════════════════════════════════════════════
def render_public_view(users: list):
    st.markdown('<div class="logo">E-<span>CV</span></div>', unsafe_allow_html=True)

    tabs = st.tabs([u["name"] for u in users])

    for tab, u in zip(tabs, users):
        with tab:
            col_left, col_right = st.columns([1, 2.4], gap="large")

            with col_left:
                if u.get("profilePicture"):
                    avatar_html = f'<img class="avatar-img" src="{esc(u["profilePicture"])}" alt="avatar" />'
                else:
                    avatar_html = f'<div class="avatar">{esc((u["name"] or "?")[0])}</div>'

                st.markdown(f"""
                    <div class="profile-card">
                        {avatar_html}
                        <div class="p-name">{esc(u['name'])}</div>
                        <div class="p-nim">NIM {esc(u['nim'])}</div>
                        <div class="p-bio">{esc(u['bio'])}</div>
                        <div class="p-contact">📧 {esc(u['email'])}</div>
                        <div class="p-contact">📱 {esc(u['phone'])}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_right:
                edu_html = "".join(
                    f'<div class="item"><div class="t">{esc(e.get("degree", ""))}</div>'
                    f'<div class="s">{esc(e.get("institution", ""))} · {esc(e.get("year", ""))}</div></div>'
                    for e in (u.get("education") or [])
                ) or '<div class="empty">Belum ada data pendidikan.</div>'
                st.markdown(f'<div class="card"><h3>Pendidikan</h3>{edu_html}</div>',
                            unsafe_allow_html=True)

                exp_html = "".join(
                    f'<div class="item"><div class="t">{esc(e.get("role", ""))}</div>'
                    f'<div class="s">{esc(e.get("company", ""))} · {esc(e.get("year", ""))}</div>'
                    f'<div class="d">{esc(e.get("description", ""))}</div></div>'
                    for e in (u.get("experience") or [])
                ) or '<div class="empty">Belum ada pengalaman.</div>'
                st.markdown(f'<div class="card"><h3>Pengalaman</h3>{exp_html}</div>',
                            unsafe_allow_html=True)

                skill_html = "".join(
                    f'<span class="chip">{esc(s)}</span>'
                    for s in (u.get("skills") or [])
                ) or '<div class="empty">Belum ada keahlian.</div>'
                st.markdown(f'<div class="card"><h3>Keahlian</h3>{skill_html}</div>',
                            unsafe_allow_html=True)

                mp = u.get("mainProject") or {}
                st.markdown(
                    f'<div class="card"><h3>Proyek Utama</h3>'
                    f'<a class="project-main" href="{esc(mp.get("url", "#"))}" target="_blank" rel="noopener">'
                    f'{esc(mp.get("name", "—"))}</a></div>',
                    unsafe_allow_html=True,
                )

                proj_html = "".join(
                    f'<a class="link-row" href="{esc(p.get("url", "#"))}" target="_blank" rel="noopener">'
                    f'<span>🔗 {esc(p.get("name", ""))}</span><span>↗</span></a>'
                    for p in (u.get("otherProjects") or [])
                ) or '<div class="empty">Belum ada proyek lain.</div>'
                st.markdown(f'<div class="card"><h3>Proyek Lainnya</h3>{proj_html}</div>',
                            unsafe_allow_html=True)

                files_html = "".join(
                    f'<a class="link-row" href="{esc(f.get("url", "#"))}" target="_blank" rel="noopener">'
                    f'<span>{"📄" if f.get("type") == "pdf" else "🖼️"} {esc(f.get("name", ""))}</span>'
                    f'<span>⬇️</span></a>'
                    for f in (u.get("files") or [])
                ) or '<div class="empty">Belum ada berkas.</div>'
                st.markdown(f'<div class="card"><h3>Berkas</h3>{files_html}</div>',
                            unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 8. LOGIN VIEW
# ════════════════════════════════════════════════════════════════════
def render_login_page(data: dict):
    st.markdown('<div class="logo">E-<span>CV</span> · Admin</div>', unsafe_allow_html=True)
    st.subheader("🔐 Login Admin")
    st.caption("Masukkan NIM dan sandi Anda, atau `master` dan sandi master.")

    with st.form("login_form"):
        username = st.text_input("NIM / Username", placeholder="221001001 atau master")
        password = st.text_input("Sandi", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Masuk", type="primary", use_container_width=True)

    if submitted:
        username_norm = username.strip()
        if not username_norm or not password:
            st.error("❌ NIM dan sandi wajib diisi.")
        elif username_norm.lower() == "master":
            if sha256(password) == data["masterPassword"]:
                st.session_state.logged_in_as = "master"
                st.session_state.is_master = True
                st.session_state.flash = "✅ Selamat datang, Master Admin."
                st.rerun()
            else:
                st.error("❌ Sandi master salah.")
        else:
            user = next((u for u in data["users"] if u["nim"] == username_norm), None)
            if user and sha256(password) == user["password"]:
                st.session_state.logged_in_as = user["id"]
                st.session_state.is_master = False
                st.session_state.flash = f"✅ Selamat datang, {user['name']}."
                st.rerun()
            else:
                st.error("❌ NIM atau sandi salah.")

    st.divider()
    if st.button("← Kembali ke Publik", use_container_width=True):
        st.query_params.clear()
        st.rerun()


# ════════════════════════════════════════════════════════════════════
# 9. ADMIN PANEL
# ════════════════════════════════════════════════════════════════════
def render_admin_panel(data: dict):
    is_master = st.session_state.is_master
    current_user_id = st.session_state.logged_in_as

    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🔐 Admin Panel")
        if is_master:
            st.caption("Masuk sebagai **Master Admin**")
        else:
            cu = next(u for u in data["users"] if u["id"] == current_user_id)
            st.caption(f"Masuk sebagai **{cu['name']}** ({cu['nim']})")
        if not CLOUDINARY_READY:
            st.warning("⚠️ Cloudinary belum dikonfigurasi — unggah berkas dinonaktifkan.")
    with col2:
        if st.button("🚪 Keluar", type="primary", use_container_width=True):
            st.session_state.logged_in_as = None
            st.session_state.is_master = False
            st.session_state.flash = None
            st.query_params.clear()
            st.rerun()

    if st.session_state.flash:
        st.success(st.session_state.flash)
        st.session_state.flash = None

    st.divider()

    if is_master:
        options = {f"{u['name']} ({u['nim']})": u["id"] for u in data["users"]}
        selected_label = st.selectbox("Pilih pengguna yang akan dikelola", list(options.keys()))
        target_user_id = options[selected_label]
    else:
        target_user_id = current_user_id

    target_user = next(u for u in data["users"] if u["id"] == target_user_id)

    if is_master:
        tab_labels = ["📝 Edit Data", "📁 Berkas", "🔄 Reset Sandi"]
    else:
        tab_labels = ["📝 Edit Data", "📁 Berkas", "🔑 Ubah Sandi"]

    tabs = st.tabs(tab_labels)

    with tabs[0]:
        render_edit_data_tab(target_user, data)

    with tabs[1]:
        render_files_tab(target_user, data)

    with tabs[2]:
        if is_master:
            render_reset_password_tab(target_user, data)
        else:
            render_change_password_tab(target_user, data)


def render_edit_data_tab(u: dict, data: dict):
    # ── Foto Profil ──
    st.markdown("#### Foto Profil")
    av_col1, av_col2 = st.columns([1, 3])
    with av_col1:
        if u.get("profilePicture"):
            st.image(u["profilePicture"], width=120)
        else:
            initials = esc((u["name"] or "?")[0])
            st.markdown(
                f'<div style="width:120px;height:120px;border-radius:50%;'
                f'background:#dbeafe;color:#2563eb;display:flex;align-items:center;'
                f'justify-content:center;font-size:44px;font-weight:700;">{initials}</div>',
                unsafe_allow_html=True,
            )
    with av_col2:
        av_key = f"avatar_uploader_{u['id']}_{st.session_state.avatar_upload_version}"
        avatar_file = st.file_uploader(
            "Unggah foto profil (.png / .jpeg · maks 5 MB)",
            type=["png", "jpeg", "jpg"],
            key=av_key,
            disabled=not CLOUDINARY_READY,
        )
        if avatar_file is not None:
            ok, msg = validate_upload(avatar_file)
            if not ok:
                st.error(f"❌ {msg}")
            else:
                if st.button("⬆️ Unggah Foto Profil", key=f"av_btn_{av_key}", type="primary"):
                    result = upload_bytes(avatar_file.getvalue(), avatar_file.name, "image")
                    if result:
                        u["profilePicture"] = result["url"]
                        save_data(data)
                        st.session_state.avatar_upload_version += 1
                        st.session_state.flash = "✅ Foto profil berhasil diperbarui."
                        st.rerun()
        if u.get("profilePicture"):
            if st.button("🗑️ Hapus Foto Profil", key=f"av_del_{av_key}"):
                u["profilePicture"] = ""
                save_data(data)
                st.session_state.avatar_upload_version += 1
                st.session_state.flash = "✅ Foto profil dihapus."
                st.rerun()

    st.divider()

    version = st.session_state.save_version
    key_base = f"{u['id']}_{version}"

    with st.form(f"edit_form_{key_base}"):
        st.markdown("#### Data Dasar")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nama Lengkap", value=u.get("name", ""), key=f"name_{key_base}")
            email = st.text_input("Email", value=u.get("email", ""), key=f"email_{key_base}")
        with col2:
            nim = st.text_input("NIM", value=u.get("nim", ""), key=f"nim_{key_base}")
            phone = st.text_input("Telepon", value=u.get("phone", ""), key=f"phone_{key_base}")

        bio = st.text_area("Bio", value=u.get("bio", ""), key=f"bio_{key_base}", height=90)
        skills_text = st.text_input(
            "Keahlian (pisahkan dengan koma)",
            value=", ".join(u.get("skills") or []),
            key=f"skills_{key_base}",
        )

        st.markdown("#### Pendidikan")
        edu_df = pd.DataFrame(u.get("education") or [], columns=["degree", "institution", "year"])
        edited_edu = st.data_editor(edu_df, num_rows="dynamic", use_container_width=True,
                                    key=f"edu_editor_{key_base}")

        st.markdown("#### Pengalaman")
        exp_df = pd.DataFrame(u.get("experience") or [], columns=["role", "company", "year", "description"])
        edited_exp = st.data_editor(exp_df, num_rows="dynamic", use_container_width=True,
                                    key=f"exp_editor_{key_base}")

        st.markdown("#### Proyek Utama")
        mp = u.get("mainProject") or {}
        col1, col2 = st.columns(2)
        with col1:
            mp_name = st.text_input("Nama Proyek Utama", value=mp.get("name", ""), key=f"mpname_{key_base}")
        with col2:
            mp_url = st.text_input("URL Proyek Utama", value=mp.get("url", ""), key=f"mpurl_{key_base}")

        st.markdown("#### Proyek Lainnya")
        proj_df = pd.DataFrame(u.get("otherProjects") or [], columns=["name", "url"])
        edited_proj = st.data_editor(proj_df, num_rows="dynamic", use_container_width=True,
                                     key=f"proj_editor_{key_base}")

        submitted = st.form_submit_button("💾 Simpan Perubahan", type="primary", use_container_width=True)

    if submitted:
        u["name"] = name.strip()
        u["nim"] = nim.strip()
        u["email"] = email.strip()
        u["phone"] = phone.strip()
        u["bio"] = bio.strip()
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
    st.markdown("#### Unggah Berkas Baru")
    st.caption("Hanya `.pdf`, `.png`, `.jpeg` · **maksimal 5 MB** per berkas.")

    fu_key = f"file_uploader_{u['id']}_{st.session_state.file_upload_version}"
    new_file = st.file_uploader(
        "Pilih berkas",
        type=["pdf", "png", "jpeg", "jpg"],
        key=fu_key,
        disabled=not CLOUDINARY_READY,
    )

    if new_file is not None:
        ok, msg = validate_upload(new_file)
        if not ok:
            st.error(f"❌ {msg}")
        else:
            st.info(f"📎 **{new_file.name}** · {new_file.size / 1024:.1f} KB")
            if st.button("⬆️ Unggah Berkas", type="primary", key=f"fu_btn_{fu_key}"):
                resource_type = "raw" if new_file.type == "application/pdf" else "image"
                result = upload_bytes(new_file.getvalue(), new_file.name, resource_type)
                if result:
                    u["files"].append({
                        "name": new_file.name,
                        "url": result["url"],
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
        st.markdown('<div class="empty">Belum ada berkas.</div>', unsafe_allow_html=True)
        return

    for i, f in enumerate(files):
        col1, col2, col3 = st.columns([4, 1.2, 1])
        with col1:
            icon = "📄" if f.get("type") == "pdf" else "🖼️"
            st.markdown(f"{icon} **{esc(f.get('name', 'tanpa nama'))}**")
        with col2:
            st.link_button("👁️ Lihat", f.get("url", "#"), use_container_width=True)
        with col3:
            unique_key = f"del_{u['id']}_{i}_{f.get('public_id', f.get('name', 'x'))}"
            if st.button("🗑️ Hapus", key=unique_key, use_container_width=True):
                destroy_on_cloudinary(
                    f.get("public_id", ""),
                    "raw" if f.get("type") == "pdf" else "image",
                )
                u["files"].remove(f)
                save_data(data)
                st.session_state.flash = f"✅ Berkas '{f.get('name')}' dihapus."
                st.rerun()


def render_change_password_tab(u: dict, data: dict):
    st.markdown("#### Ubah Sandi Anda")
    st.caption("Minimal 6 karakter. Sandi lama wajib dimasukkan untuk verifikasi.")

    with st.form(f"change_pwd_{u['id']}"):
        old = st.text_input("Sandi lama", type="password")
        new1 = st.text_input("Sandi baru", type="password")
        new2 = st.text_input("Konfirmasi sandi baru", type="password")
        submitted = st.form_submit_button("Ubah Sandi", type="primary", use_container_width=True)

    if submitted:
        if sha256(old) != u["password"]:
            st.error("❌ Sandi lama salah.")
        elif len(new1) < 6:
            st.error("❌ Sandi baru minimal 6 karakter.")
        elif new1 != new2:
            st.error("❌ Konfirmasi sandi tidak cocok.")
        else:
            u["password"] = sha256(new1)
            save_data(data)
            st.session_state.flash = "✅ Sandi berhasil diubah."
            st.rerun()


def render_reset_password_tab(u: dict, data: dict):
    st.markdown(f"#### Reset Sandi: {u['name']} ({u['nim']})")
    st.caption("Sebagai Master Admin, Anda dapat mengganti sandi pengguna tanpa perlu sandi lama.")

    with st.form(f"reset_pwd_{u['id']}"):
        new1 = st.text_input("Sandi baru", type="password")
        new2 = st.text_input("Konfirmasi sandi baru", type="password")
        submitted = st.form_submit_button("Reset Sandi", type="primary", use_container_width=True)

    if submitted:
        if len(new1) < 6:
            st.error("❌ Sandi baru minimal 6 karakter.")
        elif new1 != new2:
            st.error("❌ Konfirmasi sandi tidak cocok.")
        else:
            u["password"] = sha256(new1)
            save_data(data)
            st.session_state.flash = f"✅ Sandi {u['name']} berhasil direset."
            st.rerun()


# ════════════════════════════════════════════════════════════════════
# 10. ROUTING
# ════════════════════════════════════════════════════════════════════
data = load_and_migrate()

is_logged_in = st.session_state.logged_in_as is not None
admin_mode = st.query_params.get("admin") == "1"

if is_logged_in:
    render_admin_panel(data)
elif admin_mode:
    render_login_page(data)
else:
    render_public_view(data["users"])
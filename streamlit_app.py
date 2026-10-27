"""
E-CV — Step 1: Public view + Hidden Admin (login + edit data + passwords)
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
from pathlib import Path

import pandas as pd
import streamlit as st

# ════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="E-CV", page_icon="📄", layout="wide")


# ════════════════════════════════════════════════════════════════════
# 2. HELPERS
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
    """Convert a dataframe (from st.data_editor) into a list of dicts, skipping empty rows."""
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
# 3. SEED + PERSISTENCE
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
            "password": "password123",
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
            "password": "password123",
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
            "password": "password123",
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
    """Load users.json, creating and/or hashing plaintext passwords as needed."""
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

    if changed:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return data


# ════════════════════════════════════════════════════════════════════
# 4. SESSION STATE
# ════════════════════════════════════════════════════════════════════
if "logged_in_as" not in st.session_state:
    st.session_state.logged_in_as = None
if "is_master" not in st.session_state:
    st.session_state.is_master = False
if "save_version" not in st.session_state:
    st.session_state.save_version = 0
if "flash" not in st.session_state:
    st.session_state.flash = None


# ════════════════════════════════════════════════════════════════════
# 5. GLOBAL CSS (applies to both public and admin)
# ════════════════════════════════════════════════════════════════════
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


# ════════════════════════════════════════════════════════════════════
# 6. PUBLIC VIEW
# ════════════════════════════════════════════════════════════════════
def render_public_view(users: list):
    st.markdown('<div class="logo">E-<span>CV</span></div>', unsafe_allow_html=True)

    tabs = st.tabs([u["name"] for u in users])

    for tab, u in zip(tabs, users):
        with tab:
            col_left, col_right = st.columns([1, 2.4], gap="large")

            # ── LEFT: Profile
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

            # ── RIGHT: Content
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
# 7. LOGIN VIEW
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
# 8. ADMIN PANEL
# ════════════════════════════════════════════════════════════════════
def render_admin_panel(data: dict):
    is_master = st.session_state.is_master
    current_user_id = st.session_state.logged_in_as

    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🔐 Admin Panel")
        if is_master:
            st.caption("Masuk sebagai **Master Admin**")
        else:
            cu = next(u for u in data["users"] if u["id"] == current_user_id)
            st.caption(f"Masuk sebagai **{cu['name']}** ({cu['nim']})")
    with col2:
        if st.button("🚪 Keluar", type="primary", use_container_width=True):
            st.session_state.logged_in_as = None
            st.session_state.is_master = False
            st.session_state.flash = None
            st.query_params.clear()
            st.rerun()

    # Flash message
    if st.session_state.flash:
        st.success(st.session_state.flash)
        st.session_state.flash = None

    st.divider()

    # Target selector (master only)
    if is_master:
        options = {f"{u['name']} ({u['nim']})": u["id"] for u in data["users"]}
        selected_label = st.selectbox("Pilih pengguna yang akan dikelola", list(options.keys()))
        target_user_id = options[selected_label]
    else:
        target_user_id = current_user_id

    target_user = next(u for u in data["users"] if u["id"] == target_user_id)

    # Tabs
    if is_master:
        tab_labels = ["📝 Edit Data", "🔄 Reset Sandi"]
    else:
        tab_labels = ["📝 Edit Data", "🔑 Ubah Sandi"]

    tabs = st.tabs(tab_labels)

    with tabs[0]:
        render_edit_data_tab(target_user, data)

    with tabs[1]:
        if is_master:
            render_reset_password_tab(target_user, data)
        else:
            render_change_password_tab(target_user, data)


# ── Edit Data tab ────────────────────────────────────────────────
def render_edit_data_tab(u: dict, data: dict):
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
        edited_edu = st.data_editor(
            edu_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"edu_editor_{key_base}",
        )

        st.markdown("#### Pengalaman")
        exp_df = pd.DataFrame(u.get("experience") or [], columns=["role", "company", "year", "description"])
        edited_exp = st.data_editor(
            exp_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"exp_editor_{key_base}",
        )

        st.markdown("#### Proyek Utama")
        mp = u.get("mainProject") or {}
        col1, col2 = st.columns(2)
        with col1:
            mp_name = st.text_input("Nama Proyek Utama", value=mp.get("name", ""), key=f"mpname_{key_base}")
        with col2:
            mp_url = st.text_input("URL Proyek Utama", value=mp.get("url", ""), key=f"mpurl_{key_base}")

        st.markdown("#### Proyek Lainnya")
        proj_df = pd.DataFrame(u.get("otherProjects") or [], columns=["name", "url"])
        edited_proj = st.data_editor(
            proj_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"proj_editor_{key_base}",
        )

        submitted = st.form_submit_button(
            "💾 Simpan Perubahan", type="primary", use_container_width=True
        )

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


# ── Change Password tab (non-master) ─────────────────────────────
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


# ── Reset Password tab (master only) ─────────────────────────────
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
# 9. ROUTING
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
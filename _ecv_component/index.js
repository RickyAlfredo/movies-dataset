/* E-CV Streamlit Custom Component — full frontend */
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

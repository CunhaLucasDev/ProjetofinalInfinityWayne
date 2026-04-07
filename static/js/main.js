/* ============================================================
   WAYNE INDUSTRIES – main.js
   ============================================================ */

// ─── TOAST ────────────────────────────────────────────────

const ICONS = { success: '✓', error: '✗', warning: '⚠', info: 'ℹ' };

function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `toast t-${type}`;
  el.innerHTML = `<span style="font-size:15px">${ICONS[type] || '•'}</span><span>${msg}</span>`;
  container.appendChild(el);

  setTimeout(() => {
    el.style.transition = 'opacity .3s, transform .3s';
    el.style.opacity = '0';
    el.style.transform = 'translateX(12px)';
    setTimeout(() => el.remove(), 320);
  }, 3500);
}

// ─── MODAL ────────────────────────────────────────────────

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('open');
  const form = el.querySelector('form');
  if (form) form.reset();
}

// Fechar ao clicar no overlay
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('overlay')) {
    e.target.classList.remove('open');
  }
});

// Fechar com ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.overlay.open').forEach(m => m.classList.remove('open'));
  }
});

// ─── API ──────────────────────────────────────────────────

async function apiCall(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Erro desconhecido');
  return data;
}

// ─── TABLE SEARCH ─────────────────────────────────────────

function filterTable(inputId, tbodyId) {
  const q = document.getElementById(inputId).value.toLowerCase();
  const rows = document.querySelectorAll(`#${tbodyId} tr`);
  rows.forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

// ─── RESOURCES ────────────────────────────────────────────

let _editResId = null;

function openAddResource() {
  _editResId = null;
  document.getElementById('res-modal-title').textContent = 'Novo Recurso';
  document.getElementById('res-form').reset();
  openModal('res-modal');
}

function openEditResource(id, name, type, status, location, description) {
  _editResId = id;
  document.getElementById('res-modal-title').textContent = 'Editar Recurso';
  document.getElementById('r-name').value        = name;
  document.getElementById('r-type').value        = type;
  document.getElementById('r-status').value      = status;
  document.getElementById('r-location').value    = location;
  document.getElementById('r-description').value = description;
  openModal('res-modal');
}

async function saveResource() {
  const data = {
    name:        document.getElementById('r-name').value.trim(),
    type:        document.getElementById('r-type').value,
    status:      document.getElementById('r-status').value,
    location:    document.getElementById('r-location').value.trim(),
    description: document.getElementById('r-description').value.trim(),
  };

  if (!data.name) { showToast('O nome é obrigatório.', 'error'); return; }

  const saveBtn = document.getElementById('res-save-btn');
  saveBtn.disabled = true;
  saveBtn.textContent = 'Salvando…';

  try {
    if (_editResId) {
      await apiCall(`/api/resources/${_editResId}`, 'PUT', data);
      showToast('Recurso atualizado com sucesso!');
    } else {
      await apiCall('/api/resources', 'POST', data);
      showToast('Recurso adicionado com sucesso!');
    }
    closeModal('res-modal');
    setTimeout(() => location.reload(), 900);
  } catch (err) {
    showToast(err.message, 'error');
    saveBtn.disabled = false;
    saveBtn.textContent = 'Salvar';
  }
}

async function deleteResource(id, name) {
  if (!confirm(`Confirmar exclusão de:\n"${name}"\n\nEssa ação não pode ser desfeita.`)) return;
  try {
    await apiCall(`/api/resources/${id}`, 'DELETE');
    showToast('Recurso removido.');
    setTimeout(() => location.reload(), 900);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ─── USERS ────────────────────────────────────────────────

let _editUserId = null;

function openAddUser() {
  _editUserId = null;
  document.getElementById('user-modal-title').textContent = 'Novo Usuário';
  document.getElementById('user-form').reset();
  document.getElementById('u-password').required = true;
  const hint = document.getElementById('pw-hint');
  if (hint) hint.style.display = 'none';
  openModal('user-modal');
}

function openEditUser(id, name, email, role, active) {
  _editUserId = id;
  document.getElementById('user-modal-title').textContent = 'Editar Usuário';
  document.getElementById('u-name').value   = name;
  document.getElementById('u-email').value  = email;
  document.getElementById('u-role').value   = role;
  document.getElementById('u-active').value = active ? '1' : '0';
  document.getElementById('u-password').value    = '';
  document.getElementById('u-password').required = false;
  const hint = document.getElementById('pw-hint');
  if (hint) hint.style.display = 'block';
  openModal('user-modal');
}

async function saveUser() {
  const data = {
    name:     document.getElementById('u-name').value.trim(),
    email:    document.getElementById('u-email').value.trim(),
    role:     document.getElementById('u-role').value,
    active:   parseInt(document.getElementById('u-active').value),
    password: document.getElementById('u-password').value,
  };

  if (!data.name || !data.email) { showToast('Nome e e-mail são obrigatórios.', 'error'); return; }
  if (!_editUserId && !data.password) { showToast('A senha é obrigatória para novos usuários.', 'error'); return; }

  const saveBtn = document.getElementById('user-save-btn');
  saveBtn.disabled = true;
  saveBtn.textContent = 'Salvando…';

  try {
    if (_editUserId) {
      await apiCall(`/api/users/${_editUserId}`, 'PUT', data);
      showToast('Usuário atualizado!');
    } else {
      await apiCall('/api/users', 'POST', data);
      showToast('Usuário criado com sucesso!');
    }
    closeModal('user-modal');
    setTimeout(() => location.reload(), 900);
  } catch (err) {
    showToast(err.message, 'error');
    saveBtn.disabled = false;
    saveBtn.textContent = 'Salvar';
  }
}

async function deleteUser(id, name) {
  if (!confirm(`Confirmar exclusão do usuário:\n"${name}"`)) return;
  try {
    await apiCall(`/api/users/${id}`, 'DELETE');
    showToast('Usuário removido.');
    setTimeout(() => location.reload(), 900);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ─── CHARTS ───────────────────────────────────────────────

function initCharts(stats) {
  if (typeof Chart === 'undefined') return;

  Chart.defaults.color = '#888';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";

  // Doughnut – por tipo
  const typeEl = document.getElementById('chart-type');
  if (typeEl) {
    new Chart(typeEl, {
      type: 'doughnut',
      data: {
        labels: ['Veículos', 'Equipamentos', 'Dispositivos de Segurança'],
        datasets: [{
          data: [stats.vehicles, stats.equipment, stats.security_devices],
          backgroundColor: ['#8e44ad', '#2980b9', '#c0392b'],
          borderColor: '#141414',
          borderWidth: 4,
          hoverOffset: 8,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { position: 'bottom', labels: { padding: 16, boxWidth: 10, font: { size: 11 } } }
        }
      }
    });
  }

  // Bar – por status
  const statusEl = document.getElementById('chart-status');
  if (statusEl) {
    new Chart(statusEl, {
      type: 'bar',
      data: {
        labels: ['Operacional', 'Manutenção', 'Inativo'],
        datasets: [{
          label: 'Recursos',
          data: [stats.operational, stats.maintenance, stats.inactive],
          backgroundColor: [
            'rgba(39,174,96,.75)', 'rgba(230,126,34,.75)', 'rgba(192,57,43,.75)'
          ],
          borderColor: ['#27ae60', '#e67e22', '#c0392b'],
          borderWidth: 1,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#222' }, ticks: { color: '#888', font: { size: 11 } } },
          y: {
            grid: { color: '#222' },
            ticks: { color: '#888', stepSize: 1, font: { size: 11 } },
            beginAtZero: true,
          }
        }
      }
    });
  }

  // Bar – usuários por perfil
  const usersEl = document.getElementById('chart-users');
  if (usersEl) {
    new Chart(usersEl, {
      type: 'bar',
      data: {
        labels: ['Admin', 'Gerente', 'Funcionário'],
        datasets: [{
          label: 'Usuários',
          data: [stats.admins, stats.managers, stats.employees],
          backgroundColor: [
            'rgba(192,57,43,.75)', 'rgba(41,128,185,.75)', 'rgba(100,100,100,.65)'
          ],
          borderColor: ['#c0392b', '#2980b9', '#666'],
          borderWidth: 1,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#222' }, ticks: { color: '#888', font: { size: 11 } } },
          y: {
            grid: { color: '#222' },
            ticks: { color: '#888', stepSize: 1, font: { size: 11 } },
            beginAtZero: true,
          }
        }
      }
    });
  }
}

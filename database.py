import sqlite3
import hashlib
from datetime import datetime

DB_PATH = 'wayne.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'employee',
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'operational',
        location TEXT,
        description TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        resource_id INTEGER,
        ip_address TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    conn.commit()

    # Cria dados padrão se não existir admin
    existing = c.execute('SELECT id FROM users WHERE role = "admin"').fetchone()
    if not existing:
        _create_default_data(c)
        conn.commit()

    conn.close()


def _create_default_data(c):
    now = datetime.now().isoformat()

    users = [
        ('Bruce Wayne',       'bruce@wayne.com',  hash_password('batman123'),  'admin'),
        ('Alfred Pennyworth', 'alfred@wayne.com', hash_password('butler456'),  'manager'),
        ('Lucius Fox',        'lucius@wayne.com', hash_password('tech789'),    'manager'),
        ('Dick Grayson',      'dick@wayne.com',   hash_password('robin101'),   'employee'),
    ]
    for name, email, pw, role in users:
        c.execute(
            'INSERT INTO users (name, email, password_hash, role, active, created_at) VALUES (?,?,?,?,1,?)',
            (name, email, pw, role, now)
        )

    resources = [
        ('Batmóvel',                    'vehicle',         'operational', 'Hangar B-1',        'Veículo principal de patrulha'),
        ('Batwing',                     'vehicle',         'maintenance', 'Hangar A-1',        'Aeronave stealth furtiva'),
        ('Traje de Combate v3',         'equipment',       'operational', 'Arsenal Principal', 'Traje blindado de titânio reforçado'),
        ('Computador Forense',          'equipment',       'operational', 'Batcaverna',        'Análise de evidências digitais'),
        ('Câmera de Segurança #47',     'security_device', 'operational', 'Portão Leste',      'Câmera 4K com visão noturna'),
        ('Sistema de Alarme Central',   'security_device', 'operational', 'Torre de Controle', 'Monitoramento 24h da sede'),
        ('Helicóptero de Reconhecimento','vehicle',        'inactive',    'Hangar C-2',        'Em revisão anual programada'),
        ('Dispositivo de Escuta Avançado','security_device','operational','Laboratório 3',     'Alcance de até 5 km'),
    ]
    for name, rtype, status, loc, desc in resources:
        c.execute(
            'INSERT INTO resources (name, type, status, location, description, created_at, updated_at) VALUES (?,?,?,?,?,?,?)',
            (name, rtype, status, loc, desc, now, now)
        )


# ─── HELPERS ────────────────────────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(user, password):
    return user['password_hash'] == hash_password(password)


# ─── USERS ───────────────────────────────────────────────────────────────────

def get_user_by_email(email):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user


def get_all_users():
    conn = get_db()
    rows = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_user(name, email, password, role):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        'INSERT INTO users (name, email, password_hash, role, active, created_at) VALUES (?,?,?,?,1,?)',
        (name, email, hash_password(password), role, now)
    )
    conn.commit()
    conn.close()


def update_user(uid, data):
    conn = get_db()
    if data.get('password'):
        conn.execute(
            'UPDATE users SET name=?, role=?, active=?, password_hash=? WHERE id=?',
            (data['name'], data['role'], data.get('active', 1), hash_password(data['password']), uid)
        )
    else:
        conn.execute(
            'UPDATE users SET name=?, role=?, active=? WHERE id=?',
            (data['name'], data['role'], data.get('active', 1), uid)
        )
    conn.commit()
    conn.close()


def delete_user(uid):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id=?', (uid,))
    conn.commit()
    conn.close()


# ─── RESOURCES ───────────────────────────────────────────────────────────────

def get_all_resources():
    conn = get_db()
    rows = conn.execute('SELECT * FROM resources ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_resource(name, rtype, status, location, description):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        'INSERT INTO resources (name, type, status, location, description, created_at, updated_at) VALUES (?,?,?,?,?,?,?)',
        (name, rtype, status, location, description, now, now)
    )
    conn.commit()
    conn.close()


def update_resource(rid, data):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        'UPDATE resources SET name=?, type=?, status=?, location=?, description=?, updated_at=? WHERE id=?',
        (data['name'], data['type'], data['status'], data['location'], data['description'], now, rid)
    )
    conn.commit()
    conn.close()


def delete_resource(rid):
    conn = get_db()
    conn.execute('DELETE FROM resources WHERE id=?', (rid,))
    conn.commit()
    conn.close()


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_db()

    def count(q, *args):
        return conn.execute(q, args).fetchone()[0]

    stats = {
        'total_resources':  count('SELECT COUNT(*) FROM resources'),
        'total_users':      count('SELECT COUNT(*) FROM users WHERE active=1'),
        'operational':      count('SELECT COUNT(*) FROM resources WHERE status="operational"'),
        'maintenance':      count('SELECT COUNT(*) FROM resources WHERE status="maintenance"'),
        'inactive':         count('SELECT COUNT(*) FROM resources WHERE status="inactive"'),
        'vehicles':         count('SELECT COUNT(*) FROM resources WHERE type="vehicle"'),
        'equipment':        count('SELECT COUNT(*) FROM resources WHERE type="equipment"'),
        'security_devices': count('SELECT COUNT(*) FROM resources WHERE type="security_device"'),
        'admins':           count('SELECT COUNT(*) FROM users WHERE role="admin" AND active=1'),
        'managers':         count('SELECT COUNT(*) FROM users WHERE role="manager" AND active=1'),
        'employees':        count('SELECT COUNT(*) FROM users WHERE role="employee" AND active=1'),
    }
    conn.close()
    return stats


# ─── LOGS ────────────────────────────────────────────────────────────────────

def log_action(user_id, action, resource_id, ip_address):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        'INSERT INTO access_logs (user_id, action, resource_id, ip_address, timestamp) VALUES (?,?,?,?,?)',
        (user_id, action, resource_id, ip_address, now)
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit=10):
    conn = get_db()
    rows = conn.execute('''
        SELECT al.*, u.name AS user_name
        FROM access_logs al
        LEFT JOIN users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

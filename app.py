from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from functools import wraps
import database as db

app = Flask(__name__)
app.secret_key = 'wayne-industries-batcave-2024'


# ─── DECORATORS ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                return jsonify({'error': 'Acesso negado. Permissão insuficiente.'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = db.get_user_by_email(email)

        if user and db.check_password(user, password):
            if not user['active']:
                flash('Conta desativada. Contate o administrador.', 'error')
                return render_template('login.html')
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            db.log_action(user['id'], 'LOGIN', None, request.remote_addr)
            return redirect(url_for('dashboard'))

        flash('E-mail ou senha inválidos.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'user_id' in session:
        db.log_action(session['user_id'], 'LOGOUT', None, request.remote_addr)
        session.clear()
    return redirect(url_for('login'))


# ─── PAGE ROUTES ─────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.get_dashboard_stats()
    logs  = db.get_recent_logs(10)
    return render_template('dashboard.html', stats=stats, logs=logs)


@app.route('/resources')
@login_required
def resources():
    items = db.get_all_resources()
    return render_template('resources.html', resources=items)


@app.route('/users')
@login_required
def users():
    if session.get('role') != 'admin':
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('dashboard'))
    all_users = db.get_all_users()
    return render_template('users.html', users=all_users)


# ─── RESOURCES API ───────────────────────────────────────────────────────────

@app.route('/api/resources', methods=['POST'])
@roles_required('admin', 'manager')
def api_add_resource():
    data = request.json or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Nome é obrigatório.'}), 400

    db.add_resource(name, data.get('type', 'equipment'),
                    data.get('status', 'operational'),
                    data.get('location', ''), data.get('description', ''))
    db.log_action(session['user_id'], 'ADD_RESOURCE', None, request.remote_addr)
    return jsonify({'success': True})


@app.route('/api/resources/<int:rid>', methods=['PUT'])
@roles_required('admin', 'manager')
def api_update_resource(rid):
    data = request.json or {}
    db.update_resource(rid, data)
    db.log_action(session['user_id'], 'UPDATE_RESOURCE', rid, request.remote_addr)
    return jsonify({'success': True})


@app.route('/api/resources/<int:rid>', methods=['DELETE'])
@roles_required('admin')
def api_delete_resource(rid):
    db.delete_resource(rid)
    db.log_action(session['user_id'], 'DELETE_RESOURCE', rid, request.remote_addr)
    return jsonify({'success': True})


# ─── USERS API ───────────────────────────────────────────────────────────────

@app.route('/api/users', methods=['POST'])
@roles_required('admin')
def api_add_user():
    data = request.json or {}
    try:
        db.add_user(data['name'], data['email'], data['password'], data['role'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'E-mail já cadastrado ou dados inválidos. ({e})'}), 400


@app.route('/api/users/<int:uid>', methods=['PUT'])
@roles_required('admin')
def api_update_user(uid):
    data = request.json or {}
    db.update_user(uid, data)
    return jsonify({'success': True})


@app.route('/api/users/<int:uid>', methods=['DELETE'])
@roles_required('admin')
def api_delete_user(uid):
    if uid == session['user_id']:
        return jsonify({'error': 'Não é possível remover o próprio usuário.'}), 400
    db.delete_user(uid)
    return jsonify({'success': True})


@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    return jsonify(db.get_dashboard_stats())


# ─── RUN ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True)

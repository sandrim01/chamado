from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from datetime import timedelta

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'unbug_secret_key')
app.permanent_session_lifetime = timedelta(days=7)  # 7 dias para sessão permanente

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:GlKbIvEYnJiCUlpLUSzufURZGSutRTTG@nozomi.proxy.rlwy.net:14131/railway')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    # Tabela de usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nome VARCHAR(100) NOT NULL,
            papel VARCHAR(20) NOT NULL CHECK (papel IN ('cliente', 'funcionario', 'admin'))
        )
    ''')
    # Tabela de chamados (com referência ao usuário)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chamados (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            descricao TEXT NOT NULL,
            solicitante VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'aberto',
            criado_em TIMESTAMP NOT NULL DEFAULT NOW(),
            usuario_id INTEGER REFERENCES users(id)
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

class User(UserMixin):
    def __init__(self, id, username, nome, papel):
        self.id = id
        self.username = username
        self.nome = nome
        self.papel = papel

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, nome, papel FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return User(*user)
    return None

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    # Exibe chamados conforme o papel do usuário
    if current_user.papel == 'admin':
        cur.execute('SELECT * FROM chamados ORDER BY criado_em DESC')
    elif current_user.papel == 'funcionario':
        cur.execute('SELECT * FROM chamados ORDER BY criado_em DESC')
    else:  # cliente
        cur.execute('SELECT * FROM chamados WHERE usuario_id = %s ORDER BY criado_em DESC', (current_user.id,))
    chamados = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', chamados=chamados)

@app.route('/abrir', methods=['POST'])
@login_required
def abrir_chamado():
    titulo = request.form['titulo']
    descricao = request.form['descricao']
    # O solicitante será o nome do usuário logado
    solicitante = current_user.nome
    usuario_id = current_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO chamados (titulo, descricao, solicitante, status, criado_em, usuario_id) VALUES (%s, %s, %s, %s, NOW(), %s)',
                (titulo, descricao, solicitante, 'aberto', usuario_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/fechar/<int:id>', methods=['POST'])
@login_required
def fechar_chamado(id):
    # Permite fechar apenas se for admin, funcionario ou dono do chamado
    conn = get_db_connection()
    cur = conn.cursor()
    if current_user.papel == 'cliente':
        cur.execute('SELECT usuario_id FROM chamados WHERE id = %s', (id,))
        dono = cur.fetchone()
        if not dono or dono[0] != current_user.id:
            flash('Acesso negado.', 'danger')
            cur.close()
            conn.close()
            return redirect(url_for('index'))
    cur.execute('UPDATE chamados SET status = %s WHERE id = %s', ('fechado', id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_chamado(id):
    # Só admin pode excluir chamados
    if current_user.papel != 'admin':
        flash('Apenas administradores podem excluir chamados.', 'danger')
        return redirect(url_for('index'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM chamados WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember_me' in request.form
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, password_hash, nome, papel FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], user[3], user[4])
            login_user(user_obj)
            if remember_me:
                session.permanent = True
            else:
                session.permanent = False
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    if current_user.papel != 'admin':
        flash('Apenas administradores podem acessar o cadastro de usuários.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        nome = request.form['nome']
        username = request.form['username']
        password = request.form['password']
        papel = request.form['papel']
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password_hash, nome, papel) VALUES (%s, %s, %s, %s)',
                        (username, password_hash, nome, papel))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash('Erro ao cadastrar usuário: ' + str(e), 'danger')
        finally:
            cur.close()
            conn.close()
    return render_template('cadastro.html')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0')

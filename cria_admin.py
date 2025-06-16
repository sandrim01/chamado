import psycopg2
from werkzeug.security import generate_password_hash
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:GlKbIvEYnJiCUlpLUSzufURZGSutRTTG@nozomi.proxy.rlwy.net:14131/railway')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

username = 'admin'
password = 'admin123'
nome = 'Administrador'
papel = 'admin'
password_hash = generate_password_hash(password)

try:
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        print('Usuário admin já existe.')
    else:
        cur.execute("INSERT INTO users (username, password_hash, nome, papel) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, nome, papel))
        conn.commit()
        print('Usuário admin criado com sucesso!')
finally:
    cur.close()
    conn.close()

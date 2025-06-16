import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:GlKbIvEYnJiCUlpLUSzufURZGSutRTTG@nozomi.proxy.rlwy.net:14131/railway')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE chamados ADD COLUMN IF NOT EXISTS usuario_id INTEGER REFERENCES users(id);")
    conn.commit()
    print('Coluna usuario_id adicionada com sucesso na tabela chamados!')
except Exception as e:
    print('Erro ao alterar tabela:', e)
finally:
    cur.close()
    conn.close()

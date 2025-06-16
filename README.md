# Sistema de Chamados Flask

Este projeto é um sistema de abertura e controle de chamados com backend e frontend em Flask, integrado ao PostgreSQL e pronto para deploy no Railway.

## Como rodar localmente

1. Crie o ambiente virtual e ative:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # Linux/Mac
   ```
2. Instale as dependências:
   ```
   pip install flask psycopg2-binary
   ```
3. Configure a variável de ambiente `DATABASE_URL` (opcional, já está no código):
   ```
   export DATABASE_URL=postgresql://postgres:GlKbIvEYnJiCUlpLUSzufURZGSutRTTG@nozomi.proxy.rlwy.net:14131/railway
   ```
4. Execute o app:
   ```
   python app.py
   ```
5. Acesse em http://localhost:5000

## Estrutura
- `app.py`: backend e frontend Flask
- `templates/`: HTML Jinja2
- `static/`: CSS

## Deploy Railway
- Configure a variável de ambiente `DATABASE_URL` no painel do Railway.
- Comando de start: `python app.py`

---


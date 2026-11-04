"""Configure only the project-owned MySQL instance on loopback port 3307."""
from pathlib import Path
import secrets
import pymysql

root=Path(__file__).resolve().parents[1]
if (root/'.env').exists():
    raise SystemExit('.env exists; refusing to replace credentials.')
app_password=secrets.token_urlsafe(32)
root_password=secrets.token_urlsafe(32)
with pymysql.connect(host='127.0.0.1',port=3307,user='root',password='',autocommit=True) as db:
    with db.cursor() as cur:
        cur.execute('CREATE DATABASE ecocollect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        cur.execute("CREATE USER 'ecocollect'@'127.0.0.1' IDENTIFIED BY %s",(app_password,))
        cur.execute("GRANT ALL PRIVILEGES ON ecocollect.* TO 'ecocollect'@'127.0.0.1'")
        cur.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s",(root_password,))
(root/'.env').write_text(f'DB_HOST=127.0.0.1\nDB_PORT=3307\nDB_USER=ecocollect\nDB_PASSWORD={app_password}\nDB_NAME=ecocollect\nJWT_SECRET={secrets.token_urlsafe(48)}\n')
(root/'.runtime/root-credentials.txt').write_text(f'Private local instance only; port 3307\nroot password: {root_password}\n')
print('Configured local MySQL and generated .env. Credentials are excluded from Git.')

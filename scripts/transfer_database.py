"""Copy EcoCollect to installed MySQL without changing the original database."""
from pathlib import Path
from datetime import datetime
import argparse
import getpass
import secrets
import sys

import pymysql
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
TABLES = ['users', 'ewaste_categories', 'recycling_centres',
          'collection_requests', 'request_items', 'status_history']
TARGET_DB = 'ecocollect_desktop'
TARGET_USER = 'ecocollect_desktop'


def snapshot():
    config = dotenv_values(ROOT / '.env')
    if config.get('DB_PORT') != '3307':
        raise RuntimeError('This copy is no longer configured for the original port 3307. No changes made.')
    connection = pymysql.connect(host=config['DB_HOST'], port=3307,
        user=config['DB_USER'], password=config['DB_PASSWORD'],
        database=config['DB_NAME'], charset='utf8mb4')
    data = {}
    dump = ['-- EcoCollect backup. Contains account hashes and application data.',
            '-- Import into an empty database only.', 'SET NAMES utf8mb4;']
    with connection:
        with connection.cursor() as cursor:
            cursor.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            cursor.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT')
            for table in TABLES:
                cursor.execute(f'SHOW CREATE TABLE `{table}`')
                ddl = cursor.fetchone()[1]
                cursor.execute(f'SELECT * FROM `{table}` ORDER BY id')
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                insert = f'INSERT INTO `{table}` (' + ','.join(f'`{c}`' for c in columns) + ') VALUES (' + ','.join(['%s'] * len(columns)) + ')'
                data[table] = (ddl, insert, rows)
                dump.append(ddl + ';')
                dump.extend(cursor.mogrify(insert, row) + ';' for row in rows)
            connection.rollback()
    folder = ROOT / 'backups'
    folder.mkdir(exist_ok=True)
    backup = folder / ('ecocollect-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.sql')
    backup.write_text('\n\n'.join(dump) + '\n', encoding='utf-8')
    print('Backup saved:', backup)
    for table, (_, _, rows) in data.items():
        print(f'  {table}: {len(rows)} rows')
    return config, data, backup


def prepare_launcher():
    launcher = ROOT / 'Start-EcoCollect.ps1'
    original = launcher.read_text(encoding='utf-8-sig')
    start = original.index('$mysqlExe =')
    end = original.index('$ready = $false', start)
    updated = original[:start] + '# Uses the installed MySQL84 service; no bundled server is launched.\n' + original[end:]
    # Independent app ports ensure an already-running original copy cannot hide
    # a failed migration or serve the old database during verification.
    updated = updated.replace('8000', '8001').replace('5173', '5174')
    old_probe = '& $pythonExe -c \'from backend.database import engine; from sqlalchemy import text; c=engine.connect(); c.execute(text("SELECT 1")); c.close()\' 2>$null'
    updated = updated.replace(old_probe, '& $pythonExe -m backend.check_db')
    vite = ROOT / 'frontend/vite.config.js'
    vite_updated = vite.read_text(encoding='utf-8').replace('8000', '8001').replace('5173', '5174')
    return launcher, updated, vite, vite_updated


def migrate():
    marker = ROOT / 'backups/TRANSFER_SUCCESS.txt'
    if marker.exists():
        print(marker.read_text(encoding='utf-8'))
        print('Transfer was already completed. No changes made.')
        return
    launcher, launcher_text, vite, vite_text = prepare_launcher()
    print('Keep both apps idle during this transfer. The original database will only be read.')
    password = getpass.getpass('Enter the NEW MySQL root password (port 3306; typing is hidden): ')
    target = pymysql.connect(host='127.0.0.1', port=3306, user='root',
        password=password, charset='utf8mb4', autocommit=True, connect_timeout=10)
    del password
    created_db = False
    created_user = False
    try:
        with target.cursor() as cursor:
            cursor.execute('SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s', (TARGET_DB,))
            if cursor.fetchone():
                raise RuntimeError('Target database ecocollect_desktop already exists. Refusing to overwrite it.')
            cursor.execute('SELECT User FROM mysql.user WHERE User=%s', (TARGET_USER,))
            if cursor.fetchone():
                raise RuntimeError('Target database user already exists. Refusing to change its credentials.')
            config, data, backup = snapshot()
            cursor.execute(f'CREATE DATABASE `{TARGET_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            created_db = True
            target.select_db(TARGET_DB)
            for ddl, _, _ in data.values():
                cursor.execute(ddl)
            target.begin()
            for _, insert, rows in data.values():
                if rows:
                    cursor.executemany(insert, rows)
            for table, (_, _, rows) in data.items():
                cursor.execute(f'SELECT * FROM `{table}` ORDER BY id')
                if cursor.fetchall() != rows:
                    raise RuntimeError(f'Verification failed for {table}; configuration will not be switched.')
            target.commit()
            app_password = secrets.token_urlsafe(32)
            cursor.execute("CREATE USER 'ecocollect_desktop'@'127.0.0.1' IDENTIFIED BY %s", (app_password,))
            created_user = True
            cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON `{TARGET_DB}`.* TO 'ecocollect_desktop'@'127.0.0.1'")
        with pymysql.connect(host='127.0.0.1', port=3306, user=TARGET_USER,
                password=app_password, database=TARGET_DB, charset='utf8mb4') as verify:
            with verify.cursor() as cursor:
                for table, (_, _, rows) in data.items():
                    cursor.execute(f'SELECT * FROM `{table}` ORDER BY id')
                    if cursor.fetchall() != rows:
                        raise RuntimeError(f'Post-commit verification failed for {table}.')
        folder = ROOT / 'backups'
        for file in [ROOT / '.env', launcher, vite]:
            (folder / (file.name + '.before-transfer')).write_bytes(file.read_bytes())
        new_env = f'DB_HOST=127.0.0.1\nDB_PORT=3306\nDB_USER={TARGET_USER}\nDB_PASSWORD={app_password}\nDB_NAME={TARGET_DB}\nJWT_SECRET={config["JWT_SECRET"]}\n'
        temporary = ROOT / '.env.transfer'
        temporary.write_text(new_env, encoding='utf-8')
        temporary.replace(ROOT / '.env')
        launcher.write_text(launcher_text, encoding='utf-8')
        vite.write_text(vite_text, encoding='utf-8')
        message = ('SUCCESS: All six tables and every row verified on installed MySQL port 3306.\n'
                   'The Downloads copy now uses database ecocollect_desktop.\n'
                   'Original project and database were not changed.\n'
                   'Run Start-EcoCollect.cmd, then open http://127.0.0.1:5174\n'
                   'Keep backups and the old MySQL folders until the application is checked.\n')
        marker.write_text(message, encoding='utf-8')
        print(message)
    except Exception:
        target.rollback()
        # Preserve any created database for diagnosis. Never overwrite or delete
        # an existing destination, source database or copied runtime directory.
        if created_db:
            print('Transfer did not finish. The new ecocollect_desktop database was retained for diagnosis.')
        raise
    finally:
        target.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--backup-only', action='store_true')
    args = parser.parse_args()
    try:
        if args.backup_only:
            snapshot()
        else:
            migrate()
    except Exception as error:
        # Never print connection arguments, credentials or source records.
        if isinstance(error, pymysql.err.OperationalError):
            print(f'MySQL error {error.args[0]}. Check the root password and that MySQL84 is running on port 3306.')
        else:
            print('Transfer stopped:', str(error))
        sys.exit(1)

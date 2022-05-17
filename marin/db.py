import sqlite3
import json


def _connect_db() -> sqlite3.Connection:
    return sqlite3.connect('./osuextra/data.sqlite')


db = _connect_db()
cur = db.cursor()
cur.execute(f'''CREATE TABLE IF NOT EXISTS users (
    uId INT,
    osuId INT
)''')
cur.execute(f'''CREATE TABLE IF NOT EXISTS servers (
    id INT,
    memes_channel INT
)''')


def account_exists(uId) -> bool:
    db = _connect_db()
    cur = db.cursor()
    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    data = cur.fetchone()
    cur.close()
    db.close()
    return data is not None


def create_account(uId, osuId) -> None:
    db = _connect_db()
    cur = db.cursor()

    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    data = cur.fetchone()
    if data is None:
        cur.execute(
            f'''INSERT INTO users VALUES({uId}, {osuId})''')
        db.commit()
    cur.close()
    db.close()


def get_account(uId) -> dict:
    db = _connect_db()
    cur = db.cursor()
    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    d = cur.fetchone()
    cur.close()
    db.close()
    return {'uId': d[0], 'osuId': d[1]}


def update_account(uId, *args) -> None:
    db = _connect_db()
    cur = db.cursor()
    for st in args:
        cur.execute(
            f'''UPDATE users SET {st[0]} = {st[1]} WHERE uId = {uId}''')
    db.commit()
    cur.close()
    db.close()

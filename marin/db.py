import sqlite3
import json


def _connect_db() -> sqlite3.Connection:
    return sqlite3.connect('./marin/data.sqlite')


db = _connect_db()
cur = db.cursor()
cur.execute(f'''CREATE TABLE IF NOT EXISTS users (
    uId INT,
    osuId INT
)''')
cur.execute(f'''CREATE TABLE IF NOT EXISTS servers (
    id INT,
    memes_channel INT,
    music_channel INT,
    radio_enabled INT,
    playlist_url TEXT,
    card_style TEXT
)''')


def create_server(id) -> None:
    db = _connect_db()
    cur = db.cursor()

    cur.execute('''SELECT * FROM servers WHERE id = ?''', (id))
    data = cur.fetchone()
    if data is None:
        cur.execute(
            '''INSERT INTO servers VALUES(?, 0, 0, 0, "NONE",'''''' "{}")''', (id))
        db.commit()
    cur.close()
    db.close()


def delete_server(id) -> None:
    db = _connect_db()
    cur = db.cursor()

    cur.execute('''SELECT * FROM servers WHERE id = ?''', (id))
    data = cur.fetchone()
    if data is not None:
        cur.execute(
            '''DELETE FROM servers WHERE id = ?''', (id))
        db.commit()
    cur.close()
    db.close()


def get_server(id) -> dict:
    db = _connect_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM servers WHERE id = ?''', (id))
    d = cur.fetchone()
    cur.close()
    db.close()
    return {'id': d[0], 'memes_channel': d[1], 'music_channel': d[2], 'radio_enabled': d[3], 'playlist_url': d[4]}


def get_servers() -> list[int]:
    db = _connect_db()
    cur = db.cursor()
    cur.execute('''SELECT id FROM servers''')
    d = cur.fetchall()
    cur.close()
    db.close()
    return list(map(lambda x: x[0], d))


def update_server(id, *args) -> None:
    db = _connect_db()
    cur = db.cursor()
    for st in args:
        if type(st[1]) == int:
            val = st[1]
        elif type(st[1]) == dict:
            val = json.dumps(st[1])
        elif type(st[1]) == str:
            val = f'"{st[1]}"'
        else:
            continue
        cur.execute(
            '''UPDATE servers SET ? = ? WHERE id = ?''', (st[0], val, id))
    db.commit()
    cur.close()
    db.close()


def account_exists(uId) -> bool:
    db = _connect_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM users WHERE uId = ?''', (id))
    data = cur.fetchone()
    cur.close()
    db.close()
    return data is not None


def create_account(uId, osuId) -> None:
    db = _connect_db()
    cur = db.cursor()

    cur.execute('''SELECT * FROM users WHERE uId = ?''', (uId))
    data = cur.fetchone()
    if data is None:
        cur.execute(
            '''INSERT INTO users VALUES(?, ?)''', ({uId}, {osuId}))
        db.commit()
    cur.close()
    db.close()


def get_account(uId) -> dict:
    db = _connect_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM users WHERE uId = ?''', (uId))
    d = cur.fetchone()
    cur.close()
    db.close()
    return {'uId': d[0], 'osuId': d[1]}


def update_account(uId, *args) -> None:
    db = _connect_db()
    cur = db.cursor()
    for st in args:
        cur.execute(
            '''UPDATE users SET ? = ? WHERE uId = ?''', (st[0], st[1], uId))
    db.commit()
    cur.close()
    db.close()

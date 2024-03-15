import os
import asyncio
import sqlite3
import aiosqlite
from ..resource.RESOURCE_PATH import MAIN_PATH

DB_PATH = os.path.expanduser(MAIN_PATH / 'pokemon.db')


class SCORE_DB:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_SCORE
                          (UID             TEXT   NOT NULL,
                           SCORE           INT    NOT NULL,
                           SHENGWANG       INT    NOT NULL,
                           PRIMARY KEY(UID));"""
            )
        except:
            raise Exception('创建表发生错误')

    async def _new_score(self, uid):
        try:
            connection = await aiosqlite.connect(DB_PATH)
            await connection.execute(f"INSERT OR REPLACE INTO POKEMON_SCORE (UID,SCORE,SHENGWANG) VALUES ('{uid}',0,0)")
            await connection.commit()
            await connection.close()
        except:
            raise Exception('更新表发生错误')
    
    async def delete_score(self, uid):
        try:
            connection = await aiosqlite.connect(DB_PATH)
            await connection.execute(f"DELETE FROM POKEMON_SCORE WHERE UID='{uid}'")
            await connection.commit()
            await connection.close()
        except:
            raise Exception('更新表发生错误')
    
    async def change_score(self, newuid, olduid):
        connection = await aiosqlite.connect(DB_PATH)
        await connection.execute(f"UPDATE POKEMON_SCORE SET UID='{newuid}' WHERE UID='{olduid}'")
        await connection.commit()
        await connection.close()
    
    async def get_score(self, uid):
        try:
            connection = await aiosqlite.connect(DB_PATH)
            cursor = await connection.execute(f"SELECT SCORE FROM POKEMON_SCORE WHERE UID='{uid}'")
            r = await cursor.fetchall()
            await connection.close()
            if r:
                return r[0][0]
            else:
                self._new_score(uid)
                return 0
        except:
            raise Exception('查找表发生错误')

    async def update_score(self, uid, score):
        now_score = await self.get_score(uid) + score
        try:
            connection = await aiosqlite.connect(DB_PATH)
            await connection.execute(f"UPDATE POKEMON_SCORE SET SCORE = {now_score} WHERE UID='{uid}'")
            await connection.commit()
            await connection.close()
        except:
            raise Exception('更新表发生错误')
    
    async def get_shengwang(self, uid):
        try:
            connection = await aiosqlite.connect(DB_PATH)
            cursor = await connection.execute(f"SELECT SHENGWANG FROM POKEMON_SCORE WHERE UID='{uid}'")
            r = await cursor.fetchall()
            await connection.close()
            if r:
                return r[0][0]
            else:
                await self._new_score(uid)
                return 0
        except:
            raise Exception('查找表发生错误')

    async def update_shengwang(self, uid, shengwang):
        now_shengwang = await self.get_shengwang(uid) + shengwang
        try:
            connection = await aiosqlite.connect(DB_PATH)
            await connection.execute(f"UPDATE POKEMON_SCORE SET SHENGWANG = {now_shengwang} WHERE UID='{uid}'")
            await connection.commit()
            await connection.close()
        except:
            raise Exception('更新表发生错误')

class RecordDAO:
    def __init__(self):
        self.db_path = DB_PATH
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                'CREATE TABLE IF NOT EXISTS limiter'
                '(key TEXT NOT NULL, num INT NOT NULL, date INT, PRIMARY KEY(key))'
            )

    def exist_check(self, key):
        try:
            key = str(key)
            with self.connect() as conn:
                conn.execute(
                    'INSERT INTO limiter (key,num,date) VALUES (?, 0,-1)',
                    (key,),
                )
            return
        except:
            return

    def get_num(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                'SELECT num FROM limiter WHERE key=? ', (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def clear_key(self, key):
        key = str(key)
        self.exist_check(key)
        with self.connect() as conn:
            conn.execute(
                'UPDATE limiter SET num=0 WHERE key=?',
                (key,),
            )

    def increment_key(self, key, num):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute(
                'UPDATE limiter SET num=num+? WHERE key=?',
                (
                    num,
                    key,
                ),
            )

    def get_date(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                'SELECT date FROM limiter WHERE key=? ', (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def set_date(self, date, key):
        print(date)
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute(
                'UPDATE limiter SET date=? WHERE key=?',
                (
                    date,
                    key,
                ),
            )

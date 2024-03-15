import os
import asyncio
import sqlite3
import aiosqlite
from ..resource.RESOURCE_PATH import MAIN_PATH

DB_PATH = os.path.expanduser(MAIN_PATH / 'pokemon.db')


class GAME_DB:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(DB_PATH)
    
    def _create_table(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_GAME
                          (UID             TEXT   NOT NULL,
                           TYPE            TEXT   NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID, TYPE));"""
            )
        except:
            raise Exception('创建表发生错误')

    async def _new_game_num(self, uid, gametype):
        try:
            connection = await aiosqlite.connect(DB_PATH)
            await connection.execute(f"INSERT OR REPLACE INTO POKEMON_GAME (UID,TYPE,NUM) VALUES ('{uid}','{gametype}',0)")
            await connection.commit()
            await connection.close()
        except:
            raise Exception('更新表发生错误')

    async def get_game_num(self, uid, gametype):
        try:
            connection = await aiosqlite.connect(DB_PATH)
            cursor = await connection.execute(f"SELECT NUM FROM POKEMON_GAME WHERE UID='{uid}' AND TYPE='{gametype}'")
            rows = await cursor.fetchall()
            await connection.close()
            if rows:
                return rows[0][0]
            else:
                await self._new_game_num(uid, gametype)
                return 0
        except:
            raise Exception('查找表发生错误')

    async def update_game_num(self, uid, gametype, num=1):
        game_num = await self.get_game_num(uid, gametype) + num
        try:
            connection = await aiosqlite.connect(DB_PATH)
            await connection.execute(f"UPDATE POKEMON_GAME SET NUM = {game_num} WHERE UID='{uid}' AND TYPE='{gametype}'")
            await connection.commit()
            await connection.close()
            return game_num
        except:
            raise Exception('更新表发生错误')

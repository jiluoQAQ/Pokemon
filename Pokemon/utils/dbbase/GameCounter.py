import asyncio
import random
import os
import sqlite3
import math
import json
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
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_GAME
                          (UID             TEXT   NOT NULL,
                           TYPE            TEXT   NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID, TYPE));''')
        except:
            raise Exception('创建表发生错误')
    
    def _new_game_num(self, uid, gametype):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_GAME (UID,TYPE,NUM) VALUES (?,?,?)", (uid, gametype, 0)
                )  
        except:
            raise Exception('更新表发生错误')
    
    def get_game_num(self, uid, gametype):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM POKEMON_GAME WHERE UID={uid} AND TYPE='{gametype}'").fetchall()
                if r:
                    return r[0][0]
                else:
                    self._new_game_num(uid, gametype)
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def update_game_num(self,uid,gametype,num = 1):
        game_num = self.get_game_num(uid,gametype) + num
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE POKEMON_GAME SET NUM = ? WHERE UID=? AND TYPE=?",
                    (game_num, uid, gametype),
                )
                return game_num
        except:
            raise Exception('更新表发生错误')
import asyncio
import random
import os
import sqlite3
import math
import json
from ..utils.resource.RESOURCE_PATH import MAIN_PATH
DB_PATH = os.path.expanduser(MAIN_PATH / 'pokemon.db')
    
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
                "CREATE TABLE IF NOT EXISTS limiter"
                "(key TEXT NOT NULL, num INT NOT NULL, date INT, PRIMARY KEY(key))"
            )
    
    def exist_check(self, key):
        try:
            key = str(key)
            with self.connect() as conn:
                conn.execute("INSERT INTO limiter (key,num,date) VALUES (?, 0,-1)", (key,), )
            return
        except:
            return

    def get_num(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT num FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def clear_key(self, key):
        key = str(key)
        self.exist_check(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=0 WHERE key=?", (key,), )
        return

    def increment_key(self, key, num):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=num+? WHERE key=?", (num, key,))
        return

    def get_date(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT date FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def set_date(self, date, key):
        print(date)
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET date=? WHERE key=?", (date, key,), )
        return

class PokeCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()
        self._create_table_map()
    
    def _connect(self):
        return sqlite3.connect(DB_PATH)
    
    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_TABLE
                          (UID             INT    NOT NULL,
                           BIANHAO         INT    NOT NULL,
                           LEVEL           INT    NOT NULL,
                           EXP             INT    NOT NULL,
                           GT_HP           INT   NOT NULL,
                           GT_ATK          INT   NOT NULL,
                           GT_DEF          INT   NOT NULL,
                           GT_STK          INT   NOT NULL,
                           GT_SEF          INT   NOT NULL,
                           GT_SPD          INT   NOT NULL,
                           NL_HP           INT   NOT NULL,
                           NL_ATK          INT   NOT NULL,
                           NL_DEF          INT   NOT NULL,
                           NL_STK          INT   NOT NULL,
                           NL_SEF          INT   NOT NULL,
                           NL_SPD          INT   NOT NULL,
                           XINGGE          TEXT   NOT NULL,
                           JINENG          TEXT   NOT NULL,
                           PRIMARY KEY(UID,BIANHAO));''')
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_map(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_MAP
                          (UID             INT    NOT NULL,
                           HUIZHANG        INT    NOT NULL,
                           MAP_NAME        TEXT   NOT NULL,
                           PRIMARY KEY(UID));''')
        except:
            raise Exception('创建表发生错误')
    
    def _get_map_now(self,uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT HUIZHANG,MAP_NAME FROM POKEMON_MAP WHERE UID={uid}").fetchall()
                if r:
                    return r[0]
                else:
                    return [0,'']
        except:
            raise Exception('查找表发生错误')
    
    def _add_map_now(self,uid,map_name):
        mapinfo = self._get_map_now(uid)
        huizhang = mapinfo[0]
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_MAP (UID,HUIZHANG,MAP_NAME) VALUES (?,?,?)", (uid, huizhang, map_name)
                )  
        except:
            raise Exception('更新表发生错误')
    
    def _add_huizhang_now(self,uid,huizhang):
        mapinfo = self._get_map_now(uid)
        map_name = mapinfo[1]
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_MAP (UID,HUIZHANG,MAP_NAME) VALUES (?,?,?)", (uid, huizhang, map_name)
                )  
        except:
            raise Exception('更新表发生错误')
    
    def _add_pokemon_info(self, uid, bianhao, pokemon_info):
        level, gt_hp, gt_atk, gt_def, gt_stk, gt_sdf, gt_spd, nl_hp, nl_atk, nl_def, nl_stk,nl_sef, nl_spd, xingge, jineng = pokemon_info
        #print(pokemon_info)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_TABLE (UID,BIANHAO,LEVEL,EXP,GT_HP,GT_ATK,GT_DEF,GT_STK,GT_SEF,GT_SPD,NL_HP,NL_ATK,NL_DEF,NL_STK,NL_SEF,NL_SPD,XINGGE,JINENG) \
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (uid, bianhao, level, 0, gt_hp, gt_atk, gt_def, gt_stk, gt_sdf, gt_spd, nl_hp, nl_atk, nl_def, nl_stk,nl_sef, nl_spd, xingge, jineng)
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _add_pokemon_level(self, uid, bianhao, level, exp):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_TABLE (UID,BIANHAO,LEVEL, EXP) \
                                VALUES (?,?,?,?)", (uid, bianhao, level, exp)
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _add_pokemon_nuli(self, uid, bianhao, nl_hp, nl_atk, nl_def, nl_stk,nl_sef, nl_spd):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_TABLE (UID,BIANHAO,NL_HP,NL_ATK,NL_DEF,NL_STK,NL_SEF,NL_SPD) \
                                VALUES (?,?,?,?,?,?,?,?)", (uid, bianhao, nl_hp, nl_atk, nl_def, nl_stk,nl_sef, nl_spd)
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _add_pokemon_jineng(self, uid, bianhao, jineng):
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE POKEMON_TABLE SET JINENG = ? WHERE UID=? AND BIANHAO=?",
                    (jineng, uid, bianhao),
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _get_pokemon_info(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT LEVEL,GT_HP,GT_ATK,GT_DEF,GT_STK,GT_SEF,GT_SPD,NL_HP,NL_ATK,NL_DEF,NL_STK,NL_SEF,NL_SPD,XINGGE,JINENG FROM POKEMON_TABLE WHERE UID={uid} AND BIANHAO={bianhao}").fetchall()
                if r:
                    return r[0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_level(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT LEVEL,EXP FROM POKEMON_TABLE WHERE UID={uid} AND BIANHAO={bianhao}").fetchall()
                if r:
                    return r[0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_list(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT BIANHAO,LEVEL FROM POKEMON_TABLE WHERE UID={uid} ORDER BY LEVEL desc LIMIT 20").fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
            
    def _delete_poke_info(self, uid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM POKEMON_TABLE  WHERE UID=?",
                (uid),
            )
            
    def _delete_poke_bianhao(self, uid, bianhao):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM POKEMON_TABLE  WHERE UID=? AND BIANHAO=?",
                (uid, bianhao),
            )
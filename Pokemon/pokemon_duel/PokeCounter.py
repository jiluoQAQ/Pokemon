import asyncio
import random
import os
import sqlite3
import math
import json
from ..utils.resource.RESOURCE_PATH import MAIN_PATH
DB_PATH = os.path.expanduser(MAIN_PATH / 'pokemon.db')

class PokeCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()
        self._create_table_map()
        self._create_table_group()
        self._create_table_egg()
    
    def _connect(self):
        return sqlite3.connect(DB_PATH)
    
    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_TABLE
                          (UID             TEXT   NOT NULL,
                           BIANHAO         INT    NOT NULL,
                           LEVEL           INT    NOT NULL,
                           EXP             INT    NOT NULL,
                           GT_HP           INT    NOT NULL,
                           GT_ATK          INT    NOT NULL,
                           GT_DEF          INT    NOT NULL,
                           GT_STK          INT    NOT NULL,
                           GT_SEF          INT    NOT NULL,
                           GT_SPD          INT    NOT NULL,
                           NL_HP           INT    NOT NULL,
                           NL_ATK          INT    NOT NULL,
                           NL_DEF          INT    NOT NULL,
                           NL_STK          INT    NOT NULL,
                           NL_SEF          INT    NOT NULL,
                           NL_SPD          INT    NOT NULL,
                           XINGGE          TEXT   NOT NULL,
                           JINENG          TEXT   NOT NULL,
                           PRIMARY KEY(UID,BIANHAO));''')
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_map(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_MAP
                          (UID             TEXT   NOT NULL,
                           HUIZHANG        TEXT   NOT NULL,
                           MAP_NAME        TEXT   NOT NULL,
                           NICKNAME        TEXT   NOT NULL,
                           PRIMARY KEY(UID));''')
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_group(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_TEAM
                          (UID             TEXT   NOT NULL,
                           TEAM            TEXT   NOT NULL,
                           PRIMARY KEY(UID));''')
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_egg(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS POKEMON_EGG
                          (UID             TEXT   NOT NULL,
                           BIANHAO         INT    NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID, BIANHAO));''')
        except:
            raise Exception('创建表发生错误')
    
    def _add_pokemon_group(self, uid, pokemon_list):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_TEAM (UID,TEAM) VALUES (?,?)", (uid, pokemon_list)
                )  
        except:
            raise Exception('更新表发生错误')
    
    def get_pokemon_group(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT TEAM FROM POKEMON_TEAM WHERE UID='{uid}'").fetchall()
                if r:
                    return r[0][0]
                else:
                    return ''
        except:
            raise Exception('查找表发生错误')
    
    def delete_pokemon_group(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_TEAM WHERE UID='{uid}'"
            ).fetchall()
    
    def _add_pokemon_egg(self, uid, bianhao, use_num):
        eggnum = self.get_pokemon_egg(uid, bianhao) + use_num
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_EGG (UID,BIANHAO,NUM) VALUES (?,?,?)", (uid, bianhao, eggnum)
                )  
        except:
            raise Exception('更新表发生错误')
    
    def get_pokemon_egg(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM POKEMON_EGG WHERE UID='{uid}' AND BIANHAO={bianhao}").fetchall()
                if r:
                    return r[0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def delete_pokemon_egg(self, uid):
        
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_EGG WHERE UID='{uid}'"
            ).fetchall()
    
    def _get_map_now(self,uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT HUIZHANG,MAP_NAME,NICKNAME FROM POKEMON_MAP WHERE UID='{uid}'").fetchall()
                if r:
                    return r[0]
                else:
                    return [0,'']
        except:
            raise Exception('查找表发生错误')
    
    def _get_map_info_nickname(self,nickname):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT HUIZHANG,MAP_NAME,UID FROM POKEMON_MAP WHERE NICKNAME='{nickname}'").fetchall()
                if r:
                    return r[0]
                else:
                    return [0,'',0]
        except:
            raise Exception('查找表发生错误')
    
    def _add_map_now(self,uid,map_name):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET MAP_NAME='{map_name}' WHERE UID='{uid}'"
                )  
        except:
            raise Exception('更新表发生错误')
    
    def _new_map_info(self,uid,map_name,nickname):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO POKEMON_MAP (UID,HUIZHANG,MAP_NAME,NICKNAME) VALUES (?,?,?,?)", (uid, 0, map_name,nickname)
                )  
        except:
            raise Exception('更新表发生错误')
    
    def _update_map_name(self,uid,nickname):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET NICKNAME='{nickname}' WHERE UID='{uid}'"
                )  
        except:
            raise Exception('更新表发生错误')
    
    def delete_pokemon_map(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_MAP  WHERE UID='{uid}'"
            ).fetchall()
    
    def _add_huizhang_now(self,uid,huizhang):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET HUIZHANG='{huizhang}' WHERE UID='{uid}'"
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
                    f"UPDATE POKEMON_TABLE SET LEVEL=?, EXP=? WHERE UID='{uid}' AND BIANHAO=?",(level, exp, bianhao)
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _add_pokemon_nuli(self, uid, bianhao, nl_hp, nl_atk, nl_def, nl_stk,nl_sef, nl_spd):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_TABLE SET NL_HP=?,NL_ATK=?,NL_DEF=?,NL_STK=?,NL_SEF=?,NL_SPD=? WHERE UID='{uid}' AND BIANHAO=?",
                    (nl_hp, nl_atk, nl_def, nl_stk,nl_sef, nl_spd, bianhao)
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _add_pokemon_jineng(self, uid, bianhao, jineng):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_TABLE SET JINENG='{jineng}' WHERE UID='{uid}' AND BIANHAO={bianhao}"
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _add_pokemon_id(self, uid, bianhao, changeid):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_TABLE SET BIANHAO='{changeid}' WHERE UID='{uid}' AND BIANHAO={bianhao}"
                )
                  
        except:
            raise Exception('更新表发生错误')
            
    def _get_pokemon_info(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT LEVEL,GT_HP,GT_ATK,GT_DEF,GT_STK,GT_SEF,GT_SPD,NL_HP,NL_ATK,NL_DEF,NL_STK,NL_SEF,NL_SPD,XINGGE,JINENG,EXP FROM POKEMON_TABLE WHERE UID='{uid}' AND BIANHAO={bianhao}").fetchall()
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
                    f"SELECT LEVEL,EXP FROM POKEMON_TABLE WHERE UID='{uid}' AND BIANHAO={bianhao}").fetchall()
                if r:
                    return r[0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_num(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT COUNT(BIANHAO) AS NUM FROM POKEMON_TABLE WHERE UID='{uid}'").fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_list(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT BIANHAO,LEVEL FROM POKEMON_TABLE WHERE UID='{uid}' ORDER BY LEVEL desc LIMIT 20").fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
            
    def _delete_poke_info(self, uid):
        with self._connect() as conn:
            conn.execute(f"DELETE FROM POKEMON_TABLE WHERE UID='{uid}'").fetchall()
            
    def _delete_poke_bianhao(self, uid, bianhao):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_TABLE WHERE UID='{uid}' AND BIANHAO={bianhao}"
            ).fetchall()
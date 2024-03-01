import os
import sqlite3
from ..resource.RESOURCE_PATH import MAIN_PATH

DB_PATH = os.path.expanduser(MAIN_PATH / 'pokemon.db')


class PokeCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()
        self._create_table_map()
        self._create_table_group()
        self._create_table_egg()
        self._create_table_prop()
        self._create_table_star()
        self._create_table_starrush()
        self._create_table_map_refresh()
        self._create_table_refresh_send()
        self._create_table_exchange()
        self._create_table_technical()
        self._create_table_boss_fight()
        self._create_table_chongsheng_num()

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_TABLE
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
                           PRIMARY KEY(UID,BIANHAO));"""
            )
        except:
            raise Exception('创建表发生错误')

    def _create_table_map(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_MAP
                          (UID             TEXT   NOT NULL,
                           HUIZHANG        TEXT   NOT NULL,
                           MAP_NAME        TEXT   NOT NULL,
                           NICKNAME        TEXT   NOT NULL,
                           PRIMARY KEY(UID));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_group(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_TEAM
                          (UID             TEXT   NOT NULL,
                           TEAM            TEXT   NOT NULL,
                           PRIMARY KEY(UID));"""
            )
        except:
            raise Exception('创建表发生错误')

    def _create_table_egg(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_EGG
                          (UID             TEXT   NOT NULL,
                           BIANHAO         INT    NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID, BIANHAO));"""
            )
        except:
            raise Exception('创建表发生错误')

    def _create_table_prop(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_PROP
                          (UID             TEXT   NOT NULL,
                           PROP            TEXT   NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID, PROP));"""
            )
        except:
            raise Exception('创建表发生错误')

    def _create_table_star(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_STAR
                          (UID             TEXT   NOT NULL,
                           BIANHAO         INT    NOT NULL,
                           TYPE            INT    NOT NULL,
                           PRIMARY KEY(UID, BIANHAO));"""
            )
        except:
            raise Exception('创建表发生错误')

    def _create_table_starrush(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS POKEMON_STARRUSH
                          (UID             TEXT   NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_map_refresh(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS MAP_REFRESH
                          (DIQU             TEXT   NOT NULL,
                           DIDIAN           TEXT   NOT NULL,
                           POKEMON          TEXT   NOT NULL,
                           PRIMARY KEY(DIQU));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_refresh_send(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS REFRESH_SEND
                          (GROUPID          TEXT   NOT NULL,
                           BOTID            TEXT   NOT NULL,
                           PRIMARY KEY(GROUPID));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_exchange(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS PROP_EXCHANGE
                          (EXCHANGEID       TEXT   NOT NULL,
                           PROPTYPE         TEXT   NOT NULL,
                           PROPNAME         TEXT   NOT NULL,
                           NUM              TEXT   NOT NULL,
                           UID              TEXT   NOT NULL,
                           SCORE            INT    NOT NULL,
                           UPTIME           INT    NOT NULL,
                           PRIMARY KEY(EXCHANGEID));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_technical(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS PROP_TECHNICAL
                          (UID             TEXT   NOT NULL,
                           PROP            TEXT   NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID, PROP));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_boss_fight(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS BOSS_FIGHT
                          (UID             TEXT   NOT NULL,
                           SHANGHAI        INT   NOT NULL,
                           TIME            INT   NOT NULL,
                           PRIMARY KEY(UID,TIME));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    def _create_table_chongsheng_num(self):
        try:
            self._connect().execute(
                """CREATE TABLE IF NOT EXISTS CHONGSHENG
                          (UID             TEXT   NOT NULL,
                           BIANHAO        INT    NOT NULL,
                           NUM             INT    NOT NULL,
                           PRIMARY KEY(UID,BIANHAO));"""
            )
        except:
            raise Exception('创建表发生错误')
    
    async def _new_chongsheng_num(self, uid, bianhao):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO CHONGSHENG (UID,BIANHAO,NUM) VALUES (?,?,?)',
                    (uid, bianhao, 0),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def get_chongsheng_num(self,uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM CHONGSHENG WHERE UID='{uid}' AND BIANHAO = {bianhao}"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    await self._new_chongsheng_num(uid, bianhao)
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def update_chongsheng(self,uid,bianhao,num):
        chongsheng_num = await self.get_chongsheng_num(uid, bianhao)
        now_num = int(chongsheng_num) + num
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE CHONGSHENG SET NUM={now_num} WHERE UID='{uid}' AND BIANHAO = {bianhao}"
                )

        except:
            raise Exception('更新表发生错误')
    
    async def get_boss_shanghai(self,uid,week):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT SHANGHAI FROM BOSS_FIGHT WHERE UID='{uid}' AND TIME = {week}"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def _new_boss_shanghai(self, uid, shanghai, week):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO BOSS_FIGHT (UID,SHANGHAI,TIME) VALUES (?,?,?)',
                    (uid, shanghai, week),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def get_boss_shanghai_list(self,week):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT UID,SHANGHAI FROM BOSS_FIGHT WHERE TIME = {week} ORDER BY SHANGHAI DESC LIMIT 0,50"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def get_game_user_list(self):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT UID FROM POKEMON_MAP WHERE HUIZHANG>0"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def get_pokemon_technical_list(self, uid, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT PROP,NUM FROM PROP_TECHNICAL WHERE UID='{uid}' AND NUM>0 ORDER BY NUM DESC LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    num = conn.execute(
                        f"SELECT COUNT(PROP) AS PROPNUM FROM PROP_TECHNICAL WHERE UID='{uid}' AND NUM>0"
                    ).fetchall()
                    return num[0][0],r
                else:
                    return 0,0
        except:
            raise Exception('查找表发生错误')

    async def _new_pokemon_technical(self, uid, propname):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO PROP_TECHNICAL (UID,PROP,NUM) VALUES (?,?,?)',
                    (uid, propname, 0),
                )
        except:
            raise Exception('更新表发生错误')

    async def _get_pokemon_technical(self, uid, propname):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM PROP_TECHNICAL WHERE UID='{uid}' AND PROP='{propname}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    await self._new_pokemon_technical(uid, propname)
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def _add_pokemon_technical(self, uid, propname, num):
        now_num = await self._get_pokemon_technical(uid, propname) + int(num)
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO PROP_TECHNICAL (UID,PROP,NUM) VALUES (?,?,?)',
                    (uid, propname, now_num),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def delete_technical_uid(self,uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM PROP_TECHNICAL WHERE UID='{uid}'"
            ).fetchall()
    
    async def change_technical_uid(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE PROP_TECHNICAL SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    async def new_exchange(self,exchangeid,proptype,propname,num,uid,score,uptime):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO PROP_EXCHANGE (EXCHANGEID,PROPTYPE,PROPNAME,NUM,UID,SCORE,UPTIME) VALUES (?,?,?,?,?,?,?)',
                    (exchangeid,proptype,propname,num,uid,score,uptime),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def update_exchange(self,exchangeid,num):
        exchange_num = await self._get_exchange_num(exchangeid)
        now_num = int(exchange_num) + num
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE PROP_EXCHANGE SET NUM={now_num} WHERE EXCHANGEID='{exchangeid}'"
                )

        except:
            raise Exception('更新表发生错误')
    
    async def _get_exchange_num(self,exchangeid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM PROP_EXCHANGE WHERE EXCHANGEID='{exchangeid}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def _get_exchange_info(self,exchangeid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT PROPTYPE,PROPNAME,NUM,UID,SCORE FROM PROP_EXCHANGE WHERE EXCHANGEID='{exchangeid}'"
                ).fetchall()
                if r:
                    return r[0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def delete_exchange(self,exchangeid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM PROP_EXCHANGE WHERE EXCHANGEID='{exchangeid}'"
            ).fetchall()
    
    async def delete_exchange_uid(self,uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM PROP_EXCHANGE WHERE UID='{uid}'"
            ).fetchall()
    
    async def change_exchange_uid(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE PROP_EXCHANGE SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    async def get_exchange_list(self, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT EXCHANGEID,PROPTYPE,PROPNAME,NUM,SCORE FROM PROP_EXCHANGE WHERE NUM>0 ORDER BY PROPNAME ASC,SCORE ASC LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    num = conn.execute(
                        f"SELECT COUNT(EXCHANGEID) AS EXCHANGENUM FROM PROP_EXCHANGE WHERE NUM>0"
                    ).fetchall()
                    return num[0][0],r
                else:
                    return 0,0
        except:
            raise Exception('查找表发生错误')
    
    async def get_exchange_list_my(self, uid, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT EXCHANGEID,PROPTYPE,PROPNAME,NUM,SCORE FROM PROP_EXCHANGE WHERE NUM>0 AND UID='{uid}' ORDER BY PROPNAME ASC,SCORE ASC LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    num = conn.execute(
                        f"SELECT COUNT(EXCHANGEID) AS EXCHANGENUM FROM PROP_EXCHANGE WHERE NUM>0 AND UID='{uid}'"
                    ).fetchall()
                    return num[0][0],r
                else:
                    return 0,0
        except:
            raise Exception('查找表发生错误')
    
    async def get_exchange_list_sx_type(self, proptype, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT EXCHANGEID,PROPTYPE,PROPNAME,NUM,SCORE FROM PROP_EXCHANGE WHERE NUM>0 AND PROPTYPE='{proptype}' ORDER BY PROPNAME ASC,SCORE ASC LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    num = conn.execute(
                        f"SELECT COUNT(EXCHANGEID) AS EXCHANGENUM FROM PROP_EXCHANGE WHERE NUM>0 AND PROPTYPE='{proptype}'"
                    ).fetchall()
                    return num[0][0],r
                else:
                    return 0,0
        except:
            raise Exception('查找表发生错误')
    
    async def get_exchange_list_sx_name(self, proptype, propname, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT EXCHANGEID,PROPTYPE,PROPNAME,NUM,SCORE FROM PROP_EXCHANGE WHERE NUM>0 AND PROPTYPE='{proptype}' AND PROPNAME='{propname}' ORDER BY PROPNAME ASC,SCORE ASC LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    num = conn.execute(
                        f"SELECT COUNT(EXCHANGEID) AS EXCHANGENUM FROM PROP_EXCHANGE WHERE NUM>0 AND PROPTYPE='{proptype}' AND PROPNAME='{propname}'"
                    ).fetchall()
                    return num[0][0],r
                else:
                    return 0,0
        except:
            raise Exception('查找表发生错误')
    
    async def get_exchange_list_time(self, findtime):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT EXCHANGEID,PROPTYPE,PROPNAME,NUM,UID FROM PROP_EXCHANGE WHERE UPTIME<{findtime}"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def update_refresh_send(self,groupid,botid):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO REFRESH_SEND (GROUPID,BOTID) VALUES (?,?)',
                    (groupid, botid),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def get_refresh_send_list(self):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT GROUPID,BOTID FROM REFRESH_SEND"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def delete_refresh_send(self,groupid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM REFRESH_SEND WHERE GROUPID='{groupid}'"
            ).fetchall()
    
    async def update_map_refresh(self,diqu,didian,pokemon):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO MAP_REFRESH (DIQU,DIDIAN,POKEMON) VALUES (?,?,?)',
                    (diqu, didian, pokemon),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def get_map_refresh(self,diqu,didian):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT POKEMON FROM MAP_REFRESH WHERE DIQU='{diqu}' AND DIDIAN='{didian}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def get_map_refresh_list(self):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT DIQU,DIDIAN,POKEMON FROM MAP_REFRESH"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    async def update_pokemon_star(self, uid, bianhao, startype=0):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_STAR (UID,BIANHAO,TYPE) VALUES (?,?,?)',
                    (uid, bianhao, startype),
                )
        except:
            raise Exception('更新表发生错误')

    async def get_pokemon_star(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT TYPE FROM POKEMON_STAR WHERE UID='{uid}' AND BIANHAO={bianhao}"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def _delete_poke_star(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_STAR WHERE UID='{uid}'"
            ).fetchall()
    
    async def _change_poke_star(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_STAR SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    async def _delete_poke_starrush_uid(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_STARRUSH WHERE UID='{uid}'"
            ).fetchall()
    
    async def _change_poke_starrush_uid(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_STARRUSH SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    async def _delete_poke_star_bianhao(self, uid, bianhao):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_STAR WHERE UID='{uid}' AND BIANHAO={bianhao}"
            ).fetchall()

    async def get_pokemon_starrush(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM POKEMON_STARRUSH WHERE UID='{uid}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    await self.new_pokemon_starrush(uid)
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def update_pokemon_starrush(self, uid, num):
        rushnum = await self.get_pokemon_starrush(uid) + num
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_STARRUSH (UID,NUM) VALUES (?,?)',
                    (uid, rushnum),
                )
        except:
            raise Exception('更新表发生错误')

    async def new_pokemon_starrush(self, uid):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_STARRUSH (UID,NUM) VALUES (?,?)',
                    (uid, 0),
                )
        except:
            raise Exception('更新表发生错误')

    async def get_pokemon_prop_list(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT PROP,NUM FROM POKEMON_PROP WHERE UID='{uid}' AND NUM>0 ORDER BY NUM"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def _new_pokemon_prop(self, uid, propname):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_PROP (UID,PROP,NUM) VALUES (?,?,?)',
                    (uid, propname, 0),
                )
        except:
            raise Exception('更新表发生错误')

    async def _get_pokemon_prop(self, uid, propname):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM POKEMON_PROP WHERE UID='{uid}' AND PROP='{propname}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    await self._new_pokemon_prop(uid, propname)
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def _add_pokemon_prop(self, uid, propname, num):
        now_num = await self._get_pokemon_prop(uid, propname) + int(num)
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_PROP (UID,PROP,NUM) VALUES (?,?,?)',
                    (uid, propname, now_num),
                )
        except:
            raise Exception('更新表发生错误')
    
    async def delete_pokemon_prop(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_PROP WHERE UID='{uid}'"
            ).fetchall()
    
    async def change_pokemon_prop(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_PROP SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    async def _add_pokemon_group(self, uid, pokemon_list):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_TEAM (UID,TEAM) VALUES (?,?)',
                    (uid, pokemon_list),
                )
        except:
            raise Exception('更新表发生错误')

    async def get_pokemon_group(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT TEAM FROM POKEMON_TEAM WHERE UID='{uid}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return ''
        except:
            raise Exception('查找表发生错误')

    async def delete_pokemon_group(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_TEAM WHERE UID='{uid}'"
            ).fetchall()
    
    async def change_pokemon_group(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_TEAM SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    async def _add_pokemon_egg(self, uid, bianhao, use_num):
        eggnum = int(await self.get_pokemon_egg(uid, bianhao)) + int(use_num)
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_EGG (UID,BIANHAO,NUM) VALUES (?,?,?)',
                    (uid, bianhao, eggnum),
                )
        except:
            raise Exception('更新表发生错误')

    async def delete_pokemon_egg_bianhao(self, uid, bianhao):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_EGG SET NUM=0 WHERE UID='{uid}' AND BIANHAO={bianhao}"
                )
        except:
            raise Exception('更新表发生错误')
    
    async def update_pokemon_egg_bianhao(self, uid, bianhao, egg_num):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_EGG SET NUM={egg_num} WHERE UID='{uid}' AND BIANHAO={bianhao}"
                )
        except:
            raise Exception('更新表发生错误')
    
    async def get_pokemon_egg(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT NUM FROM POKEMON_EGG WHERE UID='{uid}' AND BIANHAO={bianhao}"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def get_pokemon_egg_num(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT COUNT(BIANHAO) AS EGGNUM FROM POKEMON_EGG WHERE UID='{uid}' AND NUM>0"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def get_pokemon_egg_list(self, uid, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT BIANHAO,NUM FROM POKEMON_EGG WHERE UID='{uid}' AND NUM>0 ORDER BY NUM desc,BIANHAO ASC LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    async def delete_pokemon_egg(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_EGG WHERE UID='{uid}'"
            ).fetchall()
    
    async def change_pokemon_egg(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_EGG SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    def _get_map_now(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT HUIZHANG,MAP_NAME,NICKNAME FROM POKEMON_MAP WHERE UID='{uid}'"
                ).fetchall()
                if r:
                    return r[0]
                else:
                    return [0, '', 0]
        except:
            raise Exception('查找表发生错误')

    def _get_map_info_nickname(self, nickname):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT HUIZHANG,MAP_NAME,UID FROM POKEMON_MAP WHERE NICKNAME='{nickname}'"
                ).fetchall()
                if r:
                    return r[0]
                else:
                    return [0, '', 0]
        except:
            raise Exception('查找表发生错误')

    def _add_map_now(self, uid, map_name):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET MAP_NAME='{map_name}' WHERE UID='{uid}'"
                )
        except:
            raise Exception('更新表发生错误')

    def _new_map_info(self, uid, map_name, nickname):
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_MAP (UID,HUIZHANG,MAP_NAME,NICKNAME) VALUES (?,?,?,?)',
                    (uid, 0, map_name, nickname),
                )
        except:
            raise Exception('更新表发生错误')

    def _update_map_name(self, uid, nickname):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET NICKNAME='{nickname}' WHERE UID='{uid}'"
                )
        except:
            raise Exception('更新表发生错误')

    def _update_map_huizhang(self, uid, huizhang):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET HUIZHANG={huizhang} WHERE UID='{uid}'"
                )
        except:
            raise Exception('更新表发生错误')

    def delete_pokemon_map(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_MAP  WHERE UID='{uid}'"
            ).fetchall()
    
    def change_pokemon_map(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_MAP SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    def _add_huizhang_now(self, uid, huizhang):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_MAP SET HUIZHANG='{huizhang}' WHERE UID='{uid}'"
                )
        except:
            raise Exception('更新表发生错误')

    def _add_pokemon_info(self, uid, bianhao, pokemon_info, exp=0):
        (
            level,
            gt_hp,
            gt_atk,
            gt_def,
            gt_stk,
            gt_sdf,
            gt_spd,
            nl_hp,
            nl_atk,
            nl_def,
            nl_stk,
            nl_sef,
            nl_spd,
            xingge,
            jineng,
        ) = pokemon_info
        # print(pokemon_info)
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO POKEMON_TABLE (UID,BIANHAO,LEVEL,EXP,GT_HP,GT_ATK,GT_DEF,GT_STK,GT_SEF,GT_SPD,NL_HP,NL_ATK,NL_DEF,NL_STK,NL_SEF,NL_SPD,XINGGE,JINENG) \
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        uid,
                        bianhao,
                        level,
                        exp,
                        gt_hp,
                        gt_atk,
                        gt_def,
                        gt_stk,
                        gt_sdf,
                        gt_spd,
                        nl_hp,
                        nl_atk,
                        nl_def,
                        nl_stk,
                        nl_sef,
                        nl_spd,
                        xingge,
                        jineng,
                    ),
                )

        except:
            raise Exception('更新表发生错误')

    def _add_pokemon_level(self, uid, bianhao, level, exp):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_TABLE SET LEVEL=?, EXP=? WHERE UID='{uid}' AND BIANHAO=?",
                    (level, exp, bianhao),
                )

        except:
            raise Exception('更新表发生错误')

    def _add_pokemon_nuli(
        self, uid, bianhao, nl_hp, nl_atk, nl_def, nl_stk, nl_sef, nl_spd
    ):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_TABLE SET NL_HP=?,NL_ATK=?,NL_DEF=?,NL_STK=?,NL_SEF=?,NL_SPD=? WHERE UID='{uid}' AND BIANHAO=?",
                    (nl_hp, nl_atk, nl_def, nl_stk, nl_sef, nl_spd, bianhao),
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

    def _add_pokemon_xingge(self, uid, bianhao, xingge):
        try:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE POKEMON_TABLE SET XINGGE='{xingge}' WHERE UID='{uid}' AND BIANHAO={bianhao}"
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
                    f"SELECT LEVEL,GT_HP,GT_ATK,GT_DEF,GT_STK,GT_SEF,GT_SPD,NL_HP,NL_ATK,NL_DEF,NL_STK,NL_SEF,NL_SPD,XINGGE,JINENG,EXP FROM POKEMON_TABLE WHERE UID='{uid}' AND BIANHAO={bianhao}"
                ).fetchall()
                if r:
                    return r[0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_info_list(self, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT UID,(GT_HP+GT_ATK+GT_DEF+GT_SEF+GT_SPD+GT_STK) AS GT_Z FROM POKEMON_TABLE WHERE BIANHAO={bianhao} ORDER BY (GT_HP+GT_ATK+GT_DEF+GT_SEF+GT_SPD+GT_STK) DESC LIMIT 0,50"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_info_list_pm(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT BIANHAO,(GT_HP+GT_ATK+GT_DEF+GT_SEF+GT_SPD+GT_STK) AS GT_Z FROM POKEMON_TABLE WHERE UID='{uid}' ORDER BY (GT_HP+GT_ATK+GT_DEF+GT_SEF+GT_SPD+GT_STK) DESC LIMIT 0,50"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')
    
    def _get_pokemon_level(self, uid, bianhao):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT LEVEL,EXP FROM POKEMON_TABLE WHERE UID='{uid}' AND BIANHAO={bianhao}"
                ).fetchall()
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
                    f"SELECT COUNT(BIANHAO) AS NUM FROM POKEMON_TABLE WHERE UID='{uid}'"
                ).fetchall()
                if r:
                    return r[0][0]
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    def _get_pokemon_list(self, uid, page=0):
        num = 30
        startnum = num * page
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT BIANHAO,LEVEL FROM POKEMON_TABLE WHERE UID='{uid}' ORDER BY LEVEL desc,BIANHAO asc LIMIT {startnum},{num}"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    def _get_my_pokemon(self, uid):
        try:
            with self._connect() as conn:
                r = conn.execute(
                    f"SELECT BIANHAO FROM POKEMON_TABLE WHERE UID='{uid}' ORDER BY LEVEL desc"
                ).fetchall()
                if r:
                    return r
                else:
                    return 0
        except:
            raise Exception('查找表发生错误')

    def _delete_poke_info(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_TABLE WHERE UID='{uid}'"
            ).fetchall()
    
    def _change_poke_info(self, newuid, olduid):
        with self._connect() as conn:
            conn.execute(
                f"UPDATE POKEMON_TABLE SET UID='{newuid}' WHERE UID='{olduid}'"
            ).fetchall()
    
    def _delete_poke_bianhao(self, uid, bianhao):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM POKEMON_TABLE WHERE UID='{uid}' AND BIANHAO={bianhao}"
            ).fetchall()

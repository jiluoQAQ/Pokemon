import asyncio
import os
import random
import math
import textwrap
import json
from PIL import Image, ImageDraw
import copy
from async_timeout import timeout
from .pokemon import *
from .pokeconfg import *
from gsuid_core.message_models import Button
from .until import *
from pathlib import Path
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.segment import MessageSegment
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH, CHAR_ICON_S_PATH
from ..utils.dbbase.ScoreCounter import SCORE_DB
from ..utils.dbbase.PokeCounter import PokeCounter
from ..utils.convert import DailyAmountLimiter
from .data_source import make_jineng_use

class FIGHT_PIPEI:
    def __init__(self):
        self.pokelist = {}
        self.pokeinfo = {}
        self.zhuangtai = {}
        self.changdi = {}
        self.jineng_use = {}
        self.now_jineng = {}
        self.fight_flag = {}
        self.fight_mes = {}
    
    async def new_fight_flag(self,fightid):
        self.fight_flag[fightid] = 0
    
    async def update_fight_flag(self,fightid,fightflag):
        self.fight_flag[fightid] = fightflag
    
    async def get_fight_flag(self,fightid):
        fightflag = self.fight_flag[fightid] if self.fight_flag.get(fightid) is not None else 0
        return fightflag
    
    async def new_fight_changdi(self,fightid,changdi):
        self.changdi[fightid] = changdi
    
    async def new_fight_info(self,fightid,uid,pokemonlist,pokemoninfo,pokezhuangtai,usejineng):
        self.pokelist[fightid] = {}
        self.pokeinfo[fightid] = {}
        self.zhuangtai[fightid] = {}
        self.jineng_use[fightid] = {}
        self.now_jineng[fightid] = {}
        self.pokelist[fightid][uid] = pokemonlist
        self.pokeinfo[fightid][uid] = pokemoninfo
        self.zhuangtai[fightid][uid] = pokezhuangtai
        self.jineng_use[fightid][uid] = usejineng
        self.now_jineng[fightid][uid] = ''
    
    async def get_fight_info(self,fightid,uid):
        pokemoninfo = []
        pokezhuangtai = []
        usejineng = []
        if self.pokeinfo.get(fightid) is not None:
            pokemoninfo = self.pokeinfo[fightid][uid] if self.pokeinfo[fightid].get(uid) is not None else []
        if self.zhuangtai.get(fightid) is not None:
            pokezhuangtai = self.zhuangtai[fightid][uid] if self.zhuangtai[fightid].get(uid) is not None else []
        if self.jineng_use.get(fightid) is not None:
            usejineng = self.jineng_use[fightid][uid] if self.jineng_use[fightid].get(uid) is not None else []
        return pokemoninfo,pokezhuangtai,usejineng
    
    async def get_changdi_info(self,fightid):
        changdiinfo = self.changdi[fightid] if self.changdi.get(fightid) is not None else []
        return changdiinfo
    
    async def update_jineng(self,fightid,uid,jinengname):
        self.now_jineng[fightid][uid] = jinengname
        self.jineng_use[fightid][uid].append(jinengname)
    
    async def get_jineng_use(self,fightid,uid):
        if self.jineng_use.get(fightid) is not None:
            usejineng = self.jineng_use[fightid][uid] if self.jineng_use[fightid].get(uid) is not None else []
        return usejineng
    
    async def get_jineng_name(self,fightid,uid):
        if self.now_jineng.get(fightid) is not None:
            jinengname = self.now_jineng[fightid][uid] if self.now_jineng[fightid].get(uid) is not None else ''
        return jinengname
    
FIGHT = FIGHT_PIPEI()

async def fight_pipei_now(fightid,myuid,diuid,myname,diname):
    

async def pokemon_fight_pipei(bot,ev,myuid,diuid,myname,diname,mypokemon_info,dipokemon_info,fightid):
    shul = 1
    fight_flag = 0
    last_jineng1 = ''
    last_jineng2 = ''
    button_user_input_my = []
    button_user_input_my.append(myuid)
    jineng_use = await FIGHT.get_jineng_use(fightid,myuid)
    while fight_flag == 0:
        mesg = ''
        jieshu = 0
        myjinenglist = re.split(',', mypokemon_info[14])
        dijinenglist = re.split(',', dipokemon_info[14])
        myjinengbuttons = []
        dijinengbuttons = []
        my_ues_jineng_list = []
        di_ues_jineng_list = []
        for myjn in myjinenglist:
            jn_use_num_my = jineng_use.count(myjn)
            jineng_info1 = JINENG_LIST[myjn]
            myjn_but = f'{myjn}({int(jineng_info1[4])-int(jn_use_num_my)}/{int(jineng_info1[4])})'
            myjn_name = myjn
            if int(jn_use_num_my) < int(jineng_info1[4]):
                my_ues_jineng_list.append(myjn)
                myjinengbuttons.append(Button(myjn_but, myjn_name, myjn_but, action=1, permisson=0, specify_user_ids=button_user_input_my))

            
        if len(my_ues_jineng_list) == 0:
            my_ues_jineng_list.append('挣扎')
            myjinengbuttons = [Button('挣扎', '挣扎', '挣扎', action=1, permisson=0, specify_user_ids=button_user_input_my)]

        jineng1_use = 0
        runmynum = 0
        try:
            async with timeout(FIGHT_TIME):
                while jineng1_use == 0:
                    if runmynum == 0:
                        myresp = await bot.receive_resp(
                            f'{myname}请在{FIGHT_TIME}秒内选择一个技能使用!',
                            myjinengbuttons,
                            unsuported_platform=True
                        )
                        if myresp is not None:
                            mys = myresp.text
                            uidmy = myresp.user_id
                            if str(uidmy) == str(myuid):
                                if mys in my_ues_jineng_list:
                                    jineng1 = mys
                                    await bot.send(f'{myname}已选择完成，等待对手确认中')
                                    jineng1_use = 1
                        runmynum = 1
                    else:
                        myresp = await bot.receive_mutiply_resp()
                        if myresp is not None:
                            mys = myresp.text
                            uidmy = myresp.user_id
                            if str(uidmy) == str(myuid):
                                if mys in my_ues_jineng_list:
                                    jineng1 = mys
                                    await bot.send(f'{myname}已选择完成，等待对手确认中')
                                    jineng1_use = 1
        except asyncio.TimeoutError:
            myinfo = await FIGHT.get_fight_info(fightid,myuid)
            diinfo = await FIGHT.get_fight_info(fightid,diuid)
            changdi = await FIGHT.get_changdi_info(fightid)
            jineng1 = await now_use_jineng(
                myinfo, diinfo, my_ues_jineng_list, dijinenglist, changdi
            )
        await FIGHT.update_jineng(fightid,myuid,jineng1)
        jineng2_use = 0
        try:
            async with timeout(FIGHT_TIME):
                while jineng2_use == 0:
                    await asyncio.sleep(.5)
                    jineng2 = await FIGHT.get_jineng_name(fightid,diuid)
                    if jineng2 != '':
                        jineng2_use = 1
        except asyncio.TimeoutError:
            myinfo = await FIGHT.get_fight_info(fightid,myuid)
            diinfo = await FIGHT.get_fight_info(fightid,diuid)
            changdi = await FIGHT.get_changdi_info(fightid)
            jineng2 = await now_use_jineng(
                diinfo, myinfo, dijinenglist, my_ues_jineng_list, changdi
            )
            await FIGHT.update_jineng(fightid,diuid,jineng2)
        
        fightflag = await FIGHT.get_fight_flag(fightid)
        if fightflag == 0:
            fightflag = 1
            await FIGHT.update_fight_flag(fightid,1)
            await fight_pipei_now(fightid,myuid,diuid,myname,diname)
        
        while fightflag == 1:
            await asyncio.sleep(.5)
            fightflag = await FIGHT.get_fight_flag(fightid)
        
        if fightflag == 2:
            fightmes = await FIGHT.get_fight_mes(fightid)
            await bot.send(fightmes)
        
        myinfo = await FIGHT.get_fight_info(fightid,myuid)
        if myinfo[17] <= 0:
            return myinfo
        
async def fight_pk_pipei(
    bot, ev, myuid, diuid, mypokelist, dipokelist, myname, fightid, level=0
):
    zhuangtai = [['无', 0], ['无', 0]]
    changdi = [['无天气', 99], ['', 0]]
    changci = 1
    myinfo = []
    jineng_use = []
    mesg = []
    max_my_num = len(mypokelist)
    max_di_num = len(dipokelist)
    bg_num = 1
    await FIGHT.new_fight_changdi(fightid, changdi)
    while len(mypokelist) > 0 and len(dipokelist) > 0:
        mes = f'第{changci}场\n'
        mes += f'{myname}剩余精灵{len(mypokelist)}只\n{diname}剩余精灵{len(dipokelist)}只\n'
        changci += 1
        if len(myinfo) == 0:
            bianhao1 = mypokelist[0]
            mypokemon_info = await get_pokeon_info(myuid, bianhao1)
            myinfo = await new_pokemon_info(bianhao1, mypokemon_info, level)
            mystartype = await POKE.get_pokemon_star(myuid, bianhao1)
            myinfo[0] = f'{starlist[mystartype]}{myinfo[0]}'
            jineng_use1 = []
            await FIGHT.new_fight_info(fightid,myuid,myinfo,mypokelist,zhuangtai,jineng_use)
            
        await bot.send(mes)

        mes = f'{myname}派出了精灵\n{starlist[mystartype]}{POKEMON_LIST[bianhao1][0]} Lv.{myinfo[2]}'
        img = CHAR_ICON_PATH / f'{CHARA_NAME[bianhao1][0]}.png'
        if mystartype > 0:
            img = CHAR_ICON_S_PATH / f'{CHARA_NAME[bianhao1][0]}_s.png'
        img = await convert_img(img)
        await bot.send(
            [MessageSegment.text(mes), MessageSegment.image(img)]
        )
        bianhao2 = dipokelist[0]
        distartype = await POKE.get_pokemon_star(diuid, dipokelist[0])
        dipokemon_info = await get_pokeon_info(diuid, dipokelist[0])
        mes = f'{diname}派出了精灵\n{starlist[distartype]}{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}'
        img = CHAR_ICON_PATH / f'{CHARA_NAME[bianhao2][0]}.png'
        if distartype > 0:
            img = CHAR_ICON_S_PATH / f'{CHARA_NAME[bianhao2][0]}_s.png'
        img = await convert_img(img)
        await bot.send(
            [MessageSegment.text(mes), MessageSegment.image(img)]
        )
        
        myinfo = await pokemon_fight_pipei(bot,ev,myuid,diuid,myname,mypokemon_info,dipokemon_info,fightid)

        if myinfo[17] <= 0:
            jiesuan_msg = (
                f'{diname}的{POKEMON_LIST[bianhao2][0]}战胜了{myname}的{POKEMON_LIST[bianhao1][0]}'
            )
            myinfo = []
            myzhuangtai = [['无', 0], ['无', 0]]
            mypokelist.remove(bianhao1)
            jineng_use = []
        else:
            jiesuan_msg = (
                f'{myname}的{POKEMON_LIST[bianhao1][0]}战胜了{diname}的{POKEMON_LIST[bianhao2][0]}'
            )
        await bot.send(jiesuan_msg)
    return mypokelist, dipokelist
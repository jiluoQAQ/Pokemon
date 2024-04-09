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
    
    async def new_fight(self,fightid,changdi):
        self.pokelist[fightid] = {}
        self.pokeinfo[fightid] = {}
        self.zhuangtai[fightid] = {}
        self.jineng_use[fightid] = {}
        self.now_jineng[fightid] = {}
        self.fight_flag[fightid] = {}
        self.fight_mes[fightid] = ''
        self.changdi[fightid] = changdi
        
    async def new_fight_mes(self,fightid):
        self.fight_mes[fightid] = ''
    
    async def update_fight_mes(self,fightid,mesg):
        self.fight_mes[fightid] = mesg
    
    async def get_fight_mes(self,fightid):
        fightmes = self.fight_mes[fightid] if self.fight_mes.get(fightid) is not None else ''
        return fightmes
    
    async def new_fight_flag(self,fightid,uid):
        self.fight_flag[fightid][uid] = 0
    
    async def update_fight_flag(self,fightid,uid,fightflag):
        self.fight_flag[fightid][uid] = fightflag
    
    async def get_fight_flag(self,fightid,uid):
        fightflag = self.fight_flag[fightid][uid] if self.fight_flag[fightid].get(uid) is not None else 0
        return fightflag
    
    async def new_fight_changdi(self,fightid,changdi):
        self.changdi[fightid] = changdi
    
    async def new_fight_info(self,fightid,uid,pokemonlist,pokemoninfo,pokezhuangtai):
        self.pokelist[fightid][uid] = pokemonlist
        self.pokeinfo[fightid][uid] = pokemoninfo
        self.zhuangtai[fightid][uid] = pokezhuangtai
        self.jineng_use[fightid][uid] = []
        self.now_jineng[fightid][uid] = ''
    
    async def update_fight_info(self,fightid,uid,pokemoninfo,pokezhuangtai):
        self.pokeinfo[fightid][uid] = pokemoninfo
        self.zhuangtai[fightid][uid] = pokezhuangtai
    
    async def get_fight_info(self,fightid,uid):
        pokemoninfo = self.pokeinfo[fightid][uid] if self.pokeinfo[fightid].get(uid) is not None else []
        pokezhuangtai = self.zhuangtai[fightid][uid] if self.zhuangtai[fightid].get(uid) is not None else []
        usejineng = self.now_jineng[fightid][uid] if self.now_jineng[fightid].get(uid) is not None else []
        return pokemoninfo,pokezhuangtai,usejineng
    
    async def get_changdi_info(self,fightid):
        changdiinfo = self.changdi[fightid] if self.changdi.get(fightid) is not None else []
        return changdiinfo
    
    async def update_changdi_info(self,fightid,changdiinfo):
        self.changdi[fightid] = changdiinfo
    
    async def update_jineng(self,fightid,uid,jinengname):
        self.now_jineng[fightid][uid] = jinengname
        self.jineng_use[fightid][uid].append(jinengname)
    
    async def get_jineng_use(self,fightid,uid):
        usejineng = self.jineng_use[fightid][uid]
        return usejineng
    
    async def get_pokelist(self,fightid,uid):
        pokemonlist = self.pokelist[fightid][uid] if self.pokelist[fightid].get(uid) is not None else []
        return pokemonlist
        
    async def get_jineng_name(self,fightid,uid):
        if self.now_jineng.get(fightid) is not None:
            jinengname = self.now_jineng[fightid][uid] if self.now_jineng[fightid].get(uid) is not None else ''
        return jinengname
    
FIGHT = FIGHT_PIPEI()

async def fight_pipei_now(fightid,uid1,uid2,name1,name2):
    fightflag1 = await FIGHT.get_fight_flag(fightid,uid1)
    fightflag2 = await FIGHT.get_fight_flag(fightid,uid2)
    mesg = ''
    if fightflag1 == 1 and fightflag2 == 1:
        jieshu = 0
        jineng_use1 = await FIGHT.get_jineng_use(fightid,uid1)
        jineng_use2 = await FIGHT.get_jineng_use(fightid,uid2)
        if len(jineng_use1) > 1:
            last_jineng1 = jineng_use1[len(jineng_use1) - 2]
        else:
            jineng_use1 = ''
        if len(jineng_use1) > 1:
            last_jineng2 = jineng_use1[len(jineng_use1) - 2]
        else:
            last_jineng2 = ''
        myinfo,myzhuangtai,jineng1 = await FIGHT.get_fight_info(fightid,uid1)
        diinfo,dizhuangtai,jineng2 = await FIGHT.get_fight_info(fightid,uid2)
        changdi = await FIGHT.get_changdi_info(fightid)
        mysd = await get_nowshuxing(myinfo[8], myinfo[13], '速度', myinfo[1], changdi[0][0])
        if myzhuangtai[0][0] == '麻痹' and int(myzhuangtai[0][1]) > 0:
            mysd = int(mysd * 0.5)
        disd = await get_nowshuxing(diinfo[8], diinfo[13], '速度', diinfo[1], changdi[0][0])
        if dizhuangtai[0][0] == '麻痹' and int(dizhuangtai[0][1]) > 0:
            disd = int(mysd * 0.5)
        # 先手判断
        myxianshou = 1
        if jineng1 in xianzhi or jineng2 in xianzhi:
            if jineng1 in xianzhi and jineng2 in xianzhi:
                if mysd < disd:
                    myxianshou = 0
            else:
                if jineng1 in xianzhi:
                    myxianshou = 1
                if jineng2 in xianzhi:
                    myxianshou = 0
        elif jineng1 in youxian or jineng2 in youxian:
            if jineng1 in youxian and jineng2 in youxian:
                if mysd < disd:
                    myxianshou = 0
            else:
                if jineng1 in youxian:
                    myxianshou = 1
                if jineng2 in youxian:
                    myxianshou = 0
        else:
            if mysd < disd:
                myxianshou = 0
        
        # 双方出手
        my_mesg = ''
        di_mesg = ''
        if myxianshou == 1:
            if jieshu == 0:
                mychushou = await get_chushou_flag(myzhuangtai)
                if mychushou == 1:
                    if jineng1 in lianxu_shibai and jineng1 == last_jineng1:
                        my_mesg = my_mesg + f'\n{myinfo[0]}使用了技能{jineng1}，技能发动失败'
                    else:
                        # 我方攻击
                        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = await make_jineng_use(jineng1, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi)
                        my_mesg = my_mesg + mes

                else:
                    if (
                        myzhuangtai[0][0] == '混乱'
                        and int(myzhuangtai[0][1]) > 0
                    ):
                        (
                            mes,
                            myinfo,
                            diinfo,
                            myzhuangtai,
                            dizhuangtai,
                            changdi,
                        ) = await get_hunluan_sh(
                            myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
                        )
                        my_mesg = my_mesg + '\n' + mes
                    else:
                        my_mesg = (
                            my_mesg
                            + f'\n{myinfo[0]}{myzhuangtai[0][0]}中，技能发动失败'
                        )
                if myinfo[17] <= 0 or diinfo[17] <= 0:
                    jieshu = 1
                mesg = mesg + my_mesg

            if jieshu == 0:
                dichushou = await get_chushou_flag(dizhuangtai)
                if dichushou == 1:
                    if jineng2 in lianxu_shibai and jineng2 == last_jineng2:
                        di_mesg = di_mesg + f'\n{diinfo[0]}使用了技能{jineng2}，技能发动失败'
                    else:
                        # 敌方攻击
                        mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = await make_jineng_use(jineng2, diinfo, myinfo, dizhuangtai, myzhuangtai, changdi)
                        di_mesg = di_mesg + mes
                else:
                    if (
                        dizhuangtai[0][0] == '混乱'
                        and int(dizhuangtai[0][1]) > 0
                    ):
                        (
                            mes,
                            diinfo,
                            myinfo,
                            dizhuangtai,
                            myzhuangtai,
                            changdi,
                        ) = await get_hunluan_sh(
                            diinfo, myinfo, dizhuangtai, myzhuangtai, changdi
                        )
                        di_mesg = di_mesg + '\n' + mes
                    else:
                        di_mesg = (
                            di_mesg
                            + f'\n{diinfo[0]}{dizhuangtai[0][0]}中，技能发动失败'
                        )
                if myinfo[17] <= 0 or diinfo[17] <= 0:
                    jieshu = 1
                mesg = mesg + '\n' + di_mesg

        else:
            if jieshu == 0:
                dichushou = await get_chushou_flag(dizhuangtai)
                if dichushou == 1:
                    if jineng2 in lianxu_shibai and jineng2 == last_jineng2:
                        di_mesg = di_mesg + f'\n{diinfo[0]}使用了技能{jineng2}，技能发动失败'
                    else:
                        # 敌方攻击
                        mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = await make_jineng_use(jineng2, diinfo, myinfo, dizhuangtai, myzhuangtai, changdi)
                        di_mesg = di_mesg + mes
                else:
                    if (
                        dizhuangtai[0][0] == '混乱'
                        and int(dizhuangtai[0][1]) > 0
                    ):
                        (
                            mes,
                            diinfo,
                            myinfo,
                            dizhuangtai,
                            myzhuangtai,
                            changdi,
                        ) = await get_hunluan_sh(
                            diinfo, myinfo, dizhuangtai, myzhuangtai, changdi
                        )
                        di_mesg = di_mesg + '\n' + mes
                    else:
                        di_mesg = (
                            di_mesg
                            + f'\n{diinfo[0]}{dizhuangtai[0][0]}中，技能发动失败'
                        )
                if myinfo[17] <= 0 or diinfo[17] <= 0:
                    jieshu = 1
                mesg = mesg + di_mesg

            if jieshu == 0:
                mychushou = await get_chushou_flag(myzhuangtai)
                if mychushou == 1:
                    if jineng1 in lianxu_shibai and jineng1 == last_jineng1:
                        my_mesg = my_mesg + f'\n{myinfo[0]}使用了技能{jineng1}，技能发动失败'
                    else:
                        # 我方攻击
                        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = await make_jineng_use(jineng1, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi)
                        my_mesg = my_mesg + mes
                else:
                    if (
                        myzhuangtai[0][0] == '混乱'
                        and int(myzhuangtai[0][1]) > 0
                    ):
                        (
                            mes,
                            myinfo,
                            diinfo,
                            myzhuangtai,
                            dizhuangtai,
                            changdi,
                        ) = await get_hunluan_sh(
                            myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
                        )
                        my_mesg = my_mesg + '\n' + mes
                    else:
                        my_mesg = (
                            my_mesg
                            + f'\n{myinfo[0]}{myzhuangtai[0][0]}中，技能发动失败'
                        )
                if myinfo[17] <= 0 or diinfo[17] <= 0:
                    jieshu = 1
                mesg = mesg + '\n' + my_mesg
        
        # 回合结束天气与状态伤害计算
        changdi_mesg = ''
        if (
            myzhuangtai[0][0] in kouxuelist
            and int(myzhuangtai[0][1]) > 0
            and myinfo[17] > 0
        ):
            (
                mes,
                myinfo,
                diinfo,
                myzhuangtai,
                dizhuangtai,
                changdi,
            ) = await get_zhuangtai_sh(
                myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
            )
            changdi_mesg = changdi_mesg + mes + '\n'
        if myinfo[17] <= 0 or diinfo[17] <= 0:
            jieshu = 1

        if (
            dizhuangtai[0][0] in kouxuelist
            and int(dizhuangtai[0][1]) > 0
            and diinfo[17] > 0
        ):
            (
                mes,
                diinfo,
                myinfo,
                dizhuangtai,
                myzhuangtai,
                changdi,
            ) = await get_zhuangtai_sh(
                diinfo, myinfo, dizhuangtai, myzhuangtai, changdi
            )
            changdi_mesg = changdi_mesg + mes + '\n'
        if myinfo[17] <= 0 or diinfo[17] <= 0:
            jieshu = 1

        if (
            changdi[0][0] in tq_kouxuelist
            and int(changdi[0][1]) > 0
            and jieshu == 0
        ):
            (
                mes,
                myinfo,
                diinfo,
                myzhuangtai,
                dizhuangtai,
                changdi,
            ) = await get_tianqi_sh(
                myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
            )
            changdi_mesg = changdi_mesg + mes + '\n'
        if myinfo[17] <= 0 or diinfo[17] <= 0:
            jieshu = 1

        if (
            myzhuangtai[0][0] in hh_yichanglist
            and int(myzhuangtai[0][1]) > 0
            and myinfo[17] > 0
        ):
            myshengyuyc = int(myzhuangtai[0][1]) - 1
            if myshengyuyc == 0:
                changdi_mesg = (
                    changdi_mesg
                    + f'{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n'
                )
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0
            else:
                myzhuangtai[0][1] = myshengyuyc

        if (
            dizhuangtai[0][0] in hh_yichanglist
            and int(dizhuangtai[0][1]) > 0
            and diinfo[17] > 0
        ):
            dishengyuyc = int(dizhuangtai[0][1]) - 1
            if dishengyuyc == 0:
                changdi_mesg = (
                    changdi_mesg
                    + f'{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n'
                )
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0
            else:
                dizhuangtai[0][1] = dishengyuyc

        if (
            myzhuangtai[1][0] in hh_yichanglist
            and int(myzhuangtai[1][1]) > 0
            and myinfo[17] > 0
        ):
            myshengyuyc = int(myzhuangtai[1][1]) - 1
            if myshengyuyc == 0:
                changdi_mesg = (
                    changdi_mesg
                    + f'{myinfo[0]}的{myzhuangtai[1][0]}状态解除了\n'
                )
                myzhuangtai[1][0] = '无'
                myzhuangtai[1][1] = 0
            else:
                myzhuangtai[1][1] = myshengyuyc

        if (
            dizhuangtai[1][0] in hh_yichanglist
            and int(dizhuangtai[1][1]) > 0
            and diinfo[17] > 0
        ):
            dishengyuyc = int(dizhuangtai[1][1]) - 1
            if dishengyuyc == 0:
                changdi_mesg = (
                    changdi_mesg
                    + f'{diinfo[0]}的{dizhuangtai[1][0]}状态解除了\n'
                )
                dizhuangtai[1][0] = '无'
                dizhuangtai[1][1] = 0
            else:
                dizhuangtai[1][1] = dishengyuyc

        if (
            myzhuangtai[0][0] in jiechulist
            and int(myzhuangtai[0][1]) > 0
            and myinfo[17] > 0
        ):
            suiji = int(math.floor(random.uniform(0, 100)))
            if suiji <= 20:
                changdi_mesg = (
                    changdi_mesg
                    + f'{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n'
                )
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0

        if (
            dizhuangtai[0][0] in jiechulist
            and int(dizhuangtai[0][1]) > 0
            and diinfo[17] > 0
        ):
            suiji = int(math.floor(random.uniform(0, 100)))
            if suiji <= 20:
                changdi_mesg = (
                    changdi_mesg
                    + f'{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n'
                )
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0

        if int(changdi[0][1]) > 0 and changdi[0][0] != '无天气':
            shengyutianqi = int(changdi[0][1]) - 1
            if shengyutianqi == 0:
                changdi_mesg = (
                    changdi_mesg + f'{changdi[0][0]}停止了，天气影响消失了\n'
                )
                changdi[0][0] = '无天气'
                changdi[0][1] = 99
            else:
                changdi[0][1] = shengyutianqi
                changdi_mesg = changdi_mesg + f'{changdi[0][0]}持续中\n'
        mesg = mesg + changdi_mesg
        await FIGHT.update_fight_info(fightid,uid1,myinfo,myzhuangtai)
        await FIGHT.update_fight_info(fightid,uid2,diinfo,dizhuangtai)
        await FIGHT.update_changdi_info(fightid,changdi)
        await FIGHT.update_fight_flag(fightid,uid1,2)
        await FIGHT.update_fight_flag(fightid,uid2,2)
        await FIGHT.update_fight_mes(fightid,mesg)
    
async def pokemon_fight_pipei(
    bot,ev,myuid,diuid,myname,diname,mypokemon_info,dipokemon_info,fightid,mes
):
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
        await FIGHT.update_fight_flag(fightid,myuid,0)
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
                            f'{mes}\n{myname}请在{FIGHT_TIME}秒内选择一个技能使用!',
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
            myinfo,myzhuangtai,jineng_use1 = await FIGHT.get_fight_info(fightid,myuid)
            diinfo,dizhuangtai,jineng_use2 = await FIGHT.get_fight_info(fightid,diuid)
            changdi = await FIGHT.get_changdi_info(fightid)
            jineng1 = await now_use_jineng(
                myinfo, diinfo, my_ues_jineng_list, dijinenglist, changdi
            )
        await FIGHT.update_jineng(fightid,myuid,jineng1)
        await FIGHT.update_fight_flag(fightid,myuid,1)
        await fight_pipei_now(fightid,myuid,diuid,myname,diname)
        fightflag = 1
        while fightflag == 1:
            await asyncio.sleep(.5)
            fightflag = await FIGHT.get_fight_flag(fightid,myuid)
        
        if fightflag == 2:
            mes = await FIGHT.get_fight_mes(fightid)
        
        myinfo,myzhuangtai,jineng_use1 = await FIGHT.get_fight_info(fightid,myuid)
        if myinfo[17] <= 0:
            fight_flag = 1
        diinfo,dizhuangtai,jineng_use2 = await FIGHT.get_fight_info(fightid,diuid)
        dipokelist = await FIGHT.get_pokelist(fightid,diuid)
        if diinfo[17] <= 0 and myinfo[17] > 0:
            dipokehp = 0
            dipokenum = len(dipokelist)
            if diinfo[17] <= 0 and len(dipokelist) > 1:
                await bot.send(f'{mes}\n等待{diname}更换精灵中')
            while dipokehp <= 0 and dipokenum > 0:
                await asyncio.sleep(.5)
                diinfo,dizhuangtai,jineng_use2 = await FIGHT.get_fight_info(fightid,diuid)
                dipokehp = diinfo[17]
                dipokelist = await FIGHT.get_pokelist(fightid,diuid)
                dipokenum = len(dipokelist)
            if dipokenum == 0:
                return myinfo,mes
            diusepokeid = await get_poke_bianhao(diinfo[0])
            distartype = await POKE.get_pokemon_star(diuid, diusepokeid)
            mes = f"{diname}派出了{starlist[distartype]}{diinfo[0]} Lv.{diinfo[2]}"
    return myinfo,mes

async def get_new_pokemon_id(bot, ev, uid, pokelist, myname, mes):
    pokebuttonlist = []
    button_user_input_my = []
    button_user_input_my.append(uid)
    pokenamelist = []
    for pokeid in pokelist:
        pokenamelist.append(CHARA_NAME[pokeid][0])
        pokebuttonlist.append(Button(f'{CHARA_NAME[pokeid][0]}', f'{CHARA_NAME[pokeid][0]}', f'{CHARA_NAME[pokeid][0]}', action=1, permisson=0, specify_user_ids=button_user_input_my))
    button_use = 0
    runmynum = 0
    try:
        async with timeout(FIGHT_TIME):
            while button_use == 0:
                if runmynum == 0:
                    myresp = await bot.receive_resp(
                        f'{mes}\n{myname}请在{FIGHT_TIME}秒内选择需要派出的精灵!',
                        pokebuttonlist,
                        unsuported_platform=True
                    )
                    if myresp is not None:
                        mys = myresp.text
                        uidmy = myresp.user_id
                        if str(uidmy) == str(uid):
                            if mys in pokenamelist:
                                usepokename = mys
                                button_use = 1
                    runmynum = 1
                else:
                    myresp = await bot.receive_mutiply_resp()
                    if myresp is not None:
                        mys = myresp.text
                        uidmy = myresp.user_id
                        if str(uidmy) == str(uid):
                            if mys in pokenamelist:
                                usepokename = mys
                                button_use = 1
    except asyncio.TimeoutError:
        usepokename = pokenamelist[0]
    usepokeid = await get_poke_bianhao(usepokename)
    return usepokeid
    
async def fight_pk_pipei(
    bot, ev, myuid, diuid, mypokelist, dipokelist, myname, diname, fightid, level=0
):
    zhuangtai = [['无', 0], ['无', 0]]
    changci = 1
    myinfo = []
    jineng_use = []
    mesg = []
    max_my_num = len(mypokelist)
    max_di_num = len(dipokelist)
    bg_num = 1
    mes = ''
    while len(mypokelist) > 0 and len(dipokelist) > 0:
        changci += 1
        if len(myinfo) == 0:
            if max_my_num == len(mypokelist):
                bianhao1 = mypokelist[0]
            else:
                if len(mypokelist) > 1:
                    bianhao1 = await get_new_pokemon_id(bot, ev, myuid, mypokelist, myname, mes)
                else:
                    bianhao1 = mypokelist[0]
            mypokemon_info = await get_pokeon_info(myuid, bianhao1)
            myinfo = await new_pokemon_info(bianhao1, mypokemon_info, level)
            mystartype = await POKE.get_pokemon_star(myuid, bianhao1)
            myinfo[0] = f'{starlist[mystartype]}{myinfo[0]}'
            await FIGHT.new_fight_info(fightid,myuid,mypokelist,myinfo,zhuangtai)
        mes = f'\n{myname}派出了精灵\n{starlist[mystartype]}{POKEMON_LIST[bianhao1][0]} Lv.{myinfo[2]}'
        if max_di_num == len(dipokelist) and max_my_num == len(mypokelist):
            bianhao2 = dipokelist[0]
            distartype = await POKE.get_pokemon_star(diuid, dipokelist[0])
            dipokemon_info = await get_pokeon_info(diuid, dipokelist[0])
            mes += f'\n{diname}派出了精灵\n{starlist[distartype]}{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}'
        myinfo,mes = await pokemon_fight_pipei(bot,ev,myuid,diuid,myname,diname,mypokemon_info,dipokemon_info,fightid,mes)
        if myinfo[17] <= 0:
            myinfo = []
            myzhuangtai = [['无', 0], ['无', 0]]
            mypokelist.remove(bianhao1)
            jineng_use = []
        dipokelist = await FIGHT.get_pokelist(fightid,diuid)
    return mypokelist, dipokelist, mes
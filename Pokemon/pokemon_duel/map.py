import asyncio
import base64
import os
import re
import random
import sqlite3
import math
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.image.convert import convert_img
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH
import copy
import json
from .pokeconfg import *
from .pokemon import *
from .PokeCounter import *
from .until import *
from pathlib import Path

TS_FIGHT = 20
TS_PROP = 10
TS_POKEMON = 70
WIN_EGG = 10

Excel_path = Path(__file__).parent
with Path.open(Excel_path / 'map.json', encoding='utf-8') as f:
    map_dict = json.load(f)
    diqulist = map_dict['diqulist']
    didianlist = map_dict['didianlist']

sv_pokemon_map = SV('宝可梦探索', priority=5)

@sv_pokemon_map.on_prefix(['探索测试'])
async def map_ts_test(bot, ev: Event):
    args = ev.text.split()
    gid = ev.group_id
    uid = ev.user_id
    this_map = args[0]
    if didianlist[this_map]['type'] == "城镇":
        return await bot.send(f'您当前处于城镇中没有可探索的区域', at_sender=True)
    mes = []
    
    if didianlist[this_map]['type'] == "野外":
        pokelist = list(CHARA_NAME.keys())
        mypokelist = random.sample(pokelist, 4)
        ts_z = TS_FIGHT + TS_PROP + TS_POKEMON
        ts_num = int(math.floor(random.uniform(0,ts_z)))
        ts_quality = TS_POKEMON
        if ts_num <= ts_quality:
            # 遇怪
            pokelist = didianlist[this_map]['pokemon']
            dipokelist = random.sample(pokelist, 1)
            pokename = CHARA_NAME[dipokelist[0]][0]
            pokemonid = dipokelist[0]
            mes_list,mypokelist,dipokelist = await fight_yw_ys(gid,uid,mypokelist,dipokelist,didianlist[this_map]['level'][0],didianlist[this_map]['level'][1],1)
            if len(mypokelist) == 0:
                mes = f'您被野生宝可梦{pokename}打败了'
                mes_list.append(MessageSegment.text(mes))
                await bot.send(MessageSegment.node(mes_list))
            if len(dipokelist) == 0:
                mes = f'您打败了{pokename}\n'
                zs_num = int(math.floor(random.uniform(0,100)))
                if zs_num <= WIN_EGG:
                    mes += f'您获得了{pokename}精灵蛋'
                mes_list.append(MessageSegment.text(mes))
                await bot.send(MessageSegment.node(mes_list))
        else:
            ts_quality += TS_FIGHT
            if ts_num <= ts_quality:
                # 对战
                pokelist = didianlist[this_map]['pokemon']
                maxnum = min(5,int(didianlist[this_map]['need']) + 1)
                pokenum = int(math.floor(random.uniform(1,maxnum)))
                dipokelist = []
                for item in range(0,pokenum):
                    dipokelist.append(random.sample(pokelist, 1)[0])
                mes_list,mypokelist,dipokelist = await fight_yw_ys(gid,uid,mypokelist,dipokelist,didianlist[this_map]['level'][0],didianlist[this_map]['level'][1])
                if len(mypokelist) == 0:
                    mes = '您被野外训练家[未命名]打败了'
                    mes_list.append(MessageSegment.text(mes))
                    await bot.send(MessageSegment.node(mes_list))
                if len(dipokelist) == 0:
                    mes = '您打败了野外训练家[未命名]\n'
                    get_score = (int(didianlist[this_map]['need']) + 1) * 500
                    mes += f'您获得了{get_score}金钱'
                    mes_list.append(MessageSegment.text(mes))
                    await bot.send(MessageSegment.node(mes_list))
            else:
                await bot.send('您获得了道具[还没写好]', at_sender=True)

@sv_pokemon_map.on_fullmatch(['当前地点信息'])
async def map_info_now(bot, ev: Event):
    gid = ev.group_id
    uid = ev.user_id
    this_map = "华蓝洞窟"
    mes = []
    diquname = diqulist[didianlist[this_map]['fname']]['name']
    mes.append(MessageSegment.text(f'当前所在地为:{diquname}-{this_map}\n'))
    if didianlist[this_map]['type'] == "城镇":
        mes.append(MessageSegment.text(f'当前所在地打工1小时可获得xxx金币\n'))
    if didianlist[this_map]['type'] == "野外":
        name_str = get_pokemon_name_list(didianlist[this_map]['pokemon'])
        mes.append(MessageSegment.text(f'当前所在地野外探索遭遇的精灵为\n{name_str}\n'))
        mes.append(MessageSegment.text(f"等级:{didianlist[this_map]['level'][0]}-{didianlist[this_map]['level'][1]}\n"))
        if didianlist[this_map]['pokemon_s']:
            pokemon_s_list = didianlist[this_map]['pokemon_s']
            mes.append(MessageSegment.text(f'当前所在地野外垂钓遭遇的精灵为\n'))
            for item in pokemon_s_list:
                mes.append(MessageSegment.text(f'拥有徽章数大于{str(item)}枚时\n'))
                name_str = get_pokemon_name_list(pokemon_s_list[item]['pokemon'])
                mes.append(MessageSegment.text(f'{name_str}\n'))
                mes.append(MessageSegment.text(f"等级:{pokemon_s_list[item]['level'][0]}-{pokemon_s_list[item]['level'][1]}\n"))
    await bot.send(mes, at_sender=True)

@sv_pokemon_map.on_prefix(['前往'])
async def pokemom_go_map(bot, ev: Event):
    args = ev.text.split()
    if len(args)<1:
        return await bot.send('请输入 前往+地点名称。', at_sender=True)
    go_map = args[0]
    uid = ev.user_id
    this_map = "华蓝洞窟"
    my_hz = 0
    if go_map == this_map:
        return await bot.send(f'您已经处于{this_map}中，无需前往', at_sender=True)
    list_dizhi = list(didianlist.keys())
    if go_map not in list_dizhi:
        return await bot.send(f'地图上没有{go_map},请输入正确的地址名称', at_sender=True)
    if didianlist[go_map]['fname'] == didianlist[this_map]['fname']:
        if int(my_hz) >= int(didianlist[go_map]['need']):
            await bot.send(f'您已到达{go_map},当前地址信息可输入[当前地点信息]查询', at_sender=True)
        else:
            return await bot.send(f"前往{go_map}所需徽章为{str(didianlist[go_map]['need'])}枚,您的徽章为{str(my_hz)}枚,无法前往", at_sender=True)
    else:
        if int(my_hz) >= 8:
            await bot.send(f'您已到达{go_map},当前地址信息可输入[当前地点信息]查询', at_sender=True)
        else:
            return await bot.send(f"跨地区前往需要8枚徽章,您的徽章为{str(my_hz)}枚,无法前往", at_sender=True)




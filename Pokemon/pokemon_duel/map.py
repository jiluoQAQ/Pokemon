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

Excel_path = Path(__file__).parent
with Path.open(Excel_path / 'map.json', encoding='utf-8') as f:
    map_dict = json.load(f)
    diqulist = map_dict['diqulist']
    didianlist = map_dict['didianlist']

sv_pokemon_map = SV('宝可梦探索', priority=5)
    
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
    list_dizhi = didianlist.keys()
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




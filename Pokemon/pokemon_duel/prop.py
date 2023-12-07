import asyncio
import base64
import os
import re
import random
import copy
import sqlite3
import math
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.image.convert import convert_img
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH
from ..utils.dbbase.ScoreCounter import SCORE_DB
from gsuid_core.message_models import Button
import copy
import json
from .pokeconfg import *
from .pokemon import *
from .PokeCounter import *
from .until import *
from pathlib import Path
from ..utils.fonts.starrail_fonts import (
    sr_font_18,
    sr_font_20,
    sr_font_23,
    sr_font_24,
    sr_font_26,
    sr_font_28,
    sr_font_34,
    sr_font_38,
)


Excel_path = Path(__file__).parent
with Path.open(Excel_path / 'prop.json', encoding='utf-8') as f:
    prop_dict = json.load(f)
    proplist = prop_dict['proplist']
    
TEXT_PATH = Path(__file__).parent / 'texture2D'

sv_pokemon_prop = SV('宝可梦道具', priority=5)

@sv_pokemon_prop.on_fullmatch(['道具帮助','宝可梦道具帮助'])
async def pokemon_help_prop(bot, ev: Event):
    msg='''  
             宝可梦道具帮助
指令：
1、道具商店(查看商城出售的道具)
2、道具信息[道具名](查看道具的具体信息)
3、购买道具[道具名][数量](购买道具,数量默认为1)
4、使用道具[道具名][精灵名][数量](对宝可梦使用道具,数量默认为1)
5、我的道具(查看我的道具列表)
 '''
    buttons = [
        Button(f'✅道具商店', '道具商店'),
        Button(f'✅我的道具', '我的道具'),
        Button(f'✅购买道具', '购买道具', action = 2),
        Button(f'✅道具信息', '道具信息', action = 2),
        Button(f'✅使用道具', '使用道具', action = 2),
    ]
    await bot.send_option(msg,buttons)


@sv_pokemon_prop.on_fullmatch(['道具商店'])
async def prop_shop_list(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
    mychenghao,huizhang = get_chenghao(uid)
    SCORE = SCORE_DB()
    my_score = SCORE.get_score(uid)
    mes = f'我的金币:{my_score}\n商品列表(商品随得到的徽章增多)\n'
    propinfolist = ''
    for propinfo in proplist:
        if proplist[propinfo]['score'] > 0 and huizhang >= proplist[propinfo]['huizhang']:
            propinfolist += f"{propinfo} [{proplist[propinfo]['type']}] 售价:{proplist[propinfo]['score']}\n"
    if propinfolist == '':
        mes = '商店暂时没有出售的物品，去挑战道馆试试吧'
        buttons = [
            Button(f'挑战道馆', '挑战道馆'),
        ]
    else:
        mes += propinfolist
        buttons = [
            Button(f'✅购买道具', '购买道具', action = 2),
            Button(f'📖道具信息', '道具信息', action = 2),
        ]
    await bot.send_option(mes,buttons)

@sv_pokemon_prop.on_prefix(['道具信息'])
async def prop_info(bot, ev: Event):
    args = ev.text.split()
    if len(args)!=1:
        return await bot.send('请输入 道具信息+道具名称', at_sender=True)
    propname = args[0]
    uid = ev.user_id
    mychenghao,huizhang = get_chenghao(uid)
    try:
        propinfo = proplist[propname]
        mes = f"名称：{propname}\n类型：{propinfo['type']}\n描述：{propinfo['content']}"
        if propinfo['score'] > 0:
            mes += f"\n售价：{propinfo['score']}"
        if propinfo['score'] > 0 and int(huizhang) >= propinfo['huizhang']:
            buttons = [
                Button('✅购买道具', f'购买道具 {propname}', action = 2),
            ]
            await bot.send_option(mes,buttons)
        else:
            await bot.send(mes)
    except:
        return await bot.send('无法找到该道具，请输入正确的道具名称。', at_sender=True)

@sv_pokemon_prop.on_prefix(['购买道具'])
async def prop_buy(bot, ev: Event):
    args = ev.text.split()
    if len(args)<1:
        return await bot.send('请输入 购买道具+道具名称+道具数量 用空格隔开', at_sender=True)
    propname = args[0]
    if len(args) == 2:
        propnum = int(args[1])
    else:
        propnum = 1
    uid = ev.user_id
    POKE = PokeCounter()
    SCORE = SCORE_DB()
    mychenghao,huizhang = get_chenghao(uid)
    try:
        propinfo = proplist[propname]
        if propinfo['score'] == 0:
            return await bot.send(f"无法购买该道具", at_sender=True)
        my_score = SCORE.get_score(uid)
        use_score = propinfo['score'] * propnum
        if propinfo['huizhang'] > int(huizhang):
            return await bot.send(f"需要{propinfo['huizhang']}枚徽章才能开放{propname}的购买", at_sender=True)
        if use_score > my_score:
            return await bot.send(f'购买{propnum}件{propname}需要金币{use_score},您的金币不足', at_sender=True)
        SCORE.update_score(uid, 0 - use_score)
        POKE._add_pokemon_prop(uid, propname, propnum)
        mes = f"恭喜！您花费了{use_score}金币成功购买了{propnum}件{propname}"
        if propinfo['type'] == '消耗品':
            buttons = [
                Button('✅使用道具', f'使用道具 {propname}', action = 2),
            ]
            await bot.send_option(mes,buttons)
        else:
            await bot.send(mes)
    except:
        return await bot.send('无法找到该道具，请输入正确的道具名称。', at_sender=True)

@sv_pokemon_prop.on_prefix(['使用道具'])
async def prop_use(bot, ev: Event):
    args = ev.text.split()
    if len(args)<2:
        return await bot.send('请输入 使用道具+道具名称+精灵名+道具数量 用空格隔开', at_sender=True)
    propname = args[0]
    pokename = args[1]
    if len(args) == 3:
        propnum = int(args[2])
    else:
        propnum = 1
    uid = ev.user_id
    POKE = PokeCounter()
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid,bianhao)
    if pokemon_info == 0:
        return await bot.send(f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True)
    
    propkeylist = proplist.keys()
    if propname not in propkeylist:
        return await bot.send('无法找到该道具，请输入正确的道具名称。', at_sender=True)
    propinfo = proplist[propname]
    if propinfo['type'] == '进化':
        return await bot.send('进化类道具无法直接使用，进华时会自动消耗。', at_sender=True)
    if propinfo['use'][0] == '性格':
        propnum = 1
    mypropnum = POKE._get_pokemon_prop(uid, propname)
    if mypropnum == 0:
        return await bot.send(f'您还没有{propname}哦。', at_sender=True)
    if mypropnum < propnum:
        return await bot.send(f'您的{propname}数量小于{propnum}，使用失败。', at_sender=True)
    if propinfo['use'][0] == '性格':
        if pokemon_info[13] == propinfo['use'][1]:
            return await bot.send(f'您的{POKEMON_LIST[bianhao][0]}的性格已经是{pokemon_info[13]}了，使用失败。', at_sender=True)
        POKE._add_pokemon_xingge(uid, bianhao, propinfo['use'][1])
        POKE._add_pokemon_prop(uid, propname, -1)
        mes = f"使用成功！您的{POKEMON_LIST[bianhao][0]}的性格变成了{propinfo['use'][1]}。"
        buttons = [
            Button(f'📖精灵状态', f'精灵状态{pokename}'),
        ]
        await bot.send_option(mes,buttons)
    elif propinfo['use'][0] == '努力':
        if propinfo['use'][2] > 0:
            nl_z = pokemon_info[7] + pokemon_info[8] + pokemon_info[9] + pokemon_info[10] + pokemon_info[11] + pokemon_info[12]
            if nl_z >= 510:
                return await bot.send(f'使用失败,{POKEMON_LIST[bianhao][0]}的基础值已经无法再提升了。', at_sender=True)
            nl_index = int(propinfo['use'][1] + 7)
            if pokemon_info[nl_index] >= 252:
                return await bot.send(f"使用失败,{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值已经无法再提升了。", at_sender=True)
            add_num = propnum * propinfo['use'][2]
            need_num = 252 - pokemon_info[nl_index]
            if add_num < need_num:
                use_peop_num = propnum
            else:
                use_peop_num = math.ceil(propnum - (add_num-need_num)/propinfo['use'][2])
            add_num = use_peop_num * propinfo['use'][2]
            change_nl = min(252, add_num + pokemon_info[nl_index])
            change_nl_num = change_nl - pokemon_info[nl_index]
            # print(nl_index)
            pokemon_info = list(pokemon_info)
            pokemon_info[nl_index] = change_nl
            POKE = PokeCounter()
            POKE._add_pokemon_nuli(uid, bianhao, pokemon_info[7], pokemon_info[8], pokemon_info[9], pokemon_info[10], pokemon_info[11], pokemon_info[12])
            mes = f"使用成功！{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值提升了{change_nl_num}点"
            POKE._add_pokemon_prop(uid, propname, 0 - use_peop_num)
            buttons = [
                Button(f'📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes,buttons)
        else:
            nl_index = int(propinfo['use'][1] + 7)
            if pokemon_info[nl_index] == 0:
                return await bot.send(f"使用失败,{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值已经无法再降低了。", at_sender=True)
            add_num = 0 - propnum * propinfo['use'][2]
            need_num = pokemon_info[nl_index]
            if add_num < need_num:
                use_peop_num = propnum
            else:
                use_peop_num = math.ceil(propnum - (add_num-need_num)/(0-propinfo['use'][2]))
            add_num = use_peop_num * propinfo['use'][2]
            change_nl = max(0, add_num + pokemon_info[nl_index])
            change_nl_num = pokemon_info[nl_index] - change_nl
            pokemon_info = list(pokemon_info)
            pokemon_info[nl_index] = change_nl
            POKE = PokeCounter()
            POKE._add_pokemon_nuli(uid, bianhao, pokemon_info[7], pokemon_info[8], pokemon_info[9], pokemon_info[10], pokemon_info[11], pokemon_info[12])
            mes = f"使用成功！{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值降低了{change_nl_num}点"
            POKE._add_pokemon_prop(uid, propname, 0 - use_peop_num)
            buttons = [
                Button(f'📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes,buttons)
    elif propinfo['use'][0] == '升级':
        if propinfo['use'][1] == 'level':
            if pokemon_info[0] == 100:
                return await bot.send(f'使用失败,{POKEMON_LIST[bianhao][0]}的等级已经无法再提升了。', at_sender=True)
            add_level = propinfo['use'][2] * propnum
            need_level = 100 - pokemon_info[0]
            if add_level <= need_level:
                use_peop_num = propnum
            else:
                use_peop_num = math.ceil(propnum - (add_level-need_level)/propinfo['use'][2])
            add_level = use_peop_num * propinfo['use'][2]
            now_level = pokemon_info[0] + add_level
            POKE._add_pokemon_level(uid, bianhao, now_level, 0)
            mes = f"使用成功！{POKEMON_LIST[bianhao][0]}的等级提升了{add_level}"
            POKE._add_pokemon_prop(uid, propname, 0 - use_peop_num)
            buttons = [
                Button(f'📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes,buttons)
    
@sv_pokemon_prop.on_fullmatch(['我的道具'])
async def prop_my_list(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
    myproplist = POKE.get_pokemon_prop_list(uid)
    if myproplist == 0:
        return await bot.send(f'您还没有道具哦。', at_sender=True)
    mes = ''
    for propinfo in myproplist:
        mes += f'{propinfo[0]} 数量 {propinfo[1]}\n'
    buttons = [
        Button(f'📖道具信息', '道具信息', action = 2),
        Button(f'✅使用道具', '使用道具', action = 2),
    ]
    await bot.send_option(mes,buttons)
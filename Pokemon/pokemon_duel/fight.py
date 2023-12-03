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
import copy
import json
from .pokeconfg import *
from .pokemon import *
from .PokeCounter import *
from .until import *
from pathlib import Path
from .nameconfig import First_Name, Last_Name, Call_Name
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

TS_FIGHT = 20
TS_PROP = 0
TS_POKEMON = 70
WIN_EGG = 10
black_color = (0, 0, 0)

Excel_path = Path(__file__).parent
with Path.open(Excel_path / 'map.json', encoding='utf-8') as f:
    map_dict = json.load(f)
    diqulist = map_dict['diqulist']
    didianlist = map_dict['didianlist']
    daoguanlist = map_dict['daoguanlist']
    tianwanglist = map_dict['tianwanglist']
    guanjunlist = map_dict['guanjunlist']

TEXT_PATH = Path(__file__).parent / 'texture2D'

sv_pokemon_pk = SV('宝可梦对战', priority=5)

@sv_pokemon_pk.on_fullmatch(['挑战道馆'])
async def pk_vs_daoguan(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send('您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询', at_sender=True)
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
    if this_map == '':
        return await bot.send('您还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send('您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
    
    mapinfo = POKE._get_map_now(uid)
    mychenghao,huizhang = get_chenghao(uid)
    if int(mapinfo[0]) > 7:
        if int(mapinfo[0]) == 8:
            return await bot.send('您已通过8个道馆的挑战，可以去[挑战天王]了 ', at_sender=True)
        if int(mapinfo[0]) == 9:
            return await bot.send(f'您已经是【{mychenghao}】了，可以去[挑战四天王冠军]了，就不要拿小的开玩笑了', at_sender=True)
        if int(mapinfo[0]) == 10:
            return await bot.send(f'尊敬的【{mychenghao}】，您莫非是在开玩笑吗', at_sender=True)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    mes = ''
    name = name[:10]
    
    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    diquname = didianlist[this_map]['fname']
    daoguaninfo = daoguanlist[diquname][str(huizhang)]
        
    # 对战
    chenghao = "道馆训练家"
    xingming = daoguaninfo['name']
    diname = chenghao + ' ' + xingming
    min_level = daoguaninfo['level'][0]
    max_level = daoguaninfo['level'][1]
    # pokenum = 3
    dipokelist = copy.deepcopy(daoguaninfo['pokemonlist'])
    mes += f'{diname}向您发起了对战\n'
    
    my_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    di_image = Image.open(trainers_path / f'{xingming}.png').convert('RGBA').resize((120, 120))
    bg_img.paste(my_image, (0, 0), my_image)
    bg_img.paste(di_image, (580, 0), di_image)
    img_draw = ImageDraw.Draw(bg_img)
    img_draw.text(
        (125, 30),
        mychenghao,
        black_color,
        sr_font_24,
        'lm',
    )
    img_draw.text(
        (125, 65),
        f'{name}',
        black_color,
        sr_font_24,
        'lm',
    )
    img_draw.text(
        (575, 30),
        chenghao,
        black_color,
        sr_font_24,
        'rm',
    )
    img_draw.text(
        (575, 65),
        xingming,
        black_color,
        sr_font_24,
        'rm',
    )
    bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,min_level,max_level)
    mes += mes_list
    if math.ceil((img_height + 130)/1280) > bg_num:
        bg_num += 1
        bg_img = change_bg_img(bg_img, bg_num)
    img_draw = ImageDraw.Draw(bg_img)
    if len(mypokelist) == 0:
        mes += f'\n您被{diname}打败了，眼前一黑'
        # mes_list.append(MessageSegment.text(mes))
        img_draw.text(
            (575, img_height + 30),
            f'您被{diname}打败了，眼前一黑',
            black_color,
            sr_font_20,
            'rm',
        )
        bg_img.paste(di_image, (580, img_height), di_image)
        img_height += 130
        # await bot.send(mes, at_sender=True)
    if len(dipokelist) == 0:
        mes += f'\n您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'您打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )
        SCORE = SCORE_DB()
        new_huizhang = int(huizhang) + 1
        get_score = new_huizhang * 1000
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您获得了1枚徽章'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        POKE._update_map_huizhang(uid,new_huizhang)
        img_draw.text(
            (125, img_height + 100),
            f'您获得了1枚徽章',
            black_color,
            sr_font_20,
            'lm',
        )
        bg_img.paste(my_image, (0, img_height), my_image)
        # mes_list.append(MessageSegment.text(mes))
        # await bot.send(mes, at_sender=True)
        img_height += 130
    img_bg = Image.new('RGB', (700, img_height), (255, 255, 255))
    img_bg.paste(bg_img, (0, 0))
    img_bg = await convert_img(img_bg)
    await bot.send(img_bg)

@sv_pokemon_pk.on_fullmatch(['挑战天王'])
async def pk_vs_tianwang(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send('您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询', at_sender=True)
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
    if this_map == '':
        return await bot.send('您还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send('您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
    
    mapinfo = POKE._get_map_now(uid)
    mychenghao,huizhang = get_chenghao(uid)
    if int(mapinfo[0]) < 8:
        return await bot.send(f'请先挑战完8个道馆再向天王发起挑战哦', at_sender=True)
    if int(mapinfo[0]) > 8:
        if int(mapinfo[0]) == 9:
            return await bot.send(f'您已经是【{mychenghao}】了，可以去[挑战四天王冠军]了，就不要开玩笑了', at_sender=True)
        if int(mapinfo[0]) == 10:
            return await bot.send(f'尊敬的【{mychenghao}】，您莫非是在开玩笑吗', at_sender=True)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    mes = ''
    name = name[:10]
    
    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    ranlist = [0,1,2,3]
    tianwangid = int(random.sample(ranlist,1)[0])
    
    diquname = didianlist[this_map]['fname']
    tianwanginfo = tianwanglist[diquname][tianwangid]
        
    # 对战
    chenghao = "天王训练家"
    xingming = tianwanginfo['name']
    diname = chenghao + ' ' + xingming
    min_level = tianwanginfo['level'][0]
    max_level = tianwanginfo['level'][1]
    # pokenum = 3
    dipokelist = copy.deepcopy(tianwanginfo['pokemonlist'])
    mes += f'{diname}向您发起了对战\n'
    
    my_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    di_image = Image.open(trainers_path / f'{xingming}.png').convert('RGBA').resize((120, 120))
    bg_img.paste(my_image, (0, 0), my_image)
    bg_img.paste(di_image, (580, 0), di_image)
    img_draw = ImageDraw.Draw(bg_img)
    img_draw.text(
        (125, 30),
        mychenghao,
        black_color,
        sr_font_24,
        'lm',
    )
    img_draw.text(
        (125, 65),
        f'{name}',
        black_color,
        sr_font_24,
        'lm',
    )
    img_draw.text(
        (575, 30),
        chenghao,
        black_color,
        sr_font_24,
        'rm',
    )
    img_draw.text(
        (575, 65),
        xingming,
        black_color,
        sr_font_24,
        'rm',
    )
    bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,min_level,max_level)
    mes += mes_list
    if math.ceil((img_height + 130)/1280) > bg_num:
        bg_num += 1
        bg_img = change_bg_img(bg_img, bg_num)
    img_draw = ImageDraw.Draw(bg_img)
    if len(mypokelist) == 0:
        mes += f'\n您被{diname}打败了，眼前一黑'
        # mes_list.append(MessageSegment.text(mes))
        img_draw.text(
            (575, img_height + 30),
            f'您被{diname}打败了，眼前一黑',
            black_color,
            sr_font_20,
            'rm',
        )
        bg_img.paste(di_image, (580, img_height), di_image)
        img_height += 130
        # await bot.send(mes, at_sender=True)
    if len(dipokelist) == 0:
        mes += f'\n您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'您打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )
        SCORE = SCORE_DB()
        new_huizhang = int(mapinfo[0]) + 1
        get_score = new_huizhang * 1000
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您成为了【天王训练家】'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        POKE._update_map_huizhang(uid,new_huizhang)
        img_draw.text(
            (125, img_height + 100),
            f'您成为了【天王训练家】',
            black_color,
            sr_font_20,
            'lm',
        )
        bg_img.paste(my_image, (0, img_height), my_image)
        # mes_list.append(MessageSegment.text(mes))
        # await bot.send(mes, at_sender=True)
        img_height += 130
    img_bg = Image.new('RGB', (700, img_height), (255, 255, 255))
    img_bg.paste(bg_img, (0, 0))
    img_bg = await convert_img(img_bg)
    await bot.send(img_bg)
    
@sv_pokemon_pk.on_fullmatch(['挑战四天王冠军'])
async def pk_vs_guanjun(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send('您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询', at_sender=True)
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
    if this_map == '':
        return await bot.send('您还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send('您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
    
    mapinfo = POKE._get_map_now(uid)
    mychenghao,huizhang = get_chenghao(uid)
    if int(mapinfo[0]) < 9:
        return await bot.send(f'请先成为【天王训练家】再向冠军发起挑战哦', at_sender=True)
    if int(mapinfo[0]) > 9:
        return await bot.send(f'您已经是【{mychenghao}】，就不要拿同事刷经验了', at_sender=True)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    mes = ''
    name = name[:10]
    
    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    
    diquname = didianlist[this_map]['fname']
    guanjuninfo = guanjunlist[diquname]
        
    # 对战
    chenghao = "四天王冠军"
    xingming = guanjuninfo['name']
    diname = chenghao + ' ' + xingming
    min_level = guanjuninfo['level'][0]
    max_level = guanjuninfo['level'][1]
    # pokenum = 3
    dipokelist = copy.deepcopy(guanjuninfo['pokemonlist'])
    mes += f'{diname}向您发起了对战\n'
    
    my_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    di_image = Image.open(trainers_path / f'{xingming}.png').convert('RGBA').resize((120, 120))
    bg_img.paste(my_image, (0, 0), my_image)
    bg_img.paste(di_image, (580, 0), di_image)
    img_draw = ImageDraw.Draw(bg_img)
    img_draw.text(
        (125, 30),
        mychenghao,
        black_color,
        sr_font_24,
        'lm',
    )
    img_draw.text(
        (125, 65),
        f'{name}',
        black_color,
        sr_font_24,
        'lm',
    )
    img_draw.text(
        (575, 30),
        chenghao,
        black_color,
        sr_font_24,
        'rm',
    )
    img_draw.text(
        (575, 65),
        xingming,
        black_color,
        sr_font_24,
        'rm',
    )
    bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,min_level,max_level)
    mes += mes_list
    if math.ceil((img_height + 130)/1280) > bg_num:
        bg_num += 1
        bg_img = change_bg_img(bg_img, bg_num)
    img_draw = ImageDraw.Draw(bg_img)
    if len(mypokelist) == 0:
        mes += f'\n您被{diname}打败了，眼前一黑'
        # mes_list.append(MessageSegment.text(mes))
        img_draw.text(
            (575, img_height + 30),
            f'您被{diname}打败了，眼前一黑',
            black_color,
            sr_font_20,
            'rm',
        )
        bg_img.paste(di_image, (580, img_height), di_image)
        img_height += 130
        # await bot.send(mes, at_sender=True)
    if len(dipokelist) == 0:
        mes += f'\n您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'您打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )
        SCORE = SCORE_DB()
        new_huizhang = int(mapinfo[0]) + 1
        get_score = new_huizhang * 1000
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您成为了【冠军训练家】'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        POKE._update_map_huizhang(uid,new_huizhang)
        img_draw.text(
            (125, img_height + 100),
            f'您成为了【冠军训练家】',
            black_color,
            sr_font_20,
            'lm',
        )
        bg_img.paste(my_image, (0, img_height), my_image)
        # mes_list.append(MessageSegment.text(mes))
        # await bot.send(mes, at_sender=True)
        img_height += 130
    img_bg = Image.new('RGB', (700, img_height), (255, 255, 255))
    img_bg.paste(bg_img, (0, 0))
    img_bg = await convert_img(img_bg)
    await bot.send(img_bg)
    
@sv_pokemon_pk.on_command(('无级别对战','无级别战斗'))
async def pokemon_pk_wjb(bot, ev: Event):
    if ev.bot_id == 'qqgroup':
        return await bot.send('当前平台不支持无级别对战。', at_sender=True)
    uid = ev.user_id
    POKE = PokeCounter()
    mapinfo = POKE._get_map_now(uid)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    
    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(f'{name} 还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询', at_sender=True)
    if mapinfo[1] == '':
        return await bot.send(f'{name} 还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(f'{name} 还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    
    if ev.at is not None:
        diuid = ev.at
        dimapinfo = POKE._get_map_now(diuid)
        if dimapinfo[2] == 0:
            return await bot.send('没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。', at_sender=True)
        diname = dimapinfo[2]
    else:
        args = ev.text.split()
        if len(args)!=1:
            return await bot.send('请输入 无级别对战+对战训练家昵称/at对战训练家。', at_sender=True)
        nickname = args[0]
        dimapinfo = POKE._get_map_info_nickname(nickname)
        if dimapinfo[2] == 0:
            return await bot.send('没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。', at_sender=True)
        diuid = dimapinfo[2]
        diname = nickname
    
    dipokelist = POKE._get_pokemon_list(diuid)
    if dipokelist == 0:
        return await bot.send(f'{diname} 还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询', at_sender=True)
    if dimapinfo[1] == '':
        return await bot.send(f'{diname} 还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    di_team = POKE.get_pokemon_group(diuid)
    if my_team == '':
        return await bot.send(f'{diname} 还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    
    if name == diname:
        return await bot.send('不能自己打自己哦。', at_sender=True)
    
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
    
    di_pokemon_team = di_team.split(',')
    dipokelist = []
    for bianhao in di_pokemon_team:
        bianhao = int(bianhao)
        dipokelist.append(bianhao)
    
    mychenghao,myhuizhang = get_chenghao(uid)
    dichenghao,dihuizhang = get_chenghao(diuid)

    name = name[:10]
    diname = diname[:10]
    # 对战
    mes = f'{mychenghao} {name}向{dichenghao} {diname}发起了挑战'
    await bot.send(mes)
    
    mypokelist,dipokelist = await fight_pk_s(bot,ev,uid,diuid,mypokelist,dipokelist,name,diname)

    if len(mypokelist) == 0:
        mes = f'{diname}打败了{name}，获得了对战的胜利'
        
    if len(dipokelist) == 0:
        mes = f'{name}打败了{diname}，获得了对战的胜利'
    await bot.send(mes)
import asyncio
import base64
import os
import re
import random
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

TEXT_PATH = Path(__file__).parent / 'texture2D'

sv_pokemon_map = SV('宝可梦探索', priority=5)

@sv_pokemon_map.on_fullmatch(['我的金钱'])
async def map_my_score(bot, ev: Event):
    uid = ev.user_id
    SCORE = SCORE_DB()
    my_score = SCORE.get_score(uid)
    await bot.send(f'您的金钱为{my_score}', at_sender=True)

@sv_pokemon_map.on_prefix(('更新队伍','创建队伍'))
async def map_my_group(bot, ev: Event):
    args = ev.text.split()
    if len(args)<1:
        return await bot.send('请输入 更新队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    if len(args)>4:
        return await bot.send('一个队伍最多只能有4只宝可梦。', at_sender=True)
    uid = ev.user_id
    pokemon_list = []
    name_str = ''
    for pokemon_name in args:
        bianhao = get_poke_bianhao(pokemon_name)
        if bianhao == 0:
            return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
        pokemon_info = get_pokeon_info(uid,bianhao)
        if pokemon_info == 0:
            return await bot.send(f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True)
        pokemon_list.append(str(bianhao))
        name_str += f'{pokemon_name} Lv.{pokemon_info[0]}\n'
    POKE = PokeCounter()
    pokemon_str = ','.join(pokemon_list)
    POKE._add_pokemon_group(uid,pokemon_str)
    
    await bot.send(f'编组成功，当前队伍\n{name_str}', at_sender=True)

@sv_pokemon_map.on_fullmatch(['训练家名片'])
async def map_my_info(bot, ev: Event):
    print(ev)
    uid = ev.user_id
    POKE = PokeCounter()
    SCORE = SCORE_DB()
    my_score = SCORE.get_score(uid)
    my_pokemon = POKE._get_pokemon_num(uid)
    if my_pokemon == 0:
        return await bot.send('您还没有领取初始精灵成为训练家哦', at_sender=True)
    my_team = POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    mapinfo = POKE._get_map_now(uid)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    mes = ''
    mes += f'训练家名称:{name}\n'
    mes += f'拥有金钱:{my_score}\n'
    mes += f'拥有徽章:{mapinfo[0]}\n'
    if mapinfo[1]:
        this_map = mapinfo[1]
        diquname = diqulist[didianlist[this_map]['fname']]['name']
        mes += f'当前所在地:{diquname}-{this_map}\n'
    mes += f'拥有精灵:{my_pokemon}只\n'
    mes += f'当前队伍:'
    if my_team:
        for bianhao in pokemon_list:
            bianhao = int(bianhao)
            pokemon_info = get_pokeon_info(uid,bianhao)
            mes += f'\n{CHARA_NAME[bianhao][0]} Lv.{pokemon_info[0]}'
    await bot.send(mes, at_sender=True)

@sv_pokemon_map.on_prefix(('修改训练家名称','修改名称'))
async def update_my_name(bot, ev: Event):
    args = ev.text.split()
    if len(args)<1:
        return await bot.send('请输入 修改训练家名称+昵称。', at_sender=True)
    uid = ev.user_id
    name = args[0]
    if len(name)>10:
        return await bot.send('昵称长度不能超过10个字符。', at_sender=True)
    POKE = PokeCounter()
    mapinfo = POKE._get_map_info_nickname(name)
    if mapinfo[2] == 0:
        POKE._update_map_name(uid,name)
        await bot.send(f'修改成功，当前训练家名称为 {name}', at_sender=True)
    else:
        return await bot.send('该昵称已被其他玩家抢注，请选择其他昵称。', at_sender=True)

@sv_pokemon_map.on_fullmatch(['打工'])
async def map_work_test(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send('您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。', at_sender=True)
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
    if not daily_work_limiter.check(uid):
        return await bot.send('今天的打工次数已经超过上限了哦，明天再来吧。', at_sender=True)
    if didianlist[this_map]['type'] == "野外":
        return await bot.send('野外区域无法打工，请返回城镇哦', at_sender=True)
    
    if didianlist[this_map]['type'] == "城镇":
        SCORE = SCORE_DB()
        get_score = (int(didianlist[this_map]['need']) + 1) * 5000
        SCORE.update_score(uid, get_score)
        daily_work_limiter.increase(uid)
        mes = f'您通过打工获得了{get_score}金钱'
        await bot.send(mes, at_sender=True)

@sv_pokemon_map.on_fullmatch(['野外探索v'])
async def map_ts_test(bot, ev: Event):
    uid = ev.user_id
    POKE = PokeCounter()
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
    if didianlist[this_map]['type'] == "城镇":
        return await bot.send(f'您当前处于城镇中没有可探索的区域', at_sender=True)
    mes = []
    if didianlist[this_map]['type'] == "野外":
        pokelist = list(CHARA_NAME.keys())
        ts_z = TS_FIGHT + TS_PROP + TS_POKEMON
        ts_num = int(math.floor(random.uniform(0,ts_z)))
        ts_quality = TS_POKEMON
        if ts_num <= ts_quality:
            # 遇怪
            pokelist = didianlist[this_map]['pokemon']
            dipokelist = random.sample(pokelist, 1)
            pokename = CHARA_NAME[dipokelist[0]][0]
            pokemonid = dipokelist[0]
            await bot.send(f'野生宝可梦{pokename}出现了', at_sender=True)
            mes_list,mypokelist,dipokelist = await fight_yw_ys(uid,mypokelist,dipokelist,didianlist[this_map]['level'][0],didianlist[this_map]['level'][1],1)
            if len(mypokelist) == 0:
                mes = f'您被野生宝可梦{pokename}打败了'
                mes_list.append(MessageSegment.text(mes))
                await bot.send(MessageSegment.node(mes_list))
            if len(dipokelist) == 0:
                mes = f'您打败了{pokename}\n'
                zs_num = int(math.floor(random.uniform(0,100)))
                # if zs_num <= WIN_EGG:
                    # mes += f'您获得了{pokename}精灵蛋'
                    # POKE._add_pokemon_egg(uid,pokemonid,1)
                mes_list.append(MessageSegment.text(mes))
                await bot.send(MessageSegment.node(mes_list))
        else:
            ts_quality += TS_FIGHT
            if ts_num <= ts_quality:
                # 对战
                diname = str(random.sample(Call_Name, 1)[0]) + ' ' + str(random.sample(First_Name, 1)[0]) + str(random.sample(Last_Name, 1)[0])
                pokelist = didianlist[this_map]['pokemon']
                maxnum = min(5,int(didianlist[this_map]['need']) + 1)
                min_level = didianlist[this_map]['level'][0]/2 + didianlist[this_map]['level'][0]
                max_level = didianlist[this_map]['level'][0]/2 + didianlist[this_map]['level'][1]
                pokenum = int(math.floor(random.uniform(1,maxnum)))
                dipokelist = []
                await bot.send(f'{diname}向您发起了对战', at_sender=True)
                for item in range(0,pokenum):
                    dipokelist.append(random.sample(pokelist, 1)[0])
                mes_list,mypokelist,dipokelist = await fight_yw_ys(uid,mypokelist,dipokelist,min_level,max_level)
                if len(mypokelist) == 0:
                    mes = f'您被{diname}打败了，眼前一黑'
                    mes_list.append(MessageSegment.text(mes))
                    await bot.send(MessageSegment.node(mes_list))
                if len(dipokelist) == 0:
                    mes = f'您打败了{diname}\n'
                    SCORE = SCORE_DB()
                    get_score = (int(didianlist[this_map]['need']) + 1) * 500
                    SCORE.update_score(uid, get_score)
                    mes += f'您获得了{get_score}金钱'
                    mes_list.append(MessageSegment.text(mes))
                    await bot.send(MessageSegment.node(mes_list))
            else:
                await bot.send('您获得了道具', at_sender=True)

@sv_pokemon_map.on_fullmatch(['野外探索'])
async def map_ts_test_noauto_use(bot, ev: Event):
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
    if didianlist[this_map]['type'] == "城镇":
        return await bot.send(f'您当前处于城镇中没有可探索的区域', at_sender=True)
    
    mapinfo = POKE._get_map_now(uid)
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
    if didianlist[this_map]['type'] == "野外":
        pokelist = list(CHARA_NAME.keys())
        ts_z = TS_FIGHT + TS_POKEMON
        ts_num = int(math.floor(random.uniform(0,ts_z)))
        ts_quality = TS_POKEMON
        if ts_num <= ts_quality:
            # 遇怪
            pokelist = didianlist[this_map]['pokemon']
            dipokelist = random.sample(pokelist, 1)
            pokename = CHARA_NAME[dipokelist[0]][0]
            pokemonid = dipokelist[0]
            # mes += f'野生宝可梦{pokename}出现了\n'
            my_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
            di_image = Image.open(CHAR_ICON_PATH / f'{pokename}.png').convert('RGBA').resize((120, 120))
            bg_img.paste(my_image, (0, 0), my_image)
            bg_img.paste(di_image, (580, 0), di_image)
            img_draw = ImageDraw.Draw(bg_img)
            img_draw.text(
                (125, 30),
                '训练家',
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
                '野生宝可梦',
                black_color,
                sr_font_24,
                'rm',
            )
            img_draw.text(
                (575, 65),
                f'{pokename}',
                black_color,
                sr_font_24,
                'rm',
            )
            bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,didianlist[this_map]['level'][0],didianlist[this_map]['level'][1],1)
            if math.ceil((img_height + 120)/1280) > bg_num:
                bg_num += 1
                bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
            # mes += mes_list
            if len(mypokelist) == 0:
                # mes += f'您被野生宝可梦{pokename}打败了'
                # mes_list.append(MessageSegment.text(mes))
                # await bot.send(mes, at_sender=True)
                img_draw.text(
                    (575, img_height + 30),
                    f'您被{pokename}打败了，眼前一黑',
                    black_color,
                    sr_font_20,
                    'rm',
                )
                bg_img.paste(di_image, (580, img_height), di_image)
                img_height += 130
            if len(dipokelist) == 0:
                # mes += f'您打败了{pokename}'
                # zs_num = int(math.floor(random.uniform(0,100)))
                # if zs_num <= WIN_EGG:
                    # mes += f'您获得了{pokename}精灵蛋'
                    # POKE._add_pokemon_egg(uid,pokemonid,1)
                # mes_list.append(MessageSegment.text(mes))
                # await bot.send(mes, at_sender=True)
                img_draw.text(
                    (125, img_height + 30),
                    f'您打败了{pokename}',
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
            
        else:
            ts_quality += TS_FIGHT
            if ts_num <= ts_quality:
                # 对战
                chenghao = str(random.sample(Call_Name, 1)[0])
                xingming = str(random.sample(First_Name, 1)[0]) + str(random.sample(Last_Name, 1)[0])
                diname = chenghao + ' ' + xingming
                pokelist = didianlist[this_map]['pokemon']
                maxnum = min(5,int(didianlist[this_map]['need']) + 1)
                min_level = didianlist[this_map]['level'][0]/2 + didianlist[this_map]['level'][0]
                max_level = didianlist[this_map]['level'][0]/2 + didianlist[this_map]['level'][1]
                pokenum = int(math.floor(random.uniform(1,maxnum)))
                # pokenum = 3
                dipokelist = []
                mes += f'{diname}向您发起了对战\n'
                for item in range(0,pokenum):
                    dipokelist.append(random.sample(pokelist, 1)[0])
                
                my_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
                di_image = Image.open(trainers_path / f'{chenghao}.png').convert('RGBA').resize((120, 120))
                bg_img.paste(my_image, (0, 0), my_image)
                bg_img.paste(di_image, (580, 0), di_image)
                img_draw = ImageDraw.Draw(bg_img)
                img_draw.text(
                    (125, 30),
                    '训练家',
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
                # mes += mes_list
                if math.ceil((img_height + 120)/1280) > bg_num:
                    bg_num += 1
                    bg_img = change_bg_img(bg_img, bg_num)
                img_draw = ImageDraw.Draw(bg_img)
                if len(mypokelist) == 0:
                    # mes += f'您被{diname}打败了，眼前一黑'
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
                    # mes += f'您打败了{diname}\n'
                    img_draw.text(
                        (125, img_height + 30),
                        f'您打败了{diname}',
                        black_color,
                        sr_font_20,
                        'lm',
                    )
                    SCORE = SCORE_DB()
                    get_score = (int(didianlist[this_map]['need']) + 1) * 500
                    SCORE.update_score(uid, get_score)
                    mes += f'您获得了{get_score}金钱'
                    img_draw.text(
                        (125, img_height + 65),
                        f'您获得了{get_score}金钱',
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
            else:
                await bot.send('您获得了道具[还没写好]', at_sender=True)

@sv_pokemon_map.on_prefix(('训练家对战','训练家挑战','挑战训练家'))
async def pokemon_pk_auto(bot, ev: Event):
    args = ev.text.split()
    if len(args)!=1:
        return await bot.send('请输入 训练家对战+对战训练家昵称 中间用空格隔开。', at_sender=True)
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
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    
    nickname = args[0]
    dimapinfo = POKE._get_map_info_nickname(nickname)
    if dimapinfo[2] == 0:
        return await bot.send('没有找到该训练家，请输入 正确的对战训练家昵称。', at_sender=True)
    
    diname = nickname
    if name == diname:
        return await bot.send('不能自己打自己哦。', at_sender=True)
    diuid = dimapinfo[2]
    dipokelist = POKE._get_pokemon_list(diuid)
    if mypokelist == 0:
        return await bot.send(f'{diname}还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询', at_sender=True)
    di_team = POKE.get_pokemon_group(diuid)
    if di_team == '':
        return await bot.send(f'{diname}您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。', at_sender=True)
    di_pokemon_team = di_team.split(',')
    dipokelist = []
    for bianhao in di_pokemon_team:
        bianhao = int(bianhao)
        dipokelist.append(bianhao)
    
    name = name[:10]
    diname = diname[:10]
    # 对战
    mes = ''
    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    my_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    di_image = Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    bg_img.paste(my_image, (0, 0), my_image)
    bg_img.paste(di_image, (580, 0), di_image)
    img_draw = ImageDraw.Draw(bg_img)
    img_draw.text(
        (125, 30),
        '训练家',
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
        '训练家',
        black_color,
        sr_font_24,
        'rm',
    )
    img_draw.text(
        (575, 65),
        diname,
        black_color,
        sr_font_24,
        'rm',
    )
    bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_pk(bot,ev,bg_img,uid,diuid,mypokelist,dipokelist,name,diname)
    # mes += mes_list
    if math.ceil((img_height + 120)/1280) > bg_num:
        bg_num += 1
        bg_img = change_bg_img(bg_img, bg_num)
    img_draw = ImageDraw.Draw(bg_img)
    if len(mypokelist) == 0:
        # mes += f'您被{diname}打败了，眼前一黑'
        # mes_list.append(MessageSegment.text(mes))
        img_draw.text(
            (575, img_height + 30),
            f'{diname}打败了{name}',
            black_color,
            sr_font_20,
            'rm',
        )
        SCORE = SCORE_DB()
        get_score = (int(mapinfo[0]) + 1) * 500
        SCORE.update_score(diuid, get_score)
        mes += f'您获得了{get_score}金钱'
        img_draw.text(
            (575, img_height + 65),
            f'{diname}获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'rm',
        )
        bg_img.paste(di_image, (580, img_height), di_image)
        img_height += 130
        # await bot.send(mes, at_sender=True)
    if len(dipokelist) == 0:
        # mes += f'您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'{name}打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )
        SCORE = SCORE_DB()
        get_score = (int(dimapinfo[0]) + 1) * 500
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱'
        img_draw.text(
            (125, img_height + 65),
            f'{name}获得了{get_score}金钱',
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

@sv_pokemon_map.on_fullmatch(['野外探索测试'])
async def map_ts_test_noauto(bot, ev: Event):
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
    if didianlist[this_map]['type'] == "城镇":
        return await bot.send(f'您当前处于城镇中没有可探索的区域', at_sender=True)
    
    mapinfo = POKE._get_map_now(uid)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname','') != '':
                name = sender['nickname']
    mes = ''
    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    if didianlist[this_map]['type'] == "野外":
        pokelist = list(CHARA_NAME.keys())
        ts_z = TS_FIGHT + TS_POKEMON
        ts_num = int(math.floor(random.uniform(0,ts_z)))
        ts_quality = TS_POKEMON
        if ts_num <= ts_quality:
            # 遇怪
            pokelist = didianlist[this_map]['pokemon']
            dipokelist = random.sample(pokelist, 1)
            pokename = CHARA_NAME[dipokelist[0]][0]
            pokemonid = dipokelist[0]
            mes += f'野生宝可梦{pokename}出现了\n'
            bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,didianlist[this_map]['level'][0],didianlist[this_map]['level'][1],1)
            mes += mes_list
            if len(mypokelist) == 0:
                mes += f'\n您被野生宝可梦{pokename}打败了'
            if len(dipokelist) == 0:
                mes += f'\n您打败了{pokename}'
            await bot.send(mes)
            
        else:
            ts_quality += TS_FIGHT
            if ts_num <= ts_quality:
                # 对战
                chenghao = str(random.sample(Call_Name, 1)[0])
                xingming = str(random.sample(First_Name, 1)[0]) + str(random.sample(Last_Name, 1)[0])
                diname = chenghao + ' ' + xingming
                pokelist = didianlist[this_map]['pokemon']
                maxnum = min(5,int(didianlist[this_map]['need']) + 1)
                min_level = didianlist[this_map]['level'][0]/2 + didianlist[this_map]['level'][0]
                max_level = didianlist[this_map]['level'][0]/2 + didianlist[this_map]['level'][1]
                pokenum = int(math.floor(random.uniform(1,maxnum)))
                dipokelist = []
                mes += f'{diname}向您发起了对战\n'
                for item in range(0,pokenum):
                    dipokelist.append(random.sample(pokelist, 1)[0])
                
                bg_img,bg_num,img_height,mes_list,mypokelist,dipokelist = await fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,min_level,max_level)
                mes += mes_list
                if len(mypokelist) == 0:
                    mes += f'您被{diname}打败了，眼前一黑'
                if len(dipokelist) == 0:
                    mes += f'您打败了{diname}\n'
                    SCORE = SCORE_DB()
                    get_score = (int(didianlist[this_map]['need']) + 1) * 500
                    SCORE.update_score(uid, get_score)
                    mes += f'您获得了{get_score}金钱'
                await bot.send(mes)
            else:
                await bot.send('您获得了道具[还没写好]', at_sender=True)

@sv_pokemon_map.on_prefix(['选择初始地区'])
async def pokemom_new_map(bot, ev: Event):
    args = ev.text.split()
    if len(args)<1:
        return await bot.send('请输入 选择初始地区+地点名称。', at_sender=True)
    go_map = args[0]
    uid = ev.user_id
    POKE = PokeCounter()
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
    my_hz = 0
    if this_map:
        return await bot.send(f'您已经处于{this_map}中，无法重选初始地区', at_sender=True)
    
    diqu_list = list(diqulist.keys())
    if go_map not in diqu_list:
        return await bot.send(f'地图上没有{go_map},请输入正确的地区名称', at_sender=True)
    if diqulist[go_map]['open'] == 1:
        go_didian = diqulist[go_map]['chushi']
        if ev.sender:
            sender = ev.sender
            name = sender['card'] or sender['nickname']
        else:
            name = uid
        POKE._new_map_info(uid, go_didian, name)
        await bot.send(f"您已成功选择初始地区{diqulist[go_map]['name']}\n当前所在地{go_didian}\n可输入[当前地点信息]查询", at_sender=True)
    else:
        return await bot.send(f"当前地区暂未开放请先前往其他地区冒险", at_sender=True)

@sv_pokemon_map.on_fullmatch(['当前地点信息'])
async def map_info_now(bot, ev: Event):
    gid = ev.group_id
    uid = ev.user_id
    POKE = PokeCounter()
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
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
    POKE = PokeCounter()
    mapinfo = POKE._get_map_now(uid)
    this_map = mapinfo[1]
    my_hz = 0
    if go_map == this_map:
        return await bot.send(f'您已经处于{this_map}中，无需前往', at_sender=True)
    list_dizhi = list(didianlist.keys())
    if go_map not in list_dizhi:
        return await bot.send(f'地图上没有{go_map},请输入正确的地址名称', at_sender=True)
    if didianlist[go_map]['fname'] == didianlist[this_map]['fname']:
        if int(my_hz) >= int(didianlist[go_map]['need']):
            POKE._add_map_now(uid, go_map)
            await bot.send(f'您已到达{go_map},当前地址信息可输入[当前地点信息]查询', at_sender=True)
        else:
            return await bot.send(f"前往{go_map}所需徽章为{str(didianlist[go_map]['need'])}枚,您的徽章为{str(my_hz)}枚,无法前往", at_sender=True)
    else:
        if int(my_hz) >= 8:
            await bot.send(f'您已到达{go_map},当前地址信息可输入[当前地点信息]查询', at_sender=True)
        else:
            return await bot.send(f"跨地区前往需要8枚徽章,您的徽章为{str(my_hz)}枚,无法前往", at_sender=True)




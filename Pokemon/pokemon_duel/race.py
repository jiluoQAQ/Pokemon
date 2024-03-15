import math
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.message_models import Button
import json
import pytz
import time
from .pokeconfg import *
from .until import *
from pathlib import Path
from datetime import datetime
from gsuid_core.gss import gss
from gsuid_core.logger import logger
from gsuid_core.aps import scheduler
from .pmconfig import *
sv_pokemon_race = SV('宝可梦比赛官方', pm=0)
sv_race_pokemon = SV('宝可梦比赛', priority=5)


@sv_pokemon_race.on_command(['开始赌狗大赛'])
async def start_race_dugou(bot, ev: Event):
    args = ev.text.split()
    pokename = args[0]
    eggnum = int(args[1])
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    #join_user = ['334249888','288978994','320341442','346271201','199611561','279781856','148108580','338562604','192456894','361002310','229921200','391721206','326779266','332008428','257959967']
    join_user = ['5755149']
    mes = '比赛开始！'
    for userid in join_user:
        mapinfo = await POKE._get_map_now(userid)
        egg_num = await POKE.get_pokemon_egg(userid, bianhao)
        await POKE.update_pokemon_egg_bianhao(userid, bianhao, eggnum)
        mes += f'\n参赛选手{mapinfo[2]}的{pokename}精灵蛋已由{egg_num}重置为{eggnum}'
    await bot.send(mes)

@sv_race_pokemon.on_command(['赌狗大赛排名'])
async def race_dugou_paiming(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send('请输入结算的宝可梦名称。', at_sender=True)
    pokename = args[0]
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    userliist = []
    pokemon_info_list = await POKE._get_pokemon_info_list(bianhao)
    if pokemon_info_list == 0:
        return await bot.send('这个宝可梦还没有人拥有哦~。', at_sender=True)
    join_user = ['334249888','288978994','320341442','346271201','199611561','279781856','148108580','338562604','192456894','361002310','229921200','391721206','326779266','332008428','257959967']
    mes = '比赛排名信息'
    userliist = []
    for userid in join_user:
        pokemon_info = await get_pokeon_info(userid, bianhao)
        userinfo = []
        if pokemon_info == 0:
            gt_z = 0
        else:
            gt_z = int(pokemon_info[1]) + int(pokemon_info[2]) + int(pokemon_info[3]) + int(pokemon_info[4]) + int(pokemon_info[5]) + int(pokemon_info[6])
        userinfo.append(userid)
        userinfo.append(gt_z)
        userliist.append(userinfo)
    userData = sorted(userliist,key=lambda cus:cus[1],reverse=True)
    shul = 1
    max_gt = userData[0][1]
    for detail in userData:
        if int(detail[1]) < int(max_gt):
            shul += 1
        mapinfo = await POKE._get_map_now(detail[0])
        mes += f'\n第{shul}名:{mapinfo[2]} 个体值:{detail[1]}'
    await bot.send(mes)

@sv_race_pokemon.on_command(['查看排名'])
async def race_dugou_paim(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send('请输入结算的宝可梦名称。', at_sender=True)
    pokename = args[0]
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    userliist = []
    pokemon_info_list = await POKE._get_pokemon_info_list(bianhao)
    if pokemon_info_list == 0:
        return await bot.send('这个宝可梦还没有人拥有哦~。', at_sender=True)
    mes = f'{pokename}排名(只显示前50名)'
    shul = 1
    for detail in pokemon_info_list:
        mapinfo = await POKE._get_map_now(detail[0])
        mes += f'\n第{shul}名:{mapinfo[2]} 个体值:{detail[1]}'
        shul += 1
    await bot.send(mes)

@sv_race_pokemon.on_command(['查看我的排名'])
async def race_dugou_paim(bot, ev: Event):
    uid = ev.user_id
    pokemon_info_list = await POKE._get_pokemon_info_list_pm(uid)
    if pokemon_info_list == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )
    mes = f'我的排名(只显示前50名)'
    shul = 1
    for detail in pokemon_info_list:
        mes += f'\n第{shul}名:{CHARA_NAME[detail[0]][0]} 个体值:{detail[1]}'
        shul += 1
    await bot.send(mes)
    
@sv_pokemon_race.on_command(['赌狗大赛结算'])
async def end_race_dugou(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send('请输入结算的宝可梦名称。', at_sender=True)
    pokename = args[0]
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    #join_user = ['334249888','288978994','320341442','346271201','199611561','279781856','148108580','338562604','192456894','361002310','229921200','391721206','326779266','332008428','257959967']
    join_user = ['5755149']
    max_gt = 0
    userliist = []
    for userid in join_user:
        userinfo = []
        pokemon_info = await get_pokeon_info(userid, bianhao)
        if pokemon_info == 0:
            gt_z = 0
        else:
            gt_z = int(pokemon_info[1]) + int(pokemon_info[2]) + int(pokemon_info[3]) + int(pokemon_info[4]) + int(pokemon_info[5]) + int(pokemon_info[6])
        userinfo.append(userid)
        userinfo.append(gt_z)
        userliist.append(userinfo)
        await POKE.update_pokemon_egg_bianhao(userid, bianhao, 0)
    userData = sorted(userliist,key=lambda cus:cus[1],reverse=True)
    mes = '比赛结束！现在公布排名'
    shul = 1
    max_gt = userData[0][1]
    for detail in userData:
        if int(detail[1]) < int(max_gt):
            shul += 1
        mapinfo = await POKE._get_map_now(detail[0])
        mes += f'\n第{shul}名:{mapinfo[2]} 个体值:{detail[1]}'
        if shul == 1:
            await SCORE.update_score(detail[0], 18888888)
            await POKE._add_pokemon_prop(detail[0], '神奇糖果', 888)
            mes += f'\n获得奖励金币18888888，神奇糖果888，指定精灵蛋888'
        elif shul == 2:
            await SCORE.update_score(detail[0], 8888888)
            await POKE._add_pokemon_prop(detail[0], '神奇糖果', 666)
            mes += f'\n获得奖励金币8888888，神奇糖果666，指定精灵蛋666'
        elif shul == 3:
            await SCORE.update_score(detail[0], 6666666)
            await POKE._add_pokemon_prop(detail[0], '神奇糖果', 333)
            mes += f'\n获得奖励金币6666666，神奇糖果333，指定精灵蛋333'
        else:
            await SCORE.update_score(detail[0], 666666)
            await POKE._add_pokemon_prop(detail[0], '神奇糖果', 66)
            mes += f'\n获得参与奖金币666666，神奇糖果66'
    mes += '\n固定奖励已发放完成，获得精灵蛋的冠亚季军请联系我领取需要的精灵\n比赛用精灵蛋已回收'
    await bot.send(mes)
import copy
import json
import math
import random
import pytz
import datetime
from pathlib import Path
from gsuid_core.sv import SV
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from .until import *
from .pokemon import *
from .pokeconfg import *
from ..utils.fonts.starrail_fonts import sr_font_20, sr_font_24
from .fightconfig import *

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
    weekbosslist = map_dict['weekbosslist']
    dungeonlist = map_dict['dungeon']

TEXT_PATH = Path(__file__).parent / 'texture2D'

sv_pokemon_pk = SV('宝可梦对战', priority=5)
sv_pokemon_tansuo = SV('宝可梦探索', priority=5)
@sv_pokemon_pk.on_fullmatch(['战斗帮助'])
async def fight_help(bot, ev: Event):
    msg = """
宝可梦战斗系统帮助
#指令：
1、挑战【道馆/天王/四天王冠军】:通过战胜【道馆/天王/四天王冠军】获得徽章称号，进一步解锁功能
2、训练家对战【昵称】:与昵称为【昵称】的训练家进行对战(自动战斗)
3、无级别对战【昵称】:与其他训练家进行一场无等级限制的手动对战
4、限制级对战【昵称】:与其他训练家进行一场等级限制为50的手动对战
5、首领列表：查看所有的首领信息与地点
6、首领信息：查看当前地点的首领信息
7、首领挑战：挑战该地点的首领，获胜可获得大量奖励
8、世界boss信息：查看当期世界boss信息
9、世界boss挑战：挑战世界boss获得奖励
10、世界boss伤害排名：查看世界boss伤害排名
11、匹配对战：与别的群的训练家对战
 """
    buttons = [
        Button('首领列表', '首领列表', '首领列表', action=1),
        Button('首领信息', '首领信息', '首领信息', action=1),
        Button('首领挑战', '首领挑战', '首领挑战', action=1),
        Button('世界boss挑战', '世界boss挑战', '世界boss挑战', action=1),
        Button('世界boss排名', '世界boss伤害排名', '世界boss排名', action=1),
        Button('训练家对战', '训练家对战', '训练家对战', action=2),
        Button('无级别对战', '无级别对战', '无级别对战', action=2),
        Button('限制级对战', '限制级对战', '限制级对战', action=2),
        Button('匹配对战', '匹配对战', '匹配对战', action=2),
    ]
    await bot.send_option(msg, buttons)

@sv_pokemon_tansuo.on_fullmatch(['挑战道馆'])
async def pk_vs_daoguan(bot, ev: Event):
    uid = ev.user_id

    mypokelist = await POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    if mapinfo[4] == 1:
        return await bot.send('正在自动探索中，无法挑战，请关闭自动探索后再试吧', at_sender=True)
    this_map = mapinfo[1]
    if this_map == '':
        return await bot.send('您还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = await POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(
            '您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)

    mapinfo = await POKE._get_map_now(uid)
    mychenghao, huizhang = await get_chenghao(uid)
    if int(mapinfo[0]) > 7:
        if int(mapinfo[0]) == 8:
            return await bot.send('您已通过8个道馆的挑战，可以去[挑战天王]了 ', at_sender=True)
        if int(mapinfo[0]) == 9:
            return await bot.send(
                f'您已经是【{mychenghao}】了，可以去[挑战四天王冠军]了，就不要拿小的开玩笑了',
                at_sender=True,
            )
        if int(mapinfo[0]) == 10:
            return await bot.send(
                f'尊敬的【{mychenghao}】，您莫非是在开玩笑吗', at_sender=True
            )
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']
    mes = ''
    name = str(name)[:10]

    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    diquname = didianlist[this_map]['fname']
    daoguaninfo = daoguanlist[diquname][str(huizhang)]

    # 对战
    chenghao = '道馆训练家'
    xingming = daoguaninfo['name']
    diname = chenghao + ' ' + xingming
    min_level = daoguaninfo['level'][0]
    max_level = daoguaninfo['level'][1]
    # pokenum = 3
    dipokelist = copy.deepcopy(daoguaninfo['pokemonlist'])
    mes += f'您向{diname}发起了道馆对战\n'

    my_image = (
        Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    )
    di_image = (
        Image.open(trainers_path / f'{xingming}.png')
        .convert('RGBA')
        .resize((120, 120))
    )
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
    (
        bg_img,
        bg_num,
        img_height,
        mes_list,
        mypokelist,
        dipokelist,
    ) = await fight_yw_ys_s(
        bg_img, bot, ev, uid, mypokelist, dipokelist, min_level, max_level
    )
    mes += mes_list
    if math.ceil((img_height + 130) / 1280) > bg_num:
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
    new_huizhang = int(huizhang)
    if len(dipokelist) == 0:
        mes += f'\n您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'您打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )

        new_huizhang = int(huizhang) + 1
        get_score = new_huizhang * 1000
        await SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您获得了1枚徽章'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        await POKE._update_map_huizhang(uid, new_huizhang)
        img_draw.text(
            (125, img_height + 100),
            '您获得了1枚徽章',
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
    if new_huizhang < 8:
        buttons = [
            Button('挑战道馆', '挑战道馆', '挑战道馆', action=1),
        ]
    else:
        buttons = [
            Button('挑战天王', '挑战天王', '挑战天王', action=1),
        ]
    await bot.send_option(img_bg, buttons)


@sv_pokemon_tansuo.on_fullmatch(['挑战天王'])
async def pk_vs_tianwang(bot, ev: Event):
    uid = ev.user_id

    mypokelist = await POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    if mapinfo[4] == 1:
        return await bot.send('正在自动探索中，无法挑战，请关闭自动探索后再试吧', at_sender=True)
    this_map = mapinfo[1]
    if this_map == '':
        return await bot.send('您还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = await POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(
            '您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)

    mapinfo = await POKE._get_map_now(uid)
    mychenghao, huizhang = await get_chenghao(uid)
    if int(mapinfo[0]) < 8:
        return await bot.send('请先挑战完8个道馆再向天王发起挑战哦', at_sender=True)
    if int(mapinfo[0]) > 8:
        if int(mapinfo[0]) == 9:
            return await bot.send(
                f'您已经是【{mychenghao}】了，可以去[挑战四天王冠军]了，就不要开玩笑了',
                at_sender=True,
            )
        if int(mapinfo[0]) == 10:
            return await bot.send(
                f'尊敬的【{mychenghao}】，您莫非是在开玩笑吗', at_sender=True
            )
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']
    mes = ''
    name = str(name)[:10]

    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'
    ranlist = [0, 1, 2, 3]
    tianwangid = int(random.sample(ranlist, 1)[0])

    diquname = didianlist[this_map]['fname']
    tianwanginfo = tianwanglist[diquname][tianwangid]

    # 对战
    chenghao = '天王训练家'
    xingming = tianwanginfo['name']
    diname = chenghao + ' ' + xingming
    min_level = tianwanginfo['level'][0]
    max_level = tianwanginfo['level'][1]
    # pokenum = 3
    dipokelist = copy.deepcopy(tianwanginfo['pokemonlist'])
    mes += f'您向{diname}发起了天王挑战\n'

    my_image = (
        Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    )
    di_image = (
        Image.open(trainers_path / f'{xingming}.png')
        .convert('RGBA')
        .resize((120, 120))
    )
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
    (
        bg_img,
        bg_num,
        img_height,
        mes_list,
        mypokelist,
        dipokelist,
    ) = await fight_yw_ys_s(
        bg_img, bot, ev, uid, mypokelist, dipokelist, min_level, max_level
    )
    mes += mes_list
    if math.ceil((img_height + 130) / 1280) > bg_num:
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
    new_huizhang = int(huizhang)
    if len(dipokelist) == 0:
        mes += f'\n您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'您打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )

        new_huizhang = int(mapinfo[0]) + 1
        get_score = new_huizhang * 1000
        await SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您成为了【天王训练家】'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        await POKE._update_map_huizhang(uid, new_huizhang)
        img_draw.text(
            (125, img_height + 100),
            '您成为了【天王训练家】',
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
    if new_huizhang == 8:
        buttons = [
            Button('重新挑战', '挑战天王', '重新挑战', action=1),
        ]
    else:
        buttons = [
            Button('挑战冠军', '挑战四天王冠军', '挑战冠军', action=1),
        ]
    await bot.send_option(img_bg, buttons)


@sv_pokemon_tansuo.on_fullmatch(['挑战四天王冠军'])
async def pk_vs_guanjun(bot, ev: Event):
    uid = ev.user_id

    mypokelist = await POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    if mapinfo[4] == 1:
        return await bot.send('正在自动探索中，无法挑战，请关闭自动探索后再试吧', at_sender=True)
    this_map = mapinfo[1]
    if this_map == '':
        return await bot.send('您还选择初始地区，请输入 选择初始地区+地区名称。', at_sender=True)
    my_team = await POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(
            '您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )
    pokemon_team = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_team:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)

    mapinfo = await POKE._get_map_now(uid)
    mychenghao, huizhang = await get_chenghao(uid)
    if int(mapinfo[0]) < 9:
        return await bot.send('请先成为【天王训练家】再向冠军发起挑战哦', at_sender=True)
    if int(mapinfo[0]) > 9:
        return await bot.send(f'您已经是【{mychenghao}】，就不要拿同事刷经验了', at_sender=True)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']
    mes = ''
    name = str(name)[:10]

    bg_img = Image.open(TEXT_PATH / 'duel_bg.jpg')
    vs_img = Image.open(TEXT_PATH / 'vs.png').convert('RGBA').resize((100, 89))
    bg_img.paste(vs_img, (300, 12), vs_img)
    trainers_path = TEXT_PATH / 'trainers'

    diquname = didianlist[this_map]['fname']
    guanjuninfo = guanjunlist[diquname]

    # 对战
    chenghao = '四天王冠军'
    xingming = guanjuninfo['name']
    diname = chenghao + ' ' + xingming
    min_level = guanjuninfo['level'][0]
    max_level = guanjuninfo['level'][1]
    # pokenum = 3
    dipokelist = copy.deepcopy(guanjuninfo['pokemonlist'])
    mes += f'您向{diname}发起了冠军挑战\n'

    my_image = (
        Image.open(trainers_path / '0.png').convert('RGBA').resize((120, 120))
    )
    di_image = (
        Image.open(trainers_path / f'{xingming}.png')
        .convert('RGBA')
        .resize((120, 120))
    )
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
    (
        bg_img,
        bg_num,
        img_height,
        mes_list,
        mypokelist,
        dipokelist,
    ) = await fight_yw_ys_s(
        bg_img, bot, ev, uid, mypokelist, dipokelist, min_level, max_level
    )
    mes += mes_list
    if math.ceil((img_height + 130) / 1280) > bg_num:
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
    new_huizhang = int(mapinfo[0])
    if len(dipokelist) == 0:
        mes += f'\n您打败了{diname}\n'
        img_draw.text(
            (125, img_height + 30),
            f'您打败了{diname}',
            black_color,
            sr_font_20,
            'lm',
        )

        new_huizhang = int(mapinfo[0]) + 1
        get_score = new_huizhang * 1000
        await SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您成为了【冠军训练家】'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        await POKE._update_map_huizhang(uid, new_huizhang)
        img_draw.text(
            (125, img_height + 100),
            '您成为了【冠军训练家】',
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
    if new_huizhang == 9:
        buttons = [
            Button('重新挑战', '挑战四天王冠军', '重新挑战', action=1),
        ]
    else:
        buttons = [
            Button('查看名片', '训练家名片', '查看名片', action=1),
        ]
    await bot.send_option(img_bg, buttons)


@sv_pokemon_pk.on_command(('无级别对战', '无级别战斗', '无级别挑战'))
async def pokemon_pk_wjb(bot, ev: Event):
    # if ev.bot_id == 'qqgroup':
    # return await bot.send('当前平台不支持无级别对战。', at_sender=True)
    uid = ev.user_id

    mapinfo = await POKE._get_map_now(uid)
    if mapinfo[4] == 1:
        return await bot.send('正在自动探索中，无法对战，请关闭自动探索后再试吧', at_sender=True)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']

    mypokelist = await POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            f'{name} 还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    if mapinfo[1] == '':
        return await bot.send(
            f'{name} 还选择初始地区，请输入 选择初始地区+地区名称。',
            at_sender=True,
        )
    my_team = await POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(
            f'{name} 还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )

    if ev.at is not None:
        diuid = ev.at
        dimapinfo = await POKE._get_map_now(diuid)
        if dimapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。',
                at_sender=True,
            )
        diname = dimapinfo[2]
    else:
        args = ev.text.split()
        if len(args) != 1:
            return await bot.send(
                '请输入 无级别对战+对战训练家昵称/at对战训练家。',
                at_sender=True,
            )
        nickname = args[0]
        dimapinfo = await POKE._get_map_info_nickname(nickname)
        if dimapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。',
                at_sender=True,
            )
        diuid = dimapinfo[2]
        diname = nickname
    if dimapinfo[4] == 1:
        return await bot.send(f'{nickname}正在自动探索中，无法对战，请关闭自动探索后再试吧', at_sender=True)
    dipokelist = await POKE._get_pokemon_list(diuid)
    if dipokelist == 0:
        return await bot.send(
            f'{diname} 还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    if dimapinfo[1] == '':
        return await bot.send(
            f'{diname} 还选择初始地区，请输入 选择初始地区+地区名称。',
            at_sender=True,
        )
    di_team = await POKE.get_pokemon_group(diuid)
    if my_team == '':
        return await bot.send(
            f'{diname} 还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )

    if name == diname:
        return await bot.send('不能自己打自己哦。', at_sender=True)

    xuanzeflag = 0
    rundinum = 0
    xuanzelist = ['接受对战', '拒绝对战']
    try:
        async with timeout(30):
            while xuanzeflag == 0:
                if rundinum == 0:
                    resp = await bot.receive_resp(
                        f'{name}向{diname}发起了无级别对战的邀请，请在30秒内选择接受/拒绝!',
                        xuanzelist,
                        unsuported_platform=True,
                        is_mutiply=True,
                    )
                    rundinum = 1
                    if resp is not None:
                        dis = resp.text
                        uiddi = resp.user_id
                        if str(uiddi) == str(diuid):
                            if dis in xuanzelist:
                                xuanze = dis
                                xuanzeflag = 1
                else:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        dis = resp.text
                        uiddi = resp.user_id
                        if str(uiddi) == str(diuid):
                            if dis in xuanzelist:
                                xuanze = dis
                                xuanzeflag = 1
    except asyncio.TimeoutError:
        xuanze = '拒绝对战'
    if xuanze == '拒绝对战':
        return await bot.send(f'{diname} 拒绝了您的无级别对战申请。', at_sender=True)
    await bot.send(f'{diname} 接受了您的无级别对战申请，即将开始对战。', at_sender=True)
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

    mychenghao, myhuizhang = await get_chenghao(uid)
    dichenghao, dihuizhang = await get_chenghao(diuid)

    name = str(name)[:10]
    diname = str(diname)[:10]
    # 对战
    mes = f'{mychenghao} {name}向{dichenghao} {diname}发起了挑战'
    await bot.send(mes)

    mypokelist, dipokelist = await fight_pk_s(
        bot, ev, uid, diuid, mypokelist, dipokelist, name, diname
    )

    if len(mypokelist) == 0:
        mes = f'{diname}打败了{name}，获得了对战的胜利'

    if len(dipokelist) == 0:
        mes = f'{name}打败了{diname}，获得了对战的胜利'
    await bot.send(mes)


@sv_pokemon_pk.on_command(('限制级对战', '限制级战斗', '限制级挑战'))
async def pokemon_pk_xzdj(bot, ev: Event):
    # if ev.bot_id == 'qqgroup':
    # return await bot.send('当前平台不支持无级别对战。', at_sender=True)
    uid = ev.user_id

    mapinfo = await POKE._get_map_now(uid)
    if mapinfo[4] == 1:
        return await bot.send('正在自动探索中，无法对战，请关闭自动探索后再试吧', at_sender=True)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']

    mypokelist = await POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            f'{name} 还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    if mapinfo[1] == '':
        return await bot.send(
            f'{name} 还选择初始地区，请输入 选择初始地区+地区名称。',
            at_sender=True,
        )
    my_team = await POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(
            f'{name} 还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )

    if ev.at is not None:
        diuid = ev.at
        dimapinfo = await POKE._get_map_now(diuid)
        if dimapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。',
                at_sender=True,
            )
        diname = dimapinfo[2]
    else:
        args = ev.text.split()
        if len(args) != 1:
            return await bot.send(
                '请输入 无级别对战+对战训练家昵称/at对战训练家。',
                at_sender=True,
            )
        nickname = args[0]
        dimapinfo = await POKE._get_map_info_nickname(nickname)
        if dimapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。',
                at_sender=True,
            )
        diuid = dimapinfo[2]
        diname = nickname
    if dimapinfo[4] == 1:
        return await bot.send(f'{nickname}正在自动探索中，无法对战，请关闭自动探索后再试吧', at_sender=True)
    dipokelist = await POKE._get_pokemon_list(diuid)
    if dipokelist == 0:
        return await bot.send(
            f'{diname} 还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    if dimapinfo[1] == '':
        return await bot.send(
            f'{diname} 还选择初始地区，请输入 选择初始地区+地区名称。',
            at_sender=True,
        )
    di_team = await POKE.get_pokemon_group(diuid)
    if my_team == '':
        return await bot.send(
            f'{diname} 还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',
            at_sender=True,
        )

    if name == diname:
        return await bot.send('不能自己打自己哦。', at_sender=True)

    xuanzeflag = 0
    rundinum = 0
    xuanzelist = ['接受对战', '拒绝对战']
    try:
        async with timeout(30):
            while xuanzeflag == 0:
                if rundinum == 0:
                    resp = await bot.receive_resp(
                        f'{name}向{diname}发起了限制级对战的邀请，请在30秒内选择接受/拒绝!',
                        xuanzelist,
                        unsuported_platform=True,
                        is_mutiply=True,
                    )
                    rundinum = 1
                    if resp is not None:
                        dis = resp.text
                        uiddi = resp.user_id
                        if str(uiddi) == str(diuid):
                            if dis in xuanzelist:
                                xuanze = dis
                                xuanzeflag = 1
                else:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        dis = resp.text
                        uiddi = resp.user_id
                        if str(uiddi) == str(diuid):
                            if dis in xuanzelist:
                                xuanze = dis
                                xuanzeflag = 1
    except asyncio.TimeoutError:
        xuanze = '拒绝对战'
    if xuanze == '拒绝对战':
        return await bot.send(f'{diname} 拒绝了您的限制级对战申请。', at_sender=True)
    await bot.send(f'{diname} 接受了您的限制级对战申请，即将开始对战。', at_sender=True)

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

    mychenghao, myhuizhang = await get_chenghao(uid)
    dichenghao, dihuizhang = await get_chenghao(diuid)

    name = str(name)[:10]
    diname = str(diname)[:10]
    # 对战
    mes = f'{mychenghao} {name}向{dichenghao} {diname}发起了挑战'
    await bot.send(mes)

    mypokelist, dipokelist = await fight_pk_s(
        bot, ev, uid, diuid, mypokelist, dipokelist, name, diname, 50
    )

    if len(mypokelist) == 0:
        mes = f'{diname}打败了{name}，获得了对战的胜利'

    if len(dipokelist) == 0:
        mes = f'{name}打败了{diname}，获得了对战的胜利'
    await bot.send(mes)

@sv_pokemon_pk.on_fullmatch(('boss列表', '首领列表'))
async def pokemon_pk_boss_list(bot, ev: Event):
    mes = ''
    for diquname in weekbosslist:
        for didianname in weekbosslist[diquname]:
            mes += f"首领名称：{POKEMON_LIST[weekbosslist[diquname][didianname]['bossid']][0]}\n"
            mes += f"出没地点：{diquname}-{didianname}\n"
    buttons = [
        Button('前往', '前往', '前往', action=2),
    ]
    await bot.send_option(mes, buttons)
    
@sv_pokemon_pk.on_fullmatch(('boss信息', '周本boss信息', '首领信息'))
async def pokemon_pk_boss_week_info(bot, ev: Event):
    uid = ev.user_id
    mypoke = await POKE._get_pokemon_list(uid)
    if mypoke == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    this_map = mapinfo[1]
    diquname = didianlist[this_map]['fname']
    bosslist_diqu = list(weekbosslist.keys())
    if diquname not in bosslist_diqu:
        return await bot.send(
            f'当前地区暂时没有出现boss，清前往其他地区进行挑战', at_sender=True
        )
    bosslist_didian = list(weekbosslist[diquname].keys())
    if this_map not in bosslist_didian:
        return await bot.send(
            f'当前地点暂时没有出现boss，清前往其他地点进行挑战', at_sender=True
        )
    bossinfo = weekbosslist[diquname][this_map]
    bossbianhao = bossinfo['bossid']
    pokemon_info_boss = await get_pokeon_info_boss(bossbianhao, bossinfo, 100)
    HP_1, W_atk_1, W_def_1, M_atk_1, M_def_1, speed_1 = await get_pokemon_shuxing_boss(
        bossbianhao, pokemon_info_boss, 1.2
    )
    HP_2, W_atk_2, W_def_2, M_atk_2, M_def_2, speed_2 = await get_pokemon_shuxing_boss(
        bossbianhao, pokemon_info_boss, 1.5
    )
    HP_3, W_atk_3, W_def_3, M_atk_3, M_def_3, speed_3 = await get_pokemon_shuxing_boss(
        bossbianhao, pokemon_info_boss, 1.8
    )
    mes = f"boss信息\n名称:{POKEMON_LIST[bossinfo['bossid']][0]}\n等级:{pokemon_info_boss[0]}\n各阶段属性\n血量:{HP_1}-{HP_2}-{HP_3}\n物攻:{W_atk_1}-{W_atk_2}-{W_atk_3}\n物防:{W_def_1}-{W_def_2}-{W_def_3}\n特攻:{M_atk_1}-{M_atk_2}-{M_atk_3}\n特防:{M_def_1}-{M_def_2}-{M_def_3}\n速度:{speed_1}-{speed_2}-{speed_3}"
    buttons = [
        Button('首领挑战', '首领挑战', '首领挑战', action=1),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_pk.on_fullmatch(('boss挑战', '周本boss挑战', '首领挑战'))
async def pokemon_pk_boss_week(bot, ev: Event):
    uid = ev.user_id
    mypoke = await POKE._get_pokemon_list(uid)
    if mypoke == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    name = mapinfo[2]
    this_map = mapinfo[1]
    if not daily_boss.check_week(uid):
        await bot.send(
            '本周的挑战次数已经超过上限了哦，本次挑战无法获得奖励。', at_sender=True
        )
    diquname = didianlist[this_map]['fname']
    bosslist_diqu = list(weekbosslist.keys())
    if diquname not in bosslist_diqu:
        return await bot.send(
            f'当前地区暂时没有出现boss，清前往其他地区进行挑战', at_sender=True
        )
    bosslist_didian = list(weekbosslist[diquname].keys())
    if this_map not in bosslist_didian:
        return await bot.send(
            f'当前地点暂时没有出现boss，清前往其他地点进行挑战', at_sender=True
        )
    bossinfo = weekbosslist[diquname][this_map]
    bossbianhao = bossinfo['bossid']
    my_team = await POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    my_max_level = 0
    mypokelist = []
    for bianhao in pokemon_list:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
        pokemon_info = await get_pokeon_info(uid, bianhao)
        if pokemon_info[0] > my_max_level:
            my_max_level = pokemon_info[0]
    boss_level = min(100, my_max_level+5)
    boss_level = max(40, boss_level)
    mes = f"【首领】{POKEMON_LIST[bossinfo['bossid']][0]}进入了战斗"
    await bot.send(mes)
    name = str(name)[:10]
    dipokelist = [bossbianhao,bossbianhao,bossbianhao]
    mypokelist, dipokelist = await fight_boss(bot, ev, uid, mypokelist, dipokelist, boss_level, name, bossinfo)
    
    if len(mypokelist) == 0:
        mes = f"您被【首领】{POKEMON_LIST[bossinfo['bossid']][0]}击败了,眼前一黑"
    
    if len(dipokelist) == 0:
        mes = f"您打败了【首领】{POKEMON_LIST[bossinfo['bossid']][0]}\n"
        if daily_boss.check_week(uid):
            catch_flag = await catch_pokemon(bot, ev, uid, bossbianhao)
            if catch_flag == 1:
                eggid = await get_pokemon_eggid(bossbianhao)
                mes += f'您获得了{CHARA_NAME[eggid][0]}精灵蛋x1\n'
                await POKE._add_pokemon_egg(uid, eggid, 1)
            beilv = math.ceil((boss_level - 40)/20)
            get_score = BOSS_GOLD * beilv
            await SCORE.update_score(uid, get_score)
            mes += f'您获得了{get_score}金钱\n'
            get_tangguo = BOSS_TG * beilv
            await POKE._add_pokemon_prop(uid, "神奇糖果", get_tangguo)
            mes += f'您获得了神奇糖果x{get_tangguo}\n'
            jswg_num = int(math.floor(random.uniform(0, 100)))
            if jswg_num <= BOSS_WGJ * beilv:
                await POKE._add_pokemon_prop(uid, "金色王冠", 1)
                mes += f'您获得了金色王冠x1\n'
            yswg_num = int(math.floor(random.uniform(0, 100)))
            if yswg_num <= BOSS_WGY * beilv:
                await POKE._add_pokemon_prop(uid, "银色王冠", 1)
                mes += f'您获得了银色王冠x1\n'
            get_gold = BOSS_SCORE * beilv
            await SCORE.update_shengwang(uid, get_gold)
            mes += f'您获得了{get_gold}首领币'
            daily_boss.increase(uid)
    await bot.send(mes)

@sv_pokemon_pk.on_fullmatch(('世界boss信息'))
async def pokemon_pk_boss_week_info(bot, ev: Event):
    uid = ev.user_id
    tz = pytz.timezone('Asia/Shanghai')
    current_date = datetime.datetime.now(tz)
    this_year, this_week, _ = current_date.isocalendar()
    week = int(str(this_year) + str(this_week))
    bossinfo = sjbossinfo[str(week)]
    bossbianhao = bossinfo['bossid']
    pokemon_info_boss = await get_pokeon_info_boss(bossbianhao, bossinfo, 100)
    HP_1, W_atk_1, W_def_1, M_atk_1, M_def_1, speed_1 = await get_pokemon_shuxing_boss_sj(
        bossbianhao, pokemon_info_boss, 1.1
    )
    HP_2, W_atk_2, W_def_2, M_atk_2, M_def_2, speed_2 = await get_pokemon_shuxing_boss_sj(
        bossbianhao, pokemon_info_boss, 1.2
    )
    HP_3, W_atk_3, W_def_3, M_atk_3, M_def_3, speed_3 = await get_pokemon_shuxing_boss_sj(
        bossbianhao, pokemon_info_boss, 1.4
    )
    mes = f"boss信息\n名称:{POKEMON_LIST[bossinfo['bossid']][0]}\n等级:{pokemon_info_boss[0]}\n性格:{pokemon_info_boss[13]}\n技能:{pokemon_info_boss[14]}\n前三阶段属性\n血量:{HP_1}-{HP_2}-{HP_3}\n物攻:{W_atk_1}-{W_atk_2}-{W_atk_3}\n物防:{W_def_1}-{W_def_2}-{W_def_3}\n特攻:{M_atk_1}-{M_atk_2}-{M_atk_3}\n特防:{M_def_1}-{M_def_2}-{M_def_3}\n速度:{speed_1}-{speed_2}-{speed_3}\n"
    mes += f"世界boss奖励：\n伤害超过35000，奖励随机异兽或悖谬精灵蛋\n伤害超过45000，奖励当期世界boss蛋\n伤害每超过5000，奖励20万金币+15糖果"
    buttons = [
        Button('世界boss挑战', '世界boss挑战', '世界boss挑战', action=1),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_pk.on_fullmatch(('世界boss挑战', '世界首领挑战'))
async def pokemon_pk_boss_sj(bot, ev: Event):
    uid = ev.user_id
    mypoke = await POKE._get_pokemon_list(uid)
    if mypoke == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    name = mapinfo[2]
    this_map = mapinfo[1]
    tz = pytz.timezone('Asia/Shanghai')
    current_date = datetime.datetime.now(tz)
    this_year, this_week, _ = current_date.isocalendar()
    week = int(str(this_year) + str(this_week))
    bossinfo = sjbossinfo[str(week)]
    bossbianhao = bossinfo['bossid']
    my_team = await POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    my_max_level = 0
    mypokelist = []
    for bianhao in pokemon_list:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
    mes = f"【世界首领】{POKEMON_LIST[bossinfo['bossid']][0]}进入了战斗"
    await bot.send(mes)
    name = str(name)[:10]
    shanghai = await fight_boss_sj(bot, ev, uid, mypokelist, name, bossinfo)
    
    old_shanghai = await POKE.get_boss_shanghai(uid, week)
    mes = f"【世界首领】挑战完成，本次造成伤害{shanghai}"
    if int(shanghai) > int(old_shanghai):
        await POKE._new_boss_shanghai(uid, shanghai, week)
        if shanghai >= 5000:
            new_num = int(shanghai/5000)
            old_num = int(old_shanghai/5000)
            get_num = new_num - old_num
            if get_num > 0:
                get_score = 200000 * get_num
                get_tangguo = 15 * get_num
                await SCORE.update_score(uid, get_score)
                await POKE._add_pokemon_prop(uid, "神奇糖果", get_tangguo)
                mes += f"\n获得了金币x{get_score}"
                mes += f"\n获得了神奇糖果x{get_tangguo}"
        if shanghai >= 35000 and old_shanghai < 35000:
            get_poke_id = random.sample(boss_poke_get_list, 1)[0]
            await POKE._add_pokemon_egg(uid, get_poke_id, 1)
            mes += f"\n获得了{CHARA_NAME[get_poke_id][0]}精灵蛋x1"
        if shanghai >= 45000 and old_shanghai < 45000:
            get_egg_id = await get_pokemon_eggid(int(bossinfo['bossid']))
            await POKE._add_pokemon_egg(uid, get_egg_id, 1)
            mes += f"\n获得了{CHARA_NAME[get_egg_id][0]}精灵蛋x1"
        old_shanghai = shanghai
    mes += f"\n本周最高伤害{old_shanghai}"
    buttons = [
        Button('本周伤害排名', '世界boss伤害排名', '本周伤害排名', action=1),
        Button('上周伤害排名', '世界boss伤害排名上周', '上周伤害排名', action=1),
        Button('再次挑战', '世界boss挑战', '再次挑战', action=1),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_pk.on_fullmatch(('挑战试炼塔', '挑战精灵塔'))
async def pokemon_pk_dungeon(bot, ev: Event):
    uid = ev.user_id
    mypoke = await POKE._get_pokemon_list(uid)
    if mypoke == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )
    mapinfo = await POKE._get_map_now(uid)
    name = mapinfo[2]
    my_dungeon_num = await POKE.get_dungeon_info(uid)
    if my_dungeon_num >= dungeon_max_num:
        return await bot.send('您已经通过最高难度的精灵塔了，等之后再来挑战吧', at_sender=True,)
    my_team = await POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    mypokelist = []
    for bianhao in pokemon_list:
        bianhao = int(bianhao)
        mypokelist.append(bianhao)
    dungeon_str = str(my_dungeon_num + 1)
    dungeoninfo = dungeonlist[dungeon_str]
    dungeonpoke = dungeoninfo['pokelist']
    dungeonlevel = dungeoninfo['pokelevel']
    dipokelist = []
    for pokeid in dungeonpoke:
        dipokelist.append(int(pokeid))
    await bot.send(f"您开始了试炼塔第{dungeon_str}层的挑战")
    mypokelist, dipokelist = await fight_dungeon(bot, ev, uid, mypokelist, dipokelist, dungeonlevel, name, dungeonpoke)
    if len(mypokelist) == 0:
        mes = f"您挑战试炼塔第{dungeon_str}层挑战失败"
    
    if len(dipokelist) == 0:
        mes = f"您通过了试炼塔第{dungeon_str}层的挑战\n"
        await POKE.update_dungeon(uid,int(dungeon_str))
        addscore = dungeoninfo['firstreward']['score']
        await SCORE.update_score(uid, addscore)
        mes += f"您获得了奖励\n金币+{addscore}"
        for reward in dungeoninfo['firstreward']['prop']:
            mes += f"\n{reward['name']}+{reward['num']}"
            await POKE._add_pokemon_prop(uid, reward['name'], reward['num'])
    buttons = [
        Button('挑战下一层', '挑战精灵塔', '挑战下一层', action=1),
        Button('扫荡最高层', '扫荡精灵塔', '扫荡最高层', action=1),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_pk.on_fullmatch(('扫荡试炼塔', '扫荡精灵塔'))
async def pokemon_sd_dungeon(bot, ev: Event):
    uid = ev.user_id
    mypoke = await POKE._get_pokemon_list(uid)
    if mypoke == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )
    if not daily_dungeon.check(uid):
        return await bot.send(
            '今天的试炼塔扫荡次数已经超过上限了哦，明天再来吧。', at_sender=True
        )
    mapinfo = await POKE._get_map_now(uid)
    name = mapinfo[2]
    my_dungeon_num = await POKE.get_dungeon_info(uid)
    if my_dungeon_num == 0:
        return await bot.send(
            '您还没有通过试炼塔的挑战哦，请挑战成功后再来扫荡吧', at_sender=True
        )
    dungeon_str = str(my_dungeon_num)
    dungeoninfo = dungeonlist[dungeon_str]
    mes = f"试炼塔{dungeon_str}层扫荡成功！"
    addscore = dungeoninfo['reward']['score']
    await SCORE.update_score(uid, addscore)
    mes += f"\n您获得了奖励\n金币+{addscore}"
    daily_dungeon.increase(uid)
    for reward in dungeoninfo['reward']['prop']:
        mes += f"\n{reward['name']}+{reward['num']}"
        await POKE._add_pokemon_prop(uid, reward['name'], reward['num'])
    await bot.send(mes)

@sv_pokemon_pk.on_fullmatch(('试炼塔排名', '精灵塔排名'))
async def pokemon_dungeon_paiming(bot, ev: Event):
    uid = ev.user_id
    dungeon_list = await POKE.get_dungeon_list()
    if dungeon_list == 0:
        return bot.send('目前还没有人挑战过精灵塔哦')
    mesg = "精灵塔排名（只显示前30名）"
    for detail in dungeon_list:
        mapinfo = await POKE._get_map_now(detail[0])
        name = mapinfo[2]
        mesg += f'\n{name} 已通过{detail[1]}层'
    await bot.send(mesg)

@sv_pokemon_pk.on_command(('世界boss伤害排名'))
async def pokemon_pk_boss_sj_paiming(bot, ev: Event):
    args = ev.text.split()
    if len(args) == 1:
        week_key = args[0]
    else:
        week_key = '本周'
    tz = pytz.timezone('Asia/Shanghai')
    current_date = datetime.datetime.now(tz)
    this_year, this_week, _ = current_date.isocalendar()
    if week_key == '上周':
        current_date = current_date.date()
        # 获取上周的日期
        last_week = current_date - datetime.timedelta(days=7)
         
        # 获取上周的年份和周数
        previous_year, previous_week, _ = last_week.isocalendar()
        week = int(str(previous_year) + str(previous_week))
    else:
        week = int(str(this_year) + str(this_week))
    shanghai_list = await POKE.get_boss_shanghai_list(week)
    if shanghai_list == 0:
        return await bot.send(f'{week_key}还没有训练家挑战世界boss')
    bossinfo = sjbossinfo[str(week)]
    mes = f"{week_key}世界boss伤害排名【{POKEMON_LIST[bossinfo['bossid']][0]}】(只显示前50名)"
    for detail in shanghai_list:
        mapinfo = await POKE._get_map_now(detail[0])
        mes += f'\n{mapinfo[2]} 伤害：{detail[1]}'
    
    buttons = [
        Button('本周伤害排名', '世界boss伤害排名', '本周伤害排名', action=1),
        Button('上周伤害排名', '世界boss伤害排名上周', '上周伤害排名', action=1),
        Button('世界boss信息', '世界boss信息', '世界boss信息', action=1),
        Button('再次挑战', '世界boss挑战', '再次挑战', action=1),
    ]
    await bot.send_option(mes, buttons)
    
@sv_pokemon_pk.on_command(('匹配对战'))
async def pokemon_pk_pipei(bot, ev: Event):
    uid = ev.user_id
    my_team = await POKE.get_pokemon_group(uid)
    if my_team == '':
        return await bot.send(f'您还没有创建队伍，请输入 创建队伍+宝可梦名称(中间用空格分隔)。',at_sender=True)
    pipeiinfo = await POKE.get_pipei_info(uid)
    if pipeiinfo != 0:
        if pipeiinfo[0] == 0:
            return await bot.send('您已经处于匹配状态')
    pipeilist = await POKE.get_pipei_list(uid)
    fight_falg = 0
    mymapinfo = await POKE._get_map_now(uid)
    mypipeinum = mymapinfo[3]
    uidlist = []
    if pipeilist != 0:
        for uidinfo in pipeilist:
            dimap = await POKE._get_map_now(uidinfo[0])
            pipei_cb = int(mypipeinum) - int(dimap[3])
            if pipei_cb < 250 and pipei_cb > -250:
                uidlist.append(uidinfo[0])
    if len(uidlist) > 0:
        await bot.send('开始匹配中，匹配时间30秒')  
        diuid = random.sample(uidlist, 1)[0]
        string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        random_list = random.sample(list(string), 8)
        fightid = ''.join(random_list)
        await POKE.update_pipei_flag(diuid,uid,fightid)
        await POKE.update_pipei_flag(uid,diuid,fightid)
        fight_falg = 1
    else:
        await bot.send('开始匹配中，匹配时间60秒')  
        await POKE._new_pipei_info(uid)
        fight_falg = 0
    
    if fight_falg == 0:
        try:
            async with timeout(60):
                while fight_falg == 0:
                    pipeiinfo = await POKE.get_pipei_info(uid)
                    if pipeiinfo[0] != 0:
                        fightid = pipeiinfo[1]
                        diuid = pipeiinfo[2]
                        fight_falg = 1
                    await asyncio.sleep(.5)
        except asyncio.TimeoutError:
            fight_falg = 3
            await POKE.delete_pipei_uid(uid)
            return await bot.send('匹配超时，匹配失败') 
                
    pipeiinfo = await POKE.get_pipei_info(uid)
    fightid = pipeiinfo[1]
    changdi = [['无天气', 99], ['', 0]]
    await FIGHT.new_fight(fightid, changdi)
    if fight_falg == 1:
        dimapinfo = await POKE._get_map_now(diuid)
        name = mymapinfo[2]
        diname = dimapinfo[2]
        myduanwei = await get_now_duanwei(mypipeinum)
        diduanwei = await get_now_duanwei(dimapinfo[3])
        xuanzelistname = ['同意对战', '取消对战']
        button_user_input_my = []
        button_user_input_my.append(uid)
        xuanzelist = [
            Button('同意对战', '同意对战', '同意对战', action=1, permisson=0, specify_user_ids=button_user_input_my),
            Button('取消对战', '取消对战', '取消对战', action=1, permisson=0, specify_user_ids=button_user_input_my),
        ]
        xuanzeflag = 0
        rundinum = 0
        try:
            async with timeout(30):
                while xuanzeflag == 0:
                    if rundinum == 0:
                        resp = await bot.receive_resp(
                            f'匹配成功，您的对手为{diname}({diduanwei})，请在30秒内选择同意/取消!',
                            xuanzelist,
                            unsuported_platform=True,
                            is_mutiply=True,
                        )
                        rundinum = 1
                        if resp is not None:
                            resps = resp.text
                            respuid = resp.user_id
                            if str(respuid) == str(uid):
                                if resps in xuanzelistname:
                                    xuanze = resps
                                    xuanzeflag = 1
                    else:
                        resp = await bot.receive_mutiply_resp()
                        if resp is not None:
                            resps = resp.text
                            respuid = resp.user_id
                            if str(respuid) == str(uid):
                                if resps in xuanzelistname:
                                    xuanze = resps
                                    xuanzeflag = 1
        except asyncio.TimeoutError:
            xuanze = '取消对战'
            
        if xuanze == '取消对战':
            await POKE.update_pipei_fight(uid,-1)
            return await bot.send('您取消了对战')
        
        if xuanze == '同意对战':
            await FIGHT.new_fight_uid(fightid, uid)
            await POKE.update_pipei_fight(uid,1)
            await bot.send('您同意了对战，等待对手确认中')
        
        start_flag = 0
        try:
            async with timeout(30):
                while start_flag == 0:
                    pipeiinfodi = await POKE.get_pipei_info(diuid)
                    if pipeiinfodi[3] != 0:
                        start_flag = pipeiinfodi[3]
                    await asyncio.sleep(.5)
        except asyncio.TimeoutError:
            start_flag = -1
        
        if start_flag == -1:
            await POKE.delete_pipei_uid(uid)
            await POKE.delete_pipei_uid(diuid)
            return await bot.send('对手取消了对战')
        
        if start_flag == 1:
            pokemon_team = my_team.split(',')
            mypokelist = []
            for bianhao in pokemon_team:
                bianhao = int(bianhao)
                mypokelist.append(bianhao)
            
            di_team = await POKE.get_pokemon_group(diuid)
            di_pokemon_team = di_team.split(',')
            dipokelist = []
            for bianhao in di_pokemon_team:
                bianhao = int(bianhao)
                dipokelist.append(bianhao)
            mypokelist, dipokelist, mes = await fight_pk_pipei(bot, ev, uid, diuid, mypokelist, dipokelist, name, diname, fightid)
            mypokenum = len(mypokelist)
            dipokenum = len(dipokelist)
            if str(myduanwei) == str(diduanwei):
                add_pipei_num = 20
            else:
                if mymapinfo[3] > dimapinfo[3]:
                    add_pipei_num = 15
                else:
                    add_pipei_num = 25
            if mypokenum == 0 and dipokenum == 0:
                mes += "\n双方同时失去战斗能力，平局"
            if mypokenum > 0 and dipokenum == 0:
                await POKE.update_map_pipei_num(uid,add_pipei_num)
                mes += f"\n{name}战胜了{diname}\n您获得了赛季积分{add_pipei_num}"
            if mypokenum == 0 and dipokenum > 0:
                await POKE.update_map_pipei_num(uid,0-add_pipei_num)
                mes += f"\n{diname}战胜了{name}\n您失去了赛季积分{add_pipei_num}"
            await POKE.delete_pipei_uid(uid)
            await POKE.delete_pipei_uid(diuid)
            await bot.send(mes)
            

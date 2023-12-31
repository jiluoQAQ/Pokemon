import copy
import json
import math
import random
from pathlib import Path

from gsuid_core.sv import SV
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from .until import *
from .pokemon import *
from .pokeconfg import *
from .PokeCounter import *
from ..utils.fonts.starrail_fonts import sr_font_20, sr_font_24

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

    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    mapinfo = POKE._get_map_now(uid)
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

    mapinfo = POKE._get_map_now(uid)
    mychenghao, huizhang = get_chenghao(uid)
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
    name = name[:10]

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
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您获得了1枚徽章'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        POKE._update_map_huizhang(uid, new_huizhang)
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
    await bot.send(mes)


@sv_pokemon_pk.on_fullmatch(['挑战天王'])
async def pk_vs_tianwang(bot, ev: Event):
    uid = ev.user_id

    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    mapinfo = POKE._get_map_now(uid)
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

    mapinfo = POKE._get_map_now(uid)
    mychenghao, huizhang = get_chenghao(uid)
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
    name = name[:10]

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
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您成为了【天王训练家】'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        POKE._update_map_huizhang(uid, new_huizhang)
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
    await bot.send(mes)


@sv_pokemon_pk.on_fullmatch(['挑战四天王冠军'])
async def pk_vs_guanjun(bot, ev: Event):
    uid = ev.user_id

    mypokelist = POKE._get_pokemon_list(uid)
    if mypokelist == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。\n初始精灵列表可输入[初始精灵列表]查询',
            at_sender=True,
        )
    mapinfo = POKE._get_map_now(uid)
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

    mapinfo = POKE._get_map_now(uid)
    mychenghao, huizhang = get_chenghao(uid)
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
    name = name[:10]

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
        SCORE.update_score(uid, get_score)
        mes += f'您获得了{get_score}金钱\n您成为了【冠军训练家】'
        img_draw.text(
            (125, img_height + 65),
            f'您获得了{get_score}金钱',
            black_color,
            sr_font_20,
            'lm',
        )
        POKE._update_map_huizhang(uid, new_huizhang)
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
    await bot.send(mes)


@sv_pokemon_pk.on_command(('无级别对战', '无级别战斗', '无级别挑战'))
async def pokemon_pk_wjb(bot, ev: Event):
    # if ev.bot_id == 'qqgroup':
    # return await bot.send('当前平台不支持无级别对战。', at_sender=True)
    uid = ev.user_id

    mapinfo = POKE._get_map_now(uid)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']

    mypokelist = POKE._get_pokemon_list(uid)
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
        dimapinfo = POKE._get_map_now(diuid)
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
        dimapinfo = POKE._get_map_info_nickname(nickname)
        if dimapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。',
                at_sender=True,
            )
        diuid = dimapinfo[2]
        diname = nickname

    dipokelist = POKE._get_pokemon_list(diuid)
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

    mychenghao, myhuizhang = get_chenghao(uid)
    dichenghao, dihuizhang = get_chenghao(diuid)

    name = name[:10]
    diname = diname[:10]
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

    mapinfo = POKE._get_map_now(uid)
    name = mapinfo[2]
    if name == uid:
        if ev.sender:
            sender = ev.sender
            if sender.get('nickname', '') != '':
                name = sender['nickname']

    mypokelist = POKE._get_pokemon_list(uid)
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
        dimapinfo = POKE._get_map_now(diuid)
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
        dimapinfo = POKE._get_map_info_nickname(nickname)
        if dimapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的对战训练家昵称或at该名训练家。',
                at_sender=True,
            )
        diuid = dimapinfo[2]
        diname = nickname

    dipokelist = POKE._get_pokemon_list(diuid)
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

    mychenghao, myhuizhang = get_chenghao(uid)
    dichenghao, dihuizhang = get_chenghao(diuid)

    name = name[:10]
    diname = diname[:10]
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

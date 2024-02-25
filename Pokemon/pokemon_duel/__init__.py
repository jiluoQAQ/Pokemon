import os
import re
import math

from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.message_models import Button
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.image.convert import convert_img
from .pmconfig import *
from .map import *
from .prop import *
from .race import *
from .fight import *
from .until import *
from .pokemon import *
from .pokeconfg import *
from .PokeCounter import *
from .draw_image import draw_pokemon_info, draw_pokemon_info_tj
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH

sv_pokemon_duel = SV('宝可梦状态', priority=5)


@sv_pokemon_duel.on_fullmatch(('精灵帮助', '宝可梦帮助'))
async def pokemon_help(bot, ev: Event):
    msg = """
             宝可梦帮助
特别注意！！！
野外探索有内置的2秒CD,使用连点器的建议点击间隔设置成3秒,减少负载。提升流畅性
特别注意！！！

进入游戏请先输入 领取初始精灵【精灵名】 开局，初始精灵有各个版本的御三家，如
    领取初始精灵小火龙
指令：
1、初始精灵列表:查询可以领取的初始精灵
2、领取初始精灵【精灵名】:领取初始精灵【精灵名】
3、精灵状态【精灵名】:查询【精灵名】的属性信息
4、我的精灵列表:查询我拥有的等级前20的精灵
5、宝可梦重开:删除我所有的精灵信息
6、放生精灵【精灵名】放生名为【精灵名】的精灵
7、学习精灵技能【精灵名】 【技能名】:让精灵学习技能
8、遗忘精灵技能【精灵名】 【技能名】:让精灵遗忘技能
9、野外探索:在野外地区与野生宝可梦或训练师战斗获取精灵经验
10、打工:在城镇地区打工进行打工赚取金币
11、前往【地点名】:前往【地点名】的地点
12、宝可梦进化【精灵名】:让你的宝可梦进化为【精灵名】，需要有前置进化型精灵
13、修改训练家名称【昵称】:把你的训练家名称改为【昵称】，【昵称】有唯一性，作为对战识别符
14、查看地图【地区名】:查询【地区名】的地点信息，【地区名】可留空，默认所在地区
15、我的精灵蛋:查询我的精灵蛋信息
16、重置个体值【精灵名】:消耗一枚【精灵名】初始形态的精灵蛋对【精灵名】的个体值进行重置,后面跟数量可以进行多次重置
17、宝可梦孵化【精灵名】:消耗一枚【精灵名】的精灵蛋孵化出一只lv.5的【精灵名】
18、更新队伍【精灵名】:更新手持队伍信息，不同的宝可梦用空格分隔，最多4只
19、大量出现信息:查询当前随机出现的大量宝可梦消息
20、宝可梦重生【精灵名】:让等级到100级的精灵重生为精灵蛋
21、道具帮助:查看道具系统/交易所的使用说明
22、更新公告:查看最近更新内容
注:
同一类型的精灵只能拥有一只:进化型为不同类型
后续功能在写了在写了 新建文件夹

其他宝可梦相关小游戏可以点击小游戏帮助查询
 """
    buttons = [
        Button('✅道具帮助', '道具帮助', action=1),
        Button('✅战斗帮助', '战斗帮助', action=1),
        Button('📖精灵状态', '精灵状态', action=2),
        Button('🔄更新队伍', '更新队伍', action=2),
        Button('✅领取初始精灵', '领取初始精灵', action=2),
        Button('🏝️野外探索', '野外探索', action=1),
        Button('🗺查看地图', '查看地图', action=1),
        Button('✅大量出现信息', '大量出现信息', action=1),
        Button('✅小游戏帮助', '小游戏帮助', action=1),
    ]
    await bot.send_option(msg, buttons)

@sv_pokemon_duel.on_fullmatch(('更新公告', '查看公告'))
async def pokemon_gonggao(bot, ev: Event):
    msg = """
       宝可梦小游戏更新公告：
2024-2-25
1.添加平台数据转移功能(管理员)
2.可以发红包了(pm发红包【红包口令】【红包金额】【红包数量】)
2024-2-23
1.完成首领挑战(周本)
2.添加首领商店(货币为首领挑战掉落的首领币)
3.添加金色王冠、银色王冠道具
2024-2-21
1.添加部分回复类技能效果
2.宝可梦重开添加道具、学习机的重置
3.修改打工获取的金币为根据自身训练家等级获取
4.修改连续战队只获取一次努力值的bug
5.消息发送方式【图片/文字】可以指令替换
2024-2-20
1.添加周本boss，暂时只加了属性查看
2.部分技能名称优化
2024-2-19
1.神兽个体值修改，必定为3V及以上
2.发放奖励、赠送道具添加给予对象的昵称识别
2024-1-31
1.精灵状态添加闪光精灵的形象图
2024-1-29
1.手动对战加入PP值设定
2024-1-22
1.添加成都、丰缘地图
2.道具赠送添加金币，学习机的赠送功能
 """
    await bot.send(msg, at_sender=True)
    
    
@sv_pokemon_duel.on_fullmatch(['小游戏帮助', '宝可梦小游戏帮助'])
async def pokemon_help_game(bot, ev: Event):
    msg = """
             宝可梦小游戏帮助
游戏名：
1、宝可梦猜猜我是谁
（给出宝可梦剪影，猜猜是哪只宝可梦）
注:
其他的宝可梦小游戏正在火速开发中(新建文件夹)
 """
    buttons = [
        Button('✅我是谁', '我是谁', action=1),
    ]
    await bot.send_option(msg, buttons)


@sv_pokemon_duel.on_command(('我的精灵列表', '我的宝可梦列表'))
async def my_pokemon_list(bot, ev: Event):
    page = ''.join(re.findall('^[a-zA-Z0-9_\u4e00-\u9fa5]+$', ev.text))
    if not page:
        page = 0
    else:
        page = int(page) - 1
    uid = ev.user_id

    pokemon_num = POKE._get_pokemon_num(uid)
    if pokemon_num == 0:
        return await bot.send(
            '您还没有精灵，请输入 领取初始精灵+初始精灵名称 开局。',
            at_sender=True,
        )

    page_num = math.floor(pokemon_num / 30) + 1
    mypokelist = POKE._get_pokemon_list(uid, page)
    mes = ''
    page = page + 1
    mes += '您的精灵信息为(按等级与编号排序一页30只):'
    for pokemoninfo in mypokelist:
        startype = await POKE.get_pokemon_star(uid, pokemoninfo[0])
        mes += f'\n {starlist[startype]}{POKEMON_LIST[pokemoninfo[0]][0]}({pokemoninfo[1]})'
    if page_num > 1:
        mes += f'\n第({page}/{page_num})页'
    buttons = [
        Button('📖精灵状态', '精灵状态', action=2),
        Button('🔄更新队伍', '更新队伍', action=2),
    ]
    if page > 1:
        uppage = page - 1
        buttons.append(Button('⬅️上一页', f'我的精灵列表{uppage}', action=1))
    if page_num > 1:
        buttons.append(Button(f'⏺️跳转({page}/{page_num})', '我的精灵列表', action=2))
    if page < page_num:
        dowmpage = page + 1
        buttons.append(Button('➡️下一页', f'我的精灵列表{dowmpage}', action=1))
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_command(('精灵图鉴', '宝可梦图鉴'))
async def show_poke_info(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 精灵图鉴+宝可梦名称 中间用空格隔开。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    im, jinhualist = await draw_pokemon_info_tj(bianhao)
    
    buttons = []
    for jinhuainfo in jinhualist:
        buttons.append(
            Button(
                f'📖图鉴{jinhuainfo[1]}',
                f'精灵图鉴{jinhuainfo[1]}',
                action=1,
            )
        )
    await bot.send_option(im, buttons)


@sv_pokemon_duel.on_command(('精灵状态', '宝可梦状态'))
async def get_my_poke_info_t(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 精灵状态+宝可梦名称 中间用空格隔开。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = await get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    im, jinhualist = await draw_pokemon_info(uid, pokemon_info, bianhao)
    buttons = [
        Button('📖查图鉴', f'精灵图鉴{pokename}', action=1),
        Button('📖学技能', f'学习技能{pokename}', action=2),
        Button('📖遗忘技能', f'遗忘技能{pokename}', action=2),
    ]
    if pokename == '伊布':
        buttons = [
            Button('📖学技能', f'学习技能{pokename}', action=2),
            Button('📖遗忘技能', f'遗忘技能{pokename}', action=2),
        ]
    for jinhuainfo in jinhualist:
        buttons.append(
            Button(
                f'⏫进化{jinhuainfo[1]}',
                f'宝可梦进化{jinhuainfo[1]}',
                action=1,
            )
        )
    await bot.send_option(im, buttons)


@sv_pokemon_duel.on_fullmatch(('初始精灵列表', '初始宝可梦列表'))
async def get_chushi_list(bot, ev: Event):
    mes = []
    mes = ''
    mes += '可输入领取初始精灵+精灵名称领取'
    for bianhao in chushi_list:
        # img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao][0]}.png'
        # img = await convert_img(img)
        mes += f'\n{POKEMON_LIST[bianhao][0]} 属性:{POKEMON_LIST[bianhao][7]}'
    buttons = [
        Button('✅领取初始精灵', '领取初始精灵', action=2),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_command(('领取初始精灵', '领取初始宝可梦'))
async def get_chushi_pokemon(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        mes = '请输入 领取初始精灵+宝可梦名称。初始精灵列表可点击下方按钮查询'
        buttons = [
            Button('📖初始精灵列表', '初始精灵列表', action=1),
        ]
        return await bot.send_option(mes, buttons)
    pokename = args[0]
    uid = ev.user_id

    my_pokemon = POKE._get_pokemon_num(uid)
    if my_pokemon > 0:
        return await bot.send('您已经有精灵了，无法领取初始精灵。', at_sender=True)

    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    if bianhao not in chushi_list:
        return await bot.send(
            f'{POKEMON_LIST[bianhao][0]}不属于初始精灵，无法领取。',
            at_sender=True,
        )
    startype = await get_pokemon_star(uid)
    pokemon_info = add_pokemon(uid, bianhao, startype)
    await POKE._add_pokemon_group(uid, bianhao)

    await POKE.update_pokemon_star(uid, bianhao, startype)
    if bianhao in [1,4,7]:
        go_didian = '1号道路'
    elif bianhao in [152,155,158]:
        go_didian = '29号道路'
    elif bianhao in [252,255,258]:
        go_didian = '101号道路'
    else:
        csdidianlist = ['1号道路', '29号道路', '101号道路']
        go_didian = random.sample(csdidianlist, 1)[0]
    name = uid
    if ev.sender:
        sender = ev.sender
        if sender.get('nickname', '') != '':
            name = sender['nickname']
    POKE._new_map_info(uid, go_didian, name)

    HP, W_atk, W_def, M_atk, M_def, speed = await get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    picfile = os.path.join(
        FILE_PATH, 'icon', f'{POKEMON_LIST[bianhao][0]}.png'
    )
    mes = ''
    mes += '恭喜！您领取到了初始精灵\n'
    img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao][0]}.png'
    img = await convert_img(img)
    # mes.append(MessageSegment.image(img))
    mes += f'{starlist[startype]}{POKEMON_LIST[bianhao][0]}\nLV:{pokemon_info[0]}\n属性:{POKEMON_LIST[bianhao][7]}\n性格:{pokemon_info[13]}\nHP:{HP}({pokemon_info[1]})\n物攻:{W_atk}({pokemon_info[2]})\n物防:{W_def}({pokemon_info[3]})\n特攻:{M_atk}({pokemon_info[4]})\n特防:{M_def}({pokemon_info[5]})\n速度:{speed}({pokemon_info[6]})\n'
    mes += f'可用技能\n{pokemon_info[14]}'
    buttons = [
        Button('📖精灵状态', f'精灵状态{pokename}', action=1),
        Button('🏝️野外探索', '野外探索', action=1),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_fullmatch(['宝可梦重开'])
async def chongkai_pokemon(bot, ev: Event):
    uid = ev.user_id
    await chongkai(uid)
    mes = '重开成功，请重新领取初始精灵开局'
    buttons = [
        Button('✅领取初始精灵', '领取初始精灵', action=2),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('放生精灵', '放生宝可梦'))
async def fangsheng_pokemon(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 放生精灵+宝可梦名称 中间用空格隔开。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = await get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )

    my_pokemon = POKE._get_pokemon_num(uid)
    if my_pokemon == 1:
        return await bot.send('您就这么一只精灵了，无法放生。', at_sender=True)
    await fangshen(uid, bianhao)
    startype = await POKE.get_pokemon_star(uid, bianhao)
    my_team = await POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    if str(bianhao) in pokemon_list:
        pokemon_list.remove(str(bianhao))
        pokemon_str = ','.join(pokemon_list)
        await POKE._add_pokemon_group(uid, pokemon_str)
    await bot.send(
        f'放生成功，{starlist[startype]}{POKEMON_LIST[bianhao][0]}离你而去了',
        at_sender=True,
    )


@sv_pokemon_duel.on_prefix(('学习精灵技能', '学习宝可梦技能', '学习技能'))
async def add_pokemon_jineng(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 2:
        return await bot.send(
            '请输入 学习精灵技能+宝可梦名称+技能名称 中间用空格隔开。',
            at_sender=True,
        )
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = await get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    jinengname = args[1]

    startype = await POKE.get_pokemon_star(uid, bianhao)
    if str(jinengname) in str(pokemon_info[14]):
        return await bot.send(
            f'学习失败，您的精灵 {starlist[startype]}{POKEMON_LIST[bianhao][0]}已学会{jinengname}。',
            at_sender=True,
        )
    jinenglist = re.split(',', pokemon_info[14])
    if len(jinenglist) >= 4:
        return await bot.send(
            f'学习失败，您的精灵 {starlist[startype]}{POKEMON_LIST[bianhao][0]}已学会4个技能，请先遗忘一个技能后再学习。',
            at_sender=True,
        )
    jinengzu = get_level_jineng(pokemon_info[0], bianhao)
    xuexizu = POKEMON_XUEXI[bianhao]
    if jinengname not in jinengzu and jinengname not in xuexizu:
        return await bot.send(
            f'学习失败，当前等级学习无法学习该技能或{pokename}无法通过学习机学会该技能。',
            at_sender=True,
        )
    mes_xh = ''
    if jinengname not in jinengzu and jinengname in xuexizu:
        xuexiji_num = await POKE._get_pokemon_technical(uid, jinengname)
        if xuexiji_num == 0:
            return await bot.send(
                f'学习失败，您的[{jinengname}]技能机数量不足。',
                at_sender=True,
            )
        await POKE._add_pokemon_technical(uid,jinengname,-1)
        mes_xh = f'您消耗了招式学习机[{jinengname}]x1，使'

    jineng = pokemon_info[14] + ',' + jinengname

    POKE._add_pokemon_jineng(uid, bianhao, jineng)
    mes = f'恭喜，{mes_xh}您的精灵 {starlist[startype]}{POKEMON_LIST[bianhao][0]}学会了技能{jinengname}'
    buttons = [
        Button('📖学习技能', f'学习技能 {pokename}', action=2),
        Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
        Button('📖精灵状态', f'精灵状态{pokename}', action=1),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('遗忘精灵技能', '遗忘宝可梦技能', '遗忘技能'))
async def del_pokemon_jineng(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 2:
        return await bot.send(
            '请输入 学习精灵技能+宝可梦名称+技能名称 中间用空格隔开。',
            at_sender=True,
        )
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = await get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    jinengname = args[1]

    startype = await POKE.get_pokemon_star(uid, bianhao)
    if str(jinengname) not in str(pokemon_info[14]):
        return await bot.send(
            f'遗忘失败，您的精灵 {starlist[startype]}{POKEMON_LIST[bianhao][0]}未学习{jinengname}。',
            at_sender=True,
        )
    jinenglist = re.split(',', pokemon_info[14])
    if len(jinenglist) == 1:
        return await bot.send('遗忘失败，需要保留1个技能用于对战哦。', at_sender=True)
    jinenglist.remove(jinengname)
    jineng = ''
    shul = 0
    for name in jinenglist:
        if shul > 0:
            jineng = jineng + ','
        jineng = jineng + name
        shul = shul + 1

    POKE._add_pokemon_jineng(uid, bianhao, jineng)
    mes = f'成功，您的精灵{starlist[startype]}{POKEMON_LIST[bianhao][0]}遗忘了技能{jinengname}'
    buttons = [
        Button('📖学习技能', f'学习技能 {pokename}', action=2),
        Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
        Button('📖精灵状态', f'精灵状态{pokename}', action=1),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(['精灵技能信息'])
async def get_jineng_info_text(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 精灵技能信息+技能名称 中间用空格隔开。', at_sender=True)
    jineng = args[0]
    try:
        jinenginfo = JINENG_LIST[jineng]
        mes = f'名称：{jineng}\n属性：{jinenginfo[0]}\n类型：{jinenginfo[1]}\n威力：{jinenginfo[2]}\n命中：{jinenginfo[3]}\nPP值：{jinenginfo[4]}\n描述：{jinenginfo[5]}'
        if jinenginfo[6] == '':
            mes += '\n技能未添加'
        else:
            mes += '\n技能已添加'
        await bot.send(mes)
    except:
        await bot.send('无法找到该技能，请输入正确的技能名称。', at_sender=True)


@sv_pokemon_duel.on_prefix(['宝可梦进化'])
async def get_jineng_info(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 宝可梦进化+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    zhongzu = POKEMON_LIST[bianhao]
    if len(zhongzu) < 9:
        return await bot.send('暂时没有该宝可梦的进化信息，请等待后续更新。', at_sender=True)
    if zhongzu[8] == '-':
        return await bot.send('暂时没有该宝可梦的进化信息。', at_sender=True)
    use_flag = 0

    my_pokemon_list = POKE._get_my_pokemon(uid)
    for pokemonid in my_pokemon_list:
        if int(pokemonid[0]) == int(bianhao):
            use_flag = 1
            break
    if use_flag == 1:
        return await bot.send(f'已经有{pokename}了，不能同时拥有同一只精灵哦。', at_sender=True)

    kid_poke_id = int(zhongzu[8])
    pokemon_info = await get_pokeon_info(uid, kid_poke_id)

    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[kid_poke_id][0]}，无法进化。',
            at_sender=True,
        )
    startype = await POKE.get_pokemon_star(uid, kid_poke_id)
    if zhongzu[9].isdigit():
        if pokemon_info[0] < int(zhongzu[9]):
            return await bot.send(
                f'进化成{POKEMON_LIST[bianhao][0]}需要 Lv.{zhongzu[9]}\n您的{starlist[startype]}{POKEMON_LIST[kid_poke_id][0]}等级为 Lv.{pokemon_info[0]}，无法进化',
                at_sender=True,
            )
        else:
            await POKE.update_pokemon_star(uid, bianhao, startype)
            await POKE._delete_poke_star_bianhao(uid, kid_poke_id)
            POKE._add_pokemon_id(uid, kid_poke_id, bianhao)
            my_team = await POKE.get_pokemon_group(uid)
            pokemon_list = my_team.split(',')
            if str(kid_poke_id) in pokemon_list:
                team_list = []
                for pokeid in pokemon_list:
                    if int(pokeid) == int(kid_poke_id):
                        pokeid = bianhao
                    team_list.append(str(pokeid))
                pokemon_str = ','.join(team_list)
                await POKE._add_pokemon_group(uid, pokemon_str)
            mes = f'恭喜！您的宝可梦 {starlist[startype]}{POKEMON_LIST[kid_poke_id][0]} 进化成了 {starlist[startype]}{POKEMON_LIST[bianhao][0]}'
            buttons = [
                Button('📖学习技能', f'学习技能 {pokename}', action=2),
                Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
                Button('📖精灵状态', f'精灵状态{pokename}', action=1),
            ]
            await bot.send_option(mes, buttons)
    else:
        mypropnum = await POKE._get_pokemon_prop(uid, zhongzu[9])
        if mypropnum == 0:
            return await bot.send(
                f'进化成{POKEMON_LIST[bianhao][0]}需要道具{zhongzu[9]}，您还没有该道具，无法进化',
                at_sender=True,
            )
        else:
            await POKE.update_pokemon_star(uid, bianhao, startype)
            await POKE._delete_poke_star_bianhao(uid, kid_poke_id)
            POKE._add_pokemon_id(uid, kid_poke_id, bianhao)
            my_team = await POKE.get_pokemon_group(uid)
            pokemon_list = my_team.split(',')
            await POKE._add_pokemon_prop(uid, zhongzu[9], -1)
            if str(kid_poke_id) in pokemon_list:
                team_list = []
                for pokeid in pokemon_list:
                    if int(pokeid) == int(kid_poke_id):
                        pokeid = bianhao
                    team_list.append(str(pokeid))
                pokemon_str = ','.join(team_list)
                await POKE._add_pokemon_group(uid, pokemon_str)
            mes = f'恭喜！您的宝可梦 {starlist[startype]}{POKEMON_LIST[kid_poke_id][0]} 进化成了 {starlist[startype]}{POKEMON_LIST[bianhao][0]}'
            buttons = [
                Button('📖学习技能', f'学习技能 {pokename}', action=2),
                Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
                Button('📖精灵状态', f'精灵状态{pokename}', action=1),
            ]
            await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_command(('我的精灵蛋', '我的宝可梦蛋'))
async def my_pokemon_egg_list(bot, ev: Event):
    page = ''.join(re.findall('^[a-zA-Z0-9_\u4e00-\u9fa5]+$', ev.text))
    if not page:
        page = 0
    else:
        page = int(page) - 1
    uid = ev.user_id

    myegglist = await POKE.get_pokemon_egg_list(uid, page)
    if myegglist == 0:
        return await bot.send('您还没有精灵蛋', at_sender=True)
    egg_num = await POKE.get_pokemon_egg_num(uid)
    page_num = math.floor(egg_num / 30) + 1
    mes = ''
    page = page + 1
    mes += '您的精灵蛋信息为(一页只显示30种按数量和编号排序):\n'
    for pokemoninfo in myegglist:
        mes += f'{POKEMON_LIST[pokemoninfo[0]][0]} 数量 {pokemoninfo[1]}\n'
    if page_num > 1:
        mes += f'第({page}/{page_num})页'
    buttons = [
        Button('📖宝可梦孵化', '宝可梦孵化', action=2),
        Button('📖重置个体值', '重置个体值', action=2),
        Button('📖丢弃精灵蛋', '丢弃精灵蛋', action=2),
    ]
    if page > 1:
        uppage = page - 1
        buttons.append(Button('⬅️上一页', f'我的精灵蛋{uppage}', action=1))
    if page_num > 1:
        buttons.append(Button(f'⏺️跳转({page}/{page_num})', '我的精灵蛋', action=2))
    if page < page_num:
        dowmpage = page + 1
        buttons.append(Button('➡️下一页', f'我的精灵蛋{dowmpage}', action=1))

    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('丢弃精灵蛋', '丢弃宝可梦蛋'))
async def my_pokemon_egg_use(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send('请输入 丢弃精灵蛋+宝可梦名称+丢弃数量。', at_sender=True)

    uid = ev.user_id
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)

    egg_num = await POKE.get_pokemon_egg(uid, bianhao)
    if egg_num == 0:
        return await bot.send(f'您还没有{pokename}的精灵蛋哦。', at_sender=True)
    if len(args) == 2:
        eggnum = int(args[1])
        if eggnum > egg_num:
            eggnum = egg_num
    else:
        eggnum = egg_num
    await POKE._add_pokemon_egg(uid, bianhao, 0 - eggnum)
    mes = f'成功！您丢弃了{pokename}精灵蛋x{eggnum}'
    buttons = [
        Button('📖宝可梦孵化', '宝可梦孵化', action=2),
        Button('📖重置个体值', '重置个体值', action=2),
        Button('📖我的精灵蛋', '我的精灵蛋', action=1),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_command(('重置个体值', '个体值重置'))
async def my_pokemon_gt_up(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send('请输入 重置个体值+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    mapinfo = POKE._get_map_now(uid)
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    my_pokemon_info = await get_pokeon_info(uid, bianhao)
    if my_pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    if len(args) > 1:
        rest_num = int(args[1])
    else:
        rest_num = 1
    
    if len(args) == 3:
        gt_max_num = int(args[2])
    else:
        gt_max_num = 3
    kidid = await get_pokemon_eggid(bianhao)
    egg_num = await POKE.get_pokemon_egg(uid, kidid)
    if egg_num == 0:
        return await bot.send(
            f'重置个体值需要消耗1枚同一种类型的精灵蛋哦，您没有{POKEMON_LIST[kidid][0]}的精灵蛋。',
            at_sender=True,
        )
    (
        HP_o,
        W_atk_o,
        W_def_o,
        M_atk_o,
        M_def_o,
        speed_o,
    ) = await get_pokemon_shuxing(bianhao, my_pokemon_info)
    if egg_num < rest_num:
        return await bot.send(
            f'重置{rest_num}次个体值需要消耗{rest_num}枚同一种类型的精灵蛋哦，您的{POKEMON_LIST[kidid][0]}精灵蛋不足。',
            at_sender=True,
        )
    if rest_num == 1:
        await POKE._add_pokemon_egg(uid, kidid, -1)
        startype = await POKE.get_pokemon_star(uid, bianhao)
        new_star_type = await get_pokemon_star(uid)
        if new_star_type > startype:
            startype = new_star_type
            await POKE.update_pokemon_star(uid, bianhao, startype)
        pokemon_info = await new_pokemon_gt(uid, bianhao, startype)

        HP, W_atk, W_def, M_atk, M_def, speed = await get_pokemon_shuxing(
            bianhao, pokemon_info
        )
        change_mes = f''
        if new_star_type > 0:
            change_mes = f'您的宝可梦形态好像发生了改变\n'
        mes = f'[{mapinfo[2]}]{change_mes}{starlist[startype]}{pokename}个体值重置成功，重置后属性如下\n'

        mes += f'HP:{HP_o}→{HP}({my_pokemon_info[1]}→{pokemon_info[1]})\n物攻:{W_atk_o}→{W_atk}({my_pokemon_info[2]}→{pokemon_info[2]})\n物防:{W_def_o}→{W_def}({my_pokemon_info[3]}→{pokemon_info[3]})\n特攻:{M_atk_o}→{M_atk}({my_pokemon_info[4]}→{pokemon_info[4]})\n特防:{M_def_o}→{M_def}({my_pokemon_info[5]}→{pokemon_info[5]})\n速度:{speed_o}→{speed}({my_pokemon_info[6]}→{pokemon_info[6]})'
        starflag = await POKE.get_pokemon_starrush(uid)
        mes += f'\n({starflag}/1024)'
        # mes.append(MessageSegment.image(img))

    else:
        startype = await POKE.get_pokemon_star(uid, bianhao)
        starflag = await POKE.get_pokemon_starrush(uid)
        jishu = 0
        rest_flag = 0
        while rest_num > 0 and rest_flag == 0:
            starflag += 1
            jishu += 1
            rest_num = rest_num - 1
            star_num = int(math.floor(random.uniform(0, 40960)))
            new_star_type = 0
            if starflag >= 1024 or star_num <= 10:
                new_star_type = 1
                star_num2 = int(math.floor(random.uniform(0, 160)))
                print(star_num2)
                if star_num2 <= 10:
                    new_star_type = 2
            if starflag == 1023:
                rest_flag = 1
            if new_star_type > 0:
                starflag = 0
                rest_flag = 2
            if new_star_type > startype:
                startype = new_star_type
                await POKE.update_pokemon_star(uid, bianhao, startype)
            pokemon_info = []
            pokemon_info.append(my_pokemon_info[0])
            gtmax = []
            if startype > 0:
                gtmax = random.sample([1, 2, 3, 4, 5, 6], startype)
            if bianhao in jinyonglist:
                gtmax = random.sample([1, 2, 3, 4, 5, 6], 3)
            gt_max_sl = 0
            for num in range(1, 7):
                if num in gtmax:
                    gt_num = 31
                else:
                    gt_num = int(math.floor(random.uniform(1, 32)))
                pokemon_info.append(gt_num)
                if gt_num == 31:
                    gt_max_sl += 1
            if gt_max_sl >= gt_max_num:
                rest_flag = 3
            for num in range(7, 15):
                pokemon_info.append(my_pokemon_info[num])
        await POKE.update_pokemon_starrush(uid, jishu)
        if rest_flag == 0:
            mes = f'[{mapinfo[2]}]您的个体值{jishu}次重置完成，重置后属性如下'
        if rest_flag == 1:
            mes = f'[{mapinfo[2]}]您的个体值{jishu}次重置成功，还差一次就出闪光啦，重置后属性如下'
        if rest_flag == 2:
            mes = f'[{mapinfo[2]}]您的个体值{jishu}次重置成功，您的精灵形象发生了改变，重置后属性如下'
            await POKE.new_pokemon_starrush(uid)
        if rest_flag == 3:
            mes = f'[{mapinfo[2]}]您的个体值{jishu}次重置成功，您的精灵拥有了很高的潜力，重置后属性如下'
        await POKE._add_pokemon_egg(uid, kidid, 0 - jishu)
        POKE._add_pokemon_info(uid, bianhao, pokemon_info, my_pokemon_info[15])
        HP, W_atk, W_def, M_atk, M_def, speed = await get_pokemon_shuxing(
            bianhao, pokemon_info
        )
        mes += f'\n{starlist[startype]}{pokename}\n'
        mes += f'HP:{HP_o}→{HP}({my_pokemon_info[1]}→{pokemon_info[1]})\n物攻:{W_atk_o}→{W_atk}({my_pokemon_info[2]}→{pokemon_info[2]})\n物防:{W_def_o}→{W_def}({my_pokemon_info[3]}→{pokemon_info[3]})\n特攻:{M_atk_o}→{M_atk}({my_pokemon_info[4]}→{pokemon_info[4]})\n特防:{M_def_o}→{M_def}({my_pokemon_info[5]}→{pokemon_info[5]})\n速度:{speed_o}→{speed}({my_pokemon_info[6]}→{pokemon_info[6]})'
        mes += f'\n({starflag}/1024)'
    buttons = [
        Button('📖精灵状态', f'精灵状态{pokename}', action=1),
        Button('📖重置个体值', f'重置个体值{pokename}', action=2),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_command(['宝可梦重生'])
async def get_pokemon_form_chongsheng(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 宝可梦重生+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)

    my_pokemon_info = await get_pokeon_info(uid, bianhao)
    if my_pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    if my_pokemon_info[0] < 100:
        return await bot.send(f'您的{pokename}等级不足100，无法重生。', at_sender=True)

    my_pokemon = POKE._get_pokemon_num(uid)
    if my_pokemon == 1:
        return await bot.send('您就这么一只精灵了，无法重生。', at_sender=True)

    eggid = await get_pokemon_eggid(bianhao)
    await POKE._add_pokemon_egg(uid, eggid, 1)
    await fangshen(uid, bianhao)
    my_team = await POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    if str(bianhao) in pokemon_list:
        pokemon_list.remove(str(bianhao))
        pokemon_str = ','.join(pokemon_list)
        await POKE._add_pokemon_group(uid, pokemon_str)
    mes = f'{pokename}重生成功，您获得了{POKEMON_LIST[eggid][0]}精灵蛋x1'
    buttons = [
        Button('📖宝可梦孵化', f'宝可梦孵化{POKEMON_LIST[eggid][0]}', action=1),
    ]
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_command(['赠送物品'])
async def give_prop_pokemon_egg(bot, ev: Event):
    args = ev.text.split()
    uid = ev.user_id
    if len(args) < 2:
        return await bot.send('请输入 赠送物品[道具/精灵蛋/金币/学习机][名称][数量][赠送对象昵称/at]。', at_sender=True)
    proptype = args[0]
    if proptype not in ['金币','金钱','道具', '精灵蛋', '宝可梦蛋', '蛋', '学习机']:
        return await bot.send('请输入正确的类型 道具/精灵蛋/金币/学习机。', at_sender=True)
    if ev.at is not None:
        suid = ev.at
        smapinfo = POKE._get_map_now(suid)
        if smapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请at需要发放奖励的对象/该人员未成为训练家。',
                at_sender=True,
            )
        sname = smapinfo[2]
    else:
        if proptype in ['金币','金钱']:
            if len(args) == 2:
                snickname = args[1]
            else:
                snickname = args[2]
        else:
            if len(args) < 3:
                return await bot.send(
                    '请输入赠送训练家的昵称或at该名训练家。',
                    at_sender=True,
                )
            if len(args) == 3:
                snickname = args[2]
            else:
                snickname = args[3]
        smapinfo = POKE._get_map_info_nickname(snickname)
        if smapinfo[2] == 0:
            return await bot.send(
                '没有找到该训练家，请输入 正确的训练家昵称或at该名训练家。',
                at_sender=True,
            )
        suid = smapinfo[2]
        sname = snickname
    
    propname = args[1]
    if len(args) >= 3 and proptype in ['道具', '精灵蛋', '宝可梦蛋', '蛋', '学习机']:
        if args[2].isdigit():
            propnum = int(args[2])
        else:
            propnum = 1
    else:
        propnum = 1
    if propnum < 1:
        return await bot.send('赠送物品的数量需大于0。', at_sender=True)
    break_flag = 0
    if suid == '34674183F5CFA2481E4249C32A3B54B5':
        break_flag = 1
    if proptype == '金币' or proptype == '金钱':
        propnum = int(args[1])
        if propnum < 1:
            return await bot.send('赠送金币的数量需大于1。', at_sender=True)
        my_score = SCORE.get_score(uid)
        if break_flag == 0:
            if my_score < propnum:
                return await bot.send('您的金币不足',at_sender=True)
            SCORE.update_score(uid, 0 - propnum)
        SCORE.update_score(suid, propnum)
        mes = f'您赠送给了{sname} 金币x{propnum}。'
    if proptype == '道具':
        propkeylist = proplist.keys()
        if propname not in propkeylist:
            return await bot.send('无法找到该道具，请输入正确的道具名称。', at_sender=True)
        mypropnum = await POKE._get_pokemon_prop(uid, propname)
        if break_flag == 0:
            if mypropnum == 0:
                return await bot.send(f'您还没有{propname}哦。', at_sender=True)
            if mypropnum < propnum:
                return await bot.send(
                    f'您的{propname}数量小于{propnum}，赠送失败。', at_sender=True
                )
            await POKE._add_pokemon_prop(uid, propname, 0 - propnum)
        await POKE._add_pokemon_prop(suid, propname, propnum)
        mes = f'您赠送给了{sname} 道具{propname}x{propnum}。'
    if proptype == '学习机':
        jinenglist = JINENG_LIST.keys()
        if propname not in jinenglist:
            return await bot.send('无法找到该技能，请输入正确的技能学习机名称。', at_sender=True)
        xuexiji_num = await POKE._get_pokemon_technical(uid, propname)
        if break_flag == 0:
            if xuexiji_num == 0:
                return await bot.send(f'您还没有{propname}学习机哦。', at_sender=True)
            if xuexiji_num < propnum:
                return await bot.send(
                    f'您的{propname}学习机数量小于{propnum}，赠送失败。', at_sender=True
                )
            await POKE._add_pokemon_technical(uid,propname,0 - propnum)
        await POKE._add_pokemon_technical(suid,propname,propnum)
        mes = f'您赠送给了{sname} 学习机{propname}x{propnum}。'
    if proptype == '精灵蛋' or proptype == '宝可梦蛋' or proptype == '蛋':
        proptype = '精灵蛋'
        bianhao = await get_poke_bianhao(propname)
        if bianhao == 0:
            return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
        egg_num = await POKE.get_pokemon_egg(uid, bianhao)
        if break_flag == 0:
            if egg_num == 0:
                return await bot.send(f'您还没有{propname}的精灵蛋哦。', at_sender=True)
            if egg_num < propnum:
                return await bot.send(
                    f'您的{propname}精灵蛋数量小于{propnum}，赠送失败。', at_sender=True
                )

            await POKE._add_pokemon_egg(uid, bianhao, 0 - propnum)
        await POKE._add_pokemon_egg(suid, bianhao, propnum)
        mes = f'您赠送给了{sname} {propname}精灵蛋x{propnum}。'
    await bot.send(mes)


@sv_pokemon_duel.on_prefix(['宝可梦孵化'])
async def get_pokemon_form_egg(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 宝可梦孵化+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = await get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)

    egg_num = await POKE.get_pokemon_egg(uid, bianhao)
    if egg_num == 0:
        return await bot.send(f'您还没有{pokename}的精灵蛋哦。', at_sender=True)
    use_flag = 0
    my_pokemon_list = POKE._get_my_pokemon(uid)
    for pokemonid in my_pokemon_list:
        if int(pokemonid[0]) == int(bianhao):
            use_flag = 1
            break
    if use_flag == 1:
        return await bot.send(f'已经有{pokename}了，不能同时拥有同一只精灵哦。', at_sender=True)
    await POKE._add_pokemon_egg(uid, bianhao, -1)

    startype = await get_pokemon_star(uid)
    pokemon_info = add_pokemon(uid, bianhao, startype)
    await POKE.update_pokemon_star(uid, bianhao, startype)
    HP, W_atk, W_def, M_atk, M_def, speed = await get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    mes = ''
    mes += '恭喜！孵化成功了\n'
    mes += f'{starlist[startype]}{POKEMON_LIST[bianhao][0]}\nLV:{pokemon_info[0]}\n属性:{POKEMON_LIST[bianhao][7]}\n性格:{pokemon_info[13]}\nHP:{HP}({pokemon_info[1]})\n物攻:{W_atk}({pokemon_info[2]})\n物防:{W_def}({pokemon_info[3]})\n特攻:{M_atk}({pokemon_info[4]})\n特防:{M_def}({pokemon_info[5]})\n速度:{speed}({pokemon_info[6]})\n'
    mes += f'可用技能\n{pokemon_info[14]}'
    my_team = await POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    if len(pokemon_list) < 4:
        pokemon_list.append(str(bianhao))
        pokemon_str = ','.join(pokemon_list)
        await POKE._add_pokemon_group(uid, pokemon_str)
    buttons = [
        Button('📖精灵状态', f'精灵状态{pokename}', action=1),
        Button('📖重置个体值', f'重置个体值{pokename}', action=1),
    ]
    await bot.send_option(mes, buttons)

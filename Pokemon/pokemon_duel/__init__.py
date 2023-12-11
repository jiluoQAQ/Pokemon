import os
import re
import math
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.image.convert import convert_img
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH
from gsuid_core.message_models import Button
from ..utils.dbbase.ScoreCounter import SCORE_DB
from .pokeconfg import *
from .pokemon import *
from .PokeCounter import *
from .until import *
from .map import *
from .fight import *
from .prop import *

sv_pokemon_duel = SV('宝可梦状态', priority=5)


@sv_pokemon_duel.on_fullmatch(['精灵帮助', '宝可梦帮助'])
async def pokemon_help(bot, ev: Event):
    msg = """
             宝可梦帮助
进入游戏请先输入 领取初始精灵[精灵名] 开局，初始精灵有各个版本的御三家，如
    领取初始精灵小火龙
指令：
1、初始精灵列表(查询可以领取的初始精灵)
2、领取初始精灵[精灵名](领取初始精灵[精灵名])
3、精灵状态[精灵名](查询[精灵名]的属性信息)
4、我的精灵列表(查询我拥有的等级前20的精灵)
5、宝可梦重开(删除我所有的精灵信息)
6、放生精灵[精灵名](放生名为[精灵名]的精灵)
7、学习精灵技能[精灵名] [技能名](让精灵学习技能[非学习机技能])
8、遗忘精灵技能[精灵名] [技能名](让精灵遗忘技能)
9、野外探索(在野外地区与野生宝可梦或训练师战斗获取精灵经验)
10、打工(在城镇地区打工进行打工赚取金币)
11、前往[地点名](前往[地点名]的地点)
12、宝可梦进化[精灵名](让你的宝可梦进化为[精灵名]，需要有前置进化型精灵)
13、修改训练家名称[昵称](把你的训练家名称改为[昵称]，[昵称]有唯一性，作为对战识别符)
14、训练家对战[昵称](与昵称为[昵称]的训练家进行对战)
15、挑战[道馆][天王][四天王冠军](通过战胜[道馆][天王][四天王冠军]获得徽章称号，进一步解锁功能)
16、查看地图[地区名](查询[地区名]的地点信息，[地区名]可留空，默认所在地区)
17、我的精灵蛋(查询我的精灵蛋信息)
18、重置个体值[精灵名](消耗一枚[精灵名]初始形态的精灵蛋对[精灵名]的个体值进行重置)
19、宝可梦孵化[精灵名](消耗一枚[精灵名]的精灵蛋孵化出一只lv.5的[精灵名])
20、更新队伍[精灵名](更新手持队伍信息，不同的宝可梦用空格分隔，最多4只)
21、无级别对战[昵称/at对方]与其他训练家进行一场无等级限制的手动对战
22、大量出现信息(查询当前随机出现的大量宝可梦消息)
23、道具帮助(查看道具系统的使用说明)
注:
同一类型的精灵只能拥有一只(进化型为不同类型)
后续功能在写了在写了(新建文件夹)

其他宝可梦相关小游戏可以点击小游戏帮助查询
 """
    buttons = [
        Button('📖精灵状态', '精灵状态', action=2),
        Button('🔄更新队伍', '更新队伍', action=2),
        Button('✅领取初始精灵', '领取初始精灵', action=2),
        Button('🏝️野外探索', '野外探索'),
        Button('🗺查看地图', '查看地图'),
        Button('✅道具帮助', '道具帮助'),
        Button('✅大量出现信息', '大量出现信息'),
        Button('✅小游戏帮助', '小游戏帮助'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(msg, at_sender=True)
    else:
        await bot.send_option(msg, buttons)


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
        Button('✅我是谁', '我是谁'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(msg, at_sender=True)
    else:
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

    page_num = math.floor(pokemon_num / 30)
    mypokelist = POKE._get_pokemon_list(uid, page)
    mes = ''
    mes += '您的精灵信息为(按等级与编号排序一页30只):'
    for pokemoninfo in mypokelist:
        startype = POKE.get_pokemon_star(uid, pokemoninfo[0])
        mes += f'\n {starlist[startype]}{POKEMON_LIST[pokemoninfo[0]][0]}({pokemoninfo[1]})'
    if page_num > 0:
        mes += f'第({page + 1}/{page_num + 1})页'
    buttons = [
        Button('📖精灵状态', '精灵状态', action=2),
        Button('🔄更新队伍', '更新队伍', action=2),
    ]
    if page > 0:
        uppage = page - 1
        buttons.append(Button('⬅️上一页', f'我的精灵列表 {uppage}'))
    if page_num > 0:
        Button(f'⏺️跳转({page+1}/{page_num+1})', '我的精灵列表', action=2)
    if page < page_num:
        dowmpage = page + 1
        buttons.append(Button('➡️下一页', f'我的精灵列表 {dowmpage}'))
    await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(['技能测试'])
async def get_my_poke_jineng_button_test(bot, ev: Event):
    print(str(ev))
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 技能测试+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    jinenglist = re.split(',', pokemon_info[14])
    # resp = await bot.receive_resp(markdown,jinenglist,unsuported_platform=False)
    resp = await bot.receive_resp(
        '请在60秒内选择一个技能使用!', jinenglist, unsuported_platform=False
    )
    if resp is not None:
        s = resp.text
        uid = resp.user_id
        if s in jinenglist:
            jineng1 = s
            await bot.send(f'你选择的是{resp.text}', at_sender=True)
            jineng_use = 1


@sv_pokemon_duel.on_prefix(('精灵状态', '宝可梦状态'))
async def get_my_poke_info(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send(
            '请输入 精灵状态+宝可梦名称 中间用空格隔开。', at_sender=True
        )
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    HP, W_atk, W_def, M_atk, M_def, speed = get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao][0]}.png'
    img = await convert_img(img)
    mes = []

    startype = POKE.get_pokemon_star(uid, bianhao)
    # mes.append(MessageSegment.image(img))
    mes.append(
        MessageSegment.text(
            f'{starlist[startype]}{POKEMON_LIST[bianhao][0]}\nLV:{pokemon_info[0]}\n属性:{POKEMON_LIST[bianhao][7]}\n性格:{pokemon_info[13]}\n属性值[种族值](个体值)\nHP:{HP}[{POKEMON_LIST[bianhao][1]}]({pokemon_info[1]})\n物攻:{W_atk}[{POKEMON_LIST[bianhao][2]}]({pokemon_info[2]})\n物防:{W_def}[{POKEMON_LIST[bianhao][3]}]({pokemon_info[3]})\n特攻:{M_atk}[{POKEMON_LIST[bianhao][4]}]({pokemon_info[4]})\n特防:{M_def}[{POKEMON_LIST[bianhao][5]}]({pokemon_info[5]})\n速度:{speed}[{POKEMON_LIST[bianhao][6]}]({pokemon_info[6]})\n努力值:{pokemon_info[7]},{pokemon_info[8]},{pokemon_info[9]},{pokemon_info[10]},{pokemon_info[11]},{pokemon_info[12]}\n'
        )
    )
    mes.append(MessageSegment.text(f'可用技能\n{pokemon_info[14]}'))
    jinenglist = get_level_jineng(pokemon_info[0], bianhao)
    mes.append(MessageSegment.text('\n当前等级可学习的技能为：\n'))
    for jn_name in jinenglist:
        mes.append(MessageSegment.text(f'{jn_name},'))
    if pokemon_info[0] < 100:
        need_exp = get_need_exp(bianhao, pokemon_info[0]) - pokemon_info[15]
        mes.append(MessageSegment.text(f'\n下级所需经验{need_exp}'))
    buttonlist = ['学习技能', '遗忘技能']
    buttons = [
        Button('📖学习技能', f'学习技能 {pokename}', action=2),
        Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
    ]
    for pokemonid in POKEMON_LIST:
        if len(POKEMON_LIST[pokemonid]) > 8:
            if str(POKEMON_LIST[pokemonid][8]) == str(bianhao):
                if POKEMON_LIST[pokemonid][9].isdigit():
                    mes.append(
                        MessageSegment.text(
                            f'\nLv.{POKEMON_LIST[pokemonid][9]} 可进化为{POKEMON_LIST[pokemonid][0]}'
                        )
                    )
                else:
                    mes.append(
                        MessageSegment.text(
                            f'\n使用道具 {POKEMON_LIST[pokemonid][9]} 可进化为{POKEMON_LIST[pokemonid][0]}'
                        )
                    )
                buttons.append(
                    Button(
                        f'⏫宝可梦进化{POKEMON_LIST[pokemonid][0]}',
                        f'宝可梦进化{POKEMON_LIST[pokemonid][0]}',
                    )
                )
    # print(buttonlist)
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


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
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('领取初始精灵', '领取初始宝可梦'))
async def get_chushi_pokemon(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.finish(
            ev,
            '请输入 领取初始精灵+宝可梦名称 中间用空格隔开。',
            at_sender=True,
        )
    pokename = args[0]
    uid = ev.user_id

    my_pokemon = POKE._get_pokemon_num(uid)
    if my_pokemon > 0:
        return await bot.send(
            '您已经有精灵了，无法领取初始精灵。', at_sender=True
        )

    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    if bianhao not in chushi_list:
        return await bot.send(
            f'{POKEMON_LIST[bianhao][0]}不属于初始精灵，无法领取。',
            at_sender=True,
        )
    startype = get_pokemon_star(uid)
    pokemon_info = add_pokemon(uid, bianhao, startype)
    POKE._add_pokemon_group(uid, bianhao)

    POKE.update_pokemon_star(uid, bianhao, startype)
    go_didian = '1号道路'
    name = uid
    if ev.sender:
        sender = ev.sender
        if sender.get('nickname', '') != '':
            name = sender['nickname']
    POKE._new_map_info(uid, go_didian, name)

    HP, W_atk, W_def, M_atk, M_def, speed = get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    picfile = os.path.join(
        FILE_PATH, 'icon', f'{POKEMON_LIST[bianhao][0]}.png'
    )
    mes = []
    mes.append(MessageSegment.text('恭喜！您领取到了初始精灵\n'))
    img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao][0]}.png'
    img = await convert_img(img)
    # mes.append(MessageSegment.image(img))
    mes.append(
        MessageSegment.text(
            f'{starlist[startype]}{POKEMON_LIST[bianhao][0]}\nLV:{pokemon_info[0]}\n属性:{POKEMON_LIST[bianhao][7]}\n性格:{pokemon_info[13]}\nHP:{HP}({pokemon_info[1]})\n物攻:{W_atk}({pokemon_info[2]})\n物防:{W_def}({pokemon_info[3]})\n特攻:{M_atk}({pokemon_info[4]})\n特防:{M_def}({pokemon_info[5]})\n速度:{speed}({pokemon_info[6]})\n'
        )
    )
    mes.append(MessageSegment.text(f'可用技能\n{pokemon_info[14]}'))
    buttonlist = [f'精灵状态{pokename}', '野外探索']
    buttons = [
        Button('📖精灵状态', f'精灵状态{pokename}'),
        Button('🏝️野外探索', '野外探索'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_fullmatch(['宝可梦重开'])
async def chongkai_pokemon(bot, ev: Event):
    uid = ev.user_id
    chongkai(uid)
    mes = '重开成功，请重新领取初始精灵开局'
    buttons = [
        Button('✅领取初始精灵', '领取初始精灵', action=2),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('放生精灵', '放生宝可梦'))
async def fangsheng_pokemon(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send(
            '请输入 放生精灵+宝可梦名称 中间用空格隔开。', at_sender=True
        )
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )

    my_pokemon = POKE._get_pokemon_num(uid)
    if my_pokemon == 1:
        return await bot.send('您就这么一只精灵了，无法放生。', at_sender=True)
    fangshen(uid, bianhao)
    startype = POKE.get_pokemon_star(uid, bianhao)
    my_team = POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    if str(bianhao) in pokemon_list:
        pokemon_list.remove(str(bianhao))
        pokemon_str = ','.join(pokemon_list)
        POKE._add_pokemon_group(uid, pokemon_str)
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
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    jinengname = args[1]

    startype = POKE.get_pokemon_star(uid, bianhao)
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
    if jinengname not in jinengzu:
        return await bot.send(
            '学习失败，不存在该技能或该技能无法在当前等级学习(学习机技能请使用技能学习机进行教学)。',
            at_sender=True,
        )
    jineng = pokemon_info[14] + ',' + jinengname

    POKE._add_pokemon_jineng(uid, bianhao, jineng)
    mes = f'恭喜，您的精灵 {starlist[startype]}{POKEMON_LIST[bianhao][0]}学会了技能{jinengname}'
    buttonlist = ['学习技能', '遗忘技能', f'精灵状态{pokename}']
    buttons = [
        Button('📖学习技能', f'学习技能 {pokename}', action=2),
        Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
        Button('📖精灵状态', f'精灵状态{pokename}'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
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
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    jinengname = args[1]

    startype = POKE.get_pokemon_star(uid, bianhao)
    if str(jinengname) not in str(pokemon_info[14]):
        return await bot.send(
            f'遗忘失败，您的精灵 {starlist[startype]}{POKEMON_LIST[bianhao][0]}未学习{jinengname}。',
            at_sender=True,
        )
    jinenglist = re.split(',', pokemon_info[14])
    if len(jinenglist) == 1:
        return await bot.send(
            '遗忘失败，需要保留1个技能用于对战哦。', at_sender=True
        )
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
        Button('📖精灵状态', f'精灵状态{pokename}'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(['精灵技能信息'])
async def get_jineng_info(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send(
            '请输入 精灵技能信息+技能名称 中间用空格隔开。', at_sender=True
        )
    jineng = args[0]
    try:
        jinenginfo = JINENG_LIST[jineng]
        mes = f'名称：{jineng}\n属性：{jinenginfo[0]}\n类型：{jinenginfo[1]}\n威力：{jinenginfo[2]}\n命中：{jinenginfo[3]}\nPP值：{jinenginfo[4]}\n描述：{jinenginfo[5]}'
        await bot.send(mes)
    except:
        await bot.send(
            '无法找到该技能，请输入正确的技能名称。', at_sender=True
        )


@sv_pokemon_duel.on_prefix(['宝可梦进化'])
async def get_jineng_info(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 宝可梦进化+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    zhongzu = POKEMON_LIST[bianhao]
    if len(zhongzu) < 9:
        return await bot.send(
            '暂时没有该宝可梦的进化信息，请等待后续更新。', at_sender=True
        )
    if zhongzu[8] == '-':
        return await bot.send('暂时没有该宝可梦的进化信息。', at_sender=True)
    use_flag = 0

    my_pokemon_list = POKE._get_my_pokemon(uid)
    for pokemonid in my_pokemon_list:
        if int(pokemonid[0]) == int(bianhao):
            use_flag = 1
            break
    if use_flag == 1:
        return await bot.send(
            f'已经有{pokename}了，不能同时拥有同一只精灵哦。', at_sender=True
        )

    kid_poke_id = int(zhongzu[8])
    pokemon_info = get_pokeon_info(uid, kid_poke_id)

    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[kid_poke_id][0]}，无法进化。',
            at_sender=True,
        )
    if zhongzu[9].isdigit():
        if pokemon_info[0] < int(zhongzu[9]):
            return await bot.send(
                f'进化成{POKEMON_LIST[bianhao][0]}需要 Lv.{zhongzu[9]}\n您的{POKEMON_LIST[kid_poke_id][0]}等级为 Lv.{pokemon_info[0]}，无法进化',
                at_sender=True,
            )
        else:
            startype = POKE.get_pokemon_star(uid, kid_poke_id)
            POKE._delete_poke_star_bianhao(uid, kid_poke_id)
            POKE.update_pokemon_star(uid, bianhao, startype)
            POKE._add_pokemon_id(uid, kid_poke_id, bianhao)
            my_team = POKE.get_pokemon_group(uid)
            pokemon_list = my_team.split(',')
            if str(kid_poke_id) in pokemon_list:
                team_list = []
                for pokeid in pokemon_list:
                    if int(pokeid) == int(kid_poke_id):
                        pokeid = bianhao
                    team_list.append(str(pokeid))
                pokemon_str = ','.join(team_list)
                POKE._add_pokemon_group(uid, pokemon_str)
            mes = f'恭喜！您的宝可梦 {starlist[startype]}{POKEMON_LIST[kid_poke_id][0]} 进化成了 {starlist[startype]}{POKEMON_LIST[bianhao][0]}'
            buttons = [
                Button('📖学习技能', f'学习技能 {pokename}', action=2),
                Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
                Button('📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes, buttons)
    else:
        mypropnum = POKE._get_pokemon_prop(uid, zhongzu[9])
        if mypropnum == 0:
            return await bot.send(
                f'进化成{POKEMON_LIST[bianhao][0]}需要道具{zhongzu[9]}，您还没有该道具，无法进化',
                at_sender=True,
            )
        else:
            POKE._add_pokemon_id(uid, kid_poke_id, bianhao)
            my_team = POKE.get_pokemon_group(uid)
            pokemon_list = my_team.split(',')
            POKE._add_pokemon_prop(uid, zhongzu[9], -1)
            if str(kid_poke_id) in pokemon_list:
                team_list = []
                for pokeid in pokemon_list:
                    if int(pokeid) == int(kid_poke_id):
                        pokeid = bianhao
                    team_list.append(str(pokeid))
                pokemon_str = ','.join(team_list)
                POKE._add_pokemon_group(uid, pokemon_str)
            mes = f'恭喜！您的宝可梦 {POKEMON_LIST[kid_poke_id][0]} 进化成了 {POKEMON_LIST[bianhao][0]}'
            buttons = [
                Button('📖学习技能', f'学习技能 {pokename}', action=2),
                Button('📖遗忘技能', f'遗忘技能 {pokename}', action=2),
                Button('📖精灵状态', f'精灵状态{pokename}'),
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

    myegglist = POKE.get_pokemon_egg_list(uid, page)
    if myegglist == 0:
        return await bot.send('您还没有精灵蛋', at_sender=True)
    egg_num = POKE.get_pokemon_egg_num(uid)
    page_num = math.floor(egg_num / 30)
    mes = ''
    mes += '您的精灵蛋信息为(一页只显示30种按数量和编号排序):\n'
    for pokemoninfo in myegglist:
        mes += f'{POKEMON_LIST[pokemoninfo[0]][0]} 数量 {pokemoninfo[1]}\n'
    if page_num > 0:
        mes += f'第({page+1}/{page_num+1})页'
    buttons = [
        Button('📖宝可梦孵化', '宝可梦孵化', action=2),
        Button('📖重置个体值', '重置个体值', action=2),
        Button('📖丢弃精灵蛋', '丢弃精灵蛋', action=2),
    ]
    if page > 0:
        uppage = page - 1
        buttons.append(Button('⬅️上一页', f'我的精灵蛋 {uppage}'))
    if page_num > 0:
        Button(f'⏺️跳转({page + 1}/{page_num + 1})', '我的精灵蛋', action=2)
    if page < page_num:
        dowmpage = page + 1
        buttons.append(Button('➡️下一页', f'我的精灵蛋 {dowmpage}'))

    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('丢弃精灵蛋', '丢弃宝可梦蛋'))
async def my_pokemon_egg_use(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send(
            '请输入 丢弃精灵蛋+宝可梦名称+丢弃数量。', at_sender=True
        )

    uid = ev.user_id
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)

    egg_num = POKE.get_pokemon_egg(uid, bianhao)
    if egg_num == 0:
        return await bot.send(
            f'您还没有{pokename}的精灵蛋哦。', at_sender=True
        )
    if len(args) == 2:
        eggnum = int(args[1])
        if eggnum > egg_num:
            eggnum = egg_num
    else:
        eggnum = egg_num
    POKE._add_pokemon_egg(uid, bianhao, 0 - eggnum)
    mes = f'成功！您丢弃了{pokename}精灵蛋x{eggnum}'
    buttonlist = ['宝可梦孵化', '重置个体值', '我的精灵蛋']
    buttons = [
        Button('📖宝可梦孵化', '宝可梦孵化', action=2),
        Button('📖重置个体值', '重置个体值', action=2),
        Button('📖我的精灵蛋', '我的精灵蛋', action=2),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(('重置个体值', '个体值重置'))
async def my_pokemon_gt_up(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 重置个体值+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    my_pokemon_info = get_pokeon_info(uid, bianhao)
    if my_pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )
    HP_o, W_atk_o, W_def_o, M_atk_o, M_def_o, speed_o = get_pokemon_shuxing(
        bianhao, my_pokemon_info
    )
    kidid = get_pokemon_eggid(bianhao)

    egg_num = POKE.get_pokemon_egg(uid, kidid)
    if egg_num == 0:
        return await bot.send(
            f'重置个体值需要消耗1枚同一种类型的精灵蛋哦，您没有{POKEMON_LIST[kidid][0]}的精灵蛋。',
            at_sender=True,
        )
    POKE._add_pokemon_egg(uid, kidid, -1)
    startype = POKE.get_pokemon_star(uid, bianhao)
    new_star_type = get_pokemon_star(uid)
    if new_star_type > startype:
        startype = new_star_type
        POKE.update_pokemon_star(uid, bianhao, startype)
    pokemon_info = new_pokemon_gt(uid, bianhao, startype)

    HP, W_atk, W_def, M_atk, M_def, speed = get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    mes = f'{starlist[startype]}{pokename}个体值重置成功，重置后属性如下\n'
    mes += f'HP:{HP_o}/{HP}({my_pokemon_info[1]}/{pokemon_info[1]})\n物攻:{W_atk_o}/{W_atk}({my_pokemon_info[2]}/{pokemon_info[2]})\n物防:{W_def_o}/{W_def}({my_pokemon_info[3]}/{pokemon_info[3]})\n特攻:{M_atk_o}/{M_atk}({my_pokemon_info[4]}/{pokemon_info[4]})\n特防:{M_def_o}/{M_def}({my_pokemon_info[5]}/{pokemon_info[5]})\n速度:{speed_o}/{speed}({my_pokemon_info[6]}/{pokemon_info[6]})'
    # mes.append(MessageSegment.image(img))
    buttonlist = [f'精灵状态{pokename}', f'重置个体值{pokename}']
    buttons = [
        Button('📖精灵状态', f'精灵状态{pokename}'),
        Button('📖重置个体值', f'重置个体值{pokename}'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)


@sv_pokemon_duel.on_prefix(['宝可梦孵化'])
async def get_pokemon_form_egg(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 宝可梦孵化+宝可梦名称。', at_sender=True)
    pokename = args[0]
    uid = ev.user_id
    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)

    egg_num = POKE.get_pokemon_egg(uid, bianhao)
    if egg_num == 0:
        return await bot.send(
            f'您还没有{pokename}的精灵蛋哦。', at_sender=True
        )
    use_flag = 0
    my_pokemon_list = POKE._get_my_pokemon(uid)
    for pokemonid in my_pokemon_list:
        if int(pokemonid[0]) == int(bianhao):
            use_flag = 1
            break
    if use_flag == 1:
        return await bot.send(
            f'已经有{pokename}了，不能同时拥有同一只精灵哦。', at_sender=True
        )
    POKE._add_pokemon_egg(uid, bianhao, -1)
    pokemon_info = add_pokemon(uid, bianhao)
    startype = get_pokemon_star(uid)
    POKE.update_pokemon_star(uid, bianhao, startype)
    HP, W_atk, W_def, M_atk, M_def, speed = get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    mes = ''
    mes += '恭喜！孵化成功了\n'
    mes += f'{starlist[startype]}{POKEMON_LIST[bianhao][0]}\nLV:{pokemon_info[0]}\n属性:{POKEMON_LIST[bianhao][7]}\n性格:{pokemon_info[13]}\nHP:{HP}({pokemon_info[1]})\n物攻:{W_atk}({pokemon_info[2]})\n物防:{W_def}({pokemon_info[3]})\n特攻:{M_atk}({pokemon_info[4]})\n特防:{M_def}({pokemon_info[5]})\n速度:{speed}({pokemon_info[6]})\n'
    mes += f'可用技能\n{pokemon_info[14]}'
    my_team = POKE.get_pokemon_group(uid)
    pokemon_list = my_team.split(',')
    if len(pokemon_list) < 4:
        pokemon_list.append(str(bianhao))
        pokemon_str = ','.join(pokemon_list)
        POKE._add_pokemon_group(uid, pokemon_str)
    buttonlist = [f'精灵状态{pokename}', f'重置个体值{pokename}']
    buttons = [
        Button('📖精灵状态', f'精灵状态{pokename}'),
        Button('📖重置个体值', f'重置个体值{pokename}'),
    ]
    if ev.bot_id == 'qqgroup':
        await bot.send(mes, at_sender=True)
    else:
        await bot.send_option(mes, buttons)

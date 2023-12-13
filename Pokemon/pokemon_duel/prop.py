import math
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.message_models import Button
import json
import pytz
import time
from .pokeconfg import *
from .pokemon import *
from .PokeCounter import *
from .until import *
from pathlib import Path
from gsuid_core.gss import gss
from gsuid_core.logger import logger
from gsuid_core.aps import scheduler
from ..utils.dbbase.ScoreCounter import SCORE_DB

Excel_path = Path(__file__).parent
with Path.open(Excel_path / 'prop.json', encoding='utf-8') as f:
    prop_dict = json.load(f)
    proplist = prop_dict['proplist']

TEXT_PATH = Path(__file__).parent / 'texture2D'

sv_pokemon_prop = SV('宝可梦道具', priority=5)


@sv_pokemon_prop.on_fullmatch(['道具帮助', '宝可梦道具帮助'])
async def pokemon_help_prop(bot, ev: Event):
    msg = """
             宝可梦道具帮助
指令：
1、道具商店(查看商城出售的道具)
2、道具信息[道具名](查看道具的具体信息)
3、购买道具[道具名][数量](购买道具,数量默认为1)
4、使用道具[道具名][精灵名][数量](对宝可梦使用道具,数量默认为1)
5、我的道具(查看我的道具列表)
6、查看交易所([类型][名称])(查看交易所寄售的商品，类型名称可为空)
7、交易所上架[类型][名称][数量][单价](上架物品到交易所，例：交易所上架 精灵蛋 皮丘 5 8888)
8、交易所购买[商品ID][数量](交易所购买商品，数量默认为1)
9、我的寄售(查看我寄售在交易所的商品)
注：
交易所寄售的商品出售成功会收取10%的手续费
 """
    buttons = [
        Button('✅道具商店', '道具商店'),
        Button('✅我的道具', '我的道具'),
        Button('💰查看交易所', '查看交易所'),
        Button('✅购买道具', '购买道具', action=2),
        Button('✅道具信息', '道具信息', action=2),
        Button('✅使用道具', '使用道具', action=2),
    ]
    await bot.send_option(msg, buttons)


@sv_pokemon_prop.on_fullmatch(['道具商店'])
async def prop_shop_list(bot, ev: Event):
    uid = ev.user_id

    mychenghao, huizhang = get_chenghao(uid)

    my_score = SCORE.get_score(uid)
    mes = f'我的金币:{my_score}\n商品列表(商品随得到的徽章增多)\n'
    propinfolist = ''
    for propinfo in proplist:
        if (
            proplist[propinfo]['score'] > 0
            and huizhang >= proplist[propinfo]['huizhang']
        ):
            propinfolist += f"{propinfo} [{proplist[propinfo]['type']}] 售价:{proplist[propinfo]['score']}\n"
    if propinfolist == '':
        mes = '商店暂时没有出售的物品，去挑战道馆试试吧'
        buttons = [
            Button('挑战道馆', '挑战道馆'),
        ]
    else:
        mes += propinfolist
        buttons = [
            Button('✅购买道具', '购买道具', action=2),
            Button('📖道具信息', '道具信息', action=2),
        ]
    await bot.send_option(mes, buttons)


@sv_pokemon_prop.on_prefix(['道具信息'])
async def prop_info(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 道具信息+道具名称', at_sender=True)
    propname = args[0]
    uid = ev.user_id
    mychenghao, huizhang = get_chenghao(uid)
    try:
        propinfo = proplist[propname]
        mes = f"名称：{propname}\n类型：{propinfo['type']}\n描述：{propinfo['content']}"
        if propinfo['score'] > 0:
            mes += f"\n售价：{propinfo['score']}"
        if propinfo['score'] > 0 and int(huizhang) >= propinfo['huizhang']:
            buttons = [
                Button('✅购买道具', f'购买道具 {propname}', action=2),
            ]
            await bot.send_option(mes, buttons)
        else:
            await bot.send(mes)
    except:
        return await bot.send(
            '无法找到该道具，请输入正确的道具名称。', at_sender=True
        )


@sv_pokemon_prop.on_prefix(['购买道具'])
async def prop_buy(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send(
            '请输入 购买道具+道具名称+道具数量 用空格隔开', at_sender=True
        )
    propname = args[0]
    if len(args) == 2:
        propnum = int(args[1])
    else:
        propnum = 1
    uid = ev.user_id

    mychenghao, huizhang = get_chenghao(uid)
    try:
        propinfo = proplist[propname]
        if propinfo['score'] == 0:
            return await bot.send('无法购买该道具', at_sender=True)
        my_score = SCORE.get_score(uid)
        use_score = propinfo['score'] * propnum
        if propinfo['huizhang'] > int(huizhang):
            return await bot.send(
                f"需要{propinfo['huizhang']}枚徽章才能开放{propname}的购买",
                at_sender=True,
            )
        if use_score > my_score:
            return await bot.send(
                f'购买{propnum}件{propname}需要金币{use_score},您的金币不足',
                at_sender=True,
            )
        SCORE.update_score(uid, 0 - use_score)
        await POKE._add_pokemon_prop(uid, propname, propnum)
        mes = f'恭喜！您花费了{use_score}金币成功购买了{propnum}件{propname}'
        if propinfo['type'] == '消耗品':
            buttons = [
                Button('✅使用道具', f'使用道具 {propname}', action=2),
            ]
            await bot.send_option(mes, buttons)
        else:
            await bot.send(mes)
    except:
        return await bot.send(
            '无法找到该道具，请输入正确的道具名称。', at_sender=True
        )


@sv_pokemon_prop.on_prefix(['使用道具'])
async def prop_use(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 2:
        return await bot.send(
            '请输入 使用道具+道具名称+精灵名+道具数量 用空格隔开',
            at_sender=True,
        )
    propname = args[0]
    pokename = args[1]
    if len(args) == 3:
        propnum = int(args[2])
    else:
        propnum = 1
    uid = ev.user_id

    bianhao = get_poke_bianhao(pokename)
    if bianhao == 0:
        return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
    pokemon_info = get_pokeon_info(uid, bianhao)
    if pokemon_info == 0:
        return await bot.send(
            f'您还没有{POKEMON_LIST[bianhao][0]}。', at_sender=True
        )

    propkeylist = proplist.keys()
    if propname not in propkeylist:
        return await bot.send(
            '无法找到该道具，请输入正确的道具名称。', at_sender=True
        )
    propinfo = proplist[propname]
    if propinfo['type'] == '进化':
        return await bot.send(
            '进化类道具无法直接使用，进华时会自动消耗。', at_sender=True
        )
    if propinfo['use'][0] == '性格':
        propnum = 1
    mypropnum = await POKE._get_pokemon_prop(uid, propname)
    if mypropnum == 0:
        return await bot.send(f'您还没有{propname}哦。', at_sender=True)
    if mypropnum < propnum:
        return await bot.send(
            f'您的{propname}数量小于{propnum}，使用失败。', at_sender=True
        )
    if propinfo['use'][0] == '性格':
        if pokemon_info[13] == propinfo['use'][1]:
            return await bot.send(
                f'您的{POKEMON_LIST[bianhao][0]}的性格已经是{pokemon_info[13]}了，使用失败。',
                at_sender=True,
            )
        POKE._add_pokemon_xingge(uid, bianhao, propinfo['use'][1])
        await POKE._add_pokemon_prop(uid, propname, -1)
        mes = f"使用成功！您的{POKEMON_LIST[bianhao][0]}的性格变成了{propinfo['use'][1]}。"
        buttons = [
            Button('📖精灵状态', f'精灵状态{pokename}'),
        ]
        await bot.send_option(mes, buttons)
    elif propinfo['use'][0] == '努力':
        if propinfo['use'][2] > 0:
            nl_z = (
                pokemon_info[7]
                + pokemon_info[8]
                + pokemon_info[9]
                + pokemon_info[10]
                + pokemon_info[11]
                + pokemon_info[12]
            )
            if nl_z >= 510:
                return await bot.send(
                    f'使用失败,{POKEMON_LIST[bianhao][0]}的基础值已经无法再提升了。',
                    at_sender=True,
                )
            nl_index = int(propinfo['use'][1] + 7)
            if pokemon_info[nl_index] >= 252:
                return await bot.send(
                    f"使用失败,{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值已经无法再提升了。",
                    at_sender=True,
                )
            add_num = propnum * propinfo['use'][2]
            need_num = 252 - pokemon_info[nl_index]
            if add_num < need_num:
                use_peop_num = propnum
            else:
                use_peop_num = math.ceil(
                    propnum - (add_num - need_num) / propinfo['use'][2]
                )
            add_num = use_peop_num * propinfo['use'][2]
            change_nl = min(252, add_num + pokemon_info[nl_index])
            change_nl_num = change_nl - pokemon_info[nl_index]
            # print(nl_index)
            pokemon_info = list(pokemon_info)
            pokemon_info[nl_index] = change_nl

            POKE._add_pokemon_nuli(
                uid,
                bianhao,
                pokemon_info[7],
                pokemon_info[8],
                pokemon_info[9],
                pokemon_info[10],
                pokemon_info[11],
                pokemon_info[12],
            )
            mes = f"使用成功！{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值提升了{change_nl_num}点"
            await POKE._add_pokemon_prop(uid, propname, 0 - use_peop_num)
            buttons = [
                Button('📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes, buttons)
        else:
            nl_index = int(propinfo['use'][1] + 7)
            if pokemon_info[nl_index] == 0:
                return await bot.send(
                    f"使用失败,{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值已经无法再降低了。",
                    at_sender=True,
                )
            add_num = 0 - propnum * propinfo['use'][2]
            need_num = pokemon_info[nl_index]
            if add_num < need_num:
                use_peop_num = propnum
            else:
                use_peop_num = math.ceil(
                    propnum - (add_num - need_num) / (0 - propinfo['use'][2])
                )
            add_num = use_peop_num * propinfo['use'][2]
            change_nl = max(0, add_num + pokemon_info[nl_index])
            change_nl_num = pokemon_info[nl_index] - change_nl
            pokemon_info = list(pokemon_info)
            pokemon_info[nl_index] = change_nl

            POKE._add_pokemon_nuli(
                uid,
                bianhao,
                pokemon_info[7],
                pokemon_info[8],
                pokemon_info[9],
                pokemon_info[10],
                pokemon_info[11],
                pokemon_info[12],
            )
            mes = f"使用成功！{POKEMON_LIST[bianhao][0]}的{zhongzu_list[propinfo['use'][1]][1]}基础值降低了{change_nl_num}点"
            await POKE._add_pokemon_prop(uid, propname, 0 - use_peop_num)
            buttons = [
                Button('📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes, buttons)
    elif propinfo['use'][0] == '升级':
        if propinfo['use'][1] == 'level':
            if pokemon_info[0] == 100:
                return await bot.send(
                    f'使用失败,{POKEMON_LIST[bianhao][0]}的等级已经无法再提升了。',
                    at_sender=True,
                )
            add_level = propinfo['use'][2] * propnum
            need_level = 100 - pokemon_info[0]
            if add_level <= need_level:
                use_peop_num = propnum
            else:
                use_peop_num = math.ceil(
                    propnum - (add_level - need_level) / propinfo['use'][2]
                )
            add_level = use_peop_num * propinfo['use'][2]
            now_level = pokemon_info[0] + add_level
            POKE._add_pokemon_level(uid, bianhao, now_level, 0)
            mes = (
                f'使用成功！{POKEMON_LIST[bianhao][0]}的等级提升了{add_level}'
            )
            await POKE._add_pokemon_prop(uid, propname, 0 - use_peop_num)
            buttons = [
                Button('📖精灵状态', f'精灵状态{pokename}'),
            ]
            await bot.send_option(mes, buttons)


@sv_pokemon_prop.on_fullmatch(['我的道具'])
async def prop_my_list(bot, ev: Event):
    uid = ev.user_id

    myproplist = await POKE.get_pokemon_prop_list(uid)
    if myproplist == 0:
        return await bot.send('您还没有道具哦。', at_sender=True)
    mes = ''
    for propinfo in myproplist:
        mes += f'{propinfo[0]} 数量 {propinfo[1]}\n'
    buttons = [
        Button('📖道具信息', '道具信息', action=2),
        Button('✅使用道具', '使用道具', action=2),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_prop.on_prefix(['交易所上架'])
async def exchange_up_prop(bot, ev: Event):
    #交易所上架 道具 奇异甜食 5 500
    uid = ev.user_id
    args = ev.text.split()
    if len(args) != 4:
        return await bot.send('请输入 交易所上架[类型][名称][数量][单价] 中间用空格分隔。\n如 交易所上架 精灵蛋 皮丘 5 8888', at_sender=True)
    proptype = args[0]
    if proptype not in ['道具','精灵蛋','宝可梦蛋','蛋']:
        return await bot.send('请输入正确的类型 道具/精灵蛋。', at_sender=True)
    propname = args[1]
    propnum = int(args[2])
    if propnum < 1:
        return await bot.send('上架商品的数量需大于1。', at_sender=True)
    score = int(args[3])
    if score < 10:
        return await bot.send('上架商品的价格需大于10。', at_sender=True)
    string = "0123456789"
    random_list = random.sample(list(string), 8)
    exchangeid = ''.join(random_list)
    if proptype == '道具':
        propkeylist = proplist.keys()
        if propname not in propkeylist:
            return await bot.send('无法找到该道具，请输入正确的道具名称。', at_sender=True)
        mypropnum = await POKE._get_pokemon_prop(uid, propname)
        if mypropnum == 0:
            return await bot.send(f'您还没有{propname}哦。', at_sender=True)
        if mypropnum < propnum:
            return await bot.send(f'您的{propname}数量小于{propnum}，上架失败。', at_sender=True)
        now_time = math.ceil(time.time())
        await POKE.new_exchange(exchangeid,proptype,propname,propnum,uid,score,now_time)
        await POKE._add_pokemon_prop(uid, propname, 0 - propnum)
        mes = f'您以单价{score}的价格成功上架了{propname}x{propnum}。'
    if proptype == '精灵蛋' or proptype == '宝可梦蛋' or proptype == '蛋':
        proptype = '精灵蛋'
        bianhao = get_poke_bianhao(propname)
        if bianhao == 0:
            return await bot.send('请输入正确的宝可梦名称。', at_sender=True)
        egg_num = await POKE.get_pokemon_egg(uid, bianhao)
        if egg_num == 0:
            return await bot.send(f'您还没有{pokename}的精灵蛋哦。', at_sender=True)
        if egg_num < propnum:
            return await bot.send(f'您的{pokename}精灵蛋数量小于{propnum}，上架失败。', at_sender=True)
        now_time = math.ceil(time.time())
        await POKE.new_exchange(exchangeid,'精灵蛋',bianhao,propnum,uid,score,now_time)
        await POKE._add_pokemon_egg(uid, bianhao, 0 - propnum)
        mes = f'您以单价{score}的价格成功上架了{propname}精灵蛋x{propnum}。'
    buttons = [
        Button('💰寄售商品','交易所上架', action=2),
        Button('💰购买商品','交易所购买', action=2),
        Button('💰我的寄售','我的寄售'),
        Button('💰查看交易所', '查看交易所'),
        Button('💰交易所筛选', '查看交易所', action=2),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_prop.on_prefix(['交易所下架'])
async def exchange_down_prop(bot, ev: Event):
    args = ev.text.split()
    if len(args) != 1:
        return await bot.send('请输入 交易所下架[商品ID]', at_sender=True)
    exchangeid = args[0]
    uid = ev.user_id
    exchange_info = await POKE._get_exchange_info(exchangeid)
    if exchange_info == 0:
        return await bot.send('请输入正确的商品ID或该商品已售出', at_sender=True)
    if exchange_info[3] != uid:
        return await bot.send('您不是该商品的上架人，无法执行下架操作', at_sender=True)
    if exchange_info[0] == '道具':
        await POKE._add_pokemon_prop(uid, exchange_info[1], int(exchange_info[2]))
        mes = f'您下架了{exchange_info[1]}{exchange_info[0]}x{exchange_info[2]}。'
    if exchange_info[0] == '精灵蛋':
        await POKE._add_pokemon_egg(uid, int(exchange_info[1]), int(exchange_info[2]))
        mes = f'您下架了{POKEMON_LIST[int(exchange_info[1])][0]}{exchange_info[0]}x{exchange_info[2]}。'
    await POKE.delete_exchange(exchangeid)
    buttons = [
        Button('💰寄售商品','交易所上架', action=2),
        Button('💰购买商品','交易所购买', action=2),
        Button('💰我的寄售','我的寄售'),
        Button('💰查看交易所', '查看交易所'),
        Button('💰交易所筛选', '查看交易所', action=2),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_prop.on_command(['查看交易所'])
async def show_exchange_list(bot, ev: Event):
    args = ev.text.split()
    upbutton = ''
    downbutton = ''
    if len(args) > 0:
        if args[0].isdigit():
            page = int(args[0]) - 1
            exchangenum,exchange_list = await POKE.get_exchange_list(page)
            page_num = math.floor(exchangenum / 30)
            if page > 0:
                upbutton = f'查看交易所{page}'
            if page_num > page + 1:
                downbutton = f'查看交易所{page+2}'
        else:
            proptype = args[0]
            if proptype not in ['道具','精灵蛋']:
                return await bot.send('请输入正确的类型 道具/精灵蛋。', at_sender=True)
            if len(args) == 1:
                page = 0
                exchangenum,exchange_list = await POKE.get_exchange_list_sx_type(proptype,page)
                page_num = math.floor(exchangenum / 30)
                if page > 0:
                    upbutton = f'查看交易所{proptype} {page}'
                if page_num > page + 1:
                    downbutton = f'查看交易所{proptype} {page+2}'
            else:
                if args[1].isdigit():
                    page = int(args[1]) - 1
                    exchangenum,exchange_list = await POKE.get_exchange_list_sx_type(proptype,page)
                    page_num = math.floor(exchangenum / 30)
                    if page > 0:
                        upbutton = f'查看交易所{proptype} {page}'
                    if page_num > page + 1:
                        downbutton = f'查看交易所{proptype} {page+2}'
                else:
                    propname = args[1]
                    if proptype == '精灵蛋':
                        exchangename = get_poke_bianhao(propname)
                    else:
                        exchangename = propname
                    page = 0
                    if len(args) == 2:
                        exchangenum,exchange_list = await POKE.get_exchange_list_sx_name(proptype,exchangename,page)
                        page_num = math.floor(exchangenum / 30)
                        if page > 0:
                            upbutton = f'查看交易所{proptype} {propname} {page}'
                        if page_num > page + 1:
                            downbutton = f'查看交易所{proptype} {propname} {page+2}'
                    if len(args) == 3:
                        page = int(args[2]) - 1
                        exchangenum,exchange_list = await POKE.get_exchange_list_sx_name(proptype,exchangename,page)
                        page_num = math.floor(exchangenum / 30)
                        if page > 0:
                            upbutton = f'查看交易所{proptype} {propname} {page}'
                        if page_num > page + 1:
                            downbutton = f'查看交易所{proptype} {propname} {page+2}'
    else:
        page = 0
        exchangenum,exchange_list = await POKE.get_exchange_list(page)
        page_num = math.floor(exchangenum / 30)
        if page > 0:
            upbutton = f'查看交易所{page}'
        if page_num > page + 1:
            downbutton = f'查看交易所{page+2}'
    if exchangenum == 0:
        return await bot.send('当前交易所没有寄售中的商品', at_sender=True)
    mes = '当前寄售中的商品为\n商品ID 类型 名称 数量 单价'
    for exchangeinfo in exchange_list:
        mes += f'\n{exchangeinfo[0]} {exchangeinfo[1]}'
        propname = exchangeinfo[2]
        if exchangeinfo[1] == '精灵蛋':
            propname = POKEMON_LIST[int(exchangeinfo[2])][0]
        mes += f' {propname} {exchangeinfo[3]} {exchangeinfo[4]}'
    buttons = [
        Button('💰我的寄售','我的寄售'),
        Button('💰寄售商品','交易所上架', action=2),
        Button('💰购买商品','交易所购买', action=2),
    ]
    if upbutton != '':
        buttons.append(Button('上一页',f'{upbutton}', action=2))
    if downbutton != '':
        buttons.append(Button('下一页',f'{downbutton}', action=2))
    await bot.send_option(mes, buttons)

@sv_pokemon_prop.on_command(['交易所购买'])
async def exchange_buy_prop(bot, ev: Event):
    args = ev.text.split()
    if len(args) < 1:
        return await bot.send('请输入 交易所购买[商品ID][数量] 用空格分隔，数量默认为1', at_sender=True)
    exchangeid = args[0]
    uid = ev.user_id
    exchange_info = await POKE._get_exchange_info(exchangeid)
    if exchange_info == 0:
        return await bot.send('请输入正确的商品ID或该商品已售出', at_sender=True)
    if len(args) == 2:
        buy_num = int(args[1])
    else:
        buy_num = 1
    if buy_num > int(exchange_info[2]):
        return await bot.send(f'寄售中物品数量不足{buy_num}，请重新输入数量', at_sender=True)
    need_score = buy_num * int(exchange_info[4])
    my_score = SCORE.get_score(uid)
    if need_score > my_score:
        if exchange_info[0] == '精灵蛋':
            return await bot.send(f'购买{buy_num}件{POKEMON_LIST[int(exchange_info[1])][0]}{exchange_info[0]}需要金币{need_score}，您的金币不足', at_sender=True)
        if exchange_info[0] == '道具':
            return await bot.send(f'购买{buy_num}件{exchange_info[1]}需要金币{need_score}，您的金币不足', at_sender=True)
    if buy_num == int(exchange_info[2]):
        await POKE.delete_exchange(exchangeid)
    else:
        await POKE.update_exchange(exchangeid, 0 - buy_num)
    if exchange_info[0] == '道具':
        await POKE._add_pokemon_prop(uid, exchange_info[1], buy_num)
        mes = f'您花费了{need_score}金币，成功购买了{exchange_info[1]}{exchange_info[0]}x{buy_num}。'
    if exchange_info[0] == '精灵蛋':
        await POKE._add_pokemon_egg(uid, int(exchange_info[1]), buy_num)
        mes = f'您花费了{need_score}金币，成功购买了{POKEMON_LIST[int(exchange_info[1])][0]}{exchange_info[0]}x{buy_num}。'
    SCORE.update_score(uid, 0 - need_score)
    get_score = math.ceil(need_score * 0.9)
    SCORE.update_score(exchange_info[3], get_score)
    buttons = [
        Button('💰寄售商品','交易所上架', action=2),
        Button('💰购买商品','交易所购买', action=2),
        Button('💰我的寄售','我的寄售'),
        Button('💰查看交易所', '查看交易所'),
        Button('💰交易所筛选', '查看交易所', action=2),
    ]
    await bot.send_option(mes, buttons)

@sv_pokemon_prop.on_command(['我的寄售'])
async def show_exchange_list_my(bot, ev: Event):
    args = ev.text.split()
    upbutton = ''
    downbutton = ''
    uid = ev.user_id
    if len(args) > 0:
        page = int(args[0]) - 1
        exchangenum,exchange_list = await POKE.get_exchange_list_my(uid,page)
        page_num = math.floor(exchangenum / 30)
        if page > 0:
            upbutton = f'我的寄售{page}'
        if page_num > page + 1:
            downbutton = f'我的寄售{page+2}'
    else:
        page = 0
        exchangenum,exchange_list = await POKE.get_exchange_list_my(uid,page)
        page_num = math.floor(exchangenum / 30)
        if page > 0:
            upbutton = f'我的寄售{page}'
        if page_num > page + 1:
            downbutton = f'我的寄售{page+2}'
    if exchangenum == 0:
        return await bot.send('您没有寄售中的商品', at_sender=True)
    mes = '您当前寄售中的商品为\n商品ID 类型 名称 数量 单价'
    for exchangeinfo in exchange_list:
        mes += f'\n{exchangeinfo[0]} {exchangeinfo[1]}'
        propname = exchangeinfo[2]
        if exchangeinfo[1] == '精灵蛋':
            propname = POKEMON_LIST[int(exchangeinfo[2])][0]
        mes += f' {propname} {exchangeinfo[3]} {exchangeinfo[4]}'
    buttons = [
        Button('💰寄售商品','交易所上架', action=2),
        Button('💰购买商品','交易所购买', action=2),
    ]
    if upbutton != '':
        buttons.append(Button('上一页',f'{upbutton}', action=2))
    if downbutton != '':
        buttons.append(Button('下一页',f'{downbutton}', action=2))
    await bot.send_option(mes, buttons)

# 每日0点执行交易所7天无销售商品自动下架
@scheduler.scheduled_job('cron', hour ='*')
async def down_exchange_day():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.hour not in [0]:
        return
    findtime = math.ceil(time.time()) - 259200
    exchange_list = await POKE.get_exchange_list_time(findtime)
    if exchange_list == 0:
        logger.info('今日无超时寄售商品，无需下架')
        return
    down_num = 0
    for exchange_info in exchange_list:
        if exchange_info[1] == '道具':
            await POKE._add_pokemon_prop(exchange_info[4], exchange_info[2], int(exchange_info[3]))
        if exchange_info[1] == '精灵蛋':
            await POKE._add_pokemon_egg(exchange_info[4], int(exchange_info[2]), int(exchange_info[3]))
        await POKE.delete_exchange(exchange_info[0])
        down_num += 1
    logger.info(f'今日已执行{down_num}件交易所超期商品下架')









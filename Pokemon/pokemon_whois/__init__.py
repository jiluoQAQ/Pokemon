import random
import asyncio
import importlib
from os import path
import math
import pygtrie
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from async_timeout import timeout
from gsuid_core.models import Event
from PIL import Image, ImageDraw, ImageFont
from gsuid_core.message_models import Button
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.segment import MessageSegment
from . import poke_data
from ..utils.convert import DailyAmountLimiter
from ..utils.dbbase.GameCounter import GAME_DB
from ..utils.dbbase.ScoreCounter import SCORE_DB
from ..utils.dbbase.PokeCounter import PokeCounter
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH
from ..pokemon_duel.pokemon import *

PIC_SIDE_LENGTH = 25
LH_SIDE_LENGTH = 75
ONE_TURN_TIME = 20
WHOIS_NUM = 6
daily_whois_limiter = DailyAmountLimiter('whois', WHOIS_NUM, 0)
FILE_PATH = path.dirname(__file__)
FONTS_PATH = path.join(FILE_PATH, 'font')
FONTS_PATH = path.join(FONTS_PATH, 'sakura.ttf')

sv_pokemon_whois = SV('我是谁', priority=5)


class WinnerJudger:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}
        self.correct_win_pic = {}

    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)

    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def set_correct_win_pic(self, gid, pic):
        self.correct_win_pic[gid] = pic

    def get_correct_win_pic(self, gid):
        return self.correct_win_pic[gid]

    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid

    def get_correct_chara_id(self, gid):
        return (
            self.correct_chara_id[gid]
            if self.correct_chara_id.get(gid) is not None
            else 9999
        )

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = 9999


winner_judger = WinnerJudger()

class WinnerJudgerCC:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}
        self.correct_win_pic = {}

    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)

    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def set_correct_win_pic(self, gid, pic):
        self.correct_win_pic[gid] = pic

    def get_correct_win_pic(self, gid):
        return self.correct_win_pic[gid]

    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid

    def get_correct_chara_id(self, gid):
        return (
            self.correct_chara_id[gid]
            if self.correct_chara_id.get(gid) is not None
            else 9999
        )

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = 9999


winner_judger_cc = WinnerJudgerCC()

class WinnerJudgerSX:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_shuxlist = {}

    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)

    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def set_correct_shuxlist(self, gid, shuxlist):
        self.correct_shuxlist[gid] = shuxlist

    def get_correct_shuxlist(self, gid):
        return (
            self.correct_shuxlist[gid]
            if self.correct_shuxlist.get(gid) is not None
            else []
        )

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_shuxlist[gid] = []


winner_judger_sx = WinnerJudgerSX()

class Roster:
    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()

    def update(self):
        importlib.reload(poke_data)
        self._roster.clear()
        for idx, names in poke_data.CHARA_NAME.items():
            for n in names:
                if n not in self._roster:
                    self._roster[n] = idx
        self._all_name_list = self._roster.keys()

    def get_id(self, name):
        return self._roster[name] if name in self._roster else 9999


roster = Roster()


async def get_win_pic(name, enname):
    im = Image.new('RGB', (640, 464), (255, 255, 255))
    base_img = path.join(FILE_PATH, 'whois_bg.jpg')
    dtimg = Image.open(base_img)
    dtbox = (0, 0)
    im.paste(dtimg, dtbox)
    image = Image.open(CHAR_ICON_PATH / f'{name}.png').convert('RGBA')
    image = image.resize((230, 230))
    dtbox = (50, 60)
    im.paste(image, dtbox, mask=image.split()[3])

    draw = ImageDraw.Draw(im)
    line = enname
    font = ImageFont.truetype(FONTS_PATH, 40)
    draw.text(
        (470, 40),
        line,
        (255, 255, 0),
        font,
        'mm',
    )

    line = name
    font = ImageFont.truetype(FONTS_PATH, 42)
    draw.text(
        (470, 100),
        line,
        (255, 255, 0),
        font,
        'mm',
    )
    img = await convert_img(im)
    return img

shuxinglist = {
    1:'HP',
    2:'物攻',
    3:'物防',
    4:'特攻',
    5:'特防',
    6:'速度',
}

listshuxing = ['一般','飞行','火','超能力','水','虫','电','岩石','草','幽灵','冰','龙','格斗','恶','毒','钢','地面','妖精']

huanshoulist = ['梦幻','时拉比','基拉祈','霏欧纳','	代欧奇希斯','达克莱伊','谢米','比克提尼','凯路迪欧','美洛耶塔','盖诺赛克特','蒂安希','波尔凯尼恩','玛机雅娜','玛夏多','捷拉奥拉','美录坦','萨戮德','桃歹郎']

async def get_pokemon_tssx(sxlist, cc_list):
    shux_flag = 0
    while shux_flag == 0 and len(cc_list) > 0:
        atkshux = random.sample(cc_list, 1)[0]
        kezhilist = SHUXING_LIST[atkshux]
        beilv = 1
        kezhi_flag = 0
        for shuxing in sxlist:
            if float(kezhilist[shuxing]) > 1 or float(kezhilist[shuxing]) < 1:
                kezhi_flag = 1
            beilv = beilv * float(kezhilist[shuxing])
        if kezhi_flag == 1:
            shux_flag = 1
        cc_list.remove(atkshux)
    
    if beilv > 1:
        mes = f"被{atkshux}属性攻击{beilv}倍克制"
    if beilv == 1:
        mes = f"{atkshux}属性攻击会造成正常伤害"
    if beilv < 1 and beilv > 0:
        mes = f"只承受{atkshux}属性攻击{beilv}倍伤害"
    if beilv == 0:
        mes = f"受到{atkshux}属性攻击无效果"
    return cc_list,mes

async def get_pokemon_ts(name, cc_type):
    pokeid = roster.get_id(name)
    if cc_type == '属性':
        shuxing = POKEMON_LIST[pokeid][7]
        mes = f'精灵的属性为{shuxing}'
    if cc_type == '种族高':
        pokeinfo = POKEMON_LIST[pokeid]
        max_sx = 0
        max_sx_name = ''
        for shuzhi in range(1,7):
            if int(pokeinfo[shuzhi]) >= int(max_sx):
                if int(pokeinfo[shuzhi]) == int(max_sx):
                    max_sx_name = max_sx_name + f' {shuxinglist[shuzhi]}'
                else:
                    max_sx = pokeinfo[shuzhi]
                    max_sx_name = shuxinglist[shuzhi]
        mes = f'精灵最高的种族为{max_sx_name},数值为{max_sx}'
    if cc_type == '种族低':
        pokeinfo = POKEMON_LIST[pokeid]
        min_sx = 999
        min_sx_name = ''
        for shuzhi in range(1,7):
            if int(pokeinfo[shuzhi]) <= int(min_sx):
                if int(pokeinfo[shuzhi]) == int(min_sx):
                    min_sx_name = min_sx_name + f' {shuxinglist[shuzhi]}'
                else:
                    min_sx = pokeinfo[shuzhi]
                    min_sx_name = shuxinglist[shuzhi]
        mes = f'精灵最低的种族为{min_sx_name},数值为{min_sx}'
    if cc_type == '名字':
        name_len = len(name)
        mes = f'精灵名字{name_len}个字'
    if cc_type == '等级技能':
        len_dengji_jn = LEVEL_JINENG_LIST[pokeid]
        jn_num = len(len_dengji_jn)
        if jn_num > 3:
            dengji_jn_list = random.sample(len_dengji_jn, 4)
            mes = '精灵通过升级可以学习的其中4个技能为：'
            for jn_info in dengji_jn_list:
                mes += f'{jn_info[1]} '
        else:
            if jn_num == 0:
                mes = '精灵没有通过升级可以学习的技能'
            else:
                mes = f'精灵通过升级可以学习的{jn_num}个技能为：'
                for jn_info in len_dengji_jn:
                    mes += f'{jn_info[1]} '
    if cc_type == '特性':
        tx_list = POKETX_LIST[pokeid]
        if len(tx_list[1]) > 0:
            catch_num = int(math.floor(random.uniform(0, 100)))
            if catch_num <= 50:
                tx_name = random.sample(tx_list[1], 1)[0]
                mes = f'精灵的隐藏特性为{tx_name}'
            else:
                tx_name = random.sample(tx_list[0], 1)[0]
                mes = f'精灵其中一个普通特性为{tx_name}'
        else:
            tx_name = random.sample(tx_list[0], 1)[0]
            mes = f'精灵其中一个普通特性为{tx_name}'
    return mes

@sv_pokemon_whois.on_fullmatch('猜属性')
async def pokemon_shux_this(bot: Bot, ev: Event):
    if winner_judger_sx.get_on_off_status(ev.group_id):
        await bot.send('此轮游戏还没结束，请勿重复使用指令')
        return
    winner_judger_sx.turn_on(ev.group_id)
    sxlist = random.sample(listshuxing, 2)
    name_shux = ''
    for sxname in sxlist:
        name_shux += f'{sxname} '
    winner_judger_sx.set_correct_shuxlist(ev.group_id, sxlist)
    print(sxlist)
    cc_list = ['一般','飞行','火','超能力','水','虫','电','岩石','草','幽灵','冰','龙','格斗','恶','毒','钢','地面','妖精']
    mes = '下面每隔15秒会提示克制倍率，最多5条，猜测这是哪种属性组合'
    await bot.send(mes)
    cc_flag = 0
    buttons_a = [
        Button('猜一下', '/'),
    ]
    buttons_d = [
        Button('✅再来一局', '猜属性', action=1),
    ]
    index_num = 1
    while index_num < 6 and len(cc_list) > 0:
        cc_list, ts_mes = await get_pokemon_tssx(sxlist,cc_list)
        mes = f'提示{index_num}：{ts_mes}'
        await bot.send_option(mes, buttons_a)
        try:
            async with timeout(15):
                while True:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        gid = resp.group_id
                        uid = resp.user_id
                        sxcc = resp.text
                        # await bot.send(f'你说的是 {resp.text} 吧？')
                        sxcc_flag = 0
                        for sxname in sxlist:
                            if str(sxname) in str(sxcc) or str(sxname) == str(sxcc):
                                sxcc_flag = sxcc_flag + 1
                        if (int(sxcc_flag) == 2 and winner_judger_sx.get_winner(ev.group_id) == ''):
                            GAME = GAME_DB()
                            win_num = await GAME.update_game_num(uid, 'whosx')
                            mesg_d = []
                            mesg = ''
                            if daily_whois_limiter.check(uid):
                                SCORE = SCORE_DB()
                                await SCORE.update_score(uid, 1000)
                                daily_whois_limiter.increase(uid)
                                mesg = '获得1000金币\n'
                            winner_judger_sx.record_winner(ev.group_id, ev.user_id)
                            winner_judger_sx.turn_off(ev.group_id)
                            POKE = PokeCounter()
                            mapinfo = await POKE._get_map_now(uid)
                            myname = mapinfo[2]
                            myname = str(myname)[:10]
                            mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name_shux}'
                            chongsheng_num = await POKE.get_chongsheng_num(uid,9999)
                            if chongsheng_num >= 666:
                                huanshouname = random.sample(huanshoulist, 1)[0]
                                huanshouid = roster.get_id(huanshouname)
                                await POKE._add_pokemon_egg(uid, huanshouid, 1)
                                mes += f'\n{myname}获得了{huanshouname}精灵蛋x1'
                                await POKE._new_chongsheng_num(uid,9999)
                            await POKE.update_chongsheng(uid,9999,1)
                            await bot.send_option(mes, buttons_d)
                            return
        except asyncio.TimeoutError:
            pass
        index_num = index_num + 1
    if winner_judger_sx.get_winner(ev.group_id) != '':
        winner_judger_sx.turn_off(ev.group_id)
        return
    winner_judger_sx.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name_shux}'
    await bot.send_option(mes, buttons_d)

@sv_pokemon_whois.on_fullmatch('猜精灵')
async def pokemon_whois_cc(bot: Bot, ev: Event):
    if winner_judger_cc.get_on_off_status(ev.group_id):
        await bot.send('此轮游戏还没结束，请勿重复使用指令')
        return
    winner_judger_cc.turn_on(ev.group_id)
    chara_id_list = list(poke_data.CHARA_NAME.keys())
    poke_list = poke_data.CHARA_NAME
    random.shuffle(chara_id_list)
    winner_judger_cc.set_correct_chara_id(ev.group_id, chara_id_list[0])
    # print(chara_id_list[0])

    name = poke_list[chara_id_list[0]][0]
    enname = poke_list[chara_id_list[0]][1]
    win_mes = await get_win_pic(name, enname)
    winner_judger_cc.set_correct_win_pic(ev.group_id, win_mes)
    print(name)
    cc_list = ['属性','种族高','种族低','名字','等级技能','特性']
    mes = '下面每隔15秒会提示精灵的信息，总共6条，猜测这是哪只精灵'
    await bot.send(mes)
    cc_flag = 0
    buttons_a = [
        Button('猜一下', '/'),
    ]
    buttons_d = [
        Button('✅再来一局', '猜精灵', action=1),
        Button('📖查看图鉴', f'精灵图鉴{name}', action=1),
    ]
    for index in range(1,7):
        cc_type = random.sample(cc_list, 1)[0]
        ts_mes = await get_pokemon_ts(name,cc_type)
        mes = f'提示{index}：{ts_mes}'
        await bot.send_option(mes, buttons_a)
        try:
            async with timeout(15):
                while True:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        s = resp.text.strip()
                        gid = resp.group_id
                        uid = resp.user_id
                        cid = roster.get_id(s)
                        # await bot.send(f'你说的是 {resp.text} 吧？')
                        if (
                            cid != 9999
                            and cid
                            == winner_judger_cc.get_correct_chara_id(ev.group_id)
                            and winner_judger_cc.get_winner(ev.group_id) == ''
                        ):
                            GAME = GAME_DB()
                            win_num = await GAME.update_game_num(uid, 'whocc')
                            mesg_d = []
                            mesg = ''
                            if daily_whois_limiter.check(uid):
                                SCORE = SCORE_DB()
                                await SCORE.update_score(uid, 1000)
                                daily_whois_limiter.increase(uid)
                                mesg = '获得1000金币\n'
                            winner_judger_cc.record_winner(ev.group_id, ev.user_id)
                            win_mes = winner_judger_cc.get_correct_win_pic(gid)
                            winner_judger_cc.turn_off(ev.group_id)
                            POKE = PokeCounter()
                            mapinfo = await POKE._get_map_now(uid)
                            myname = mapinfo[2]
                            myname = str(myname)[:10]
                            mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name}'
                            chongsheng_num = await POKE.get_chongsheng_num(uid,151)
                            if chongsheng_num >= 233:
                                huanshouname = random.sample(huanshoulist, 1)[0]
                                huanshouid = roster.get_id(huanshouname)
                                await POKE._add_pokemon_egg(uid, huanshouid, 1)
                                mes += f'\n{myname}获得了{huanshouname}精灵蛋x1'
                                await POKE._new_chongsheng_num(uid,151)
                            await POKE.update_chongsheng(uid,151,1)
                            mesg_d.append(MessageSegment.text(mes))
                            mesg_d.append(MessageSegment.image(win_mes))
                            await bot.send_option(mesg_d, buttons_d)
                            return
        except asyncio.TimeoutError:
            pass
        cc_list.remove(cc_type)
    if winner_judger_cc.get_winner(ev.group_id) != '':
        winner_judger_cc.turn_off(ev.group_id)
        return
    winner_judger_cc.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name}'
    mesg_c = []
    mesg_c.append(MessageSegment.text(mes))
    mesg_c.append(MessageSegment.image(win_mes))
    await bot.send_option(mesg_c, buttons_d)

@sv_pokemon_whois.on_fullmatch('我是谁')
async def pokemon_whois(bot: Bot, ev: Event):
    if winner_judger.get_on_off_status(ev.group_id):
        await bot.send('此轮游戏还没结束，请勿重复使用指令')
        return
    winner_judger.turn_on(ev.group_id)
    chara_id_list = list(poke_data.CHARA_NAME.keys())
    poke_list = poke_data.CHARA_NAME
    random.shuffle(chara_id_list)
    winner_judger.set_correct_chara_id(ev.group_id, chara_id_list[0])
    # print(chara_id_list[0])

    name = poke_list[chara_id_list[0]][0]
    enname = poke_list[chara_id_list[0]][1]
    win_mes = await get_win_pic(name, enname)
    winner_judger.set_correct_win_pic(ev.group_id, win_mes)
    print(name)
    im = Image.new('RGB', (640, 464), (255, 255, 255))
    base_img = path.join(FILE_PATH, 'whois_bg.jpg')
    dtimg = Image.open(base_img)
    dtbox = (0, 0)
    im.paste(dtimg, dtbox)

    image = Image.open(CHAR_ICON_PATH / f'{name}.png').convert('RGBA')
    image = image.resize((230, 230))
    width = image.size[0]  # 获取图片宽度
    height = image.size[1]  # 获取图片高度
    for x in range(width):
        for y in range(height):
            R, G, B, A = image.getpixel((x, y))  # 获取单个像素点的RGB

            """转化为灰度：整数方法"""
            if A == 0:
                Gray = 255
            else:
                Gray = 0
                A = 255
            # if x == 0 and y == 0:
            # print(str(rgba))
            # print("R:"+str(R))
            # print("G:"+str(G))
            # print("B:"+str(B))
            # print("A:"+str(A))
            # print("Gray:"+str(Gray))
            """转化为灰度图：GRB(Gray,Gray,Gray)替换GRB(R,G,B)"""
            image.putpixel((x, y), (Gray, Gray, Gray, A))
    """保存灰度图"""
    image = image.convert('RGBA')
    dtbox = (50, 60)
    im.paste(image, dtbox, mask=image.split()[3])

    draw = ImageDraw.Draw(im)
    line = '？？？'
    font = ImageFont.truetype(FONTS_PATH, 40)
    draw.text(
        (470, 40),
        line,
        (255, 255, 0),
        font,
        'mm',
    )

    line = '我是谁'
    font = ImageFont.truetype(FONTS_PATH, 42)
    draw.text(
        (470, 100),
        line,
        (255, 255, 0),
        font,
        'mm',
    )
    img = await convert_img(im)
    # output = BytesIO()
    # im.save(output, format="PNG")
    # base64_str = 'base64://' + base64.b64encode(output.getvalue()).decode()
    mesg_a = []
    mes = f'猜猜我是谁，({ONE_TURN_TIME}s后公布答案)'
    mesg_a.append(MessageSegment.text(mes))
    #await bot.send(mes)
    # print(img_send)
    #await bot.send(img)
    mesg_a.append(MessageSegment.image(img))
    buttons_d = [
        Button('✅再来一局', '我是谁', action=1),
        Button('📖查看图鉴', f'精灵图鉴{name}', action=1),
    ]
    buttons_a = [
        Button('猜一下', '/'),
    ]
    await bot.send_option(mesg_a, buttons_a)
    try:
        async with timeout(ONE_TURN_TIME):
            while True:
                resp = await bot.receive_mutiply_resp()
                if resp is not None:
                    s = resp.text.strip()
                    gid = resp.group_id
                    uid = resp.user_id
                    cid = roster.get_id(s)
                    # await bot.send(f'你说的是 {resp.text} 吧？')
                    if (
                        cid != 9999
                        and cid
                        == winner_judger.get_correct_chara_id(ev.group_id)
                        and winner_judger.get_winner(ev.group_id) == ''
                    ):
                        GAME = GAME_DB()
                        win_num = await GAME.update_game_num(uid, 'whois')
                        mesg_d = []
                        mesg = ''
                        if daily_whois_limiter.check(uid):
                            SCORE = SCORE_DB()
                            await SCORE.update_score(uid, 1000)
                            daily_whois_limiter.increase(uid)
                            mesg = '获得1000金币\n'
                        winner_judger.record_winner(ev.group_id, ev.user_id)
                        win_mes = winner_judger.get_correct_win_pic(gid)
                        winner_judger.turn_off(ev.group_id)
                        POKE = PokeCounter()
                        mapinfo = await POKE._get_map_now(uid)
                        myname = mapinfo[2]
                        myname = str(myname)[:10]
                        mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name}'
                        chongsheng_num = await POKE.get_chongsheng_num(uid,150)
                        if chongsheng_num >= 999:
                            await POKE._add_pokemon_egg(uid, 150, 1)
                            mes += f'\n{myname}获得了超梦精灵蛋x1'
                            await POKE._new_chongsheng_num(uid,150)
                        await POKE.update_chongsheng(uid,150,1)
                        mesg_d.append(MessageSegment.text(mes))
                        mesg_d.append(MessageSegment.image(win_mes))
                        await bot.send_option(mesg_d, buttons_d)
                        return
    except asyncio.TimeoutError:
        pass
    if winner_judger.get_winner(ev.group_id) != '':
        winner_judger.turn_off(ev.group_id)
        return
    winner_judger.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name}'
    mesg_c = []
    mesg_c.append(MessageSegment.text(mes))
    mesg_c.append(MessageSegment.image(win_mes))
    await bot.send_option(mesg_c, buttons_d)


@sv_pokemon_whois.on_fullmatch('重置我是谁')
async def cz_pokemon_whois(bot: Bot, ev: Event):
    winner_judger.turn_off(ev.group_id)
    buttons = [
        Button('✅我是谁', '我是谁'),
    ]
    await bot.send_option('重置成功，请重新发送我是谁开始新一轮游戏', buttons)

@sv_pokemon_whois.on_fullmatch('重置猜精灵')
async def cz_pokemon_whoiscc(bot: Bot, ev: Event):
    winner_judger_cc.turn_off(ev.group_id)
    buttons = [
        Button('✅猜精灵', '猜精灵'),
    ]
    await bot.send_option('重置成功，请重新发送猜精灵开始新一轮游戏', buttons)

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
POKE = PokeCounter()


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

class WinnerJudgerJN:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_jineng = {}

    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)

    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def set_correct_jineng(self, gid, jinengname):
        self.correct_jineng[gid] = jinengname

    def get_correct_jineng(self, gid):
        return (
            self.correct_jineng[gid]
            if self.correct_jineng.get(gid) is not None
            else ''
        )

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_jineng[gid] = ''


winner_judger_jn = WinnerJudgerJN()

class WinnerJudgerTJ:
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


winner_judger_tj = WinnerJudgerTJ()

class Roster:
    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()

    def update(self):
        self._roster.clear()
        for idx, names in CHARA_NAME.items():
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

huanshoulist = ['梦幻','时拉比','基拉祈','玛纳霏','代欧奇希斯','达克莱伊','谢米','比克提尼','凯路迪欧','美洛耶塔','盖诺赛克特','蒂安希','波尔凯尼恩','玛机雅娜','玛夏多','捷拉奥拉','美录坦','萨戮德','熊徒弟','桃歹郎']

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
    if cc_type == '种族':
        pokeinfo = POKEMON_LIST[pokeid]
        zz_num = 0
        for shuzhi in range(1,7):
            zz_num = zz_num + int(pokeinfo[shuzhi])
        mes = f'精灵种族值为{zz_num}'
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

async def get_jineng_ts(name, cc_type):
    pokeid = roster.get_id(name)
    jinenginfo = JINENG_LIST[name]
    if cc_type == '属性':
        mes = f'技能的属性为 {jinenginfo[0]}'
    if cc_type == '类型':
        mes = f'技能的类型为 {jinenginfo[1]}'
    if cc_type == '威力':
        mes = f'技能的威力为 {jinenginfo[2]}'
    if cc_type == '命中':
        mes = f'技能的命中率为 {jinenginfo[3]}'
    if cc_type == 'PP':
        mes = f'技能的初始PP值为 {jinenginfo[4]}'
    if cc_type == '名字':
        name_len = len(name)
        mes = f'技能名字{name_len}个字'
    return mes

@sv_pokemon_whois.on_fullmatch('猜图鉴')
async def pokemon_whois_tj(bot: Bot, ev: Event):
    if winner_judger_tj.get_on_off_status(ev.group_id):
        await bot.send('此轮游戏还没结束，请勿重复使用指令')
        return
    winner_judger_tj.turn_on(ev.group_id)
    chara_id_list = list(CHARA_NAME.keys())
    poke_list = CHARA_NAME
    random.shuffle(chara_id_list)
    winner_judger_tj.set_correct_chara_id(ev.group_id, chara_id_list[0])

    poke_data = poke_list[chara_id_list[0]]
    if len(poke_data) < 2:
        print(f"数据不完整，ID={chara_id_list[0]}, data={poke_data}")
        name = poke_data[0] if len(poke_data) >= 1 else "未知"
        enname = "unknown"
    else:
        name = poke_data[0]
        enname = poke_data[1]

    win_mes = await get_win_pic(name, enname)
    winner_judger_tj.set_correct_win_pic(ev.group_id, win_mes)
    print(name)
    mes = '下面这条描述是图鉴里描述哪个宝可梦的'
    mes += f'\n{POKEMON_CONTENT[chara_id_list[0]][0]}'
    buttons_a = [
        Button('猜一下', ' ', '猜一下', action=2),
    ]
    buttons_d = [
        Button('✅再来一局', '猜图鉴', action=1),
        Button('📖查看信息', f'精灵图鉴{name}', action=1),
    ]
    await bot.send_option(mes, buttons_a)

    winner_uid = None
    try:
        async with timeout(35):
            while True:
                resp = await bot.receive_mutiply_resp()
                if resp is not None:
                    s = resp.text.strip()
                    gid = resp.group_id
                    uid = resp.user_id
                    cid = roster.get_id(s)
                    if (
                        cid != 9999
                        and cid == winner_judger_tj.get_correct_chara_id(ev.group_id)
                        and winner_judger_tj.get_winner(ev.group_id) == ''
                    ):
                        winner_uid = uid
                        winner_judger_tj.record_winner(ev.group_id, uid)
                        winner_judger_tj.turn_off(ev.group_id)
                        break
    except asyncio.TimeoutError:
        pass

    if winner_uid is not None:
        GAME = GAME_DB()
        win_num = await GAME.update_game_num(winner_uid, 'whotj')
        mesg = ''
        if daily_whois_limiter.check(winner_uid):
            SCORE = SCORE_DB()
            await SCORE.update_score(winner_uid, 1000)
            daily_whois_limiter.increase(winner_uid)
            mesg = '获得1000金币\n'
        mapinfo = await POKE._get_map_now(winner_uid)
        myname = mapinfo[2]
        myname = str(myname)[:10]
        mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name}'
        chongsheng_num = await POKE.update_chongsheng(winner_uid, 9997, 1)
        mes += f'\n{chongsheng_num}/233'
        if chongsheng_num >= 233:
            huanshouname = random.sample(huanshoulist, 1)[0]
            huanshouid = roster.get_id(huanshouname)
            await POKE._add_pokemon_egg(winner_uid, huanshouid, 1)
            mes += f'\n{myname}获得了{huanshouname}精灵蛋x1'
            await POKE._new_chongsheng_num(winner_uid, 9997)
        mesg_d = [MessageSegment.text(mes), MessageSegment.image(win_mes)]
        await bot.send_option(mesg_d, buttons_d)
        return

    if winner_judger_tj.get_winner(ev.group_id) != '':
        winner_judger_tj.turn_off(ev.group_id)
        return
    winner_judger_tj.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name}'
    mesg_c = [MessageSegment.text(mes), MessageSegment.image(win_mes)]
    await bot.send_option(mesg_c, buttons_d)


@sv_pokemon_whois.on_fullmatch('猜技能')
async def pokemon_whois_jn(bot: Bot, ev: Event):
    if winner_judger_jn.get_on_off_status(ev.group_id):
        await bot.send('此轮游戏还没结束，请勿重复使用指令')
        return
    winner_judger_jn.turn_on(ev.group_id)
    jineng_name_list = list(JINENG_LIST.keys())
    find_flag = 0
    while find_flag == 0:
        name = random.sample(jineng_name_list, 1)[0]
        if JINENG_LIST[name][1] != '变化':
            find_flag = 1
    winner_judger_jn.set_correct_jineng(ev.group_id, name)
    print(name)
    cc_list = ['属性', '类型', '威力', '命中', 'PP', '名字']
    mes = '下面每隔15秒会提示技能的信息，总共6条，猜测这是哪个技能'
    await bot.send(mes)
    buttons_a = [
        Button('猜一下', ' ', '猜一下', action=2),
    ]
    buttons_d = [
        Button('✅再来一局', '猜技能', action=1),
        Button('📖查看信息', f'精灵技能信息{name}', action=1),
    ]

    winner_uid = None
    game_over = False
    for index in range(1, 7):
        if game_over:
            break
        cc_type = random.sample(cc_list, 1)[0]
        ts_mes = await get_jineng_ts(name, cc_type)
        mes = f'提示{index}：{ts_mes}'
        await bot.send_option(mes, buttons_a)
        try:
            async with timeout(15):
                while True:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        jncc = resp.text
                        if jncc == name and winner_judger_jn.get_winner(ev.group_id) == '':
                            winner_uid = resp.user_id
                            winner_judger_jn.record_winner(ev.group_id, winner_uid)
                            winner_judger_jn.turn_off(ev.group_id)
                            game_over = True
                            break
        except asyncio.TimeoutError:
            pass
        cc_list.remove(cc_type)

    if winner_uid is not None:
        GAME = GAME_DB()
        win_num = await GAME.update_game_num(winner_uid, 'whojn')
        mesg = ''
        if daily_whois_limiter.check(winner_uid):
            SCORE = SCORE_DB()
            await SCORE.update_score(winner_uid, 1000)
            daily_whois_limiter.increase(winner_uid)
            mesg = '获得1000金币\n'
        mapinfo = await POKE._get_map_now(winner_uid)
        myname = mapinfo[2]
        myname = str(myname)[:10]
        mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name}'
        chongsheng_num = await POKE.update_chongsheng(winner_uid, 9998, 1)
        mes += f'\n{chongsheng_num}/198'
        if chongsheng_num >= 198:
            huanshouname = random.sample(huanshoulist, 1)[0]
            huanshouid = roster.get_id(huanshouname)
            await POKE._add_pokemon_egg(winner_uid, huanshouid, 1)
            mes += f'\n{myname}获得了{huanshouname}精灵蛋x1'
            await POKE._new_chongsheng_num(winner_uid, 9998)
        await bot.send_option(mes, buttons_d)
        return

    if winner_judger_jn.get_winner(ev.group_id) != '':
        winner_judger_jn.turn_off(ev.group_id)
        return
    winner_judger_jn.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name}'
    await bot.send_option(mes, buttons_d)


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
    cc_list = ['一般', '飞行', '火', '超能力', '水', '虫', '电', '岩石', '草', '幽灵', '冰', '龙', '格斗', '恶', '毒', '钢', '地面', '妖精']
    mes = '下面每隔15秒会提示克制倍率，最多5条，猜测这是哪种属性组合'
    await bot.send(mes)
    buttons_a = [
        Button('猜一下', ' ', '猜一下', action=2),
    ]
    buttons_d = [
        Button('✅再来一局', '猜属性', action=1),
    ]

    winner_uid = None
    game_over = False
    index_num = 1
    while index_num < 6 and len(cc_list) > 0 and not game_over:
        cc_list, ts_mes = await get_pokemon_tssx(sxlist, cc_list)
        mes = f'提示{index_num}：{ts_mes}'
        await bot.send_option(mes, buttons_a)
        try:
            async with timeout(15):
                while True:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        sxcc = resp.text
                        sxcc_flag = 0
                        for sxname in sxlist:
                            if str(sxname) in str(sxcc) or str(sxname) == str(sxcc):
                                sxcc_flag += 1
                        if sxcc_flag == 2 and winner_judger_sx.get_winner(ev.group_id) == '':
                            winner_uid = resp.user_id
                            winner_judger_sx.record_winner(ev.group_id, winner_uid)
                            winner_judger_sx.turn_off(ev.group_id)
                            game_over = True
                            break
        except asyncio.TimeoutError:
            pass
        index_num += 1

    if winner_uid is not None:
        GAME = GAME_DB()
        win_num = await GAME.update_game_num(winner_uid, 'whosx')
        mesg = ''
        if daily_whois_limiter.check(winner_uid):
            SCORE = SCORE_DB()
            await SCORE.update_score(winner_uid, 1000)
            daily_whois_limiter.increase(winner_uid)
            mesg = '获得1000金币\n'
        mapinfo = await POKE._get_map_now(winner_uid)
        myname = mapinfo[2]
        myname = str(myname)[:10]
        mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name_shux}'
        chongsheng_num = await POKE.update_chongsheng(winner_uid, 9999, 1)
        mes += f'\n{chongsheng_num}/198'
        if chongsheng_num >= 198:
            huanshouname = random.sample(huanshoulist, 1)[0]
            huanshouid = roster.get_id(huanshouname)
            await POKE._add_pokemon_egg(winner_uid, huanshouid, 1)
            mes += f'\n{myname}获得了{huanshouname}精灵蛋x1'
            await POKE._new_chongsheng_num(winner_uid, 9999)
        await bot.send_option(mes, buttons_d)
        return

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
    chara_id_list = list(CHARA_NAME.keys())
    poke_list = CHARA_NAME
    random.shuffle(chara_id_list)
    winner_judger_cc.set_correct_chara_id(ev.group_id, chara_id_list[0])

    poke_data = poke_list[chara_id_list[0]]
    if len(poke_data) < 2:
        print(f"数据不完整，ID={chara_id_list[0]}, data={poke_data}")
        name = poke_data[0] if len(poke_data) >= 1 else "未知"
        enname = "unknown"
    else:
        name = poke_data[0]
        enname = poke_data[1]

    win_mes = await get_win_pic(name, enname)
    winner_judger_cc.set_correct_win_pic(ev.group_id, win_mes)
    print(name)
    cc_list = ['属性', '种族高', '种族', '名字', '等级技能', '特性']
    mes = '下面每隔15秒会提示精灵的信息，总共6条，猜测这是哪只精灵'
    await bot.send(mes)
    buttons_a = [
        Button('猜一下', ' ', '猜一下', action=2),
    ]
    buttons_d = [
        Button('✅再来一局', '猜精灵', action=1),
        Button('📖查看图鉴', f'精灵图鉴{name}', action=1),
    ]

    winner_uid = None
    game_over = False
    for index in range(1, 7):
        if game_over:
            break
        cc_type = random.sample(cc_list, 1)[0]
        ts_mes = await get_pokemon_ts(name, cc_type)
        mes = f'提示{index}：{ts_mes}'
        await bot.send_option(mes, buttons_a)
        try:
            async with timeout(15):
                while True:
                    resp = await bot.receive_mutiply_resp()
                    if resp is not None:
                        s = resp.text.strip()
                        cid = roster.get_id(s)
                        if (
                            cid != 9999
                            and cid == winner_judger_cc.get_correct_chara_id(ev.group_id)
                            and winner_judger_cc.get_winner(ev.group_id) == ''
                        ):
                            winner_uid = resp.user_id
                            winner_judger_cc.record_winner(ev.group_id, winner_uid)
                            winner_judger_cc.turn_off(ev.group_id)
                            game_over = True
                            break
        except asyncio.TimeoutError:
            pass
        cc_list.remove(cc_type)

    if winner_uid is not None:
        GAME = GAME_DB()
        win_num = await GAME.update_game_num(winner_uid, 'whocc')
        mesg = ''
        if daily_whois_limiter.check(winner_uid):
            SCORE = SCORE_DB()
            await SCORE.update_score(winner_uid, 1000)
            daily_whois_limiter.increase(winner_uid)
            mesg = '获得1000金币\n'
        mapinfo = await POKE._get_map_now(winner_uid)
        myname = mapinfo[2]
        myname = str(myname)[:10]
        mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name}'
        chongsheng_num = await POKE.update_chongsheng(winner_uid, 151, 1)
        mes += f'\n{chongsheng_num}/198'
        if chongsheng_num >= 198:
            huanshouname = random.sample(huanshoulist, 1)[0]
            huanshouid = roster.get_id(huanshouname)
            await POKE._add_pokemon_egg(winner_uid, huanshouid, 1)
            mes += f'\n{myname}获得了{huanshouname}精灵蛋x1'
            await POKE._new_chongsheng_num(winner_uid, 151)
        mesg_d = [MessageSegment.text(mes), MessageSegment.image(win_mes)]
        await bot.send_option(mesg_d, buttons_d)
        return

    if winner_judger_cc.get_winner(ev.group_id) != '':
        winner_judger_cc.turn_off(ev.group_id)
        return
    winner_judger_cc.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name}'
    mesg_c = [MessageSegment.text(mes), MessageSegment.image(win_mes)]
    await bot.send_option(mesg_c, buttons_d)


@sv_pokemon_whois.on_fullmatch('我是谁')
async def pokemon_whois(bot: Bot, ev: Event):
    if winner_judger.get_on_off_status(ev.group_id):
        await bot.send('此轮游戏还没结束，请勿重复使用指令')
        return
    winner_judger.turn_on(ev.group_id)
    chara_id_list = list(CHARA_NAME.keys())
    poke_list = CHARA_NAME
    random.shuffle(chara_id_list)
    winner_judger.set_correct_chara_id(ev.group_id, chara_id_list[0])

    poke_data = poke_list[chara_id_list[0]]
    if len(poke_data) < 2:
        print(f"数据不完整，ID={chara_id_list[0]}, data={poke_data}")
        name = poke_data[0] if len(poke_data) >= 1 else "未知"
        enname = "unknown"
    else:
        name = poke_data[0]
        enname = poke_data[1]

    win_mes = await get_win_pic(name, enname)
    winner_judger.set_correct_win_pic(ev.group_id, win_mes)
    print(name)

    # 绘制灰度图片
    im = Image.new('RGB', (640, 464), (255, 255, 255))
    base_img = path.join(FILE_PATH, 'whois_bg.jpg')
    dtimg = Image.open(base_img)
    im.paste(dtimg, (0, 0))
    image = Image.open(CHAR_ICON_PATH / f'{name}.png').convert('RGBA')
    image = image.resize((230, 230))
    width, height = image.size
    for x in range(width):
        for y in range(height):
            R, G, B, A = image.getpixel((x, y))
            if A == 0:
                Gray = 255
            else:
                Gray = 0
                A = 255
            image.putpixel((x, y), (Gray, Gray, Gray, A))
    image = image.convert('RGBA')
    im.paste(image, (50, 60), mask=image.split()[3])
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONTS_PATH, 40)
    draw.text((470, 40), '？？？', (255, 255, 0), font, 'mm')
    font = ImageFont.truetype(FONTS_PATH, 42)
    draw.text((470, 100), '我是谁', (255, 255, 0), font, 'mm')
    img = await convert_img(im)

    mesg_a = [MessageSegment.text(f'猜猜我是谁，({ONE_TURN_TIME}s后公布答案)'), MessageSegment.image(img)]
    buttons_d = [
        Button('✅再来一局', '我是谁', action=1),
        Button('📖查看图鉴', f'精灵图鉴{name}', action=1),
    ]
    buttons_a = [
        Button('猜一下', ' ', '猜一下', action=2),
    ]
    await bot.send_option(mesg_a, buttons_a)

    winner_uid = None
    try:
        async with timeout(ONE_TURN_TIME):
            while True:
                resp = await bot.receive_mutiply_resp()
                print(resp)
                if resp is not None:
                    s = resp.text.strip()
                    cid = roster.get_id(s)
                    if (
                        cid != 9999
                        and cid == winner_judger.get_correct_chara_id(ev.group_id)
                        and winner_judger.get_winner(ev.group_id) == ''
                    ):
                        winner_uid = resp.user_id
                        winner_judger.record_winner(ev.group_id, winner_uid)
                        winner_judger.turn_off(ev.group_id)
                        break
    except asyncio.TimeoutError:
        pass

    if winner_uid is not None:
        GAME = GAME_DB()
        win_num = await GAME.update_game_num(winner_uid, 'whois')
        mesg = ''
        if daily_whois_limiter.check(winner_uid):
            SCORE = SCORE_DB()
            await SCORE.update_score(winner_uid, 1000)
            daily_whois_limiter.increase(winner_uid)
            mesg = '获得1000金币\n'
        mapinfo = await POKE._get_map_now(winner_uid)
        myname = mapinfo[2]
        myname = str(myname)[:10]
        mes = f'{myname}猜对了，真厉害！\n{mesg}TA已经猜对{win_num}次了\n正确答案是:{name}'
        chongsheng_num = await POKE.update_chongsheng(winner_uid, 150, 1)
        mes += f'\n{chongsheng_num}/1000'
        if chongsheng_num >= 1000:
            await POKE._add_pokemon_egg(winner_uid, 150, 1)
            mes += f'\n{myname}获得了超梦精灵蛋x1'
            await POKE._new_chongsheng_num(winner_uid, 150)
        mesg_d = [MessageSegment.text(mes), MessageSegment.image(win_mes)]
        await bot.send_option(mesg_d, buttons_d)
        return

    if winner_judger.get_winner(ev.group_id) != '':
        winner_judger.turn_off(ev.group_id)
        return
    winner_judger.turn_off(ev.group_id)
    mes = f'很遗憾，没有人答对~\n正确答案是:{name}'
    mesg_c = [MessageSegment.text(mes), MessageSegment.image(win_mes)]
    await bot.send_option(mesg_c, buttons_d)

@sv_pokemon_whois.on_fullmatch('重置小游戏')
async def cz_pokemon_whois(bot: Bot, ev: Event):
    print(ev)
    winner_judger.turn_off(ev.group_id)
    winner_judger_cc.turn_off(ev.group_id)
    winner_judger_sx.turn_off(ev.group_id)
    winner_judger_jn.turn_off(ev.group_id)
    winner_judger_tj.turn_off(ev.group_id)
    buttons = [
        Button('✅我是谁', '我是谁', '✅我是谁', action=1),
        Button('✅猜精灵', '猜精灵', '✅猜精灵', action=1),
        Button('✅猜属性', '猜属性', '✅猜属性', action=1),
        Button('✅猜技能', '猜技能', '✅猜技能', action=1),
        Button('✅猜图鉴', '猜图鉴', '✅猜图鉴', action=1),
    ]
    await bot.send_option('重置成功，请重新发送指令开始新一轮游戏', buttons)


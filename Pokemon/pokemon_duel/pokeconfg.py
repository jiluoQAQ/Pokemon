import asyncio
import base64
import os
import random
import sqlite3
import math
import textwrap
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw
import copy
import json
from async_timeout import timeout
from .pokemon import *
from .PokeCounter import *
from .until import *
from pathlib import Path
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.segment import MessageSegment
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH
from ..utils.convert import DailyAmountLimiter
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
FILE_PATH = os.path.dirname(__file__)
black_color = (0, 0, 0)
RESET_HOUR = 0  # 每日使用次数的重置时间，0代表凌晨0点，1代表凌晨1点，以此类推
WORK_NUM = 2
TEXT_PATH = Path(__file__).parent / 'texture2D'
def get_poke_bianhao(name):
    for bianhao in CHARA_NAME:
        if str(name) in CHARA_NAME[bianhao]:
            return bianhao
    return 0
#造成伤害天气
tq_kouxuelist = ['沙暴','冰雹']
#损失血量异常状态
kouxuelist = ['灼伤','中毒']
#可自动解除状态异常
jiechulist = ['冰冻','混乱','睡眠']
#无法出手异常
tingzhilist = ['冰冻','睡眠','休息']
#概率无法出手异常
chushoulist = ['混乱','麻痹']
#有回合限制的异常状态
hh_yichanglist = ['混乱','睡眠','休息','无敌']
#强制先手技能
xianzhi = ['守住','看穿','极巨防壁','拦堵']
#先手技能
youxian = ['电光一闪','音速拳','神速','真空波','子弹拳','冰砾','影子偷袭','水流喷射','飞水手里剑','圆瞳','电电加速']
#性格列表
list_xingge = ['实干','孤僻','勇敢','固执','调皮','大胆','坦率','悠闲','淘气','无虑','胆小','急躁','认真','天真','保守','稳重','冷静','害羞','马虎','沉着','温顺','狂妄','慎重','浮躁']
#初始精灵列表
chushi_list = [1,4,7,152,155,158,252,255,258,387,390,393,495,498,501,650,653,656,722,725,728,810,813,816]
#种族值对照表
zhongzu_list = {
    0:['HP','生命'],
    1:['ATK','攻击'],
    2:['DEF','防御'],
    3:['STK','特攻'],
    4:['SEF','特防'],
    5:['SPD','速度'],
}

daily_work_limiter = DailyAmountLimiter("work", WORK_NUM, RESET_HOUR)

#生成精灵初始技能
def add_new_pokemon_jineng(level,bianhao):
    jinenglist = get_level_jineng(level,bianhao)
    if len(jinenglist) <= 4:
        if len(jinenglist) == 0:
            jinengzu = ['挣扎']
        else:
            jinengzu = jinenglist
    else:
        jinengzu = random.sample(jinenglist,4)
    return jinengzu

#获取当前等级可以学习的技能
def get_level_jineng(level,bianhao):
    jinenglist = LEVEL_JINENG_LIST[bianhao]
    kexuelist = []
    #print(jinenglist)
    for item in jinenglist:
        #print(item[0])
        if int(level) >= int(item[0]):
            if JINENG_LIST[item[1]][6] != '':
                kexuelist.append(item[1])
    return kexuelist

#添加宝可梦，随机生成个体值
def add_pokemon(uid,bianhao):
    POKE = PokeCounter()
    pokemon_info = []
    level = 5
    pokemon_info.append(level)
    for num in range(1,7):
        gt_num = int(math.floor(random.uniform(1,32)))
        pokemon_info.append(gt_num)
    for num in range(1,7):
        pokemon_info.append(0)
    xingge = random.sample(list_xingge,1)
    pokemon_info.append(xingge[0])
    jinengzu = add_new_pokemon_jineng(level,bianhao)
    jineng = ''
    shul = 0
    for jinengname in jinengzu:
        if shul>0:
            jineng = jineng + ','
        jineng = jineng + jinengname
        shul = shul + 1
    pokemon_info.append(jineng)
    POKE._add_pokemon_info(uid,bianhao,pokemon_info)
    return pokemon_info

#重置宝可梦个体值
def new_pokemon_gt(uid,bianhao):
    POKE = PokeCounter()
    my_pokemon_info = get_pokeon_info(uid,bianhao)
    pokemon_info = []
    pokemon_info.append(my_pokemon_info[0])
    for num in range(1,7):
        gt_num = int(math.floor(random.uniform(1,32)))
        pokemon_info.append(gt_num)
    for num in range(7,15):
        pokemon_info.append(my_pokemon_info[num])
    POKE._add_pokemon_info(uid,bianhao,pokemon_info,my_pokemon_info[15])
    return pokemon_info
    
#获取宝可梦，随机个体，随机努力，测试用
def get_pokeon_info_sj(bianhao,level = 100):
    pokemon_info = []
    pokemon_info.append(level)
    gt_hp = int(math.floor(random.uniform(1,32)))
    
    for num in range(1,7):
        gt_num = int(math.floor(random.uniform(1,32)))
        pokemon_info.append(gt_num)
    
    max_nl = level * 5.1 + 1
    nuli = int(math.floor(random.uniform(0,max_nl)))
    for num in range(1,6):
        MAXNULI = nuli
        if nuli > 252:
            MAXNULI = 252
        MAXNULI = MAXNULI + 1
        nulinum = int(math.floor(random.uniform(0,MAXNULI)))
        nuli = nuli - nulinum
        pokemon_info.append(nulinum)
    if nuli > 0:
        if nuli < 252:
            pokemon_info.append(nuli)
        else:
            nulinum = int(math.floor(random.uniform(1,256)))
            pokemon_info.append(nuli)
    else:
        pokemon_info.append(0)
    xingge = random.sample(list_xingge,1)
    pokemon_info.append(xingge[0])
    jinengzu = add_new_pokemon_jineng(level,bianhao)
    jineng = ''
    shul = 0
    for jinengname in jinengzu:
        if shul>0:
            jineng = jineng + ','
        jineng = jineng + jinengname
        shul = shul + 1
    pokemon_info.append(jineng)
    return pokemon_info

#获取宝可梦信息
def get_pokeon_info(uid,bianhao):
    POKE = PokeCounter()
    pokemon_info = POKE._get_pokemon_info(uid,bianhao)
    return pokemon_info

#计算宝可梦属性
def get_pokemon_shuxing(bianhao,pokemon_info):
    zhongzu_info = POKEMON_LIST[bianhao]
    xingge_info = XINGGE_LIST[pokemon_info[13]]
    #print(xingge_info)
    name = zhongzu_info[0]
    HP = math.ceil((((int(zhongzu_info[1])*2) + int(pokemon_info[1]) + (int(pokemon_info[7])/4)) * int(pokemon_info[0]))/100 + 10 + int(pokemon_info[0]))
    W_atk = math.ceil(((((int(zhongzu_info[2])*2) + int(pokemon_info[2]) + int((int(pokemon_info[8])/4))) * int(pokemon_info[0]))/100 + 5)*float(xingge_info[0]))
    W_def = math.ceil(((((int(zhongzu_info[3])*2) + int(pokemon_info[3]) + int((int(pokemon_info[9])/4))) * int(pokemon_info[0]))/100 + 5)*float(xingge_info[1]))
    M_atk = math.ceil(((((int(zhongzu_info[4])*2) + int(pokemon_info[4]) + int((int(pokemon_info[10])/4))) * int(pokemon_info[0]))/100 + 5)*float(xingge_info[2]))
    M_def = math.ceil(((((int(zhongzu_info[5])*2) + int(pokemon_info[5]) + int((int(pokemon_info[11])/4))) * int(pokemon_info[0]))/100 + 5)*float(xingge_info[3]))
    speed = math.ceil(((((int(zhongzu_info[6])*2) + int(pokemon_info[6]) + int((int(pokemon_info[12])/4))) * int(pokemon_info[0]))/100 + 5)*float(xingge_info[4]))
    return HP,W_atk,W_def,M_atk,M_def,speed
    
#重开，清除宝可梦列表个人信息
def chongkai(uid):
    POKE = PokeCounter()
    POKE._delete_poke_info(uid)
    POKE.delete_pokemon_egg(uid)
    POKE.delete_pokemon_map(uid)
    POKE.delete_pokemon_group(uid)

#放生
def fangshen(uid,bianhao):
    POKE = PokeCounter()
    POKE._delete_poke_bianhao(uid,bianhao)
    
# 技能使用ai
def now_use_jineng(myinfo,diinfo,myjinenglist,dijinenglist,changdi):
    mysd = get_nowshuxing(myinfo[8], myinfo[13])
    disd = get_nowshuxing(diinfo[8], diinfo[13])
    # 判断技能中是否有能够击杀对方的技能/伤害最大的技能
    max_shanghai = 0
    use_jineng = ''
    myjisha = 0
    for jineng in myjinenglist:
        jinenginfo = JINENG_LIST[jineng]
        if jinenginfo[2].isdigit():
            tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
            if tianqi_xz > 0:
                shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
                if shuxing_xz > 0:
                    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])
                    yaohai_xz = 1
                    if jinenginfo[1] == '物理':
                        myatk = get_nowshuxing(myinfo[4],myinfo[9])
                        didef = get_nowshuxing(diinfo[5],diinfo[10])
                    else:
                        myatk = get_nowshuxing(myinfo[6],myinfo[11])
                        didef = get_nowshuxing(diinfo[7],diinfo[12])
                    shanghai = get_shanghai_num(jinenginfo[2],myinfo[2],myatk,didef,yaohai_xz,shuxing_xz,benxi_xz,tianqi_xz)
                    if shanghai >= diinfo[17]:
                        if mysd > disd:
                            max_shanghai = shanghai
                            use_jineng = jineng
                            myjisha = 1
                            return jineng
                    if shanghai > max_shanghai:
                        max_shanghai = shanghai
                        use_jineng = jineng
    
    dijisha = 0
    for jinengdi in dijinenglist:
        jinenginfo = JINENG_LIST[jinengdi]
        if jinenginfo[2].isdigit():
            tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
            if tianqi_xz > 0:
                shuxing_xz = get_shanghai_beilv(jinenginfo[0], myinfo[1])
                if shuxing_xz > 0:
                    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])
                    yaohai_xz = 1
                    if jinenginfo[1] == '物理':
                        myatk = get_nowshuxing(diinfo[4],diinfo[9])
                        didef = get_nowshuxing(myinfo[5],myinfo[10])
                    else:
                        myatk = get_nowshuxing(diinfo[6],diinfo[11])
                        didef = get_nowshuxing(myinfo[7],myinfo[12])
                    shanghai = get_shanghai_num(jinenginfo[2],diinfo[2],myatk,didef,yaohai_xz,shuxing_xz,benxi_xz,tianqi_xz)
                    if shanghai >= myinfo[17]:
                        dijisha = 1
    
    
    # 敌方速度快于我方，并且有能造成击杀的伤害时，使用先制伤害技能
    if disd > mysd and dijisha == 1:
        max_shanghai = 0
        use_jineng = ''
        for jineng in myjinenglist:
            if jineng in youxian:
                jinenginfo = JINENG_LIST[jineng]
                if jinenginfo[2].isdigit():
                    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
                    if tianqi_xz > 0:
                        shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
                        if shuxing_xz > 0:
                            benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])
                            yaohai_xz = 1
                            if jinenginfo[1] == '物理':
                                myatk = get_nowshuxing(myinfo[4],myinfo[9])
                                didef = get_nowshuxing(diinfo[5],diinfo[10])
                            else:
                                myatk = get_nowshuxing(myinfo[6],myinfo[11])
                                didef = get_nowshuxing(diinfo[7],diinfo[12])
                            shanghai = get_shanghai_num(jinenginfo[2],myinfo[2],myatk,didef,yaohai_xz,shuxing_xz,benxi_xz,tianqi_xz)
                            if shanghai > max_shanghai:
                                max_shanghai = shanghai
                                use_jineng = jineng
        if max_shanghai > 0:
            return use_jineng
        else:
            return random.sample(myjinenglist,1)[0]
    
    # 未造成击杀，判断自身血量状态与是否有回复效果技能，并且速度快于地方或者地方没有对我方造成击杀的技能
    if myinfo[17] < myinfo[17]/2:
        if dijisha == 1 and mysd > disd:
            for jineng in myjinenglist:
                jinenginfo = JINENG_LIST[jineng]
                if jinenginfo[2] == '变化' and '回复' in jinenginfo[5]:
                    return jineng
                if jinenginfo[2].isdigit() and '回复' in jinenginfo[5]:
                    return jineng
    # 双方都未造成击杀，且我方其中一个技能能对地方造成敌方当前生命一半以上时
    if max_shanghai > diinfo[17]/2:
        return use_jineng
    
    # 移除无效招式
    jinenglist = copy.deepcopy(myjinenglist)
    for jineng in jinenglist:
        jinenginfo = JINENG_LIST[jineng]
        tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
        if tianqi_xz == 0:
            jinenglist.remove(jineng)
        shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
        if shuxing_xz == 0:
            jinenglist.remove(jineng)
    # 保留变化类招式与可以造成1/5伤害以上的招式
    jineng_use_list = []
    if len(jinenglist) > 0:
        for jineng in jinenglist:
            jinenginfo = JINENG_LIST[jineng]
            if jinenginfo[2] == '变化':
                jineng_use_list.append(jineng)
            if jinenginfo[2].isdigit():
                tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
                if tianqi_xz > 0:
                    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
                    if shuxing_xz > 0:
                        benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])
                        yaohai_xz = 1
                        if jinenginfo[1] == '物理':
                            myatk = get_nowshuxing(myinfo[4],myinfo[9])
                            didef = get_nowshuxing(diinfo[5],diinfo[10])
                        else:
                            myatk = get_nowshuxing(myinfo[6],myinfo[11])
                            didef = get_nowshuxing(diinfo[7],diinfo[12])
                        shanghai = get_shanghai_num(jinenginfo[2],myinfo[2],myatk,didef,yaohai_xz,shuxing_xz,benxi_xz,tianqi_xz)
                        if shanghai > diinfo[17]/5:
                            jineng_use_list.append(jineng)
    
    if len(jineng_use_list) > 0:
        if use_jineng in jineng_use_list and max_shanghai > diinfo[17]/3:
            return use_jineng
        else:
            return random.sample(jineng_use_list,1)[0]
    else:
        return random.sample(myjinenglist,1)[0]

def get_chenghao(uid):
    POKE = PokeCounter()
    mapinfo = POKE._get_map_now(uid)
    huizhang = int(mapinfo[0])
    if huizhang == 9:
        chenghao = '天王训练家'
        huizhangnum = 8
        return chenghao,huizhangnum
    elif huizhang == 10:
        chenghao = '冠军训练家'
        huizhangnum = 8
        return chenghao,huizhangnum
    else:
        if huizhang == 0:
            chenghao = '新手训练家'
            return chenghao,huizhang
        elif huizhang < 3:
            chenghao = '普通训练家'
            return chenghao,huizhang
        elif huizhang < 6:
            chenghao = '精英训练家'
            return chenghao,huizhang
        else:
            chenghao = '资深训练家'
            return chenghao,huizhang

def get_text_line(content,num):
    content_line = []
    text_list = content.split('\n')
    for text in text_list:
        para = textwrap.wrap(text, width=num)
        for line in para:
            content_line.append(line)
    return content_line

def change_bg_img(bg_img,bg_num):
    img_bg = Image.new('RGB', (700, 1280*bg_num), (255, 255, 255))
    bg_img_bg = Image.open(TEXT_PATH / 'duel_bg.jpg')
    img_bg.paste(bg_img_bg, (0, 1280 * (bg_num - 1)))
    img_bg.paste(bg_img, (0, 0))
    return img_bg

def get_pokemon_eggid(pokemonid):
    zhongzu = POKEMON_LIST[pokemonid]
    if len(zhongzu) < 9:
        return pokemonid
    find_flag = 0
    kidid = 0
    while find_flag == 0:
        zhongzu = POKEMON_LIST[pokemonid]
        if zhongzu[8] == '-':
            kidid = pokemonid
            find_flag = 1
        else:
            pokemonid = int(zhongzu[8])
    return kidid

def pokemon_fight(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi,mypokemon_info,dipokemon_info,jineng1 = None,jineng2 = None):
    shul = 1
    mesg = ''
    fight_flag = 0
    while fight_flag == 0:
        jieshu = 0
        myjinenglist = re.split(',',mypokemon_info[14])
        dijinenglist = re.split(',',dipokemon_info[14])
        jineng1 = now_use_jineng(myinfo,diinfo,myjinenglist,dijinenglist,changdi)
        jinenginfo1 = JINENG_LIST[jineng1]
        
        jineng2 = now_use_jineng(diinfo,myinfo,dijinenglist,myjinenglist,changdi)
        jinenginfo2 = JINENG_LIST[jineng2]
        
        mesg = mesg + f"回合：{shul}\n"
        shul = shul + 1
        mysd = get_nowshuxing(myinfo[8], myinfo[13])
        if myzhuangtai[0][0] == '麻痹' and int(myzhuangtai[0][1])>0:
            mysd = int(mysd*0.5)
        disd = get_nowshuxing(diinfo[8], diinfo[13])
        if dizhuangtai[0][0] == '麻痹' and int(dizhuangtai[0][1])>0:
            disd = int(mysd*0.5)
        
        #先手判断
        myxianshou = 1
        if jineng1 in xianzhi or jineng2 in xianzhi:
            if jineng1 in xianzhi and jineng2 in xianzhi:
                if mysd < disd:
                    myxianshou = 0
            else:
                if jineng1 in xianzhi:
                    myxianshou = 1
                if jineng2 in xianzhi:
                    myxianshou = 0
        elif jineng1 in youxian or jineng2 in youxian:
            if jineng1 in youxian and jineng2 in youxian:
                if mysd < disd:
                    myxianshou = 0
            else:
                if jineng1 in youxian:
                    myxianshou = 1
                if jineng2 in youxian:
                    myxianshou = 0
        else:
            if mysd < disd:
                myxianshou = 0
        
        #判断我方能否发动攻击
        mychushou = 1
        if myzhuangtai[0][0] in tingzhilist and int(myzhuangtai[0][1]) > 0:
            mychushou = 0
        if myzhuangtai[0][0] in chushoulist and int(myzhuangtai[0][1]) > 0:
            if myzhuangtai[0][0] == '麻痹':
                shuzhi = 25
            if myzhuangtai[0][0] == '混乱':
                shuzhi = 33
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= shuzhi:
                mychushou = 0
        
        #判断敌方能否发动攻击
        dichushou = 1
        if dizhuangtai[0][0] in tingzhilist and int(dizhuangtai[0][1]) > 0:
            dichushou = 0
        if dizhuangtai[0][0] in chushoulist and int(dizhuangtai[0][1]) > 0:
            if dizhuangtai[0][0] == '麻痹':
                shuzhi = 25
            if dizhuangtai[0][0] == '混乱':
                shuzhi = 33
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= shuzhi:
                dichushou = 0
        
        #双方出手
        if myxianshou == 1:
            if jieshu == 0:
                if mychushou == 1:
                    #我方攻击
                    canshu1 = {'jineng':jineng1,'myinfo':myinfo,'diinfo':diinfo,'myzhuangtai':myzhuangtai,'dizhuangtai':dizhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo1[6]}', globals(), canshu1)
                    mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = canshu1['ret']
                    mesg = mesg + mes + '\n'
                else:
                    if myzhuangtai[0][0] == '混乱' and int(myzhuangtai[0][1]) > 0:
                        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_hunluan_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
                        mesg = mesg + mes + '\n'
                        
                    else:
                        mesg = mesg + f"{myinfo[0]}{myzhuangtai[0][0]}中，技能发动失败\n"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
            
            if jieshu == 0:
                if dichushou == 1:
                    #敌方攻击
                    canshu2 = {'jineng':jineng2,'myinfo':diinfo,'diinfo':myinfo,'myzhuangtai':dizhuangtai,'dizhuangtai':myzhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo2[6]}', globals(), canshu2)
                    mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = canshu2['ret']
                    mesg = mesg + mes + '\n'
                else:
                    if dizhuangtai[0][0] == '混乱' and int(dizhuangtai[0][1]) > 0:
                        mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_hunluan_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
                        mesg = mesg + mes + '\n'
                    else:
                        mesg = mesg + f"{diinfo[0]}{dizhuangtai[0][0]}中，技能发动失败\n"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
        
        else:
            if jieshu == 0:
                if dichushou == 1:
                    #敌方攻击
                    canshu2 = {'jineng':jineng2,'myinfo':diinfo,'diinfo':myinfo,'myzhuangtai':dizhuangtai,'dizhuangtai':myzhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo2[6]}', globals(), canshu2)
                    mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = canshu2['ret']
                    mesg = mesg + mes + '\n'
                else:
                    if dizhuangtai[0][0] == '混乱' and int(dizhuangtai[0][1]) > 0:
                        mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_hunluan_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
                        mesg = mesg + mes + '\n'
                    else:
                        mesg = mesg + f"{diinfo[0]}{dizhuangtai[0][0]}中，技能发动失败\n"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
            
            if jieshu == 0:
                if mychushou == 1:
                    #我方攻击
                    canshu1 = {'jineng':jineng1,'myinfo':myinfo,'diinfo':diinfo,'myzhuangtai':myzhuangtai,'dizhuangtai':dizhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo1[6]}', globals(), canshu1)
                    mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = canshu1['ret']
                    mesg = mesg + mes + '\n'
                else:
                    if myzhuangtai[0][0] == '混乱' and int(myzhuangtai[0][1]) > 0:
                        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_hunluan_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
                        mesg = mesg + mes + '\n'
                    else:
                        mesg = mesg + f"{myinfo[0]}{myzhuangtai[0][0]}中，技能发动失败\n"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
        
        #回合结束天气与状态伤害计算
        if myzhuangtai[0][0] in kouxuelist and int(myzhuangtai[0][1]) > 0 and myinfo[17] > 0:
            mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_zhuangtai_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
            mesg = mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
        
        if dizhuangtai[0][0] in kouxuelist and int(dizhuangtai[0][1]) > 0 and diinfo[17] > 0:
            mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_zhuangtai_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
            mesg = mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
        
        if changdi[0][0] in tq_kouxuelist and int(changdi[0][1]) > 0 and jieshu == 0:
            mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_tianqi_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
            mesg = mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
        
        if myzhuangtai[0][0] in hh_yichanglist and int(myzhuangtai[0][1]) > 0 and myinfo[17] > 0:
            myshengyuyc = int(myzhuangtai[0][1]) - 1
            if myshengyuyc == 0:
                mesg = mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0
            else:
                myzhuangtai[0][1] = myshengyuyc
                
        if dizhuangtai[0][0] in hh_yichanglist and int(dizhuangtai[0][1]) > 0 and diinfo[17] > 0:
            dishengyuyc = int(dizhuangtai[0][1]) - 1
            if dishengyuyc == 0:
                mesg = mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0
            else:
                dizhuangtai[0][1] = dishengyuyc
        
        if myzhuangtai[1][0] in hh_yichanglist and int(myzhuangtai[1][1]) > 0 and myinfo[17] > 0:
            myshengyuyc = int(myzhuangtai[1][1]) - 1
            if myshengyuyc == 0:
                mesg = mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[1][0] = '无'
                myzhuangtai[1][1] = 0
            else:
                myzhuangtai[1][1] = myshengyuyc
                
        if dizhuangtai[1][0] in hh_yichanglist and int(dizhuangtai[1][1]) > 0 and diinfo[17] > 0:
            dishengyuyc = int(dizhuangtai[1][1]) - 1
            if dishengyuyc == 0:
                mesg = mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[1][0] = '无'
                dizhuangtai[1][1] = 0
            else:
                dizhuangtai[1][1] = dishengyuyc
        
        if myzhuangtai[0][0] in jiechulist and int(myzhuangtai[0][1]) > 0 and myinfo[17] > 0:
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= 20:
                mesg = mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0

        if dizhuangtai[0][0] in jiechulist and int(dizhuangtai[0][1]) > 0 and diinfo[17] > 0:
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= 20:
                mesg = mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0
        
        if int(changdi[0][1]) > 0 and changdi[0][0] != '无天气':
            shengyutianqi = int(changdi[0][1]) - 1
            if shengyutianqi == 0:
                mesg = mesg + f"{changdi[0][0]}停止了，天气影响消失了\n"
                changdi[0][0] = '无天气'
                changdi[0][1] = 99
            else:
                changdi[0][1] = shengyutianqi
                mesg = mesg + f"{changdi[0][0]}持续中\n"
        if(jieshu == 1):
            fight_flag = 1
    return mesg,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi
    
async def pokemon_fight_s(bg_img,img_height,bg_num,bot,ev,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi,mypokemon_info,dipokemon_info,jineng1 = None,jineng2 = None):
    shul = 1
    fight_flag = 0
    mesg = ''
    my_pokemon_img = Image.open(CHAR_ICON_PATH / f'{myinfo[0]}.png').convert('RGBA').resize((80, 80))
    di_pokemon_img = Image.open(CHAR_ICON_PATH / f'{diinfo[0]}.png').convert('RGBA').resize((80, 80))
    img_draw = ImageDraw.Draw(bg_img)
    while fight_flag == 0:
        jieshu = 0
        myjinenglist = re.split(',',mypokemon_info[14])
        dijinenglist = re.split(',',dipokemon_info[14])
        jineng_use = 0
        # try:
            # async with timeout(60):
                # while jineng_use == 0:
                    # resp = await bot.receive_resp(f'请在60秒内选择一个技能使用!',myjinenglist,unsuported_platform=False)
                    # if resp is not None:
                        # s = resp.text
                        # uid = resp.user_id
                        # if s in myjinenglist:
                            # jineng1 = s
                            # # await bot.send(f'你选择的是{resp.text}')
                            # jineng_use = 1
        # except asyncio.TimeoutError:
            # jineng1 = now_use_jineng(myinfo,diinfo,myjinenglist,dijinenglist,changdi)
        jineng1 = now_use_jineng(myinfo,diinfo,myjinenglist,dijinenglist,changdi)
        jinenginfo1 = JINENG_LIST[jineng1]
        print(jineng1)
        jineng2 = now_use_jineng(diinfo,myinfo,dijinenglist,myjinenglist,changdi)
        jinenginfo2 = JINENG_LIST[jineng2]
        print(jineng2)
        img_height += 30
        if math.ceil((img_height + 50)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        img_draw.text(
            (350, img_height),
            f'回合{shul}',
            black_color,
            sr_font_24,
            'mm',
        )
        img_height += 50
        mesg = mesg + f"\n回合：{shul}\n"
        shul = shul + 1
        mysd = get_nowshuxing(myinfo[8], myinfo[13])
        if myzhuangtai[0][0] == '麻痹' and int(myzhuangtai[0][1])>0:
            mysd = int(mysd*0.5)
        disd = get_nowshuxing(diinfo[8], diinfo[13])
        if dizhuangtai[0][0] == '麻痹' and int(dizhuangtai[0][1])>0:
            disd = int(mysd*0.5)
        
        #先手判断
        myxianshou = 1
        if jineng1 in xianzhi or jineng2 in xianzhi:
            if jineng1 in xianzhi and jineng2 in xianzhi:
                if mysd < disd:
                    myxianshou = 0
            else:
                if jineng1 in xianzhi:
                    myxianshou = 1
                if jineng2 in xianzhi:
                    myxianshou = 0
        elif jineng1 in youxian or jineng2 in youxian:
            if jineng1 in youxian and jineng2 in youxian:
                if mysd < disd:
                    myxianshou = 0
            else:
                if jineng1 in youxian:
                    myxianshou = 1
                if jineng2 in youxian:
                    myxianshou = 0
        else:
            if mysd < disd:
                myxianshou = 0
        
        #判断我方能否发动攻击
        mychushou = 1
        if myzhuangtai[0][0] in tingzhilist and int(myzhuangtai[0][1]) > 0:
            mychushou = 0
        if myzhuangtai[0][0] in chushoulist and int(myzhuangtai[0][1]) > 0:
            if myzhuangtai[0][0] == '麻痹':
                shuzhi = 25
            if myzhuangtai[0][0] == '混乱':
                shuzhi = 33
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= shuzhi:
                mychushou = 0
        
        #判断敌方能否发动攻击
        dichushou = 1
        if dizhuangtai[0][0] in tingzhilist and int(dizhuangtai[0][1]) > 0:
            dichushou = 0
        if dizhuangtai[0][0] in chushoulist and int(dizhuangtai[0][1]) > 0:
            if dizhuangtai[0][0] == '麻痹':
                shuzhi = 25
            if dizhuangtai[0][0] == '混乱':
                shuzhi = 33
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= shuzhi:
                dichushou = 0
        if math.ceil((img_height + 240)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        #双方出手
        my_mesg = ''
        di_mesg = ''
        if myxianshou == 1:
            if jieshu == 0:
                if mychushou == 1:
                    #我方攻击
                    canshu1 = {'jineng':jineng1,'myinfo':myinfo,'diinfo':diinfo,'myzhuangtai':myzhuangtai,'dizhuangtai':dizhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo1[6]}', globals(), canshu1)
                    mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = canshu1['ret']
                    my_mesg = my_mesg + mes
                    
                else:
                    if myzhuangtai[0][0] == '混乱' and int(myzhuangtai[0][1]) > 0:
                        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_hunluan_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
                        my_mesg = my_mesg + '\n' + mes
                    else:
                        my_mesg = my_mesg + f"\n{myinfo[0]}{myzhuangtai[0][0]}中，技能发动失败"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
                mesg = mesg + my_mesg
                bg_img.paste(my_pokemon_img, (20, img_height), my_pokemon_img)
                my_para = get_text_line(my_mesg,25)
                my_mes_h = 0
                for line in my_para:
                    img_draw.text(
                        (125, img_height + my_mes_h),
                        line,
                        black_color,
                        sr_font_18,
                        'lm',
                    )
                    my_mes_h += 30
                my_add_height = max(70, my_mes_h)
                img_height = img_height + my_add_height + 10
            if jieshu == 0:
                if dichushou == 1:
                    #敌方攻击
                    canshu2 = {'jineng':jineng2,'myinfo':diinfo,'diinfo':myinfo,'myzhuangtai':dizhuangtai,'dizhuangtai':myzhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo2[6]}', globals(), canshu2)
                    mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = canshu2['ret']
                    di_mesg = di_mesg + mes
                else:
                    if dizhuangtai[0][0] == '混乱' and int(dizhuangtai[0][1]) > 0:
                        mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_hunluan_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
                        di_mesg = di_mesg + '\n' + mes
                    else:
                        di_mesg = di_mesg + f"\n{diinfo[0]}{dizhuangtai[0][0]}中，技能发动失败"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
                mesg = mesg + di_mesg
                bg_img.paste(di_pokemon_img, (600, img_height), di_pokemon_img)
                di_para = get_text_line(di_mesg,25)
                di_mes_h = 0
                for line in di_para:
                    img_draw.text(
                        (575, img_height + di_mes_h),
                        line,
                        black_color,
                        sr_font_18,
                        'rm',
                    )
                    di_mes_h += 30
                di_add_height = max(70, di_mes_h)
                img_height = img_height + di_add_height + 10
                
        else:
            if jieshu == 0:
                if dichushou == 1:
                    #敌方攻击
                    canshu2 = {'jineng':jineng2,'myinfo':diinfo,'diinfo':myinfo,'myzhuangtai':dizhuangtai,'dizhuangtai':myzhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo2[6]}', globals(), canshu2)
                    mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = canshu2['ret']
                    di_mesg = di_mesg + mes
                else:
                    if dizhuangtai[0][0] == '混乱' and int(dizhuangtai[0][1]) > 0:
                        mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_hunluan_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
                        di_mesg = di_mesg + '\n' + mes
                    else:
                        di_mesg = di_mesg + f"\n{diinfo[0]}{dizhuangtai[0][0]}中，技能发动失败"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
                mesg = mesg + di_mesg
                bg_img.paste(di_pokemon_img, (600, img_height), di_pokemon_img)
                di_para = get_text_line(di_mesg,25)
                di_mes_h = 0
                for line in di_para:
                    img_draw.text(
                        (575, img_height + di_mes_h),
                        line,
                        black_color,
                        sr_font_18,
                        'rm',
                    )
                    di_mes_h += 30
                di_add_height = max(70, di_mes_h)
                img_height = img_height + di_add_height + 10
                
            if jieshu == 0:
                if mychushou == 1:
                    #我方攻击
                    canshu1 = {'jineng':jineng1,'myinfo':myinfo,'diinfo':diinfo,'myzhuangtai':myzhuangtai,'dizhuangtai':dizhuangtai,'changdi':changdi}
                    exec(f'ret = {jinenginfo1[6]}', globals(), canshu1)
                    mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = canshu1['ret']
                    my_mesg = my_mesg + mes
                else:
                    if myzhuangtai[0][0] == '混乱' and int(myzhuangtai[0][1]) > 0:
                        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_hunluan_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
                        my_mesg = my_mesg + '\n' + mes
                    else:
                        my_mesg = my_mesg + f"\n{myinfo[0]}{myzhuangtai[0][0]}中，技能发动失败"
                if myinfo[17] == 0 or diinfo[17] == 0:
                    jieshu = 1
                mesg = mesg + my_mesg
                bg_img.paste(my_pokemon_img, (20, img_height), my_pokemon_img)
                my_para = get_text_line(my_mesg,25)
                my_mes_h = 0
                for line in my_para:
                    img_draw.text(
                        (125, img_height + my_mes_h),
                        line,
                        black_color,
                        sr_font_18,
                        'lm',
                    )
                    my_mes_h += 30
                my_add_height = max(70, my_mes_h)
                img_height = img_height + my_add_height + 10
        #回合结束天气与状态伤害计算
        changdi_mesg = ''
        if myzhuangtai[0][0] in kouxuelist and int(myzhuangtai[0][1]) > 0 and myinfo[17] > 0:
            mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_zhuangtai_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
            changdi_mesg = changdi_mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
        
        if dizhuangtai[0][0] in kouxuelist and int(dizhuangtai[0][1]) > 0 and diinfo[17] > 0:
            mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_zhuangtai_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
            changdi_mesg = changdi_mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
        
        if changdi[0][0] in tq_kouxuelist and int(changdi[0][1]) > 0 and jieshu == 0:
            mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_tianqi_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
            changdi_mesg = changdi_mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
        
        if myzhuangtai[0][0] in hh_yichanglist and int(myzhuangtai[0][1]) > 0 and myinfo[17] > 0:
            myshengyuyc = int(myzhuangtai[0][1]) - 1
            if myshengyuyc == 0:
                changdi_mesg = changdi_mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0
            else:
                myzhuangtai[0][1] = myshengyuyc
                
        if dizhuangtai[0][0] in hh_yichanglist and int(dizhuangtai[0][1]) > 0 and diinfo[17] > 0:
            dishengyuyc = int(dizhuangtai[0][1]) - 1
            if dishengyuyc == 0:
                changdi_mesg = changdi_mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0
            else:
                dizhuangtai[0][1] = dishengyuyc
        
        if myzhuangtai[1][0] in hh_yichanglist and int(myzhuangtai[1][1]) > 0 and myinfo[17] > 0:
            myshengyuyc = int(myzhuangtai[1][1]) - 1
            if myshengyuyc == 0:
                changdi_mesg = changdi_mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[1][0] = '无'
                myzhuangtai[1][1] = 0
            else:
                myzhuangtai[1][1] = myshengyuyc
                
        if dizhuangtai[1][0] in hh_yichanglist and int(dizhuangtai[1][1]) > 0 and diinfo[17] > 0:
            dishengyuyc = int(dizhuangtai[1][1]) - 1
            if dishengyuyc == 0:
                changdi_mesg = changdi_mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[1][0] = '无'
                dizhuangtai[1][1] = 0
            else:
                dizhuangtai[1][1] = dishengyuyc
        
        if myzhuangtai[0][0] in jiechulist and int(myzhuangtai[0][1]) > 0 and myinfo[17] > 0:
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= 20:
                changdi_mesg = changdi_mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0

        if dizhuangtai[0][0] in jiechulist and int(dizhuangtai[0][1]) > 0 and diinfo[17] > 0:
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= 20:
                changdi_mesg = changdi_mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0
        
        if int(changdi[0][1]) > 0 and changdi[0][0] != '无天气':
            shengyutianqi = int(changdi[0][1]) - 1
            if shengyutianqi == 0:
                changdi_mesg = changdi_mesg + f"{changdi[0][0]}停止了，天气影响消失了\n"
                changdi[0][0] = '无天气'
                changdi[0][1] = 99
            else:
                changdi[0][1] = shengyutianqi
                changdi_mesg = changdi_mesg + f"{changdi[0][0]}持续中\n"
        mesg = mesg + changdi_mesg
        if math.ceil((img_height + 120)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        changdi_para = get_text_line(changdi_mesg,30)
        changdi_mes_h = 0
        for line in changdi_para:
            img_draw.text(
                (350, img_height + changdi_mes_h),
                line,
                black_color,
                sr_font_18,
                'mm',
            )
            changdi_mes_h += 30
        img_height = img_height + changdi_mes_h
        #await bot.send(mesg, at_sender=True)
        if(jieshu == 1):
            fight_flag = 1
    return bg_img,img_height,bg_num,mesg,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi

def get_pokemon_name_list(pokemon_list):
    name_str = ''
    for index, pokemonid in enumerate(pokemon_list):
        if index > 0:
            name_str += ','
        name_str += CHARA_NAME[pokemonid][0]
    return name_str

def new_pokemon_info(pokemonid, pokemon_info):
    pokemoninfo = []
    pokemoninfo.append(POKEMON_LIST[pokemonid][0])
    pokemoninfo.append(POKEMON_LIST[pokemonid][7])
    pokemoninfo.append(pokemon_info[0])
    pokemonshux = []
    pokemonshux = get_pokemon_shuxing(pokemonid,pokemon_info)
    for shuzhi in pokemonshux:
        pokemoninfo.append(shuzhi)
    for num in range(1,9):
        pokemoninfo.append(0)
    pokemoninfo.append(pokemonshux[0])
    return pokemoninfo

def get_nl_info(uid, pokemonid, pokemon_info, zhongzhuid, nl_num):
    nl_z = pokemon_info[7] + pokemon_info[8] + pokemon_info[9] + pokemon_info[10] + pokemon_info[11] + pokemon_info[12]
    if nl_z >= 510:
        mes = ''
        return mes,pokemon_info
    nl_index = int(zhongzhuid + 7)
    change_nl = min(252, nl_num + pokemon_info[nl_index])
    if change_nl > pokemon_info[nl_index]:
        change_nl_num = change_nl - pokemon_info[nl_index]
        # print(nl_index)
        pokemon_info = list(pokemon_info)
        pokemon_info[nl_index] = change_nl
        POKE = PokeCounter()
        POKE._add_pokemon_nuli(uid, pokemonid, pokemon_info[7], pokemon_info[8], pokemon_info[9], pokemon_info[10], pokemon_info[11], pokemon_info[12])
        mes = f'获得了{zhongzu_list[zhongzhuid][1]}努力值{change_nl_num}'
        return mes,pokemon_info
    else:
        mes = ''
        return mes,pokemon_info

def get_need_exp(pokemonid, level):
    zhongzu = POKEMON_LIST[pokemonid]
    zhongzu_info = []
    for item in [1,2,3,4,5,6]:
        zhongzu_info.append(int(zhongzu[item]))
    zhongzu_num = 0
    for index, num in enumerate(zhongzu_info):
        zhongzu_num += int(num)
    exp_xz = 10 * math.ceil(level/10)/10
    need_exp = math.ceil((zhongzu_num * level/10) * exp_xz)
    return need_exp
    
#增加角色经验
def add_exp(uid,pokemonid,exp):
    POKE = PokeCounter()
    levelinfo = POKE._get_pokemon_level(uid,pokemonid)
    now_level = levelinfo[0]
    need_exp = get_need_exp(pokemonid, now_level)
    now_exp = levelinfo[1] + exp
    level_flag = 0
    if now_level>=100:
        level_flag = 1
        last_exp = now_exp * 0.1
        now_exp = 0
    while now_exp>=need_exp:
        now_level = now_level+1
        now_exp = now_exp-need_exp
        need_exp = get_need_exp(pokemonid, now_level)
        if now_level>=100:
            level_flag = 1
            last_exp = now_exp * 0.1
            now_exp = 0
            break
    msg = ''
    if now_level > levelinfo[0]:
        msg += f'等级提升到了{now_level}\n'
    if level_flag == 1:
        POKE._add_pokemon_level(uid, pokemonid, now_level, now_exp)
        # CE._add_exp_chizi(uid, last_exp)
        msg += f"超出等级上限，没有获得经验"
        return msg
    else:
        POKE._add_pokemon_level(uid, pokemonid, now_level, now_exp)
        return msg

def get_win_reward(uid, mypokemonid, myinfo, pokemon_info, pokemonid, level):
    mes = ''
    zhongzu = POKEMON_LIST[pokemonid]
    zhongzu_info = []
    for item in [1,2,3,4,5,6]:
        zhongzu_info.append(int(zhongzu[item]))
    zhongzu_num = 0
    max_zhongzu = 0
    max_zhongzuid = 0
    for index, num in enumerate(zhongzu_info):
        if int(num) >= int(max_zhongzu):
            max_zhongzu = int(num)
            max_zhongzuid = index
        zhongzu_num += int(num)
    # 获得经验值
    level_xz = level - myinfo[2]
    if myinfo[2] > level:
        level_xz = max((0 - level)/2, level_xz)
    get_exp = math.ceil((zhongzu_num * (level + level_xz)/10) * 0.5)
    mes = f'获得了经验{get_exp}\n'
    mesg = add_exp(uid,mypokemonid,get_exp)
    mes += mesg
    #获得努力值
    nl_num = 0
    if max_zhongzu >= 30:
        nl_num += 1
    if max_zhongzu >= 50:
        nl_num += 1
    if max_zhongzu >= 100:
        nl_num += 1
    mesg,pokemon_info = get_nl_info(uid, mypokemonid, pokemon_info, max_zhongzuid, nl_num)
    if mesg:
        mes += mesg
    newinfo = new_pokemon_info(mypokemonid, pokemon_info)
    newinfo[17] = myinfo[17]
    return mes,newinfo

async def fight_yw_ys_s(bg_img,bot,ev,uid,mypokelist,dipokelist,minlevel,maxlevel,ys = 0):
    myzhuangtai = [['无', 0],['无', 0]]
    dizhuangtai = [['无', 0],['无', 0]]
    changdi = [['无天气', 99],['', 0]]
    changci = 1
    myinfo = []
    diinfo = []
    mesg = ''
    max_my_num = len(mypokelist)
    max_di_num = len(dipokelist)
    img_height = 90
    bg_num = 1
    while len(mypokelist) > 0 and len(dipokelist) > 0:
        img_height += 30
        if math.ceil((img_height + 50)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        mesg += f'第{changci}场\n'
        img_draw = ImageDraw.Draw(bg_img)
        img_draw.text(
            (350, img_height + 10),
            f'第{changci}场',
            black_color,
            sr_font_28,
            'mm',
        )
        if math.ceil((img_height + 50)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        ball_new = Image.open(TEXT_PATH / 'ball_new.png').convert('RGBA').resize((20, 20))
        ball_bad = Image.open(TEXT_PATH / 'ball_bad.png').convert('RGBA').resize((20, 20))
        for item in range(0, max_my_num):
            if item < len(mypokelist):
                ball_img = ball_new
            else:
                ball_img = ball_bad
            ball_x = 125 + (20 + 5) * item
            ball_y = img_height
            bg_img.paste(ball_img, (ball_x, ball_y), ball_img)
        
        for item in range(1, max_di_num + 1):
            if item <= len(dipokelist):
                ball_img = ball_new
            else:
                ball_img = ball_bad
            ball_x = 575 - (20 + 5) * item
            ball_y = img_height
            bg_img.paste(ball_img, (ball_x, ball_y), ball_img)
        img_height += 55
        
        if math.ceil((img_height + 120)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        # mesg.append(MessageSegment.text(mes))
        changci += 1
        if len(myinfo) == 0:
            bianhao1 = mypokelist[0]
            mypokemon_info = get_pokeon_info(uid,bianhao1)
            myinfo = new_pokemon_info(bianhao1, mypokemon_info)
        if len(diinfo) == 0:
            bianhao2 = random.sample(dipokelist, 1)[0]
            dilevel = int(math.floor(random.uniform(minlevel,maxlevel)))
            dipokemon_info = get_pokeon_info_sj(bianhao2,dilevel)
            diinfo = new_pokemon_info(bianhao2, dipokemon_info)
        if myinfo[3] == myinfo[17]:
            mesg += f'我方派出了精灵\n{POKEMON_LIST[bianhao1][0]} Lv.{mypokemon_info[0]}\n'
            # mesg.append(MessageSegment.text(mes))
            # img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao1][0]}.png'
            # img = await convert_img(img)
            # mesg.append(MessageSegment.image(img))
            # await bot.send([MessageSegment.text(mes),MessageSegment.image(img)])
            # await bot.send(mes, at_sender=True)
            # await bot.send(img, at_sender=True)
        img_draw.text(
            (125, img_height),
            '我方派出了',
            black_color,
            sr_font_20,
            'lm',
        )
        img_draw.text(
            (125, img_height + 40),
            f'{POKEMON_LIST[bianhao1][0]} Lv.{mypokemon_info[0]}',
            black_color,
            sr_font_20,
            'lm',
        )
        # if diinfo[3] == diinfo[17]:
            # mesg.append(MessageSegment.text(mes))
            # img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao2][0]}.png'
            # img = await convert_img(img)
            # mesg.append(MessageSegment.image(img))
            # await bot.send([MessageSegment.text(mes),MessageSegment.image(img)])
            # await bot.send(mes, at_sender=True)
            # await bot.send(img, at_sender=True)
        if ys == 1:
            mesg += f'野生精灵出现了\n{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}\n'
            img_draw.text(
                (575, img_height),
                '野生精灵出现了',
                black_color,
                sr_font_20,
                'rm',
            )
        else:
            mesg += f'敌方派出了精灵\n{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}\n'
            img_draw.text(
                (575, img_height),
                '敌方派出了',
                black_color,
                sr_font_20,
                'rm',
            )
        img_draw.text(
            (575, img_height + 40),
            f'{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}',
            black_color,
            sr_font_20,
            'rm',
        )
        img_height += 70
        bg_img,img_height,bg_num,mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = await pokemon_fight_s(bg_img,img_height,bg_num,bot,ev,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi,mypokemon_info,dipokemon_info)
        img_draw = ImageDraw.Draw(bg_img)
        mesg += mes
        if math.ceil((img_height + 100)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        # mesg.append(MessageSegment.text(mes))
        if myinfo[17] == 0:
            myinfo = []
            myzhuangtai = [['无', 0],['无', 0]]
            mypokelist.remove(bianhao1)
            mesg += f'{POKEMON_LIST[bianhao2][0]}战胜了{POKEMON_LIST[bianhao1][0]}'
            img_draw.text(
                (575, img_height),
                f'{POKEMON_LIST[bianhao2][0]}战胜了{POKEMON_LIST[bianhao1][0]}',
                black_color,
                sr_font_18,
                'rm',
            )
            img_height = img_height
            # mesg.append(MessageSegment.text(mes))
            #await bot.send(mes, at_sender=True)
        if diinfo[17] == 0:
            diinfo = []
            dizhuangtai = [['无', 0],['无', 0]]
            dipokelist.remove(bianhao2)
            win_mesg = f'{POKEMON_LIST[bianhao1][0]}战胜了{POKEMON_LIST[bianhao2][0]}'
            # mesg.append(MessageSegment.text(mes))
            #await bot.send(mes, at_sender=True)
            # 我方获得经验/努力值奖励
            mes,myinfo = get_win_reward(uid, bianhao1, myinfo, mypokemon_info, bianhao2, dipokemon_info[0])
            win_mesg += mes
            mesg += f'\n{mes}'
            win_para = get_text_line(win_mesg,30)
            win_mes_h = 0
            for line in win_para:
                img_draw.text(
                    (125, img_height + win_mes_h),
                    line,
                    black_color,
                    sr_font_18,
                    'lm',
                )
                win_mes_h += 30
            img_height = img_height + win_mes_h
            # mesg.append(MessageSegment.text(mes))
            #await bot.send(mes, at_sender=True)
    return bg_img,bg_num,img_height,mesg,mypokelist,dipokelist

async def fight_pk(bot,ev,bg_img,myuid,diuid,mypokelist,dipokelist,myname,diname):
    myzhuangtai = [['无', 0],['无', 0]]
    dizhuangtai = [['无', 0],['无', 0]]
    changdi = [['无天气', 99],['', 0]]
    changci = 1
    myinfo = []
    diinfo = []
    mesg = ''
    max_my_num = len(mypokelist)
    max_di_num = len(dipokelist)
    img_height = 90
    bg_num = 1
    while len(mypokelist) > 0 and len(dipokelist) > 0:
        img_height += 30
        if math.ceil((img_height + 50)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        mesg += f'第{changci}场\n'
        img_draw = ImageDraw.Draw(bg_img)
        img_draw.text(
            (350, img_height + 10),
            f'第{changci}场',
            black_color,
            sr_font_28,
            'mm',
        )
        if math.ceil((img_height + 50)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        ball_new = Image.open(TEXT_PATH / 'ball_new.png').convert('RGBA').resize((20, 20))
        ball_bad = Image.open(TEXT_PATH / 'ball_bad.png').convert('RGBA').resize((20, 20))
        for item in range(0, max_my_num):
            if item < len(mypokelist):
                ball_img = ball_new
            else:
                ball_img = ball_bad
            ball_x = 125 + (20 + 5) * item
            ball_y = img_height
            bg_img.paste(ball_img, (ball_x, ball_y), ball_img)
        
        for item in range(1, max_di_num + 1):
            if item <= len(dipokelist):
                ball_img = ball_new
            else:
                ball_img = ball_bad
            ball_x = 575 - (20 + 5) * item
            ball_y = img_height
            bg_img.paste(ball_img, (ball_x, ball_y), ball_img)
        img_height += 55
        
        if math.ceil((img_height + 120)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        # mesg.append(MessageSegment.text(mes))
        changci += 1
        if len(myinfo) == 0:
            bianhao1 = mypokelist[0]
            mypokemon_info = get_pokeon_info(myuid,bianhao1)
            myinfo = new_pokemon_info(bianhao1, mypokemon_info)
        if len(diinfo) == 0:
            bianhao2 = dipokelist[0]
            dipokemon_info = get_pokeon_info(diuid,bianhao2)
            diinfo = new_pokemon_info(bianhao2, dipokemon_info)
        if myinfo[3] == myinfo[17]:
            mesg += f'{myname}派出了精灵\n{POKEMON_LIST[bianhao1][0]} Lv.{mypokemon_info[0]}\n'
            # mesg.append(MessageSegment.text(mes))
            # img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao1][0]}.png'
            # img = await convert_img(img)
            # mesg.append(MessageSegment.image(img))
            # await bot.send([MessageSegment.text(mes),MessageSegment.image(img)])
            # await bot.send(mes, at_sender=True)
            # await bot.send(img, at_sender=True)
        img_draw.text(
            (125, img_height),
            f'{myname}派出了',
            black_color,
            sr_font_20,
            'lm',
        )
        img_draw.text(
            (125, img_height + 40),
            f'{POKEMON_LIST[bianhao1][0]} Lv.{mypokemon_info[0]}',
            black_color,
            sr_font_20,
            'lm',
        )
        # if diinfo[3] == diinfo[17]:
            # mesg.append(MessageSegment.text(mes))
            # img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao2][0]}.png'
            # img = await convert_img(img)
            # mesg.append(MessageSegment.image(img))
            # await bot.send([MessageSegment.text(mes),MessageSegment.image(img)])
            # await bot.send(mes, at_sender=True)
            # await bot.send(img, at_sender=True)
        mesg += f'{diname}派出了精灵\n{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}\n'
        img_draw.text(
            (575, img_height),
            f'{diname}派出了',
            black_color,
            sr_font_20,
            'rm',
        )
        img_draw.text(
            (575, img_height + 40),
            f'{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}',
            black_color,
            sr_font_20,
            'rm',
        )
        img_height += 70
        bg_img,img_height,bg_num,mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = await pokemon_fight_s(bg_img,img_height,bg_num,bot,ev,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi,mypokemon_info,dipokemon_info)
        img_draw = ImageDraw.Draw(bg_img)
        mesg += mes
        if math.ceil((img_height + 100)/1280) > bg_num:
            bg_num += 1
            bg_img = change_bg_img(bg_img, bg_num)
            img_draw = ImageDraw.Draw(bg_img)
        # mesg.append(MessageSegment.text(mes))
        if myinfo[17] == 0:
            myinfo = []
            myzhuangtai = [['无', 0],['无', 0]]
            mypokelist.remove(bianhao1)
            lose_msg = f'{POKEMON_LIST[bianhao2][0]}战胜了{POKEMON_LIST[bianhao1][0]}'
            mes,diinfo = get_win_reward(diuid, bianhao2, diinfo, dipokemon_info, bianhao1, mypokemon_info[0])
            lose_msg += mes
            mesg += f'\n{mes}'
            lose_para = get_text_line(lose_msg,30)
            lose_mes_h = 0
            for line in lose_para:
                img_draw.text(
                    (575, img_height + lose_mes_h),
                    line,
                    black_color,
                    sr_font_18,
                    'rm',
                )
                lose_mes_h += 30
            img_height = img_height + lose_mes_h
        if diinfo[17] == 0:
            diinfo = []
            dizhuangtai = [['无', 0],['无', 0]]
            dipokelist.remove(bianhao2)
            win_mesg = f'{POKEMON_LIST[bianhao1][0]}战胜了{POKEMON_LIST[bianhao2][0]}'
            # 我方获得经验/努力值奖励
            mes,myinfo = get_win_reward(myuid, bianhao1, myinfo, mypokemon_info, bianhao2, dipokemon_info[0])
            win_mesg += mes
            mesg += f'\n{mes}'
            win_para = get_text_line(win_mesg,30)
            win_mes_h = 0
            for line in win_para:
                img_draw.text(
                    (125, img_height + win_mes_h),
                    line,
                    black_color,
                    sr_font_18,
                    'lm',
                )
                win_mes_h += 30
            img_height = img_height + win_mes_h
            # mesg.append(MessageSegment.text(mes))
            #await bot.send(mes, at_sender=True)
    return bg_img,bg_num,img_height,mesg,mypokelist,dipokelist

async def fight_yw_ys(uid,mypokelist,dipokelist,minlevel,maxlevel,ys = 0):
    myzhuangtai = [['无', 0],['无', 0]]
    dizhuangtai = [['无', 0],['无', 0]]
    changdi = [['无天气', 99],['', 0]]
    mesg = []
    changci = 1
    myinfo = []
    diinfo = []
    while len(mypokelist) > 0 and len(dipokelist) > 0:
        # mes = f'第{changci}场\n'
        # mesg.append(MessageSegment.text(mes))
        changci += 1
        if len(myinfo) == 0:
            bianhao1 = mypokelist[0]
            mypokemon_info = get_pokeon_info(uid,bianhao1)
            myinfo = new_pokemon_info(bianhao1, mypokemon_info)
        if len(diinfo) == 0:
            bianhao2 = random.sample(dipokelist, 1)[0]
            dilevel = int(math.floor(random.uniform(minlevel,maxlevel)))
            dipokemon_info = get_pokeon_info_sj(bianhao2,dilevel)
            diinfo = new_pokemon_info(bianhao2, dipokemon_info)
        if myinfo[3] == myinfo[17]:
            mes = f'我方派出了精灵\n{POKEMON_LIST[bianhao1][0]} Lv.{mypokemon_info[0]}'
            mesg.append(MessageSegment.text(mes))
            img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao1][0]}.png'
            img = await convert_img(img)
            mesg.append(MessageSegment.image(img))
        if diinfo[3] == diinfo[17]:
            if ys == 1:
                mes = f'野生精灵出现了\n{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}'
            else:
                mes = f'敌方派出了精灵\n{POKEMON_LIST[bianhao2][0]} Lv.{dipokemon_info[0]}'
            mesg.append(MessageSegment.text(mes))
            img = CHAR_ICON_PATH / f'{POKEMON_LIST[bianhao2][0]}.png'
            img = await convert_img(img)
            mesg.append(MessageSegment.image(img))
        mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = pokemon_fight(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi,mypokemon_info,dipokemon_info)
        mesg.append(MessageSegment.text(mes))
        if myinfo[17] == 0:
            myinfo = []
            myzhuangtai = [['无', 0],['无', 0]]
            mypokelist.remove(bianhao1)
            mes = f'{POKEMON_LIST[bianhao2][0]}战胜了{POKEMON_LIST[bianhao1][0]}'
            mesg.append(MessageSegment.text(mes))
        if diinfo[17] == 0:
            diinfo = []
            dizhuangtai = [['无', 0],['无', 0]]
            dipokelist.remove(bianhao2)
            mes = f'{POKEMON_LIST[bianhao1][0]}战胜了{POKEMON_LIST[bianhao2][0]}'
            mesg.append(MessageSegment.text(mes))
            # 我方获得经验/努力值奖励
            mes,myinfo = get_win_reward(uid, bianhao1, myinfo, mypokemon_info, bianhao2, dipokemon_info[0])
            mesg.append(MessageSegment.text(mes))
    return mesg,mypokelist,dipokelist
        
        
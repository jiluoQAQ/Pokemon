import asyncio
import base64
import os
import random
import sqlite3
import math
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
import copy
import json
from .pokemon import *
from .PokeCounter import *
from .until import *

FILE_PATH = os.path.dirname(__file__)

def get_poke_bianhao(name):
    for bianhao in CHARA_NAME:
        if str(name) in CHARA_NAME[bianhao]:
            return bianhao
    return 0
#造成伤害天气
tq_kouxuelist = ['沙暴','冰雹']
#损失血量异常状态
kouxuelist = ['灼烧','中毒']
#可自动解除状态异常
jiechulist = ['冰冻','混乱','睡眠']
#无法出手异常
tingzhilist = ['冰冻','睡眠','休息']
#概率无法出手异常
chushoulist = ['混乱','麻痹']
#有回合限制的异常状态
hh_yichanglist = ['混乱','睡眠','休息']
#强制先手技能
xianzhi = ['守住','看穿','极巨防壁','拦堵']
#先手技能
youxian = ['电光一闪','音速拳','神速','真空波','子弹拳','冰砾','影子偷袭','水流喷射','飞水手里剑','圆瞳','电电加速']
#性格列表
list_xingge = ['实干','孤僻','勇敢','固执','调皮','大胆','坦率','悠闲','淘气','无虑','胆小','急躁','认真','天真','保守','稳重','冷静','害羞','马虎','沉着','温顺','狂妄','慎重','浮躁']
#初始精灵列表
chushi_list = [1,4,7,152,155,158,252,255,258,387,390,393,495,498,501,650,653,656,810,813,816]
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
def add_pokemon(gid,uid,bianhao):
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
    POKE._add_pokemon_info(gid,uid,bianhao,pokemon_info)
    return pokemon_info

#获取宝可梦，随机个体，随机努力，测试用
def get_pokeon_info_sj(gid,uid,bianhao):
    pokemon_info = []
    level = 100
    pokemon_info.append(level)
    gt_hp = int(math.floor(random.uniform(1,32)))
    
    for num in range(1,7):
        gt_num = int(math.floor(random.uniform(1,32)))
        pokemon_info.append(gt_num)
    
    nuli = 510
    for num in range(1,6):
        MAXNULI = nuli
        if nuli > 255:
            MAXNULI = 255
        MAXNULI = MAXNULI + 1
        nulinum = int(math.floor(random.uniform(0,MAXNULI)))
        nuli = nuli - nulinum
        pokemon_info.append(nulinum)
    if nuli > 0:
        if nuli < 255:
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
def get_pokeon_info(gid,uid,bianhao):
    POKE = PokeCounter()
    pokemon_info = POKE._get_pokemon_info(gid,uid,bianhao)
    return pokemon_info

#计算宝可梦属性
def get_pokemon_shuxing(gid,uid,bianhao,pokemon_info):
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
def chongkai(gid,uid):
    POKE = PokeCounter()
    POKE._delete_poke_info(gid,uid)

#放生
def fangshen(gid,uid,bianhao):
    POKE = PokeCounter()
    POKE._delete_poke_bianhao(gid,uid,bianhao)
    
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
        
def pokemon_fight(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi,mypokemon_info,dipokemon_info,jineng1 = None,jineng2 = None):
    shul = 1
    jieshu = 0
    mesg = ''
    while jieshu == 0:
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
                break
            
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
                break
        
        else:
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
                break
            
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
                break
        
        #回合结束天气与状态伤害计算
        if myzhuangtai[0][0] in kouxuelist and int(myzhuangtai[0][1]) > 0:
            mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_zhuangtai_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
            mesg = mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
            break
        
        if dizhuangtai[0][0] in kouxuelist and int(dizhuangtai[0][1]) > 0:
            mes,diinfo,myinfo,dizhuangtai,myzhuangtai,changdi = get_zhuangtai_sh(diinfo,myinfo,dizhuangtai,myzhuangtai,changdi)
            mesg = mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
            break
        
        if changdi[0][0] in tq_kouxuelist and int(changdi[0][1]) > 0:
            mes,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi = get_tianqi_sh(myinfo,diinfo,myzhuangtai,dizhuangtai,changdi)
            mesg = mesg + mes + '\n'
        if myinfo[17] == 0 or diinfo[17] == 0:
            jieshu = 1
            break
        
        if myzhuangtai[0][0] in hh_yichanglist and int(myzhuangtai[0][1]) > 0:
            myshengyuyc = int(myzhuangtai[0][1]) - 1
            if myshengyuyc == 0:
                mesg = mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0
            else:
                myzhuangtai[0][1] = myshengyuyc
                
        if dizhuangtai[0][0] in hh_yichanglist and int(dizhuangtai[0][1]) > 0:
            dishengyuyc = int(dizhuangtai[0][1]) - 1
            if dishengyuyc == 0:
                mesg = mesg + f"{diinfo[0]}的{dizhuangtai[0][0]}状态解除了\n"
                dizhuangtai[0][0] = '无'
                dizhuangtai[0][1] = 0
            else:
                dizhuangtai[0][1] = dishengyuyc
        
        if myzhuangtai[0][0] in jiechulist and int(myzhuangtai[0][1]) > 0:
            suiji = int(math.floor(random.uniform(0,100)))
            if suiji <= 20:
                mesg = mesg + f"{myinfo[0]}的{myzhuangtai[0][0]}状态解除了\n"
                myzhuangtai[0][0] = '无'
                myzhuangtai[0][1] = 0

        if dizhuangtai[0][0] in jiechulist and int(dizhuangtai[0][1]) > 0:
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
    return mesg,myinfo,diinfo,myzhuangtai,dizhuangtai,changdi
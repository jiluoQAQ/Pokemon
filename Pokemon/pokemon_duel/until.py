import re
import random
import math
from .pokemon import *


def get_shuxing_xiuzheng(atkshux, myshux):
    shuxinglist = re.split(',', myshux)
    xiuzheng = 1
    if atkshux in shuxinglist:
        xiuzheng = 1.5
    return xiuzheng


def get_shanghai_beilv(atkshux, dishux):
    kezhilist = SHUXING_LIST[atkshux]
    shuxinglist = re.split(',', dishux)
    beilv = 1
    for shuxing in shuxinglist:
        beilv = beilv * float(kezhilist[shuxing])
    return beilv


def get_yaohai(yaohai):
    yaohailist = [42, 125, 500, 1000]
    if int(yaohai) > 3:
        return 1.5
    suiji = int(math.floor(random.uniform(0, 1000)))
    if yaohailist[int(yaohai)] >= suiji:
        return 1.5
    else:
        return 1


def update_shux_info(info, sxname, uplevel, uptype):
    # 9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级
    shuxlist = {
        'ATK': [9, '攻击'],
        'DEF': [10, '防御'],
        'SPATK': [11, '特攻'],
        'SPDEF': [12, '特防'],
        'SPD': [13, '速度'],
        'CT': [14, '要害'],
        'ER': [15, '闪避'],
        'ACT': [16, '命中'],
    }
    shuxlvreturn = {
        '6': '巨幅',
        '5': '巨幅',
        '4': '巨幅',
        '3': '巨幅',
        '2': '大幅',
        '1': '',
        '0': '',
    }
    for name in shuxlist.keys():
        if sxname == name:
            if uptype == 'down':
                if int(info[shuxlist[name][0]]) == -6:
                    msg = f'{info[0]}的{shuxlist[name][1]}已经无法再降低了！'
                else:
                    newnum = int(info[shuxlist[name][0]]) - int(uplevel)
                    if int(newnum) < -6:
                        info[shuxlist[name][0]] = -6
                        uplevel_num = int(info[shuxlist[name][0]]) + 6
                        msg = f'{info[0]}的{shuxlist[name][1]}{shuxlvreturn[str(uplevel_num)]}降低了！'
                    else:
                        info[shuxlist[name][0]] = newnum
                        msg = f'{info[0]}的{shuxlist[name][1]}{shuxlvreturn[uplevel]}降低了！'
            else:
                if int(info[shuxlist[name][0]]) == 6:
                    msg = f'{info[0]}的{shuxlist[name][1]}已经无法再提高了！'
                else:
                    newnum = int(info[shuxlist[name][0]]) + int(uplevel)
                    if int(newnum) > 6:
                        info[shuxlist[name][0]] = 6
                        uplevel_num = 6 - int(info[shuxlist[name][0]])
                        msg = f'{info[0]}的{shuxlist[name][1]}{shuxlvreturn[str(uplevel_num)]}提高了！'
                    else:
                        info[shuxlist[name][0]] = newnum
                        msg = f'{info[0]}的{shuxlist[name][1]}{shuxlvreturn[uplevel]}提高了！'
    return msg, info


def get_mingzhong(jineng_mz, my_mngzhong, di_shanbi, changdi):
    if jineng_mz == '-':
        return 1
    jineng_b = (255 * int(jineng_mz)) / 100
    mingzhong_lv = int(my_mngzhong) - int(di_shanbi)
    if mingzhong_lv > 0:
        xiuzheng = (3 + mingzhong_lv) / 3 * 100
    elif mingzhong_lv < 0:
        xiuzheng = 3 / (3 - mingzhong_lv) * 100
    else:
        xiuzheng = 100
    changdixuzheng = 1
    if changdi[0][0] == '起雾' and int(changdi[0][1]) > 0:
        changdixuzheng = 0.6
    mingzhong = int((jineng_b * xiuzheng * changdixuzheng) / 255)
    # print(mingzhong)
    suiji = int(math.floor(random.uniform(0, 100)))
    if suiji <= mingzhong:
        return 1
    else:
        return 0


def get_nowshuxing(shuxing, dengji):
    if dengji > 0:
        xiuzheng = (2 + int(dengji)) / 2
    elif dengji < 0:
        xiuzheng = 2 / (2 - int(dengji))
    else:
        xiuzheng = 1
    shuzhi = int(int(shuxing) * xiuzheng)
    return shuzhi


def get_shanghai_num(
    weili, level, atk, fangyu, yaohai, shuxing, benxi, tianqi_xz
):
    lvxiuzheng = (2 * int(level) + 10) / 250
    sh_zhanbi = int(atk) / int(fangyu)
    suiji = float(math.floor(random.uniform(85, 100)) / 100)
    shanghai = int(
        (lvxiuzheng * sh_zhanbi * int(weili) + 2)
        * float(yaohai)
        * float(shuxing)
        * float(benxi)
        * suiji
        * float(tianqi_xz)
    )
    return shanghai


def get_teshu_zt(zt_jl, ztname, dishux):
    mianyi = 0
    shuxinglist = re.split(',', dishux)
    if ztname == '麻痹' and '电' in shuxinglist:
        mianyi = 1
    if ztname == '中毒':
        if '钢' in shuxinglist or '毒' in shuxinglist:
            mianyi = 1
    if ztname == '灼伤' and '火' in shuxinglist:
        mianyi = 1
    if ztname == '冰冻' and '冰' in shuxinglist:
        mianyi = 1
    if mianyi == 1:
        return 0
    suiji = int(math.floor(random.uniform(0, 100)))
    if suiji <= int(zt_jl):
        return 1
    else:
        return 0


# 无加成伤害技能
def get_shanghai_pt(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 无加成命中要害伤害技能
def get_shanghai_pt_yh(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = 1.5
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 自爆
def get_shanghai_zb(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    myinfo[17] = 0
    mes = mes + f'\n{myinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def get_shanghai_pt_bh(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, index
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    jineng_sh = myinfo[int(index)]
    shanghai = get_shanghai_num(
        jineng_sh,
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 会对自身造成伤害的技能
def get_shanghai_pt_fs(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    mymaxhp = myinfo[3]
    down_my_hp = math.ceil(myinfo[3] * 0.1)
    now_my_hp = max(1, myinfo[17] - down_my_hp)
    last_my_hp = myinfo[17] - now_my_hp
    myinfo[17] = now_my_hp
    mes = (
        mes
        + f'{myinfo[0]}因为反作用力损伤了{last_my_hp}点血量\n剩余血量{myinfo[17]}'
    )
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 会对自身回复血量的技能
def get_shanghai_pt_xh(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, xh_bl
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    hx_num = math.ceil(shanghai * float(xh_bl))
    now_my_hp = min(myinfo[3], myinfo[17] + hx_num)
    last_my_hp = now_my_hp - myinfo[17]
    myinfo[17] = now_my_hp
    mes = mes + f'{myinfo[0]}吸取了{last_my_hp}点血量\n剩余血量{myinfo[17]}'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 附加异常状态伤害技能
def get_shanghai_zt(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
    ztname,
    zt_jl,
    zt_hh=99,
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp

    zt_mingzhong = 0
    if dizhuangtai[0][0] == '无' or int(dizhuangtai[0][1]) == 0:
        zt_mingzhong = get_teshu_zt(zt_jl, ztname, diinfo[1])
        if zt_mingzhong == 1:
            dizhuangtai[0][0] = ztname
            dizhuangtai[0][1] = int(zt_hh)

    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
        if zt_mingzhong == 1:
            mes = mes + f'\n{diinfo[0]}{ztname}了'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'

    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 附加异常状态伤害技能
def get_shanghai_zt_my(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
    ztname,
    zt_jl,
    zt_hh=99,
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    zt_mingzhong = 0
    if myzhuangtai[0][0] == '无' or int(myzhuangtai[0][1]) == 0:
        zt_mingzhong = get_teshu_zt(zt_jl, ztname, diinfo[1])
        if zt_mingzhong == 1:
            myzhuangtai[0][0] = ztname
            myzhuangtai[0][1] = int(zt_hh)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        if zt_mingzhong == 1:
            mes = mes + f'\n{myinfo[0]}{ztname}了'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp

    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    if zt_mingzhong == 1:
        mes = mes + f'\n{myinfo[0]}{ztname}了'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 异常状态双倍伤害技能普通
def get_sbshanghai_pt(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    weili = int(jinenginfo[2])
    if int(dizhuangtai[0][1]) > 0 and dizhuangtai[0][0] != '无':
        weili = weili * 2
    shanghai = get_shanghai_num(
        weili,
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][0] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def get_lxshanghai_pt(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, csmim, csmax
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    weili = int(jinenginfo[2])
    if int(dizhuangtai[0][1]) > 0 and dizhuangtai[0][0] != '无':
        weili = weili * 2
    shanghai = get_shanghai_num(
        weili,
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][0] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    cishu = int(math.floor(random.uniform(csmim, csmax)))
    shanghai = shanghai * cishu

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'击中{cishu}次，对{diinfo[0]}总计造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def get_bisha(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]
    if myinfo[2] < diinfo[2]:
        mes = '技能使用失败'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    mingzhong = 30 + myinfo[2] - diinfo[2]

    suiji = int(math.floor(random.uniform(0, 100)))
    if suiji > mingzhong:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    diinfo[17] = 0
    mes = f'{myinfo[0]}使用了技能{jineng}，一击必杀\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def add_wudi(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    myzhuangtai[1][0] = '无敌'
    myzhuangtai[1][1] = 1
    mes = f'{myinfo[0]}使用了技能{jineng}'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def get_hunluan_sh(myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    myatk = get_nowshuxing(myinfo[4], myinfo[9])
    mydef = get_nowshuxing(myinfo[5], myinfo[10])
    shanghai = get_shanghai_num(
        40,
        myinfo[2],
        myatk,
        mydef,
        1,
        1,
        1,
        1,
    )
    if int(shanghai) >= int(myinfo[17]):
        lasthp = 0
    else:
        lasthp = myinfo[17] - shanghai
    myinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}混乱了，攻击了自己，'
    if myinfo[17] > 0:
        mes = mes + f'\n{myinfo[0]}剩余血量{myinfo[17]}'
    else:
        mes = mes + f'\n{myinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def get_gushang(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, shanghai
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    shanghai = int(shanghai)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'

    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 获取状态持续伤害
def get_zhuangtai_sh(myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    if myzhuangtai[0][0] == '灼伤':
        shanghai = int(myinfo[3] / 16)
    if myzhuangtai[0][0] == '中毒':
        shanghai = int(myinfo[3] / 8)
    if int(shanghai) >= int(myinfo[17]):
        lasthp = 0
    else:
        lasthp = myinfo[17] - shanghai
    shanghai = min(60, shanghai)
    myinfo[17] = lasthp
    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}{myzhuangtai[0][0]}了，扣除血量{shanghai}'
    if myinfo[17] > 0:
        mes = mes + f'\n{myinfo[0]}剩余血量{myinfo[17]}'
    else:
        mes = mes + f'\n{myinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 获取天气持续伤害
def get_tianqi_sh(myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    myshuxinglist = re.split(',', myinfo[1])
    dishuxinglist = re.split(',', diinfo[1])

    mykouxue = 1
    dikouxue = 1
    if changdi[0][0] == '沙暴':
        mianyishux = ['岩石', '地面', '钢']
        for shux in myshuxinglist:
            if shux in mianyishux:
                mykouxue = 0
                break
        for shux in dishuxinglist:
            if shux in mianyishux:
                dikouxue = 0
                break

    if changdi[0][0] == '冰雹':
        mianyishux = ['冰']
        for shux in myshuxinglist:
            if shux in mianyishux:
                mykouxue = 0
                break
        for shux in dishuxinglist:
            if shux in mianyishux:
                dikouxue = 0
                break

    mes = f'{changdi[0][0]}持续中'
    if mykouxue == 1:
        shanghai = int(myinfo[3] / 16)
        if int(shanghai) >= int(myinfo[17]):
            lasthp = 0
        else:
            lasthp = myinfo[17] - shanghai
        myinfo[17] = lasthp
        # print('shanghai:' + str(shanghai))
        mes = mes + f'\n{myinfo[0]}扣除血量{shanghai}'
        if myinfo[17] > 0:
            mes = mes + f'\n{myinfo[0]}剩余血量{myinfo[17]}'
        else:
            mes = mes + f'\n{myinfo[0]}失去了战斗能力'
    if dikouxue == 1:
        shanghai = int(diinfo[3] / 16)
        if int(shanghai) >= int(diinfo[17]):
            lasthp = 0
        else:
            lasthp = diinfo[17] - shanghai
        diinfo[17] = lasthp
        # print('shanghai:' + str(shanghai))
        mes = mes + f'\n{diinfo[0]}扣除血量{shanghai}'
        if diinfo[17] > 0:
            mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
        else:
            mes = mes + f'\n{diinfo[0]}失去了战斗能力'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def up_my_hp(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, bh_bl):
    jinenginfo = JINENG_LIST[jineng]
    hx_num = math.ceil(myinfo[3] * float(bh_bl))
    now_my_hp = min(myinfo[3], myinfo[17] + hx_num)
    last_my_hp = now_my_hp - myinfo[17]
    myinfo[17] = now_my_hp
    mes = f'{myinfo[0]}使用了技能{jineng}回复{last_my_hp}点血量\n剩余血量{myinfo[17]}'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

def sleep(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi):
    myinfo[17] = myinfo[3]
    myzhuangtai[0][0] = '睡眠'
    myzhuangtai[0][1] = 2
    mes = f'{myinfo[0]}睡觉了，身体得到了回复\n剩余血量{myinfo[17]}'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

# 我方技能对敌方属性提升/降低效果
def up_shux_info_di(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
    sxinfo,
    lvinfo,
    typeinfo,
):
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    sxlist = re.split(',', sxinfo)
    lvlist = re.split(',', lvinfo)
    typelist = re.split(',', typeinfo)
    updatesx_num = len(sxlist)
    mesg = f'{myinfo[0]}使用了技能{jineng}'
    for i in range(updatesx_num):
        sxname = sxlist[i]
        uplevel = lvlist[i]
        uptype = typelist[i]
        mes, diinfo = update_shux_info(diinfo, sxname, uplevel, uptype)
        mesg = mesg + '\n' + mes
    return mesg, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 我方伤害技能对我方属性提升/降低效果
def up_shuxshanghai_my(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
    sxinfo,
    lvinfo,
    typeinfo,
    bh_jl=20,
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp

    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    suiji = int(math.floor(random.uniform(0, 100)))
    if suiji < int(bh_jl):
        sxlist = re.split(',', sxinfo)
        lvlist = re.split(',', lvinfo)
        typelist = re.split(',', typeinfo)
        updatesx_num = len(sxlist)
        for i in range(updatesx_num):
            sxname = sxlist[i]
            uplevel = lvlist[i]
            uptype = typelist[i]
            mesg, myinfo = update_shux_info(myinfo, sxname, uplevel, uptype)
            mes = mes + '\n' + mesg
    if diinfo[17] > 0:
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'

    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 我方伤害技能对敌方属性提升/降低效果
def dowm_shuxshanghai_di(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
    sxinfo,
    lvinfo,
    typeinfo,
    bh_jl=20,
):
    # 0NAME,1属性,2LV,3HP,4ATK,5DEF,6SP.ATK,7SP.DEF,8SPD,9攻击等级,10防御等级,11特攻等级,12特防等级,13速度等级,14要害等级,15闪避等级,16命中等级,17剩余血量
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    tianqi_xz = int(TIANQIXZ_LIST[changdi[0][0]][jinenginfo[0]])
    if tianqi_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，{changdi[0][0]}天气，{jinenginfo[0]}属性技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    # print(myinfo)
    # print(diinfo)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    shuxing_xz = get_shanghai_beilv(jinenginfo[0], diinfo[1])
    # print('shuxing_xz:' + str(shuxing_xz))
    if shuxing_xz == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，没有效果'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    benxi_xz = get_shuxing_xiuzheng(jinenginfo[0], myinfo[1])

    # print('benxi_xz:' + str(benxi_xz))
    yaohai_xz = get_yaohai(myinfo[14])
    # print('yaohai_xz:' + str(yaohai_xz))
    if jinenginfo[1] == '物理':
        myatk = get_nowshuxing(myinfo[4], myinfo[9])
        didef = get_nowshuxing(diinfo[5], diinfo[10])
    else:
        myatk = get_nowshuxing(myinfo[6], myinfo[11])
        didef = get_nowshuxing(diinfo[7], diinfo[12])

    shanghai = get_shanghai_num(
        jinenginfo[2],
        myinfo[2],
        myatk,
        didef,
        yaohai_xz,
        shuxing_xz,
        benxi_xz,
        tianqi_xz,
    )

    # 灼伤状态我方物理伤害减半
    if (
        myzhuangtai[0][1] > 0
        and myzhuangtai[0][1] == '灼伤'
        and jinenginfo[1] == '物理'
    ):
        shanghai = int(shanghai * 0.5)

    if int(shanghai) >= int(diinfo[17]):
        lasthp = 0
    else:
        lasthp = diinfo[17] - shanghai
    diinfo[17] = lasthp

    # print('shanghai:' + str(shanghai))
    mes = f'{myinfo[0]}使用了技能{jineng}，'
    if shuxing_xz > 1:
        mes = mes + '效果拔群，'
    elif shuxing_xz < 1:
        mes = mes + '效果不理想，'
    if yaohai_xz > 1:
        mes = mes + '命中要害，'
    mes = mes + f'对{diinfo[0]}造成了{shanghai}点伤害'
    if diinfo[17] > 0:
        suiji = int(math.floor(random.uniform(0, 100)))
        if suiji < int(bh_jl):
            sxlist = re.split(',', sxinfo)
            lvlist = re.split(',', lvinfo)
            typelist = re.split(',', typeinfo)
            updatesx_num = len(sxlist)
            for i in range(updatesx_num):
                sxname = sxlist[i]
                uplevel = lvlist[i]
                uptype = typelist[i]
                mesg, diinfo = update_shux_info(
                    diinfo, sxname, uplevel, uptype
                )
                mes = mes + '\n' + mesg
        mes = mes + f'\n{diinfo[0]}剩余血量{diinfo[17]}'
    else:
        mes = mes + f'\n{diinfo[0]}失去了战斗能力'

    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


# 我方变化类技能对我方的属性提升
def up_shux_info_my(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
    sxinfo,
    lvinfo,
    typeinfo,
):
    jinenginfo = JINENG_LIST[jineng]
    sxlist = re.split(',', sxinfo)
    lvlist = re.split(',', lvinfo)
    typelist = re.split(',', typeinfo)
    updatesx_num = len(sxlist)
    mesg = f'{myinfo[0]}使用了技能{jineng}'
    for i in range(updatesx_num):
        sxname = sxlist[i]
        uplevel = lvlist[i]
        uptype = typelist[i]
        mes, myinfo = update_shux_info(myinfo, sxname, uplevel, uptype)
        mesg = mesg + '\n' + mes
    return mesg, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

# 魂舞烈音爆
def hwlyb(
    jineng,
    myinfo,
    diinfo,
    myzhuangtai,
    dizhuangtai,
    changdi,
):
    jinenginfo = JINENG_LIST[jineng]
    sxlist = ['ATK','DEF','SPATK','SPDEF','SPD']
    lvlist = ['1','1','1','1','1']
    typelist = ['up','up','up','up','up']
    updatesx_num = len(sxlist)
    mesg = f'{myinfo[0]}使用了技能{jineng}'
    shanghai = math.ceil(myinfo[3]/3)
    if shanghai >= myinfo[17]:
        mesg += '\nHP不足，技能使用失败'
    else:
        myinfo[17] = myinfo[17] - shanghai
        mesg += f'\n{myinfo[0]}扣除血量{shanghai}，剩余血量{myinfo[17]}'
        for i in range(updatesx_num):
            sxname = sxlist[i]
            uplevel = lvlist[i]
            uptype = typelist[i]
            mes, myinfo = update_shux_info(myinfo, sxname, uplevel, uptype)
            mesg = mesg + '\n' + mes
    return mesg, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

# 我方变化类技能对地方的附加状态
def give_info_di(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, ztname, hh_num=5
):
    jinenginfo = JINENG_LIST[jineng]

    if dizhuangtai[1][0] == '无敌' and int(dizhuangtai[1][1]) > 0:
        mes = f'{diinfo[0]}处于保护状态，技能无效'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

    ismingzhong = get_mingzhong(jinenginfo[3], myinfo[16], diinfo[15], changdi)
    if ismingzhong == 0:
        mes = f'{myinfo[0]}使用了技能{jineng}，技能未命中'
        return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
    mes = f'{myinfo[0]}使用了技能{jineng}\n'
    zt_mingzhong = 0
    if dizhuangtai[0][0] == '无' or int(dizhuangtai[0][1]) == 0:
        zt_mingzhong = get_teshu_zt(100, ztname, diinfo[1])
        if zt_mingzhong == 1:
            dizhuangtai[0][0] = ztname
            dizhuangtai[0][1] = int(hh_num)
            mes = mes + f'\n{diinfo[0]}{ztname}了'
    else:
        mes = mes + f'\n{diinfo[0]}{dizhuangtai[0][0]}中'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi


def changdi_change(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, tqname
):
    jinenginfo = JINENG_LIST[jineng]
    changdi[0][0] = tqname
    changdi[0][1] = 5
    mes = f'\n{myinfo[0]}使用了技能{jineng}\n天气变成了{tqname}'
    return mes, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi

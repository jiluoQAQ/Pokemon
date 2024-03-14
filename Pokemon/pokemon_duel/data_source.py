from typing import List, Union
from .models import Jinengfunc
from .until import *

jinengfuncs = [
    Jinengfunc(("普通伤害",), get_shanghai_pt),
    Jinengfunc(("状态伤害",), get_shanghai_zt),
    Jinengfunc(("连续伤害",), get_lxshanghai_pt),
    Jinengfunc(("一击必杀",), get_bisha),
    Jinengfunc(("必中要害",), get_shanghai_pt_yh),
    Jinengfunc(("自身强化",), up_shux_info_my),
    Jinengfunc(("敌方削弱",), up_shux_info_di),
    Jinengfunc(("附加状态",), give_info_di),
    Jinengfunc(("固定伤害",), get_gushang),
    Jinengfunc(("回复伤害",), get_shanghai_pt_xh),
    Jinengfunc(("附加伤害",), dowm_shuxshanghai_di),
    Jinengfunc(("生命回复",), up_my_hp),
    Jinengfunc(("无敌",), add_wudi),
    Jinengfunc(("状态添加",), get_shanghai_zt_my),
    Jinengfunc(("反伤伤害",), get_shanghai_pt_fs),
    Jinengfunc(("变化伤害",), get_shanghai_pt_bh),
    Jinengfunc(("强化伤害",), up_shuxshanghai_my),
    Jinengfunc(("自爆",), get_shanghai_zb),
    Jinengfunc(("连续要害",), get_shanghai_pt_yh_lx),
    Jinengfunc(("异常双倍",), get_sbshanghai_pt),
    Jinengfunc(("连续加伤",), get_shanghai_sxj),
    Jinengfunc(("睡觉",), sleep),
    Jinengfunc(("魂舞烈音爆",), hwlyb),
    Jinengfunc(("天气",), changdi_change),
]

async def make_jineng_use(
    jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi
):
    jinenginfo = JINENG_LIST[jineng]
    jinengtype = jinenginfo[6]
    funcjineng_info: Jinengfunc = {}
    for funcjineng in jinengfuncs:
        if jinengtype in funcjineng.keywords:
            funcjineng_info = funcjineng
    if jinenginfo[7] == '':
        return await funcjineng_info.func(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi)
    else:
        return await funcjineng_info.func(jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, **jinenginfo[7])

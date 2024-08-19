RESET_HOUR = 0  # 每日使用次数的重置时间，0代表凌晨0点，1代表凌晨1点，以此类推
WORK_NUM = 2    #每日打工次数
random_egg_buy = 50 #每日随机蛋购买次数
TS_FIGHT = 20   #探索野外训练师对战概率
TS_PROP = 10    #探索道具发现概率
TS_POKEMON = 70 #探索野生宝可梦遭遇概率
WIN_EGG = 18    #野生宝可梦精灵蛋掉落概率
WIN_PROP = 15   #野生宝可梦学习机掉落概率
DALIANG_POKE = 30   #当前地点大量出现的宝可梦遭遇概率
QUN_POKE = 15   #野生宝可梦群居战概率
TS_CD = 2   #探索CD
TS_PIC = 0 #探索发送类型，1为发送图片，0为发送文字
boss_fight = 3  #每周Boss挑战次数
FIGHT_TIME = 20 #释放技能时间
BOSS_GOLD = 50000   #boss掉落金币基数
BOSS_TG = 10    #boss掉落神奇糖果基数
BOSS_WGJ = 5    #boss掉落金色王冠基础概率
BOSS_WGY = 10   #boss掉落银色王冠基础概率
BOSS_SCORE = 20 #boss掉落BOSS币基础概率
button_action = 1
dungeon_max_num = 3
dungeon_sd = 1 #精灵塔每天的扫荡次数
AUTO_TS_JS = 30 #自动探索奖励结算间隔(秒)

# 造成伤害天气
tq_kouxuelist = ['沙暴', '冰雹']
# 损失血量异常状态
kouxuelist = ['灼伤', '中毒']
# 可自动解除状态异常
jiechulist = ['冰冻', '混乱', '睡眠']
# 无法出手异常
tingzhilist = ['冰冻', '睡眠', '休息']
# 概率无法出手异常
chushoulist = ['混乱', '麻痹']
# 有回合限制的异常状态
hh_yichanglist = ['混乱', '睡眠', '休息', '无敌']
# 强制先手技能
xianzhi = ['守住', '看穿', '极巨防壁', '拦堵']
lianxu_shibai = ['守住', '看穿']
# 先手技能
youxian = [
    '电光一闪',
    '音速拳',
    '神速',
    '真空波',
    '子弹拳',
    '冰砾',
    '影子偷袭',
    '水流喷射',
    '飞水手里剑',
    '圆瞳',
    '电电加速',
    '喷射拳',
]
# 性格列表
list_xingge = [
    '勤奋',
    '怕寂寞',
    '固执',
    '顽皮',
    '勇敢',
    '大胆',
    '坦率',
    '淘气',
    '乐天',
    '悠闲',
    '内敛',
    '慢吞吞',
    '害羞',
    '马虎',
    '冷静',
    '温和',
    '温顺',
    '慎重',
    '浮躁',
    '自大',
    '胆小',
    '急躁',
    '爽朗',
    '天真',
    '认真',
]
# 初始精灵列表
chushi_list = [
    1,
    4,
    7,
    152,
    155,
    158,
    252,
    255,
    258,
    387,
    390,
    393,
    495,
    498,
    501,
    650,
    653,
    656,
    722,
    725,
    728,
    810,
    813,
    816,
    906,
    909,
    912,
]

# 种族值对照表
zhongzu_list = {
    0: ['HP', '生命'],
    1: ['ATK', '攻击'],
    2: ['DEF', '防御'],
    3: ['STK', '特攻'],
    4: ['SEF', '特防'],
    5: ['SPD', '速度'],
}

#闪光标志
starlist = {
    0: '',
    1: '★',
    2: '✨',
}

boss_buff = {
    0: 1.2,
    1: 1.5,
    2: 1.8,
}

boss_sj_buff = {
    0: 0.8,
    1: 0.9,
    2: 1,
    3: 1.1,
    4: 1.2,
    5: 1.3,
    6: 1.4,
    7: 1.5,
    8: 1.6,
    9: 1.7,
    10: 1.8,
    11: 1.9,
    12: 2.0,
    13: 2.1,
    14: 2.2,
    15: 2.3,
    16: 2.4,
    17: 2.5,
    18: 2.6,
    18: 2.7,
    19: 2.8,
    20: 2.9,
    21: 3.0,
    22: 3.2,
    23: 3.4,
    24: 3.6,
    25: 3.8,
    26: 4,
    27: 5,
    28: 6,
    29: 7,
    30: 8
}

duanweilist = {
    0:'新手级',
    200:'精灵球级',
    400:'超级球级',
    700:'高级球级',
    1000:'大师球级'
}

sjbossinfo = {
    "20248" :{
        "bossid": 384,
        "jinenglist":"画龙点睛,铁头,龙爪,咬碎",
        "xingge":"固执"
    },
    "20249" :{
        "bossid": 384,
        "jinenglist":"画龙点睛,铁头,龙爪,咬碎",
        "xingge":"固执"
    },
    "202410" :{
        "bossid": 383,
        "jinenglist":"断崖之剑,雷电拳,高温重压,劈瓦",
        "xingge":"固执"
    },
    "202411" :{
        "bossid": 382,
        "jinenglist":"十万伏特,原始之力,根源波动,冰冻光束",
        "xingge":"内敛"
    },
    "202412" :{
        "bossid": 716,
        "jinenglist":"月亮之力,冥想,精神强念,真气弹",
        "xingge":"内敛"
    },
    "202413" :{
        "bossid": 791,
        "jinenglist":"流星闪冲,意念头锤,地震,咬碎",
        "xingge":"固执"
    },
    "202434" :{
        "bossid": 717,
        "jinenglist":"潜灵奇袭,龙之俯冲,死亡之翼,恶之波动",
        "xingge":"认真"
    },
    "202435" :{
        "bossid": 716,
        "jinenglist":"月亮之力,冥想,精神强念,真气弹",
        "xingge":"内敛"
    },
    "202436" :{
        "bossid": 383,
        "jinenglist":"断崖之剑,雷电拳,高温重压,劈瓦",
        "xingge":"固执"
    },
    "202437" :{
        "bossid": 382,
        "jinenglist":"十万伏特,原始之力,根源波动,冰冻光束",
        "xingge":"内敛"
    },
    "202438" :{
        "bossid": 384,
        "jinenglist":"画龙点睛,铁头,龙爪,咬碎",
        "xingge":"固执"
    }
}

#世界boss随机精灵奖励列表
boss_poke_get_list = [793,794,795,796,797,798,799,803,805,806,987,988,989,992,993,994,995]

#禁用精灵列表
jinyonglist = [144,145,146,150,151,243,244,245,249,250,251,377,378,379,380,381,382,383,384,385,386,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,638,639,640,641,642,643,644,645,646,647,648,649,716,717,718,719,720,721,772,773,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801,802,803,804,805,806,807,808,809,888,889,890,891,892,893,894,895,896,897,898,905,1001,1002,1003,1004,1007,1008,1009,1010,1014,1015,1016,1017,287,288,289,646001,646002,888001,898001,898002,144002,145002,146002,386101,386102,386103,483101,484101,487101,492101,641101,642101,645101,800101,800102,800103,892101,720101,1020,1021,1022,1023,1024,1025]

#扭蛋禁用表
jinyonglist_random_egg = [144,145,146,150,151,243,244,245,249,250,251,377,378,379,380,381,382,383,384,385,386,480,481,482,483,484,485,486,487,488,490,491,492,493,494,638,639,640,641,642,643,644,645,646,647,648,649,716,717,718,719,720,721,772,773,785,786,787,788,789,790,791,792,800,801,802,807,808,809,888,889,890,891,892,893,894,895,896,897,898,905,1001,1002,1003,1004,1007,1008,1009,1010,1014,1015,1016,1017,287,288,289,646001,646002,888001,898001,898002,144002,145002,146002,386101,386102,386103,483101,484101,487101,492101,641101,642101,645101,800101,800102,800103,892101,720101,1020,1021,1022,1023,1024,1025]
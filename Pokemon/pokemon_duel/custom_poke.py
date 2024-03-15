# 自定义宝可梦设置：
# 宝可梦的名称，和其他的别称叫法写入CUSTOM_CHARA_NAME，具体参考demo
# 宝可梦的种族值，属性，进化信息写入CUSTOM_POKEMON_LIST，具体参考注释
# 宝可梦升级可以学习的技能写入CUSTOM_LEVEL_JINENG_LIST，具体参考注释
# 宝可梦通过学习机学习的技能写入CUSTOM_POKEMON_XUEXI
# 宝可梦的描述吸入CUSTOM_POKEMON_CONTENT
# 宝可梦立绘需要2张png图，图片长宽比为4：3
# 普通立绘一张，为[名称.png]放入gsuid_core\data\Pokemon\resource\icon下
# 闪光立绘一张，为[名称_s.png]放入gsuid_core\data\Pokemon\resource\staricon下

#自定义宝可梦名称,别称
#宝可梦的ID最好是5000以上，10000以内，10000以上设置的是其他形态的判断
CUSTOM_CHARA_NAME = {
    5001: ['测试名称','测试别称3'],
}

#自定义宝可梦种族值
# 0:名称，1：HP，2：物理攻击，3：物理防御，4：魔法攻击，5：魔法防御，6：速度，7：属性：8前置进化宝可梦id，9：进化条件
# 如果是等级进化，就写进化的等级，需要消耗道具就写需要的道具
CUSTOM_POKEMON_LIST = {
    5001: ['测试名称', '100', '100', '100', '100', '100', '100', '格斗', '-', '-'],
}


#自定义宝可梦等级技能表
#前面是学习需要的等级，后面是技能名称
CUSTOM_LEVEL_JINENG_LIST = {
    5001: [
        ['0', '叫声'],
        ['10', '摇尾巴'],
        ['30', '剑舞'],
        ['50', '聚气'],
        ['70', '燕返'],
        ['90', '点到为止'],
    ]
} 

#自定义宝可梦学习机技能表
CUSTOM_POKEMON_XUEXI = {
    5001:['叫声'],
}

#自定义宝可描述
CUSTOM_POKEMON_CONTENT = {
    5001:['我是描述'],
} 

import re
import math
from pathlib import Path

from PIL import Image, ImageDraw
from gsuid_core.utils.image.convert import convert_img
from .pmconfig import *
from .pokemon import *
from .pokeconfg import *
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH, CHAR_ICON_S_PATH
from ..utils.fonts.starrail_fonts import sr_font_15, sr_font_28, sr_font_32, sr_font_40

TEXT_PATH = Path(__file__).parent / 'texture2D'
sx_image = Image.open(TEXT_PATH / 'sx.png')
mask_bar = Image.open(TEXT_PATH / 'mask_bar.png')
info_top_img = Image.open(TEXT_PATH / 'bg_top.jpg')
info_bottom_img = Image.open(TEXT_PATH / 'bg_bottom.jpg')
info_title_img = Image.open(TEXT_PATH / 'title.png')
poro_bar = Image.open(TEXT_PATH / 'poro_bar.png')
exp_bar = Image.open(TEXT_PATH / 'exp_bar.png')
skill_title = Image.open(TEXT_PATH / 'skill_title.png')
up_title = Image.open(TEXT_PATH / 'up_title.png')
info_text_color = (232, 222, 179)

SHUX_LIST_XX = ['攻击', '防御', '特攻', '特防', '速度']
SHUX_LIST_DRAW = {
    '一般': [(159, 161, 159), (0, -2)],
    '格斗': [(255, 128, 0), (0, -42)],
    '飞行': [(129, 181, 239), (0, -82)],
    '毒': [(145, 65, 203), (0, -122)],
    '地面': [(145, 81, 33), (0, -162)],
    '岩石': [(175, 169, 129), (0, -202)],
    '虫': [(145, 161, 25), (0, -242)],
    '幽灵': [(112, 65, 112), (0, -282)],
    '钢': [(96, 161, 184), (0, -322)],
    '火': [(230, 40, 41), (0, -362)],
    '水': [(41, 128, 239), (0, -402)],
    '草': [(63, 161, 41), (0, -442)],
    '电': [(250, 192, 0), (0, -482)],
    '超能力': [(239, 65, 121), (0, -522)],
    '冰': [(63, 216, 255), (0, -562)],
    '龙': [(80, 96, 225), (0, -602)],
    '恶': [(80, 65, 63), (0, -642)],
    '妖精': [(239, 112, 239), (0, -682)],
}
JINENG_LEIXING = {
    '物理': (0, -722),
    '特殊': (0, -762),
    '变化': (0, -802),
}


async def draw_pokemon_info(uid, pokemon_info, bianhao):
    bg_height = 770
    jinenglist = await get_level_jineng(pokemon_info[0], bianhao)
    jineng_num = len(jinenglist)
    if jineng_num > 0:
        bg_height += math.ceil(jineng_num / 4) * 45 + 130
    jinhualist = []
    for pokemonid in POKEMON_LIST:
        if len(POKEMON_LIST[pokemonid]) > 8:
            if str(POKEMON_LIST[pokemonid][8]) == str(bianhao) and POKEMON_LIST[pokemonid][9] != '-':
                jinhualist.append(
                    [POKEMON_LIST[pokemonid][9], CHARA_NAME[pokemonid][0]]
                )
    if len(jinhualist) > 0:
        bg_height += len(jinhualist) * 150 + 50
    bg_height = max(bg_height, 1376)
    img = Image.new('RGBA', (900, bg_height + 124))
    img.paste(info_top_img, (0, 0))
    bg_center = Image.open(TEXT_PATH / 'bg_center.jpg').resize(
        (900, bg_height)
    )
    img.paste(bg_center, (0, 62))
    img.paste(info_bottom_img, (0, bg_height + 62))
    startype = await POKE.get_pokemon_star(uid, bianhao)
    starlist_draw = {
        0: '',
        1: '★',
        2: '◆',
    }
    img.paste(info_title_img, (0, 41), info_title_img)
    img_draw = ImageDraw.Draw(img)
    # 画名称标题
    img_draw.text(
        (285, 121),
        f'{starlist_draw[startype]}{POKEMON_LIST[bianhao][0]}',
        info_text_color,
        sr_font_40,
        'mm',
    )
    if startype > 0:
        img_draw.text(
            (350, 190),
            f'{starlist_draw[startype]}',
            (255, 255, 0),
            sr_font_40,
            'mm',
        )
    img_draw.text(
        (516, 132),
        '属性',
        info_text_color,
        sr_font_32,
        'mm',
    )
    img_draw.text(
        (630, 132),
        '个体',
        info_text_color,
        sr_font_32,
        'mm',
    )
    img_draw.text(
        (750, 132),
        '努力',
        info_text_color,
        sr_font_32,
        'mm',
    )
    # 画形象
    icon_src = CHAR_ICON_PATH / f'{CHARA_NAME[bianhao][0]}.png'
    if startype > 0:
        icon_src = CHAR_ICON_S_PATH / f'{CHARA_NAME[bianhao][0]}_s.png'
    pokemon_img = (
        Image.open(icon_src)
        .convert('RGBA')
        .resize((300, 300))
    )
    img.paste(pokemon_img, (70, 168), pokemon_img)

    HP, W_atk, W_def, M_atk, M_def, speed = await get_pokemon_shuxing(
        bianhao, pokemon_info
    )
    # 画属性
    img.paste(poro_bar, (454, 170), poro_bar)
    img.paste(poro_bar, (454, 225), poro_bar)
    img.paste(poro_bar, (454, 280), poro_bar)
    img.paste(poro_bar, (454, 335), poro_bar)
    img.paste(poro_bar, (454, 390), poro_bar)
    img.paste(poro_bar, (454, 445), poro_bar)
    xingge_info = XINGGE_LIST[pokemon_info[13]]
    img_draw.text((413, 193), 'HP', (53, 77, 105), sr_font_28, 'mm')
    for shul, shux in enumerate(SHUX_LIST_XX):
        sx_color = (53, 77, 105)
        if float(xingge_info[shul]) > 1:
            sx_color = (255, 0, 0)
        if float(xingge_info[shul]) < 1:
            sx_color = (0, 255, 0)
        img_draw.text((413, 55 * shul + 248), shux, sx_color, sr_font_28, 'mm')
    # 属性
    img_draw.text((516, 193), f'{HP}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 248), f'{W_atk}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 303), f'{W_def}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 358), f'{M_atk}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 413), f'{M_def}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 468), f'{speed}', (0, 0, 0), sr_font_28, 'mm')
    # 个体
    img_draw.text(
        (630, 193), f'{pokemon_info[1]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (630, 248), f'{pokemon_info[2]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (630, 303), f'{pokemon_info[3]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (630, 358), f'{pokemon_info[4]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (630, 413), f'{pokemon_info[5]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (630, 468), f'{pokemon_info[6]}', (0, 0, 0), sr_font_28, 'mm'
    )
    # 努力
    img_draw.text(
        (750, 193), f'{pokemon_info[7]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (750, 248), f'{pokemon_info[8]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (750, 303), f'{pokemon_info[9]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (750, 358), f'{pokemon_info[10]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (750, 413), f'{pokemon_info[11]}', (0, 0, 0), sr_font_28, 'mm'
    )
    img_draw.text(
        (750, 468), f'{pokemon_info[12]}', (0, 0, 0), sr_font_28, 'mm'
    )
    # 画经验条
    img_draw.text(
        (82, 525), f'Lv.{pokemon_info[0]}', (0, 0, 0), sr_font_32, 'lm'
    )
    z_exp = await get_need_exp(bianhao, pokemon_info[0])
    need_exp = z_exp - pokemon_info[15]
    img.paste(exp_bar, (190, 520), exp_bar)
    if pokemon_info[0] < 100:
        exp_with = 381 * (pokemon_info[15] / z_exp) + 1
    else:
        exp_with = 382
        need_exp = 0
    exp_tc = Image.open(TEXT_PATH / 'exp_tc.png').resize((int(exp_with), 12))
    img.paste(exp_tc, (190, 520), exp_tc)
    img_draw.text((580, 525), f'下级所需 {need_exp}', (0, 0, 0), sr_font_32, 'lm')
    img_draw.text(
        (818, 578),
        f'性格：{pokemon_info[13]}',
        (0, 0, 0),
        sr_font_28,
        'rm',
    )
    # 画属性类型
    shuxinglist = re.split(',', POKEMON_LIST[bianhao][7])
    for shul, shuxing in enumerate(shuxinglist):
        shuxing_img = Image.new('RGBA', (142, 38), SHUX_LIST_DRAW[shuxing][0])
        shuxing_img.paste(sx_image, SHUX_LIST_DRAW[shuxing][1], sx_image)
        shuxing_temp = Image.new('RGBA', (142, 38))
        shuxing_temp.paste(shuxing_img, (0, 0), mask_bar)
        shuxing_draw = ImageDraw.Draw(shuxing_temp)
        shuxing_draw.text(
            (91, 19),
            f'{shuxing}',
            (255, 255, 255),
            sr_font_28,
            'mm',
        )
        img.paste(shuxing_temp, (150 * shul + 82, 559), shuxing_temp)
    img.paste(skill_title, (77, 620), skill_title)
    img_draw.text(
        (274, 657),
        '当前技能',
        info_text_color,
        sr_font_40,
        'mm',
    )
    my_jineng = re.split(',', pokemon_info[14])
    jineng_bar_mask = mask_bar.copy()
    jineng_bar_mask = jineng_bar_mask.resize((180, 38))
    for shul, jineng in enumerate(my_jineng):
        jineng_img = Image.new(
            'RGBA', (180, 38), SHUX_LIST_DRAW[JINENG_LIST[jineng][0]][0]
        )
        jineng_img.paste(
            sx_image, JINENG_LEIXING[JINENG_LIST[jineng][1]], sx_image
        )
        jineng_temp = Image.new('RGBA', (180, 38))
        jineng_temp.paste(jineng_img, (0, 0), jineng_bar_mask)
        jineng_draw = ImageDraw.Draw(jineng_temp)
        jineng_draw.text(
            (100, 19),
            f'{jineng}',
            (255, 255, 255),
            sr_font_28,
            'mm',
        )
        img.paste(jineng_temp, (187 * shul + 82, 710), jineng_temp)
    jn_y = 0
    if len(jinenglist) > 0:
        img.paste(skill_title, (77, 770), skill_title)
        img_draw.text(
            (274, 807),
            '回忆技能',
            info_text_color,
            sr_font_40,
            'mm',
        )
        for shul, jineng in enumerate(jinenglist):
            jn_y = math.floor(shul / 4)
            jn_x = shul - (4 * jn_y)
            jineng_img = Image.new(
                'RGBA', (180, 38), SHUX_LIST_DRAW[JINENG_LIST[jineng][0]][0]
            )
            jineng_img.paste(
                sx_image, JINENG_LEIXING[JINENG_LIST[jineng][1]], sx_image
            )
            jineng_temp = Image.new('RGBA', (180, 38))
            jineng_temp.paste(jineng_img, (0, 0), jineng_bar_mask)
            jineng_draw = ImageDraw.Draw(jineng_temp)
            jineng_draw.text(
                (100, 19),
                f'{jineng}',
                (255, 255, 255),
                sr_font_28,
                'mm',
            )
            img.paste(
                jineng_temp, (187 * jn_x + 82, jn_y * 45 + 860), jineng_temp
            )
    if len(jinhualist) > 0:
        start_y = (jn_y + 1) * 45 + 880
        img.paste(up_title, (77, start_y), up_title)
        img_draw.text(
            (274, start_y + 37),
            '进化信息',
            info_text_color,
            sr_font_40,
            'mm',
        )
        for shul, jinhuainfo in enumerate(jinhualist):
            jinhua_icon = CHAR_ICON_PATH / f'{jinhuainfo[1]}.png'
            if startype > 0:
                jinhua_icon = CHAR_ICON_S_PATH / f'{jinhuainfo[1]}_s.png'
            pokemon_jinhua = (
                Image.open(jinhua_icon)
                .convert('RGBA')
                .resize((140, 140))
            )
            img.paste(
                pokemon_jinhua, (82, shul * 150 + start_y + 90), pokemon_jinhua
            )
            if jinhuainfo[0].isdigit():
                jinhua_xuqiu = f'Lv.{jinhuainfo[0]} 可进化为 {jinhuainfo[1]}'
            else:
                jinhua_xuqiu = f'使用道具 {jinhuainfo[0]} 可进化为 {jinhuainfo[1]}'
            img_draw.text(
                (280, shul * 150 + start_y + 160),
                f'{jinhua_xuqiu}',
                (0, 0, 0),
                sr_font_32,
                'lm',
            )
    img_draw.text(
        (450, bg_height + 108),
        'Created by GsCore & Pokemon & jiluoQAQ',
        (140, 140, 140),
        sr_font_15,
        'mm',
    )
    res = await convert_img(img)
    return res, jinhualist

async def draw_pokemon_info_tj(bianhao):
    bg_height = 600
    jinengxxlist = await get_level_jineng(100, bianhao)
    jinengxx_num = len(jinengxxlist)
    if jinengxx_num > 0:
        bg_height += math.ceil(jinengxx_num / 4) * 45 + 130
    jinenglist = POKEMON_XUEXI[bianhao]
    jineng_num = len(jinenglist)
    if jineng_num > 0:
        bg_height += math.ceil(jineng_num / 4) * 45 + 100
    jinhualist = []
    for pokemonid in POKEMON_LIST:
        if len(POKEMON_LIST[pokemonid]) > 8:
            if str(POKEMON_LIST[pokemonid][8]) == str(bianhao) and POKEMON_LIST[pokemonid][9] != '-':
                jinhualist.append(
                    [POKEMON_LIST[pokemonid][9], CHARA_NAME[pokemonid][0]]
                )
    if len(jinhualist) > 0:
        bg_height += len(jinhualist) * 150 + 50
    miaoshu = POKEMON_CONTENT[bianhao][0]
    miaoshu_para = get_text_line(miaoshu, 25)
    miaoshu_height = len(miaoshu_para) * 40
    bg_height += miaoshu_height
    bg_height = max(bg_height, 1376)
    img = Image.new('RGBA', (900, bg_height + 124))
    img.paste(info_top_img, (0, 0))
    bg_center = Image.open(TEXT_PATH / 'bg_center.jpg').resize(
        (900, bg_height)
    )
    img.paste(bg_center, (0, 62))
    img.paste(info_bottom_img, (0, bg_height + 62))
    img.paste(info_title_img, (0, 41), info_title_img)
    img_draw = ImageDraw.Draw(img)
    # 画名称标题
    img_draw.text(
        (285, 121),
        f'{POKEMON_LIST[bianhao][0]}',
        info_text_color,
        sr_font_40,
        'mm',
    )
    img_draw.text(
        (516, 132),
        '种族',
        info_text_color,
        sr_font_32,
        'mm',
    )
    img_draw.text(
        (630, 132),
        '最小值',
        info_text_color,
        sr_font_32,
        'mm',
    )
    img_draw.text(
        (750, 132),
        '最大值',
        info_text_color,
        sr_font_32,
        'mm',
    )
    # 画形象
    pokemon_img = (
        Image.open(CHAR_ICON_PATH / f'{CHARA_NAME[bianhao][0]}.png')
        .convert('RGBA')
        .resize((300, 300))
    )
    img.paste(pokemon_img, (70, 168), pokemon_img)

    # 画属性
    img.paste(poro_bar, (454, 170), poro_bar)
    img.paste(poro_bar, (454, 225), poro_bar)
    img.paste(poro_bar, (454, 280), poro_bar)
    img.paste(poro_bar, (454, 335), poro_bar)
    img.paste(poro_bar, (454, 390), poro_bar)
    img.paste(poro_bar, (454, 445), poro_bar)
    img_draw.text((413, 193), 'HP', (53, 77, 105), sr_font_28, 'mm')
    for shul, shux in enumerate(SHUX_LIST_XX):
        sx_color = (53, 77, 105)
        img_draw.text((413, 55 * shul + 248), shux, sx_color, sr_font_28, 'mm')
    # 种族
    zhongzu_info = POKEMON_LIST[bianhao]
    img_draw.text((516, 193), f'{zhongzu_info[1]}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 248), f'{zhongzu_info[2]}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 303), f'{zhongzu_info[3]}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 358), f'{zhongzu_info[4]}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 413), f'{zhongzu_info[5]}', (0, 0, 0), sr_font_28, 'mm')
    img_draw.text((516, 468), f'{zhongzu_info[6]}', (0, 0, 0), sr_font_28, 'mm')
    # 最小属性
    MIN_HP = math.ceil((int(zhongzu_info[1]) * 2) + 10 + 100)
    img_draw.text(
        (630, 193), f'{MIN_HP}', (0, 0, 0), sr_font_28, 'mm'
    )
    MIN_atk = math.ceil(((int(zhongzu_info[2]) * 2) + 5) * 0.9)
    img_draw.text(
        (630, 248), f'{MIN_atk}', (0, 0, 0), sr_font_28, 'mm'
    )
    MIN_def = math.ceil(((int(zhongzu_info[3]) * 2) + 5) * 0.9)
    img_draw.text(
        (630, 303), f'{MIN_def}', (0, 0, 0), sr_font_28, 'mm'
    )
    MIN_spatk = math.ceil(((int(zhongzu_info[4]) * 2) + 5) * 0.9)
    img_draw.text(
        (630, 358), f'{MIN_spatk}', (0, 0, 0), sr_font_28, 'mm'
    )
    MIN_spdef = math.ceil(((int(zhongzu_info[5]) * 2) + 5) * 0.9)
    img_draw.text(
        (630, 413), f'{MIN_spdef}', (0, 0, 0), sr_font_28, 'mm'
    )
    MIN_spd = math.ceil(((int(zhongzu_info[6]) * 2) + 5) * 0.9)
    img_draw.text(
        (630, 468), f'{MIN_spd}', (0, 0, 0), sr_font_28, 'mm'
    )
    # 最大属性
    MAX_HP = math.ceil(((int(zhongzu_info[1]) * 2) + 94) + 110)
    img_draw.text(
        (750, 193), f'{MAX_HP}', (0, 0, 0), sr_font_28, 'mm'
    )
    MAX_atk = math.ceil(((int(zhongzu_info[2]) * 2) + 99) * 1.1)
    img_draw.text(
        (750, 248), f'{MAX_atk}', (0, 0, 0), sr_font_28, 'mm'
    )
    MAX_def = math.ceil(((int(zhongzu_info[3]) * 2) + 99) * 1.1)
    img_draw.text(
        (750, 303), f'{MAX_def}', (0, 0, 0), sr_font_28, 'mm'
    )
    MAX_spatk = math.ceil(((int(zhongzu_info[4]) * 2) + 99) * 1.1)
    img_draw.text(
        (750, 358), f'{MAX_spatk}', (0, 0, 0), sr_font_28, 'mm'
    )
    MAX_spdef = math.ceil(((int(zhongzu_info[5]) * 2) + 99) * 1.1)
    img_draw.text(
        (750, 413), f'{MAX_spdef}', (0, 0, 0), sr_font_28, 'mm'
    )
    MAX_spd = math.ceil(((int(zhongzu_info[6]) * 2) + 99) * 1.1)
    img_draw.text(
        (750, 468), f'{MAX_spd}', (0, 0, 0), sr_font_28, 'mm'
    )
    # 画属性类型
    shuxinglist = re.split(',', POKEMON_LIST[bianhao][7])
    for shul, shuxing in enumerate(shuxinglist):
        shuxing_img = Image.new('RGBA', (142, 38), SHUX_LIST_DRAW[shuxing][0])
        shuxing_img.paste(sx_image, SHUX_LIST_DRAW[shuxing][1], sx_image)
        shuxing_temp = Image.new('RGBA', (142, 38))
        shuxing_temp.paste(shuxing_img, (0, 0), mask_bar)
        shuxing_draw = ImageDraw.Draw(shuxing_temp)
        shuxing_draw.text(
            (91, 19),
            f'{shuxing}',
            (255, 255, 255),
            sr_font_28,
            'mm',
        )
        img.paste(shuxing_temp, (150 * shul + 82, 520), shuxing_temp)
    
    miaoshu_h = 0
    for line in miaoshu_para:
        img_draw.text(
            (91, 600 + miaoshu_h),
            line,
            black_color,
            sr_font_28,
            'lm',
        )
        miaoshu_h += 40
    start_height = 600 + miaoshu_h + 10
    djjn_height = 0
    if len(jinengxxlist) > 0:
        img.paste(skill_title, (77, start_height), skill_title)
        img_draw.text(
            (274, start_height + 37),
            '等级技能',
            info_text_color,
            sr_font_40,
            'mm',
        )
        jineng_bar_mask = mask_bar.copy()
        jineng_bar_mask = jineng_bar_mask.resize((180, 38))
        jn_y = 0
        for shul, jineng in enumerate(jinengxxlist):
            jn_y = math.floor(shul / 4)
            jn_x = shul - (4 * jn_y)
            jineng_img = Image.new(
                'RGBA', (180, 38), SHUX_LIST_DRAW[JINENG_LIST[jineng][0]][0]
            )
            jineng_img.paste(
                sx_image, JINENG_LEIXING[JINENG_LIST[jineng][1]], sx_image
            )
            jineng_temp = Image.new('RGBA', (180, 38))
            jineng_temp.paste(jineng_img, (0, 0), jineng_bar_mask)
            jineng_draw = ImageDraw.Draw(jineng_temp)
            jineng_draw.text(
                (100, 19),
                f'{jineng}',
                (255, 255, 255),
                sr_font_28,
                'mm',
            )
            img.paste(
                jineng_temp, (187 * jn_x + 82, jn_y * 45 + start_height + 90), jineng_temp
            )
        djjn_height = djjn_height + 160 + (jn_y * 45)
    start_height = 600 + miaoshu_h + 10 + djjn_height
    img.paste(skill_title, (77, start_height), skill_title)
    img_draw.text(
        (274, start_height + 37),
        '学习机技能',
        info_text_color,
        sr_font_40,
        'mm',
    )
    jn_y = 0
    for shul, jineng in enumerate(jinenglist):
        jn_y = math.floor(shul / 4)
        jn_x = shul - (4 * jn_y)
        jineng_img = Image.new(
            'RGBA', (180, 38), SHUX_LIST_DRAW[JINENG_LIST[jineng][0]][0]
        )
        jineng_img.paste(
            sx_image, JINENG_LEIXING[JINENG_LIST[jineng][1]], sx_image
        )
        jineng_temp = Image.new('RGBA', (180, 38))
        jineng_temp.paste(jineng_img, (0, 0), jineng_bar_mask)
        jineng_draw = ImageDraw.Draw(jineng_temp)
        jineng_draw.text(
            (100, 19),
            f'{jineng}',
            (255, 255, 255),
            sr_font_28,
            'mm',
        )
        img.paste(
            jineng_temp, (187 * jn_x + 82, jn_y * 45 + start_height + 90), jineng_temp
        )
    if len(jinhualist) > 0:
        start_y = (jn_y + 1) * 45 + start_height + 110
        img.paste(up_title, (77, start_y), up_title)
        img_draw.text(
            (274, start_y + 37),
            '进化信息',
            info_text_color,
            sr_font_40,
            'mm',
        )
        for shul, jinhuainfo in enumerate(jinhualist):
            pokemon_jinhua = (
                Image.open(CHAR_ICON_PATH / f'{jinhuainfo[1]}.png')
                .convert('RGBA')
                .resize((140, 140))
            )
            img.paste(
                pokemon_jinhua, (82, shul * 150 + start_y + 90), pokemon_jinhua
            )
            if jinhuainfo[0].isdigit():
                jinhua_xuqiu = f'Lv.{jinhuainfo[0]} 可进化为 {jinhuainfo[1]}'
            else:
                jinhua_xuqiu = f'使用道具 {jinhuainfo[0]} 可进化为 {jinhuainfo[1]}'
            img_draw.text(
                (280, shul * 150 + start_y + 160),
                f'{jinhua_xuqiu}',
                (0, 0, 0),
                sr_font_32,
                'lm',
            )
    img_draw.text(
        (450, bg_height + 108),
        'Created by GsCore & Pokemon & jiluoQAQ',
        (140, 140, 140),
        sr_font_15,
        'mm',
    )
    res = await convert_img(img)
    return res, jinhualist
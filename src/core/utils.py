import datetime

COLORS = {
    (0, 0, 0, 255): '黑色(black)',
    (60, 60, 60, 255): '深灰色(dark_gray)',
    (120, 120, 120, 255): '灰色(gray)',
    (170, 170, 170, 255): '中灰色(medium_gray)',
    (210, 210, 210, 255): '浅灰色(light_gray)',
    (255, 255, 255, 255): '白色(white)',
    (96, 0, 24, 255): '深红色(deep_red)',
    (165, 14, 30, 255): '暗红色(dark_red)',
    (237, 28, 36, 255): '红色(red)',
    (250, 128, 114, 255): '浅红色(light_red)',
    (228, 92, 26, 255): '暗橙色(dark_orange)',
    (255, 127, 39, 255): '橙色(orange)',
    (246, 170, 9, 255): '金色(gold)',
    (249, 221, 59, 255): '黄色(yellow)',
    (255, 250, 188, 255): '浅黄色(light_yellow)',
    (156, 132, 49, 255): '暗金菊色(dark_goldenrod)',
    (197, 173, 49, 255): '金菊色(goldenrod)',
    (232, 212, 95, 255): '浅金菊色(light_goldenrod)',
    (74, 107, 58, 255): '暗橄榄色(dark_olive)',
    (90, 148, 74, 255): '橄榄色(olive)',
    (132, 197, 115, 255): '浅橄榄色(light_olive)',
    (14, 185, 104, 255): '暗绿色(dark_green)',
    (19, 230, 123, 255): '绿色(green)',
    (135, 255, 94, 255): '浅绿色(light_green)',
    (12, 129, 110, 255): '暗青色(dark_teal)',
    (16, 174, 166, 255): '青色(teal)',
    (19, 225, 190, 255): '浅青色(light_teal)',
    (15, 121, 159, 255): '暗青蓝色(dark_cyan)',
    (96, 247, 242, 255): '青蓝色(cyan)',
    (187, 250, 242, 255): '浅青蓝色(light_cyan)',
    (40, 80, 158, 255): '暗蓝色(dark_blue)',
    (64, 147, 228, 255): '蓝色(blue)',
    (125, 199, 255, 255): '浅蓝色(light_blue)',
    (77, 49, 184, 255): '暗靛蓝色(dark_indigo)',
    (107, 80, 246, 255): '靛蓝色(indigo)',
    (153, 177, 251, 255): '浅靛蓝色(light_indigo)',
    (74, 66, 132, 255): '暗板蓝色(dark_slate_blue)',
    (122, 113, 196, 255): '板蓝色(slate_blue)',
    (181, 174, 241, 255): '浅板蓝色(light_slate_blue)',
    (120, 12, 153, 255): '暗紫色(dark_purple)',
    (170, 56, 185, 255): '紫色(purple)',
    (224, 159, 249, 255): '浅紫色(light_purple)',
    (203, 0, 122, 255): '暗粉色(dark_pink)',
    (236, 31, 128, 255): '粉色(pink)',
    (243, 141, 169, 255): '浅粉色(light_pink)',
    (155, 82, 73, 255): '暗桃色(dark_peach)',
    (209, 128, 120, 255): '桃色(peach)',
    (250, 182, 164, 255): '浅桃色(light_peach)',
    (104, 70, 52, 255): '暗棕色(dark_brown)',
    (149, 104, 42, 255): '棕色(brown)',
    (219, 164, 99, 255): '浅棕色(light_brown)',
    (123, 99, 82, 255): '暗褐色(dark_tan)',
    (156, 132, 107, 255): '褐色(tan)',
    (214, 181, 148, 255): '浅褐色(light_tan)',
    (209, 128, 81, 255): '暗米色(dark_beige)',
    (248, 178, 119, 255): '米色(beige)',
    (255, 197, 165, 255): '浅米色(light_beige)',
    (109, 100, 63, 255): '暗石色(dark_stone)',
    (148, 140, 107, 255): '石色(stone)',
    (205, 197, 158, 255): '浅石色(light_stone)',
    (51, 57, 65, 255): '暗板岩色(dark_slate)',
    (109, 117, 141, 255): '板岩色(slate)',
    (179, 185, 209, 255): '浅板岩色(light_slate)',
}

def name_of_color(color: tuple):
    if color[3] == 0:
        return '透明'
    if color in COLORS:
        return COLORS[color]
    else:
        return '未知颜色'
    
def format_relative_time(target_time: datetime.datetime) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = now - target_time

    # 获取总秒数
    total_seconds = delta.total_seconds()

    # 1. 几秒前 (小于1分钟)
    if total_seconds < 60:
        return "刚才"

    # 2. 几分钟前 (小于1小时)
    minutes = int(total_seconds / 60)
    if minutes < 60:
        return f"{minutes} 分钟前"

    # 3. 几小时前 (小于1天)
    hours = int(total_seconds / 3600)
    if hours < 24:
        return f"{hours} 小时前"

    # 4. 几天前 (小于1周)
    days = delta.days
    if days < 7:
        return f"{days} 天前"
    
    # 5. 几周前
    if days < 30:
        weeks = int(days / 7)
        return f"{weeks} 周前"

    # 6. 很久之前 (超过一个月)
    return "很久之前"
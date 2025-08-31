from collections import namedtuple
from PIL import Image
import asyncio
import numpy as np
import datetime
from src.core.settings import settings
from src.core.logging import logger
from src.core.area import area_manager, fetch_current_image
from src.core.fs import path_manager

Diff = namedtuple("Diff", ["x", "y", "original", "current"])

def get_original_image(area: dict):
    return Image.open(path_manager.get(f"data/originals/{area['name']}.png")).convert("RGBA")


def get_mask_image(area: dict):
    return Image.open(path_manager.get(f"data/masks/{area['name']}.png")).convert("L")


class CurrentImageFetcher:
    def __init__(self):
        self._cache = {}
        self._is_last_from_cache = False

    def is_last_from_cache(self) -> bool:
        return self._is_last_from_cache

    async def fetch(self, area: dict):
        x = area["position"]["x"]
        y = area["position"]["y"]

        if (x, y) in self._cache:
            logger.info(f'从缓存中找到 `{area["name"]}` 所在区块')
            self._is_last_from_cache = True
            return self._cache[(x, y)]

        image = await fetch_current_image(area)
        self._cache[(x, y)] = image
        self._is_last_from_cache = False
        return image


def compute_differences(
        area_image: Image.Image,
        current_image: Image.Image,
        mask_image: Image.Image
) -> list[Diff]:
# 1. 将 PIL 图像转换为 NumPy 数组
    arr_area = np.array(area_image)
    arr_current = np.array(current_image)
    arr_mask = np.array(mask_image)

    # 2. 创建一个布尔掩码
    # 遮罩的非零像素
    valid_mask = arr_mask != 0

    # 比较原始图像和当前图像，找出差异点
    # '!=' 比较的是整个 RGBA 像素，返回一个 (H, W, 4) 的布尔数组
    # 'any(axis=2)' 检查每个像素的 RGBA 值是否至少有一个不同
    diff_mask = (arr_area != arr_current).any(axis=2)

    # 3. 结合两个掩码，找出既在遮罩内又有差异的像素
    # 这里的 & 是按位与操作，它将两个布尔数组的真值结合起来
    final_mask = valid_mask & diff_mask

    # 4. 使用 np.where 获取所有符合条件的像素的坐标
    # np.where 返回一个元组，包含所有真值点的行和列索引
    diff_coords_y, diff_coords_x = np.where(final_mask)

    # 5. 提取差异点的原始像素值和当前像素值
    # 使用高级索引一次性获取所有差异点的像素数据
    original_pixels = arr_area[diff_coords_y, diff_coords_x]
    current_pixels = arr_current[diff_coords_y, diff_coords_x]

    # 6. 将结果转换为 Diff 命名元组的列表
    # 使用 zip 将坐标和像素数据打包，然后用列表推导式创建 Diff 对象
    diffs = [
        Diff(x, y, tuple(original), tuple(current))
        for x, y, original, current in zip(
            diff_coords_x,
            diff_coords_y,
            original_pixels,
            current_pixels
        )
    ]

    return diffs


def draw_differences(mask_image: Image.Image, diffs: list[Diff]):
    highlight_color = (255, 0, 0, 255)

    diff_image = mask_image.convert("RGBA")
    arr = np.array(diff_image)
    mask = (arr[:, :, :3] == (255, 255, 255)).all(axis=2)
    arr[mask] = (255, 255, 255) + (210,)
    mask = (arr[:, :, :3] == (0, 0, 0)).all(axis=2)
    arr[mask] = (0, 0, 0) + (210,)

    coords = np.array([(d.x, d.y) for d in diffs])
    if coords.size > 0:
        arr[coords[:, 1], coords[:, 0]] = highlight_color
    return Image.fromarray(arr)

async def monitor_all(areas: list[dict]):
    results = {}
    fetcher = CurrentImageFetcher()
    for i, area in enumerate(areas):
        if area['ignored']:
            logger.warning(f'已跳过对 {area["name"]} 的检查')
            continue

        failed = False
        try:
            results[area["name"]] = await _monitor_one(fetcher, area)
        except Exception as e:
            logger.warning(f'检查 {area["name"]} 失败')
            failed = True
        if i < len(areas) - 1:
            wait_ms = settings.wait_for_next_area_ms
            if failed or not fetcher.is_last_from_cache():
                logger.info(f'等待 {wait_ms}ms 后进行下次网络请求...')
                await asyncio.sleep(wait_ms / 1000)

    area_manager.save()
    return results

async def _monitor_one(fetcher: CurrentImageFetcher, area: dict) -> dict:
    current_image = await fetcher.fetch(area)
    
    original_image = get_original_image(area)
    mask_image = get_mask_image(area)

    logger.info(f'正在检查异常...')
    diffs = compute_differences(original_image, current_image, mask_image)
    logger.info(f'正在生成结果展示图...')
    diff_image = draw_differences(mask_image, diffs)
    result = {
        "diffs": diffs,
        "diff_image": diff_image,
        "current_image": current_image,
        "original_image": original_image,
        "mask_image": mask_image
    }
    area['last_check_date'] = datetime.datetime.now(datetime.timezone.utc)
    return result
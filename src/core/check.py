from collections import namedtuple
from PIL import Image
import asyncio
import numpy as np
import datetime
from src.core.settings import Settings
from src.core.logging import logger
from src.core.area import AreaManager, fetch_current_image
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
            logger().info(f'从缓存中找到 `{area["name"]}` 所在区块')
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
    logger().info(f'正在检查异常...')
    diffs = []
    width, height = area_image.size

    for x in range(width):
        for y in range(height):
            if mask_image.getpixel((x, y)) == 0:  # Assuming mask is binary (0 or 255)
                continue
            if area_image.getpixel((x, y)) != current_image.getpixel((x, y)):
                diffs.append(Diff(x, y, area_image.getpixel((x, y)), current_image.getpixel((x, y))))
    return diffs


def draw_differences(mask_image: Image.Image, diffs: list[Diff]):
    logger().info(f'正在绘制结果展示图...')
    highlight_color = (255, 0, 0, 255)

    diff_image = mask_image.convert("RGBA")
    arr = np.array(diff_image)
    mask = (arr[:, :, :3] == (255, 255, 255)).all(axis=2)
    arr[mask] = (255, 255, 255) + (210,)
    mask = (arr[:, :, :3] == (0, 0, 0)).all(axis=2)
    arr[mask] = (0, 0, 0) + (210,)
    diff_image = Image.fromarray(arr)

    for diff in diffs:
        diff_image.putpixel((diff.x, diff.y), highlight_color)
    return diff_image

async def monitor_all(areas: list[dict]):
    results = {}
    fetcher = CurrentImageFetcher()
    for i, area in enumerate(areas):
        if area['ignored']:
            logger().warning(f'已跳过对 {area["name"]} 的检查')
            continue

        failed = False
        try:
            results[area["name"]] = await _monitor_one(fetcher, area)
        except Exception as e:
            logger().warning(f'检查 {area["name"]} 失败')
            failed = True
        if i < len(areas) - 1:
            wait_ms = Settings().wait_for_next_area_ms
            if failed or not fetcher.is_last_from_cache():
                logger().info(f'等待 {wait_ms}ms 后进行下次网络请求...')
                await asyncio.sleep(wait_ms / 1000)

    AreaManager().save()
    return results

async def _monitor_one(fetcher: CurrentImageFetcher, area: dict) -> dict:
    current_image = await fetcher.fetch(area)
    
    original_image = get_original_image(area)
    mask_image = get_mask_image(area)
    diffs = compute_differences(original_image, current_image, mask_image)
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
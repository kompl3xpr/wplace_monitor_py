import tomllib
import tomli_w
import os
import io
import httpx
import shutil
import asyncio
from PIL import Image
from src.core.fs import path_manager
from src.core.logging import logger

async def fetch_current_image(area: dict):
    x = area["position"]["x"]
    y = area["position"]["y"]

    url = f"https://backend.wplace.live/files/s0/tiles/{x}/{y}.png"
    logger().info(f'正在从 wplace.live 获取 `{area["name"]}` 所在区块...')
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGBA")
    return image


class AreaManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # 只在第一次实例化时执行
            with open(path_manager.get("data/areas.toml"), "rb") as f:
                config = tomllib.load(f)
            self._areas = config["areas"]
            AreaManager._initialized = True

    @property
    def areas(self) -> list[dict]:
        return self._areas
    
    def add_area(self, name, x, y) -> dict:
        logger().info('新区域：正在创建中...')
        new_area = {
            'name': name,
            'position': { 'x': x, 'y': y },
            'ignored': False,
        }
        logger().info('新区域：正在获取当前状态作为参考图...')
        try:
            img = asyncio.run(fetch_current_image(new_area))
            self.update_original(name, img)

        except Exception as e:
            logger().error(f'无法加载参考图: {e}')
            return
        
        logger().info('新区域：正在复制遮罩模板...')
        self.update_mask(name, path_manager.get('assets/mask_template.png'))

        self.areas.append(new_area)
        self.save()
        logger().info('已添加新区域')
        return new_area
    
    def has(self, name: str) -> bool:
        return any([a['name'] == name for a in self._areas])
    
    def area(self, name: str) -> dict:
        return [area for area in self._areas if area['name'] == name][0]
    
    def remove(self, name: str):
        self._areas = [a for a in self._areas if a['name'] != name]
        self.save()
        try:
            os.remove(path_manager.get_mask_image(name))
            os.remove(path_manager.get_original_image(name))
        except Exception:
            pass
    
    def rename_area(self, area: dict, new_name: str):
        old_name = area['name']
        area['name'] = new_name
        
        try:
            if os.path.exists(path_manager.get_mask_image(old_name)):
                os.rename(path_manager.get_mask_image(old_name), path_manager.get_mask_image(new_name))
            if os.path.exists(path_manager.get_original_image(old_name)):
                os.rename(path_manager.get_original_image(old_name), path_manager.get_original_image(new_name))
        except Exception as e:
            print(f"failed to rename data file: {e}")

    def set_position(self, area: dict, x: int, y: int):
        area['position'] = {'x': x, 'y': y }

    def set_ignored(self, area: dict, ignored: bool):
        area['ignored'] = ignored

    def save(self):
        with open(path_manager.get("data/areas.toml"), "wb") as f:
            f.write(tomli_w.dumps({"areas": self._areas}).encode("utf-8"))

    def update_mask(self, area_name: str, mask: str | Image.Image):
        if mask is not None:
            if type(mask) == str:
                try:
                    shutil.copy(mask, path_manager.get_mask_image(area_name))
                except Exception as e:
                    logger().error(f"无法复制遮罩文件: {e}")
            else:
                mask: Image.Image = mask
                try:
                    mask.save(path_manager.get_mask_image(area_name))
                except Exception as e:
                    logger().error(f"无法保存遮罩文件: {e}")  


    def update_original(self, area_name: str, original: str | Image.Image):
        if original is not None:
            if type(original) == str:
                try:
                    shutil.copy(original, path_manager.get_original_image(area_name))
                except Exception as e:
                    logger().error(f"无法复制参考图文件: {e}")
            else:
                original: Image.Image = original
                try:
                    original.save(path_manager.get_original_image(area_name))
                except Exception as e:
                    logger().error(f"无法保存参考图文件: {e}")  

import asyncio
import time
from src.core import load_areas_config, monitor_all, path_manager

if __name__ == "__main__":
    areas = load_areas_config(path_manager.get("data/areas.toml"))
    while True:
        start_time = time.time()
        results = asyncio.run(monitor_all(areas))
        for area_name, result in results.items():
            diffs = result["diffs"]
            diff_image = result["diff_image"]
            if diffs:
                print(f"Area '{area_name}' has {len(diffs)} differences.")
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 300 - elapsed_time)  # 5 minutes interval
        time.sleep(sleep_time)
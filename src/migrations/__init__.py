from .migrator import *
from src.core import logger
from src.core import app_path
import os

def is_version_too_low():
    return not os.path.exists(app_path().get('assets/.migrated')) 

def apply_migrations(from_version: str='0.1.0'):
    logger().info("正在执行版本迁移...")
    migrators = [
        Migrator_0_2_3(),
    ]

    for migrator in migrators:
        if migrator.should_migrate(from_version):
            logger().info(f"正在执行迁移程序 {migrator}...")
            migrator.migrate()
    
    with open(app_path().get('assets/.migrated'), 'w') as _:
        pass


__all__ = [
    "apply_migrations",
]
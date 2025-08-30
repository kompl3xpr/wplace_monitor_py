import os
import shutil
import subprocess
import sys
from pathlib import Path

def main():
    # 获取脚本所在的目录，作为基准路径
    base_path = Path(__file__).resolve().parent
    print(f"当前脚本目录：{base_path}")

    # 定义 PyInstaller 的 spec 文件路径
    spec_file = base_path / 'wplace_monitor_gui.spec'
    if not spec_file.exists():
        print(f"错误: 找不到 {spec_file}。请确保文件存在。")
        sys.exit(1)

    # 定义要复制的源目录和目标目录
    source_dirs = [base_path / 'data', base_path / 'assets']
    target_dist_dir = base_path / 'dist' / 'wplace_monitor_gui'


    requirements_file = base_path / 'requirements.txt'
    if requirements_file.exists():
        print("---")
        print("正在安装依赖...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                check=True
            )
            print("依赖安装成功！")
        except subprocess.CalledProcessError:
            print("错误: 依赖安装失败。请检查 requirements.txt 文件和网络连接。")
            sys.exit(1)
    else:
        print("警告: 找不到 requirements.txt 文件，跳过依赖安装。")

    print("---")
    print("正在启动 PyInstaller 构建...")
    print(f"使用 spec 文件：{spec_file}")
    
    try:
        # 使用 subprocess 运行 PyInstaller 命令
        # check=True 会在命令返回非零退出码时抛出 CalledProcessError
        subprocess.run(
            ['pyinstaller', str(spec_file)], 
            check=True, 
            cwd=base_path
        )
        print("PyInstaller 构建成功！")

        print("---")
        print("正在复制 data 和 assets 文件夹...")
        
        # 复制文件
        for source_dir in source_dirs:
            if source_dir.exists():
                # 确定目标路径
                dest_dir = target_dist_dir / source_dir.name
                
                # 如果目标目录已存在，先删除它以避免 shutil.copytree 报错
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                    print(f"已删除旧目录：{dest_dir}")
                
                shutil.copytree(source_dir, dest_dir)
                print(f"成功复制 {source_dir} 到 {dest_dir}")
            else:
                print(f"警告: 找不到源目录 {source_dir}，跳过复制。")

        print("---")
        print("构建脚本执行完毕。")
        print(f"最终输出位于：{target_dist_dir}")

    except FileNotFoundError:
        print("错误: 找不到 pyinstaller 命令。请确保 PyInstaller 已安装并添加到 PATH。")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"错误: PyInstaller 构建失败，错误代码 {e.returncode}")
        print("请检查 PyInstaller 输出以获取更多详细信息。")
        sys.exit(1)
    except shutil.Error as e:
        print(f"错误: 复制文件时发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
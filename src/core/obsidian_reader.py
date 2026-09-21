"""Obsidian 笔记读取模块：扫描仓库，统计笔记信息"""
import os
import sys
from datetime import datetime, timedelta

# 将 src/ 加入模块搜索路径（支持直接运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_config


def _get_week_start(today):
    """获取本周起始日（周一）"""
    return today - timedelta(days=today.weekday())


def _get_month_start(today):
    """获取本月起始日（1 号）"""
    return today.replace(day=1)


def scan_notes():
    """递归扫描 Obsidian 仓库中的所有 .md 文件

    返回:
        list[dict]: 笔记列表，每条包含 path、name、mtime
    """
    config = get_config()
    vault_path = config["obsidian_vault_path"]
    exclude_folders = config.get("exclude_folders", [])

    if not os.path.exists(vault_path):
        raise FileNotFoundError(f"Obsidian 仓库路径不存在: {vault_path}")

    notes = []
    for root, dirs, files in os.walk(vault_path):
        # 排除指定文件夹
        dirs[:] = [d for d in dirs if d not in exclude_folders]

        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)
                except OSError:
                    # 跳过无法访问的文件（如特殊字符导致的路径问题）
                    continue
                notes.append({
                    "path": file_path,
                    "name": file,
                    "mtime": datetime.fromtimestamp(mtime),
                })

    return notes


def get_statistics(notes):
    """统计笔记信息

    参数:
        notes: scan_notes() 返回的笔记列表

    返回:
        dict: 统计结果
    """
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    week_start = _get_week_start(today)
    month_start = _get_month_start(today)

    # 总笔记数
    total = len(notes)

    # 今日新增（修改时间在今天）
    today_count = sum(1 for n in notes if n["mtime"].strftime("%Y-%m-%d") == today_str)

    # 本周新增（修改时间在本周）
    week_count = sum(1 for n in notes if week_start <= n["mtime"] <= today)

    # 本月新增（修改时间在本月）
    month_count = sum(1 for n in notes if month_start <= n["mtime"] <= today)

    # 最近 10 条笔记（按修改时间倒序）
    recent_notes = sorted(notes, key=lambda n: n["mtime"], reverse=True)[:10]

    return {
        "total": total,
        "today_count": today_count,
        "week_count": week_count,
        "month_count": month_count,
        "recent_notes": recent_notes,
    }


if __name__ == "__main__":
    # 测试：扫描并统计
    print("扫描 Obsidian 仓库...")
    notes = scan_notes()
    stats = get_statistics(notes)

    print(f"总笔记数: {stats['total']}")
    print(f"今日新增: {stats['today_count']}")
    print(f"本周新增: {stats['week_count']}")
    print(f"本月新增: {stats['month_count']}")
    print()
    print("最近 10 条笔记（按修改时间倒序）:")
    print("-" * 60)
    for note in stats["recent_notes"]:
        mtime_str = note["mtime"].strftime("%Y-%m-%d %H:%M")
        print(f"  {mtime_str} | {note['name']}")
        print(f"    {note['path']}")
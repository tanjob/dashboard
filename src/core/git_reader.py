"""Git 提交读取模块：统计指定作者的提交活动"""
import os
import sys
import subprocess
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


def get_commits():
    """调用 git log 获取提交记录

    返回:
        list[dict]: 提交列表，每条包含 date、time、message
    """
    config = get_config()
    repo_path = config["git_repo_path"]
    author = config["git_author"]

    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"Git 仓库路径不存在: {repo_path}")

    # 调用 git log 命令
    cmd = [
        "git", "log",
        f"--author={author}",
        "--since=1 month ago",
        "--pretty=format:%ai|%s",
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError("git log 命令执行超时")
    except FileNotFoundError:
        raise FileNotFoundError("未找到 git 命令，请确认已安装 Git")

    if result.returncode != 0:
        raise RuntimeError(f"git log 执行失败: {result.stderr}")

    # 解析每一行: "2026-09-05 09:00:00 +0800|提交信息"
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue

        timestamp_str, message = parts
        try:
            # 解析 ISO 格式时间戳: 2026-09-05 09:00:00 +0800
            dt = datetime.strptime(timestamp_str.strip(), "%Y-%m-%d %H:%M:%S %z")
            # 转换为本地时间（去掉时区）
            dt = dt.replace(tzinfo=None)
        except ValueError:
            continue

        commits.append({
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M"),
            "datetime": dt,
            "message": message.strip(),
        })

    return commits


def get_statistics(commits):
    """统计提交信息

    参数:
        commits: get_commits() 返回的提交列表

    返回:
        dict: 统计结果
    """
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    week_start = _get_week_start(today)
    month_start = _get_month_start(today)

    # 总提交次数（近一个月）
    total = len(commits)

    # 今日提交
    today_count = sum(1 for c in commits if c["date"] == today_str)

    # 本周提交
    week_count = sum(1 for c in commits if week_start <= c["datetime"] <= today)

    # 本月提交
    month_count = sum(1 for c in commits if month_start <= c["datetime"] <= today)

    # 最近 10 条提交（按时间倒序）
    recent_commits = sorted(commits, key=lambda c: c["datetime"], reverse=True)[:10]

    return {
        "total": total,
        "today_count": today_count,
        "week_count": week_count,
        "month_count": month_count,
        "recent_commits": recent_commits,
    }


if __name__ == "__main__":
    # 测试：获取提交并统计
    print("获取 Git 提交记录...")
    commits = get_commits()
    stats = get_statistics(commits)

    print(f"总提交次数（近一个月）: {stats['total']}")
    print(f"今日提交: {stats['today_count']}")
    print(f"本周提交: {stats['week_count']}")
    print(f"本月提交: {stats['month_count']}")
    print()
    print("最近 10 条提交（按时间倒序）:")
    print("-" * 60)
    for commit in stats["recent_commits"]:
        print(f"  {commit['date']} {commit['time']} | {commit['message'][:40]}")
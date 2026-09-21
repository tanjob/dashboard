"""dashboard CLI 入口：读取日志和笔记，生成日报/周报/月报和图表"""
import sys
import os
from datetime import datetime, timedelta

# 将 src/ 加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_config
from core.log_reader import read_log
from core.obsidian_reader import scan_notes, get_statistics
from core.git_reader import get_commits, get_statistics as get_git_statistics
from core.report_generator import (
    save_report,
    save_weekly_report,
    save_monthly_report,
    generate_charts,
)


def load_data():
    """读取日志、笔记、提交数据"""
    records = read_log()
    print(f"读取到 {len(records)} 条日志记录")

    print("扫描 Obsidian 笔记...")
    notes = scan_notes()
    print(f"总笔记数: {len(notes)}")

    print("获取 Git 提交记录...")
    commits = get_commits()
    print(f"总提交次数: {len(commits)}")

    return records, notes, commits


def build_daily_stats(records, notes, commits):
    """按天分组统计本周的日志、笔记、Git 提交数

    返回:
        dict: {"2026-09-14": {"logs": 2, "notes": 1, "commits": 0}, ...}
    """
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # 周一
    week_end = week_start + timedelta(days=6)  # 周日

    daily_stats = {}

    # 统计日志（按 date 字段）
    for r in records:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if week_start <= d <= week_end:
            date_str = r["date"]
            daily_stats.setdefault(date_str, {"logs": 0, "notes": 0, "commits": 0})
            daily_stats[date_str]["logs"] += 1

    # 统计笔记（按 mtime 日期）
    for n in notes:
        if week_start <= n["mtime"] <= week_end:
            date_str = n["mtime"].strftime("%Y-%m-%d")
            daily_stats.setdefault(date_str, {"logs": 0, "notes": 0, "commits": 0})
            daily_stats[date_str]["notes"] += 1

    # 统计 Git 提交（按 date 字段）
    for c in commits:
        try:
            d = datetime.strptime(c["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if week_start <= d <= week_end:
            date_str = c["date"]
            daily_stats.setdefault(date_str, {"logs": 0, "notes": 0, "commits": 0})
            daily_stats[date_str]["commits"] += 1

    return daily_stats


def generate_daily(records, notes, commits):
    """生成日报"""
    # 检查今日报告是否已生成
    config = get_config()
    report_file = config["report_file"]
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        config["output_dir"],
        report_file,
    )
    if os.path.exists(report_path):
        report_mtime = datetime.fromtimestamp(os.path.getmtime(report_path))
        today_str = datetime.now().strftime("%Y-%m-%d")
        if report_mtime.strftime("%Y-%m-%d") == today_str:
            print("今日报告已生成，跳过")
            return

    # 统计并生成日报
    notes_stats = get_statistics(notes)
    git_stats = get_git_statistics(commits)
    report_path = save_report(records, notes_stats, git_stats)
    print(f"报告已生成：output/{report_file}")

    # 生成图表
    daily_stats = build_daily_stats(records, notes, commits)
    chart_file = generate_charts(daily_stats)
    print(f"图表已生成：{os.path.basename(chart_file)}")


def generate_weekly(records, notes, commits):
    """生成周报"""
    report_path = save_weekly_report(records, notes, commits)
    print(f"周报已生成：{os.path.basename(report_path)}")

    # 生成图表
    daily_stats = build_daily_stats(records, notes, commits)
    chart_file = generate_charts(daily_stats)
    print(f"图表已生成：{os.path.basename(chart_file)}")


def generate_monthly(records, notes, commits):
    """生成月报"""
    report_path = save_monthly_report(records, notes, commits)
    print(f"月报已生成：{os.path.basename(report_path)}")

    # 生成图表
    daily_stats = build_daily_stats(records, notes, commits)
    chart_file = generate_charts(daily_stats)
    print(f"图表已生成：{os.path.basename(chart_file)}")


def main():
    """CLI 入口"""
    # 0. 配置检查
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(project_root, "config.json")

    # 检查 config.json 是否存在
    if not os.path.exists(config_path):
        print("请先复制 config.example.json 为 config.json，并填写你的路径")
        print("命令: copy config.example.json config.json")
        return

    # 检查 obsidian_vault_path 是否为空
    config = get_config()
    if not config.get("obsidian_vault_path"):
        print("请填写你的 Obsidian 仓库绝对路径")
        print("在 config.json 中设置 obsidian_vault_path 字段")
        return

    # 解析命令
    if len(sys.argv) < 2:
        print("使用方法: python dashboard.py <today|week|month>")
        print("  today  - 生成今日报告")
        print("  week   - 生成本周报告")
        print("  month  - 生成本月报告")
        return

    command = sys.argv[1]

    # 读取数据（三个命令共用）
    records, notes, commits = load_data()

    # 根据命令分发
    if command == "today":
        print("生成今日报告...")
        generate_daily(records, notes, commits)
    elif command == "week":
        print("生成本周报告...")
        generate_weekly(records, notes, commits)
    elif command == "month":
        print("生成本月报告...")
        generate_monthly(records, notes, commits)
    else:
        print(f"未知命令: {command}")
        print("使用方法: python dashboard.py <today|week|month>")


if __name__ == "__main__":
    main()
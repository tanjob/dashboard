"""报告生成模块：统计今日/本周/本月记录，生成 Markdown 报告"""
import os
import sys
from datetime import datetime, timedelta

# 将 src/ 加入模块搜索路径（支持直接运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_config, get_project_root
from common.utils import get_output_path, ensure_dir


def _parse_date(date_str):
    """解析日期字符串为 datetime 对象"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _get_week_start(today):
    """获取本周起始日（周一）"""
    return today - timedelta(days=today.weekday())


def _get_month_start(today):
    """获取本月起始日（1 号）"""
    return today.replace(day=1)


def _get_month_end(today):
    """获取本月结束日（月末）"""
    if today.month == 12:
        return today.replace(year=today.year + 1, month=1) - timedelta(days=1)
    return today.replace(month=today.month + 1) - timedelta(days=1)


def _in_range(dt, start, end):
    """判断时间是否在 [start, end] 范围内"""
    return dt is not None and start <= dt <= end


def _build_report(title, period_records, period_notes, period_commits, period_label):
    """构建通用报告内容（周报/月报共用）

    参数:
        title: 报告标题（如"学习周报"）
        period_records: 时间范围内的日志记录
        period_notes: 时间范围内的笔记（带 mtime）
        period_commits: 时间范围内的提交（带 datetime）
        period_label: 时间范围标签（如"本周"、"本月"）
    """
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"**{period_label}记录：** {len(period_records)} 条")
    lines.append(f"**{period_label}笔记：** {len(period_notes)} 条")
    lines.append(f"**{period_label}提交：** {len(period_commits)} 条")
    lines.append("")

    # 学习记录列表
    lines.append(f"## {period_label}的学习记录")
    lines.append("")
    if period_records:
        for record in period_records:
            time_str = record["time"] if record["time"] else "未知时间"
            content = record["content"] if record["content"] else "无内容"
            lines.append(f"- **{time_str}**：{content}")
    else:
        lines.append(f"_{period_label}还没有学习记录_")
    lines.append("")

    # 按日期统计
    lines.append(f"## {period_label}学习统计")
    lines.append("")
    if period_records:
        daily_count = {}
        for r in period_records:
            daily_count[r["date"]] = daily_count.get(r["date"], 0) + 1
        lines.append("| 日期 | 记录数 |")
        lines.append("|------|--------|")
        for date in sorted(daily_count.keys()):
            lines.append(f"| {date} | {daily_count[date]} |")
    else:
        lines.append(f"_{period_label}还没有学习记录_")
    lines.append("")

    # 笔记统计
    lines.append(f"## {period_label}笔记统计")
    lines.append("")
    if period_notes:
        lines.append(f"**{period_label}新增笔记：** {len(period_notes)} 条")
        lines.append("")
        lines.append(f"### {period_label}笔记列表（按修改时间倒序）")
        lines.append("")
        lines.append("| 修改时间 | 文件名 |")
        lines.append("|---------|--------|")
        sorted_notes = sorted(period_notes, key=lambda n: n["mtime"], reverse=True)[:10]
        for note in sorted_notes:
            mtime_str = note["mtime"].strftime("%Y-%m-%d %H:%M")
            lines.append(f"| {mtime_str} | {note['name']} |")
    else:
        lines.append(f"_{period_label}没有新增笔记_")
    lines.append("")

    # Git 提交统计
    lines.append(f"## {period_label}Git 提交统计")
    lines.append("")
    if period_commits:
        lines.append(f"**{period_label}提交次数：** {len(period_commits)} 条")
        lines.append("")
        lines.append(f"### {period_label}提交列表（按时间倒序）")
        lines.append("")
        lines.append("| 提交时间 | 提交信息 |")
        lines.append("|---------|---------|")
        sorted_commits = sorted(period_commits, key=lambda c: c["datetime"], reverse=True)[:10]
        for commit in sorted_commits:
            time_str = f"{commit['date']} {commit['time']}"
            lines.append(f"| {time_str} | {commit['message']} |")
    else:
        lines.append(f"_{period_label}没有提交记录_")
    lines.append("")

    return "\n".join(lines)


def generate_weekly_report(records, notes=None, commits=None):
    """统计本周（周一至周日）的学习日志、笔记、Git 提交

    参数:
        records: 日志记录列表
        notes: 笔记列表（obsidian_reader.scan_notes 返回）
        commits: 提交列表（git_reader.get_commits 返回）

    返回:
        str: Markdown 格式的周报
    """
    today = datetime.now()
    week_start = _get_week_start(today)
    week_end = week_start + timedelta(days=6)  # 周日

    week_records = [r for r in records if _in_range(_parse_date(r["date"]), week_start, week_end)]
    week_notes = [n for n in notes if _in_range(n["mtime"], week_start, week_end)] if notes else []
    week_commits = [c for c in commits if _in_range(c["datetime"], week_start, week_end)] if commits else []

    return _build_report("学习周报", week_records, week_notes, week_commits, "本周")


def generate_monthly_report(records, notes=None, commits=None):
    """统计本月（1 日至月末）的学习日志、笔记、Git 提交

    参数:
        records: 日志记录列表
        notes: 笔记列表（obsidian_reader.scan_notes 返回）
        commits: 提交列表（git_reader.get_commits 返回）

    返回:
        str: Markdown 格式的月报
    """
    today = datetime.now()
    month_start = _get_month_start(today)
    month_end = _get_month_end(today)

    month_records = [r for r in records if _in_range(_parse_date(r["date"]), month_start, month_end)]
    month_notes = [n for n in notes if _in_range(n["mtime"], month_start, month_end)] if notes else []
    month_commits = [c for c in commits if _in_range(c["datetime"], month_start, month_end)] if commits else []

    return _build_report("学习月报", month_records, month_notes, month_commits, "本月")


def save_weekly_report(records, notes=None, commits=None):
    """生成周报并保存，文件名带日期戳 weekly_report_2026-09-18.md

    返回:
        str: 报告文件路径
    """
    config = get_config()
    output_dir = get_output_path()
    ensure_dir(output_dir)

    report_content = generate_weekly_report(records, notes, commits)
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_file = get_output_path(f"weekly_report_{today_str}.md")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_file


def save_monthly_report(records, notes=None, commits=None):
    """生成月报并保存，文件名带日期戳 monthly_report_2026-09.md

    返回:
        str: 报告文件路径
    """
    config = get_config()
    output_dir = get_output_path()
    ensure_dir(output_dir)

    report_content = generate_monthly_report(records, notes, commits)
    month_str = datetime.now().strftime("%Y-%m")
    report_file = get_output_path(f"monthly_report_{month_str}.md")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_file


def generate_charts(daily_stats):
    """生成 HTML 图表（Chart.js，本地引用不依赖 CDN）

    参数:
        daily_stats: 按天分组的统计结果
                     {"2026-09-14": {"logs": 2, "notes": 3, "commits": 1}, ...}

    返回:
        str: HTML 文件路径
    """
    config = get_config()
    chart_dir = os.path.join(get_project_root(), config["chart_output_dir"])
    ensure_dir(chart_dir)

    # 准备图表数据
    dates = sorted(daily_stats.keys())
    logs_data = [daily_stats[d].get("logs", 0) for d in dates]
    notes_data = [daily_stats[d].get("notes", 0) for d in dates]
    commits_data = [daily_stats[d].get("commits", 0) for d in dates]

    # 三个数据源的总量（柱状图）
    total_logs = sum(logs_data)
    total_notes = sum(notes_data)
    total_commits = sum(commits_data)

    # 本地 Chart.js 路径（相对 HTML 文件）
    chart_js_path = os.path.join("..", "static", "chart.min.js")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学习统计图表 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <script src="{chart_js_path}"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .chart-container h2 {{
            color: #34495e;
            margin-top: 0;
        }}
        canvas {{
            max-height: 400px;
        }}
    </style>
</head>
<body>
    <h1>学习统计图表</h1>
    <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="chart-container">
        <h2>本周每天学习条数（折线图）</h2>
        <canvas id="lineChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>数据源数量对比（柱状图）</h2>
        <canvas id="barChart"></canvas>
    </div>

    <script>
        // 折线图：本周每天的学习条数
        const lineCtx = document.getElementById('lineChart').getContext('2d');
        new Chart(lineCtx, {{
            type: 'line',
            data: {{
                labels: {dates},
                datasets: [
                    {{
                        label: '日志',
                        data: {logs_data},
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.3
                    }},
                    {{
                        label: '笔记',
                        data: {notes_data},
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.3
                    }},
                    {{
                        label: 'Git 提交',
                        data: {commits_data},
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: '本周每天学习条数' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});

        // 柱状图：三个数据源的数量对比
        const barCtx = document.getElementById('barChart').getContext('2d');
        new Chart(barCtx, {{
            type: 'bar',
            data: {{
                labels: ['日志', '笔记', 'Git 提交'],
                datasets: [{{
                    label: '数量',
                    data: [{total_logs}, {total_notes}, {total_commits}],
                    backgroundColor: ['#3498db', '#2ecc71', '#e74c3c']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: '三个数据源数量对比' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    # 保存 HTML 文件，文件名带日期戳
    today_str = datetime.now().strftime("%Y-%m-%d")
    chart_file = os.path.join(chart_dir, f"charts_{today_str}.html")

    with open(chart_file, "w", encoding="utf-8") as f:
        f.write(html)

    return chart_file


def generate_report(records, notes_stats=None, git_stats=None):
    """根据日志记录生成统计报告

    参数:
        records: log_reader 返回的记录列表
                 [{"date": "2026-09-05", "time": "01:00", "content": "..."}]
        notes_stats: obsidian_reader 返回的笔记统计（可选）
                     {"total": 431, "today_count": 4, ...}
        git_stats: git_reader 返回的提交统计（可选）
                   {"total": 1, "today_count": 0, ...}

    返回:
        str: Markdown 格式的报告
    """
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    week_start = _get_week_start(today)
    month_start = _get_month_start(today)

    # 1. 统计今天的记录
    today_records = [r for r in records if r["date"] == today_str]

    # 2. 统计本周的记录（本周一至今）
    week_records = []
    for r in records:
        d = _parse_date(r["date"])
        if d and week_start <= d <= today:
            week_records.append(r)

    # 3. 统计本月的记录（本月 1 号至今）
    month_records = []
    for r in records:
        d = _parse_date(r["date"])
        if d and month_start <= d <= today:
            month_records.append(r)

    # 生成报告
    lines = []
    lines.append("# 学习日报")
    lines.append("")
    lines.append(f"**生成时间：** {today.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"**今日记录：** {len(today_records)} 条")
    lines.append(f"**本周记录：** {len(week_records)} 条")
    lines.append(f"**本月记录：** {len(month_records)} 条")
    lines.append("")

    # 今天的学习记录列表
    lines.append("## 今天的学习记录")
    lines.append("")
    if today_records:
        for record in today_records:
            time_str = record["time"] if record["time"] else "未知时间"
            content = record["content"] if record["content"] else "无内容"
            lines.append(f"- **{time_str}**：{content}")
    else:
        lines.append("_今天还没有学习记录_")
    lines.append("")

    # 本周学习统计
    lines.append("## 本周学习统计")
    lines.append("")
    if week_records:
        # 按日期分组统计
        daily_count = {}
        for r in week_records:
            daily_count[r["date"]] = daily_count.get(r["date"], 0) + 1
        lines.append("| 日期 | 记录数 |")
        lines.append("|------|--------|")
        for date in sorted(daily_count.keys()):
            lines.append(f"| {date} | {daily_count[date]} |")
    else:
        lines.append("_本周还没有学习记录_")
    lines.append("")

    # 本月学习统计
    lines.append("## 本月学习统计")
    lines.append("")
    if month_records:
        # 按周分组统计
        week_count = {}
        for r in month_records:
            d = _parse_date(r["date"])
            if d:
                week_num = (d - month_start).days // 7 + 1
                week_key = f"第 {week_num} 周"
                week_count[week_key] = week_count.get(week_key, 0) + 1
        lines.append("| 周次 | 记录数 |")
        lines.append("|------|--------|")
        for week in sorted(week_count.keys()):
            lines.append(f"| {week} | {week_count[week]} |")
    else:
        lines.append("_本月还没有学习记录_")
    lines.append("")

    # ========== 笔记统计 ==========
    lines.append("## 笔记统计")
    lines.append("")
    if notes_stats:
        lines.append(f"**总笔记数：** {notes_stats['total']}")
        lines.append(f"**今日新增：** {notes_stats['today_count']}")
        lines.append(f"**本周新增：** {notes_stats['week_count']}")
        lines.append(f"**本月新增：** {notes_stats['month_count']}")
        lines.append("")

        lines.append("### 最近 10 条笔记（按修改时间倒序）")
        lines.append("")
        lines.append("| 修改时间 | 文件名 |")
        lines.append("|---------|--------|")
        for note in notes_stats["recent_notes"]:
            mtime_str = note["mtime"].strftime("%Y-%m-%d %H:%M")
            lines.append(f"| {mtime_str} | {note['name']} |")
    else:
        lines.append("_未提供笔记统计_")
    lines.append("")

    # ========== Git 提交统计 ==========
    lines.append("## Git 提交统计")
    lines.append("")
    if git_stats:
        lines.append(f"**总提交次数：** {git_stats['total']}")
        lines.append(f"**今日提交：** {git_stats['today_count']}")
        lines.append(f"**本周提交：** {git_stats['week_count']}")
        lines.append(f"**本月提交：** {git_stats['month_count']}")
        lines.append("")

        lines.append("### 最近 10 条提交（按时间倒序）")
        lines.append("")
        lines.append("| 提交时间 | 提交信息 |")
        lines.append("|---------|---------|")
        for commit in git_stats["recent_commits"]:
            time_str = f"{commit['date']} {commit['time']}"
            lines.append(f"| {time_str} | {commit['message']} |")
    else:
        lines.append("_未提供 Git 提交统计_")
    lines.append("")

    return "\n".join(lines)


def save_report(records, notes_stats=None, git_stats=None):
    """生成报告并保存到 output 目录

    参数:
        records: 日志记录列表
        notes_stats: 笔记统计（可选）
        git_stats: Git 提交统计（可选）

    返回:
        str: 报告文件路径
    """
    config = get_config()
    output_dir = get_output_path()
    ensure_dir(output_dir)

    report_content = generate_report(records, notes_stats, git_stats)
    report_file = get_output_path(config["report_file"])

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_file


if __name__ == "__main__":
    # 测试：读取日志并生成报告
    from core.log_reader import read_log

    records = read_log()
    print(f"读取到 {len(records)} 条记录")
    report_file = save_report(records)
    print(f"报告已生成: {report_file}")
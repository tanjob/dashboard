"""dashboard Web 应用：浏览器生成日报/周报/月报"""
import sys
import os
from datetime import datetime

# 将 src/ 加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, render_template, render_template_string, jsonify
import markdown

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

app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "templates",
    ),
)

# ========== 首页 HTML ==========
INDEX_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dashboard 学习日报生成器</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .buttons {
            display: flex;
            gap: 15px;
            margin: 30px 0;
        }
        .btn {
            flex: 1;
            padding: 15px 20px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            color: white;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .btn-daily { background: #3498db; }
        .btn-week { background: #2ecc71; }
        .btn-month { background: #e74c3c; }
        .result {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .result h2 { color: #34495e; }
        .report-content {
            line-height: 1.8;
            padding: 15px;
            background: #fafafa;
            border-radius: 6px;
            border: 1px solid #eee;
        }
        .report-content table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        .report-content th, .report-content td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .report-content th { background: #f0f0f0; }
        .chart-frame {
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-top: 15px;
        }
        .loading { color: #888; font-style: italic; }
    </style>
</head>
<body>
    <h1>📊 dashboard 学习日报生成器</h1>
    <p>选择要生成的报告类型：</p>

    <div class="buttons">
        <button class="btn btn-daily" onclick="generate('daily')">生成日报</button>
        <button class="btn btn-week" onclick="generate('week')">生成周报</button>
        <button class="btn btn-month" onclick="generate('month')">生成月报</button>
    </div>

    <div id="result" class="result" style="display:none;">
        <h2 id="result-title"></h2>
        <div id="result-body"></div>
    </div>

    <script>
        async function generate(type) {
            const resultDiv = document.getElementById('result');
            const titleEl = document.getElementById('result-title');
            const bodyEl = document.getElementById('result-body');

            resultDiv.style.display = 'block';
            titleEl.textContent = '正在生成...';
            bodyEl.innerHTML = '<p class="loading">请稍候，正在生成报告...</p>';

            try {
                const resp = await fetch('/generate/' + type, { method: 'POST' });
                const data = await resp.json();

                if (data.success) {
                    titleEl.textContent = data.title;
                    bodyEl.innerHTML = data.report_html + data.chart_html;
                } else {
                    titleEl.textContent = '生成失败';
                    bodyEl.innerHTML = '<p style="color:red">' + data.error + '</p>';
                }
            } catch (e) {
                titleEl.textContent = '错误';
                bodyEl.innerHTML = '<p style="color:red">请求失败: ' + e + '</p>';
            }
        }
    </script>
</body>
</html>
"""


def load_data():
    """读取日志、笔记、提交数据"""
    records = read_log()
    notes = scan_notes()
    commits = get_commits()
    return records, notes, commits


def build_daily_stats(records, notes, commits):
    """按天分组统计本周数据（用于图表）"""
    from datetime import timedelta
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    daily_stats = {}
    for r in records:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if week_start <= d <= week_end:
            daily_stats.setdefault(r["date"], {"logs": 0, "notes": 0, "commits": 0})
            daily_stats[r["date"]]["logs"] += 1
    for n in notes:
        if week_start <= n["mtime"] <= week_end:
            date_str = n["mtime"].strftime("%Y-%m-%d")
            daily_stats.setdefault(date_str, {"logs": 0, "notes": 0, "commits": 0})
            daily_stats[date_str]["notes"] += 1
    for c in commits:
        try:
            d = datetime.strptime(c["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if week_start <= d <= week_end:
            daily_stats.setdefault(c["date"], {"logs": 0, "notes": 0, "commits": 0})
            daily_stats[c["date"]]["commits"] += 1
    return daily_stats


def read_report_content(report_path):
    """读取报告文件内容"""
    with open(report_path, "r", encoding="utf-8") as f:
        return f.read()


def read_chart_html(chart_path):
    """读取图表 HTML 文件内容"""
    with open(chart_path, "r", encoding="utf-8") as f:
        return f.read()


@app.route("/", methods=["GET"])
def index():
    """首页"""
    return render_template("index.html")


@app.route("/charts/<filename>", methods=["GET"])
def serve_chart(filename):
    """提供图表 HTML 文件"""
    config = get_config()
    chart_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        config["chart_output_dir"],
    )
    chart_path = os.path.join(chart_dir, filename)
    if os.path.exists(chart_path):
        with open(chart_path, "r", encoding="utf-8") as f:
            return f.read()
    return "图表文件不存在", 404


@app.route("/generate/<report_type>", methods=["POST"])
def generate(report_type):
    """生成报告"""
    try:
        records, notes, commits = load_data()

        # 根据类型调用对应函数
        if report_type == "daily":
            notes_stats = get_statistics(notes)
            git_stats = get_git_statistics(commits)
            report_path = save_report(records, notes_stats, git_stats)
            title = "📋 日报"
        elif report_type == "week":
            report_path = save_weekly_report(records, notes, commits)
            title = "📅 周报"
        elif report_type == "month":
            report_path = save_monthly_report(records, notes, commits)
            title = "📆 月报"
        else:
            return {"success": False, "error": f"未知报告类型: {report_type}"}, 400

        # 生成图表
        daily_stats = build_daily_stats(records, notes, commits)
        chart_path = generate_charts(daily_stats)

        # 读取报告内容并渲染 Markdown
        report_content = read_report_content(report_path)
        report_html = markdown.markdown(
            report_content,
            extensions=["tables", "fenced_code"],
        )

        # 图表通过 Flask 路由提供（替代 file:/// 协议）
        chart_filename = os.path.basename(chart_path)

        return {
            "success": True,
            "title": title,
            "report_html": f'<div class="report-content">{report_html}</div>',
            "chart_html": f'<iframe class="chart-frame" src="/charts/{chart_filename}"></iframe>',
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


if __name__ == "__main__":
    print("dashboard Web 应用启动")
    print("访问: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
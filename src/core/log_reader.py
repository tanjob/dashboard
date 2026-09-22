"""日志读取模块：从 SQLite 数据库读取 daily_log 表记录"""
import os
import sys
import sqlite3

# 将 src/ 加入模块搜索路径（支持直接运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_config
from common.utils import get_data_path


def read_log():
    """读取 SQLite 数据库中的 daily_log 表，返回记录列表

    每条记录: {"date": "2026-09-05", "time": "01:00", "content": "日志内容"}

    返回:
        list[dict]: 记录列表，每条包含 date、time、content
    """
    config = get_config()
    db_path = get_data_path("dashboard.db")

    # 数据库不存在时返回空列表
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date, content FROM daily_log ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    records = []
    for date_ts, content in rows:
        # date 字段可能存完整时间戳 "2026-09-05 01:00" 或仅日期 "2026-09-22"
        if " " in date_ts:
            date = date_ts[:10]     # 日期部分: 2026-09-05
            time = date_ts[11:]     # 时间部分: 01:00
        else:
            date = date_ts
            time = ""

        records.append({
            "date": date,
            "time": time,
            "content": content,
        })

    return records


def count_records():
    """统计记录总数"""
    return len(read_log())


if __name__ == "__main__":
    # 测试：读取并打印记录
    records = read_log()
    print(f"共读取到 {len(records)} 条记录")
    print("=" * 50)
    for record in records:
        print(f"日期: {record['date']} | 时间: {record['time']}")
        print(f"内容: {record['content'][:40]}")
        print("-" * 50)
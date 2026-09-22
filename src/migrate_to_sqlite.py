"""迁移脚本：把 daily_log.md 的记录迁移到 SQLite 数据库"""
import os
import sqlite3
import sys

# 将 src/ 加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.config import get_config
from common.utils import get_data_path, ensure_dir


def parse_md_records(md_path):
    """读取 daily_log.md，按 --- 分隔成多条记录

    每条记录: {"timestamp": "2026-08-26 07:48", "content": "日志内容"}
    """
    if not os.path.exists(md_path):
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    records = []
    for record in content.split("---"):
        record = record.strip()
        if not record:
            continue

        lines = record.split("\n")
        timestamp = ""
        content_lines = []

        for line in lines:
            # 时间戳行格式: ## 2026-08-26 07:48
            if line.startswith("## ") and len(line) > 3:
                timestamp = line[3:].strip()
            else:
                content_lines.append(line)

        records.append({
            "timestamp": timestamp,
            "content": "\n".join(content_lines).strip(),
        })

    return records


def migrate():
    """执行迁移"""
    config = get_config()

    # 1. 读取 daily_log.md
    md_path = get_data_path(config["log_file"])
    records = parse_md_records(md_path)
    print(f"读取到 {len(records)} 条记录")

    # 2. 创建 SQLite 数据库文件 data/dashboard.db
    db_path = get_data_path("dashboard.db")
    ensure_dir(os.path.dirname(db_path))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. 创建表 daily_log（字段：id, date, content）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            content TEXT
        )
    """)

    # 清空旧数据，避免重复迁移
    cursor.execute("DELETE FROM daily_log")

    # 4. 插入所有记录（date 存完整时间戳，便于读取时拆分日期和时间）
    for record in records:
        cursor.execute(
            "INSERT INTO daily_log (date, content) VALUES (?, ?)",
            (record["timestamp"], record["content"]),
        )

    conn.commit()
    count = cursor.execute("SELECT COUNT(*) FROM daily_log").fetchone()[0]
    conn.close()

    # 5. 打印迁移结果
    print(f"迁移完成，共插入 {count} 条记录")
    print(f"数据库文件: {db_path}")


if __name__ == "__main__":
    migrate()
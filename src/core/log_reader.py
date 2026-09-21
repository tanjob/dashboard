"""日志读取模块：从 config.json 读取路径，解析 daily_log.md"""
import os
import sys

# 将 src/ 加入模块搜索路径（支持直接运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_config
from common.utils import get_data_path


def read_log():
    """读取 daily_log.md，返回记录列表

    每条记录: {"date": "2026-09-05", "time": "01:00", "content": "日志内容"}

    返回:
        list[dict]: 记录列表，每条包含 date、time、content
    """
    # 1. 从 config.json 读取 daily_log.md 的路径
    config = get_config()
    log_file = get_data_path(config["log_file"])

    # 文件不存在时返回空列表
    if not os.path.exists(log_file):
        return []

    # 2. 读取文件内容，按 "---" 分隔成多条记录
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()

    records = []
    for record in content.split("---"):
        record = record.strip()
        if not record:
            continue

        # 解析每条记录：提取日期时间和内容
        lines = record.split("\n")
        timestamp = ""
        content_lines = []

        for line in lines:
            # 时间戳行格式: ## 2026-09-05 01:00
            if line.startswith("## ") and len(line) > 3:
                timestamp = line[3:].strip()
            else:
                content_lines.append(line)

        # 3. 返回每条记录的日期和内容
        if timestamp:
            date = timestamp[:10]      # 日期部分: 2026-09-05
            time = timestamp[11:]      # 时间部分: 01:00
        else:
            date = ""
            time = ""

        records.append({
            "date": date,
            "time": time,
            "content": "\n".join(content_lines).strip(),
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
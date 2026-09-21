# dashboard

日志统计工具：读取 `daily_log.md`，生成 Markdown 格式的统计报告。

## 项目结构

```
dashboard/
├── config.json              # 配置文件
├── README.md                # 项目说明
├── data/                    # 数据目录（存放 daily_log.md）
├── output/                  # 输出目录（存放生成的报告）
└── src/
    ├── main/
    │   └── dashboard.py     # CLI 入口
    ├── core/
    │   ├── log_reader.py    # 读取 daily_log.md
    │   └── report_generator.py  # 生成报告
    └── common/
        ├── config.py        # 读取配置
        └── utils.py         # 公共工具
```

## 功能

- 读取 `data/daily_log.md` 中的日志记录
- 按日期统计记录数量
- 显示最近 10 条记录
- 生成 Markdown 格式报告到 `output/report.md`

## 使用方法

```bash
# 进入项目目录
cd C:\Projects\dashboard

# 运行 CLI
python src\main\dashboard.py
```

## 输出示例

```
==================================================
        dashboard - 日志统计工具
==================================================

读取到 11 条日志记录
报告已生成: C:\Projects\dashboard\output\report.md

==================================================
报告摘要:
  记录总数: 11
  报告文件: C:\Projects\dashboard\output\report.md
==================================================
```

## 配置说明

`config.json` 中的配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `data_dir` | 数据目录 | `data` |
| `log_file` | 日志文件名 | `daily_log.md` |
| `output_dir` | 输出目录 | `output` |
| `report_file` | 报告文件名 | `report.md` |
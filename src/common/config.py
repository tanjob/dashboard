"""配置读取模块"""
import json
import os


# 默认配置（config.json 不存在时使用，如云端部署）
DEFAULT_CONFIG = {
    "data_dir": "data",
    "log_file": "daily_log.md",
    "categories_file": "service_categories.md",
    "output_dir": "output",
    "report_file": "daily_report.md",
    "chart_output_dir": "output",
    "search_results_limit": 10,
    "obsidian_vault_path": "",
    "exclude_folders": [".obsidian", ".git", "node_modules", "output"],
    "git_repo_path": "",
    "git_author": "",
}


class Config:
    """读取配置：优先环境变量 > config.json > 默认配置"""

    def __init__(self, project_root=None):
        self.project_root = project_root or self._detect_project_root()
        self._data = None

    def _detect_project_root(self):
        """自动检测项目根目录（config.py 所在目录的上两级）"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(script_dir))

    def read(self):
        """读取配置"""
        if self._data is None:
            # 1. 优先从环境变量 DASHBOARD_CONFIG 读取（云端部署场景）
            env_config = os.environ.get("DASHBOARD_CONFIG")
            if env_config:
                try:
                    self._data = json.loads(env_config)
                    return self._data
                except json.JSONDecodeError:
                    pass  # 环境变量格式错误，继续尝试其他方式

            # 2. 读取 config.json
            config_path = os.path.join(self.project_root, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            else:
                # 3. 配置文件不存在时使用默认配置（如云端部署）
                self._data = DEFAULT_CONFIG.copy()

        return self._data

    def get(self, key, default=None):
        """获取配置项"""
        return self.read().get(key, default)


# 模块级单例
_config = Config()


def get_config():
    """获取配置（单例）"""
    return _config.read()


def get_project_root():
    """获取项目根目录"""
    return _config.project_root
"""配置读取模块"""
import json
import os


class Config:
    """读取 config.json 配置"""

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
            config_path = os.path.join(self.project_root, "config.json")
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
            with open(config_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
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
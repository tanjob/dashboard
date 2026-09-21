"""公共工具模块"""
import os
from .config import get_config, get_project_root


def get_data_path(filename=None):
    """获取 data 目录下的文件路径"""
    config = get_config()
    data_dir = os.path.join(get_project_root(), config["data_dir"])
    if filename:
        return os.path.join(data_dir, filename)
    return data_dir


def get_output_path(filename=None):
    """获取 output 目录下的文件路径"""
    config = get_config()
    output_dir = os.path.join(get_project_root(), config["output_dir"])
    if filename:
        return os.path.join(output_dir, filename)
    return output_dir


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
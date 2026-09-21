@echo off
chcp 65001 >nul
title dashboard 学习日报生成器

echo ==========================================
echo         dashboard 学习日报生成器
echo ==========================================
echo.

REM ========== 1. 检测 Python ==========
echo [1/4] 检测 Python...
python --version >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.7 以上版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "delims=" %%v in ('python --version 2^>^&1') do echo [OK] 已检测到 %%v

REM ========== 2. 检测 config.json ==========
echo.
echo [2/4] 检测配置文件...
if not exist "config.json" (
    echo [错误] 未找到 config.json
    echo 请先复制 config.example.json 为 config.json，并填写你的配置
    echo 命令: copy config.example.json config.json
    pause
    exit /b 1
)
echo [OK] 配置文件存在

REM ========== 3. 安装依赖 ==========
echo.
echo [3/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [警告] 依赖安装可能失败，请检查网络或手动执行 pip install -r requirements.txt
)

REM ========== 4. 生成今日报告 ==========
echo.
echo [4/4] 生成今日报告...
python src\main\dashboard.py today

REM ========== 5. 完成 ==========
echo.
echo ==========================================
echo 执行完毕！报告和图表在 output 目录下
echo ==========================================
pause
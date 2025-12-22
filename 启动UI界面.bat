@echo off
chcp 65001 >nul
echo ========================================
echo  Modbus协议信息提取工具 - Web UI
echo ========================================
echo.
echo 正在启动 Gradio 界面...
echo.
echo 启动后浏览器会自动打开，或手动访问：
echo http://localhost:7860
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

cd /d "%~dp0"
uv run python app.py

pause


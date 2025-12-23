@echo off
chcp 65001 >nul
echo ================================
echo  启动 MinerU PDF解析服务
echo ================================
echo.
echo 服务地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo.
echo 提示: 保持此窗口打开以维持服务运行
echo 按 Ctrl+C 可以停止服务
echo.
echo ================================
echo.

uv run python -m mineru.server --host 0.0.0.0 --port 8000

pause


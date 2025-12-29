@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo                    鉴权功能演示
echo ═══════════════════════════════════════════════════════════════
echo.
echo 本脚本将演示鉴权功能的各项特性
echo.
echo ═══════════════════════════════════════════════════════════════
echo                    演示步骤
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. 查看当前鉴权配置
echo 2. 运行鉴权功能测试
echo 3. 启动用户管理工具
echo 4. 启动应用（带鉴权）
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
echo.

:menu
cls
echo ═══════════════════════════════════════════════════════════════
echo                    鉴权功能演示菜单
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. 查看鉴权配置文件
echo 2. 运行鉴权功能测试
echo 3. 启动用户管理工具
echo 4. 启动应用（带鉴权）
echo 5. 查看帮助文档
echo 0. 退出
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
set /p choice=请选择 (0-5): 

if "%choice%"=="1" goto show_config
if "%choice%"=="2" goto run_test
if "%choice%"=="3" goto manage_users
if "%choice%"=="4" goto start_app
if "%choice%"=="5" goto show_help
if "%choice%"=="0" goto end
goto menu

:show_config
cls
echo ═══════════════════════════════════════════════════════════════
echo                    当前鉴权配置
echo ═══════════════════════════════════════════════════════════════
echo.
type config\auth.json
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
goto menu

:run_test
cls
echo ═══════════════════════════════════════════════════════════════
echo                    运行鉴权功能测试
echo ═══════════════════════════════════════════════════════════════
echo.
uv run python test_auth.py
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
goto menu

:manage_users
cls
echo ═══════════════════════════════════════════════════════════════
echo                    用户管理工具
echo ═══════════════════════════════════════════════════════════════
echo.
uv run python manage_users.py
echo.
pause
goto menu

:start_app
cls
echo ═══════════════════════════════════════════════════════════════
echo                    启动应用（带鉴权）
echo ═══════════════════════════════════════════════════════════════
echo.
echo 应用将在浏览器中打开...
echo.
echo 默认登录信息：
echo   用户名: admin
echo   密码: admin123
echo.
echo 按 Ctrl+C 停止应用
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
uv run python app.py
pause
goto menu

:show_help
cls
echo ═══════════════════════════════════════════════════════════════
echo                    帮助文档
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📖 详细文档：
echo.
echo   1. AUTHENTICATION_GUIDE.md       - 完整使用指南
echo   2. QUICKSTART_AUTH.md            - 快速开始指南
echo   3. config\AUTH_README.md         - 配置文件说明
echo   4. AUTH_IMPLEMENTATION_SUMMARY.md - 实现总结
echo   5. CHANGELOG_AUTH.md             - 更新日志
echo   6. 鉴权功能说明.txt               - 中文说明
echo.
echo 🔧 工具脚本：
echo.
echo   1. manage_users.py               - 用户管理工具
echo   2. test_auth.py                  - 鉴权功能测试
echo.
echo ⚙️ 配置文件：
echo.
echo   1. config\auth.json              - 鉴权配置
echo.
echo 💡 快速命令：
echo.
echo   启动应用:     uv run python app.py
echo   管理用户:     uv run python manage_users.py
echo   测试功能:     uv run python test_auth.py
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
goto menu

:end
cls
echo ═══════════════════════════════════════════════════════════════
echo                    感谢使用！
echo ═══════════════════════════════════════════════════════════════
echo.
echo 如有问题，请查看文档：
echo   - AUTHENTICATION_GUIDE.md
echo   - QUICKSTART_AUTH.md
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
exit


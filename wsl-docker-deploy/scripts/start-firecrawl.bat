@echo off
REM Firecrawl 一键启动脚本
REM 用法: 双击此文件或在终端运行
echo ================================
echo Firecrawl Self-Hosted 启动脚本
echo ================================
echo.
echo [1/3] 确保 Docker Desktop 已运行...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker 未运行，正在启动 Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo 等待 Docker 就绪（约 60 秒）...
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker ps >nul 2>&1
    if %errorlevel% neq 0 goto wait_docker
    echo Docker 就绪!
) else (
    echo Docker 已运行.
)

echo.
echo [2/3] 启动 Firecrawl 容器...
cd /d C:\Users\Aorus\tmp\firecrawl-selfhost
docker compose -f docker-compose.windows.yaml up -d
if %errorlevel% neq 0 (
    echo 启动失败! 请检查 Docker 日志.
    pause
    exit /b 1
)

echo.
echo [3/3] 等待 Firecrawl API 就绪...
:wait_api
timeout /t 3 /nobreak >nul
curl -s http://localhost:3002/health >nul 2>&1
if %errorlevel% neq 0 goto wait_api

echo.
echo ================================
echo Firecrawl 启动完成!
echo API: http://localhost:3002
echo 健康检查: curl http://localhost:3002/health
echo ================================
pause

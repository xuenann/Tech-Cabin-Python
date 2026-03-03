@echo off
setlocal enabledelayedexpansion

title Python Environment Switcher

:: ===============================
:: 1. 设置虚拟环境根目录,
::    需要将下面目录替换为您本地python环境的绝对路径
:: ===============================
set "VENV_ROOT=D:\APP_root\python_envs"

if not exist "%VENV_ROOT%" (
    echo 错误：目录不存在 %VENV_ROOT%
    pause
    exit /b
)

echo ======================================================
echo         Python Virtual Environment Switcher
echo ======================================================
echo.

:: ===============================
:: 2. 扫描所有虚拟环境
:: ===============================
set index=0

for /d %%D in ("%VENV_ROOT%\*") do (
    if exist "%%D\Scripts\python.exe" (
        set /a index+=1
        set "env!index!=%%D"
        
        for /f "delims=" %%V in ('"%%D\Scripts\python.exe" --version') do (
            set "ver!index!=%%V"
        )
    )
)

if %index%==0 (
    echo 未发现任何虚拟环境
    pause
    exit /b
)

:: ===============================
:: 3. 显示菜单
:: ===============================
echo 请选择要激活的 Python 环境：
echo.

for /l %%i in (1,1,%index%) do (
    for %%P in ("!env%%i!") do (
        echo %%i. %%~nxP  -  !ver%%i!
    )
)

echo 0. 退出
echo.

set /p choice=输入选项数字: 

if "%choice%"=="0" exit /b

if not defined env%choice% (
    echo 错误：无效选项
    pause
    exit /b
)

set "SELECTED=!env%choice%!"

echo.
echo 正在激活: !SELECTED!
echo.

:: ===============================
:: 4. 激活环境
:: ===============================
call "!SELECTED!\Scripts\activate.bat"

echo.
echo 当前环境已激活
echo 输入 deactivate 退出虚拟环境
:: 显示当前 Python 版本
python --version
echo ======================================================


cmd
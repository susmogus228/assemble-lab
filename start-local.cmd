@echo off
setlocal
cd /d "%~dp0"
where conda >nul 2>nul
if errorlevel 1 (
  echo Conda was not found. Install Miniforge and create the environment using environment.yml.
  exit /b 1
)
call conda run --no-capture-output -n assemblelab python server.py

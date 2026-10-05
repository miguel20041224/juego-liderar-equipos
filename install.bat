@echo off
setlocal
cd /d "%~dp0"

set "NORUN=0"
if /i "%~1"=="--no-run" set "NORUN=1"

set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo ERROR: se necesita Python 3.10 o superior y no se encontro.
  echo Instalalo con: winget install Python.Python.3.12
  echo o desde https://www.python.org/downloads/ ^(marca "Add python.exe to PATH"^).
  exit /b 1
)
echo ^>^> Usando %PY%

if not exist ".venv\Scripts\python.exe" (
  echo ^>^> Creando entorno virtual .venv
  %PY% -m venv .venv
  if errorlevel 1 (
    echo ERROR: no se pudo crear el entorno virtual.
    exit /b 1
  )
)

echo ^>^> Instalando dependencias
".venv\Scripts\python.exe" -m pip install --quiet -U pip
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install --quiet -e .
if errorlevel 1 exit /b 1

> jugar.bat (
  echo @echo off
  echo cd /d "%%~dp0"
  echo ".venv\Scripts\python.exe" -m liderar %%*
)

echo ^>^> Instalacion completa. Para jugar en el futuro: jugar.bat
if "%NORUN%"=="0" call jugar.bat
endlocal

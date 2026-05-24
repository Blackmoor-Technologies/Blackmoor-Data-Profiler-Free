@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "PYTHON_CMD=python"
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"

echo.
echo ========================================
echo Blackmoor Data Profiler setup
echo ========================================
echo.

pushd "%REPO_ROOT%" >nul

if not exist "%PYTHON_EXE%" (
    echo Creating .venv with Python virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create .venv.
        echo Ensure Python is installed and available on PATH.
        popd >nul
        exit /b 1
    )
) else (
    echo Reusing existing .venv.
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: .venv Python not found after setup.
    echo Expected: .venv\Scripts\python.exe
    popd >nul
    exit /b 1
)

echo.
echo Using local virtual environment:
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo ERROR: Unable to run .venv Python.
    popd >nul
    exit /b 1
)

echo.
echo Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip.
    popd >nul
    exit /b 1
)

echo.
echo Installing dependencies from requirements.txt...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    popd >nul
    exit /b 1
)

popd >nul

echo.
echo Setup complete.
echo Next steps:
echo   scripts\validate.bat
echo   scripts\run_app.bat
exit /b 0
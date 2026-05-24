@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"

echo.
echo ========================================
echo Blackmoor Data Profiler validation
echo ========================================
echo.

if not exist "%PYTHON_EXE%" (
    echo ERROR: .venv Python not found.
    echo Expected: .venv\Scripts\python.exe
    echo Create it with:
    echo python -m venv .venv
    exit /b 1
)

pushd "%REPO_ROOT%" >nul

echo Using local virtual environment:
"%PYTHON_EXE%" --version
if errorlevel 1 (
    popd >nul
    exit /b 1
)

echo.
echo Running py_compile...
"%PYTHON_EXE%" -m py_compile app.py profiler\file_loader.py profiler\schema_profile.py profiler\quality_checks.py profiler\report_builder.py profiler\data_dictionary.py scripts\generate_sample_reports.py
if errorlevel 1 (
    popd >nul
    exit /b 1
)

echo.
echo Running pytest...
"%PYTHON_EXE%" -m pytest tests\test_file_loader.py tests\test_schema_profile.py tests\test_quality_checks.py tests\test_report_builder.py tests\test_data_dictionary.py
if errorlevel 1 (
    popd >nul
    exit /b 1
)

popd >nul

echo.
echo Validation passed.
exit /b 0
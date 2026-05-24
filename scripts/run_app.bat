@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "STREAMLIT_EXE=%REPO_ROOT%\.venv\Scripts\streamlit.exe"

if not exist "%STREAMLIT_EXE%" (
    echo ERROR: Streamlit not found in .venv.
    echo Run:
    echo .venv\Scripts\python.exe -m pip install -r requirements.txt
    exit /b 1
)

pushd "%REPO_ROOT%" >nul
"%STREAMLIT_EXE%" run app.py
set "EXIT_CODE=%ERRORLEVEL%"
popd >nul
exit /b %EXIT_CODE%
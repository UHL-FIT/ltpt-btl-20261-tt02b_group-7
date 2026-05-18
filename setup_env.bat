@echo off
echo ========================================================
echo KHOI TAO MOI TRUONG PYTHON (VIRTUAL ENVIRONMENT)
echo ========================================================

IF NOT EXIST ".venv" (
    echo [1/3] Dang tao moi truong ao .venv...
    python -m venv .venv
) ELSE (
    echo [1/3] Moi truong .venv da ton tai.
)

echo [2/3] Dang kich hoat moi truong...
call .venv\Scripts\activate.bat

echo [3/3] Dang cai dat cac thu vien (requirements.txt)...
pip install -r requirements.txt

echo.
echo ========================================================
echo HOAN TAT!
echo De chay ung dung, hay go lenh: 
echo   .venv\Scripts\activate
echo   python main.py
echo ========================================================
pause

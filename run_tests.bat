@echo off
title Chay Kiem Thu (Unit Tests)
echo ========================================================
echo DANG CHAY KIEM THU TU DONG (UNIT TESTS)
echo ========================================================

:: Kiem tra moi truong ao
if not exist ".venv\Scripts\activate.bat" (
    echo [LOI] Khong tim thay moi truong ao .venv!
    echo Vui long chay setup_env.bat truoc.
    pause
    exit /b 1
)

:: Kich hoat moi truong ao va chay test
call .venv\Scripts\activate.bat
python -m unittest discover -s tests -p "test_*.py" -v

echo ========================================================
pause

@echo off
chcp 65001 >/dev/null
echo ============================================
echo   Amazon Listing 拆解工具
echo ============================================
echo.
echo Starting Backend (API: http://localhost:8000)...
start "Listing-Backend" cmd /c "cd /d D:\亚马逊Listing拆解工具\backend && pip install -r requirements.txt -q && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo.
echo Starting Frontend (Web: http://localhost:5173)...
start "Listing-Frontend" cmd /c "cd /d D:\亚马逊Listing拆解工具\frontend && npm install --silent && npx vite --host 0.0.0.0"
echo.
echo 浏览器打开 http://localhost:5173 即可使用
pause

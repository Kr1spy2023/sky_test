@echo off
echo ====================================
echo   Sky Test - Запуск платформы
echo ====================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден! Установите Python 3.8 или выше.
    pause
    exit /b 1
)

echo [1/3] Установка зависимостей...
pip install -r requirements.txt >nul 2>&1

echo [2/3] Запуск backend сервера...
cd backend
start cmd /k "python app.py"

echo [3/3] Запуск frontend сервера...
cd ..\frontend
start cmd /k "python -m http.server 8080"

echo.
echo ====================================
echo   Сервисы запущены!
echo ====================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8080
echo Swagger:  http://localhost:8000/swagger
echo.
echo Откройте браузер и перейдите на:
echo http://localhost:8080
echo.
echo Для остановки закройте окна терминалов.
echo.
pause

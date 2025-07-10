@echo off
echo 🤖 StudiaOnline Bot - MONITOREO AUTOMÁTICO
echo ============================================
echo.
echo 🔄 Iniciando monitoreo cada 30 minutos...
echo 🚨 Solo recibirás email cuando haya NUEVAS plazas
echo ⏹️  Presiona Ctrl+C para detener
echo.
:loop
python studia_bot_definitivo.py
echo.
echo ⏳ Esperando 30 minutos para la próxima ejecución...
timeout /t 1800 /nobreak >nul
goto loop
pause

@echo off
echo 🚀 Configuración para GitHub Actions
echo ==================================
echo.
echo ⭐ GitHub Actions - 100% GRATIS PARA SIEMPRE
echo    - Ejecuta cada 10 minutos automáticamente
echo    - Sin límites reales para repos públicos  
echo    - Ya configurado en .github/workflows/monitor.yml
echo    - Logs detallados en tiempo real
echo.
pause
echo.

echo 📋 Verificando archivos necesarios...
if not exist "requirements.txt" (
    echo ❌ Falta requirements.txt
    pause
    exit
)

if not exist "studia_bot_definitivo.py" (
    echo ❌ Falta studia_bot_definitivo.py
    pause
    exit
)

if not exist ".github\workflows\monitor.yml" (
    echo ❌ Falta .github/workflows/monitor.yml
    echo ⚠️  El workflow de GitHub Actions no está configurado
    pause
)

echo ✅ Archivos necesarios encontrados
echo.

echo 🔧 Inicializando Git...
git init
echo ✅ Git inicializado
echo.

echo 📦 Añadiendo archivos...
git add .
echo ✅ Archivos añadidos
echo.

echo 📝 Creando commit...
git commit -m "Bot StudiaOnline - Configurado para GitHub Actions"
echo ✅ Commit creado
echo.

echo 🌐 Configuración de repositorio remoto
echo Introduce la URL de tu repositorio GitHub:
echo Ejemplo: https://github.com/tuusuario/bot-studia-online.git
set /p repo_url="URL del repositorio: "

echo.
echo 🔗 Añadiendo repositorio remoto...
git branch -M main
git remote add origin %repo_url%
echo ✅ Repositorio remoto configurado
echo.

echo 🚀 Subiendo código a GitHub...
git push -u origin main
echo.

if %errorlevel% equ 0 (
    echo ✅ ¡ÉXITO! Código subido a GitHub
    echo.
    echo 🎯 CONFIGURACIÓN GITHUB ACTIONS:
    echo.
    echo 1. Hacer repositorio PÚBLICO (para uso ilimitado gratis):
    echo    Settings ^> General ^> Change visibility ^> Public
    echo.
    echo 2. Configurar GitHub Secrets:
    echo    Settings ^> Secrets and variables ^> Actions ^> New repository secret
    echo    Añadir estos 5 secrets:
    echo    - STUDIA_USERNAME (tu usuario StudiaOnline)
    echo    - STUDIA_PASSWORD (tu contraseña StudiaOnline) 
    echo    - EMAIL_FROM (tu Gmail)
    echo    - EMAIL_PASSWORD (app password de Gmail)
    echo    - EMAIL_TO (destinatarios separados por comas)
    echo.
    echo 3. Activar workflow:
    echo    Actions ^> "StudiaOnline Bot Monitor" ^> Enable workflow
    echo.
    echo 4. ¡LISTO! Se ejecuta cada 10 minutos automáticamente
    echo    - Logs visibles en Actions tab
    echo    - Solo envía email cuando hay cambios
    echo    - 100%% GRATIS para siempre
    echo.
    echo 📖 Guía completa en README.md
) else (
    echo ❌ Error subiendo a GitHub
    echo Verifica la URL del repositorio y tus credenciales
)

echo.
pause

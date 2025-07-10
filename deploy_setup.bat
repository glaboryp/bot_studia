@echo off
echo 🚀 Preparación para Railway Deployment
echo =====================================
echo.
echo Este script te ayudará a subir el bot a GitHub
echo Necesitarás haber creado un repositorio en GitHub primero
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

if not exist "Procfile" (
    echo ❌ Falta Procfile
    pause
    exit
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
git commit -m "Bot StudiaOnline con monitoreo automatico - listo para Railway"
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
    echo 📋 PRÓXIMOS PASOS:
    echo 1. Ir a https://railway.app
    echo 2. Login with GitHub
    echo 3. New Project → Deploy from GitHub repo
    echo 4. Seleccionar tu repositorio
    echo 5. Configurar variables de entorno
    echo.
    echo 📖 Ver GUIA_DEPLOY.md para instrucciones detalladas
) else (
    echo ❌ Error subiendo a GitHub
    echo Verifica la URL del repositorio y tus credenciales
)

echo.
pause

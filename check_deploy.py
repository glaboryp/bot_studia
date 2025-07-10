#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

def check_deployment_readiness():
    """Verificar que el proyecto está listo para deployment en Railway"""
    
    print("🔍 VERIFICANDO PREPARACIÓN PARA RAILWAY")
    print("=" * 50)
    
    required_files = [
        "studia_bot_definitivo.py",
        "requirements.txt", 
        "Procfile",
        "railway.json",
        ".gitignore"
    ]
    
    required_env_vars = [
        "STUDIA_USERNAME",
        "STUDIA_PASSWORD",
        "EMAIL_FROM",
        "EMAIL_PASSWORD", 
        "EMAIL_TO"
    ]
    
    # Verificar archivos
    print("\n📁 ARCHIVOS REQUERIDOS:")
    all_files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - FALTA")
            all_files_ok = False
    
    # Verificar .env (local)
    print("\n🔐 CONFIGURACIÓN LOCAL (.env):")
    if os.path.exists(".env"):
        print("   ✅ .env encontrado")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        env_ok = True
        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var}: {'*' * len(value)}")
            else:
                print(f"   ❌ {var}: NO CONFIGURADO")
                env_ok = False
    else:
        print("   ❌ .env no encontrado")
        env_ok = False
    
    # Verificar que .env está en .gitignore
    print("\n🚫 VERIFICAR .gitignore:")
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()
            if ".env" in gitignore_content:
                print("   ✅ .env está en .gitignore")
            else:
                print("   ⚠️  .env NO está en .gitignore - AÑÁDELO")
        
        if "cursos_anteriores.json" in gitignore_content:
            print("   ✅ cursos_anteriores.json está en .gitignore")
        else:
            print("   ⚠️  cursos_anteriores.json NO está en .gitignore")
    
    # Verificar que el bot funciona
    print("\n🤖 VERIFICAR BOT:")
    try:
        # Importar sin ejecutar
        sys.path.insert(0, '.')
        spec = __import__('studia_bot_definitivo')
        print("   ✅ studia_bot_definitivo.py se puede importar")
    except Exception as e:
        print(f"   ❌ Error importando bot: {e}")
        all_files_ok = False
    
    # Resumen
    print("\n" + "=" * 50)
    if all_files_ok and env_ok:
        print("🎉 ¡LISTO PARA RAILWAY!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Subir código a GitHub (usa deploy_setup.bat)")
        print("2. Ir a railway.app")
        print("3. Deploy from GitHub repo")
        print("4. Configurar variables de entorno EN RAILWAY")
        print("5. Ver logs para verificar funcionamiento")
        print("\n📖 Lee GUIA_DEPLOY.md para instrucciones detalladas")
        return True
    else:
        print("❌ HAY PROBLEMAS QUE RESOLVER")
        print("\n🔧 SOLUCIONES:")
        if not all_files_ok:
            print("   - Ejecutar desde la carpeta correcta del bot")
            print("   - Verificar que todos los archivos estén presentes")
        if not env_ok:
            print("   - Configurar .env con todas las variables")
            print("   - Verificar credenciales de StudiaOnline y Gmail")
        return False

if __name__ == "__main__":
    check_deployment_readiness()

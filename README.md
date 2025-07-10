# Bot StudiaOnline - Monitor de Cursos 🎓

Un bot automatizado que monitorea continuamente los cursos de StudiaOnline, filtra los que tienen plazas disponibles y envía notificaciones por email solo cuando detecta cambios (cursos nuevos o más plazas disponibles).

## 🚀 Características

- **Monitoreo 24/7**: Se ejecuta cada 30 minutos automáticamente
- **Filtrado inteligente**: Solo cursos de julio y agosto con plazas disponibles
- **Notificaciones inteligentes**: Email solo cuando hay cambios reales
- **Fácil despliegue**: Listo para Railway, Heroku u otras plataformas
- **Persistencia**: Guarda estado para evitar notificaciones duplicadas
- **Robusto**: Manejo de errores y logging completo

## 📋 Requisitos

- Python 3.9+
- Cuenta de StudiaOnline
- Cuenta de Gmail (para notificaciones)
- (Opcional) Cuenta de Railway para despliegue en la nube

## ⚙️ Configuración Local

### 1. Clonar el repositorio
```bash
git clone <tu-repo>
cd bot_studia
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia `.env.example` a `.env` y completa los valores:

```bash
# Credenciales StudiaOnline
STUDIA_USERNAME=tu_usuario
STUDIA_PASSWORD=tu_contraseña

# Configuración de email
EMAIL_FROM=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
EMAIL_TO=destinatario@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# URL de StudiaOnline
STUDIA_URL=https://studiaonline.org/
```

### 4. Configurar Gmail
Para usar Gmail, necesitas una "contraseña de aplicación":
1. Ve a tu cuenta de Google → Seguridad
2. Activa la verificación en 2 pasos
3. Genera una contraseña de aplicación
4. Usa esa contraseña en `EMAIL_PASSWORD`

## 🏃‍♂️ Uso

### Ejecutar una vez
```bash
python studia_bot_definitivo.py
```

### Monitoreo continuo (local)
```bash
python -c "
import subprocess
import time
while True:
    subprocess.run(['python', 'studia_bot_definitivo.py'])
    time.sleep(1800)  # 30 minutos
"
```

O usa el script de ayuda:
```bash
# Windows
run_monitor.bat

# Linux/Mac
while true; do python studia_bot_definitivo.py; sleep 1800; done
```

## ☁️ Despliegue en Railway

### Preparación automática
Ejecuta el script de configuración:
```bash
# Windows
deploy_setup.bat

# Manual
git add .
git commit -m "Configuración inicial"
git push origin main
```

### Pasos en Railway
1. **Crear proyecto**: Ve a [railway.app](https://railway.app) y conecta tu GitHub
2. **Seleccionar repo**: Elige tu repositorio del bot
3. **Configurar variables**: Ve a Variables y añade todas las del archivo `.env`
4. **Desplegar**: Railway detectará automáticamente el `Procfile` y desplegará

### Variables de entorno en Railway
Copia todas las variables de tu `.env` local:
- `STUDIA_USERNAME`
- `STUDIA_PASSWORD` 
- `EMAIL_FROM`
- `EMAIL_PASSWORD`
- `EMAIL_TO`
- `SMTP_SERVER`
- `SMTP_PORT`
- `STUDIA_URL`

## 📊 Cómo Funciona

1. **Login**: Se conecta a StudiaOnline con tus credenciales
2. **Navegación**: Va a la sección de cursos
3. **Filtrado**: Busca cursos de julio y agosto con plazas disponibles
4. **Comparación**: Compara con el estado anterior guardado en `cursos_anteriores.json`
5. **Notificación**: Si hay cambios, envía email con los cursos nuevos/actualizados
6. **Persistencia**: Guarda el nuevo estado para la próxima ejecución

### Filtros Aplicados
- ✅ Solo meses: julio, agosto
- ✅ Solo cursos con plazas disponibles
- ❌ Excluye cursos que contienen "Semestre"
- ❌ Excluye cursos sin lugar especificado

## 📁 Estructura del Proyecto

```
bot_studia/
├── studia_bot_definitivo.py    # 🤖 Bot principal
├── monitor.py                  # 🔄 Monitor para Railway
├── requirements.txt            # 📦 Dependencias
├── .env.example               # ⚙️ Plantilla de configuración
├── README.md                  # 📖 Documentación completa
├── Procfile                   # ☁️ Para Railway/Heroku
├── railway.json               # 🚂 Configuración Railway
├── runtime.txt                # 🐍 Versión de Python
├── .gitignore                 # 🙈 Archivos a ignorar
├── deploy_setup.bat           # 🚀 Script de despliegue
├── run_monitor.bat            # 🖥️ Script de monitoreo local
├── check_deploy.py            # ✅ Verificación de despliegue
└── cursos_anteriores.json     # 💾 Estado persistente (generado automáticamente)
```

## 🔧 Troubleshooting

### Error de login
- Verifica usuario y contraseña en `.env`
- Revisa que la cuenta no esté bloqueada

### Error de email
- Verifica que usas contraseña de aplicación de Gmail
- Confirma que la verificación en 2 pasos está activa

### Error en Railway
- Verifica que todas las variables de entorno están configuradas
- Revisa los logs en el dashboard de Railway

### El bot no encuentra cursos
- Es normal si no hay cursos disponibles en julio/agosto
- Revisa los logs para ver qué cursos están siendo filtrados

## 📝 Logs

El bot genera logs detallados en:
- Local: `bot_studia_definitivo.log`
- Railway: Visible en el dashboard

Los logs incluyen:
- Cursos encontrados y filtrados
- Razones de filtrado
- Estados de email
- Errores y warnings

## 🔄 Actualizaciones

Para actualizar el bot en Railway:
```bash
git add .
git commit -m "Actualización"
git push origin main
```

Railway desplegará automáticamente los cambios.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## ⚠️ Disclaimer

Este bot es para uso educativo y personal. Respeta los términos de servicio de StudiaOnline y usa el bot de manera responsable.

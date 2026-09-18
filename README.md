# Bot StudiaOnline - Monitor de Cursos 🎓

Un bot automatizado que monitorea continuamente los cursos de StudiaOnline, filtra los que tienen plazas disponibles y envía notificaciones por email solo cuando detecta cambios (cursos nuevos o más plazas disponibles).

## 🚀 Características

- **Monitoreo 24/7**: Se ejecuta cada 10 minutos automáticamente con GitHub Actions
- **Filtrado inteligente**: Solo cursos de julio y agosto con plazas disponibles
- **Notificaciones inteligentes**: Email solo cuando hay cambios reales
- **Despliegue gratuito**: GitHub Actions
- **Persistencia**: Guarda estado para evitar notificaciones duplicadas
- **Robusto**: Manejo de errores y logging completo

## 📋 Requisitos

- Python 3.9+
- Cuenta de StudiaOnline
- Cuenta de Gmail (para notificaciones)
- Cuenta de GitHub (para despliegue automático gratis)

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
# URL base de StudiaOnline (opcional, por defecto https://studiaonline.org/)
# STUDIA_BASE_URL=https://studiaonline.org/

# Credenciales StudiaOnline
STUDIA_USERNAME=tu_usuario
STUDIA_PASSWORD=tu_contraseña

# Configuración de email
EMAIL_FROM=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
EMAIL_TO=destinatario@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 4. Configurar Gmail
Para usar Gmail, necesitas una "contraseña de aplicación":
1. Ve a tu cuenta de Google → Seguridad
2. Activa la verificación en 2 pasos
3. Genera una contraseña de aplicación
4. Usa esa contraseña en `EMAIL_PASSWORD`

### 5. Múltiples destinatarios (opcional)
Para enviar notificaciones a varias personas, separa los emails con comas:
```bash
EMAIL_TO=email1@gmail.com,email2@yahoo.com,email3@hotmail.com
```
El bot enviará la misma notificación a todos los destinatarios.

## 🏃‍♂️ Uso

### Opciones de ejecución
El bot tiene 3 modos de funcionamiento:

#### 1. Verificación única (para probar)
```bash
python studia_bot_definitivo.py --once
```
Ejecuta una sola verificación y termina. Ideal para:
- Probar que todo funciona correctamente
- Ver qué cursos hay disponibles actualmente
- Verificar la configuración

#### 2. Monitoreo automático (recomendado)
```bash
python studia_bot_definitivo.py --monitor
```
Inicia el monitoreo automático cada 10 minutos. El bot:
- Se ejecuta inmediatamente al iniciarlo
- Luego se repite automáticamente cada 10 minutos
- Solo envía email cuando detecta cambios (cursos nuevos o más plazas)
- Sigue ejecutándose hasta que lo detengas con `Ctrl+C`

#### 3. Ejecución por defecto (sin parámetros)
```bash
python studia_bot_definitivo.py
```
Sin parámetros, inicia automáticamente el modo monitoreo.

### Consejos para uso local
- **Primera vez**: Usa `--once` para verificar que todo funciona
- **Uso diario**: Usa `--monitor` o `run_monitor.bat` para monitoreo continuo
- **Para detener**: Presiona `Ctrl+C` en el terminal
- **Ver logs**: Revisa el archivo `bot_studia_definitivo.log` que se genera automáticamente

### Ejemplo de uso paso a paso

```bash
# 1. Primera ejecución - verificar configuración
python studia_bot_definitivo.py --once

# Si todo funciona correctamente, verás algo como:
# ✅ Login realizado exitosamente
# ✅ CURSOS ACTUALES (17): ...
# ✅ Verificación completada

# 2. Iniciar monitoreo automático
python studia_bot_definitivo.py --monitor

# El bot mostrará:
# 🔄 === INICIANDO MONITOREO AUTOMÁTICO ===
# ⏰ Verificación cada 10 minutos
# 🚨 Email solo cuando hay NUEVAS plazas
# 
# Y se ejecutará automáticamente cada 10 minutos
# Solo recibirás email cuando haya cambios reales
```

## 🧪 Tests

El proyecto incluye tests unitarios para la lógica de filtrado de cursos (mes, año, lugar, excepción Tafira, plazas disponibles):

```bash
python3 -m unittest discover -s tests
```

## 🚀 Despliegue GRATUITO con GitHub Actions

### 📦 Configuración paso a paso

1. **Hacer repositorio público** (para uso ilimitado gratis):
   En GitHub: Repository → Settings → General → Change visibility → Public

2. **Configurar GitHub Secrets**:
   - Ve a tu repositorio → Settings → Secrets and variables → Actions → "New repository secret"
   - Añade estos secrets uno por uno:
     - `STUDIA_USERNAME` → tu usuario de StudiaOnline
     - `STUDIA_PASSWORD` → tu contraseña de StudiaOnline  
     - `EMAIL_FROM` → tu email de Gmail
     - `EMAIL_PASSWORD` → tu app password de Gmail
     - `EMAIL_TO` → emails destino (separados por comas si son varios)
   
   > ⚠️ **IMPORTANTE**: NO necesitas crear `GITHUB_TOKEN` - se proporciona automáticamente

3. **Activar el workflow**:
   - El archivo `.github/workflows/monitor.yml` ya está configurado
   - Ve a: Repository → Actions → "StudiaOnline Bot Monitor" → "Enable workflow"
   - O ejecuta manualmente: Actions → "Run workflow" → "Run workflow"

4. **¡Funciona automáticamente!**:
   - Se ejecuta cada 10 minutos, 24/7 GRATIS
   - Solo envía email cuando hay cambios reales
   - Logs detallados visibles en Actions → workflow runs
   - El bot actualiza automáticamente su estado entre ejecuciones


## 📁 Estructura del Proyecto

```
bot_studia/
├── 🤖 studia_bot_definitivo.py       # Bot principal
├── 📦 requirements.txt               # Dependencias Python
├── ⚙️ .env.example                   # Plantilla de configuración
├── 📚 README.md                      # Documentación principal
├── 🚀 .github/workflows/monitor.yml  # Configuración GitHub Actions
├── 🔧 deploy_setup.bat               # Script de despliegue Windows
├── 🗂️  .gitignore                    # Archivos a ignorar en Git
```


## 🔧 Troubleshooting

### ❌ Error de login en StudiaOnline
- Verifica `STUDIA_USERNAME` y `STUDIA_PASSWORD` 
- Confirma que puedes hacer login manual en la web
- Revisa que la cuenta no esté bloqueada

### ❌ Error de email/Gmail
- Verifica que usas **contraseña de aplicación** de Gmail (no tu contraseña normal)
- Confirma que la **verificación en 2 pasos** está activa en tu cuenta Google
- Verifica `EMAIL_FROM`, `EMAIL_PASSWORD` y `EMAIL_TO`

### ❌ Error en GitHub Actions
- Verifica que todos los **GitHub Secrets** están configurados correctamente
- Ve a Actions → workflow run → logs para ver error específico
- **Error "No module named 'bs4'"**: El archivo `requirements.txt` incluye todas las dependencias necesarias

### ❌ El bot no encuentra cursos
- **Es normal** si no hay cursos disponibles en julio/agosto con plazas
- Revisa los logs para ver qué cursos están siendo filtrados y por qué
- El bot filtra por: meses específicos, plazas disponibles, y excluye "Semestre"

### ❌ No recibo emails
- **Es normal** si no hay cambios en los cursos
- El bot **solo envía email cuando detecta cambios reales** (nuevos cursos o más plazas)
- Usa `python studia_bot_definitivo.py --once` localmente para verificar funcionamiento

### 💾 Archivo de estado (`cursos_anteriores.json`)
- **Propósito**: Almacena el estado anterior para detectar cambios
- **Ubicación**: Raíz del repositorio (incluido en el repo)
- **Actualización automática**: El bot hace commit automático tras cada verificación
- **Importante**: Si eliminas este archivo, la próxima ejecución detectará todos los cursos como "nuevos"

## 📝 Logs y Monitoreo

### GitHub Actions:
- **Logs en tiempo real**: Repository → Actions → workflow run → "monitor_courses"
- **Frecuencia**: Cada 10 minutos automáticamente  
- **Persistencia**: Logs disponibles por 90 días

### Ejecución local:
- **Archivo**: `bot_studia_definitivo.log` (generado automáticamente)
- **Consola**: Output en tiempo real al ejecutar

### Información en logs:
- ✅ Login exitoso y navegación
- 📊 Cursos encontrados y filtrados  
- 🔍 Razones específicas de filtrado
- 📧 Estado de envío de emails
- ❌ Errores y warnings detallados

## 🔄 Mantenimiento y Actualizaciones

El proyecto está diseñado para **ser estable y requerir mantenimiento mínimo**:

### 🔄 Actualizaciones automáticas:
- ✅ **GitHub Actions**: Se mantiene automáticamente actualizado
- ✅ **Python y dependencias**: GitHub usa la última versión estable
- ✅ **Logs de ejecución**: Disponibles 90 días automáticamente

### 🛠️ Mantenimiento ocasional:
- **Credenciales**: Si cambias contraseña de StudiaOnline o Gmail
- **Email destino**: Si quieres añadir/quitar destinatarios 
- **Filtros de cursos**: Si StudiaOnline cambia formato (muy raro)

### 🚀 Actualizar el bot:
```bash
git add .
git commit -m "Actualización"
git push origin main
```
GitHub Actions desplegará automáticamente los cambios.

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

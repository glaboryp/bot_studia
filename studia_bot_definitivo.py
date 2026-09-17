#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import re
from urllib.parse import urljoin
import json
import hashlib

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_studia_definitivo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class StudiaBotDefinitivo:
    def __init__(self):
        self.base_url = os.getenv('STUDIA_BASE_URL', 'https://studiaonline.org/')

        self.username = os.getenv('STUDIA_USERNAME')
        self.password = os.getenv('STUDIA_PASSWORD')
        
        # Email
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        email_to_raw = os.getenv('EMAIL_TO')
        # Soporte para múltiples destinatarios separados por comas
        if email_to_raw:
            self.email_to = [email.strip() for email in email_to_raw.split(',') if email.strip()]
        else:
            self.email_to = []
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Configuración específica
        self.target_months = ['julio', 'agosto']
        self.target_year = str(datetime.now().year)
        self.target_years = [str(int(self.target_year) - 1), self.target_year]
        
        # Session para cookies
        self.session = requests.Session()
        # Reintentar automáticamente ante fallos de red o errores 5xx puntuales
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=['GET', 'POST'],
        )
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('https://', retry_adapter)
        self.session.mount('http://', retry_adapter)
        # Configurar headers robustos para evitar bloqueos
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Archivo para guardar estado anterior
        self.state_file = 'cursos_anteriores.json'
    
    def login(self):
        """Realizar login en StudiaOnline"""
        try:
            logging.info("🔐 Iniciando proceso de login...")
            logging.info(f"🌐 URL base configurada: {self.base_url}")

            # Obtener página de login
            logging.info(f"📡 Conectando a: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar formulario de login
            login_forms = soup.find_all('form')
            login_form = None
            
            for form in login_forms:
                username_inputs = form.find_all('input', {'name': re.compile(r'login|user|usuario|email', re.I)})
                password_inputs = form.find_all('input', {'type': 'password'})
                
                if username_inputs and password_inputs:
                    login_form = form
                    break
            
            if not login_form:
                logging.error("❌ No se encontró formulario de login")
                return False
            
            # Extraer action del formulario
            form_action = login_form.get('action', '')
            if form_action.startswith('/'):
                login_url = self.base_url.rstrip('/') + form_action
            elif form_action.startswith('http'):
                login_url = form_action
            else:
                login_url = self.base_url.rstrip('/') + '/' + form_action.lstrip('/')
            
            # Preparar datos
            form_data = {}
            
            # Campos ocultos
            for hidden_input in login_form.find_all('input', {'type': 'hidden'}):
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            # Credenciales
            username_input = login_form.find('input', {'name': re.compile(r'login|user|usuario|email', re.I)})
            password_input = login_form.find('input', {'type': 'password'})
            
            if username_input:
                form_data[username_input.get('name')] = self.username
            if password_input:
                form_data[password_input.get('name')] = self.password
            
            logging.info(f"📤 Enviando credenciales a: {login_url}")
            
            # Realizar login
            login_response = self.session.post(login_url, data=form_data, allow_redirects=True, timeout=30)
            login_response.raise_for_status()

            # Verificar éxito del login: si la respuesta todavía contiene un campo de
            # contraseña, seguimos en la página de login (credenciales rechazadas)
            login_soup = BeautifulSoup(login_response.text, 'html.parser')
            if login_soup.find('input', {'type': 'password'}):
                logging.error("❌ Login fallido - seguimos en la página de login (credenciales incorrectas)")
                return False

            logging.info("✅ Login realizado exitosamente")
            return True
            
        except Exception:
            logging.exception("❌ Error durante login")
            return False
    
    def get_available_courses(self):
        """Obtener cursos con plazas disponibles de todas las páginas"""
        try:
            # Login
            if not self.login():
                return []

            # Acceder a la página de cursos principal para obtener la sesión
            courses_url = urljoin(self.base_url, '/studiapy3/venta_online/cursos')
            logging.info(f"🔍 Accediendo a página de cursos: {courses_url}")
            
            response = self.session.get(courses_url, timeout=30)

            if response.status_code != 200:
                logging.error(f"❌ Error accediendo a cursos: {response.status_code}")
                return []

            # Obtener el id_alumno de la página inicial
            id_alumno_match = re.search(r'id_alumno:\s*(\d+)', response.text)
            if not id_alumno_match:
                logging.error("❌ No se pudo extraer id_alumno de la página de cursos")
                return []
            id_alumno = int(id_alumno_match.group(1))
            
            all_courses = []
            page = 0
            
            logging.info("🌍 Filtros desactivados: buscando en TODOS los centros y regiones")
            logging.info("🚫 Excluyendo: cursos de 'Semestre' y lugares vacíos")
            
            # Explorar todas las páginas
            while True:
                logging.info(f"📄 Explorando página {page + 1}...")
                
                # URL para cargar cursos vía AJAX
                ajax_url = urljoin(self.base_url, '/studiapy3/venta_online/cursos/cursos_/')
                
                # Datos para el POST AJAX
                ajax_data = {
                    'rp': 10,  # results per page
                    'pag': page,
                    'id_ensenanza': 0,
                    'id_producto': 0,
                    'search': '',
                    # centro_alumno / region_alumno se omiten para replicar el comportamiento
                    # de un checkbox desmarcado en un <form> (no se envía el campo)
                    'fecha_filtro': '',
                    'id_alumno': id_alumno,
                    'order_by': 'fecha',
                    'puedo_cursar': '',
                }
                
                # Realizar petición AJAX
                ajax_response = self.session.post(ajax_url, data=ajax_data, timeout=30)

                if ajax_response.status_code != 200:
                    logging.error(f"❌ Error en AJAX página {page}: {ajax_response.status_code}")
                    break
                
                try:
                    ajax_json = ajax_response.json()
                    
                    if not ajax_json.get('status', False):
                        logging.warning(f"⚠️ AJAX sin status en página {page}")
                        break
                    
                    page_courses = ajax_json.get('cursos', [])
                    total_cursos = ajax_json.get('total_cursos', 0)
                    
                    if not page_courses:
                        logging.info(f"📄 Página {page + 1} sin cursos, fin de paginación")
                        break
                    
                    logging.info(f"📄 Página {page + 1}: {len(page_courses)} cursos, total disponible: {total_cursos}")
                    
                    # Procesar cursos de esta página
                    page_available_courses = self.extract_courses_from_json(page_courses)
                    all_courses.extend(page_available_courses)
                    
                    # Si esta página tiene menos de 10 cursos, es la última
                    if len(page_courses) < 10:
                        logging.info(f"📄 Última página detectada (solo {len(page_courses)} cursos)")
                        break
                    
                    page += 1
                    
                    # Seguridad: máximo 10 páginas
                    if page >= 10:
                        logging.warning("⚠️ Límite de 10 páginas alcanzado")
                        break
                        
                except Exception:
                    logging.exception(f"❌ Error procesando AJAX página {page}")
                    break
            
            # Eliminar duplicados finales
            unique_courses = []
            seen_titles = set()
            
            for course in all_courses:
                title_key = re.sub(r'[^a-zA-Z0-9]', '', course['title'].lower())
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_courses.append(course)
            
            logging.info(f"📊 Total páginas exploradas: {page + 1}")
            logging.info(f"📊 Total cursos únicos con plazas: {len(unique_courses)}")
            
            return unique_courses
            
        except Exception:
            logging.exception("❌ Error obteniendo cursos")
            return []
    
    def extract_courses_from_json(self, cursos_data):
        """Extraer cursos con plazas disponibles de datos JSON"""
        courses = []
        
        try:
            for curso in cursos_data:
                try:
                    nombre = curso.get('nombre', '')
                    grupo_seleccionado = curso.get('grupo_seleccionado', {})
                    
                    if not grupo_seleccionado:
                        continue
                        
                    capacidad = grupo_seleccionado.get('capacidad', 0)
                    ocupacion = grupo_seleccionado.get('ocupacion', 0)
                    
                    # Verificar que grupos.lugar no esté vacío
                    grupos = curso.get('grupos', [])
                    has_valid_lugar = False
                    if grupos:
                        for grupo in grupos:
                            lugar = (grupo.get('lugar') or '').strip()
                            if lugar:  # Si hay al menos un lugar no vacío
                                has_valid_lugar = True
                                break
                    
                    # Excepción especial: permitir "Residencia Tafira Atlantic Club" aunque el lugar esté vacío
                    is_tafira_exception = 'residencia tafira atlantic club' in nombre.lower()
                    if is_tafira_exception and not has_valid_lugar:
                        logging.info(f"ℹ️ Excepción Tafira aplicada (lugar vacío) para: {nombre}")
                    
                    # Verificar que es de julio o agosto 2026, NO es un semestre y tiene lugar válido
                    is_target_month = any(month in nombre.lower() for month in self.target_months)
                    is_target_year = any(year in nombre for year in self.target_years)
                    is_not_semestre = 'semestre' not in nombre.lower()
                    
                    if is_target_month and is_target_year and is_not_semestre and (has_valid_lugar or is_tafira_exception):
                        plazas_disponibles = capacidad - ocupacion
                        
                        # Limpiar nombre completamente
                        nombre_limpio = nombre.replace('Curso anual estudios n - ', '')
                        nombre_limpio = nombre_limpio.replace('Curso anual Repaso n - ', '')
                        nombre_limpio = nombre_limpio.split(' - mEf')[0]
                        nombre_limpio = nombre_limpio.split(' -dlmEf')[0]
                        nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio).strip()
                        
                        # Determinar mes
                        month = 'julio' if 'julio' in nombre.lower() else 'agosto'
                        
                        logging.info(f"🔍 Curso encontrado: {nombre_limpio}")
                        logging.info(f"   📊 {ocupacion}/{capacidad} → {plazas_disponibles} plazas libres")
                        
                        if plazas_disponibles > 0:
                            course_info = {
                                'title': nombre_limpio,
                                'month': month,
                                'capacidad': capacidad,
                                'ocupacion': ocupacion,
                                'plazas_disponibles': plazas_disponibles,
                                'available': True
                            }
                            
                            courses.append(course_info)
                            logging.info(f"✅ AGREGADO: {nombre_limpio} ({plazas_disponibles} plazas)")
                        else:
                            logging.info(f"❌ SIN PLAZAS: {nombre_limpio} (completo)")
                    else:
                        # Si no pasa los filtros, registrar por qué
                        if 'semestre' in nombre.lower():
                            logging.info(f"🚫 EXCLUIDO: {nombre} (curso de semestre)")
                        elif not has_valid_lugar:
                            logging.info(f"🚫 EXCLUIDO: {nombre} (lugar vacío)")
                        # No logear si es por mes/año incorrectos para evitar spam
                        
                except Exception:
                    logging.warning(f"⚠️ Curso omitido por error al procesarlo: {curso.get('nombre', '?')}", exc_info=True)
                    continue

            return courses

        except Exception:
            logging.exception("❌ Error extrayendo cursos de JSON")
            return []
    
    def save_courses_state(self, courses):
        """Guardar estado actual de cursos en archivo JSON"""
        try:
            # Crear un identificador único para cada curso basado en nombre y mes
            course_ids = {}
            for course in courses:
                course_id = f"{course['title']}_{course['month']}"
                course_ids[course_id] = {
                    'title': course['title'],
                    'month': course['month'],
                    'plazas_disponibles': course['plazas_disponibles'],
                    'timestamp': datetime.now().isoformat()
                }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(course_ids, f, ensure_ascii=False, indent=2)
            
            logging.info(f"💾 Estado guardado: {len(course_ids)} cursos")
            
        except Exception:
            logging.exception("❌ Error guardando estado")
    
    def commit_state_changes(self):
        """Hacer commit automático del archivo de estado actualizado"""
        try:
            import subprocess
            
            # Verificar si hay cambios en el archivo de estado
            result = subprocess.run(['git', 'status', '--porcelain', self.state_file], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.stdout.strip():
                logging.info("📝 Cambios detectados en archivo de estado, haciendo commit...")
                
                # Configurar git user si no está configurado (para GitHub Actions)
                subprocess.run(['git', 'config', '--global', 'user.email', 'action@github.com'], 
                             capture_output=True, cwd='.')
                subprocess.run(['git', 'config', '--global', 'user.name', 'GitHub Action'], 
                             capture_output=True, cwd='.')
                
                # Agregar el archivo
                subprocess.run(['git', 'add', self.state_file], 
                             capture_output=True, cwd='.')
                
                # Hacer commit
                commit_msg = f"🤖 Actualizar el estado anterior - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                subprocess.run(['git', 'commit', '-m', commit_msg], 
                             capture_output=True, cwd='.')
                
                # Push
                push_result = subprocess.run(['git', 'push'], 
                                           capture_output=True, text=True, cwd='.')
                
                if push_result.returncode == 0:
                    logging.info("✅ Estado actualizado y sincronizado con GitHub")
                else:
                    logging.warning(f"⚠️ Error haciendo push: {push_result.stderr}")
            else:
                logging.info("ℹ️ Sin cambios en archivo de estado")
                
        except Exception:
            logging.exception("❌ Error en commit automático")
            # No es crítico, el bot puede seguir funcionando
    
    def load_previous_state(self):
        """Cargar estado anterior de cursos desde archivo JSON"""
        try:
            if not os.path.exists(self.state_file):
                logging.info("📄 No hay estado anterior, primera ejecución")
                return {}
            
            with open(self.state_file, 'r', encoding='utf-8') as f:
                previous_state = json.load(f)
            
            logging.info(f"📂 Estado anterior cargado: {len(previous_state)} cursos")
            return previous_state
            
        except Exception:
            logging.exception("❌ Error cargando estado anterior")
            return {}
    
    def find_new_courses(self, current_courses, previous_state):
        """Encontrar cursos nuevos o con más plazas disponibles"""
        new_courses = []
        
        for course in current_courses:
            course_id = f"{course['title']}_{course['month']}"
            
            if course_id not in previous_state:
                # Curso completamente nuevo
                new_courses.append({
                    **course,
                    'status': 'nuevo'
                })
                logging.info(f"🆕 NUEVO: {course['title']} ({course['plazas_disponibles']} plazas)")
            else:
                # Verificar si tiene más plazas que antes
                previous_plazas = previous_state[course_id]['plazas_disponibles']
                current_plazas = course['plazas_disponibles']
                
                if current_plazas > previous_plazas:
                    # Más plazas disponibles
                    new_courses.append({
                        **course,
                        'status': 'mas_plazas',
                        'plazas_anteriores': previous_plazas
                    })
                    logging.info(f"📈 MÁS PLAZAS: {course['title']} ({previous_plazas} → {current_plazas})")
        
        return new_courses
    
    def send_clean_email(self, courses):
        """Enviar email con formato limpio y simple"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)  # Unir múltiples destinatarios con comas
            msg['Subject'] = f"StudiaOnline - Cursos Disponibles Julio/Agosto {self.target_year} ({datetime.now().strftime('%d/%m/%Y')})"

            if courses:
                body = "🎓 CURSOS CON PLAZAS DISPONIBLES\n"
                body += f"📅 JULIO Y AGOSTO {self.target_year}\n"
                body += "=" * 50 + "\n\n"
                
                # Separar por mes
                julio_courses = [c for c in courses if c['month'] == 'julio']
                agosto_courses = [c for c in courses if c['month'] == 'agosto']
                
                # Cursos de JULIO
                if julio_courses:
                    body += "📅 JULIO 2026\n"
                    body += "-" * 20 + "\n"
                    for i, course in enumerate(julio_courses, 1):
                        body += f"{i}. {course['title']}\n"
                    body += "\n"
                
                # Cursos de AGOSTO
                if agosto_courses:
                    body += "📅 AGOSTO 2026\n"
                    body += "-" * 20 + "\n"
                    for i, course in enumerate(agosto_courses, 1):
                        body += f"{i}. {course['title']}\n"
                    body += "\n"
                
                # Resumen simple
                body += f"Total: {len(courses)} cursos con plazas libres\n"
                body += f"({len(julio_courses)} en julio, {len(agosto_courses)} en agosto)\n\n"
                body += f"Búsqueda: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                body += f"🔗 {self.base_url}"

            else:
                body = "📋 REVISIÓN STUDIAONLINE\n"
                body += "=" * 30 + "\n\n"
                body += "❌ No hay cursos con plazas disponibles\n"
                body += f"   para julio y agosto {self.target_year}\n\n"
                body += f"Búsqueda: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                body += "📧 Te notificaré cuando haya plazas"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                # Enviar a todos los destinatarios
                for recipient in self.email_to:
                    server.sendmail(self.email_from, recipient, msg.as_string())
            
            logging.info(f"📧 Email enviado a {len(self.email_to)} destinatarios: {len(courses)} cursos con plazas")
            return True
            
        except Exception:
            logging.exception("❌ Error enviando email")
            return False
    
    def send_changes_email(self, new_courses):
        """Enviar email solo cuando hay cursos nuevos o cambios"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)  # Unir múltiples destinatarios con comas
            msg['Subject'] = f"🚨 StudiaOnline - NUEVAS PLAZAS DISPONIBLES! ({datetime.now().strftime('%d/%m %H:%M')})"
            
            body = "🚨 ¡ALERTA DE PLAZAS!\n"
            body += "=" * 30 + "\n\n"
            
            # Separar por tipo de cambio
            nuevos = [c for c in new_courses if c.get('status') == 'nuevo']
            mas_plazas = [c for c in new_courses if c.get('status') == 'mas_plazas']
            
            if nuevos:
                body += "🆕 CURSOS NUEVOS CON PLAZAS:\n"
                body += "-" * 30 + "\n"
                for course in nuevos:
                    body += f"📅 {course['month'].upper()}: {course['title']}\n"
                    body += f"   🎯 {course['plazas_disponibles']} plazas disponibles\n\n"
            
            if mas_plazas:
                body += "📈 CURSOS CON MÁS PLAZAS:\n"
                body += "-" * 30 + "\n"
                for course in mas_plazas:
                    body += f"📅 {course['month'].upper()}: {course['title']}\n"
                    body += f"   📈 {course['plazas_anteriores']} → {course['plazas_disponibles']} plazas\n\n"
            
            body += f"🕐 Verificado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            body += "🔄 Próxima verificación en 10 minutos\n\n"
            body += "💡 Bot monitoreando automáticamente cada 10 minutos"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                # Enviar a todos los destinatarios
                for recipient in self.email_to:
                    server.sendmail(self.email_from, recipient, msg.as_string())
            
            logging.info(f"🚨 Email de ALERTA enviado a {len(self.email_to)} destinatarios: {len(new_courses)} cambios detectados")
            return True
            
        except Exception:
            logging.exception("❌ Error enviando email de alerta")
            return False
    
    def run_search(self):
        """Ejecutar búsqueda de cursos con plazas disponibles"""
        logging.info("🚀 === BOT DEFINITIVO - MONITOREO AUTOMÁTICO ===")
        logging.info(f"👤 Usuario: {self.username}")
        logging.info(f"🎯 Objetivo: Detectar nuevas plazas disponibles")
        logging.info(f"📧 Notificación a: {', '.join(self.email_to)} ({len(self.email_to)} destinatarios)")
        
        try:
            # Cargar estado anterior
            previous_state = self.load_previous_state()
            
            # Obtener cursos actuales
            current_courses = self.get_available_courses()
            
            if current_courses:
                logging.info(f"✅ CURSOS ACTUALES ({len(current_courses)}):")
                for i, course in enumerate(current_courses, 1):
                    logging.info(f"   {i}. {course['title']}")
                    logging.info(f"      📅 {course['month'].title()} | 🎯 {course['plazas_disponibles']} plazas libres")
                
                # Buscar cambios
                new_courses = self.find_new_courses(current_courses, previous_state)
                
                if new_courses:
                    logging.info(f"🚨 CAMBIOS DETECTADOS: {len(new_courses)} modificaciones")
                    # Enviar email de alerta
                    if self.send_changes_email(new_courses):
                        logging.info("✅ Email de alerta enviado exitosamente")
                    else:
                        logging.error("❌ Error enviando email de alerta")
                else:
                    logging.info("ℹ️ Sin cambios desde la última verificación")
                
                # Guardar estado actual
                self.save_courses_state(current_courses)
                # Commit automático del estado actualizado
                self.commit_state_changes()
                
            else:
                logging.info("ℹ️ No hay cursos con plazas disponibles")
                # Guardar estado vacío
                self.save_courses_state([])
                # Commit automático del estado actualizado
                self.commit_state_changes()
            
            logging.info("✅ Verificación completada")
            return True
                
        except Exception:
            logging.exception("❌ Error en la verificación")
            return False
    
    def run_monitoring(self):
        """Ejecutar monitoreo continuo cada 10 minutos"""
        logging.info("🔄 === INICIANDO MONITOREO AUTOMÁTICO ===")
        logging.info("⏰ Verificación cada 10 minutos")
        logging.info("🚨 Email solo cuando hay NUEVAS plazas")
        logging.info("🏁 Presiona Ctrl+C para detener")
        print()
        
        # Primera verificación inmediata
        logging.info("🔍 Verificación inicial...")
        self.run_search()
        
        # Configurar verificaciones cada 10 minutos
        schedule.clear()
        schedule.every(10).minutes.do(self.run_search)
        
        try:
            while True:
                # Ejecutar verificaciones programadas
                schedule.run_pending()
                
                # Esperar 1 minuto antes de verificar de nuevo
                time.sleep(60)
                
        except KeyboardInterrupt:
            logging.info("⏹️ Monitoreo detenido por el usuario")
            print("\n⏹️ Monitoreo detenido. ¡Hasta luego!")
        except Exception as e:
            logging.exception("❌ Error en monitoreo")
            print(f"\n❌ Error en monitoreo: {e}")
            
        finally:
            logging.info("🏁 === FIN DEL MONITOREO ===")

def main():
    """Función principal"""
    print("🤖 Bot StudiaOnline - Versión MONITOREO")
    print("=" * 50)
    print("🚨 Solo envía email cuando HAY CAMBIOS")
    print("⏰ Verificación automática cada 10 minutos")
    print("🎯 Detecta NUEVAS plazas disponibles")
    print("=" * 50)
    
    bot = StudiaBotDefinitivo()
    
    # Verificar configuración
    required_fields = [
        (bot.username, "STUDIA_USERNAME"),
        (bot.password, "STUDIA_PASSWORD"),
        (bot.email_from, "EMAIL_FROM"),
        (bot.email_password, "EMAIL_PASSWORD"),
        (len(bot.email_to) > 0, "EMAIL_TO")  # Verificar que hay al menos un destinatario
    ]
    
    missing_fields = [field_name for field_value, field_name in required_fields if not field_value]
    
    if missing_fields:
        print("❌ Configuración incompleta. Faltan:")
        for field in missing_fields:
            print(f"   - {field}")
        return
    
    print(f"✅ Configuración válida")
    print(f"👤 Usuario: {bot.username}")
    print(f"📧 Notificaciones a: {', '.join(bot.email_to)} ({len(bot.email_to)} destinatarios)")
    print()
    
    # Ejecutar
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        print("🔍 Ejecutando verificación única...")
        success = bot.run_search()
        print("✅ Completado" if success else "❌ Error")
    elif len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        print("🔄 Iniciando monitoreo automático cada 10 minutos...")
        print("💡 Solo recibirás email cuando haya NUEVAS plazas")
        bot.run_monitoring()
    else:
        print("💡 Opciones disponibles:")
        print("   --once     : Verificación única")
        print("   --monitor  : Monitoreo cada 10 minutos")
        print()
        print("🔄 Iniciando monitoreo por defecto...")
        bot.run_monitoring()

if __name__ == "__main__":
    main()

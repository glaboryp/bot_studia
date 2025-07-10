#!/usr/bin/env python3
"""
Monitor script para Railway - Ejecuta el bot cada 30 minutos
"""
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_monitor():
    """Ejecuta el bot en un loop infinito cada 30 minutos"""
    logging.info("🚀 Iniciando monitor StudiaBot en Railway")
    logging.info("⏰ Intervalo: cada 30 minutos (optimizado para Railway)")
    
    while True:
        try:
            logging.info("🤖 Ejecutando bot...")
            result = subprocess.run(['python', 'studia_bot_definitivo.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logging.info("✅ Ejecución exitosa")
            else:
                logging.error(f"❌ Error en ejecución: {result.stderr}")
            
            logging.info("⏳ Esperando 30 minutos para próxima ejecución...")
            time.sleep(1800)  # 1800 segundos = 30 minutos
            
        except subprocess.TimeoutExpired:
            logging.error("⏰ Timeout: Ejecución del bot tomó más de 5 minutos")
        except Exception as e:
            logging.error(f"💥 Error inesperado: {e}")
            time.sleep(60)  # Esperar 1 minuto antes de reintentar

if __name__ == "__main__":
    run_monitor()

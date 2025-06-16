#!/home/bot_project/bot_env/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import requests
import telebot
from passwords import keys  # Módulo con credenciales
from datetime import datetime

# Configuración inicial
bot = telebot.TeleBot(keys.your_token)
MAX_MESSAGE_LENGTH = 4000  # Límite de Telegram

# --- Funciones utilitarias ---
def safe_send(chat_id, content):
    """Envía mensajes largos respetando el límite de Telegram"""
    if len(content) <= MAX_MESSAGE_LENGTH:
        bot.send_message(chat_id, content)
    else:
        parts = [content[i:i+MAX_MESSAGE_LENGTH] 
                for i in range(0, len(content), MAX_MESSAGE_LENGTH)]
        for part in parts:
            bot.send_message(chat_id, part)

def execute_command(cmd):
    """Ejecuta comandos de sistema de forma segura"""
    try:
        result = os.popen(cmd).read().strip()
        return result if result else "Sin resultados"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Funciones de comandos ---
def get_indicadores():
    """Obtiene indicadores económicos de Chile"""
    try:
        r = requests.get('https://mindicador.cl/api', timeout=10).json()
        return (
            f"IPC: {r['ipc']['valor']}\n"
            f"UF: {r['uf']['valor']:,}\n"
            f"UTM: {r['utm']['valor']:,}\n"
            f"Dólar: {r['dolar']['valor']}\n"
            f"Euro: {r['euro']['valor']}"
        )
    except Exception as e:
        return f"Error obteniendo indicadores: {str(e)}"

def get_ip_data():
    """Obtiene información de IP pública"""
    try:
        data = requests.get('http://ip-api.com/json', timeout=5).json()
        return (
            f"IP: {data['query']}\n"
            f"ISP: {data['isp']}\n"
            f"País: {data['country']}\n"
            f"Región: {data['regionName']}"
        )
    except Exception as e:
        return f"Error obteniendo datos IP: {str(e)}"

def get_sismos():
    """
    Obtiene los últimos 3 sismos desde la API de GAEL y los devuelve formateados
    """
    try:
        response = requests.get('https://api.gael.cloud/general/public/sismos', timeout=10)
        response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx
        
        sismos = response.json()
        primeros_3 = sismos[:3]  # Tomamos los primeros 3 sismos
        
        if not primeros_3:
            return "No se encontraron sismos recientes"
        
        resultados = []
        for sismo in primeros_3:
            # Formatear la fecha a un formato más legible
            fecha_original = sismo['Fecha']
            fecha_formateada = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
            
            resultados.append(
                f"⏰ **Fecha**: {fecha_formateada}\n"
                f"📍 **Ubicación**: {sismo['RefGeografica']}\n"
                f"🌋 **Magnitud**: {sismo['Magnitud']} Richter\n"
                f"⏱️ **Actualizado**: {sismo['FechaUpdate'].split('T')[0]}\n"
                f"📏 **Profundidad**: {sismo['Profundidad']} km"
            )
        
        return "\n\n".join(resultados)
        
    except requests.exceptions.RequestException as e:
        return f"🚨 Error de conexión: {str(e)}"
    except (KeyError, ValueError) as e:
        return f"⚠️ Error procesando datos: {str(e)}"
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"

# --- Handlers de comandos ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    commands = [
        "/hola - Envía tu ID de usuario",
        "/indi - Indicadores económicos",
        "/freqcpu - Frecuencia CPU RPi",
        "/ipdata - IP pública y proveedor",
        "/scan - IPs conectadas en la red",
        "/sismos - Últimos sismos en Chile",
        "/tamano - Espacio en disco RPi",
        "/temp - Temperatura RPi",
        "/uptime - Tiempo encendido RPi"
    ]
    response = "🤖 Hola, soy tu BOT!\n\nAcciones disponibles:\n" + "\n".join(commands)
    bot.reply_to(message, response)

@bot.message_handler(commands=['hola'])
def send_user_info(message):
    user = message.from_user
    bot.reply_to(message, f"Hola {user.first_name} (@{user.username})\nTu ID: {user.id}")

@bot.message_handler(commands=['indi'])
def send_indicadores(message):
    safe_send(message.chat.id, get_indicadores())

@bot.message_handler(commands=['freqcpu'])
def send_cpu_freq(message):
    freq = execute_command('cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq')
    bot.reply_to(message, f"Frecuencia CPU: {int(freq)//1000} MHz")

@bot.message_handler(commands=['ipdata'])
def send_ip_data(message):
    safe_send(message.chat.id, get_ip_data())

@bot.message_handler(commands=['scan'])
def send_network_scan(message):
    # Escaneo optimizado
    scan_result = execute_command('nmap -sn 192.168.0.0/24')
    # Filtrar solo resultados relevantes
    ips = re.findall(r'Nmap scan report for (\S+)', scan_result)
    safe_send(message.chat.id, f"Dispositivos conectados:\n" + "\n".join(ips))

@bot.message_handler(commands=['sismos'])
def send_earthquakes(message):
    sismos_info = get_sismos()
    safe_send(message.chat.id, sismos_info)

@bot.message_handler(commands=['tamano'])
def send_disk_space(message):
    disk = execute_command('df -h /')
    safe_send(message.chat.id, f"Espacio en disco:\n{disk}")

@bot.message_handler(commands=['temp'])
def send_temperature(message):
    temp = execute_command('/opt/vc/bin/vcgencmd measure_temp')
    bot.reply_to(message, temp)

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    uptime = execute_command('uptime -p')
    bot.reply_to(message, uptime)

# --- Modo ejecución programada (crontab) ---
def run_scheduled_task(task_name):
    """Ejecuta tareas específicas para crontab"""
    tasks = {
        'indi': get_indicadores,
        'sismos': get_sismos,
        'status': lambda: (
            f"🔄 {execute_command('uptime -p')}\n"
            f"🌡️ {execute_command('/opt/vc/bin/vcgencmd measure_temp')}\n"
            f"💾 {execute_command('df -h / | grep /')}"
        )
    }
    
    if task_name in tasks:
        result = tasks[task_name]()
        for chat_id in keys.TARGET_CHAT_IDS:  # Definir en passwords.py
            safe_send(chat_id, f"⏰ Reporte programado ({task_name}):\n\n{result}")
    else:
        print(f"Tarea no definida: {task_name}")

# --- Punto de entrada principal ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--cron':
        task = sys.argv[2] if len(sys.argv) > 2 else 'status'
        run_scheduled_task(task)
    else:
        print("Iniciando bot en modo interactivo...")
        bot.polling(none_stop=True)
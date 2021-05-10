#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from passwords import keys #módulo creado para almacenar token entregado por @BotFather
import telebot
import urllib3
import sys
import datetime
import random
import os
import requests
import socket

bot = telebot.TeleBot(keys.your_token) #your_token almacena el Token entregado por @BotFather 

@bot.message_handler(commands=['start']) 
def send_welcome(message):
	cid = message.chat.id
	bot.send_message(cid, 
		"""
		Hola, soy tu BOT!!!,
		Acciones disponibles
		/hola
		Envía Usuario ID
		/indi
		Envía los indicadores económicos
		/freqcpu
		Muestra FreqCPU RPi
		/ipdata
		Muestra IP pública y proveedor
		/scan
		Muestra las IP conectadas a la red
		/sismos
		Muestra los 3 últimos sismos en Chile
		/tamano
		Muestra espacio en disco RPi
		/temp
		Muestra temperatura RPi
		/uptime
		Muestra tiempo de encendido RPi


	""")

# Envia un mensaje de respuesta con tu username y tu ID
@bot.message_handler(commands=['hola'])
def hola(m):
	cid = m.chat.id
	id = m.from_user.id
	username = m.from_user.username
	first_name = m.from_user.first_name
	bot.send_message(cid, "Hola "+username+" Tu ID es : "+str(id))

#Obtiene informacion de los indicadores económicos en Chile
@bot.message_handler(commands=['indi'])
def indi(m):
	cid = m.chat.id
	r = requests.get('https://mindicador.cl/api').json()
	ipc = r['ipc']['valor']
	uf 	= r['uf']['valor']
	utm = r['utm']['valor']
	dolar = r['dolar']['valor']
	euro = r['euro']['valor']
	bot.send_message(cid,"IPC: "+str(ipc)+"\n"+"UF: "+str('{:,}'.format(uf))+"\n"+"UTM: "+str('{:,}'.format(utm))+"\n"+"Dolar: "+str(dolar)+"\n"+"Euro: "+str(euro)+"\n")

#Muestra la frecuencia disponible de la RPI
@bot.message_handler(commands=['freqcpu'])
def command_freqCPU(m):
	cid = m.chat.id
	freq_cpu = os.popen('cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq').read()
	bot.send_message(cid, freq_cpu )

#Muestra información pública de la ip
@bot.message_handler(commands=['ipdata'])
def ipdata(m):
	cid = m.chat.id #Almacena el ID
	data = requests.get('http://ip-api.com/json').json()
	query = data['query']
	isp = data['isp']
	country = data['country']
	region = data['regionName']
	bot.send_message(cid,"Informacion de su Ip Pública:\n "+query+"\n "+isp+",\n "+country+", "+region)

#realiza un escaneo de equipos conectados a la red desde la RPI		
@bot.message_handler(commands=['scan']) 
def command_scan(m):
	cid = m.chat.id #Almacena el ID
	scan = os.popen('sudo nmap -sP 192.168.0.1-254').read()
	bot.send_message(cid, scan)

# Muestra información de los últimos sismos en Chile
@bot.message_handler(commands=['sismos'])
def sismos(m):
	cid = m.chat.id
	data = requests.get('https://api.gael.cl/general/public/sismos').json()
	for info in data[0:3]:
		bot.send_message(cid,"Fecha: "+info['Fecha']+"\nLatitud :"+info['Latitud']+"\nLongitud: "+info['Longitud']+"\nProfundidad: "+info['Profundidad']+"\nMagnitud: "+info['Magnitud']+"\nAgencia: "+info['Agencia']+"\nRefGeográfica: "+info['RefGeografica']+"\nFechaUpdate: "+info['FechaUpdate']+"\n")

#Muestra el tamaño disponible de la RPI
@bot.message_handler(commands=['tamano'])
def tamano(m):
	cid = m.chat.id #Almacena el ID
	tamano = os.popen('df -h').read()
	bot.send_message(cid, tamano)

#Muestra la temperatura de la RPI
@bot.message_handler(commands=['temp'])
def command_temp(m):
	cid = m.chat.id #Almacena el ID 
	temp = os.popen('/opt/vc/bin/vcgencmd measure_temp').read()
	bot.send_message(cid, temp)

#Muestra el tiempo que lleva encendida la RPI
@bot.message_handler(commands=['uptime'])
def uptime(m):
	cid = m.chat.id #Almacena el ID
	uptime = os.popen('uptime').read()
	bot.send_message(cid, uptime)

bot.polling()
#!/usr/bin/env python3
import requests
import json
import urllib3
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
#import threading
import multiprocessing as mp
import io

info = '\033[1;35;48m'
warning = '\033[1;33;48m'
error = '\033[1;31;48m'
reset = '\033[1;37;48m'

class fHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
  def do_GET(self):
        
        self.send_response(200)
 

        self.send_header('Content-type','application/octet-stream')
        self.end_headers()
 		
        myfile = io.open(gfile, 'rb')

        message = bytes(myfile.read())

        self.wfile.write(message)
        return

def is_already_upgrading():
	v_r = requests.get(APIBaseUrl + 'firmware', verify=False)
	v_parsed = json.loads(v_r.text)
	try:
		v_bool = v_parsed['done']
		return not v_bool
	except KeyError:
		return False

def watch_upgrade():
	print(info)
	upgrading = True
	curr = ''
	while upgrading:
		r = requests.get(APIBaseUrl + 'firmware', verify=False)
		status = json.loads(r.text)
		msg = status['message']
		if msg == 'DeviceNotInRecoveryMode':
			print(error + 'ERROR: Device is Not In Recovery Mode!' + reset)
			quit()
		elif msg == 'ErasingChip':
			if not curr == 'ErasingChip':
				print('Erasing Flash...')
				curr = 'ErasingChip'
		elif msg == 'DownloadingImage':
			if not curr == 'DownloadingImage':
				print('Flashing...')
				curr = 'DownloadingImage'		
		elif msg == 'StartingApplication':
			if not curr == 'StartingApplication':
				print('Starting Firmware' + reset)
				upgrading = False
				curr = 'StartingApplication'
				quit()
		else:
			try:
				print('Raw Status: ' + msg)
			except TypeError:
				print('')
		time.sleep(1)	


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
APIBaseUrl = 'https://localhost:50352/brickServer/1/'

print(info + 'Checking if update process already started...')
update = is_already_upgrading()
if update == True:
	print(warning + "WARNING: update process is already started!" + reset)
	watch_upgrade()


def spawnserver(file):
	global gfile
	gfile = file
	print('starting File Server...')
	server_address = ('127.0.0.1', 8081)
	httpd = HTTPServer(server_address, fHTTPServer_RequestHandler)
	print('Serving binfile...')
	httpd.serve_forever()
print(info + 'What do you want to do?')
print('1. Flash latest oficial firmware')
print('2. Flash custom bin')
answ = input()
if answ == '1':
	print('Downloading API Config...')
	r = requests.get('https://config.api.education.lego.com/v1/ev3_edu/web/1.0.0/en-us')
	print('Parsing API Config...')
	api_config = json.loads(r.text)
	firmurl = api_config['app-specifics']['firmwareBin']
	print('Selected Official BIN')
elif answ == '2':
	pool = mp.Pool(mp.cpu_count())
	firmurl = 'http://localhost:8081/'
	print('Please enter .bin file path(without spaces!)')
	fpath = str(input())
	print(warning + "WARNING: DO NOT Terminate This Script!" + reset)
	#spawnserver(fpath)
	t1 = pool.apply_async(spawnserver, args=(fpath,))
	pool.close()
else:
	quit()

r = requests.get(APIBaseUrl + 'devices', verify=False)

parsed_device = json.loads(r.text)
print(info + '-----------')
try:
	did = parsed_device["availableDevices"][0]['deviceId']
except IndexError:
	print(error + 'No devices found :(' + info)
	print('-----------' + reset)
	quit()
print('Your Brick ID: ' + did)
print('-----------')

print(info + 'Connecting...')

r = requests.put(APIBaseUrl + 'devices/' + did + '?connect=true', verify=False)


print('Starting Firmware Upgrade...')


r = requests.put(APIBaseUrl + 'devices/' + did + '/firmware?url=' + firmurl, verify=False)
time.sleep(1)
watch_upgrade()
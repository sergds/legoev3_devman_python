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
class fHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
  def do_GET(self):
        
        self.send_response(200)
 

        self.send_header('Content-type','application/octet-stream')
        self.end_headers()
 		
        myfile = io.open(gfile, 'rb')

        message = bytes(myfile.read())

        self.wfile.write(message)
        return
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
APIBaseUrl = 'https://localhost:50352/brickServer/1/'
def spawnserver(file):
	global gfile
	gfile = file
	print('starting File Server...')
	server_address = ('127.0.0.1', 8081)
	httpd = HTTPServer(server_address, fHTTPServer_RequestHandler)
	print('Serving binfile...')
	httpd.serve_forever()
print('Downloading API Config...')
r = requests.get('https://config.api.education.lego.com/v1/ev3_edu/web/1.0.0/en-us')
print('Parsing API Config...')
api_config = json.loads(r.text)
print('What do you want to do?')
print('1. Flash latest oficial firmware')
print('2. Flash custom bin')
answ = input()
if answ == '1':
	firmurl = api_config['app-specifics']['firmwareBin']
	print('Selected Official BIN')
elif answ == '2':
	pool = mp.Pool(mp.cpu_count())
	firmurl = 'http://localhost:8081/'
	print('Please enter .bin file path(without spaces!)')
	fpath = str(input())
	print(fpath)
	#spawnserver(fpath)
	t1 = pool.apply_async(spawnserver, args=(fpath,))
	pool.close()
else:
	quit()
r = requests.get(APIBaseUrl + 'devices', verify=False)

parsed_device = json.loads(r.text)
print('\033[1;32;48m----------- \033[1;35;48m')
try:
	did = parsed_device["availableDevices"][0]['deviceId']
except IndexError:
	print('No devices found :(')
	quit()
print('Your Brick ID: ' + did)
print('\033[1;32;48m----------- \033[1;32;48m ')

print('\033[1;35;48mConnecting...')

r = requests.put(APIBaseUrl + 'devices/' + did + '?connect=true', verify=False)

print('Starting Firmware Upgrade...')
upgrading = True
curr = ''
r = requests.put(APIBaseUrl + 'devices/' + did + '/firmware?url=' + firmurl, verify=False)
time.sleep(1)
while upgrading:
	r = requests.get(APIBaseUrl + 'firmware', verify=False)
	status = json.loads(r.text)
	msg = status['message']
	if msg == 'DeviceNotInRecoveryMode':
		print('\033[1;31;48mDevice is Not In Recovery Mode!')
		quit()
	if msg == 'ErasingChip':
		if not curr == 'ErasingChip':
			print('Erasing Flash...')
			curr = 'ErasingChip'
	if msg == 'DownloadingImage':
		if not curr == 'DownloadingImage':
			print('Flashing...')
			curr = 'DownloadingImage'		
	if msg == 'StartingApplication':
		if not curr == 'StartingApplication':
			print('Done.')
			upgrading = False
			curr = 'StartingApplication'				
	time.sleep(1)
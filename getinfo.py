#!/usr/bin/env python3
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
APIBaseUrl = 'https://localhost:50352/brickServer/1/'

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
print('Device info: ')

r = requests.get(APIBaseUrl + 'devices/' + did, verify=False)

parsed_info = json.loads(r.text)
isRecovery = parsed_info['connectedDeviceInfo']['recoveryMode']
isRecovery_str = str(parsed_info['connectedDeviceInfo']['recoveryMode'])
contype = str(parsed_info['connectedDeviceInfo']['connectedTransport'])
bname = str(parsed_info['connectedDeviceInfo']['name'])
battery = parsed_info['connectedDeviceInfo']['batteryLevel']
battery_perc = str(battery * 100) + '%'

print('Is in Recovery mode: ' + isRecovery_str)
print('Brick name: ' + bname)
print('Connected by ' + contype)
if isRecovery == True:
	print('Battery: Unavail. in recovery :(')
else:
	print('Battery: ' + battery_perc)

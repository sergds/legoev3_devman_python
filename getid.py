#!/usr/bin/env python3
import requests
import json
APIBaseUrl = 'https://localhost:50352/brickServer/1/'
r = requests.get(APIBaseUrl + 'devices', verify=False)
parsed_device = json.loads(r.text)
print('\033[1;32;48m----------- \033[1;35;48m')
print('Your Brick ID: ' + parsed_device["availableDevices"][0]['deviceId'])
print('\033[1;32;48m----------- \033[1;32;48m ')

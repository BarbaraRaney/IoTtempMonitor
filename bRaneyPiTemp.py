    #!/usr/bin/python

import os
import glob 
import time 
import thread 
import socket 
import json
from datetime import datetime 
#from azure.mgmt.iothub import IotHubClient
from azure.servicebus import ServiceBusService, Message, Queue 

os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/' 
device1_file = glob.glob(base_dir + '28*')[0] + '/w1_slave'
device2_file = glob.glob(base_dir + '28*')[1] + '/w1_slave'
device3_file = glob.glob(base_dir + '28*')[2] + '/w1_slave'

servns ='raneybieventhubnamespace'
key_name = "RootManageSharedAccessKey"
key_value = "mQC9Uln3KUQimxkCgSuX9yTekuTzxW29STziLrQvZI0=" 

sbs = ServiceBusService(service_namespace = servns,shared_access_key_name=key_name, shared_access_key_value=key_value) 
#sbs = ServiceBusService(service_namespace = servns,shared_access_key_name=key_name, shared_access_key_value=key_value) 
#sbs.create_queue("newqueue")

def read_temp_raw(dfile):
    f = open(dfile, 'r')
    lines = f.readlines()
    f.close()
    return lines 

def read_temp(dfile):
    lines = read_temp_raw(dfile)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(dfile)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f

host = socket.gethostname() 


#while True:
try:
    data = {}
    temp1 = read_temp(device1_file)
    temp2 = read_temp(device2_file)
    temp3 = read_temp(device3_file)
    now = datetime.now()
    data['DeviceId'] = host
    data['rowId'] = now.strftime('%Y%m%d%H%M%S')
    data['timestamp'] = now.strftime('%Y/%m/%d %H:%M:%S')
    data['Temp1'] = str(temp1)
    data['Temp2'] = str(temp2)
    data['Temp3'] = str(temp3)
    json_data = json.dumps(data, sort_keys=True,ensure_ascii=True)
    print(json_data) 
#    msg = Message(json_data)
#    sbs.send_queue_message('newqueue', msg)
    sbs.send_event('raneybieventhub', json_data)
    time.sleep(5)

except Exception as e:
    print "Exception - ", repr(e)


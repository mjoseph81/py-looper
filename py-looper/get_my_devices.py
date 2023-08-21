'''
 /* 
 *  FILE    :   get_my_devices.py
 *  AUTHOR  :   Matt Joseph
 *  DATE    :   8/17/2023
 *  VERSION :   1.0.0
 *  
 *
 *  DESCRIPTION
 *  https://www.instructables.com/Py-Looper/
 *  
 *  
 *  
 *  REV HISTORY
 *  1.0.0)  Initial release
'''

import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'), ' | CHANNELS: ',p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels'))

'''
 /* 
 *  FILE    :   configure_midi_commands.py
 *  AUTHOR  :   Matt Joseph
 *  DATE    :   8/29/2023
 *  VERSION :   1.1.0
 *  
 *
 *  DESCRIPTION
 *  https://www.instructables.com/Py-Looper/
 *  
 *  
 *  
 *  REV HISTORY
 *  1.0.0)  Initial release
 *  1.1.0)  Added option to enable/disable LEDs
'''

parameters = []

parameters.append(input('Enter MIDI Control Number for MODE: '))
parameters.append(input('Enter MIDI Control Number for RESET: '))
parameters.append(input('Enter MIDI Control Number for CLEAR: '))
parameters.append(input('Enter MIDI Control Number for REC/PLAY: '))
parameters.append(input('Enter MIDI Control Number for STOP: '))
parameters.append(input('Enter MIDI Control Number for TRACK 1: '))
parameters.append(input('Enter MIDI Control Number for TRACK 2: '))
parameters.append(input('Enter MIDI Control Number for TRACK 3: '))
parameters.append(input('Enter MIDI Control Number for TRACK 4: '))
parameters.append(input('Enter COM Port for MIDI device (Ex. /dev/ttyACM0) : '))
parameters.append(input('Enable support for MODE & TRACK LEDs? (YES or NO) : '))

print(parameters)

f = open('Config/midi_commands.conf', 'w')
for param in parameters:
    f.write(param + '\n')
f.close()

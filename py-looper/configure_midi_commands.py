parameters = []

parameters.append(input('Enter MIDI Control Number for MODE: '))
parameters.append(input('Enter MIDI Control Number for RESET: '))
parameters.append(input('Enter MIDI Control Number for CLEAR: '))
parameters.append(input('Enter MIDI Control Number for REC/PLAY): '))
parameters.append(input('Enter MIDI Control Number for STOP: '))
parameters.append(input('Enter MIDI Control Number for TRACK 1: '))
parameters.append(input('Enter MIDI Control Number for TRACK 2: '))
parameters.append(input('Enter MIDI Control Number for TRACK 3: '))
parameters.append(input('Enter MIDI Control Number for TRACK 4: '))
parameters.append(input('Enter COM Port for MIDI device (Ex. /dev/ttyACM0) : '))

print(parameters)

f = open('Config/midi_commands.conf', 'w')
for param in parameters:
    f.write(param + '\n')
f.close()

parameters = []

parameters.append(input('Enter Sample Rate in Hz (Safe Choices 44100 and 48000): '))
parameters.append(input('Enter Buffer Size (Typical 256, 512, 1024) : '))
parameters.append(input('Enter Latency Correction in milliseconds: '))
parameters.append(input('Enter Input Device Index (Probably 1 or 0) : '))
parameters.append(input('Enter Output Device Index (Probably Same as Input) : '))
parameters.append(input('Enter Margin for Late Button Press in Milliseconds (Around 500 seems to work well) : '))
parameters.append(input('Enter Number of Audio Channels to record: '))

print(parameters)

f = open('Config/audio_settings.conf', 'w')
for param in parameters:
    f.write(param + '\n')
f.close()

f = open('Config/channels_to_tracks.conf', 'r')
parameters = f.readlines()
while (len(parameters) < 4):
    parameters.append('\n')
f.close()

parameters[0] = input('Enter channels to map to track 1 (separate with comma): ')
parameters[1] = input('Enter channels to map to track 2 (separate with comma): ')
parameters[2] = input('Enter channels to map to track 3 (separate with comma): ')
parameters[3] = input('Enter channels to map to track 4 (separate with comma): ')

print(parameters)

f = open('Config/channels_to_tracks.conf', 'w')
for i in range(4):
    f.write(parameters[i] + '\n')
f.close()

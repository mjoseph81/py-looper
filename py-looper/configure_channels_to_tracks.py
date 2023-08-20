'''
 /* 
 *  FILE    :   configure_channels_to_tracks.py
 *  AUTHOR  :   Matt Joseph
 *  DATE    :   8/17/2023
 *  VERSION :   1.0.0
 *  
 *
 *  DESCRIPTION
 *  https://www.instructables.com/id/DIY-Chewie-Monsta-Looper-Based-on-Ed-Sheerans/
 *  
 *  
 *  
 *  REV HISTORY
 *  1.0.0)  Initial release
'''

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
for param in parameters:
    f.write(param + '\n')
f.close()
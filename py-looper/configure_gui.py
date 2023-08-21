'''
 /* 
 *  FILE    :   configure_gui.py
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

parameters = []

parameters.append(input('Enter a name for Track 1: '))
parameters.append(input('Enter a name for Track 2: '))
parameters.append(input('Enter a name for Track 3: '))
parameters.append(input('Enter a name for Track 4: '))
parameters.append(input('Enter number of tracks to display (2 to 4): '))
parameters.append(input('Display GUI buttons? (YES or NO): '))

print(parameters)

f = open('Config/gui.conf', 'w')
for param in parameters:
    f.write(param + '\n') 
f.close()

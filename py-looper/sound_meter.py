import time, audioop
import pygame
import pyaudio
import wave

#Initialisation for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
INDEVICE = 5
OUTDEVICE = 5

#Object
p = pyaudio.PyAudio()
#stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    input_device_index = INDEVICE,
	output_device_index = OUTDEVICE,
    frames_per_buffer = CHUNK,
    start = True
)

#PyGame initialisations and basic objects
pygame.init()
screensize = (900, 600)
screen=pygame.display.set_mode(screensize)
pygame.display.set_caption("Shout harder.. :D")

#Defining colors
WHITE=(255,255,255)
RED=(255,128,128)
YELLOW=(255,255,128)
BLUE=(0,0,255)

#Loop till close button clicked
done=False
clock=pygame.time.Clock()

#variables
score=[]
width=0.8

margin = 20
samples_per_section = screensize[0]/3 - 2*margin

sound_tracks = [[0]*int(samples_per_section)]*3
max_value = [0]*3

current_section = 0

frames = []  # Initialize array to store frames

while not done:
	total=0
	
	
	# Store data in chunks for duration
	for i in range(0, int(RATE / CHUNK * 1)):
		data = stream.read(CHUNK)
		frames.append(data)
		
		reading=audioop.max(data, 2)
		total=total+reading
		
	#any scaling factor
	total=total/100

	sound_tracks[current_section] = sound_tracks[current_section][1:] + [total]
	max_value[current_section] = max(max_value[current_section], total)

	screen.fill(WHITE)

    # draw highlighted section
	pygame.draw.rect(screen,YELLOW,(screensize[0]/3*current_section, 0,screensize[0]/3, screensize[1]))

	for i in range(3):
		sectionx = i*screensize[0]/3 + margin
            #add meet wala last year ka feature
		pygame.draw.rect(screen,RED,(sectionx, screensize[1] - max_value[i],screensize[0]/3 - 2*margin, max_value[i]))

		for j in range(0,screensize[0]/3 - 2*margin):
			x = j + sectionx
			y = screensize[1] - sound_tracks[i][j]
			pygame.draw.rect(screen,BLUE,(x, y, 1, sound_tracks[i][j]))

	#frame flip must happen after all drawing commands
	pygame.display.flip()

	#Set close button event
	for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done=True
            if event.type==pygame.MOUSEBUTTONUP :
                if event.button == 3:
                    # right button pressed, clear all arrays
                    sound_tracks = [[0]*samples_per_section]*3
                    max_value = [0]*3
                    current_section = 0
                else:
                    pos = pygame.mouse.get_pos()
                    current_section = (pos[0] * 3) / screensize[0]
                    print (pos, current_section)
	
#clearing the resources
pygame.quit()
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()



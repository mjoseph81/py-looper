'''
 /* 
 *  FILE    :   audioloop_channels.py
 *  AUTHOR  :   Matt Joseph
 *  DATE    :   8/25/2023
 *  VERSION :   1.0.1
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
import numpy as np
import time
import os

#Config File
AUDIO_SETTINGS_CONF = 'audio_settings.conf'

#get configuration (audio settings etc.) from file
settings_file = open('Config/'+AUDIO_SETTINGS_CONF, 'r')
parameters = settings_file.readlines()
settings_file.close()

RATE = int(parameters[0]) #sample rate
CH_CHUNK = int(parameters[1]) #buffer size
latency_in_milliseconds = int(parameters[2])
INDEVICE = int(parameters[3]) #index (per pyaudio) of input device
OUTDEVICE = int(parameters[4]) #index of output device
overshoot_in_milliseconds = int(parameters[5]) #allowance in milliseconds for pressing 'stop recording' late
CHANNELS = int(parameters[6]) #number of channels to record

#create list of channels based on input
CH_LIST_INT = list(range(1, CHANNELS+1))
CH_LIST = [str(x) for x in CH_LIST_INT]
print(CH_LIST)

#Total CHUNK size is dependent on # of channels being recorded since they are interleaved
CHUNK = CH_CHUNK * CHANNELS

print(str(RATE) + ' ' +  str(CHUNK))
FORMAT = pyaudio.paInt16 #specifies bit depth (16-bit)

LATENCY = round((latency_in_milliseconds/1000) * (RATE/CHUNK)) #latency in buffers
print('latency correction (buffers): ' + str(LATENCY))
print('looking for devices ' + str(INDEVICE) + ' and ' + str(OUTDEVICE))

OVERSHOOT = round((overshoot_in_milliseconds/1000) * (RATE/CHUNK)) #allowance in buffers
MAXLENGTH = int(12582912 / CHUNK) #96mb of audio in total
SAMPLEMAX = 0.9 * (2**15) #maximum possible value for an audio sample (little bit of margin)
LENGTH = 0 #length of the first recording on track 1, all subsequent recordings quantized to a multiple of this.


debounce_length = 0.1 #length in seconds of button debounce period

silence = np.zeros([CHUNK], dtype = np.int16) #a buffer containing silence

#mixed output (sum of audio from tracks) is multiplied by output_volume before being played.
#This is updated dynamically as max peak in resultant audio changes
output_volume = np.float16(1.0)

restart_fadein = False
stop_fadeout = False


#multiplying by upramp and downramp gives fade-in and fade-out
downramp = np.linspace(0.8, 0, CHUNK)
upramp = np.linspace(0, 0.8, CHUNK)
#fadein() applies fade-in to a buffer
def fadein(buffer):
    np.multiply(buffer, upramp, out = buffer, casting = 'unsafe')
#fadeout() applies fade-out to a buffer
def fadeout(buffer):
    np.multiply(buffer, downramp, out = buffer, casting = 'unsafe')


class audioloop:
    def __init__(self):
        self.initialized = False
        self.length_factor = 1
        self.length = 0
        #self.audio is a 2D array of samples, each row is a buffer's worth of audio
        self.audio = np.zeros([MAXLENGTH, CHUNK], dtype = np.int16)
        self.readp = 0
        self.writep = 0
        self.isrecording = False
        self.isplaying = False
        self.iswaiting = False
        self.last_buffer_recorded = 0 #index of last buffer added
        self.preceding_buffer = np.zeros([CHUNK], dtype = np.int16)
        #dub ratio must be reduced with each overdub to keep all overdubs at the same level while preventing clipping.
        #first overdub is attenuated by a factor of 0.9, second by 0.81, etc.
        #each time the existing audio is attenuated by a factor of 0.9
        #in this way infinite overdubs of amplitude x result in total amplitude 9x.
        self.dub_ratio = 1.0
        self.rec_just_pressed = False
        self.play_just_pressed = False
        self.trackState = 0
        self.trackNumber = 0
        self.peak_vol = 0
        self.loop_length = 0
        self.channels = []
        self.ch_match_list = []
        
    #Sets channels that will be used for the loop
    def set_channels(self, channels):
        self.channels = channels
        #create array of channels that we will compare and match          
        s2 = set(self.channels)
        for x in CH_LIST:
            self.ch_match_list.append(x in s2)
        
        #print('CH_LIST: ', CH_LIST)
        #print('self.channels: ', self.channels)
        #print('self.ch_match_list: ', self.ch_match_list) 
        
    #incptrs() increments pointers and, when restarting while recording, advances dub ratio
    def incptrs(self):
        if self.readp == self.length - 1:
            self.readp = 0
            if self.isrecording:
                self.dub_ratio = self.dub_ratio * 0.9
                print(self.dub_ratio)
        else:
            self.readp = self.readp + 1
        self.writep = (self.writep + 1) % self.length
        
        
    #initialize() raises self.length to closest integer multiple of LENGTH and initializes read and write pointers
    def initialize(self):
        print('initialize called')
        if self.initialized:
            print('redundant initialization')
            return
        #set track length to LENGTH of master track so they are all the same initially (can change with instant_multiply)
        #self.writep = self.length - 1
        self.loop_length = LENGTH
        self.writep = self.loop_length  - 1
        self.last_buffer_recorded = self.writep
        self.length_factor = (int((self.length - OVERSHOOT) / LENGTH) + 1)
        self.length = self.length_factor * LENGTH
        print('length ' + str(self.length))
        print('last buffer recorded ' + str(self.last_buffer_recorded))
        #crossfade
        fadeout(self.audio[self.last_buffer_recorded]) #fade out the last recorded buffer
        fadein(self.audio[0]) #fade in first chunk
        preceding_buffer_copy = np.copy(self.preceding_buffer)
        #fadein(preceding_buffer_copy)
        self.audio[self.length - 1, :] += preceding_buffer_copy[:]
        #audio should be written ahead of where it is being read from, to compensate for input+output latency
        self.readp = (self.writep + LATENCY) % self.length
        self.initialized = True
        self.isplaying = True
        self.incptrs()
        #debounce flags
        self.rec_just_pressed = False
        self.play_just_pressed = False
        
        
    #add_buffer() appends a new buffer unless loop is filled to MAXLENGTH
    #expected to only be called before initialization
    def add_buffer(self, data):
        if self.length >= (MAXLENGTH - 1):
            self.length = 0
            print('loop full')
            return

        buff = data
        #check if a channel is not mapped to the loop
        #if not then set the samples for that channel to zero
        for n in range(0, CHANNELS):
            if self.ch_match_list[n] == False:
                #samples are interleaved, so start at offset based on the channel and step "num of channels" until the end of the samples
                for m in range(int(CH_LIST[n])-1,CHUNK,CHANNELS):
                    buff[m] = 0
                
        self.audio[self.length, :] = np.copy(buff)
        self.length = self.length + 1
    
    
    def is_restarting(self):
        if not self.initialized:
            return False
        if self.readp == 0:
            return True
        return False
    
    
    #read() reads and returns a buffer of audio from the loop
    def read(self):
        #if not initialized do nothing
        if not self.initialized:
            return(silence)
        #if initialized but muted just increment pointers
        if not self.isplaying:
            self.incptrs()
            return(silence)
        
        self.incptrs()
        
        #if initialized and playing, read audio from the loop and increment pointers
        pos = self.readp
               
        return(self.audio[pos, :])
    
    
    #dub() mixes an incoming buffer of audio with the one at writep
    def dub(self, data, fade_in = False, fade_out = False):
        if not self.initialized:
            return
        
        buff = data
        #check if a channel is not mapped to the loop
        #if not then set the samples for that channel to zero
        for n in range(0, CHANNELS):
            if self.ch_match_list[n] == False:
                #samples are interleaved, so start at offset based on the channel and step "num of channels" until the end of the samples
                for m in range(int(CH_LIST[n])-1,CHUNK,CHANNELS):
                    buff[m] = 0
                    
        datadump = np.copy(buff)
        self.audio[self.writep, :] = self.audio[self.writep, :] * 0.9 + datadump[:] * self.dub_ratio
        
        #if at the beginning or end of the buffer then crossfade
        if self.writep == self.length-1:
            self.fadeout(self.audio[self.writep, :])
        elif self.writep == 0:
            self.fadein(self.audio[self.writep, :])
            
    #clear() clears the loop so that a new loop of the same or a different length can be recorded on the track
    def clear(self):
        self.audio = np.zeros([MAXLENGTH, CHUNK], dtype = np.int16)
        self.initialized = False
        self.isplaying = False
        self.isrecording = False
        self.iswaiting = False
        self.length_factor = 1
        self.length = 0
        self.readp = 0
        self.writep = 0
        self.last_buffer_recorded = 0
        self.preceding_buffer = np.zeros([CHUNK], dtype = np.int16)
        self.rec_just_pressed = False
        self.play_just_pressed = False
        self.peak_vol = 0
        self.loop_length = 0
        self.dub_ratio = 1.0
        
        
    def start_recording(self, previous_buffer):
        self.isrecording = True
        self.iswaiting = False
        self.preceding_buffer = np.copy(previous_buffer)
        self.record = True
        
        
    #Doubles the length of the loop and copies the contents
    def instant_multiply(self):
        #Track length can't be more than half the MAXLENGTH in order to multiply
        if self.length <= (MAXLENGTH/2)-1:
            for n in range(self.length):
                self.audio[n+self.length, :] = self.audio[n, :]
            self.length += self.length
        else:
            print('Loop exceeds max length to multiply')
    
    def bouncewait_rec(self):
        self.rec_just_pressed = True
        time.sleep(debounce_length)
        self.rec_just_pressed = False
    
    def bouncewait_play(self):
        self.play_just_pressed = True
        time.sleep(debounce_length)
        self.play_just_pressed = False

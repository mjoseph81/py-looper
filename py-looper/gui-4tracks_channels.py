'''
 /* 
 *  FILE    :   gui-4tracks_channels.py
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

import tkinter as tk
from tkinter import ttk
from tkinter import *
import audioloop_channels as looper
import numpy as np
import time
import os
import pyaudio
import threading
from midi import MidiConnector
from midi import ControlChange
from midi import Message
import audioop

#App Version
VERSION = "v1.0.0"

#Config Files
GUI_CONF = 'gui.conf'
CHANNELS_CONF = 'channels_to_tracks.conf'
MIDI_CONF = 'midi_commands.conf'

#track states
S_PLAY = 0
S_MUTE = 1
S_ARM = 2
S_RECORD = 3
S_OVERDUB = 4

#Modes
M_PLAY = 0
M_RECORD = 1
M_STOP = 2

#Const
OFF = 0
ON = 1

#LED Colors
LED_OFF = 0
LED_GREEN = 1
LED_RED = 2
LED_AMBER = 3

#LEDs
LED_MODE = 0				
LED_T1 = 0				
LED_T2 = 0
LED_T3 = 0
LED_T4 = 0



isRunning = 0
mode = 0					#0=Play, 1=Record
trackState = [0,0,0,0]		#0=Play, 1=Mute, 2=Arm, 3=Record, 4=Overdub
playState = 0				#0=Stopped, 1=Playing
recState = 0				#0=Reset, 1=Recording
activeTrack = 1
tracks = [1,2,3,4]
selectedTrack = 0

screen_width = 0
screen_height = 0
frame_width = 0
frame_height = 0
peak = 0
usingMIDI = False

#Check if conf file for MIDI bindings is present and load them
#If file does not exist then disable MIDI connection
if os.path.exists('Config/'+MIDI_CONF):
	usingMIDI = True
	
	#get MIDI command configuration from file
	midi_commands_file = open('Config/'+MIDI_CONF, 'r')
	parameters = midi_commands_file.readlines()
	midi_commands_file.close()

	#Set MIDI Control Numbers
	MIDI_MODE = int(parameters[0])
	MIDI_RESET = int(parameters[1]) 
	MIDI_CLEAR = int(parameters[2]) 
	MIDI_RECPLAY = int(parameters[3]) 
	MIDI_STOP = int(parameters[4]) 
	MIDI_T1 = int(parameters[5]) 
	MIDI_T2 = int(parameters[6]) 
	MIDI_T3 = int(parameters[7]) 
	MIDI_T4 = int(parameters[8]) 
	COM_PORT = str(parameters[9]).strip("\r\n")
	print('MIDI configured')
else:
	usingMIDI = False
	print('MIDI not configured')

#Check if conf file for "Channel to Track" bindings is present and load them
if os.path.exists('Config/'+CHANNELS_CONF):
	#get channel to track binding from file
	channel_to_tracks_file = open('Config/'+CHANNELS_CONF, 'r')
	parameters = channel_to_tracks_file.readlines()
	channel_to_tracks_file.close()
	
	CH_TRACK1 = parameters[0].strip("\r\n").split(",")
	CH_TRACK2 = parameters[1].strip("\r\n").split(",")
	CH_TRACK3 = parameters[2].strip("\r\n").split(",")
	CH_TRACK4 = parameters[3].strip("\r\n").split(",")
	
	print('Track 1 Channels: ', CH_TRACK1)
	print('Track 2 Channels: ', CH_TRACK2)
	print('Track 3 Channels: ', CH_TRACK3)
	print('Track 4 Channels: ', CH_TRACK4)
	

	

#Check if conf file for GUI conf is present and load them
#If file does not exist then load Defaults
if os.path.exists('Config/'+GUI_CONF):
	#get track names from file
	track_names_file = open('Config/'+GUI_CONF, 'r')
	parameters = track_names_file.readlines()
	track_names_file.close()
	T1_NAME = parameters[0].strip("\r\n")
	T2_NAME = parameters[1].strip("\r\n")
	T3_NAME = parameters[2].strip("\r\n")
	T4_NAME = parameters[3].strip("\r\n")
	NUM_TRACKS = int(parameters[4].strip("\r\n"))
	DISPLAY_BUTTONS = parameters[5].strip("\r\n")
	
	if NUM_TRACKS < 2 or NUM_TRACKS > 4:
		print('Invalid number of Tracks defined, defaulting to 4 tracks.')
		NUM_TRACKS = 4
	
	if DISPLAY_BUTTONS != 'YES' and DISPLAY_BUTTONS != 'NO':
		print('Invalid input for button display parameter, defaulting to show buttons.')
		DISPLAY_BUTTONS = 'YES'
else:
	T1_NAME = 'Track 1'
	T2_NAME = 'Track 2'
	T3_NAME = 'Track 3'
	T4_NAME = 'Track 4'
	NUM_TRACKS = 4
	DISPLAY_BUTTONS = 'YES'
	
	
pa = pyaudio.PyAudio()

class Track(tk.Tk):
	
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		
		global frame_width
		global frame_height
		global screen_width
		global screen_height
		
		#create tkinter obj to get screen resolution then destroy it
		root = Tk()
		screen_width = root.winfo_screenwidth()
		screen_height = root.winfo_screenheight()
		root.destroy()
		
		frame_width = (screen_width / (NUM_TRACKS +1)) - 15
		frame_height = (screen_height) - 15
		
		lRed = ttk.Style()
		lRed.configure("gray1.Horizontal.TProgressbar", foreground='gray', background='black', thickness=20)
		
		sGray = ttk.Style()
		sGray.configure("gray.Horizontal.TProgressbar", foreground='gray', background='black', thickness=frame_width-20)

		self.title('Py Looper ' + VERSION)
		self.geometry('{}x{}'.format(screen_width, screen_height)) 
		self.configure(bg='black')
		
		
		# create all of the main containers
		cntl_frame = Frame(self, width=frame_width-100, height=screen_height, pady=3)
		tr1_frame = Frame(self, width=frame_width, height=frame_height, padx=3, pady=3)
		tr2_frame = Frame(self, width=frame_width, height=frame_height, padx=3, pady=3)
		tr3_frame = Frame(self, width=frame_width, height=frame_height, padx=3, pady=3)
		tr4_frame = Frame(self, width=frame_width, height=frame_height, padx=3, pady=3)
		
		# set frame background color
		cntl_frame.configure(bg='black')
		tr1_frame.configure(bg='black')
		tr2_frame.configure(bg='black')
		tr3_frame.configure(bg='black')
		tr4_frame.configure(bg='black')

		
		# layout all of the main containers
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		#add frames to the grid
		if NUM_TRACKS >= 2:
			cntl_frame.grid(row=0, column=0, sticky="ew")
			tr1_frame.grid(row=0, column=1, sticky="ew")
			tr2_frame.grid(row=0, column=2, sticky="ew")
		if NUM_TRACKS >=3:
			tr3_frame.grid(row=0, column=3, sticky="ew")
		if NUM_TRACKS ==4:
			tr4_frame.grid(row=0, column=4, sticky="ew")

		global trackState
		global S_PLAY
		
		for n in trackState:
			n = S_PLAY

		global mode
		mode = 0

		global isRunning
		isRunning = 0
		
		#Create a Mode label
		self.lblMode = tk.Label(cntl_frame, text= "PLAY", fg="green", bg="black", font=("Arial Bold", 36))
		self.lblMode.pack(pady=30)
		
		#Create a Active Track label
		self.lblTrack = tk.Label(cntl_frame, text= "TRACK 1", fg="yellow", bg="black", font=("Arial Bold", 36))
		self.lblTrack.pack(pady=30)

		if DISPLAY_BUTTONS == 'YES':
			#Create REC/PLAY button
			self.btnPlayRec = ttk.Button(cntl_frame,text="REC/PLAY", command=self.playRec)
			self.btnPlayRec.pack(pady=5)

			#Create STOP button
			self.btnStop = ttk.Button(cntl_frame,text="X / STOP", command=self.stop)
			self.btnStop.pack(pady=5)

			#Create MODE button
			self.btnMode = ttk.Button(cntl_frame,text="MODE", command=self.toggleMode)
			self.btnMode.pack(pady=5)

			#Create CLEAR button
			self.btnMode = ttk.Button(cntl_frame,text="CLEAR", command=self.clear_track)
			self.btnMode.pack(pady=5)

			#Create RESET button
			self.btnReset = ttk.Button(cntl_frame,text="RESET", command=self.reset)
			self.btnReset.pack(pady=5)
		
		

		#track 1 column
		self.track1loop = ttk.Progressbar(tr1_frame, style="gray1.Horizontal.TProgressbar", orient="horizontal", length=frame_width-10, mode="determinate")
		self.track1loop.pack(padx=5)
		self.track1vol = ttk.Progressbar(tr1_frame, style="gray.Horizontal.TProgressbar", orient="vertical", length=frame_height-200, mode="determinate")
		self.track1vol.pack(padx=5, pady=5)
		
		self.lblT1name = tk.Label(tr1_frame, text= T1_NAME, fg="WHITE", bg="black", font=("Arial Bold", 30))
		self.lblT1name.pack(pady=5)

		if DISPLAY_BUTTONS == 'YES':
			self.btnMuteTrack1 = ttk.Button(tr1_frame, text="Track 1", command=lambda: self.track_press(1))
			self.btnMuteTrack1.pack()

		#track 2 column
		self.track2loop = ttk.Progressbar(tr2_frame, style="gray1.Horizontal.TProgressbar", orient="horizontal", length=frame_width-10, mode="determinate")
		self.track2loop.pack(padx=5)
		self.track2vol = ttk.Progressbar(tr2_frame, style="gray.Horizontal.TProgressbar", orient="vertical", length=frame_height-200, mode="determinate")
		self.track2vol.pack(padx=5, pady=5)

		self.lblT2name = tk.Label(tr2_frame, text= T2_NAME, fg="WHITE", bg="black", font=("Arial Bold", 30))
		self.lblT2name.pack(pady=5)
		
		if DISPLAY_BUTTONS == 'YES':
			self.btnMuteTrack2 = ttk.Button(tr2_frame, text="Track 2", command=lambda: self.track_press(2))
			self.btnMuteTrack2.pack()

		if NUM_TRACKS >= 3:
			#track 3 column
			self.track3loop = ttk.Progressbar(tr3_frame, style="gray1.Horizontal.TProgressbar", orient="horizontal", length=frame_width-10, mode="determinate")
			self.track3loop.pack(padx=5)
			self.track3vol = ttk.Progressbar(tr3_frame, style="gray.Horizontal.TProgressbar", orient="vertical", length=frame_height-200, mode="determinate")
			self.track3vol.pack(padx=5, pady=5)

			self.lblT3name = tk.Label(tr3_frame, text= T3_NAME, fg="WHITE", bg="black", font=("Arial Bold", 30))
			self.lblT3name.pack(pady=5)
			
			if DISPLAY_BUTTONS == 'YES':
				self.btnMuteTrack3 = ttk.Button(tr3_frame, text="Track 3", command=lambda: self.track_press(3))
				self.btnMuteTrack3.pack()
		
		if NUM_TRACKS == 4:
			#track 4 column
			self.track4loop = ttk.Progressbar(tr4_frame, style="gray1.Horizontal.TProgressbar", orient="horizontal", length=frame_width-10, mode="determinate")
			self.track4loop.pack(padx=5)
			self.track4vol = ttk.Progressbar(tr4_frame, style="gray.Horizontal.TProgressbar", orient="vertical", length=frame_height-200, mode="determinate")
			self.track4vol.pack(padx=5, pady=5)

			self.lblT4name = tk.Label(tr4_frame, text= T4_NAME, fg="WHITE", bg="black", font=("Arial Bold", 30))
			self.lblT4name.pack(pady=5)

			if DISPLAY_BUTTONS == 'YES':
				self.btnMuteTrack4 = ttk.Button(tr4_frame, text="Track 4", command=lambda: self.track_press(4))
				self.btnMuteTrack4.pack()
		


		self.bytes = 0
		self.maxbytes = 0

	#Method for when the RESET button is pressed
	def reset(self):
		global mode
		global M_PLAY, M_RECORD, M_STOP
		global trackState, tracks
		global S_PLAY, S_RECORD, S_ARM, S_MUTE, S_OVERDUB
		global isRunning, recState
		global setup_isrecording, setup_donerecording
		global prev_rec_buffer, play_buffer
		global peak, output_volume, activeTrack
		
		print("Reset pressed")
		#clear all loops
		for loop in loops:
			loop.clear()
		
		#reset track states
		for n in tracks:
			trackState[n-1] = S_PLAY
			self.update_volume_bar(n)
		
		#clear global variables
		#mode = M_PLAY
		looper.LENGTH = 0
		isRunning = False
		setup_isrecording = False 
		setup_donerecording = False 
		prev_rec_buffer = np.zeros([looper.CHUNK], dtype = np.int16)
		play_buffer = np.zeros([looper.CHUNK], dtype = np.int16) 
		peak = 0
		output_volume = 0
		activeTrack = 1
		recState = 0
		
		#track 1
		self.track1loop["value"] = 0
		self.track1vol["value"] = 0	

		#track 2
		self.track2loop["value"] = 0
		self.track2vol["value"] = 0

		if NUM_TRACKS >= 3:
			#track 3
			self.track3loop["value"] = 0
			self.track3vol["value"] = 0

		if NUM_TRACKS == 4:
			#track 4
			self.track4loop["value"] = 0
			self.track4vol["value"] = 0

		self.lblTrack.config(fg='yellow', text="TRACK " + str(activeTrack))
		

	#Method for when the REC/PLAY button is pressed
	def playRec(self):
		global mode
		global M_PLAY, M_RECORD, M_STOP
		global trackState, tracks
		global S_PLAY, S_RECORD, S_ARM, S_MUTE, S_OVERDUB
		global isRunning, recState
		global rec_master_thread, close_master_thread, close_master_thread
		
		
		trackIndex = activeTrack -1
		
		if mode == M_PLAY:
			print("Play/Rec pressed in play mode")
			for loop in loops:
				if trackState[loop.trackNumber-1] == S_ARM:
					trackState[loop.trackNumber-1] = S_PLAY
					loop.isplaying = True
		elif mode == M_STOP:
			mode = M_PLAY
			for loop in loops:
				if trackState[loop.trackNumber-1] == S_ARM:
					trackState[loop.trackNumber-1] = S_PLAY
					loop.isplaying = True
				loop.readp = 0
				isRunning = True
			self.start()
					
		else:
			print("Play/Rec pressed in rec mode")
			if recState == 0:
				recState = 1
				for loop in loops:
					trackState[loop.trackNumber-1] = S_RECORD
					loop.isrecording = True
				#trackState[trackIndex] = S_RECORD
				self.gui_rec_init()
				rec_master_thread = threading.Thread(target=record_master_track)
				rec_master_thread.start()
				#record_master_track()
				
			else:
				if trackState[trackIndex] == S_MUTE:
					trackState[trackIndex] = S_PLAY
				elif trackState[trackIndex] == S_PLAY:
					trackState[trackIndex] = S_OVERDUB
					loops[trackIndex].isrecording = True
					update_vol_thread = threading.Thread(target=updatevolume)
					update_vol_thread.start()
					#updatevolume()
				elif trackState[trackIndex] == S_RECORD:
					trackState[trackIndex] = S_OVERDUB
					close_master_thread = threading.Thread(target=close_master_track)
					close_master_thread.start()
					#close_master_track()
					loops[trackIndex].isrecording = True
				elif trackState[trackIndex] == S_OVERDUB:
					trackState[trackIndex] = S_PLAY
					loops[trackIndex].isrecording = False
					update_vol_thread = threading.Thread(target=updatevolume)
					update_vol_thread.start()
					#updatevolume()
					
						
				for loop in loops:
					if loop.trackNumber != activeTrack:
						if trackState[loop.trackNumber - 1] == S_OVERDUB or trackState[loop.trackNumber - 1] == S_RECORD:
							trackState[loop.trackNumber - 1] = S_PLAY
							loop.isrecording = False
					
				if recState == 1:
					if isRunning == 0:
						isRunning=1
						self.start()
			
		for m in tracks:
			self.update_volume_bar(m)
		
	#Sets the loop bars to full and RED to indicate initial track recording
	def gui_rec_init(self):
		global frame_width
		global frame_height
		sRed = ttk.Style()
		sRed.configure("red1.Horizontal.TProgressbar", foreground='red', background='red',length=frame_width-10, thickness=20)
		
		#track 1
		self.track1loop.configure(style="red1.Horizontal.TProgressbar")
		self.track1loop["value"] = 100
		self.track1loop["maximum"] =100

		#track 2
		self.track2loop.configure(style="red1.Horizontal.TProgressbar")
		self.track2loop["value"] = 100
		self.track2loop["maximum"] = 100

		if NUM_TRACKS >= 3:
			#track 3
			self.track3loop.configure(style="red1.Horizontal.TProgressbar")
			self.track3loop["value"] = 100
			self.track3loop["maximum"] = 100
		
		if NUM_TRACKS == 4:
			#track 4
			self.track4loop.configure(style="red1.Horizontal.TProgressbar")
			self.track4loop["value"] = 100
			self.track4loop["maximum"] = 100

	
	#Method that starts the GUI after initial loop is recorded
	def start(self):
		global isRunning
		global trackState
		global ON, OFF
		global S_PLAY, S_MUTE
		global tracks
		global frame_width
		global frame_height
		global peak
		
		sRed = ttk.Style()
		sRed.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue',length=frame_width-10, thickness=20)
		
		print("start method called")
		
		vol_max = 10000
		
		
		#track 1
		self.track1loop["value"] = loops[0].length
		self.track1loop["maximum"] =loops[0].length
		self.track1loop.configure(style="blue.Horizontal.TProgressbar")

		self.track1vol["value"] = 0
		self.track1vol["maximum"] = vol_max

		#track 2
		self.track2loop["value"] = loops[1].length
		self.track2loop["maximum"] = loops[1].length
		self.track2loop.configure(style="blue.Horizontal.TProgressbar")

		self.track2vol["value"] = 0
		self.track2vol["maximum"] = vol_max

		if NUM_TRACKS >= 3:
			#track 3
			self.track3loop["value"] = loops[2].length
			self.track3loop["maximum"] = loops[2].length
			self.track3loop.configure(style="blue.Horizontal.TProgressbar")

			self.track3vol["value"] = 0
			self.track3vol["maximum"] = vol_max
		
		if NUM_TRACKS == 4:
			#track 4
			self.track4loop["value"] = loops[3].length
			self.track4loop["maximum"] = loops[3].length
			self.track4loop.configure(style="blue.Horizontal.TProgressbar")

			self.track4vol["value"] = 0
			self.track4vol["maximum"] = vol_max
				
		#create new thread for updating the loop and volume bars on the GUI	
		global read_data_thread
		read_data_thread = threading.Thread(target=self.read_bytes)
		read_data_thread.daemon = True
		read_data_thread.start()

		

	
	
	#Method for when the STOP button is pressed
	def stop(self):
		global isRunning
		global trackState, tracks, activeTrack
		global ON, OFF
		global mode, M_PLAY, M_RECORD
		global S_PLAY, S_MUTE, S_ARM
		
		
		
		if mode == M_PLAY:
			isRunning=0
			mode = M_STOP
			for loop in loops:
				if trackState[loop.trackNumber-1] != S_MUTE:
					trackState[loop.trackNumber-1] = S_ARM
				loop.isplaying = False
				loop.readp = 0


			#track 1
			self.track1loop["value"] = loops[0].length
			self.track1vol["value"] = 0	

			#track 2
			self.track2loop["value"] = loops[1].length
			self.track2vol["value"] = 0

			if NUM_TRACKS >= 3:
				#track 3
				self.track3loop["value"] = loops[2].length
				self.track3vol["value"] = 0

			if NUM_TRACKS == 4:
				#track 4
				self.track4loop["value"] = loops[3].length
				self.track4vol["value"] = 0
			
			for n in tracks:
				#self.mute(ON,n)
				self.update_volume_bar(n)
		else:
			loops[activeTrack-1].instant_multiply()

		
		
	#Method that runs in a separate thread to update the loop and volume bars
	def read_bytes(self):
		global isRunnning
		global tracks
		global peak
		
		if isRunning == 1:
			#get position of each track
			track_1_pos = loops[0].readp
			track_2_pos = loops[1].readp
			track_3_pos = loops[2].readp
			track_4_pos = loops[3].readp
		
			#calc number of samples per 50ms refresh time
			samp_per_int = looper.RATE / 50
			
			#get volume of each track for the current position
			#track_1_data = np.max(np.abs(loops[0].audio.astype(np.int32)[track_1_pos][:]))
			#track_2_data = np.max(np.abs(loops[1].audio.astype(np.int32)[track_2_pos][:]))
			#track_3_data = np.max(np.abs(loops[2].audio.astype(np.int32)[track_3_pos][:]))
			#track_4_data = np.max(np.abs(loops[3].audio.astype(np.int32)[track_4_pos][:]))
			
			
			#Since the GUI is updated every 50ms we need to get the average of all samples recorded since the last update
			#this makes the volume meters more accurate and smoother
			if track_1_pos >= samp_per_int:
				track_1_data = np.mean(np.abs(loops[0].audio.astype(np.int32)[track_1_pos-samp_per_int:track_1_pos][:]))
			else:
				track_1_data = np.max(np.abs(loops[0].audio.astype(np.int32)[track_1_pos][:]))
				
			if track_2_pos >= samp_per_int:
				track_2_data = np.mean(np.abs(loops[1].audio.astype(np.int32)[track_2_pos-samp_per_int:track_2_pos][:]))
			else:
				track_2_data = np.max(np.abs(loops[1].audio.astype(np.int32)[track_2_pos][:]))
				
			if track_3_pos >= samp_per_int:
				track_3_data = np.mean(np.abs(loops[2].audio.astype(np.int32)[track_3_pos-samp_per_int:track_3_pos][:]))
			else:
				track_3_data = np.max(np.abs(loops[2].audio.astype(np.int32)[track_3_pos][:]))
				
			if track_4_pos >= samp_per_int:
				track_4_data = np.mean(np.abs(loops[3].audio.astype(np.int32)[track_4_pos-samp_per_int:track_4_pos][:]))
			else:
				track_4_data = np.max(np.abs(loops[3].audio.astype(np.int32)[track_4_pos][:]))
			
			
			#calc RMS volume for each track
			track_1_vol = audioop.rms(track_1_data,2)
			track_2_vol = audioop.rms(track_2_data,2)
			track_3_vol = audioop.rms(track_3_data,2)
			track_4_vol = audioop.rms(track_4_data,2)
					

			
			#print('track 1 vol: ' + str(track_1_vol)
			#	 + ' | track 2 vol: ' + str(track_2_vol)
			#	 + ' | track 3 vol: ' + str(track_3_vol)
			#	 + ' | track 4 vol: ' + str(track_4_vol)
			#	 + ' | Peak vol: ' + str(peak)
			#	 )
				
		
			#track 1
			self.track1loop["value"] = track_1_pos
			self.track1loop["maximum"] =loops[0].length
			self.track1vol["value"] = track_1_vol
			self.track1vol["maximum"] = peak

			#track 2
			self.track2loop["value"] = track_2_pos
			self.track2loop["maximum"] =loops[1].length
			self.track2vol["value"] = track_2_vol
			self.track2vol["maximum"] = peak

			if NUM_TRACKS >= 3:
				#track 3
				self.track3loop["value"] = track_3_pos
				self.track3loop["maximum"] =loops[2].length
				self.track3vol["value"] = track_3_vol
				self.track3vol["maximum"] = peak
			
			if NUM_TRACKS == 4:
				#track 4
				self.track4loop["value"] = track_4_pos
				self.track4loop["maximum"] =loops[3].length
				self.track4vol["value"] = track_4_vol
				self.track4vol["maximum"] = peak
			
			

			#recursively calls itself every 50ms
			self.after(50, self.read_bytes)
				
		
	#Method to update the color of the loop and volumen bars based on track state
	def update_volume_bar(self, selectedTrack):
		global frame_width
		global frame_height
		global trackState
		global S_PLAY, S_MUTE, S_ARM, S_RECORD, S_OVERDUB
		global LED_T1, LED_T2, LED_T3, LED_T4
		
		trackIndex = selectedTrack - 1
		
		#styles for vol bar
		sGray = ttk.Style()
		sGray.configure("gray.Horizontal.TProgressbar", foreground='gray', background='gray', thickness= frame_width-20)
		
		sGreen = ttk.Style()
		sGreen.configure("green.Horizontal.TProgressbar", foreground='green', background='green', thickness= frame_width-20)
		
		sRed = ttk.Style()
		sRed.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness= frame_width-20)
		
		sYellow = ttk.Style()
		sYellow.configure("yellow.Horizontal.TProgressbar", foreground='yellow', background='yellow', thickness= frame_width-20)
		
		#styles for loop bar
		vRed = ttk.Style()
		vRed.configure("red1.Horizontal.TProgressbar", foreground='red', background='red',length=frame_width-10, thickness=20)

		vBlue = ttk.Style()
		vBlue.configure("blue1.Horizontal.TProgressbar", foreground='blue', background='blue',length=frame_width-10, thickness=20)
		
		vYellow = ttk.Style()
		vYellow.configure("yellow1.Horizontal.TProgressbar", foreground='yellow', background='yellow',length=frame_width-10, thickness=20)
		
		vGreen = ttk.Style()
		vGreen.configure("green1.Horizontal.TProgressbar", foreground='green', background='green',length=frame_width-10, thickness=20)
		
		vGray = ttk.Style()
		vGray.configure("gray1.Horizontal.TProgressbar", foreground='gray', background='gray',length=frame_width-10, thickness=20)

		#print("update_volume_bar method triggered")
		
		if selectedTrack == 1:
			print("track 1 state: " + str(trackState[trackIndex]))
			if trackState[trackIndex] == S_MUTE:
				self.track1vol.configure(style="gray.Horizontal.TProgressbar")
				self.track1loop.configure(style="gray1.Horizontal.TProgressbar")
				LED_T1 = LED_OFF
			elif trackState[trackIndex]  == S_PLAY:
				self.track1vol.configure(style="green.Horizontal.TProgressbar")
				self.track1loop.configure(style="blue1.Horizontal.TProgressbar")
				LED_T1 = LED_GREEN
			elif trackState[trackIndex]  == S_RECORD:
				self.track1vol.configure(style="red.Horizontal.TProgressbar")
				self.track1loop.configure(style="red1.Horizontal.TProgressbar")
				LED_T1 = LED_RED
			elif trackState[trackIndex]  == S_OVERDUB:
				self.track1vol.configure(style="red.Horizontal.TProgressbar")
				self.track1loop.configure(style="red1.Horizontal.TProgressbar")
				LED_T1 = LED_RED
			elif trackState[trackIndex]  == S_ARM:
				self.track1vol.configure(style="yellow.Horizontal.TProgressbar")
				self.track1loop.configure(style="yellow1.Horizontal.TProgressbar")
				LED_T1 = LED_AMBER
		elif selectedTrack == 2:
			print("track 2 state: " + str(trackState[trackIndex]))
			if trackState[trackIndex] == S_MUTE:
				self.track2vol.configure(style="gray.Horizontal.TProgressbar")
				self.track2loop.configure(style="gray1.Horizontal.TProgressbar")
				LED_T2 = LED_OFF
			elif trackState[trackIndex]  == S_PLAY:
				self.track2vol.configure(style="green.Horizontal.TProgressbar")
				self.track2loop.configure(style="blue1.Horizontal.TProgressbar")
				LED_T2 = LED_GREEN
			elif trackState[trackIndex]  == S_RECORD:
				self.track2vol.configure(style="red.Horizontal.TProgressbar")
				self.track2loop.configure(style="red1.Horizontal.TProgressbar")
				LED_T2 = LED_RED
			elif trackState[trackIndex]  == S_OVERDUB:
				self.track2vol.configure(style="red.Horizontal.TProgressbar")
				self.track2loop.configure(style="red1.Horizontal.TProgressbar")
				LED_T2 = LED_RED
			elif trackState[trackIndex]  == S_ARM:
				self.track2vol.configure(style="yellow.Horizontal.TProgressbar")
				self.track2loop.configure(style="yellow1.Horizontal.TProgressbar")
				LED_T2 = LED_AMBER
		elif selectedTrack == 3:
			if NUM_TRACKS >= 3:
				print("track 3 state: " + str(trackState[trackIndex]))
				if trackState[trackIndex] == S_MUTE:
					self.track3vol.configure(style="gray.Horizontal.TProgressbar")
					self.track3loop.configure(style="gray1.Horizontal.TProgressbar")
					LED_T3 = LED_OFF
				elif trackState[trackIndex]  == S_PLAY:
					self.track3vol.configure(style="green.Horizontal.TProgressbar")
					self.track3loop.configure(style="blue1.Horizontal.TProgressbar")
					LED_T3 = LED_GREEN
				elif trackState[trackIndex]  == S_RECORD:
					self.track3vol.configure(style="red.Horizontal.TProgressbar")
					self.track3loop.configure(style="red1.Horizontal.TProgressbar")
					LED_T3 = LED_RED
				elif trackState[trackIndex]  == S_OVERDUB:
					self.track3vol.configure(style="red.Horizontal.TProgressbar")
					self.track3loop.configure(style="red1.Horizontal.TProgressbar")
					LED_T3 = LED_RED
				elif trackState[trackIndex]  == S_ARM:
					self.track3vol.configure(style="yellow.Horizontal.TProgressbar")
					self.track3loop.configure(style="yellow1.Horizontal.TProgressbar")
					LED_T3 = LED_AMBER
		elif selectedTrack == 4:
			if NUM_TRACKS == 4:
				print("track 4 state: " + str(trackState[trackIndex]))
				if trackState[trackIndex] == S_MUTE:
					self.track4vol.configure(style="gray.Horizontal.TProgressbar")
					self.track4loop.configure(style="gray1.Horizontal.TProgressbar")
					LED_T4 = LED_OFF
				elif trackState[trackIndex]  == S_PLAY:
					self.track4vol.configure(style="green.Horizontal.TProgressbar")
					self.track4loop.configure(style="blue1.Horizontal.TProgressbar")
					LED_T4 = LED_GREEN
				elif trackState[trackIndex]  == S_RECORD:
					self.track4vol.configure(style="red.Horizontal.TProgressbar")
					self.track4loop.configure(style="red1.Horizontal.TProgressbar")
					LED_T4 = LED_RED
				elif trackState[trackIndex]  == S_OVERDUB:
					self.track4vol.configure(style="red.Horizontal.TProgressbar")
					self.track4loop.configure(style="red1.Horizontal.TProgressbar")
					LED_T4 = LED_RED
				elif trackState[trackIndex]  == S_ARM:
					self.track4vol.configure(style="yellow.Horizontal.TProgressbar")
					self.track4loop.configure(style="yellow1.Horizontal.TProgressbar")
					LED_T4 = LED_AMBER
				

	#Method called when MODE button is pressed to toggle between MODES
	def toggleMode(self):
		global mode
		global trackState, tracks
		global M_PLAY, M_RECORD
		global S_PLAY, S_MUTE, S_ARM, S_RECORD, S_OVERDUB
		global LED_MODE

		if mode== M_PLAY:
			mode = M_RECORD
			self.lblMode.config(fg='red', text="RECORD")
			LED_MODE = LED_RED
			#no change to track States
		else:
			mode = M_PLAY
			LED_MODE = LED_GREEN
			self.lblMode.config(fg='green', text="PLAY")
			#when transitioning to PLAY mode, put all tracks not in MUTE into PLAY
			for loop in loops:
				if trackState[loop.trackNumber-1] != S_MUTE:
					trackState[loop.trackNumber-1]  = S_PLAY	
					loop.isplaying = True
				loop.isrecording = False
					
					
			for m in tracks:
				self.update_volume_bar(m)

					
	#Method called when any of the TRACK buttons are pressed
	def track_press(self, selectedTrack):
		global trackState
		global tracks
		global recState, activeTrack, isRunning
		global mode, M_PLAY, M_RECORD
		global S_PLAY, S_MUTE, S_ARM, S_RECORD, S_OVERDUB
		global rec_master_thread, close_master_thread, update_vol_thread
		
		activeTrack = selectedTrack
		trackIndex = selectedTrack -1
		
		self.lblTrack.config(fg='yellow', text="TRACK " + str(activeTrack))
		
		#set track state based on mode and previous state
		if mode == M_PLAY or mode == M_STOP:
			if trackState[trackIndex] == S_PLAY:
				trackState[trackIndex] = S_MUTE
				loops[trackIndex].isplaying = False
			elif trackState[trackIndex] == S_MUTE:
				trackState[trackIndex] = S_ARM
				loops[trackIndex].isplaying = False
			elif trackState[trackIndex] == S_ARM:
				trackState[trackIndex] = S_MUTE
				loops[trackIndex].isplaying = False
		else:					
			print("Track pressed in rec mode")
			if recState == 0:
				recState = 1
				for loop in loops:
					trackState[loop.trackNumber-1] = S_RECORD
					loop.isrecording = True
				self.gui_rec_init()
				rec_master_thread = threading.Thread(target=record_master_track)
				rec_master_thread.start()
			else:
				if trackState[trackIndex] == S_MUTE:
					trackState[trackIndex] = S_PLAY
				elif trackState[trackIndex] == S_PLAY:
					trackState[trackIndex] = S_OVERDUB
					loops[trackIndex].isrecording = True
					update_vol_thread = threading.Thread(target=updatevolume)
					update_vol_thread.start()
					#updatevolume()
				elif trackState[trackIndex] == S_RECORD:
					trackState[trackIndex] = S_PLAY
					loops[trackIndex].isrecording = False
					close_master_thread = threading.Thread(target=close_master_track)
					close_master_thread.start()
					
				elif trackState[trackIndex] == S_OVERDUB:
					trackState[trackIndex] = S_PLAY
					loops[trackIndex].isrecording = False
					update_vol_thread = threading.Thread(target=updatevolume)
					update_vol_thread.start()
					#updatevolume()
					
				for loop in loops:
					if loop.trackNumber != activeTrack:
						if trackState[loop.trackNumber - 1] == S_OVERDUB or trackState[loop.trackNumber - 1] == S_RECORD:
							trackState[loop.trackNumber - 1] = S_PLAY
							loop.isrecording = False
			
		
				if recState == 1:
					if isRunning == 0:
						isRunning=1
						self.start()
			
		for m in tracks:
			self.update_volume_bar(m)
	
	#Method called when the CLEAR button is pressed
	def clear_track(self):
		global trackState
		global tracks
		global activeTrack
		global S_PLAY
		
		trackIndex = activeTrack -1
		
		if loops[trackIndex].initialized:
			loops[trackIndex].audio = np.zeros([looper.MAXLENGTH, looper.CHUNK], dtype = np.int16)
			loops[trackIndex].preceding_buffer = np.zeros([looper.MAXLENGTH, looper.CHUNK], dtype = np.int16)
			loops[trackIndex].peak_vol = 0
			loops[trackIndex].dub_ratio = 1.0
			if trackState[trackIndex] == S_ARM or trackState[trackIndex] == S_MUTE:
				trackState[trackIndex] = S_PLAY
				self.update_volume_bar(activeTrack)
		
		
#create instance of the GUI
app = Track()


#create instances of four audio loops.
loops = (looper.audioloop(), looper.audioloop(), looper.audioloop(), looper.audioloop())

#define track numbers
loops[0].trackNumber = 1
loops[1].trackNumber = 2
loops[2].trackNumber = 3
loops[3].trackNumber = 4

#pass channel bindings to loops
loops[0].set_channels(CH_TRACK1)
loops[1].set_channels(CH_TRACK2)
loops[2].set_channels(CH_TRACK3)
loops[3].set_channels(CH_TRACK4)


#while looping, prev_rec_buffer keeps track of the audio buffer recorded before the current one
prev_rec_buffer = np.zeros([looper.CHUNK], dtype = np.int16)

#update output volume to prevent mixing distortion due to sample overflow
def updatevolume():
    global output_volume
    global peak
	
    loops[0].peak_vol = np.max(np.abs(loops[0].audio.astype(np.int32)[:][:]))
    loops[1].peak_vol = np.max(np.abs(loops[0].audio.astype(np.int32)[:][:]))
    loops[2].peak_vol = np.max(np.abs(loops[0].audio.astype(np.int32)[:][:]))
    loops[3].peak_vol = np.max(np.abs(loops[0].audio.astype(np.int32)[:][:]))
	
    peak = np.max(
                  np.abs(
                          loops[0].audio.astype(np.int32)[:][:]
                        + loops[1].audio.astype(np.int32)[:][:]
                        + loops[2].audio.astype(np.int32)[:][:]
                        + loops[3].audio.astype(np.int32)[:][:]
                        )
                 )
    print('peak = ' + str(peak))
    if peak > looper.SAMPLEMAX:
        output_volume = looper.SAMPLEMAX / peak
    else:
        output_volume = 1
    print('output volume = ' + str(output_volume))




setup_isrecording = False #set to True when track 1 recording button is first pressed
setup_donerecording = False #set to true when first track 1 recording is done

play_buffer = np.zeros([looper.CHUNK], dtype = np.int16) #buffer to hold mixed audio from all 4 tracks


#Callback method for the audio instance
def looping_callback(in_data, frame_count, time_info, status):
    global play_buffer
    global prev_rec_buffer
    global setup_donerecording
    global setup_isrecording
    global activeTrack
	
	
    trackIndex = activeTrack - 1
	
    #global looper.LENGTH
    current_rec_buffer = np.copy(np.frombuffer(in_data, dtype = np.int16))
    #print('length of buffer: ', len(in_data), ' | frame_count: ',frame_count)
    
	
    #SETUP: FIRST RECORDING
    #if setup is not done i.e. if the master loop hasn't been recorded to yet
    if not setup_donerecording:
        #if setup is currently recording, that recording action happens in the following lines
        if setup_isrecording:
            #if the max allowed loop length is exceeded, stop recording and start looping
            if looper.LENGTH >= looper.MAXLENGTH:
                print('Overflow')
                setup_donerecording = True
                setup_isrecording = False
                return(looper.silence, pyaudio.paContinue)
            #otherwise append incoming audio to master loop, increment LENGTH and continue
            loops[trackIndex].add_buffer(current_rec_buffer)
            loops[trackIndex].isrecording = True
            for loop in loops:
                    if loop.trackNumber != activeTrack:
                        #record silence to non-active tracks
                        loop.isrecording = True
                        loop.add_buffer(looper.silence)
            looper.LENGTH = looper.LENGTH + 1
            return(looper.silence, pyaudio.paContinue)
        #if setup not done and not currently happening then just wait
        else:
            return(looper.silence, pyaudio.paContinue)
          	
    #execution ony reaches here if setup (first loop record and set LENGTH) finished.
        
	#when master loop restarts, start recording on any other tracks that are waiting
    if loops[0].is_restarting():
        for loop in loops:
            if loop.isrecording:
                #loop.start_recording(prev_rec_buffer)
                print('Recording...')
				
    #if a loop is recording, check initialization and accordingly append or overdub
    for loop in loops:
        if loop.isrecording:
            if loop.initialized:
                loop.dub(current_rec_buffer)
            else:
                loop.add_buffer(current_rec_buffer)

				

    #add to play_buffer only one-fourth of each audio signal times the output_volume
    play_buffer[:] = np.multiply((
                                   loops[0].read().astype(np.int32)[:]
                                 + loops[1].read().astype(np.int32)[:]
                                 + loops[2].read().astype(np.int32)[:]
                                 + loops[3].read().astype(np.int32)[:]
                                 ), looper.output_volume, out= None, casting = 'unsafe').astype(np.int16)
    #current buffer will serve as previous in next iteration
    prev_rec_buffer = np.copy(current_rec_buffer)
    #play mixed audio and move on to next iteration
    return(play_buffer, pyaudio.paContinue)


#now initializing looping_stream (the only audio stream)
looping_stream = pa.open(
    format = looper.FORMAT,
    channels = looper.CHANNELS,
    rate = looper.RATE,
    input = True,
    output = True,
    input_device_index = looper.INDEVICE,
	output_device_index = looper.OUTDEVICE,
    frames_per_buffer = looper.CH_CHUNK,
    start = True,
    stream_callback = looping_callback
)


#audio stream has now been started and the callback function is running in a background thread.
#first, we give the stream some time to properly start up
time.sleep(0.02)

print('ready')

#Method that sets up the initial track recording
def record_master_track():
	global setup_isrecording
	global activeTrack
	
	trackIndex = activeTrack - 1
	
	#when the button is pressed, set the flag... looping_callback will see this flag. Also start recording on track 1
	setup_isrecording = True
	print("recording master track")
	loops[trackIndex].start_recording(prev_rec_buffer)

#Method that completes the initial track recording
def close_master_track():
	global setup_isrecording
	global setup_donerecording
	
	
	print("closing master track")
	#now stop recording and initialize master loop
	setup_isrecording = False
	setup_donerecording = True
	for loop in loops:
		loop.initialize()
		loop.isrecording = False

	updatevolume()
	print('length is ' + str(looper.LENGTH))



finished = False

#calling finish() will set finished flag, allowing program to break from loop at end of script and exit
def finish():
    global finished
    finished = True

#restart_looper() restarts this python script
def restart_looper():
    pa.terminate() #needed to free audio device for reuse
    os.execlp('python3', 'python3', 'gui-4tracks.py') #replaces current process with a new instance of the same script


#Method that runs on a separate thread to wait and read incoming MIDI commands
def read_midi():
	while True:
		msg = conn.read()  # read on ANY channel by default
		print(msg.control_number)
		if msg.control_number == MIDI_MODE:
			app.toggleMode()
		elif msg.control_number == MIDI_RESET:
			app.reset()
		elif msg.control_number == MIDI_CLEAR:
			app.clear_track()
		elif msg.control_number == MIDI_RECPLAY:
			app.playRec()
		elif msg.control_number == MIDI_STOP:
			app.stop()
		elif msg.control_number == MIDI_T1:
			app.track_press(1)
		elif msg.control_number == MIDI_T2:
			app.track_press(2)
		elif msg.control_number == MIDI_T3:
			app.track_press(3)
		elif msg.control_number == MIDI_T4:
			app.track_press(4)
			
		send_midi(10, LED_MODE)
		send_midi(11, LED_T1)
		send_midi(12, LED_T2)
		send_midi(13, LED_T3)
		send_midi(14, LED_T4)


def send_midi(ctrl_num, value):
	cc = ControlChange(ctrl_num, value)
	msg = Message(cc, channel=1)
	conn.write(msg)
	
	
if usingMIDI == True:
	#open the COM port for the midi device
	conn = MidiConnector(COM_PORT)

	#Define a new thread and link it to 'read_midi' method so that GUI is not blocked
	midi_thread = threading.Thread(target=read_midi)
	midi_thread.setDaemon(True)
	midi_thread.start()

app.mainloop()

	
pa.terminate()
print('Done...')



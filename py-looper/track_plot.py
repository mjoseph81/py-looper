import numpy as np
import wave
import matplotlib.pyplot as plt


def wavPlot():
       
        spf = wave.open('./track1', "r")

        # Extract Raw Audio from Wav File
        sample_freq = spf.getframerate()
        n_samples = spf.getnframes()
        signal = spf.readframes(-1)

        spf.close()
        t_audio = n_samples/sample_freq
        track1 = np.frombuffer(signal, dtype=np.int16)
        
        spf = wave.open('./track2', "r")
        signal = spf.readframes(-1)
        spf.close()
        track2 = np.frombuffer(signal, dtype=np.int16)
        
        spf = wave.open('./track3', "r")
        signal = spf.readframes(-1)
        spf.close()
        track3 = np.frombuffer(signal, dtype=np.int16)
        
        spf = wave.open('./track4', "r")
        signal = spf.readframes(-1)
        spf.close()
        track4 = np.frombuffer(signal, dtype=np.int16)
    
        #get just the left channel
        track1_l = track1[0::2]
        track2_l = track2[0::2]
        track3_l = track3[0::2]
        track4_l = track4[0::2]
        
        #get just the right channel
        track1_r = track1[1::2]
        track2_r = track2[1::2]
        track3_r = track3[1::2]
        track4_r = track4[1::2]
        
        times = np.linspace(0, t_audio, num=n_samples)
       
        fig, axs = plt.subplots(3,2)
        fig.suptitle('Audio Waveforms')
        axs[0,0].plot(times, track1_l, 'tab:blue')
        axs[0,0].plot(times, track1_r, 'tab:red')
        axs[0,0].set_title('Track 1')
        #axs[0,0].set_ylim([-30000, 30000])
       
        axs[0,1].plot(times, track2_l, 'tab:blue')
        axs[0,1].plot(times, track2_r, 'tab:red')
        axs[0,1].set_title('Track 2')
        #axs[0,1].set_ylim([-30000, 30000])
        
        axs[1,0].plot(times, track3_l, 'tab:green')
        axs[1,0].plot(times, track3_r, 'tab:orange')
        axs[1,0].set_title('Track 3')
        #axs[1,0].set_ylim([-30000, 30000])
        
        axs[1,1].plot(times, track4_l, 'tab:green')
        axs[1,1].plot(times, track4_r, 'tab:orange')
        axs[1,1].set_title('Track 4')
        #axs[1,1].set_ylim([-30000, 30000])
        
        axs[2,0].plot(times, track1_l, 'tab:blue')
        axs[2,0].plot(times, track1_r, 'tab:blue')
        axs[2,0].plot(times, track2_l, 'tab:red')
        axs[2,0].plot(times, track2_r, 'tab:red')
        axs[2,0].plot(times, track3_l, 'tab:green')
        axs[2,0].plot(times, track3_r, 'tab:green')
        axs[2,0].plot(times, track4_l, 'tab:orange')
        axs[2,0].plot(times, track4_r, 'tab:orange')
        #axs[2,0].set_ylim([-30000, 30000])
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        fig.tight_layout()
        plt.show()
        
wavPlot()
        
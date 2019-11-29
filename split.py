import numpy as np
import librosa, os, youtube_dl, sys
import soundfile as sf
import matplotlib.pyplot as plt
import speech_recognition as sr 

def downloadAudio(song_url, song_title):
    '''
    Downloading video from any site and converting it to audio of wav format by using youtube_dl
    
    song_url - url of the video 
    song_title - title of the song with witch it will be saved
    '''

    outtmpl = song_title + '.%(ext)s'                                   # adding format type to the end of the song title
    ydl_opts = {                                                        # adding options
        'format': 'bestaudio/best',                                     # format
        'outtmpl': outtmpl,                                             # to name the file
        'postprocessors': [                                             
            {'key': 'FFmpegExtractAudio','preferredcodec': 'wav',       # extracting audio from video by using ffmpeg with mentioning codec as wav and quality
             'preferredquality': '192',
            },
            {'key': 'FFmpegMetadata'},
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song_url, download=True)           # extract info of the video with options metioned anddownloading it 


def splitBySilence (audio, maxSilence=1530, silenceDur=.3):
    '''
    Spliting audio by silence

    audio - path to the audio
    maxSilence - maximum number of the sample anplitude 
    silenceDur - duration of the silence in seconds
    '''

    data, sr = librosa.load(audio, sr=16000)                        # reading file and taking samples and change sample rate to 16 kHz
    t = librosa.get_duration(y=data,sr=sr)                          # audio duration in seconds
    time = np.arange(0, t, t/len(data))                             # arange the time accroding to samples' size

    silenceP = []                                                   # list to store our points of silence begining on the audio                             
    silence = 0                                                     # variable to calculate if it is silence or not
    i = 0
    while i < len(time):
        if np.abs(data[i]*sr) < maxSilence:                       # if the amplitude of the voice is not bigger than given value
            silence += int((len(time)*.01)/(int(t)))                # starting calculating silence time by adding 0.01 second 
            if silence >= int((len(time)*silenceDur)/(int(t))):     # if it is bigger than 0.03 seconds => silence
                silenceP.append(i - silenceDur*len(time)/t)         # adding the beginning of the silence
                silence = 0                                         # after considiration that it is silince we are starting again to calculate silence point
        else:    
            silence = 0                                             # in case if this wasn't silence we begin to calculate it from 0
        i += int((len(time)*.01)/(int(t)))                          # checking each 0.01 of the second

    newSilence = []                                                 # list of the real silence point
    for j in range(len(silenceP)): 
        if j+1 == len(silenceP): break                              

        if round(silenceP[j+1]-silenceP[j],1) > (silenceDur+0.1)*len(time)/t:    # if the difference of the neighbor silence points are bigger than the silenc min+0.01 second
            if newSilence:                                                       # Then it was actually not the silence     
                if newSilence[len(newSilence)-1] == silenceP[j]:                 # In case if the beginning of the silence equal to the end of the previous silence part                 
                    newSilence.remove(silenceP[j])
                    newSilence.append(silenceP[j+1])
                else:
                    newSilence.append(silenceP[j])
                    newSilence.append(silenceP[j+1])
            else:
                newSilence.append(silenceP[j])
                newSilence.append(silenceP[j+1])
    
    dividedData, durations = [], []
    j = 0
    while j < len(newSilence):
        if j+1 != len(newSilence): 
            print (int(newSilence[j]),int(newSilence[j+1]))
            durations.append((newSilence[j+1]-newSilence[j])*t/len(time))              # adding to the list of the durations of non-silent parts
            dividedData.append(data [int(newSilence[j]):int(newSilence[j+1]+6000)])    # completeng list of the new data of samples
        j+=2


    return dividedData, durations, sr

def plotAudio(audioName):
    '''
    Plotting the audio on the graph
    '''
    data, sr = librosa.load(audioName+'.wav', sr=16000)
    t = librosa.get_duration(y=data,sr=sr)
    time = np.arange(0, t, t/len(data)) 
    plt.plot(time,np.abs(data[:]*sr))
    plt.title('Voice amplitudes along the time')
    plt.show()



if len(sys.argv) < 2:
    print ('Error: Wrong usage\nUsage: python3 split.py {url_of_the_video}')  
    sys.exit()

link = str(sys.argv[1])          # link of the video
if '=' in link:
    sep = '='
else:
    sep = '/'
splited = link.rsplit(sep)    
audioName = splited[len(splited)-1]

downloadAudio(link,audioName)
plot = input("Type 1 for plotting audio, anything else if you don't want:")
if plot == 1:
    plotAudio(audioName)

# Creating and change directory to the new one for saving non-silent audio chunks
try: 
    os.mkdir(audioName) 
except(FileExistsError): 
    pass
os.chdir(audioName)

r = sr.Recognizer() # creating recognizer of the voice

k = 0

divided, durations, s = splitBySilence('../'+audioName+'.wav')
check = int(input("Type 1 if you want to check also if there is a voice in the audio chunk, anything else if you don't want :"))
for i in range(len(divided)):
    name = splited[len(splited)-1]+'_' + str(k)+'.wav'          # naming audio chunk
    sf.write(name, divided[i],s,subtype='PCM_16')               # write it first and changing bit rate
    k+=1
    # this part is not fully right as it is cheking only for azeri speech in audio
    if check == 1:
        print('Checking for voice:', name)
        if durations[i] < 65.:
            AUDIO_FILE = (name)
            with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source)                            # recording audio
            try: 
                r.recognize_google(audio, language='az-AZ')         # recognizing speech there
            except sr.UnknownValueError: 
                print("Google Speech Recognition could not understand audio")       # in case if we couldn't recognize speech
                k-=1 
                os.remove(name)                                                     # we delete it
            except sr.RequestError as e: 
                print("Could not request results from Google Speech Recognition service; {0}".format(e))




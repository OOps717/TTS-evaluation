from scipy.io import wavfile
from pesq import pesq

rate, ref = wavfile.read("./audios/real-2.wav")
rate, deg = wavfile.read("./audios/synt-2.wav")

print(pesq(rate, ref, deg, 'wb'))
print(pesq(rate, ref, deg, 'nb'))
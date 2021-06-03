from python_speech_features.base import mfcc
from python_speech_features.base import delta
from python_speech_features import logfbank
import scipy.io.wavfile as wav
import numpy as np

def compute_mfcc(wav_path, winstep=0.01):

    (rate,sig) = wav.read(wav_path)

    mfcc_feat = mfcc(
        signal=sig,
        samplerate=rate,
        appendEnergy=True,
        winstep=winstep)
    # Deltas
    d_mfcc_feat = delta(mfcc_feat, 2)
    # Deltas-Deltas
    dd_mfcc_feat = delta(d_mfcc_feat, 2)
    # transpose
    mfcc_feat = np.transpose(mfcc_feat)
    d_mfcc_feat = np.transpose(d_mfcc_feat)
    dd_mfcc_feat = np.transpose(dd_mfcc_feat)
    # concat above three features
    concat_mfcc_feat = np.concatenate(
        (mfcc_feat, d_mfcc_feat, dd_mfcc_feat))
    return concat_mfcc_feat


def mcd(C, C_hat):
    """C and C_hat are NumPy arrays of shape (T, D),
    representing mel-cepstral coefficients.

    """
    K = 10 / np.log(10) * np.sqrt(2)
    return K * np.mean(np.sqrt(np.sum((C - C_hat) ** 2, axis=1)))


coef_real = np.transpose(compute_mfcc("./audios/real-2.wav", winstep=0.02))
coef_synt = np.transpose(compute_mfcc("./audios/synt-2.wav"))

print(len(coef_real))
# print(mcd(coef_real,coef_synt))
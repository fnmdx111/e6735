import librosa
import numpy as np


# array([[  2.576e-03 -0.000e+00j,   4.327e-02 -0.000e+00j, ...,
# 3.189e-04 -0.000e+00j,  -5.961e-06 -0.000e+00j],
# [  2.441e-03 +2.884e-19j,   5.145e-02 -5.076e-03j, ...,
# -3.885e-04 -7.253e-05j,   7.334e-05 +3.868e-04j],
# ...,
# [ -7.120e-06 -1.029e-19j,  -1.951e-09 -3.568e-06j, ...,
# -4.912e-07 -1.487e-07j,   4.438e-06 -1.448e-05j],
# [  7.136e-06 -0.000e+00j,   3.561e-06 -0.000e+00j, ...,
# -5.144e-07 -0.000e+00j,  -1.514e-05 -0.000e+00j]], dtype=complex64)

# Use left-aligned frames, instead of centered frames


# Display a spectrogram
def toFreqBin(audio, framerate, samplerate):
    print(np.shape(audio))
    hopSize = (int)(samplerate / framerate)
    winSize = hopSize*2
    print(samplerate)
    freq, D = librosa.ifgram(audio, n_fft=winSize, sr=samplerate, hop_length=hopSize)
    print(np.shape(D))
    t = len(freq[0])
    re = np.zeros((t, 6))
    for i in range(len(freq)):
        for j in range(len(freq[i])):
            if (freq[i,j] <= 32):
                re[j, 0] += np.abs(D[i,j])
            elif (freq[i,j] <= 512 ):
                re[j, 1] += np.abs(D[i,j])
            elif (freq[i,j] <= 2048 ):
                re[j, 2] += np.abs(D[i,j])
            elif (freq[i,j] <= 8192 ):
                re[j, 3] += np.abs(D[i,j])
            elif (freq[i,j] <= 16384 ):
                re[j, 4] += np.abs(D[i,j])
            else:
                re[j, 5] += np.abs(D[i,j])

    return re


def loadAudio(path):
    return librosa.load(path)



import librosa
import numpy as np
cimport numpy as np
cimport cython

ctypedef np.float64_t FDTYPE
ctypedef np.complex64_t DDTYPE

def toFreqBin(audio, int framerate, int samplerate):
    cdef int hopSize = samplerate // framerate
    cdef int winSize = hopSize * 2
    print('hop: %d; win: %d' % (hopSize, winSize))

    freq, D = librosa.ifgram(audio,
                             n_fft=winSize,
                             sr=samplerate,
                             hop_length=hopSize)

    return count_bins(freq, D)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef count_bins(np.ndarray[FDTYPE, ndim=2] freq,
                np.ndarray[DDTYPE, ndim=2] D):
    cdef int _t = freq.shape[0], t = freq.shape[1]
    cdef int i, j

    cdef double f = 0.0
    cdef np.ndarray[FDTYPE, ndim=2] re = np.zeros((t, 6))

    for i in range(_t):
        for j in range(t):
            f = freq[i, j]
            if f <= 32:
                re[j, 0] += np.abs(D[i, j])
            elif f <= 512:
                re[j, 1] += np.abs(D[i, j])
            elif f <= 2048:
                re[j, 2] += np.abs(D[i, j])
            elif f <= 8192:
                re[j, 3] += np.abs(D[i, j])
            elif f <= 16384:
                re[j, 4] += np.abs(D[i, j])
            else:
                re[j, 5] += np.abs(D[i, j])

    return re

#cython: nonecheck=False
#cython: boundscheck=False
import numpy as np
cimport numpy as np

cimport cython

import cv2

ctypedef np.float32_t FDTYPE
ctypedef np.uint8_t UI8TYPE

cdef np.ndarray[FDTYPE, ndim=3] generateRGBHist(np.ndarray[UI8TYPE, ndim=3] frame,
                     int binX, int binY, int binZ):
    hist = cv2.calcHist([frame], [0, 1, 2], None,
                        [binX, binY, binZ],
                        [0, 256, 0, 256, 0, 256])
    return hist.flatten()

cdef np.ndarray[FDTYPE, ndim=3] generateHSVHist(np.ndarray[UI8TYPE, ndim=3] frame,
                     int binX, int binY, int binZ):
    hsvImg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsvImg], [0, 1, 2], None,
                        [binX, binY, binZ],
                        [0, 180, 0, 256, 0, 256])
    return hist.flatten()

cpdef generateFeature(filename,
                      int time_length, int segmentNum,
                      int framePerSegment,
                      int binX, int binY, int binZ,
                      int HistType=1):
    vidcap = cv2.VideoCapture(filename)
    if not vidcap.isOpened():
        print('could not open')
        return

    cdef list histSum = []
    cdef double fps = vidcap.get(cv2.CAP_PROP_FPS)
    cdef int length = min(int(time_length * fps),
                          vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    if length < segmentNum:
        print('Error! The number of frames is less than segment number.')
        return

    segment_length = length / segmentNum
    if segment_length < framePerSegment:
        framePerSegment = segment_length
    spacing = segment_length / framePerSegment

    cdef int num = 1
    cdef np.ndarray[FDTYPE, ndim=1] hist = np.zeros(binX * binY * binZ,
                                                    dtype=np.float32)
    cdef int count = 0
    cdef np.ndarray[UI8TYPE, ndim=3] image
    success, image = vidcap.read()

    while success and length > int(count * spacing):
        if segment_length * num <= count * spacing:
            hist /= framePerSegment
            histSum.append(hist)

            num += 1

            if HistType == 0:
                hist = generateRGBHist(image, binX, binY, binZ)
            elif HistType == 1:
                hist = generateHSVHist(image, binX, binY, binZ)
            hist /= np.sum(hist)
        else:
            if HistType == 0:
                tmp = generateRGBHist(image, binX, binY, binZ)
            elif HistType == 1:
                tmp = generateHSVHist(image, binX, binY, binZ)
            tmp /= np.sum(tmp)
            hist += tmp

        count += 1
        start = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        while start < int(count * spacing):
            _ = vidcap.read()
            start += 1

        success, image = vidcap.read()

    hist /= framePerSegment
    histSum.append(hist)

    return np.array(histSum)


def generateAMatrix(binX, binY, binZ):
    cdef int mmm = binX * binY * binZ
    cdef np.ndarray[FDTYPE, ndim=2] A = np.zeros((mmm, mmm))
    cdef np.ndarray[FDTYPE, ndim=1] h = np.zeros((0, mmm))
    cdef np.ndarray[FDTYPE, ndim=1] s = np.zeros((0, mmm))
    cdef np.ndarray[FDTYPE, ndim=1] v = np.zeros((0, mmm))

    cdef int yz
    for i in range(mmm):
        yz = binY * binZ
        h[i] = (i / yz + 0.5) * 2 * np.math.pi / binX
        s[i] = ((i % yz) / binZ + 0.5) / binY
        v[i] = (i % binZ + 0.5) / binZ

    cdef double very_long_expr
    for i in range(mmm):
        for j in range(i, mmm):
            very_long_expr = (
                (v[i] - v[j]) ** 2
                + (s[i] * np.math.cos(h[i]) - s[j] * np.math.cos(h[j])) ** 2
                + (s[i] * np.math.sin(h[i]) - s[j] * np.math.sin(h[j])) ** 2
            )
            A[i, j] = 1 - 1 / np.math.sqrt(5) * np.math.sqrt(very_long_expr)
            A[j, i] = A[i, j]

    return A


def generateSample(k, binX, binY, binZ):
    s = np.random.uniform(0, 1, (binX * binY * binZ, k))
    ss = np.sum(s, axis=0)
    s /= ss
    return s


def generateFeature2(filename, time_length, segmentNum, framePerSegment,
                     k=64, binX=18, binY=3, binZ=3, beta=50):
    pass

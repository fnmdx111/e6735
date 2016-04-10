import cv2
import numpy as np
import math

def generateRGBHist(frame, binX, binY, binZ):
    hist = cv2.calcHist([frame],[0,1,2],None,[binX,binY,binZ],[0,255, 0, 255, 0, 255])
    return hist.flatten()

def generateHSVHist(frame, binX, binY, binZ):
    hsvImg = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsvImg],[0,1,2],None,[binX,binY,binZ],[0,180, 0, 255, 0, 255])
    return hist.flatten()

def generateFeature(filename, segmentNum, HistType, binX, binY, binZ):
    vidcap = cv2.VideoCapture(filename)
    if not vidcap.isOpened(): 
        print("could not open :",fn)
        return

    histSum = np.array([]).reshape(0, binX * binY * binZ)
    length = vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    segment_length = length / segmentNum
    num = 1

    hist = np.zeros((1, binX * binY * binZ))
    start = 0
    success,image = vidcap.read()
    count = 0
    
    while (success) :
        if (segment_length * num < count) :
            hist = hist / (count - start)
            histSum = np.vstack((histSum, hist))

            start = count
            num = num + 1

            if HistType == 0 :
                hist = generateRGBHist(image, binX, binY, binZ)
            else :
                if HistType == 1 :
                    hist = generateHSVHist(image, binX, binY, binZ)
            hist = hist / np.sum(hist)
        else :
            if HistType == 0 :
                tmp = generateRGBHist(image, binX, binY, binZ)
            else :
                if HistType == 1 :
                    tmp = generateHSVHist(image, binX, binY, binZ)
            tmp = tmp / np.sum(tmp)
            hist = hist + tmp
            
        success,image = vidcap.read()
        count = count + 1
    hist = hist / (count - start)
    histSum = np.vstack((histSum, hist))
    return histSum

def generateAMatrix(binX, binY, binZ):
    A = np.zeros((binX * binY * binZ, binX * binY * binZ))
    h = []
    s = []
    v = []
    for i in range(binX * binY * binZ):
        h.append((i / (binY * binZ) + 0.5) * 2 * math.pi / binX)
        s.append(((i % (binY * binZ)) / binZ + 0.5) / binY)
        v.append((i % binZ + 0.5) / binZ)
    for i in range(binX * binY * binZ):
        for j in range(i, binX * binY * binZ):
            A[i,j] = 1 - 1 / math.sqrt(5) * math.sqrt((v[i] - v[j]) ** 2 \
                     + (s[i] * math.cos(h[i]) - s[j] * math.cos(h[j])) ** 2 \
                     + (s[i] * math.sin(h[i]) - s[j] * math.sin(h[j])) ** 2)
            A[j,i] = A[i,j]
    return A

def generateSample(k, binX, binY, binZ):
    s = np.random.uniform(0,1,(binX * binY * binZ, k))
    ss = np.sum(s, axis=0)
    s = s / ss
    return s

def generateFeature2(filename, segmentNum, binX, binY, binZ, k, beta):
    vidcap = cv2.VideoCapture(filename)
    if not vidcap.isOpened(): 
        print("could not open :",fn)
        return
    
    A = generateAMatrix(binX, binY, binZ)
    sample = generateSample(k, binX, binY, binZ)

    histSum = np.array([]).reshape(0,k)
    length = vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    segment_length = length / segmentNum
    num = 1

    hist = np.zeros((1, binX * binY * binZ))
    start = 0
    success,image = vidcap.read()
    count = 0
    dsum = []
    
    while (success) :
        if (segment_length * num < count) :
            hist = hist / (count - start)
            feature = np.zeros((1, k))
            for i in range(k) :
                diff = hist - sample[:,i]
                distance = np.dot(np.dot(diff,A),diff.transpose())
                dsum.append(distance)
                feature[0,i] = math.exp(- beta * distance);
            feature = feature / np.sum(feature)
            histSum = np.vstack((histSum, feature))

            start = count
            num = num + 1

            hist = generateHSVHist(image, binX, binY, binZ)
            hist = hist / np.sum(hist)
        else :
            tmp = generateHSVHist(image, binX, binY, binZ)
            tmp = tmp / np.sum(tmp)
            hist = hist + tmp

        success,image = vidcap.read()
        count = count + 1
    hist = hist / (count - start)
    
    feature = np.zeros((1, k))
    for i in range(k) :
        diff = hist - sample[:,i]
        distance = np.dot(np.dot(diff,A),diff.transpose())
        dsum.append(distance)
        feature[0,i] = math.exp(- beta * distance);
    feature = feature / np.sum(feature)
    histSum = np.vstack((histSum, feature))
    
    print(max(dsum))
    print(min(dsum))
    return histSum


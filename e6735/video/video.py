
import cv2
import numpy as np
import math

def generateRGBHist(frame, binX, binY, binZ):
    hist = cv2.calcHist([frame],[0,1,2],None,[binX,binY,binZ],[0,256, 0, 256, 0, 256])
    return hist.flatten()

def generateHSVHist(frame, binX, binY, binZ):
    hsvImg = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsvImg],[0,1,2],None,[binX,binY,binZ],[0,180, 0, 256, 0, 256])
    return hist.flatten()

def generateFeature(filename, time_length, segmentNum, framePerSegment, binX, binY, binZ, HistType = 1):
    vidcap = cv2.VideoCapture(filename)
    if not vidcap.isOpened(): 
        print ("could not open")
        return

    # histSum = np.array([]).reshape(0, binX * binY * binZ)
    histSum = []

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    length = int(time_length * fps)
    if length > vidcap.get(cv2.CAP_PROP_FRAME_COUNT):
        length = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    if length < segmentNum:
        print ("Error! The number of frames is less than segment Number.")
        return
    segment_length = length / segmentNum
    if segment_length < framePerSegment:
        framePerSegment = int(segment_length)
    spacing = segment_length / framePerSegment
        
    num = 1

    hist = np.zeros(binX * binY * binZ)
    count = 0
    success,image = vidcap.read()
    
    while success and int(length) > int(count * spacing):
        if segment_length * num <= count * spacing:
            hist /= framePerSegment
            histSum.append(hist)

            num += 1

            if HistType == 0 :
                hist = generateRGBHist(image, binX, binY, binZ)
            elif HistType == 1 :
                hist = generateHSVHist(image, binX, binY, binZ)
            hist /= np.sum(hist)
        else :
            if HistType == 0 :
                tmp = generateRGBHist(image, binX, binY, binZ)
            elif HistType == 1 :
                tmp = generateHSVHist(image, binX, binY, binZ)
            tmp /= np.sum(tmp)
            hist += tmp
        count += 1
        start = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        while start < int(count * spacing) :
            image = vidcap.read()
            start = start + 1
        # print (str(start) + "," + str(segment_length * num) + "," + str(length))
        success,image = vidcap.read()
        
    hist /= framePerSegment
    histSum.append(hist)
    return np.array(histSum, dtype=np.float64)

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

def generateFeature2(filename, time_length, segmentNum, framePerSegment, k = 64, binX =18, binY =3, binZ =3, beta = 50):
    vidcap = cv2.VideoCapture(filename)
    if not vidcap.isOpened(): 
        print ("could not open")
        return
    
    A = generateAMatrix(binX, binY, binZ)
    sample = generateSample(k, binX, binY, binZ)

    histSum = np.array([]).reshape(0,k)
    # length = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    length = int(time_length * fps)
    if length > vidcap.get(cv2.CAP_PROP_FRAME_COUNT):
        length = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    if length < segmentNum:
        print ("Error! The number of frames is less than segment Number.")
        return
    segment_length = length / segmentNum
    if segment_length < framePerSegment:
        framePerSegment = int(segment_length)
    spacing = segment_length / framePerSegment
    num = 1

    hist = np.zeros((1, binX * binY * binZ))
    count = 0
    success,image = vidcap.read()
    dsum = []
    
    while (success and int(length) > int(count * spacing)) :
        if (segment_length * num <= count * spacing) :
            hist = hist / framePerSegment
            feature = np.zeros((1, k))
            for i in range(k) :
                diff = hist - sample[:,i]
                distance = np.dot(np.dot(diff,A),diff.transpose())
                dsum.append(distance)
                feature[0,i] = math.exp(- beta * distance);
            feature = feature / np.sum(feature)
            histSum = np.vstack((histSum, feature))

            num = num + 1

            hist = generateHSVHist(image, binX, binY, binZ)
            hist = hist / np.sum(hist)
        else :
            tmp = generateHSVHist(image, binX, binY, binZ)
            tmp = tmp / np.sum(tmp)
            hist = hist + tmp
        count = count + 1
        start = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        while (start < int(count * spacing)) :
            image = vidcap.read()
            start = start + 1
        success,image = vidcap.read()
        
    hist = hist / framePerSegment    
    feature = np.zeros((1, k))
    for i in range(k) :
        diff = hist - sample[:,i]
        distance = np.dot(np.dot(diff,A),diff.transpose())
        dsum.append(distance)
        feature[0,i] = math.exp(- beta * distance);
    feature = feature / np.sum(feature)
    histSum = np.vstack((histSum, feature))
    return histSum

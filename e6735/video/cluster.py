import video
import numpy as np
import pyclust
import os

def histExtract(videodir = './', binX =18, binY =3, binZ =3, time_length = 0, segmentNum = 400, framePerSegment = 5):
    A = video.generateAMatrix(binX, binY, binZ)
    # np.save('Amatrix.npy',A)
    # np.savetxt('Amatrix.txt',A)
    hist = np.zeros((0, binX * binY * binZ))
    for file in os.listdir(videodir):
        if file.endswith(".mp4"):
            print(file)
            feature = video.generateFeature(file, time_length, segmentNum, framePerSegment, binX, binY, binZ)
            for item in feature:
                hist = np.vstack((hist, item))
    # np.savetxt('d.txt', hist)
    np.save('d.npy', hist)
    return

def generateSample(k, binX, binY, binZ):
    s = np.random.uniform(0,1,(k,binX * binY * binZ))
    ss = np.sum(s, axis=1)
    s = s / ss
    return s

def histClustering(k = 64):
    hist = np.load('d.npy')
    sample, membs, sse_total, sse_arr, n_iter = pyclust._kmedoids._kmedoids_run(hist, n_clusters=k, distance = video.distcalc, max_iter=20, tol=0.001)
    # np.savetxt('centers.txt', sample)
    # np.savetxt('membs.txt', membs)
    np.save('centers', sample)
    #sample = generateSample(k, binX, binY, binZ)
    #np.save('cluster.npy',sample)

    
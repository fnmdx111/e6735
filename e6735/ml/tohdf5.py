import h5py
import numpy as np
from subprocess import call
caffelocation = "D:\\CG\\caffe-windows\\Build\\x64\\Release\\caffe"
solverlocation = "D:\\CG\\e6735\\e6735\\ml\\solver.prototxt"
modellocation = "D:\\CG\\e6735\\e6735\ml\\lenet_train_test.prototxt"
def h5pyout(features, labels, path):
    s = np.shape(features)
    features = np.reshape(features, (s[0], 1, s[1], s[2]))
    print(np.shape(features))
    s = np.shape(labels)
    labels = np.reshape(labels, (s[0], 1, 1, s[1]))
    f = h5py.File(path, 'w')
    f.create_dataset('data',np.shape(features), dtype='f8')
    f.create_dataset('label', np.shape(labels), dtype='f8')

    for i in range(len(features)):
        f['data'][i] = features[i]
        f['label'][i] = labels[i]
    f.close()

def clean():
    r = call("del f:\\labelout*", shell=True)

def trainFirstTime():
    r = call(caffelocation +" train -solver " + solverlocation, shell=True)
def train(modelpath):
    r = call(caffelocation+" train -solver "+ solverlocation +" -weights " + modelpath, shell=True)
def saveModel(path):
    r = call("move f:\\lenet_iter_2000.caffemodel " + path, shell=True)
def getScore(trainedModelPath, labelShape):
    r = call(caffelocation + " test -solver " + solverlocation + " -weights " + trainedModelPath,
             shell=True)
    f = h5py.File("f:\\labelout49", 'r')
    re =  np.reshape(f["data"][0], labelShape)
    f.close()
    clean()
    return re
# from e6735.audio import audioAna as au
# a,sr = au.loadAudio("F:\\MUSIC\\Dabin,Bijou - Awakening(Original Mix).mp3")
# fbin = au.toFreqBin(a, 10, sr)
# features = []
# fbin = fbin[0:500]
# features.append(fbin)
# a,sr = au.loadAudio("F:\\MUSIC\\Shandy Kubota - Anno.mp3")
# fbin = au.toFreqBin(a, 10, sr)
# fbin = fbin[0:500]
# features.append(fbin)
# labels = []
# labels.append([0, 0,0,0 ,1,1,1,1])
# labels.append([1, 1, 1, 1, 0, 0, 0, 0])
# print(np.shape(features))
# h5pyout(features, labels, "F:\\h5fs")


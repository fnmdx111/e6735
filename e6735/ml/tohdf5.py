import h5py
import numpy as np
from subprocess import call
import os


h5path = r'F:\h5fs'
caffelocation = r"D:\CG\caffe-windows\Build\x64\Release\caffe"
solverlocation = "D:\\CG\\e6735\\e6735\\ml\\solver.prototxt"
modellocation = "D:\\CG\\e6735\\e6735\ml\\lenet_train_test.prototxt"


def h5pyout(features, labels):
    path = h5path

    s = np.shape(features)
    nfeatures = np.zeros((s[0], s[2], 1, s[1]))
    for i in range(s[0]):
        for j in range(s[2]):
            for k in range(s[1]):
                nfeatures[i][j][0][k] = features[i][k][j]
    print(np.shape(features))
    s = np.shape(labels)
    labels = np.reshape(labels, (s[0], 1, 1, s[1]))
    f = h5py.File(path, 'w')
    f.create_dataset('data',np.shape(nfeatures), dtype='f8')
    f.create_dataset('label', np.shape(labels), dtype='f8')

    for i in range(len(nfeatures)):
        f['data'][i] = nfeatures[i]
        f['label'][i] = labels[i]
    f.close()


def clean():
    r = call("del f:\\labelout*", shell=True)


def trainFirstTime():
    r = call(caffelocation +" train -solver " + solverlocation, shell=True)


def train(modelpath):
    if os.path.exists(modelpath):
        r = call(caffelocation+" train -solver "+ solverlocation +" -weights " + modelpath, shell=True)
    else:
        trainFirstTime()
        saveModel(modelpath)


def saveModel(path):
    r = call("move f:\\lenet_iter_2000.caffemodel " + path, shell=True)


def getScore(trainedModelPath, labelShape):
    print(caffelocation + " test -model " + modellocation + " -weights " + trainedModelPath)
    r = call(caffelocation + " test -model " + modellocation + " -weights " + trainedModelPath,
             shell=True)
    f = h5py.File("f:\\labelout49", 'r')
    re =  np.reshape(f["data"][0], labelShape)
    f.close()
    clean()
    return re


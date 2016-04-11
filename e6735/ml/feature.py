import numpy as np
from e6735.video import video as vi
from e6735.audio import audioAna as au
import math
from sklearn import mixture, linear_model, decomposition
from scipy import optimize
import pickle




class matchingModel:
    def __init__(self):
        self.audioBasis = None
        self.videoBasis = None

    def evaluateAudio(self, w): #w is a matrix
        return w.dot(self.audioBasis)

    def audioSquaredError(self, w, audio):
        dif = np.matrix(audio) - w.dot(self.audioBasis)
        dif = dif.dot(dif.T())
        return dif[0,0]

    def videoSquaredError(self, w, video):
        dif = np.matrix(video) - w.dot(self.videoBasis)
        dif = dif.dot(dif.T())
        return dif[0,0]

    def audioJac(self,w, audio): # n*n return
        return 2*w.T().dot(np.matrix(audio) - w.dot(self.audioBasis))

    def audioHess(self,w): #n*n
        return 2*w.T().dot(w)


class trainModelLeastError:
    def __init__(self):
        self.basis = matchingModel()
        self.features = []

    def basisError(self,inputBasis):
        self.basis.audioBasis = np.matrix(inputBasis[0])
        self.basis.videoBasis = np.matrix(inputBasis[1])
        error = 0
        for i in self.features:
            w = np.matrix(i.score)
            error += self.basis.audioSquaredError(w, i.audio)
            error += self.basis.videoSquaredError(w, i.video)
        return error

    def basisJac(self,inputBasis):
        self.basis.audioBasis = np.matrix(inputBasis[0])
        self.basis.videoBasis = np.matrix(inputBasis[1])
        jac = None
        for i in self.features:
            w = np.matrix(i.score)
            if(jac == None):
                jac = self.basis.audioJac(w,i.audio)
                #TODO video Jac
            else:
                jac += self.basis.audioJac(w,i.audio)
                #TODO video Jac
        return jac

    def basisHess(self,inputBasis):
        self.basis.audioBasis = np.matrix(inputBasis[0])
        self.basis.videoBasis = np.matrix(inputBasis[1])
        hess = None
        for i in self.features:
            w = np.matrix(i.score)
            if(hess == None):
                hess = self.basis.audioHess(w)
                #TODO video Hess
            else:
                hess += self.basis.audioHess(w)
                # TODO video Hess
        return hess

    def train(self, initBasis, maxiter):
        res = optimize.minimize(self.basisError, initBasis, method="Newton-CG",
                          jac=self.basisJac, hess=self.basisHess, options={'maxiter':maxiter,'disp': True})
        self.basis.audioBasis = res[0]
        self.basis.videoBasis = res[1]


def gmmScores(scores, classnum):
    g = mixture.GMM(n_components = classnum)
    return g.fit(scores)


def trainFeaturesLogistic(sclassifier, auFeature, auscores):
    ac = np.zeros(len(auFeature))
    for i in range(len(auscores)):
        ac[i:i + 1] = sclassifier.predict(np.array(auscores[i]).reshape((1, -1)))

    l = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
    l.fit(auFeature,ac)
    return l


def reduce(features, components):
    n = np.size(features)
    n = int(n/len(features))
    X = np.reshape(features, (len(features), n))
    pca = decomposition.PCA(components)
    pca.fit(X)
    return pca

from multiprocessing import Pool


def fileReadAu(filename):

    a, sr = au.loadAudio(filename)
    res = au.toFreqBin(a,clusterLinearModel.framerate,sr)
    res = res[0:clusterLinearModel.length]

    return res

def fileReadVi(filename):

    res = vi.generateFeature(filename,
                             math.ceil(clusterLinearModel.length/clusterLinearModel.framerate),
                             clusterLinearModel.length,
                             clusterLinearModel.frameperseg,
                             clusterLinearModel.videoBin,
                             clusterLinearModel.videoBin,
                             clusterLinearModel.videoBin)
    res = np.reshape(res, (np.size(res)))
    return res

class clusterLinearModel:
    framerate = 10
    length = 500
    videoBin = 2
    frameperseg = 1
    MIN_N_FILE_THRESHOLD = 2
    multithread = 5

    def __init__(self):
        self.la = None
        self.lv = None
        self.features = []

        self.n_files = 0

        self.n_cluster = min(20, max(self.MIN_N_FILE_THRESHOLD,
                                     self.n_files / 2))
        # must smaller than dataset

    @staticmethod
    def from_pickle(pickle_fp):
        with open(pickle_fp, 'rb') as f:
            r = clusterLinearModel()
            ret = pickle.load(f)
            r.la, r.lv = ret

            return r

    def dump(self, pickle_fp):
        with open(pickle_fp, 'wb') as f:
            pickle.dump([self.la, self.lv], f)

    def trainWithLogisticAu(self, audiofiles, auscores):
        self.n_files = len(audiofiles)
        if self.n_files < self.MIN_N_FILE_THRESHOLD:
            return [None] * len(audiofiles)

        auscores = list(auscores)

        print("loading")
        auFeature = []
        if self.multithread == 0:
            for afp in audiofiles:
                a, sr = au.loadAudio(afp)
                res = au.toFreqBin(a,self.framerate,sr)
                res = res[0:self.length]
                auFeature.append(np.reshape(res, (np.size(res))))
        else:
            if __name__ == '__main__':
                with Pool(self.multithread) as p:
                    auFeature = p.map(fileReadAu, audiofiles)

        print("classifying")

        auFeature = np.array(auFeature)

        scores = []
        scores.extend(auscores)

        classifier = gmmScores(scores,self.n_cluster)
        if len(audiofiles) >= self.MIN_N_FILE_THRESHOLD:
            self.la = trainFeaturesLogistic(classifier,auFeature, auscores)

        audioIScore = []
        if self.la is not None:
            for i in auFeature:
                audioIScore.append(self.la.predict_proba(i))

        return audioIScore
    def trainWithLogisticVi(self, videofiles, viscores):
        self.n_files = len(videofiles)
        if self.n_files < self.MIN_N_FILE_THRESHOLD:
            return  [None] * len(videofiles)

        viscores = list(viscores)

        print("loading")

        viFeature = []
        if self.multithread == 0:
            for vfp in videofiles:
                res = vi.generateFeature(vfp,
                                         math.ceil(self.length/self.framerate),
                                         self.length,
                                         self.frameperseg,
                                         self.videoBin,
                                         self.videoBin,
                                         self.videoBin)
                viFeature.append(np.reshape(res, (np.size(res))))
        else:
            if __name__ == '__main__':
                with Pool(self.multithread) as p:
                    viFeature = p.map(fileReadVi, videofiles)
        print("classifying")

        viFeature = np.array(viFeature)

        scores = []
        scores.extend(viscores)
        classifier = gmmScores(scores,self.n_cluster)
        if len(videofiles) >= self.MIN_N_FILE_THRESHOLD:
            self.lv = trainFeaturesLogistic(classifier,viFeature, viscores)
        videoIScore = []
        if self.lv is not None:
            for i in viFeature:
                videoIScore.append(self.lv.predict_proba(i))

        return videoIScore

    def scoreAudio(self, audiofile):
        if(self.la != None):
            return []
        audio, sr = au.loadAudio(audiofile)
        audioFeature = au.toFreqBin(audio,self.framerate, sr)
        audioFeature = audioFeature[0:self.length]
        audioFeature =  np.reshape(audioFeature, (np.size(audioFeature)))
        gmm = self.la.predict_proba(audioFeature)
        return gmm

    def scoreVideo(self, videoFile):
        if(self.lv != None):
            return []
        videoFeature = vi.generateFeature(videoFile,self.length,self.videoBin/3, self.videoBin/3, self.videoBin/3)
        videoFeature = np.reshape(videoFeature, (np.size(videoFeature)))
        gmm = self.la.predict_proba(videoFeature)
        return gmm
## scores psychedelic
# vibrant
# neutral
# happy
# sad
# serene
# gloomy
# energetic
# romantic
# violent
#          (.6,.0,.7,.3,.5,.6,.6,.0,.6)
# audioFiles = ["/home/voodooinnng/l.mp3", "/home/voodooinnng/z.mp3", "/home/voodooinnng/1.mp3"]
# videoFiles = []
# scores = [(.2,.2,.3,.7,.2,.2,.2,.9,.0),
#           (.7,.0,.8,.1,.3,.0,.6,.5,.2)]
#
# cl = clusterLinearModel()
# cl.trainWithLogistic(audioFiles,videoFiles,scores)
# print(cl.scoreAudio("/home/voodooinnng/1.mp3"))

import numpy as np
from e6735.video import video as vi
from e6735.audio import audioAna as au
from sklearn import mixture, linear_model, decomposition
from scipy import optimize





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


def trainFeaturesLogistic(sclassifier, auFeature, viFeature, auscores, viscores):
    l = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
    l.fit(auFeature,auscores)
    lv = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
    lv.fit(viFeature,viscores)
    return l, lv


def reduce(features, components):
    n = np.size(features)
    n = int(n/len(features))
    X = np.reshape(features, (len(features), n))
    pca = decomposition.PCA(components)
    pca.fit(X)
    return pca

class clusterLinearModel:
    def __init(self):
        self.la = None
        self.lv = None
        self.features = []
        self.framerate = 30
        self.length = 1000
        self.videoBin = 24

        self.n_cluster = 2 #must smaller than dataset

    def trainWithLogistic(self, audiofiles, videofiles, auscores, viscores):
        print("loading")
        auFeature = []
        viFeature = []
        for i in range(len(audiofiles)):
            a, sr = au.loadAudio(audiofiles[i])
            res = au.toFreqBin(a,self.framerate,sr)
            res = res[0:self.length]
            auFeature.append(np.reshape(res, (np.size(res))))
        for i in range(len(videofiles)):
            res = vi.generateFeature(i,self.length,self.videoBin/3, self.videoBin/3, self.videoBin/3)
            viFeature.append(np.reshape(res, (np.size(res))))
        print("classifying")
        scores = []
        scores.append(auscores)
        scores.append(viscores)
        classifier = gmmScores(scores,self.n_cluster)
        self.la, self.lv = trainFeaturesLogistic(classifier,auFeature, viFeature,auscores,viscores)
        audioIScore = []
        videoIScore = []
        for i in auFeature:
            audioIScore.append(self.la.predict_proba(i))
        for i in viFeature:
            videoIScore.append(self.lv.predict_proba(i))
        return audioIScore, videoIScore

    def scoreAudio(self, audiofile):
        audio, sr = au.loadAudio(audiofile)
        audioFeature = au.toFreqBin(audio,self.framerate, sr)
        audioFeature = audioFeature[0:self.length]
        audioFeature =  np.reshape(audioFeature, (np.size(audioFeature)))
        gmm = self.la.predict_proba(audioFeature)
        return gmm

    def scoreVideo(self, videoFile):
        videoFeature = vi.generateFeature(videoFile,self.length,self.videoBin/3, self.videoBin/3, self.videoBin/3)
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

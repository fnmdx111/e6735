import numpy as np
#from e6735.video import video as vi
from e6735.audio import audioAna as au
from sklearn import mixture, linear_model, decomposition
from scipy import optimize


class feature:
    score = np.zeros(10)
    audio = np.zeros((300*6))
    video = np.zeros((300*6))


class matchingModel:
    audioBasis = None
    videoBasis = None

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
        return 2*w.T().dot(np.matrix(audio) - w.dot(audioBasis))

    def audioHess(self,w): #n*n
        return 2*w.T().dot(w)


class trainModelLeastError:
    basis = matchingModel()
    features = []

    def basisError(self,inputBasis):
        basis.audioBasis = np.matrix(inputBasis[0])
        basis.videoBasis = np.matrix(inputBasis[1])
        error = 0
        for i in features:
            w = np.matrix(i.score)
            error += basis.audioSquaredError(w, audio)
            error += basis.videoSquaredError(w, video)
        return error

    def basisJac(self,inputBasis):
        basis.audioBasis = np.matrix(inputBasis[0])
        basis.videoBasis = np.matrix(inputBasis[1])
        jac = None
        for i in features:
            w = np.matrix(i.score)
            if(jac == None):
                jac = basis.audioJac(w,audio)
                #TODO video Jac
            else:
                jac += basis.audioJac(w,audio)
                #TODO video Jac
        return jac

    def basisHess(self,inputBasis):
        basis.audioBasis = np.matrix(inputBasis[0])
        basis.videoBasis = np.matrix(inputBasis[1])
        hess = None
        for i in features:
            w = np.matrix(i.score)
            if(hess == None):
                hess = basis.audioHess(w)
                #TODO video Hess
            else:
                hess += basis.audioHess(w)
                # TODO video Hess
        return hess

    def train(self, initBasis, maxiter):
        res = optimize.minimize(self.basisError, initBasis, method="Newton-CG",
                          jac=self.basisJac, hess=self.basisHess, options={'maxiter':maxiter,'disp': True})
        basis.audioBasis = res[0]
        basis.videoBasis = res[1]


def gmmScores(features, classnum):
    g = mixture.GMM(n_components = classnum)
    for i in range(len(features)):
        scores[i] = features[i].score
    return g.fit(scores)


def trainFeaturesLogistic(sclassifier, features):
    X = []
    XV = []
    Y = []
    for i in features:
        X.append(i.audio)
      #  XV.append(i.video)
        Y.append(sclassifier.predict(i.score))
    l = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
    l.fit(X,Y)
    lv = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
    #lv.fit(XV,Y)
    return l, lv


def reduce(features, components):
    a = 10
    n = np.size(features)
    n = (int)(n/len(features))
    X = np.reshape(features, (len(features), n))
    pca = decomposition.PCA(n_compnents=compnents)
    pca.fit(X)
    return pca

class clusterLinearModel:
    la = None
    lv = None
    features = []
    framerate = 30
    length = 1000
    videoBin = 24
    audioIScore = []
    videoIScore = []
    audiofiles = []
    videofiles = []

    def trainWithLogistic(self, audiofiles, videofiles,scores):
        self.audiofiles = audiofiles
        self.videofiles = videofiles
        print("loading")
        for i in range(len(scores)):
            self.features.append(feature())
            print(self.features[i])
            a, sr = au.loadAudio(audiofiles[i])
            res = au.toFreqBin(a,self.framerate,sr)
            res = res[0:self.length]
            self.features[i].audio = np.reshape(res, (np.size(res)))
            self.features[i].score = scores[i]
         #   self.features[i].video = vi.generateFeature(i,length,self.videoBin/3, self.videoBin/3, self.videoBin/3)
        print("classifying")
        classifier = gmmScores(self.features,2)
        self.la, self.lv = trainFeaturesLogistic(classifier,self.features)
        for i in self.features:
            self.audioIScore.append(self.la.predict_proba(i.audio))
        #    self.videoIScore.append(self.la.predict_proba(i.video))

    def scoreAudio(self, audiofile):
        audio, sr = au.loadAudio(audiofile)
        audioFeature = au.toFreqBin(audio,self.framerate, sr)
        audioFeature = audioFeature[0:self.length]
        audioFeature =  np.reshape(audioFeature, (np.size(audioFeature)))
        gmm = self.la.predict_proba(audioFeature)
        #TODO query with database
        auDis = []
        for i in range(len(self.features)):
            auDis.append((self.audiofiles[i], np.linalg.norm(self.audioIScore[i] - gmm)))
        sorted(auDis, key=lambda ascore:ascore[1])
        return auDis

    def scoreVideo(self, audiofile):
        audio, sr = au.loadAudio(audiofile)
        videoFeature = vi.generateFeature(i,length,self.videoBin/3, self.videoBin/3, self.videoBin/3)
        gmm = self.la.predict_proba(videoFeature)
        #TODO query with database
        viDis = []
        for i in range(len(features)):
            viDis.append((self.videofiles[i], np.linalg.norm(videoIScore[i] - gmm)))
        sorted(viDis, key=lambda ascore:ascore[1])
        return viDis
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
audioFiles = ["/home/voodooinnng/l.mp3", "/home/voodooinnng/z.mp3", "/home/voodooinnng/1.mp3"]
videoFiles = []
scores = [(.2,.2,.3,.7,.2,.2,.2,.9,.0),
          (.7,.0,.8,.1,.3,.0,.6,.5,.2)]

cl = clusterLinearModel()
cl.trainWithLogistic(audioFiles,videoFiles,scores)
print(cl.scoreAudio("/home/voodooinnng/1.mp3"))

import numpy as np
from sklearn import mixture, linear_model, decomposition
from scipy import optimize

class feature:
    score = np.zeros(10)
    audio = np.zeros((300,6))
    video = np.zeros((300,6))
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
    Y = []
    for i in features:
        X.append(i.audio)
        Y.append(sclassifier.predict(i.score))
    l = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
    l.fit(X,Y)
    return l

def reduce(features, components):
    a = 10
    n = np.size(features)
    n = (int)(n/len(features))
    X = np.reshape(features, (len(features), n))
    pca = decomposition.PCA(n_compnents=compnents)
    pca.fit(X)
    return pca



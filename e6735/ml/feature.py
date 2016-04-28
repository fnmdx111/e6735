from multiprocessing import Pool

import numpy as np
from e6735.video import video as vi
from e6735.audio import audioAna as au
import math
from sklearn import mixture, linear_model, decomposition
from scipy import optimize
import pickle
# from e6735.audio import audioAna as auc
from e6735.audio import audio_feat as auc


class matchingModel:
    def __init__(self):
        self.audioBasis = None
        self.videoBasis = None

    def evaluateAudio(self, w):  # w is a matrix
        return w.dot(self.audioBasis)

    def audioSquaredError(self, w, audio):
        dif = np.matrix(audio) - w.dot(self.audioBasis)
        dif = dif.dot(dif.T())
        return dif[0, 0]

    def videoSquaredError(self, w, video):
        dif = np.matrix(video) - w.dot(self.videoBasis)
        dif = dif.dot(dif.T())
        return dif[0, 0]

    def audioJac(self, w, audio):  # n*n return
        return 2 * w.T().dot(np.matrix(audio) - w.dot(self.audioBasis))

    def audioHess(self, w):  # n*n
        return 2 * w.T().dot(w)


class trainModelLeastError:
    def __init__(self):
        self.basis = matchingModel()
        self.features = []

    def basisError(self, inputBasis):
        self.basis.audioBasis = np.matrix(inputBasis[0])
        self.basis.videoBasis = np.matrix(inputBasis[1])
        error = 0
        for i in self.features:
            w = np.matrix(i.score)
            error += self.basis.audioSquaredError(w, i.audio)
            error += self.basis.videoSquaredError(w, i.video)
        return error

    def basisJac(self, inputBasis):
        self.basis.audioBasis = np.matrix(inputBasis[0])
        self.basis.videoBasis = np.matrix(inputBasis[1])
        jac = None
        for i in self.features:
            w = np.matrix(i.score)
            if (jac == None):
                jac = self.basis.audioJac(w, i.audio)
                # TODO video Jac
            else:
                jac += self.basis.audioJac(w, i.audio)
                # TODO video Jac
        return jac

    def basisHess(self, inputBasis):
        self.basis.audioBasis = np.matrix(inputBasis[0])
        self.basis.videoBasis = np.matrix(inputBasis[1])
        hess = None
        for i in self.features:
            w = np.matrix(i.score)
            if (hess == None):
                hess = self.basis.audioHess(w)
                # TODO video Hess
            else:
                hess += self.basis.audioHess(w)
                # TODO video Hess
        return hess

    def train(self, initBasis, maxiter):
        res = optimize.minimize(self.basisError, initBasis, method="Newton-CG",
                                jac=self.basisJac, hess=self.basisHess,
                                options={'maxiter': maxiter, 'disp': True})
        self.basis.audioBasis = res[0]
        self.basis.videoBasis = res[1]


def gmmScores(scores, classnum):
    g = mixture.GMM(n_components=classnum)
    return g.fit(scores)


def trainFeaturesLogistic(sclassifier, auFeature, auscores):
    ac = np.zeros(len(auFeature))
    s_ac = set()
    for i in range(len(auscores)):
        ac[i:i + 1] = sclassifier.predict(
            np.array(auscores[i]).reshape((1, -1)))
        s_ac.add(ac[i])

    if len(s_ac) == 0:
        return None

    l = linear_model.LogisticRegression(solver="lbfgs",
                                        multi_class="multinomial")

    l.fit(auFeature, ac)
    return ac, l


def reduce(features, components):
    n = np.size(features)
    n = int(n / len(features))
    X = np.reshape(features, (len(features), n))
    pca = decomposition.PCA(components)
    pca.fit(X)
    return pca


def __flat(xs):
    return xs.reshape(np.size(xs))


_flat = __flat


def fileReadAu(filename):
    a, sr = au.loadAudio(filename)
    res = auc.toFreqBin(a, clusterLinearModel.framerate, sr)
    res = res[0:clusterLinearModel.length]
    res = __flat(res)

    return res


def fileReadVi(filename):
    import cv2

    res = vi.generateFeature(filename,
                             math.ceil(
                                 clusterLinearModel.length /
                                 clusterLinearModel.framerate),
                             clusterLinearModel.length,
                             clusterLinearModel.frameperseg,
                             clusterLinearModel.videoBin,
                             clusterLinearModel.videoBin,
                             clusterLinearModel.videoBin)
    res = __flat(res)
    return res


class clusterLinearModel:
    framerate = 10
    length = 500
    videoBin = 2
    frameperseg = 1
    MIN_N_FILE_THRESHOLD = 2
    n_multiprocess = 0

    def __init__(self):
        self.la = None
        self.lv = None
        self.features = []

        self.audio_n_files = 0
        self.video_n_files = 0

        self.a_inv_class_idx = set()
        self.v_inv_class_idx = set()

        self.gmm_n_threshold = 2

        # must smaller than dataset

    def update_gmm_n_threshold(self, n_total):
        if n_total < 5:
            flexible_total = n_total - 1
        else:
            flexible_total = math.ceil(n_total / 2)
        self.gmm_n_threshold = min(20, max(2, flexible_total))

    @staticmethod
    def from_pickle(pickle_fp):
        with open(pickle_fp, 'rb') as f:
            r = clusterLinearModel()
            ret = pickle.load(f)
            r.audio_n_files, r.video_n_files, r.la, r.lv = ret

            return r

    def dump(self, pickle_fp):
        with open(pickle_fp, 'wb') as f:
            pickle.dump([self.audio_n_files, self.video_n_files,
                         self.la, self.lv],
                        f)

    def train(self, a_scores, audio_fps, v_scores, video_fps):
        n_total = len(audio_fps) + len(video_fps)
        self.update_gmm_n_threshold(n_total)

        if n_total < self.gmm_n_threshold:
            return [None] * len(audio_fps), [None] * len(video_fps)

        scores = a_scores + v_scores

        score_classifier = gmmScores(scores, self.gmm_n_threshold)

        if self.n_multiprocess == 0:
            a_feats = list(map(fileReadAu, audio_fps))
            v_feats = list(map(fileReadVi, video_fps))
        else:
            with Pool(self.n_multiprocess) as p:
                a_feats = p.map(fileReadAu, audio_fps)
            with Pool(self.n_multiprocess) as p:
                v_feats = p.map(fileReadVi, video_fps)

        a_ret = []
        if len(audio_fps) > 2:
            a_pscores, self.la = trainFeaturesLogistic(score_classifier,
                                                       a_feats,
                                                       a_scores)
            self.a_inv_class_idx = set(map(int, a_pscores))

            def _a(feat):
                return self.normalize(self.la.predict_proba(feat),
                                      self.a_inv_class_idx)
            a_ret.extend(map(_a, a_feats))

        v_ret = []
        if len(video_fps) > 2:
            v_pscores, self.lv = trainFeaturesLogistic(score_classifier,
                                                       v_feats,
                                                       v_scores)
            self.v_inv_class_idx = set(map(int, v_pscores))

            def _v(feat):
                return self.normalize(self.lv.predict_proba(feat),
                                      self.v_inv_class_idx)
            v_ret.extend(map(_v, v_feats))

        return a_ret or [None] * len(audio_fps), \
            v_ret or [None] * len(video_fps)

    def normalize(self, gmm, ref):
        gmm = _flat(gmm)
        ret = [0.0 for _ in range(self.gmm_n_threshold)]
        for i, idx in enumerate(ref):
            ret[idx] = gmm[i]

        return ret

    def scoreAudio(self, afp):
        if not self.la:
            return []

        af = fileReadAu(afp)
        gmm = self.la.predict_proba(af)

        return self.normalize(gmm, self.a_inv_class_idx)

    def scoreVideo(self, videoFile):
        if not self.lv:
            return []

        vf = fileReadVi(videoFile)
        gmm = self.lv.predict_proba(vf)

        return self.normalize(gmm, self.v_inv_class_idx)

# scores psychedelic
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
# audioFiles = ["/home/voodooinnng/l.mp3", "/home/voodooinnng/z.mp3",
# "/home/voodooinnng/1.mp3"]
# videoFiles = []
# scores = [(.2,.2,.3,.7,.2,.2,.2,.9,.0),
#           (.7,.0,.8,.1,.3,.0,.6,.5,.2)]
#
# cl = clusterLinearModel()
# cl.trainWithLogistic(audioFiles,videoFiles,scores)
# print(cl.scoreAudio("/home/voodooinnng/1.mp3"))

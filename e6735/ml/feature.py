import numpy as np
from sklearn import mixture, linear_model, decomposition

class feature:
    score = np.zeros(10)
    audio = np.zeros((300,6))
    video = np.zeros((300,6))

def gmmScores(features, classnum):
    g = mixture.GMM(n_components = classnum)
    for i in range(len(features)):
        scores[i] = features[i].score
    return g.fit(scores)


def trainFeatures(sclassifier, features):
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

m = np.zeros((2,2,2))
m[0] = [[1,2],[3,4]]
m[1] = [[5,6],[7,8]]
reduce(m)
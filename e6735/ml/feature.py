import numpy as np
from sklearn import mixture, linear_model

class feature:
    score = np.zeros(10)
    audio = np.zeros((1000,6))
    video = np.zeros((1000,6))

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

X = []
Y = []
for i in range(10):
    X.append([i, 10 -i])
    Y.append([1])
for i in range(10):
    X.append([i, 20 - i])
    Y.append([2])
for i in range(-10, 0):
    X.append([i, -10 -i])
    Y.append([0])
l = linear_model.LogisticRegression(solver="lbfgs", multi_class="multinomial")
l.fit(X, Y)
k= []
k.append([10,10])
print(l.predict_proba(k))
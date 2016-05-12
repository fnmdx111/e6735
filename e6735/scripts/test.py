import os
import numpy as np
from e6735.ml.tohdf5 import getScore, h5pyout
from e6735.ml.feature import fileReadAuMat, fileReadViMat
from functools import reduce


def cnn_score(folder, ext):
    if ext == 'mp4':
        mpath = 'ml/pst.bin.v'
        feat_fun = fileReadViMat
    else:
        mpath = 'ml/pst.bin.a'
        feat_fun = fileReadAuMat

    scores = {}
    for name in os.listdir(folder):
        p = os.path.join(folder, name)

        if name.endswith(ext):
            f = feat_fun(p)
            f = f.reshape((1, *f.shape))

            h5pyout(f, np.zeros((1, 8)))
            score = getScore(mpath, (1, 8))

            score = list(score.reshape(8))
            scores[name] = score

    return scores


def score_dist(s1, s2):
    ssq = reduce(lambda acc, xs: acc + abs(xs[0] - xs[1]),
                 zip(s1, s2), 0)
    return 1 - ssq / 8


if __name__ == '__main__':
    import sys

    mp4s = cnn_score(sys.argv[1], 'mp4')
    mp3s = cnn_score(sys.argv[1], 'mp3')

    from scores import a, v
    for fn in mp4s:
        scnn = mp4s[fn]
        sv = v[fn]
        print('%s: %s' % (fn, score_dist(scnn, sv)))

    for fn in mp3s:
        scnn = mp3s[fn]
        sv = a[fn]
        print('%s: %s' % (fn, score_dist(scnn, sv)))
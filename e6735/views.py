import os
import shutil
from functools import reduce
from operator import attrgetter
from tempfile import NamedTemporaryFile

from e6735.ml.tohdf5 import getScore, h5pyout, train
from .ml import feature as feat_mod

import numpy as np
from pyramid.view import view_config
from scipy.spatial import distance
from sqlalchemy.exc import IntegrityError

from e6735 import mmfp
from e6735.models import Video, Audio

import logging
L = logging.getLogger(__name__)


def score_dist(s1, s2):
    ssq = reduce(lambda acc, xs: acc + abs(xs[0] - xs[1]),
                 zip(s1, s2), 0)
    return 1 - ssq / 8


@view_config(route_name='home', renderer='templates/upload.pt')
def home(request):
    return {}


@view_config(route_name='upload', renderer='json')
def upload_new(request):
    N = int(request.POST['n'])
    L.info('Received %d upload multimedia files.', N)

    a_objs = []
    v_objs = []
    for i in range(N):
        fsrc = request.POST['file%d' % i]
        title = request.POST['title%d' % i]
        artist = request.POST['artist%d' % i]
        dims = map(float, request.POST['dims%d' % i].split(','))

        ext = 'mp4' if fsrc.type.startswith('video') else 'mp3'
        fullname = '%s - %s.%s' % (title, artist, ext)

        if ext == 'mp4':
            table = Video
        else:
            table = Audio

        cursor = request.db.query(table).\
            filter(table.title == title, table.artist == artist)

        should_add = False

        if cursor.count() == 0:
            obj = table(title, artist, ext=fsrc.type.split('/')[1])
            obj.score = tuple(dims)
            obj.feat = None
            should_add = True

            with open(mmfp(obj), 'wb') as f:
                shutil.copyfileobj(fsrc.file, f)

            if ext == 'mp4':
                feat_obj = feat_mod.fileReadViMat(mmfp(obj))
            else:
                feat_obj = feat_mod.fileReadAuMat(mmfp(obj))
            obj.feat = feat_obj

            L.info('Trying to add %s.', fullname)
            request.db.add(obj)

            (v_objs if ext == 'mp4' else a_objs).append(obj)
        else:
            obj = cursor.first()
            L.info('Updated the score of old object %s.', fullname)
            obj.score = tuple(map(lambda xs: sum(xs) / 2,
                                  zip(obj.score, dims)))
            (v_objs if ext == 'mp4' else a_objs).append(obj)

        try:
            request.db.commit()
        except IntegrityError:
            request.db.rollback()
            if should_add:
                os.remove(mmfp(obj))
            return {'status': 'failed',
                    'reason': 'database error'}

    if a_objs:
        a_feats = []
        a_scores = []
        for f in a_objs:
            a_feats.append(f.feat)
            a_scores.append(f.score)

        h5pyout(np.array(a_feats),
                np.array(a_scores))
        train(request.registry.ml_path + '.a')

    if v_objs:
        v_feats = []
        v_scores = []
        for f in v_objs:
            v_feats.append(f.feat)
            v_scores.append(f.score)

        h5pyout(np.array(v_feats),
                np.array(v_scores))
        train(request.registry.ml_path + '.v')

    return {'status': 'successful'}


def query_similar_multimedia_files(req, fp, req_type, res_type):
    db = req.db

    req_feat = (feat_mod.fileReadAuMat if req_type == 'audio' else
                feat_mod.fileReadViMat)(fp)
    req_feat = req_feat.reshape((1, *req_feat.shape))

    h5pyout(req_feat, np.zeros((1, 8)))
    if req_type == 'audio':
        score = getScore(req.registry.ml_path + '.a', (1, 8))
    else:
        score = getScore(req.registry.ml_path + '.v', (1, 8))

    score = tuple(score.reshape(8))
    res_table = Audio if res_type == 'audio' else Video
    ret = []
    for obj in db.query(res_table).all():
        obj.confidence = score_dist(obj.score, score)
        ret.append(obj)

    return sorted(ret, key=attrgetter('confidence'), reverse=True)


def open_request_file(req):
    key = 'file'
    fn = req.POST[key].filename
    f = req.POST[key].file

    return fn, f


@view_config(route_name='sos', renderer='json')
def search_by_scores(request):
    dims = tuple(map(float, request.POST['dims'].split(',')))

    objs = []
    for v in request.db.query(Video).all():
        confidence = score_dist(v.score, dims)
        v.confidence = confidence
        objs.append(v)
    for a in request.db.query(Audio).all():
        a.confidence = score_dist(a.score, dims)
        objs.append(a)

    ret = sorted(objs, key=attrgetter('confidence'), reverse=True)
    ret = ret[:20]

    return {'result': ret, 'status': 'ok',
            'resource_path': request.static_url('e6735:resources/root/'),
            'result_type': 'misc',
            'query_type': 'scores'}


@view_config(route_name='htgq', renderer='json')
def heterogeneous_query(request):
    fn, f = open_request_file(request)
    ext = fn.rsplit('.', maxsplit=1)[1]

    tmpf = NamedTemporaryFile(suffix='.' + ext, delete=False)

    shutil.copyfileobj(f, tmpf)
    tmpf.close()

    req_type = 'video' if fn.endswith('mp4') else 'audio'
    res_type = 'audio' if req_type == 'video' else 'video'
    results = query_similar_multimedia_files(request,
                                             tmpf.name,
                                             req_type, res_type)
    os.remove(tmpf.name)

    return {'result': results, 'status': 'ok',
            'resource_path': request
                .static_url('e6735:resources/%ss/' % res_type),
            'result_type': res_type,
            'query_type': 'heterogeneous'}


@view_config(route_name='hmgq', renderer='json')
def homogeneous_query(request):
    fn, f = open_request_file(request)
    ext = fn.rsplit('.', maxsplit=1)[1]

    tmpf = NamedTemporaryFile(suffix='.' + ext, delete=False)
    shutil.copyfileobj(f, tmpf)
    tmpf.close()

    req_type = 'video' if fn.endswith('mp4') else 'audio'
    res_type = 'video' if req_type == 'video' else 'audio'
    results = query_similar_multimedia_files(request,
                                             tmpf.name,
                                             req_type,
                                             res_type)

    os.remove(tmpf.name)

    return {
        'result': results, 'status': 'ok',
        'resource_path': request
            .static_url('e6735:resources/%ss/' % res_type),
        'result_type': res_type,
        'query_type': 'homogeneous'
    }


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_e6735_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


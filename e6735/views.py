import os
import random
import shutil
from operator import attrgetter
from tempfile import NamedTemporaryFile


import numpy as np
from pyramid.view import view_config
from scipy.spatial import distance
from sqlalchemy.exc import IntegrityError

from e6735 import mmfp
from e6735.models import Video, Audio


@view_config(route_name='home', renderer='templates/upload.pt')
def home(request):
    return {}


@view_config(route_name='upload', renderer='json')
def upload_new(request):
    fsrc = request.POST['file']
    title = request.POST['title']
    artist = request.POST['artist']

    dims = map(float, request.POST['dims'].split(','))

    if fsrc.type.startswith('video'):
        v = Video(title, artist, 0, 0, ext=fsrc.type.split('/')[1])
        v.score = tuple(dims)
        v.canonical_repr = None

        with open(mmfp(v), 'wb') as f:
            shutil.copyfileobj(fsrc.file, f)
            try:
                request.db.add(v)
                request.db.commit()
            except IntegrityError:
                request.db.rollback()
                os.remove(mmfp(v))
                return {'status': 'failed',
                        'reason': 'Database error.'}
    else:
        a = Audio(title, artist, ext=fsrc.type.split('/')[1])
        a.score = tuple(dims)
        a.canonical_repr = None

        with open(mmfp(a), 'wb') as f:
            shutil.copyfileobj(fsrc.file, f)
            try:
                request.db.add(a)
                request.db.commit()
            except IntegrityError:
                request.db.rollback()
                os.remove(mmfp(a))
                return {'status': 'failed',
                        'reason': 'Database error.'}

    request.registry.refit(request)

    return {'status': 'successful'}


def query_similar_multimedia_files(req, fp, ext, is_video, type_):
    db = req.db

    def append_confidence(mm):
        mm.confidence = random.random()
        return mm

    if type_ == 'htg':
        mln = req.registry.mln

        if is_video:
            gmm_score = mln.scoreVideo(fp)

            ret = []
            for audio in db.query(Audio).all():
                if audio.canonical_repr is not None:
                    audio.confidence =\
                        1 - distance.cosine(audio.canonical_repr, gmm_score)
                    ret.append(audio)
        else:
            gmm_score = mln.scoreAudio(fp)

            ret = []
            for video in db.query(Video).all():
                if video.canonical_repr is not None:
                    video.confidence =\
                        1 - distance.cosine(video.canonical_repr, gmm_score)
                    ret.append(video)
    else:
        if is_video:
            ret = map(append_confidence, db.query(Video).all())
        else:
            ret = map(append_confidence, db.query(Audio).all())

    return sorted(ret, key=attrgetter('confidence'), reverse=True)


def open_request_file(req):
    key = 'file'
    fn = req.POST[key].filename
    f = req.POST[key].file

    return fn, f


@view_config(route_name='htg-query', renderer='json')
def heterogeneous_query(request):
    fn, f = open_request_file(request)
    ext = fn.rsplit('.', maxsplit=1)[1]

    with NamedTemporaryFile(suffix='.' + ext) as tmpf:
        shutil.copyfileobj(f, tmpf)

        results = query_similar_multimedia_files(request,
                                                 tmpf.name,
                                                 ext,
                                                 fn.endswith('mp4'),
                                                 type_='htg')

        type_ = 'audio' if fn.endswith('mp4') else 'video'
        return {'result': results, 'status': 'ok',
                'resource_path': request
                    .static_url('e6735:resources/%ss/' % type_),
                'type': type_}


@view_config(route_name='hmg-query', renderer='json')
def homogeneous_query(request):
    fn, f = open_request_file(request)
    with NamedTemporaryFile() as tmpf:
        shutil.copyfileobj(f, tmpf)

        results = query_similar_multimedia_files(request.db,
                                                 tmpf.name,
                                                 fn.rsplit('.', maxsplit=1)[1],
                                                 fn.endswith('mp4'),
                                                 type_='hmg')

        type_ = 'video' if fn.endswith('mp4') else 'audio'

        return {
            'result': results, 'status': 'ok',
            'resource_path': request.static_url('e6735:resources/%ss/' % type_),
            'type': type_
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


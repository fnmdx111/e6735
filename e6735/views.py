import random
import shutil
from operator import attrgetter
from tempfile import NamedTemporaryFile

import time
from pyramid.view import view_config
from e6735.models import Video, Audio


@view_config(route_name='home', renderer='templates/upload.pt')
def home(request):
    return {}


@view_config(route_name='upload', renderer='json')
def upload_view(request):
    print(request.POST['file'],
          request.POST['dims'],
          request.POST['title'],
          request.POST['artist'])
    return {}


def query_similar_multimedia_files(db, filename, ext, is_video, type_):
    time.sleep(1)
    filename += ext

    def append_confidence(mm):
        mm.confidence = random.random()
        return mm

    if type_ == 'htg':
        if is_video:
            ret = map(append_confidence, db.query(Audio).all())
        else:
            ret = map(append_confidence, db.query(Video).all())
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

    with NamedTemporaryFile() as tmpf:
        shutil.copyfileobj(f, tmpf)

        results = query_similar_multimedia_files(request.db,
                                                 tmpf.name,
                                                 fn.rsplit('.', maxsplit=1)[1],
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


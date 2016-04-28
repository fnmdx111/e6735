import os
import shutil
from operator import attrgetter

import sys

import time
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from e6735 import ClusterLinearModel
from e6735.models import Video, Audio, Base


def train(db_session, mmfp=lambda _: _, force=True, clm=None,
          prefix=''):
    clm = clm or ClusterLinearModel()

    try:
        v_objs = db_session.query(Video).all()
        a_objs = db_session.query(Audio).all()

        if not force:
            if len(v_objs) == clm.video_n_files and \
                            len(a_objs) == clm.audio_n_files:
                return

        attr_score = attrgetter('score')

        a_gmm, v_gmm = clm.train(list(map(attr_score, a_objs)),
                                 list(map(mmfp, a_objs)),
                                 list(map(attr_score, v_objs)),
                                 list(map(mmfp, v_objs)))

        for g, o in zip(a_gmm, a_objs):
            o.canonical_repr = g
            print('Audio object %s - %s.%s: gmm = %s' % (
                o.title, o.artist, o.ext, g
            ))

        for g, o in zip(v_gmm, v_objs):
            o.canonical_repr = g
            print('Video object %s - %s.%s: gmm = %s' % (
                o.title, o.artist, o.ext, g
            ))

        db_session.commit()
        clm.dump(os.path.join(prefix, 'e6735', 'ml', 'pst.bin'))

    except IntegrityError as e:
        print(e)
        db_session.rollback()
    finally:
        db_session.close()


if __name__ == '__main__':
    prefix = ''
    if len(sys.argv) > 1:
        prefix = sys.argv[1]

    remove_sqlite = True
    if len(sys.argv) > 2:
        remove_sqlite = True if sys.argv[2] == '1' else False

    program_prefix = os.path.join('e6735', 'resources')
    if len(sys.argv) > 3:
        program_prefix = sys.argv[3]

    if remove_sqlite:
        if os.path.exists('e6735.sqlite'):
            os.remove('e6735.sqlite')
        pst = os.path.join('e6735', 'ml', 'pst.bin')
        if os.path.exists(pst):
            os.remove(pst)
        for sub in ['videos', 'audios']:
            for rp, _, fs in os.walk(os.path.join(program_prefix, sub)):
                for f in fs:
                    if not f.startswith('.'):
                        os.remove(os.path.join(rp, f))

    engine = create_engine('sqlite:///%s' % 'e6735.sqlite')
    Session = sessionmaker()
    Session.configure(bind=engine)
    if remove_sqlite:
        Base.metadata.create_all(engine)

    session = Session()

    try:
        for title, artist, score in [
            ('B4U', 'Naoki',
             [0.1, 0.9, 0.5, 0.0, 0.0, 1.0, 0.3, 0.6]),
            ('Night sky', 'USAO',
             [0.8, 0.5, 0.6, 0.2, 0.1, 0.7, 0.7, 0.3]),
            ('smooooch・∀・', 'kors k',
             [0.6, 0.6, 0.8, 0.9, 0.0, 0.5, 0.8, 0.0]),
            ('Second Heaven', 'Ryu',
             [0.3, 0.5, 0.9, 0.3, 0.0, 0.6, 0.7, 0.2])
        ]:
            audio_fp = '%s - %s.mp3' % (title, artist)
            shutil.copyfile(os.path.join(prefix, 'audios', audio_fp),
                            os.path.join(program_prefix, 'audios', audio_fp))
            a = Audio(title, artist)
            a.score = score
            session.add(a)

        for title, artist, score in [
            ('B4U', 'Naoki',
             [0.7, 0.8, 0.5, 0.2, 0.1, 1.0, 0.4, 0.6]),
            ('Night sky', 'USAO',
             [0.8, 0.4, 0.5, 0.2, 0.3, 0.6, 0.7, 0.3]),
            ('smooooch・∀・', 'kors k',
             [0.6, 0.7, 0.8, 0.9, 0.0, 0.7, 0.6, 0.0]),
            ('Second Heaven', 'Ryu',
             [0.7, 0.3, 0.3, 0.1, 0.2, 0.4, 0.7, 0.3])
        ]:
            video_fp = '%s - %s.mp4' % (title, artist)
            shutil.copyfile(os.path.join(prefix, 'videos', video_fp),
                            os.path.join(program_prefix, 'videos', video_fp))
            v = Video(title, artist, 0, 0)
            v.score = score
            session.add(v)

        session.commit()

        def mmfp(fp):
            if isinstance(fp, Audio):
                return os.path.join(program_prefix, 'audios', fp.filename())
            elif isinstance(fp, Video):
                return os.path.join(program_prefix, 'videos', fp.filename())
            raise TypeError

        t1 = time.perf_counter()
        train(session, mmfp=mmfp)
        t2 = time.perf_counter()

        print('Trained %d audios and %d videos successfully in %s seconds.' % (
            session.query(Audio).count(),
            session.query(Video).count(),
            t2 - t1
        ))
    except IntegrityError:
        session.rollback()
    finally:
        session.close()

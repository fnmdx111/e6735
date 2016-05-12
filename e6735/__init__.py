import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session
from e6735.ml import ClusterLinearModel
from e6735.models import Audio, Video

import e6735.up_config

from e6735.models import (
    DBSession,
    Base,
    )

abs_sys_path = os.getcwd()


def mmfp(mm):
    return os.path.join(abs_sys_path,
                        'e6735', 'resources',
                        'videos' if isinstance(mm, Video) else 'audios',
                        mm.filename())


def db(request):
    session = request.registry.dbmaker()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()

    request.add_finished_callback(cleanup)

    return session


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)

    config.registry.dbmaker = scoped_session(sessionmaker(bind=engine))
    config.add_request_method(db, reify=True)

    config.include('pyramid_chameleon')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('videos', up_config.resources['videos'])
    config.add_static_view('audios', up_config.resources['audios'])

    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('htgq', '/htgq')
    config.add_route('hmgq', '/hmgq')
    config.scan()

    ml_path = config.registry.settings['persistence.ml']
    config.registry.ml_path = ml_path

    # threading.Thread(target=refit_model, daemon=True).start()

    return config.make_wsgi_app()

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

import e6735.up_config

from e6735.models import (
    DBSession,
    Base,
    )


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

    config.registry.dbmaker = sessionmaker(bind=engine)
    config.add_request_method(db, reify=True)

    config.include('pyramid_chameleon')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('videos', up_config.resources['videos'])
    config.add_static_view('audios', up_config.resources['audios'])

    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('htg-query', '/htg-query')
    config.add_route('hmg-query', '/hmg-query')
    config.scan()
    return config.make_wsgi_app()

import os
import sys

import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from pyramid.scripts.common import parse_vars
from sqlalchemy import engine_from_config

from e6735.models import (
    DBSession,
    Base,
    Video,
    Audio,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)

    settings = get_appsettings(config_uri, options=options)

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        for t, a, w, h, l in [('B4U', 'Naoki', 480, 360, 100),
                     ('Night sky', 'USAO', 1280, 720, 123),
                     ('smooooch・∀・', 'kors k', 1080, 720, 117)]:
            DBSession.add(Video(t, a, w, h, l))
            DBSession.add(Audio(t, a, l))

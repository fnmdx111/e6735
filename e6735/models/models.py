from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    SmallInteger,
    PickleType
)

from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from sqlalchemy.schema import UniqueConstraint

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class MultimediaMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    _id = Column(Integer, primary_key=True)
    title = Column(Text)
    artist = Column(Text)
    length = Column(SmallInteger)
    canonical_repr = Column(PickleType)
    score = Column(PickleType)
    ext = Column(Text)

    @declared_attr
    def __table_args__(cls):
        return (UniqueConstraint('title', 'artist'),)

    def filename(self):
        return '%s - %s.%s' % (self.title, self.artist, self.ext)

    def __json__(self, req):
        return {
            'title': self.title,
            'artist': self.artist,
            'length': self.length,
            'filename': self.filename(),
            'confidence': self.confidence
        }


class Video(MultimediaMixin, Base):

    width = Column(SmallInteger)
    height = Column(SmallInteger)

    def __init__(self, title, artist, width, height, length=0, ext='mp4'):
        self.title = title
        self.artist = artist
        self.length = length
        self.width = width
        self.height = height
        self.confidence = 0.0
        self.ext = ext


class Audio(MultimediaMixin, Base):

    def __init__(self, title, artist, ext='ogg', length=0):
        self.title = title
        self.artist = artist
        self.length = length
        self.confidence = 0.0
        self.ext = ext

    def from_video(self):
        pass


Index('video_idx', Video.title, unique=True, mysql_length=255)

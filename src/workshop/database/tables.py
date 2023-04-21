from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


metadata = MetaData()

Base = declarative_base(metadata=metadata)


# Связующая таблица между таблицами video и tag
video_tag_table = Table('video_tag', Base.metadata,
    Column('video_id', Integer, ForeignKey('video.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)

    # Связь между таблицами user и channel
    channels = relationship("Channel", backref="user")

class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    # Связь между таблицами channel и video
    videos = relationship("Video", backref="channel")

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    # Связь между таблицами tag и video
    videos = relationship("Video", secondary=video_tag_table, backref="tags")

class Video(Base):
    __tablename__ = 'video'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    url = Column(String(255), nullable=False)
    upload_date = Column(String(255), nullable=False)
    views = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))

    # Связь между таблицами video и video_comment
    comments = relationship("VideoComment", backref="video")

class VideoComment(Base):
    __tablename__ = 'video_comment'

    id = Column(Integer, primary_key=True)
    text = Column(String(1000), nullable=False)
    upload_date = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    video_id = Column(Integer, ForeignKey('video.id'))

    # Связь между таблицами video_comment и comment_vote
    votes = relationship("CommentVote", backref="comment")

class CommentVote(Base):
    __tablename__ = 'comment_vote'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    comment_id = Column(Integer, ForeignKey('video_comment.id'))
    value = Column(Integer, nullable=False, default=0)
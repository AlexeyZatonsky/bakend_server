from sqlalchemy import Column, ForeignKey, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ..users.models import User
from ..videos.models import Video



comments_metadata = MetaData()

Base = declarative_base(metadata=comments_metadata)


class VideoComment(Base):
    __tablename__ = 'video_comment'

    id = Column(Integer, primary_key=True)
    text = Column(String(1000), nullable=False)
    upload_date = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id))
    video_id = Column(Integer, ForeignKey(Video.id))


class CommentVote(Base):
    __tablename__ = 'comment_vote'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    comment_id = Column(Integer, ForeignKey(VideoComment.id))
    value = Column(Integer, nullable=False, default=0)


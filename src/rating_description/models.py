from sqlalchemy import Column, ForeignKey, Integer, String, UUID
import uuid

from ..auth.models import Users
from ..videos.models import Video
from ..database import Base  # Используем единый Base

class VideoComment(Base):
    __tablename__ = 'video_comment'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    text = Column(String(1000), nullable=False)
    upload_date = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id))
    video_id = Column(UUID(as_uuid=True), ForeignKey(Video.id))


class CommentVote(Base):
    __tablename__ = 'comment_vote'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id))
    comment_id = Column(UUID(as_uuid=True), ForeignKey(VideoComment.id))
    value = Column(Integer, nullable=False, default=0)


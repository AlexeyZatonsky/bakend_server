import uuid
from datetime import datetime, UTC

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..auth.models import UsersORM
from ..videos.models import VideoORM
from ..database import Base

from ..auth.models import UsersORM
from ..courses.models import CoursesORM




#TODO: Добавление таблиц для дальнейшей проверки уникальности лайков и комментариев


#Составной ключ для комментария - пользователь может только создать и изсенить комментарий
class VideoCommentsORM(Base):
    __tablename__ = 'video_comments'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(UsersORM.id, ondelete='CASCADE'), nullable=False, primary_key=True
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(VideoORM.id, ondelete='CASCADE'), nullable=False, primary_key=True
    )

    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), nullable=False)
    


class CoursesCommentsORM(Base):
    __tablename__ = 'courses_comments'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(UsersORM.id, ondelete='CASCADE'), nullable=False, primary_key=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(CoursesORM.id, ondelete='CASCADE'), nullable=False, primary_key=True
    )

    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), nullable=False)
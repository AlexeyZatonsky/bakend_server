from pydantic import BaseModel, Field
from uuid import UUID, uuid4



class BaseVideoComment(BaseModel):
    id: UUID
    text: str = Field(max_length=1000)
    user_id: UUID
    video_id: UUID


class BaseCommentVote(BaseModel):
    id: UUID
    user_id: UUID
    comment_id: UUID
    value: int | None = 0

from pydantic import BaseModel




class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    channels: list(Channel) = []

    class Config:
        orm_mode = True




class ChannelBase(BaseModel):
    title: str

class ChannelCreate(ChannelBase):
    pass

class Channel(ChannelBase):
    id: int
    user_id: int
    videos: list(Video) = []

    class Config:
        orm_mode = True




class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True




class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    videos: list(Video) = []

    class Config:
        orm_mode = True




class VideoBase(BaseModel):
    title: str
    description: str
    url: str
    upload_date: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int
    views: int = 0
    user_id: int
    category_id: int
    channel_id: int
    comments: list(VideoComment) = []
    tags: list[Tag] = []

    class Config:
        orm_mode = True




class VideoCommentBase(BaseModel):
    text: str
    upload_date: str

class VideoCommentCreate(VideoCommentBase):
    pass

class VideoComment(VideoCommentBase):
    id: int
    user_id: int
    video_id: int
    votes: list(CommentVote) = []

    class Config:
        orm_mode = True




class CommentVoteBase(BaseModel):
    value: int

class CommentVoteCreate(CommentVoteBase):
    pass

class CommentVote(CommentVoteBase):
    id: int
    user_id: int
    comment_id: int

    class Config:
        orm_mode = True
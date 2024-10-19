from typing import Optional
from pydantic import BaseModel, Field


class PostSchema(BaseModel):
    title: str = Field(..., max_length=65)
    content: str = Field(..., max_length=255)
    completed: Optional[bool] = False


class CreatePostSchema(PostSchema):
    pass


class UpdatePostSchema(PostSchema):
    completed: bool


class ResponsePostSchema(BaseModel):
    id: int
    title: str
    content: str
    completed: bool

    class Config:
        from_attributes = True

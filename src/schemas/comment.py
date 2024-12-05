from pydantic import BaseModel, Field


class CommentSchema(BaseModel):

    description: str = Field(..., max_length=255)


class CreateCommentSchema(CommentSchema):
    pass


class UpdateCommentSchema(CommentSchema):
    pass


class ResponseCommentSchema(BaseModel):

    id: int
    description: str
    is_blocked: bool

    class Config:
        from_attributes = True

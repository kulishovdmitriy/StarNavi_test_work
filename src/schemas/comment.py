from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    """
    Represents the schema for a comment with a description field.

    Attributes:
        description (str): The content of the comment, with a maximum length of 255 characters.
    """

    description: str = Field(..., max_length=255)


class CreateCommentSchema(CommentSchema):
    pass


class UpdateCommentSchema(CommentSchema):
    pass


class ResponseCommentSchema(BaseModel):
    """
    Data model representing the schema for a response comment.

    Attributes
    ----------
    id : int
        The unique identifier for the response comment.
    description : str
        The content of the response comment.
    is_blocked : bool
        A flag indicating whether the comment is blocked.

    Config
    ------
    from_attributes : bool
        Configuration attribute to allow population of the model using attribute names.
    """

    id: int
    description: str
    is_blocked: bool

    class Config:
        from_attributes = True

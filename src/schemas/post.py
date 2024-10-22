from typing import Optional
from pydantic import BaseModel, Field


class PostSchema(BaseModel):
    """
    Represents the schema for a blog post, used for validating and defining the structure
    of a post's essential data.

    Attributes:
        title (str): The title of the post. Must be a string with a maximum length of 65 characters.
        content (str): The main content of the post. Must be a string with a maximum length of 255 characters.
        completed (Optional[bool]): Indicates if the post is completed. Defaults to False.
    """

    title: str = Field(..., max_length=65)
    content: str = Field(..., max_length=255)
    completed: Optional[bool] = False


class CreatePostSchema(PostSchema):
    pass


class UpdatePostSchema(PostSchema):
    """
    UpdatePostSchema is a class used for updating post data.

    Inherits:
        PostSchema (class): Base schema for post data.

    Attributes:
        completed (bool): Indicates whether the post is marked as completed.
    """
    completed: bool


class ResponsePostSchema(BaseModel):
    """
    ResponsePostSchema class used to define the structure of a response post.

    Attributes:
        id (int): The identifier of the post.
        title (str): The title of the post.
        content (str): The content of the post.
        completed (bool): The status indicating if the post is completed.

    Config:
        from_attributes (bool): Configuration to enable attribute parsing from input data.
    """

    id: int
    title: str
    content: str
    completed: bool

    class Config:
        from_attributes = True

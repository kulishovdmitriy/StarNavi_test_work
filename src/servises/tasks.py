import asyncio
from uuid import UUID

from src.entity.models import Comment, User, Post
from src.servises.logger import setup_logger
from src.database.db import get_database


logger = setup_logger(__name__)


async def send_auto_reply(post_id: int, comment_id: int, user_id: UUID):
    """
    Asynchronously generates and sends an auto-reply to a specific comment on a post.

    This function retrieves the user, the original comment, and the associated post from the database using their IDs.
    If all entities are found, it generates a predefined auto-reply message and creates a new comment as a reply
    to the original comment. The new comment is then added to the database, committed, and refreshed. If successful,
    it returns the generated auto-reply message. If any of the entities are not found, no action is taken.

    :param post_id: The ID of the post to which the original comment was made.
    :type post_id: int
    :param comment_id: The ID of the comment to which an auto-reply will be generated.
    :type comment_id: int
    :param user_id: The ID of the user who made the original comment.
    :type user_id: UUID
    :return: A message indicating that the auto-reply comment was generated and committed to the database.
    :rtype: str

    """

    async for session in get_database():
        user = await session.get(User, user_id)
        comment = await session.get(Comment, comment_id)
        post = await session.get(Post, post_id)

        if user and comment and post:

            generated_reply = "Thanks for the comment"

            reply_comment = Comment(
                description=generated_reply,
                post_id=post_id,
                user_id=user.id,
                parent_comment_id=comment.id
            )

            session.add(reply_comment)
            await session.commit()
            await session.refresh(reply_comment)
            logger.info("The comment was generated.")
            return generated_reply


async def send_auto_reply_after_delay(post_id: int, comment_id: int, user_id: UUID, delay_minutes: int):
    """
    Asynchronously sends an auto-reply to a specific comment on a post after a specified delay.

    This function waits for a specified amount of time (in minutes) before generating and sending an auto-reply
    to the specified comment on a post. The auto-reply is created using the `send_auto_reply` function.
    The function logs the delay and the action of creating the auto-comment.

    :param post_id: ID of the post to which the auto-reply will be sent.
    :type post_id: int
    :param comment_id: ID of the comment to which the auto-reply will be associated.
    :type comment_id: int
    :param user_id: UUID of the user for whom the auto-reply will be generated.
    :type user_id: UUID
    :param delay_minutes: Number of minutes to delay before sending the auto-reply.
    :type delay_minutes: int
    :return: None

    """

    logger.info(f"Waiting for {delay_minutes} minutes as per user settings")
    await asyncio.sleep(delay_minutes * 60)

    logger.info("Creating auto-comment:")
    await send_auto_reply(post_id, comment_id, user_id)

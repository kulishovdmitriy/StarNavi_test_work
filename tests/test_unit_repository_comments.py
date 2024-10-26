import unittest
from datetime import date # noqa
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.entity.models import Comment, User
from src.schemas.comment import CreateCommentSchema, UpdateCommentSchema
from src.repository.comments import (
    get_comments,
    get_comment_by_post,
    create_comment,
    update_comment,
    delete_comment,

)


class TestAsyncComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username="test_user")
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_comments(self):
        post_id = 1
        comment_1 = Comment(id=1, description="This is a comment", user=self.user, post_id=post_id)
        comment_2 = Comment(id=2, description="Another comment", user=self.user, post_id=post_id)

        mocked_result = MagicMock()
        mocked_result.scalars().all.return_value = [comment_1, comment_2]
        self.session.execute.return_value = mocked_result

        result = await get_comments(post_id, self.session, self.user)

        self.assertEqual(result, [comment_1, comment_2])  # Check if result is a list of comments
        self.session.execute.assert_called_once()

    async def test_get_comment_by_post(self):
        post_id = 1
        comment_id = 1
        comment = Comment(id=comment_id, description="This is a comment", user=self.user, post_id=post_id)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = comment
        self.session.execute.return_value = mocked_result

        result = await get_comment_by_post(post_id, comment_id, self.session, self.user)

        self.assertEqual(result, comment)
        self.session.execute.assert_called_once()

    async def test_create_comment(self):
        post_id = 1
        body = CreateCommentSchema(description="This is a comment")

        with patch.object(Comment, 'check_profanity', return_value=False):

            result = await create_comment(post_id, body, self.session, self.user)

            self.assertIsInstance(result, Comment)
            self.assertEqual(result.description, body.description)
            self.assertEqual(result.user, self.user)
            self.assertEqual(result.post_id, post_id)
            self.session.add.assert_called_once()
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(result)

    async def test_create_comment_with_profanity(self):
        post_id = 1
        body = CreateCommentSchema(description="forbidden_content")
        with patch.object(Comment, 'check_profanity', return_value=True):
            with self.assertRaises(HTTPException) as context:
                await create_comment(post_id, body, self.session, self.user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertEqual(context.exception.detail, "Comment contains forbidden words and is blocked.")

    async def test_create_comment_auto_reply(self):
        post_id = 1
        body = CreateCommentSchema(description="This is a comment")

        with patch.object(Comment, 'check_profanity', return_value=False):
            result = await create_comment(post_id, body, self.session, self.user)

            self.assertIsInstance(result, Comment)
            self.assertEqual(result.description, body.description)
            self.assertEqual(result.user, self.user)
            self.assertEqual(result.post_id, post_id)
            self.session.add.assert_called_once_with(result)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(result)

            # with patch('src.services.tasks.send_auto_reply_after_delay') as mock_send_auto_reply:
            #     mock_send_auto_reply.assert_called_once_with(post_id, result.id, self.user.id, self.user.reply_delay_minutes)

    async def test_create_comment_no_auto_reply(self):
        post_id = 1
        body = CreateCommentSchema(description="This is a comment")
        self.user.auto_reply_enabled = False

        with patch.object(Comment, 'check_profanity', return_value=False):
            result = await create_comment(post_id, body, self.session, self.user)

            self.assertIsInstance(result, Comment)
            self.assertEqual(result.description, body.description)
            self.assertEqual(result.user, self.user)
            self.assertEqual(result.post_id, post_id)
            self.session.add.assert_called_once_with(result)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(result)

            with patch('src.services.tasks.send_auto_reply_after_delay') as mock_send_auto_reply:
                mock_send_auto_reply.assert_not_called()

    async def test_update_comment(self):
        post_id = 1
        comment_id = 1
        body = UpdateCommentSchema(description="This is an updated comment")
        comment = Comment(id=comment_id, description="This is a comment", user=self.user, post_id=post_id)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = comment
        self.session.execute.return_value = mocked_result

        with patch.object(comment, 'check_profanity', return_value=False):
            result = await update_comment(comment_id, body, self.session, self.user)

            self.assertEqual(result, comment)
            self.assertEqual(result.description, body.description)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(comment)

    async def test_update_comment_not_found(self):
        comment_id = 1
        body = UpdateCommentSchema(description="This is an updated comment")

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None  # Комментарий не найден
        self.session.execute.return_value = mocked_result

        with self.assertRaises(HTTPException) as context:
            await update_comment(comment_id, body, self.session, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, f"Comment with id {comment_id} not found")
        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()

    async def test_update_comment_with_profanity(self):
        post_id = 1
        comment_id = 1
        body = UpdateCommentSchema(description="forbidden_content")
        comment = Comment(id=comment_id, description="This is a comment", user=self.user, post_id=post_id)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = comment
        self.session.execute.return_value = mocked_result
        with patch.object(comment, 'check_profanity', return_value=True):
            with self.assertRaises(HTTPException) as context:
                await update_comment(comment_id, body, self.session, self.user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertEqual(context.exception.detail, "Comment contains forbidden words and is blocked.")
            self.session.rollback.assert_called_once()
            self.session.commit.assert_not_called()
            self.session.refresh.assert_not_called()

    async def test_delete_comment(self):
        post_id = 1
        comment_id = 1
        comment = Comment(id=comment_id, description="This is a comment", user=self.user, post_id=post_id)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = comment
        self.session.execute.return_value = mocked_result

        result = await delete_comment(comment_id, self.session, self.user)

        self.assertEqual(result, comment)
        self.session.delete.assert_called_once_with(comment)
        self.session.commit.assert_called_once()

    async def test_delete_comment_not_found(self):
        comment_id = 1
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result

        with self.assertRaises(HTTPException) as context:
            await delete_comment(comment_id, self.session, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, f"Comment with id {comment_id} not found")
        self.session.delete.assert_not_called()

# TODO Test -> async def get_comments_daily_breakdown

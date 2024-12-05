import pytest_asyncio
from unittest.mock import patch, AsyncMock
from datetime import date
from fastapi import status

from src.conf import messages
from src.services.logger import setup_logger


logger = setup_logger(__name__)


def test_get_not_comments(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.get(f'/api/v1/comments/{post_id}', headers=headers)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data['detail'] == messages.NO_COMMENTS_FOUND.format(post_id=post_id)


def test_create_comments(client, get_token):
    token = get_token
    post_id = 1
    headers = {"Authorization": f"Bearer {token}"}
    with patch('src.entity.models.Comment.check_profanity', return_value=False):
        response = client.post(f'/api/v1/comments/{post_id}', headers=headers, json={
            "description": "test_description"
        })

        assert response.status_code == 201, response.text
        data = response.json()
        assert 'id' in data
        assert data['description'] == "test_description"
        logger.info(data['id'])


def test_get_comments(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.get(f'/api/v1/comments/{post_id}', headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_comment = data[0]
    assert 'id' in first_comment
    assert 'description' in first_comment


def test_update_comments(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    comment_id = 1
    with patch('src.entity.models.Comment.check_profanity', return_value=False):
        response = client.put(f'/api/v1/comments/{comment_id}', headers=headers, json={
            "description": "test_description2"
        })

        assert response.status_code == 202, response.text
        data = response.json()
        assert 'id' in data
        assert data['description'] == "test_description2"
        logger.info(data['id'])


def test_delete_comment(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    comment_id = 1
    post_id = 1

    response = client.delete(f'/api/v1/comments/{comment_id}/{post_id}', headers=headers)

    assert response.status_code == 204
    assert response.content == b''


def test_delete_not_comment(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    comment_id = 2
    post_id = 1

    response = client.delete(f'/api/v1/comments/{comment_id}/{post_id}', headers=headers)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data['detail'] == messages.COMMENT_NOT_FOUND_FOR_POST.format(comment_id=comment_id, post_id=post_id)


def test_comments_daily_breakdown_no_comments(client):
    date_from = date(2024, 10, 1)
    date_to = date(2024, 10, 3)

    with patch('src.repository.comments.get_comments_daily_breakdown', return_value=[]):
        response = client.get('/api/v1/comments/daily-breakdown', params={"date_from": date_from, "date_to": date_to})

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {"message": messages.NO_COMMENTS_FOR_PERIOD.format(date_from=date_from, date_to=date_to)}


@pytest_asyncio.is_async_test
async def test_comments_daily_breakdown_with_comments(client):
    date_from = date(2024, 10, 1)
    date_to = date(2024, 10, 3)

    mock_data = [
        {"date": date(2024, 10, 1), "total_comments": 2, "blocked_comments": 1},
        {"date": date(2024, 10, 2), "total_comments": 2, "blocked_comments": 0},
        {"date": date(2024, 10, 3), "total_comments": 1, "blocked_comments": 0},
    ]

    with patch('src.repository.comments.get_comments_daily_breakdown', new_callable=AsyncMock) as mock_func:
        mock_func.return_value = mock_data

        response = await client.get('/api/v1/comments/daily-breakdown',
                                    params={"date_from": date_from, "date_to": date_to})

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()

        assert len(data) == 3
        assert data[0] == {"date": date(2024, 10, 1).isoformat(), "total_comments": 2, "blocked_comments": 1}
        assert data[1] == {"date": date(2024, 10, 2).isoformat(), "total_comments": 2, "blocked_comments": 0}
        assert data[2] == {"date": date(2024, 10, 3).isoformat(), "total_comments": 1, "blocked_comments": 0}

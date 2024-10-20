import aiohttp
from src.conf.config import settings
from src.servises.logger import setup_logger


logger = setup_logger(__name__)

TOKEN_AUTH = settings.TOKEN_AUTH

BLOCK_THRESHOLD = 0.6


async def should_block_content(moderation_categories):
    for category in moderation_categories:
        if category['name'] in ['Toxic', 'Profanity', 'Sexual', 'Violent', 'Death, Harm & Tragedy']:
            if category['confidence'] > BLOCK_THRESHOLD:
                return True
    return False


async def analyze_content_post(content: str, title: str):
    token = TOKEN_AUTH
    url = "https://language.googleapis.com/v1/documents:moderateText"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    instances = [
        {"content": content},
        {"content": title}
    ]

    data = {"instances": instances}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Full response: {result}")

                    moderation_categories = result.get("moderationCategories", [])

                    if await should_block_content(moderation_categories):
                        return {"is_blocked": True}

                return {"is_blocked": False}
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return {"is_blocked": False}


async def analyze_content_comment(content: str):
    token = TOKEN_AUTH
    url = "https://language.googleapis.com/v1/documents:moderateText"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "document": {
            "type": "PLAIN_TEXT",
            "content": content
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Full response: {result}")

                    moderation_categories = result.get("moderationCategories", [])
                    if await should_block_content(moderation_categories):
                        return {"is_blocked": True}
                else:
                    error_response = await response.text()
                    logger.error(f"Error response: {error_response}")
                return {"is_blocked": False}
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return {"is_blocked": False}

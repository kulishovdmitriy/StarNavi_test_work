import aiohttp
from src.conf.config import settings
from src.services.logger import setup_logger


logger = setup_logger(__name__)

TOKEN_AUTH = settings.TOKEN_AUTH

BLOCK_THRESHOLD = 0.6


async def should_block_content(moderation_categories):
    """
    Determines whether content should be blocked based on moderation categories.

    This function evaluates a list of moderation categories, checking if any of
    them indicate content that should be blocked due to high confidence in
    harmful categories. The blocking categories include Toxic, Profanity, Sexual,
    Violent, and Death, Harm & Tragedy.

    :param moderation_categories: A list of dictionaries, where each dictionary represents
                                  a content moderation category with 'name' and 'confidence' level.
    :type moderation_categories: List[Dict[str, Union[str, float]]]

    :return: True if any moderation category exceeds the BLOCK_THRESHOLD; otherwise, False.
    :rtype: bool
    """

    for category in moderation_categories:
        if category['name'] in ['Toxic', 'Profanity', 'Sexual', 'Violent', 'Death, Harm & Tragedy']:
            if category['confidence'] > BLOCK_THRESHOLD:
                return True
    return False


async def analyze_content_post(content: str, title: str):
    """
    Analyzes the provided content and title for moderation issues.

    This function sends the content and title to an external moderation API and checks
    whether the content should be blocked based on moderation categories returned by the API.

    :param content: The main content text that needs to be analyzed for moderation.
    :type content: str
    :param title: The title associated with the main content that also needs to be analyzed.
    :type title: str
    :return: A dictionary indicating whether the content should be blocked, based on moderation analysis.
    :rtype: dict
    """

    token = TOKEN_AUTH
    url = "https://language.googleapis.com/v1/documents:moderateText"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "document": {
            "type": "PLAIN_TEXT",
            "title": title,
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

                return {"is_blocked": False}

    except aiohttp.ClientError as err:
        logger.error(f"Network error occurred: {err}")
    except Exception as err:
        logger.error(f"Error during prediction: {err}")
        return {"is_blocked": False}


async def analyze_content_comment(content: str):
    """
    Analyzes the provided content for moderation issues.

    This function sends the content to an external moderation API and checks
    whether the content should be blocked based on moderation categories returned by the API.

    :param content: The text content to be analyzed for moderation.
    :type content: str
    :return: A dictionary indicating whether the content is blocked.
             The dictionary has the key 'is_blocked' with the corresponding boolean value.
    :rtype: dict
    """

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

    except aiohttp.ClientError as err:
        logger.error(f"Network error during moderation analysis: {err}")
    except Exception as err:
        logger.error(f"Error during prediction: {err}")
        return {"is_blocked": False}

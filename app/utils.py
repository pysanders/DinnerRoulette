from flask import request
from app.config import Config


def set_user_cookie(response, username):
    """
    Set a secure user cookie on the response

    Args:
        response: Flask response object
        username (str): Username to store in cookie

    Returns:
        response: Modified response object with cookie set
    """
    response.set_cookie(
        Config.COOKIE_NAME,
        username,
        max_age=Config.COOKIE_MAX_AGE,
        httponly=Config.COOKIE_HTTPONLY,
        secure=Config.COOKIE_SECURE,
        samesite=Config.COOKIE_SAMESITE
    )
    return response


def get_user_from_cookie():
    """
    Extract username from request cookie

    Returns:
        str: Username if cookie exists, None otherwise
    """
    return request.cookies.get(Config.COOKIE_NAME)


def validate_category(category):
    """
    Validate that a category is valid

    Args:
        category (str): Category to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not category:
        return True  # Empty category is valid (means "all")
    return category in Config.VALID_CATEGORIES


def validate_restaurant_name(name):
    """
    Validate restaurant name

    Args:
        name (str): Restaurant name

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "Restaurant name is required"

    name = name.strip()
    if len(name) < 2:
        return False, "Restaurant name must be at least 2 characters"

    if len(name) > 100:
        return False, "Restaurant name must be less than 100 characters"

    return True, None


def validate_username(username):
    """
    Validate username (first name)

    Args:
        username (str): Username to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, "First name is required"

    username = username.strip()
    if len(username) < 2:
        return False, "First name must be at least 2 characters"

    if len(username) > 50:
        return False, "First name must be less than 50 characters"

    # Allow only letters, spaces, hyphens, and apostrophes
    if not all(c.isalpha() or c in " -'" for c in username):
        return False, "First name can only contain letters, spaces, hyphens, and apostrophes"

    return True, None


def create_error_response(message, code=400):
    """
    Create a standardized error response

    Args:
        message (str): Error message
        code (int): HTTP status code

    Returns:
        tuple: (response_dict, status_code)
    """
    return {
        "success": False,
        "error": message
    }, code


def create_success_response(data=None, message=None):
    """
    Create a standardized success response

    Args:
        data (dict, optional): Data to include in response
        message (str, optional): Success message

    Returns:
        dict: Response dictionary
    """
    response = {"success": True}

    if message:
        response["message"] = message

    if data:
        response.update(data)

    return response

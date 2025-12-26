from flask import Blueprint, request, jsonify, make_response
from app.models import RestaurantModel
from app.utils import (
    set_user_cookie,
    get_user_from_cookie,
    validate_category,
    validate_restaurant_name,
    validate_username,
    create_error_response,
    create_success_response
)

api = Blueprint('api', __name__, url_prefix='/api')


def get_restaurant_model():
    """Get RestaurantModel instance with current redis client"""
    from flask import current_app
    return RestaurantModel(current_app.redis)


@api.route('/user/check', methods=['GET'])
def check_user():
    """Check if user has a valid cookie"""
    username = get_user_from_cookie()

    if username:
        return jsonify(create_success_response({
            "user": username,
            "exists": True
        }))
    else:
        return jsonify({
            "success": True,
            "exists": False
        })


@api.route('/user/register', methods=['POST'])
def register_user():
    """Register a new user and set cookie"""
    data = request.get_json()

    if not data or 'first_name' not in data:
        return jsonify(create_error_response("First name is required")), 400

    first_name = data['first_name'].strip()

    # Validate username
    is_valid, error_msg = validate_username(first_name)
    if not is_valid:
        return jsonify(create_error_response(error_msg)), 400

    # Create response with cookie
    response = make_response(jsonify(create_success_response({
        "user": first_name,
        "message": f"Welcome, {first_name}!"
    })))

    set_user_cookie(response, first_name)

    return response


@api.route('/restaurants', methods=['GET'])
def get_restaurants():
    """Get all restaurants with optional category filter"""
    category = request.args.get('category', '').strip()

    # Validate category
    if category and not validate_category(category):
        return jsonify(create_error_response(
            f"Invalid category. Must be one of: quick, sit-down, nice"
        )), 400

    model = get_restaurant_model()
    restaurants = model.get_all(category=category if category else None)

    return jsonify(create_success_response({
        "restaurants": restaurants,
        "count": len(restaurants),
        "category": category if category else "all"
    }))


@api.route('/restaurants', methods=['POST'])
def add_restaurant():
    """Add a new restaurant"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    # Get request data
    data = request.get_json()

    if not data:
        return jsonify(create_error_response("Request body is required")), 400

    name = data.get('name', '').strip()
    category = data.get('category', '').strip()

    # Validate name
    is_valid, error_msg = validate_restaurant_name(name)
    if not is_valid:
        return jsonify(create_error_response(error_msg)), 400

    # Validate category
    if not category:
        return jsonify(create_error_response("Category is required")), 400

    if not validate_category(category):
        return jsonify(create_error_response(
            f"Invalid category. Must be one of: quick, sit-down, nice"
        )), 400

    # Create restaurant
    try:
        model = get_restaurant_model()
        restaurant = model.create(name, category, username)

        return jsonify(create_success_response({
            "restaurant": restaurant,
            "message": f"Added {name}!"
        })), 201

    except ValueError as e:
        return jsonify(create_error_response(str(e))), 400
    except Exception as e:
        return jsonify(create_error_response(
            "Failed to add restaurant. Please try again."
        )), 500


@api.route('/restaurants/<restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    """Soft delete a restaurant"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    # Delete restaurant
    try:
        model = get_restaurant_model()
        success = model.delete(restaurant_id, username)

        if not success:
            return jsonify(create_error_response("Restaurant not found")), 404

        return jsonify(create_success_response({
            "message": "Restaurant removed successfully"
        }))

    except Exception as e:
        return jsonify(create_error_response(
            "Failed to remove restaurant. Please try again."
        )), 500


@api.route('/randomize', methods=['GET'])
def randomize():
    """Get a random restaurant with optional category filter"""
    # Get user from cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    category = request.args.get('category', '').strip()

    # Validate category
    if category and not validate_category(category):
        return jsonify(create_error_response(
            f"Invalid category. Must be one of: quick, sit-down, nice"
        )), 400

    # Get random restaurant
    model = get_restaurant_model()
    restaurant = model.get_random(category=category if category else None)

    if not restaurant:
        return jsonify(create_error_response(
            "No restaurants available" + (f" in category '{category}'" if category else ""),
            404
        )), 404

    # Save to history and get entry ID
    entry_id = model.add_to_history(username, restaurant)

    return jsonify(create_success_response({
        "restaurant": restaurant,
        "entry_id": entry_id
    }))


@api.route('/history', methods=['GET'])
def get_history():
    """Get spin history (last 20 spins)"""
    limit = request.args.get('limit', 20, type=int)
    limit = min(max(1, limit), 50)  # Clamp between 1 and 50

    model = get_restaurant_model()
    history = model.get_history(limit=limit)

    return jsonify(create_success_response({
        "history": history,
        "count": len(history)
    }))


@api.route('/history/<entry_id>/went', methods=['POST'])
def mark_went(entry_id):
    """Mark a history entry as 'went' (user confirmed they went)"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    model = get_restaurant_model()
    success = model.mark_went(entry_id)

    if not success:
        return jsonify(create_error_response("History entry not found")), 404

    return jsonify(create_success_response({
        "message": "Marked as went!"
    }))


@api.route('/user/<username>/stats', methods=['GET'])
def get_user_stats(username):
    """Get user contribution statistics"""
    model = get_restaurant_model()
    stats = model.get_user_stats(username)

    return jsonify(create_success_response({
        "stats": stats
    }))


@api.route('/categories', methods=['GET'])
def get_categories():
    """Get available categories"""
    from app.config import Config

    return jsonify(create_success_response({
        "categories": Config.VALID_CATEGORIES
    }))

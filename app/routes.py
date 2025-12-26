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
    """Get all restaurants with optional category and distance filters"""
    category = request.args.get('category', '').strip()
    distance = request.args.get('distance', '').strip()

    model = get_restaurant_model()
    restaurants = model.get_all(
        category=category if category else None,
        distance=distance if distance else None
    )

    return jsonify(create_success_response({
        "restaurants": restaurants,
        "count": len(restaurants),
        "filters": {
            "category": category if category else "all",
            "distance": distance if distance else "all"
        }
    }))


@api.route('/restaurants', methods=['POST'])
def add_restaurant():
    """Add a new restaurant with multiple categories and distance"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    # Get request data
    data = request.get_json()

    if not data:
        return jsonify(create_error_response("Request body is required")), 400

    name = data.get('name', '').strip()
    categories = data.get('categories', [])
    distance = data.get('distance', 'nearby').strip()
    closed_days = data.get('closed_days', [])

    # Validate name
    is_valid, error_msg = validate_restaurant_name(name)
    if not is_valid:
        return jsonify(create_error_response(error_msg)), 400

    # Validate categories
    if not categories or not isinstance(categories, list):
        return jsonify(create_error_response("At least one category is required")), 400

    # Create restaurant
    try:
        model = get_restaurant_model()
        restaurant = model.create(name, categories, distance, username, closed_days)

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


@api.route('/restaurants/<restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    """Update a restaurant"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    # Get request data
    data = request.get_json()
    if not data:
        return jsonify(create_error_response("Request body is required")), 400

    name = data.get('name')
    categories = data.get('categories')
    distance = data.get('distance')
    closed_days = data.get('closed_days')

    # Validate name if provided
    if name is not None:
        is_valid, error_msg = validate_restaurant_name(name)
        if not is_valid:
            return jsonify(create_error_response(error_msg)), 400

    # Validate categories if provided
    if categories is not None and (not isinstance(categories, list) or len(categories) == 0):
        return jsonify(create_error_response("Categories must be a non-empty array")), 400

    # Update restaurant
    try:
        model = get_restaurant_model()
        restaurant = model.update(restaurant_id, name=name, categories=categories, distance=distance, closed_days=closed_days)

        if not restaurant:
            return jsonify(create_error_response("Restaurant not found")), 404

        return jsonify(create_success_response({
            "restaurant": restaurant,
            "message": "Restaurant updated successfully"
        }))

    except ValueError as e:
        return jsonify(create_error_response(str(e))), 400
    except Exception as e:
        return jsonify(create_error_response(
            "Failed to update restaurant. Please try again."
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
    """Get a random restaurant with optional category and distance filters"""
    # Get user from cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    category = request.args.get('category', '').strip()
    distance = request.args.get('distance', '').strip()

    # Get random restaurant
    model = get_restaurant_model()
    restaurant = model.get_random(
        category=category if category else None,
        distance=distance if distance else None
    )

    if not restaurant:
        filters = []
        if category:
            filters.append(f"category '{category}'")
        if distance:
            filters.append(f"distance '{distance}'")
        filter_text = " and ".join(filters) if filters else ""

        return jsonify(create_error_response(
            f"No restaurants available{' with ' + filter_text if filter_text else ''}",
            404
        )), 404

    # Save to history and get entry ID
    entry_id = model.add_to_history(username, restaurant)

    return jsonify(create_success_response({
        "restaurant": restaurant,
        "entry_id": entry_id
    }))


@api.route('/randomize/stats', methods=['GET'])
def randomize_stats():
    """Get statistics about the current randomization pool"""
    try:
        category = request.args.get('category', '').strip()
        distance = request.args.get('distance', '').strip()

        model = get_restaurant_model()
        stats = model.get_randomization_stats(
            category=category if category else None,
            distance=distance if distance else None
        )

        return jsonify(create_success_response(stats))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(create_error_response(f"Error generating stats: {str(e)}")), 500


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
    """Get all available categories (default + custom)"""
    model = get_restaurant_model()
    categories = model.get_categories()

    return jsonify(create_success_response({
        "categories": categories
    }))


@api.route('/categories', methods=['POST'])
def add_category():
    """Add a new custom category"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(create_error_response("Category name is required")), 400

    category_name = data.get('name', '').strip().lower()

    if not category_name:
        return jsonify(create_error_response("Category name cannot be empty")), 400

    if len(category_name) < 2:
        return jsonify(create_error_response("Category name must be at least 2 characters")), 400

    if len(category_name) > 30:
        return jsonify(create_error_response("Category name must be less than 30 characters")), 400

    try:
        model = get_restaurant_model()
        added = model.add_category(category_name)

        if added:
            return jsonify(create_success_response({
                "category": category_name,
                "message": f"Category '{category_name}' added successfully"
            })), 201
        else:
            return jsonify(create_error_response("Category already exists")), 400

    except Exception as e:
        return jsonify(create_error_response(
            "Failed to add category. Please try again."
        )), 500


@api.route('/distances', methods=['GET'])
def get_distances():
    """Get available distance levels"""
    from app.config import Config

    return jsonify(create_success_response({
        "distances": Config.VALID_DISTANCES,
        "default": Config.DEFAULT_DISTANCE
    }))


@api.route('/backup', methods=['POST'])
def create_backup():
    """Create a manual backup"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    try:
        model = get_restaurant_model()
        backup_file = model.backup_to_file()

        return jsonify(create_success_response({
            "backup_file": backup_file,
            "message": "Backup created successfully"
        }))

    except Exception as e:
        return jsonify(create_error_response(
            f"Failed to create backup: {str(e)}"
        )), 500


@api.route('/restore', methods=['POST'])
def restore_backup():
    """Restore from a backup file"""
    # Check user cookie
    username = get_user_from_cookie()
    if not username:
        return jsonify(create_error_response("User not registered. Please register first.")), 401

    data = request.get_json()
    if not data or 'backup_file' not in data:
        # Use latest backup if no file specified
        backup_file = "backups/restaurants_latest.json"
    else:
        backup_file = data.get('backup_file')

    try:
        model = get_restaurant_model()
        result = model.restore_from_file(backup_file)

        return jsonify(create_success_response({
            "result": result,
            "message": f"Restored {result['restaurants_restored']} restaurants and {result['categories_restored']} categories"
        }))

    except FileNotFoundError:
        return jsonify(create_error_response("Backup file not found")), 404
    except Exception as e:
        return jsonify(create_error_response(
            f"Failed to restore backup: {str(e)}"
        )), 500

import logging
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
logger = logging.getLogger(__name__)


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

    # NEW: Extract Google Places data
    place_id = data.get('place_id', '')
    phone = data.get('phone', '')
    address = data.get('address', '')
    website = data.get('website', '')
    google_distance = data.get('google_distance', '')
    eta = data.get('eta', '')

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
        restaurant = model.create(
            name, categories, distance, username, closed_days,
            place_id=place_id, phone=phone, address=address,
            website=website, google_distance=google_distance, eta=eta
        )

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

    # Extract Google Places data
    place_id = data.get('place_id')
    phone = data.get('phone')
    address = data.get('address')
    website = data.get('website')
    google_distance = data.get('google_distance')
    eta = data.get('eta')

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
        restaurant = model.update(
            restaurant_id, name=name, categories=categories, distance=distance, closed_days=closed_days,
            place_id=place_id, phone=phone, address=address, website=website,
            google_distance=google_distance, eta=eta
        )

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

    # Check rate limiting
    model = get_restaurant_model()
    can_spin, seconds_remaining = model.can_user_spin(username)
    if not can_spin:
        minutes = seconds_remaining // 60
        seconds = seconds_remaining % 60
        if minutes > 0:
            time_msg = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
        else:
            time_msg = f"{seconds}s"

        response = {
            "success": False,
            "error": f"Please wait {time_msg} before spinning again",
            "seconds_remaining": seconds_remaining
        }
        return jsonify(response), 429

    # Debug request parameters
    logger.info(f"RANDOMIZE_DEBUG: Full request URL: {request.url}")
    logger.info(f"RANDOMIZE_DEBUG: Query string: {request.query_string}")
    logger.info(f"RANDOMIZE_DEBUG: request.args: {dict(request.args)}")

    category = request.args.get('category', '').strip()
    distance = request.args.get('distance', '').strip()

    # Log the received filters
    logger.info(f"RANDOMIZE_REQUEST: user='{username}', category='{category}', distance='{distance}'")

    # Capture pool snapshot BEFORE selection (for evidence)
    pool_snapshot = model.get_randomization_stats(
        category=category if category else None,
        distance=distance if distance else None
    )
    logger.debug(f"POOL_SNAPSHOT: Captured {pool_snapshot.get('total_pool_size')} items in pool")

    # Get random restaurant
    restaurant = model.get_random(
        category=category if category else None,
        distance=distance if distance else None
    )

    # Log immediately after selection
    if restaurant:
        logger.info(f"POST_SELECT: get_random returned '{restaurant.get('name')}' (ID: {restaurant.get('id')}) for user '{username}'")

    if not restaurant:
        filters = []
        if category:
            filters.append(f"category '{category}'")
        if distance:
            filters.append(f"distance '{distance}'")
        filter_text = " and ".join(filters) if filters else ""

        logger.warning(f"No restaurants available for user {username} (filters: {filter_text})")
        return jsonify(create_error_response(
            f"No restaurants available{' with ' + filter_text if filter_text else ''}",
            404
        )), 404

    # Log the spin details BEFORE any operations
    restaurant_name = restaurant.get('name', 'Unknown')
    restaurant_id = restaurant.get('id', 'Unknown')
    logger.info(f"SPIN: User '{username}' spun and got restaurant '{restaurant_name}' (ID: {restaurant_id})")
    logger.debug(f"SPIN_DEBUG: Full restaurant object: {restaurant}")

    # Record spin time for rate limiting
    model.record_user_spin(username)

    # Save to history with filters AND pool snapshot for evidence
    entry_id = model.add_to_history(
        username,
        restaurant,
        filter_category=category if category else None,
        filter_distance=distance if distance else None,
        pool_snapshot=pool_snapshot
    )

    # Log what was ACTUALLY saved by re-checking the restaurant object
    logger.info(f"HISTORY: Added entry {entry_id} for user '{username}' - restaurant '{restaurant.get('name')}' (ID: {restaurant.get('id')}), filters=(category='{category}', distance='{distance}')")

    # Verify the restaurant object hasn't changed
    if restaurant.get('name') != restaurant_name or restaurant.get('id') != restaurant_id:
        logger.error(f"BUG DETECTED: Restaurant object changed! Was: {restaurant_name} (ID: {restaurant_id}), Now: {restaurant.get('name')} (ID: {restaurant.get('id')})")

    # Log what we're returning to the frontend
    logger.info(f"RESPONSE: Returning to frontend - restaurant '{restaurant.get('name')}' (ID: {restaurant.get('id')}), entry_id: {entry_id}")

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
        logger.exception(f"Error generating stats: {str(e)}")
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


@api.route('/config', methods=['GET'])
def get_config():
    """Get public configuration settings"""
    from app.config import Config

    return jsonify(create_success_response({
        "zip_code": Config.ZIP_CODE,
        "google_places_enabled": Config.GOOGLE_PLACES_ENABLED
    }))


@api.route('/places/search', methods=['GET'])
def search_places():
    """
    Search Google Places for restaurants
    Query param: q (search query)
    Returns: List of matching places
    """
    from app.config import Config
    from app.google_places import GooglePlacesService

    # Check if Google Places is enabled
    if not Config.GOOGLE_PLACES_ENABLED or not Config.GOOGLE_PLACES_API_KEY:
        return jsonify(create_error_response("Google Places feature is not enabled")), 400

    # Get search query
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify(create_success_response({"places": []}))

    # Search via GooglePlacesService
    try:
        service = GooglePlacesService(
            Config.GOOGLE_PLACES_API_KEY,
            Config.GOOGLE_PLACES_LOCATION,
            Config.GOOGLE_PLACES_RADIUS
        )
        places = service.search_places(query)

        return jsonify(create_success_response({
            "places": places
        }))

    except Exception as e:
        return jsonify(create_error_response(f"Search failed: {str(e)}")), 500


@api.route('/places/details/<place_id>', methods=['GET'])
def get_place_details(place_id):
    """
    Get detailed information for a specific place
    Returns: Full place details
    """
    from app.config import Config
    from app.google_places import GooglePlacesService

    # Check if enabled
    if not Config.GOOGLE_PLACES_ENABLED or not Config.GOOGLE_PLACES_API_KEY:
        return jsonify(create_error_response("Google Places feature is not enabled")), 400

    # Fetch details
    try:
        service = GooglePlacesService(
            Config.GOOGLE_PLACES_API_KEY,
            Config.GOOGLE_PLACES_LOCATION,
            Config.GOOGLE_PLACES_RADIUS
        )
        details = service.get_place_details(place_id)

        if not details:
            return jsonify(create_error_response("Place not found")), 404

        return jsonify(create_success_response({
            "place": details
        }))

    except Exception as e:
        return jsonify(create_error_response(f"Failed to fetch place details: {str(e)}")), 500


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


# =============================================================================
# Admin Endpoints (no authentication required)
# =============================================================================

@api.route('/admin/backups', methods=['GET'])
def admin_list_backups():
    """List all available backup files"""
    import os
    from app.config import Config

    backup_dir = Config.BACKUP_DIR
    backups = []

    if os.path.exists(backup_dir):
        for filename in sorted(os.listdir(backup_dir), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    "filename": filename,
                    "path": filepath,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime
                })

    return jsonify(create_success_response({
        "backup_dir": backup_dir,
        "backups": backups,
        "count": len(backups)
    }))


@api.route('/admin/restore', methods=['POST'])
def admin_restore():
    """
    Restore from a backup file (no auth required)

    POST /api/admin/restore
    Body: {"filename": "restaurants_latest.json"} or empty for latest
    """
    import os
    from app.config import Config

    data = request.get_json() or {}
    filename = data.get('filename', 'restaurants_latest.json')

    # Build full path
    backup_dir = Config.BACKUP_DIR
    backup_file = os.path.join(backup_dir, filename)

    logger.info(f"ADMIN_RESTORE: Attempting to restore from {backup_file}")

    try:
        model = get_restaurant_model()
        result = model.restore_from_file(backup_file)

        logger.info(f"ADMIN_RESTORE: Successfully restored {result['restaurants_restored']} restaurants")

        return jsonify(create_success_response({
            "result": result,
            "message": f"Restored {result['restaurants_restored']} restaurants and {result['categories_restored']} categories",
            "backup_file": backup_file
        }))

    except FileNotFoundError:
        logger.error(f"ADMIN_RESTORE: Backup file not found: {backup_file}")
        return jsonify(create_error_response(f"Backup file not found: {filename}")), 404
    except Exception as e:
        logger.exception(f"ADMIN_RESTORE: Failed to restore: {e}")
        return jsonify(create_error_response(f"Failed to restore backup: {str(e)}")), 500


@api.route('/admin/diagnose', methods=['GET'])
def admin_diagnose():
    """
    Diagnose Redis data integrity
    Shows indexes vs actual data, orphaned entries, etc.
    """
    model = get_restaurant_model()
    redis = model.redis

    # Get all IDs from index
    index_ids = redis.smembers("restaurants:index")
    index_ids = [i.decode() if isinstance(i, bytes) else i for i in index_ids]

    # Check each ID
    has_data = []
    missing_data = []

    for rid in sorted(index_ids, key=lambda x: int(x) if x.isdigit() else 0):
        data = redis.hgetall(f"restaurants:{rid}")
        if data:
            name = data.get(b'name', data.get('name', b'Unknown'))
            if isinstance(name, bytes):
                name = name.decode()
            has_data.append({"id": rid, "name": name})
        else:
            missing_data.append(rid)

    return jsonify(create_success_response({
        "index_count": len(index_ids),
        "with_data": len(has_data),
        "missing_data": len(missing_data),
        "restaurants": has_data,
        "orphaned_ids": missing_data
    }))


@api.route('/admin/fix-orphans', methods=['POST'])
def admin_fix_orphans():
    """
    Remove orphaned IDs from indexes (IDs that have no data)
    """
    model = get_restaurant_model()
    redis = model.redis

    # Get all IDs from index
    index_ids = redis.smembers("restaurants:index")
    index_ids = [i.decode() if isinstance(i, bytes) else i for i in index_ids]

    fixed = []

    for rid in index_ids:
        data = redis.hgetall(f"restaurants:{rid}")
        if not data:
            # Remove from main index
            redis.srem("restaurants:index", rid)

            # Remove from all category indexes
            for key in redis.keys("restaurants:by_category:*"):
                if isinstance(key, bytes):
                    key = key.decode()
                redis.srem(key, rid)

            # Remove from all distance indexes
            for key in redis.keys("restaurants:by_distance:*"):
                if isinstance(key, bytes):
                    key = key.decode()
                redis.srem(key, rid)

            fixed.append(rid)
            logger.info(f"ADMIN_FIX: Removed orphaned ID {rid} from indexes")

    return jsonify(create_success_response({
        "fixed_count": len(fixed),
        "fixed_ids": fixed,
        "message": f"Removed {len(fixed)} orphaned IDs from indexes"
    }))


@api.route('/admin/clear-history', methods=['POST'])
def admin_clear_history():
    """Clear all spin history"""
    model = get_restaurant_model()
    redis = model.redis

    # Get count before clearing
    count = redis.llen("spin_history")

    # Clear the history
    redis.delete("spin_history")

    logger.info(f"ADMIN: Cleared {count} history entries")

    return jsonify(create_success_response({
        "cleared_count": count,
        "message": f"Cleared {count} history entries"
    }))


@api.route('/admin/cooldowns', methods=['GET'])
def admin_list_cooldowns():
    """List all active cooldowns"""
    model = get_restaurant_model()
    redis = model.redis

    # Find all cooldown keys
    cooldown_keys = redis.keys("user:*:last_spin")
    cooldowns = []

    for key in cooldown_keys:
        if isinstance(key, bytes):
            key = key.decode()

        # Extract username from key
        username = key.replace("user:", "").replace(":last_spin", "")

        # Get the timestamp
        last_spin = redis.get(key)
        if last_spin:
            if isinstance(last_spin, bytes):
                last_spin = last_spin.decode()

            from datetime import datetime
            last_spin_time = float(last_spin)
            time_since = datetime.utcnow().timestamp() - last_spin_time
            from app.config import Config
            remaining = max(0, Config.SPIN_TIMEOUT_SECONDS - time_since)

            cooldowns.append({
                "username": username,
                "last_spin": datetime.fromtimestamp(last_spin_time).isoformat(),
                "seconds_remaining": int(remaining),
                "expired": remaining <= 0
            })

    return jsonify(create_success_response({
        "cooldowns": cooldowns,
        "count": len(cooldowns)
    }))


@api.route('/admin/clear-cooldown', methods=['POST'])
def admin_clear_cooldown():
    """Clear cooldown for a specific user or all users"""
    model = get_restaurant_model()
    redis = model.redis

    data = request.get_json() or {}
    username = data.get('username')

    if username:
        # Clear specific user
        key = f"user:{username}:last_spin"
        deleted = redis.delete(key)
        logger.info(f"ADMIN: Cleared cooldown for user '{username}'")
        return jsonify(create_success_response({
            "cleared": deleted > 0,
            "message": f"Cleared cooldown for {username}" if deleted else f"No cooldown found for {username}"
        }))
    else:
        # Clear all cooldowns
        cooldown_keys = redis.keys("user:*:last_spin")
        count = 0
        for key in cooldown_keys:
            redis.delete(key)
            count += 1

        logger.info(f"ADMIN: Cleared {count} cooldowns")
        return jsonify(create_success_response({
            "cleared_count": count,
            "message": f"Cleared {count} cooldowns"
        }))


@api.route('/admin/backup', methods=['POST'])
def admin_create_backup():
    """Create a manual backup"""
    try:
        model = get_restaurant_model()
        backup_file = model.backup_to_file()

        logger.info(f"ADMIN: Created backup at {backup_file}")

        return jsonify(create_success_response({
            "backup_file": backup_file,
            "message": "Backup created successfully"
        }))
    except Exception as e:
        logger.exception(f"ADMIN: Failed to create backup: {e}")
        return jsonify(create_error_response(f"Failed to create backup: {str(e)}")), 500


@api.route('/admin/users', methods=['GET'])
def admin_list_users():
    """List all users who have interacted with the system"""
    model = get_restaurant_model()
    redis = model.redis

    users = {}

    # Find users from various keys
    # Check cooldown keys
    for key in redis.keys("user:*:last_spin"):
        if isinstance(key, bytes):
            key = key.decode()
        username = key.replace("user:", "").replace(":last_spin", "")
        if username not in users:
            users[username] = {"username": username, "added": 0, "removed": 0, "has_cooldown": False}
        users[username]["has_cooldown"] = True

    # Check added keys
    for key in redis.keys("user:*:added"):
        if isinstance(key, bytes):
            key = key.decode()
        username = key.replace("user:", "").replace(":added", "")
        if username not in users:
            users[username] = {"username": username, "added": 0, "removed": 0, "has_cooldown": False}
        users[username]["added"] = redis.scard(key)

    # Check removed keys
    for key in redis.keys("user:*:removed"):
        if isinstance(key, bytes):
            key = key.decode()
        username = key.replace("user:", "").replace(":removed", "")
        if username not in users:
            users[username] = {"username": username, "added": 0, "removed": 0, "has_cooldown": False}
        users[username]["removed"] = redis.scard(key)

    # Also check spin history for usernames
    history = redis.lrange("spin_history", 0, -1)
    for entry_bytes in history:
        if isinstance(entry_bytes, bytes):
            entry_bytes = entry_bytes.decode()
        try:
            import json
            entry = json.loads(entry_bytes)
            username = entry.get("username")
            if username and username not in users:
                users[username] = {"username": username, "added": 0, "removed": 0, "has_cooldown": False}
        except:
            pass

    user_list = sorted(users.values(), key=lambda x: x["username"].lower())

    return jsonify(create_success_response({
        "users": user_list,
        "count": len(user_list)
    }))


@api.route('/admin/redis-info', methods=['GET'])
def admin_redis_info():
    """Get Redis connection info and stats"""
    from app.config import Config
    model = get_restaurant_model()
    redis = model.redis

    try:
        redis.ping()
        connected = True

        # Get some basic stats
        info = redis.info('memory')
        db_size = redis.dbsize()

        return jsonify(create_success_response({
            "connected": True,
            "host": Config.REDIS_HOST,
            "port": Config.REDIS_PORT,
            "db": Config.REDIS_DB,
            "db_size": db_size,
            "used_memory": info.get('used_memory_human', 'Unknown'),
            "used_memory_peak": info.get('used_memory_peak_human', 'Unknown')
        }))
    except Exception as e:
        return jsonify(create_success_response({
            "connected": False,
            "host": Config.REDIS_HOST,
            "port": Config.REDIS_PORT,
            "error": str(e)
        }))

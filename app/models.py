from datetime import datetime
import redis
from app.config import Config


class RestaurantModel:
    """Redis-based restaurant data model"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def create(self, name, categories, distance, added_by, closed_days=None):
        """
        Create a new restaurant entry

        Args:
            name (str): Restaurant name
            categories (list): List of category tags
            distance (str): Distance level (nearby, short-drive, medium-drive, far)
            added_by (str): Username who added it
            closed_days (list, optional): Days restaurant is closed (0=Sunday, 1=Monday, ..., 6=Saturday)

        Returns:
            dict: Created restaurant data with id
        """
        import json

        # Validate categories
        valid_categories = self.get_categories()
        for cat in categories:
            if cat not in valid_categories:
                raise ValueError(f"Invalid category '{cat}'. Use existing categories or add a new one.")

        # Validate distance
        if distance not in Config.VALID_DISTANCES:
            raise ValueError(f"Invalid distance. Must be one of: {Config.VALID_DISTANCES}")

        # Validate closed_days
        if closed_days is None:
            closed_days = []
        closed_days = [int(day) for day in closed_days if 0 <= int(day) <= 6]

        # Generate unique ID atomically
        restaurant_id = self.redis.incr("restaurants:counter")

        # Create restaurant hash
        restaurant_data = {
            "id": str(restaurant_id),
            "name": name,
            "categories": json.dumps(categories),  # Store as JSON array
            "distance": distance,
            "closed_days": json.dumps(closed_days),  # Store as JSON array
            "added_by": added_by,
            "added_at": datetime.utcnow().isoformat(),
            "is_active": "1"
        }

        # Store in Redis
        self.redis.hset(f"restaurants:{restaurant_id}", mapping=restaurant_data)

        # Add to indexes
        self.redis.sadd("restaurants:index", restaurant_id)
        for category in categories:
            self.redis.sadd(f"restaurants:by_category:{category}", restaurant_id)
        self.redis.sadd(f"restaurants:by_distance:{distance}", restaurant_id)
        self.redis.sadd(f"user:{added_by}:added", restaurant_id)

        # Auto-backup after create
        try:
            self.backup_to_file()
        except Exception as e:
            print(f"Backup failed: {e}")

        return self._format_restaurant(restaurant_data)

    def _format_restaurant(self, data):
        """
        Format restaurant data from Redis (convert bytes, parse JSON)

        Args:
            data (dict): Raw restaurant data from Redis

        Returns:
            dict: Formatted restaurant data
        """
        import json

        if not data:
            return None

        # Convert bytes to strings
        formatted = {k.decode('utf-8') if isinstance(k, bytes) else k:
                    v.decode('utf-8') if isinstance(v, bytes) else v
                    for k, v in data.items()}

        # Parse categories JSON if present
        if 'categories' in formatted:
            try:
                formatted['categories'] = json.loads(formatted['categories'])
            except (json.JSONDecodeError, TypeError):
                # Fallback for old single-category format
                formatted['categories'] = [formatted.get('category', 'quick')]

        # Parse closed_days JSON if present
        if 'closed_days' in formatted:
            try:
                formatted['closed_days'] = json.loads(formatted['closed_days'])
            except (json.JSONDecodeError, TypeError):
                formatted['closed_days'] = []
        else:
            formatted['closed_days'] = []

        return formatted

    def get(self, restaurant_id):
        """
        Get a single restaurant by ID

        Args:
            restaurant_id (str): Restaurant ID

        Returns:
            dict: Restaurant data or None if not found
        """
        data = self.redis.hgetall(f"restaurants:{restaurant_id}")
        return self._format_restaurant(data)

    def get_all(self, category=None, distance=None, active_only=True):
        """
        Get all restaurants, optionally filtered by category and/or distance
        Distance filter works as "max distance" - includes all closer options

        Args:
            category (str, optional): Filter by category
            distance (str, optional): Filter by max distance
            active_only (bool): Only return active restaurants (default True)

        Returns:
            list: List of restaurant dictionaries
        """
        # Define distance hierarchy (in order from closest to farthest)
        distance_hierarchy = ['nearby', 'short-drive', 'medium-drive', 'far']

        # Start with all restaurants or apply filters
        if category and distance:
            # Get all restaurants in category
            cat_ids = self.redis.smembers(f"restaurants:by_category:{category}")

            # Get all distances up to and including selected distance
            allowed_distances = distance_hierarchy[:distance_hierarchy.index(distance) + 1]
            dist_ids = set()
            for dist in allowed_distances:
                dist_ids.update(self.redis.smembers(f"restaurants:by_distance:{dist}"))

            # Intersect category with allowed distances
            ids = cat_ids.intersection(dist_ids)
        elif category:
            ids = self.redis.smembers(f"restaurants:by_category:{category}")
        elif distance:
            # Get all distances up to and including selected distance
            allowed_distances = distance_hierarchy[:distance_hierarchy.index(distance) + 1]
            dist_ids = set()
            for dist in allowed_distances:
                dist_ids.update(self.redis.smembers(f"restaurants:by_distance:{dist}"))
            ids = dist_ids
        else:
            ids = self.redis.smembers("restaurants:index")

        restaurants = []
        for rid in ids:
            # Convert bytes to string
            if isinstance(rid, bytes):
                rid = rid.decode('utf-8')

            restaurant = self.get(rid)
            if restaurant:
                # Filter by active status if requested
                if active_only and restaurant.get('is_active') != '1':
                    continue
                restaurants.append(restaurant)

        # Sort by name
        restaurants.sort(key=lambda x: x.get('name', '').lower())
        return restaurants

    def delete(self, restaurant_id, removed_by):
        """
        Soft delete a restaurant (mark as inactive)

        Args:
            restaurant_id (str): Restaurant ID to delete
            removed_by (str): Username who removed it

        Returns:
            bool: True if successful, False if not found
        """
        restaurant = self.get(restaurant_id)
        if not restaurant:
            return False

        categories = restaurant.get('categories', [])
        distance = restaurant.get('distance')

        # Mark as inactive
        self.redis.hset(f"restaurants:{restaurant_id}", "is_active", "0")

        # Track removal metadata
        self.redis.sadd(f"restaurants:{restaurant_id}:removed_by", removed_by)
        self.redis.set(f"restaurants:{restaurant_id}:removed_at", datetime.utcnow().isoformat())
        self.redis.sadd(f"user:{removed_by}:removed", restaurant_id)

        # Remove from active indexes
        self.redis.srem("restaurants:index", restaurant_id)
        for category in categories:
            self.redis.srem(f"restaurants:by_category:{category}", restaurant_id)
        if distance:
            self.redis.srem(f"restaurants:by_distance:{distance}", restaurant_id)

        # Auto-backup after delete
        try:
            self.backup_to_file()
        except Exception as e:
            print(f"Backup failed: {e}")

        return True

    def get_random(self, category=None, distance=None):
        """
        Get a random restaurant, optionally filtered by category and/or distance
        Excludes the last spin if it was within 15 minutes
        Excludes restaurants closed on the current day of week
        Includes weighted "Eat at Home" option if enabled

        Args:
            category (str, optional): Filter by category
            distance (str, optional): Filter by distance

        Returns:
            dict: Random restaurant data or None if no restaurants available
        """
        import random

        # Define distance hierarchy (in order from closest to farthest)
        distance_hierarchy = ['nearby', 'short-drive', 'medium-drive', 'far']

        # Get appropriate set based on filters
        if category and distance:
            # Get all restaurants in category
            cat_ids = self.redis.smembers(f"restaurants:by_category:{category}")

            # Get all distances up to and including selected distance
            allowed_distances = distance_hierarchy[:distance_hierarchy.index(distance) + 1]
            dist_ids = set()
            for dist in allowed_distances:
                dist_ids.update(self.redis.smembers(f"restaurants:by_distance:{dist}"))

            # Intersect category with allowed distances
            ids_list = list(cat_ids.intersection(dist_ids))
        elif category:
            ids_list = list(self.redis.smembers(f"restaurants:by_category:{category}"))
        elif distance:
            # Get all distances up to and including selected distance
            allowed_distances = distance_hierarchy[:distance_hierarchy.index(distance) + 1]
            dist_ids = set()
            for dist in allowed_distances:
                dist_ids.update(self.redis.smembers(f"restaurants:by_distance:{dist}"))
            ids_list = list(dist_ids)
        else:
            ids_list = list(self.redis.smembers("restaurants:index"))

        # Get current day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
        current_day = datetime.utcnow().weekday()
        # Convert to Sunday=0 format (Python uses Monday=0)
        current_day = (current_day + 1) % 7

        # Check for recent spin (within 15 minutes)
        excluded_id = None
        recent_history = self.get_history(limit=1)
        if recent_history:
            last_spin = recent_history[0]
            last_time = datetime.fromisoformat(last_spin.get('timestamp'))
            time_diff = (datetime.utcnow() - last_time).total_seconds()

            # If last spin was within 15 minutes (900 seconds), exclude it
            if time_diff < 900:
                excluded_id = last_spin.get('restaurant_id')

        # Build weighted pool of candidates
        pool = []

        # Add restaurants to pool (filtering out closed and excluded ones)
        for restaurant_id in ids_list:
            # Convert bytes to string if needed
            if isinstance(restaurant_id, bytes):
                restaurant_id = restaurant_id.decode('utf-8')

            # Skip if this was the recently excluded restaurant
            if excluded_id and restaurant_id == excluded_id:
                continue

            # Get the restaurant to check its closed days
            restaurant = self.get(restaurant_id)
            if not restaurant:
                continue

            # Check if restaurant is closed today
            closed_days = restaurant.get('closed_days', [])
            if current_day in closed_days:
                continue  # Skip this restaurant, it's closed today

            # Add to pool (weight of 1 for regular restaurants)
            pool.append(restaurant)

        # Add "Eat at Home" option with weight if enabled
        if Config.EAT_AT_HOME_ENABLED:
            eat_at_home = {
                "id": "eat-at-home",
                "name": Config.EAT_AT_HOME_NAME,
                "categories": ["home"],
                "distance": "nearby",
                "added_by": "System",
                "is_eat_at_home": True,
                "closed_days": []
            }
            # Add multiple times based on weight
            for _ in range(Config.EAT_AT_HOME_WEIGHT):
                pool.append(eat_at_home)

        # Return None if pool is empty
        if not pool:
            return None

        # Pick random from weighted pool
        return random.choice(pool)

    def get_randomization_stats(self, category=None, distance=None):
        """
        Get statistics about the current randomization pool without actually selecting.
        Shows what items are in the pool and their probabilities.

        Args:
            category (str, optional): Filter by category
            distance (str, optional): Filter by distance

        Returns:
            dict: Pool statistics including counts, percentages, and excluded items
        """
        import random

        # Define distance hierarchy (in order from closest to farthest)
        distance_hierarchy = ['nearby', 'short-drive', 'medium-drive', 'far']

        # Get appropriate set based on filters (same logic as get_random)
        if category and distance:
            cat_ids = self.redis.smembers(f"restaurants:by_category:{category}")
            allowed_distances = distance_hierarchy[:distance_hierarchy.index(distance) + 1]
            dist_ids = set()
            for dist in allowed_distances:
                dist_ids.update(self.redis.smembers(f"restaurants:by_distance:{dist}"))
            ids_list = list(cat_ids.intersection(dist_ids))
        elif category:
            ids_list = list(self.redis.smembers(f"restaurants:by_category:{category}"))
        elif distance:
            allowed_distances = distance_hierarchy[:distance_hierarchy.index(distance) + 1]
            dist_ids = set()
            for dist in allowed_distances:
                dist_ids.update(self.redis.smembers(f"restaurants:by_distance:{dist}"))
            ids_list = list(dist_ids)
        else:
            ids_list = list(self.redis.smembers("restaurants:index"))

        # Get current day of week
        current_day = datetime.utcnow().weekday()
        current_day = (current_day + 1) % 7  # Convert to Sunday=0 format

        # Check for recent spin exclusion
        excluded_restaurant = None
        recent_history = self.get_history(limit=1)
        if recent_history:
            last_spin = recent_history[0]
            last_time = datetime.fromisoformat(last_spin.get('timestamp'))
            time_diff = (datetime.utcnow() - last_time).total_seconds()
            if time_diff < 900:  # 15 minutes
                excluded_id = last_spin.get('restaurant_id')
                if excluded_id and excluded_id != 'eat-at-home':
                    excluded_restaurant = self.get(excluded_id)

        # Build pool (same logic as get_random)
        pool = []
        closed_today = []

        for restaurant_id in ids_list:
            if isinstance(restaurant_id, bytes):
                restaurant_id = restaurant_id.decode('utf-8')

            restaurant = self.get(restaurant_id)
            if not restaurant:
                continue

            # Check if excluded by recent spin
            if excluded_restaurant and restaurant_id == excluded_restaurant.get('id'):
                continue

            # Check if closed today
            closed_days = restaurant.get('closed_days', [])
            if current_day in closed_days:
                closed_today.append(restaurant.get('name'))
                continue

            pool.append(restaurant)

        # Add "Eat at Home" with weight
        eat_at_home_count = 0
        if Config.EAT_AT_HOME_ENABLED:
            eat_at_home = {
                "id": "eat-at-home",
                "name": Config.EAT_AT_HOME_NAME,
                "categories": ["home"],
                "distance": "nearby",
                "added_by": "System",
                "is_eat_at_home": True,
                "closed_days": []
            }
            for _ in range(Config.EAT_AT_HOME_WEIGHT):
                pool.append(eat_at_home)
            eat_at_home_count = Config.EAT_AT_HOME_WEIGHT

        # Calculate statistics
        total_items = len(pool)
        item_counts = {}
        for item in pool:
            name = item.get('name', 'Unknown')
            item_counts[name] = item_counts.get(name, 0) + 1

        # Build stats response
        items = []
        for name, count in sorted(item_counts.items()):
            percentage = (count / total_items * 100) if total_items > 0 else 0
            items.append({
                "name": name,
                "count": count,
                "percentage": round(percentage, 1)
            })

        return {
            "total_pool_size": total_items,
            "items": items,
            "excluded": excluded_restaurant.get('name') if excluded_restaurant else None,
            "excluded_reason": "Recent spin (within 15 min)" if excluded_restaurant else None,
            "closed_today": closed_today,
            "filters": {
                "category": category if category else None,
                "distance": distance if distance else None
            }
        }

    def can_user_spin(self, username):
        """
        Check if a user can spin based on rate limiting

        Args:
            username (str): Username to check

        Returns:
            tuple: (can_spin: bool, seconds_remaining: int)
        """
        last_spin_key = f"user:{username}:last_spin"
        last_spin_time = self.redis.get(last_spin_key)

        if not last_spin_time:
            return True, 0

        try:
            last_spin_time = float(last_spin_time)
            time_since_spin = datetime.utcnow().timestamp() - last_spin_time

            if time_since_spin >= Config.SPIN_TIMEOUT_SECONDS:
                return True, 0
            else:
                seconds_remaining = int(Config.SPIN_TIMEOUT_SECONDS - time_since_spin)
                return False, seconds_remaining
        except (ValueError, TypeError):
            return True, 0

    def record_user_spin(self, username):
        """
        Record that a user has just spun

        Args:
            username (str): Username who spun
        """
        last_spin_key = f"user:{username}:last_spin"
        self.redis.set(last_spin_key, datetime.utcnow().timestamp())
        # Set expiry to cleanup old data (2x timeout period)
        self.redis.expire(last_spin_key, Config.SPIN_TIMEOUT_SECONDS * 2)

    def add_to_history(self, username, restaurant):
        """
        Add a spin to the history

        Args:
            username (str): Username who pressed spin
            restaurant (dict): Restaurant that was selected

        Returns:
            str: History entry ID (timestamp-based)
        """
        import json

        entry_id = f"{datetime.utcnow().timestamp()}"

        # Get first category from categories array (or fallback to old single category field)
        categories = restaurant.get("categories", [])
        if isinstance(categories, list) and categories:
            category = categories[0]
        else:
            category = restaurant.get("category", "unknown")

        history_entry = {
            "id": entry_id,
            "username": username,
            "restaurant_id": restaurant.get("id"),
            "restaurant_name": restaurant.get("name"),
            "category": category,
            "timestamp": datetime.utcnow().isoformat(),
            "went": False
        }

        # Add to history list
        self.redis.lpush("spin_history", json.dumps(history_entry))

        # Clean up old entries periodically (every 10th entry to avoid race conditions)
        history_length = self.redis.llen("spin_history")
        if history_length % 10 == 0:
            self._cleanup_old_history()

        return entry_id

    def _cleanup_old_history(self):
        """
        Remove history entries older than HISTORY_RETENTION_DAYS
        """
        import json
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=Config.HISTORY_RETENTION_DAYS)

        # Get all history entries
        all_history = self.redis.lrange("spin_history", 0, -1)
        valid_entries = []

        for entry_bytes in all_history:
            if isinstance(entry_bytes, bytes):
                entry_bytes = entry_bytes.decode('utf-8')

            try:
                entry = json.loads(entry_bytes)
                entry_time = datetime.fromisoformat(entry.get('timestamp'))

                # Keep if within retention period
                if entry_time >= cutoff_date:
                    valid_entries.append(entry_bytes)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

        # Replace the list with only valid entries
        if valid_entries:
            self.redis.delete("spin_history")
            for entry in reversed(valid_entries):  # Reverse to maintain order
                self.redis.rpush("spin_history", entry)

    def get_history(self, limit=20):
        """
        Get spin history within retention period

        Args:
            limit (int): Number of recent history entries to retrieve (default 20)

        Returns:
            list: List of history entries (most recent first)
        """
        import json

        # Get more than limit to filter by date, then limit the results
        history_data = self.redis.lrange("spin_history", 0, -1)
        history = []

        for entry_bytes in history_data:
            if isinstance(entry_bytes, bytes):
                entry_bytes = entry_bytes.decode('utf-8')
            try:
                entry = json.loads(entry_bytes)
                history.append(entry)
            except json.JSONDecodeError:
                continue

        # Return most recent entries up to limit
        return history[:limit]

    def mark_went(self, entry_id):
        """
        Mark a history entry as "went" (user confirmed they went to this restaurant)

        Args:
            entry_id (str): History entry ID

        Returns:
            bool: True if successful, False if entry not found
        """
        import json

        # Get all history entries
        history_data = self.redis.lrange("spin_history", 0, -1)
        updated = False

        for index, entry_bytes in enumerate(history_data):
            if isinstance(entry_bytes, bytes):
                entry_bytes = entry_bytes.decode('utf-8')

            try:
                entry = json.loads(entry_bytes)

                # Check if this is the entry we're looking for
                if entry.get("id") == entry_id:
                    entry["went"] = True
                    # Update the entry in the list
                    self.redis.lset("spin_history", index, json.dumps(entry))
                    updated = True
                    break

            except json.JSONDecodeError:
                continue

        return updated

    def get_user_stats(self, username):
        """
        Get statistics for a user's contributions

        Args:
            username (str): Username

        Returns:
            dict: Stats with added and removed counts
        """
        added_count = self.redis.scard(f"user:{username}:added")
        removed_count = self.redis.scard(f"user:{username}:removed")

        return {
            "username": username,
            "added": added_count,
            "removed": removed_count
        }

    def get_categories(self):
        """
        Get all available categories (default + custom)

        Returns:
            list: List of category names
        """
        # Get custom categories from Redis
        custom_cats = self.redis.smembers("custom_categories")
        custom_list = [c.decode('utf-8') if isinstance(c, bytes) else c for c in custom_cats]

        # Combine with default categories
        all_categories = list(set(Config.DEFAULT_CATEGORIES + custom_list))
        all_categories.sort()

        return all_categories

    def add_category(self, category_name):
        """
        Add a new custom category

        Args:
            category_name (str): Category name to add

        Returns:
            bool: True if added, False if already exists
        """
        category_name = category_name.lower().strip()

        if not category_name:
            return False

        # Add to custom categories set
        result = self.redis.sadd("custom_categories", category_name)
        return result > 0

    def update(self, restaurant_id, name=None, categories=None, distance=None, closed_days=None):
        """
        Update restaurant details

        Args:
            restaurant_id (str): Restaurant ID
            name (str, optional): New name
            categories (list, optional): New list of categories
            distance (str, optional): New distance level
            closed_days (list, optional): List of closed day numbers (0-6)

        Returns:
            dict: Updated restaurant data or None if not found
        """
        import json

        restaurant = self.get(restaurant_id)
        if not restaurant:
            return None

        old_categories = restaurant.get('categories', [])
        old_distance = restaurant.get('distance')

        # Update fields
        updates = {}
        if name is not None:
            updates['name'] = name

        if categories is not None:
            # Validate categories
            valid_categories = self.get_categories()
            for cat in categories:
                if cat not in valid_categories:
                    raise ValueError(f"Invalid category '{cat}'")
            updates['categories'] = json.dumps(categories)

        if distance is not None:
            if distance not in Config.VALID_DISTANCES:
                raise ValueError(f"Invalid distance '{distance}'")
            updates['distance'] = distance

        if closed_days is not None:
            # Validate closed_days - ensure it's a list and validate each day
            if not isinstance(closed_days, list):
                raise ValueError("closed_days must be a list")
            validated_days = []
            for day in closed_days:
                try:
                    day_int = int(day)
                    if 0 <= day_int <= 6:
                        validated_days.append(day_int)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid day value: {day}")
            updates['closed_days'] = json.dumps(validated_days)

        if updates:
            self.redis.hset(f"restaurants:{restaurant_id}", mapping=updates)

            # Update indexes if categories or distance changed
            if categories is not None and categories != old_categories:
                # Remove from old category indexes
                for old_cat in old_categories:
                    self.redis.srem(f"restaurants:by_category:{old_cat}", restaurant_id)
                # Add to new category indexes
                for new_cat in categories:
                    self.redis.sadd(f"restaurants:by_category:{new_cat}", restaurant_id)

            if distance is not None and distance != old_distance:
                # Remove from old distance index
                if old_distance:
                    self.redis.srem(f"restaurants:by_distance:{old_distance}", restaurant_id)
                # Add to new distance index
                self.redis.sadd(f"restaurants:by_distance:{distance}", restaurant_id)

        # Auto-backup after update
        try:
            self.backup_to_file()
        except Exception as e:
            print(f"Backup failed: {e}")

        return self.get(restaurant_id)

    def backup_to_file(self):
        """
        Backup all restaurant data to a JSON file
        Creates timestamped backup in backups/ directory

        Returns:
            str: Path to backup file
        """
        import json
        import os

        # Get all active and inactive restaurants
        all_restaurants = self.get_all(active_only=False)

        # Also get custom categories
        categories = self.get_categories()

        backup_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "restaurants": all_restaurants,
            "custom_categories": [cat for cat in categories if cat not in Config.DEFAULT_CATEGORIES]
        }

        # Create backup filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = Config.BACKUP_DIR
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"restaurants_backup_{timestamp}.json")

        # Write backup file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        # Also maintain a "latest" backup
        latest_file = os.path.join(backup_dir, "restaurants_latest.json")
        with open(latest_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        return backup_file

    def restore_from_file(self, backup_file):
        """
        Restore restaurant data from a backup file

        Args:
            backup_file (str): Path to backup JSON file

        Returns:
            dict: Restore statistics (restaurants_restored, categories_restored)
        """
        import json
        import os

        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        with open(backup_file, 'r') as f:
            backup_data = json.load(f)

        restaurants_restored = 0
        categories_restored = 0

        # Restore custom categories first
        if 'custom_categories' in backup_data:
            for category in backup_data['custom_categories']:
                if self.add_category(category):
                    categories_restored += 1

        # Restore restaurants
        if 'restaurants' in backup_data:
            for restaurant_data in backup_data['restaurants']:
                try:
                    # Create restaurant with original ID
                    restaurant_id = restaurant_data.get('id')
                    name = restaurant_data.get('name')
                    categories = restaurant_data.get('categories', ['quick'])
                    distance = restaurant_data.get('distance', Config.DEFAULT_DISTANCE)
                    added_by = restaurant_data.get('added_by', 'restored')
                    is_active = restaurant_data.get('is_active', '1')

                    # Manually create to preserve ID
                    restaurant_hash = {
                        "id": restaurant_id,
                        "name": name,
                        "categories": json.dumps(categories) if isinstance(categories, list) else categories,
                        "distance": distance,
                        "added_by": added_by,
                        "added_at": restaurant_data.get('added_at', datetime.utcnow().isoformat()),
                        "is_active": is_active
                    }

                    # Store in Redis
                    self.redis.hset(f"restaurants:{restaurant_id}", mapping=restaurant_hash)

                    # Update indexes if active
                    if is_active == '1':
                        self.redis.sadd("restaurants:index", restaurant_id)
                        for category in (categories if isinstance(categories, list) else [categories]):
                            self.redis.sadd(f"restaurants:by_category:{category}", restaurant_id)
                        if distance:
                            self.redis.sadd(f"restaurants:by_distance:{distance}", restaurant_id)

                    restaurants_restored += 1

                except Exception as e:
                    print(f"Error restoring restaurant {restaurant_data.get('id')}: {e}")
                    continue

        return {
            "restaurants_restored": restaurants_restored,
            "categories_restored": categories_restored,
            "timestamp": backup_data.get('timestamp')
        }


def get_redis_client():
    """
    Create and return a Redis client instance

    Returns:
        redis.Redis: Redis client
    """
    return redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        password=Config.REDIS_PASSWORD,
        decode_responses=False  # We'll handle decoding manually for consistency
    )

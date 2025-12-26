from datetime import datetime
import redis
from app.config import Config


class RestaurantModel:
    """Redis-based restaurant data model"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def create(self, name, category, added_by):
        """
        Create a new restaurant entry

        Args:
            name (str): Restaurant name
            category (str): Category (quick, sit-down, or nice)
            added_by (str): Username who added it

        Returns:
            dict: Created restaurant data with id
        """
        if category not in Config.VALID_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {Config.VALID_CATEGORIES}")

        # Generate unique ID atomically
        restaurant_id = self.redis.incr("restaurants:counter")

        # Create restaurant hash
        restaurant_data = {
            "id": str(restaurant_id),
            "name": name,
            "category": category,
            "added_by": added_by,
            "added_at": datetime.utcnow().isoformat(),
            "is_active": "1"
        }

        # Store in Redis
        self.redis.hset(f"restaurants:{restaurant_id}", mapping=restaurant_data)

        # Add to indexes
        self.redis.sadd("restaurants:index", restaurant_id)
        self.redis.sadd(f"restaurants:by_category:{category}", restaurant_id)
        self.redis.sadd(f"user:{added_by}:added", restaurant_id)

        return restaurant_data

    def get(self, restaurant_id):
        """
        Get a single restaurant by ID

        Args:
            restaurant_id (str): Restaurant ID

        Returns:
            dict: Restaurant data or None if not found
        """
        data = self.redis.hgetall(f"restaurants:{restaurant_id}")

        if not data:
            return None

        # Convert bytes to strings
        return {k.decode('utf-8') if isinstance(k, bytes) else k:
                v.decode('utf-8') if isinstance(v, bytes) else v
                for k, v in data.items()}

    def get_all(self, category=None, active_only=True):
        """
        Get all restaurants, optionally filtered by category

        Args:
            category (str, optional): Filter by category
            active_only (bool): Only return active restaurants (default True)

        Returns:
            list: List of restaurant dictionaries
        """
        # Get appropriate set of IDs
        if category:
            if category not in Config.VALID_CATEGORIES:
                return []
            ids = self.redis.smembers(f"restaurants:by_category:{category}")
        else:
            ids = self.redis.smembers("restaurants:index")

        restaurants = []
        for rid in ids:
            # Convert bytes to int
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

        category = restaurant.get('category')

        # Mark as inactive
        self.redis.hset(f"restaurants:{restaurant_id}", "is_active", "0")

        # Track removal metadata
        self.redis.sadd(f"restaurants:{restaurant_id}:removed_by", removed_by)
        self.redis.set(f"restaurants:{restaurant_id}:removed_at", datetime.utcnow().isoformat())
        self.redis.sadd(f"user:{removed_by}:removed", restaurant_id)

        # Remove from active indexes
        self.redis.srem("restaurants:index", restaurant_id)
        if category:
            self.redis.srem(f"restaurants:by_category:{category}", restaurant_id)

        return True

    def get_random(self, category=None):
        """
        Get a random restaurant, optionally filtered by category

        Args:
            category (str, optional): Filter by category

        Returns:
            dict: Random restaurant data or None if no restaurants available
        """
        # Get appropriate set
        if category:
            if category not in Config.VALID_CATEGORIES:
                return None
            set_key = f"restaurants:by_category:{category}"
        else:
            set_key = "restaurants:index"

        # Get random member from set
        random_id = self.redis.srandmember(set_key)

        if not random_id:
            return None

        # Convert bytes to string if needed
        if isinstance(random_id, bytes):
            random_id = random_id.decode('utf-8')

        return self.get(random_id)

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

        history_entry = {
            "id": entry_id,
            "username": username,
            "restaurant_id": restaurant.get("id"),
            "restaurant_name": restaurant.get("name"),
            "category": restaurant.get("category"),
            "timestamp": datetime.utcnow().isoformat(),
            "went": False
        }

        # Add to history list (keep last 20)
        self.redis.lpush("spin_history", json.dumps(history_entry))
        self.redis.ltrim("spin_history", 0, 19)  # Keep only last 20

        return entry_id

    def get_history(self, limit=20):
        """
        Get spin history

        Args:
            limit (int): Number of history entries to retrieve (default 20)

        Returns:
            list: List of history entries
        """
        import json

        history_data = self.redis.lrange("spin_history", 0, limit - 1)
        history = []

        for entry_bytes in history_data:
            if isinstance(entry_bytes, bytes):
                entry_bytes = entry_bytes.decode('utf-8')
            try:
                entry = json.loads(entry_bytes)
                history.append(entry)
            except json.JSONDecodeError:
                continue

        return history

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

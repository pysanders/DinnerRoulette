# Dinner Roulette

A mobile-first web app that helps you decide where to eat! Add restaurant options, categorize them, and let the roulette wheel pick for you.

## Features

- **Random Selection**: Spin the wheel to pick a random restaurant
- **Category Filtering**: Filter by Quick, Sit Down, or Nice restaurants
- **User Tracking**: Track who added each restaurant
- **Mobile-First Design**: Optimized for phones with responsive layout
- **Cookie-Based Auth**: Simple first-name registration
- **Soft Deletes**: Track who removed restaurants without losing data
- **Docker Ready**: Easy deployment to Unraid or any Docker host

## Tech Stack

- **Backend**: Flask (Python 3.14)
- **Database**: Redis
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker + Docker Compose

## Project Structure

```
DinnerRoulette/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models.py            # Redis data models
│   ├── routes.py            # API endpoints
│   ├── utils.py             # Helper functions
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css   # Mobile-first styles
│   │   └── js/
│   │       └── app.js       # Frontend logic
│   └── templates/
│       └── index.html       # Single-page app
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── run.py
└── .env.example
```

## Local Development Setup

### Prerequisites

- Python 3.14+
- Redis server (running locally or on your network)
- pip

### Installation

1. **Clone or navigate to the project**:
   ```bash
   cd /Users/nathansanders/PycharmProjects/DinnerRoulette
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Redis connection details
   ```

5. **Run the development server**:
   ```bash
   python run.py
   ```

6. **Open in browser**:
   ```
   http://localhost:5000
   ```

## Docker Deployment (Unraid)

### Prerequisites

- Docker and Docker Compose installed on Unraid
- Existing Redis server running on Unraid

### Deployment Steps

1. **Copy project to Unraid**:
   ```bash
   # Copy the entire project directory to your Unraid server
   # Example location: /mnt/user/appdata/dinner-roulette/
   ```

2. **Create .env file**:
   ```bash
   cd /mnt/user/appdata/dinner-roulette/
   cp .env.example .env
   nano .env
   ```

3. **Configure Redis connection in .env**:
   ```bash
   SECRET_KEY=your-random-secret-key-here
   FLASK_ENV=production
   REDIS_HOST=your-unraid-ip  # e.g., 192.168.1.100
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=  # If your Redis has a password
   COOKIE_SECURE=false  # Set to true if using HTTPS
   ```

4. **Build and run with Docker Compose**:
   ```bash
   cd docker
   docker-compose up -d
   ```

5. **Access the app**:
   ```
   http://your-unraid-ip:5000
   ```

### Docker Commands

```bash
# Start the app
docker-compose -f docker/docker-compose.yml up -d

# Stop the app
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Rebuild after code changes
docker-compose -f docker/docker-compose.yml up -d --build

# Check health
curl http://localhost:5000/health
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main application page |
| GET | `/health` | Health check endpoint |
| GET | `/api/user/check` | Check if user has cookie |
| POST | `/api/user/register` | Register user and set cookie |
| GET | `/api/restaurants` | Get all restaurants |
| GET | `/api/restaurants?category=quick` | Get restaurants by category |
| POST | `/api/restaurants` | Add new restaurant |
| DELETE | `/api/restaurants/<id>` | Remove restaurant |
| GET | `/api/randomize` | Get random restaurant |
| GET | `/api/randomize?category=quick` | Get random restaurant by category |
| GET | `/api/categories` | Get available categories |
| GET | `/api/user/<username>/stats` | Get user statistics |

## Redis Data Schema

### Keys

- `restaurants:{id}` - Hash containing restaurant data
- `restaurants:index` - Set of all active restaurant IDs
- `restaurants:by_category:{category}` - Set of IDs for each category
- `restaurants:counter` - Auto-increment counter for IDs
- `user:{username}:added` - Set of restaurant IDs added by user
- `user:{username}:removed` - Set of restaurant IDs removed by user

### Restaurant Hash Structure

```python
{
    "id": "1",
    "name": "Pizza Palace",
    "category": "quick",  # quick|sit-down|nice
    "added_by": "John",
    "added_at": "2025-12-26T10:00:00Z",
    "is_active": "1"  # 1=active, 0=removed
}
```

## Categories

- **quick**: Fast food, takeout, quick meals
- **sit-down**: Casual dining restaurants
- **nice**: Fine dining, special occasions

## Configuration

All configuration is done via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key for cookies | (required) |
| FLASK_ENV | Environment (development/production) | production |
| REDIS_HOST | Redis server hostname/IP | localhost |
| REDIS_PORT | Redis server port | 6379 |
| REDIS_DB | Redis database number | 0 |
| REDIS_PASSWORD | Redis password (if required) | (empty) |
| COOKIE_SECURE | Use secure cookies (HTTPS only) | false |

## Security Notes

- Change `SECRET_KEY` in production to a random secret
- Set `COOKIE_SECURE=true` if using HTTPS
- Redis password is optional but recommended
- Cookies are httponly to prevent XSS attacks
- All user input is validated on the backend

## Troubleshooting

### Can't connect to Redis

1. Check Redis is running: `docker ps` or `redis-cli ping`
2. Verify REDIS_HOST in .env matches your Redis server IP
3. Check firewall rules allow connections on port 6379
4. Test connection: `redis-cli -h YOUR_REDIS_HOST ping`

### Docker container won't start

1. Check logs: `docker-compose logs -f`
2. Verify .env file exists and has correct values
3. Ensure port 5000 is not already in use
4. Check Docker has enough resources

### Frontend shows "Failed to load restaurants"

1. Check browser console for errors (F12)
2. Verify API is accessible: `curl http://localhost:5000/api/restaurants`
3. Check Redis connection from container logs
4. Ensure user is registered (check cookie exists)

### "User not registered" errors

1. Clear browser cookies and re-register
2. Check cookie settings in .env
3. If using HTTPS, ensure COOKIE_SECURE=true

## Development

### Running Tests Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dev dependencies (if any added later)
pip install -r requirements.txt

# Run the app
python run.py
```

### Code Structure

- **app/__init__.py**: Flask app factory and initialization
- **app/config.py**: Configuration management
- **app/models.py**: Redis data models and CRUD operations
- **app/routes.py**: API endpoint definitions
- **app/utils.py**: Helper functions (cookies, validation)
- **app/static/js/app.js**: Frontend JavaScript logic
- **app/static/css/styles.css**: Mobile-first responsive styles
- **app/templates/index.html**: Single-page application HTML

## License

This project is for personal use.

## Support

For issues or questions, check the logs and troubleshooting section above.

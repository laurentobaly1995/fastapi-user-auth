# FastAPI User Authentication System

A robust user authentication system built with FastAPI, PostgreSQL, and Redis.

## Features

- User registration and authentication
- JWT token-based authentication
- Password hashing with bcrypt
- PostgreSQL database integration
- Redis for token storage
- Protected endpoints
- Email validation

## Architecture Overview

This project uses a three-tier architecture:

1. **API Layer (FastAPI)**
   - FastAPI for high-performance API endpoints
   - Pydantic for data validation
   - Built-in OpenAPI documentation

2. **Database Layer (PostgreSQL & Redis)**
   - PostgreSQL: Main database for user data
     - Reliable and ACID compliant
     - Strong data consistency
     - Perfect for structured user data
   - Redis: Token storage
     - Fast in-memory access
     - Great for temporary token storage
     - Built-in expiration support

3. **Authentication Layer**
   - JWT tokens for stateless authentication
   - Bcrypt for secure password hashing
   - OAuth2 password flow for standardized auth

### Key Design Decisions:
- PostgreSQL over SQLite for production readiness
- Redis for token management (faster than DB queries)
- Alembic for database migrations (version control for DB schema)
- Pydantic models for input validation
- Dependency injection for clean code structure

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Homebrew (for macOS)

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
```
### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE dbname;

# Set password
ALTER USER postgres PASSWORD 'your_chosen_password';
```

### 5. Configure Environment Variables
```bash
# Create .env file
touch .env
```

Add the following to your `.env` file:
```text
DATABASE_URL=postgresql://postgres:your_password@localhost/dbname
SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

### 6. Run Database Migrations
```bash
# Create and apply migrations
alembic revision --autogenerate -m "Create users table"
alembic upgrade head
```

### 7. Start Redis Server
```bash
# On macOS
brew services start redis
```

## Running the Application
```bash
# Start the FastAPI server
uvicorn main:app --reload
```
## Testing

The following endpoints were tested manually using Postman:

1. User Registration (`POST /register`)
   - Successfully created new users
   - Properly hashed passwords in database
   - Prevented duplicate email registration

2. User Authentication (`POST /login`)
   - Successfully logged in with correct credentials
   - Generated valid JWT tokens
   - Rejected invalid credentials

3. Protected User Profile (`GET /me`)
   - Successfully retrieved user data with valid token
   - Properly rejected requests without token
   - Properly rejected invalid tokens

4. User Profile Update (`PUT /me`)
   - Successfully updated user first/last name
   - Protected endpoint requiring authentication
   - Maintained data integrity

All endpoints were tested with PostgreSQL database integration and proper error handling.

While unit tests would be nice to have, for a time-boxed 2-hour assignment, manual testing through Postman is a reasonable way to demonstrate that all core functionality works as required.


## Database Setup and API Testing

### Database Setup
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE dbname;

# Check database connection
psql dbname

# Check tables
\dt
```

### API Testing

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

2. Login to get token:
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

3. Get user profile:
```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer your-actual-token"
```

4. Update user profile:
```bash
curl -X PUT "http://localhost:8000/me" \
  -H "Authorization: Bearer your-actual-token" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name"
  }'
```
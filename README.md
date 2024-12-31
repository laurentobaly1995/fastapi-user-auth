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

git clone <your-repo-url>

2. Create a virtual environment:

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt

4. Set up PostgreSQL:

psql postgres

CREATE DATABASE dbname;


ALTER USER postgres PASSWORD 'your_chosen_password';


5. Create `.env` file:
env
DATABASE_URL=postgresql://postgres:your_password@localhost/dbname
SECRET_KEY=your_secret_key
ALGORITHM=HS256


6. Run database migrations:

alembic revision --autogenerate -m "Create users table"
alembic upgrade head


7. Start Redis server:

brew services start redis  # On macOS

## Running the Application

uvicorn main:app --reload
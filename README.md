# 🚀 BookAlchemy

BookAlchemy is a web application designed to help manage and catalog books in a library. It allows users to add, update,
and view book details, as well as manage authors associated with these books.

## 🛠 Tech Stack

- **Language:** Python 3.14
- **Framework:** FastAPI
- **Database:** SQLite
- **Infrastructure:** Docker & Docker Compose

## 🚀 Local Development

This project uses Docker to provide an isolated and reproducible development environment.

### Getting Started

1. Clone the repository.
2. Start the environment by running the following command in your terminal:

```bash
docker compose up --build -d
```

3. The API will be available at: http://localhost:8000
4. Interactive API documentation (Swagger UI) can be found at: http://localhost:8000/docs

### Important Commands

- make logs - Displays live application logs
- make test - Runs all Pytest unit tests inside the container
- make lint - Lints and formats the codebase using Ruff
- make down - Stops and removes the containers

📂 Project Structure

```
BookAlchemy
 ├── .cadence          # Configuration files for CI/CD pipelines
 ├── .github           # GitHub Actions workflows
 ├── data              # Database files
 │   └── library.sqlite3
 ├── src               # Application source code
 │   ├── app             # Main application logic
 │   │   ├── templates   # HTML templates for web pages
 │   │   │   ├── add_author.html
 │   │   │   ├── add_book.html
 │   │   │   └── home.html
 │   │   ├── __init__.py
 │   │   ├── database.py # Database operations
 │   │   ├── decorators.py
 │   │   ├── models.py   # Data models
 │   │   └── routes.py   # API endpoints
 │   └── tests           # Unit and integration tests
 │       ├── conftest.py
 │       ├── test_models.py
 │       └── test_routes.py
 ├── .dockerignore     # Files to ignore when building Docker images
 ├── compose.yaml      # Local development setup
 ├── Dockerfile        # Multi-stage build configuration
 ├── Makefile          # Command shortcuts
 └── README.md         # Project documentation
 └── requirements.txt  # Python dependencies
```

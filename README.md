# 🚀 Project Name

A brief description of what this project does and the problem it solves.

## 🛠 Tech Stack
- **Language:** Python 3.14
- **Framework:** FastAPI
- **Infrastructure:** Docker & Docker Compose

## 🚀 Local Development
This project uses Docker to provide an isolated and reproducible development environment.

### Getting Started
1. Clone the repository.
2. Start the environment by running the following command in your terminal:
   make up
3. The API will be available at: http://localhost:8000
4. Interactive API documentation (Swagger UI) can be found at: http://localhost:8000/docs

### Important Commands
- `make logs` - Displays live application logs
- `make test` - Runs all Pytest unit tests inside the container
- `make lint` - Lints and formats the codebase using Ruff
- `make down` - Stops and removes the containers

## 📂 Project Structure
.
├── .github/          # CI/CD Pipelines
├── tests/            # Pytest unit and integration tests
├── app.py            # Main application entrypoint
├── Dockerfile        # Multi-stage build configuration
├── compose.yaml      # Local development setup
├── Makefile          # Command shortcuts
└── requirements.txt  # Python dependencies

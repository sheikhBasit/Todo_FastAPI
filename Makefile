# Makefile for Todo FastAPI Project

# Variables
DOCKER_COMPOSE = docker-compose

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Run Alembic migrations
migrate:
	@echo "Running Alembic migrations..."
	$(DOCKER_COMPOSE) exec web alembic upgrade head

# Start the application
run:
	@echo "Starting the application..."
	$(DOCKER_COMPOSE) up --build

# Full setup and run
start: install migrate run
	@echo "Project is up and running!"

# Stop the application
stop:
	@echo "Stopping the application..."
	$(DOCKER_COMPOSE) down

# Clean up Docker containers and volumes
clean:
	@echo "Cleaning up Docker containers and volumes..."
	$(DOCKER_COMPOSE) down -v
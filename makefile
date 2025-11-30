.PHONY: build up down logs frontend backend restart clean

# Build all services
build:
    docker compose build

# Start containers in detached mode
up:
    docker compose up -d

# Stop and remove containers
down:
    docker compose down

# Follow logs for all services
logs:
    docker compose logs -f

# Health check (disabled for now)
# health:
#   docker inspect --format='{{.State.Health.Status}}' tank_iq-frontend-1
#   docker inspect --format='{{.State.Health.Status}}' tank_iq-backend-1

# Follow logs for frontend only
frontend:
    docker logs -f tank_iq-frontend-1

# Follow logs for backend only
backend:
    docker logs -f tank_iq-backend-1

# Restart everything (rebuild + up)
restart:
    docker compose down
    docker compose build --no-cache
    docker compose up -d

# Clean everything (containers, images, volumes)
clean:
    docker compose down --volumes --remove-orphans
    docker system prune -af







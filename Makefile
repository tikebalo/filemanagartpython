.PHONY: help install dev build up down logs clean test

help:
	@echo "FileManager Pro - Makefile Commands"
	@echo ""
	@echo "  make install     - Install all dependencies"
	@echo "  make dev         - Run in development mode"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start containers"
	@echo "  make down        - Stop containers"
	@echo "  make logs        - View logs"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make init-db     - Initialize database with admin user"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done!"

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	cd backend && uvicorn app.main:app --reload & \
	cd frontend && npm run dev

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting containers..."
	docker-compose up -d
	@echo "Application is running:"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API Docs: http://localhost:8000/docs"

down:
	@echo "Stopping containers..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf backend/storage/users/*
	rm -rf backend/storage/trash/*
	@echo "Done!"

init-db:
	@echo "Initializing database..."
	cd backend && python -c "from app.database import engine, Base; from app.models.user import User; from app.utils.security import hash_password; Base.metadata.create_all(bind=engine); from sqlalchemy.orm import Session; db = Session(engine); admin = User(username='admin', password_hash=hash_password('admin'), role='admin', quota=0); db.add(admin); db.commit(); print('Admin user created: admin/admin')"
	@echo "Done!"

test:
	@echo "Running tests..."
	cd backend && pytest
	cd frontend && npm test

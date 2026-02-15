"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()


def test_user_registration(client):
    """Test user registration endpoint."""
    response = client.post(
        "/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "student",
            "institution": "University"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_login(client):
    """Test user login endpoint."""
    # First register
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "securepass456",
            "user_type": "doctor",
        }
    )
    
    assert register_response.status_code == 201
    
    # Then login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "jane@example.com",
            "password": "securepass456"
        }
    )
    
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_duplicate_email_registration(client):
    """Test that duplicate emails are rejected."""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "pass123",
            "user_type": "student",
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "name": "User Two",
            "email": "duplicate@example.com",
            "password": "pass456",
            "user_type": "student",
        }
    )
    
    assert response.status_code == 409  # Conflict

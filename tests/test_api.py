"""
Test suite for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import get_db
from backend.models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create test database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_program():
    """Test creating a new program"""
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    
    response = client.post("/programs", json=program_data)
    assert response.status_code == 201
    data = response.json()
    assert data["program_name"] == "Test Program"
    assert data["beneficiaries"] == 100
    assert "id" in data


def test_create_program_invalid_data():
    """Test creating program with invalid data"""
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": -10,  # Invalid
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    
    response = client.post("/programs", json=program_data)
    assert response.status_code == 422  # Validation error


def test_get_programs():
    """Test retrieving all programs"""
    # Create test program
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    client.post("/programs", json=program_data)
    
    # Get all programs
    response = client.get("/programs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["program_name"] == "Test Program"


def test_get_program_by_id():
    """Test retrieving specific program by ID"""
    # Create test program
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    create_response = client.post("/programs", json=program_data)
    program_id = create_response.json()["id"]
    
    # Get program by ID
    response = client.get(f"/programs/{program_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == program_id
    assert data["program_name"] == "Test Program"


def test_get_program_not_found():
    """Test retrieving non-existent program"""
    response = client.get("/programs/9999")
    assert response.status_code == 404


def test_get_program_metrics():
    """Test computing metrics for a program"""
    # Create test program
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    create_response = client.post("/programs", json=program_data)
    program_id = create_response.json()["id"]
    
    # Get metrics
    response = client.get(f"/metrics/{program_id}")
    assert response.status_code == 200
    data = response.json()
    assert "outcome_improvement" in data
    assert "cost_per_beneficiary" in data
    assert "composite_impact_score" in data
    assert data["outcome_improvement"] == 30.0
    assert data["cost_per_beneficiary"] == 100.0


def test_analytics_summary():
    """Test analytics summary endpoint"""
    # Create test program
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    client.post("/programs", json=program_data)
    
    # Get summary
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_programs"] >= 1
    assert data["total_beneficiaries"] >= 100
    assert "average_impact_score" in data


def test_ranked_programs():
    """Test ranked programs endpoint"""
    # Create multiple programs
    programs = [
        {
            "program_name": f"Program {i}",
            "time_period": "2025-Q1",
            "beneficiaries": 100 + i * 10,
            "cost": 10000.00 + i * 1000,
            "pre_outcome_score": 40.0,
            "post_outcome_score": 70.0 + i
        }
        for i in range(3)
    ]
    
    for program in programs:
        client.post("/programs", json=program)
    
    # Get ranked programs
    response = client.get("/analytics/ranked?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    # Check that results are sorted by impact score
    scores = [p["composite_impact_score"] for p in data]
    assert scores == sorted(scores, reverse=True)


def test_delete_program():
    """Test deleting a program"""
    # Create test program
    program_data = {
        "program_name": "Test Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    create_response = client.post("/programs", json=program_data)
    program_id = create_response.json()["id"]
    
    # Delete program
    response = client.delete(f"/programs/{program_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/programs/{program_id}")
    assert get_response.status_code == 404


def test_update_program():
    """Test updating an existing program"""
    # Create test program
    program_data = {
        "program_name": "Original Program",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    create_response = client.post("/programs", json=program_data)
    program_id = create_response.json()["id"]
    
    # Update program
    updated_data = {
        "program_name": "Updated Program Name",
        "time_period": "2025-Q2",
        "beneficiaries": 200,
        "cost": 15000.00,
        "pre_outcome_score": 45.0,
        "post_outcome_score": 85.0
    }
    response = client.put(f"/programs/{program_id}", json=updated_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["program_name"] == "Updated Program Name"
    assert data["time_period"] == "2025-Q2"
    assert data["beneficiaries"] == 200
    assert data["cost"] == 15000.00
    assert data["pre_outcome_score"] == 45.0
    assert data["post_outcome_score"] == 85.0


def test_update_program_not_found():
    """Test updating non-existent program"""
    updated_data = {
        "program_name": "Test",
        "time_period": "2025-Q1",
        "beneficiaries": 100,
        "cost": 10000.00,
        "pre_outcome_score": 40.0,
        "post_outcome_score": 70.0
    }
    response = client.put("/programs/9999", json=updated_data)
    assert response.status_code == 404


"""
Test suite for analytics engine
"""

import pytest
from backend.analytics import MetricsCalculator, AnalyticsEngine
from backend.models import ProgramDB, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analytics.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_program(db_session):
    """Create sample program for testing"""
    program = ProgramDB(
        program_name="Test Program",
        time_period="2025-Q1",
        beneficiaries=100,
        cost=10000.00,
        pre_outcome_score=40.0,
        post_outcome_score=70.0
    )
    db_session.add(program)
    db_session.commit()
    db_session.refresh(program)
    return program


def test_calculate_outcome_improvement():
    """Test outcome improvement calculation"""
    result = MetricsCalculator.calculate_outcome_improvement(40.0, 70.0)
    assert result == 30.0


def test_calculate_outcome_improvement_negative():
    """Test outcome improvement with decline"""
    result = MetricsCalculator.calculate_outcome_improvement(70.0, 50.0)
    assert result == -20.0


def test_calculate_cost_per_beneficiary():
    """Test cost per beneficiary calculation"""
    result = MetricsCalculator.calculate_cost_per_beneficiary(10000.0, 100)
    assert result == 100.0


def test_calculate_cost_per_beneficiary_zero():
    """Test cost per beneficiary with zero beneficiaries"""
    result = MetricsCalculator.calculate_cost_per_beneficiary(10000.0, 0)
    assert result == 0.0


def test_calculate_growth_rate():
    """Test growth rate calculation"""
    result = MetricsCalculator.calculate_growth_rate(150, 100)
    assert result == 0.5  # 50% growth


def test_calculate_growth_rate_decline():
    """Test growth rate with decline"""
    result = MetricsCalculator.calculate_growth_rate(80, 100)
    assert result == -0.2  # 20% decline


def test_calculate_growth_rate_no_previous():
    """Test growth rate with no previous data"""
    result = MetricsCalculator.calculate_growth_rate(100, None)
    assert result is None


def test_normalize_value():
    """Test value normalization"""
    # Value in middle of range
    result = MetricsCalculator.normalize_value(50, 0, 100)
    assert result == 50.0
    
    # Value at minimum
    result = MetricsCalculator.normalize_value(0, 0, 100)
    assert result == 0.0
    
    # Value at maximum
    result = MetricsCalculator.normalize_value(100, 0, 100)
    assert result == 100.0


def test_normalize_value_beyond_range():
    """Test normalization with values beyond range"""
    # Below minimum
    result = MetricsCalculator.normalize_value(-10, 0, 100)
    assert result == 0.0  # Clamped to 0
    
    # Above maximum
    result = MetricsCalculator.normalize_value(150, 0, 100)
    assert result == 100.0  # Clamped to 100


def test_calculate_composite_score():
    """Test composite score calculation"""
    score = MetricsCalculator.calculate_composite_score(
        outcome_improvement=30.0,
        cost_per_beneficiary=100.0,
        growth_rate=0.5
    )
    
    assert isinstance(score, float)
    assert 0 <= score <= 100


def test_calculate_composite_score_no_growth():
    """Test composite score without growth rate"""
    score = MetricsCalculator.calculate_composite_score(
        outcome_improvement=30.0,
        cost_per_beneficiary=100.0,
        growth_rate=None
    )
    
    assert isinstance(score, float)
    assert 0 <= score <= 100


def test_compute_program_metrics(sample_program):
    """Test computing all metrics for a program"""
    metrics = MetricsCalculator.compute_program_metrics(sample_program)
    
    assert metrics.program_id == sample_program.id
    assert metrics.program_name == "Test Program"
    assert metrics.outcome_improvement == 30.0
    assert metrics.cost_per_beneficiary == 100.0
    assert metrics.composite_impact_score > 0


def test_get_analytics_summary_empty(db_session):
    """Test analytics summary with no programs"""
    summary = AnalyticsEngine.get_analytics_summary(db_session)
    
    assert summary.total_programs == 0
    assert summary.total_beneficiaries == 0
    assert summary.average_impact_score == 0.0


def test_get_analytics_summary(db_session, sample_program):
    """Test analytics summary with programs"""
    summary = AnalyticsEngine.get_analytics_summary(db_session)
    
    assert summary.total_programs == 1
    assert summary.total_beneficiaries == 100
    assert summary.total_cost == 10000.0
    assert summary.average_impact_score > 0
    assert summary.average_outcome_improvement == 30.0


def test_get_program_trends(db_session, sample_program):
    """Test getting program trends"""
    trends = AnalyticsEngine.get_program_trends(db_session)
    
    assert len(trends) == 1
    assert trends[0].time_period == "2025-Q1"
    assert trends[0].beneficiaries == 100
    assert trends[0].cost == 10000.0


def test_get_ranked_programs(db_session):
    """Test getting ranked programs"""
    # Create multiple programs
    programs = [
        ProgramDB(
            program_name=f"Program {i}",
            time_period="2025-Q1",
            beneficiaries=100 + i * 10,
            cost=10000.0 + i * 1000,
            pre_outcome_score=40.0,
            post_outcome_score=70.0 + i
        )
        for i in range(3)
    ]
    
    for program in programs:
        db_session.add(program)
    db_session.commit()
    
    # Get ranked programs
    ranked = AnalyticsEngine.get_ranked_programs(db_session, limit=10)
    
    assert len(ranked) == 3
    # Verify sorted by impact score (descending)
    scores = [p.composite_impact_score for p in ranked]
    assert scores == sorted(scores, reverse=True)


def test_get_ranked_programs_limit(db_session):
    """Test ranked programs with limit"""
    # Create 5 programs
    for i in range(5):
        program = ProgramDB(
            program_name=f"Program {i}",
            time_period="2025-Q1",
            beneficiaries=100,
            cost=10000.0,
            pre_outcome_score=40.0,
            post_outcome_score=70.0
        )
        db_session.add(program)
    db_session.commit()
    
    # Get top 3
    ranked = AnalyticsEngine.get_ranked_programs(db_session, limit=3)
    
    assert len(ranked) == 3


def test_get_program_by_id_with_metrics(db_session, sample_program):
    """Test getting program with metrics by ID"""
    metrics = AnalyticsEngine.get_program_by_id_with_metrics(db_session, sample_program.id)
    
    assert metrics is not None
    assert metrics.program_id == sample_program.id
    assert metrics.program_name == "Test Program"


def test_get_program_by_id_not_found(db_session):
    """Test getting non-existent program"""
    metrics = AnalyticsEngine.get_program_by_id_with_metrics(db_session, 9999)
    assert metrics is None

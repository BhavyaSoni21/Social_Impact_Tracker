"""
Utility functions for frontend
"""

import os


def format_currency(amount: float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"


def format_number(number: int) -> str:
    """Format large numbers with commas"""
    return f"{number:,}"


def format_percentage(value: float) -> str:
    """Format decimal as percentage"""
    return f"{value * 100:+.1f}%"


def get_api_url() -> str:
    """Get API base URL from environment or use default"""
    return os.getenv("API_URL", "http://localhost:8000")


def validate_program_data(data: dict) -> tuple[bool, str]:
    """
    Validate program data before submission
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        'program_name', 'time_period', 'beneficiaries', 
        'cost', 'pre_outcome_score', 'post_outcome_score'
    ]
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Missing required field: {field}"
    
    if data['beneficiaries'] <= 0:
        return False, "Beneficiaries must be greater than 0"
    
    if data['cost'] <= 0:
        return False, "Cost must be greater than 0"
    
    if not (0 <= data['pre_outcome_score'] <= 100):
        return False, "Pre-outcome score must be between 0 and 100"
    
    if not (0 <= data['post_outcome_score'] <= 100):
        return False, "Post-outcome score must be between 0 and 100"
    
    return True, ""


def get_impact_color(score: float) -> str:
    """
    Get color code based on impact score
    
    Args:
        score: Impact score (0-100)
        
    Returns:
        Color code (red, yellow, or green)
    """
    if score >= 75:
        return "green"
    elif score >= 50:
        return "yellow"
    else:
        return "red"


def get_impact_emoji(score: float) -> str:
    """
    Get emoji based on impact score
    
    Args:
        score: Impact score (0-100)
        
    Returns:
        Emoji string
    """
    if score >= 80:
        return "🌟"
    elif score >= 60:
        return "✅"
    elif score >= 40:
        return "⚠️"
    else:
        return "❌"

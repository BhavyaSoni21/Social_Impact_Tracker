"""
Analytics Engine for Social Impact Tracker
Computes impact metrics and generates insights
"""

from typing import List, Dict, Optional
from backend.models import ProgramDB, ImpactMetrics, AnalyticsSummary, ProgramTrend
from backend.config import METRIC_WEIGHTS, NORMALIZATION_RANGES
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Handles calculation of all impact metrics"""
    
    @staticmethod
    def calculate_outcome_improvement(pre_score: float, post_score: float) -> float:
        """
        Calculate outcome improvement
        
        Formula: Post-Outcome - Pre-Outcome
        
        Args:
            pre_score: Pre-intervention outcome score
            post_score: Post-intervention outcome score
            
        Returns:
            Outcome improvement value
        """
        improvement = post_score - pre_score
        logger.debug(f"Outcome improvement: {post_score} - {pre_score} = {improvement}")
        return round(improvement, 2)
    
    @staticmethod
    def calculate_cost_per_beneficiary(cost: float, beneficiaries: int) -> float:
        """
        Calculate cost efficiency per beneficiary
        
        Formula: Cost / Beneficiaries
        
        Args:
            cost: Total program cost
            beneficiaries: Number of beneficiaries
            
        Returns:
            Cost per beneficiary
        """
        if beneficiaries <= 0:
            return 0.0
        
        cost_per = cost / beneficiaries
        logger.debug(f"Cost per beneficiary: {cost} / {beneficiaries} = {cost_per}")
        return round(cost_per, 2)
    
    @staticmethod
    def calculate_growth_rate(current_beneficiaries: int, 
                             previous_beneficiaries: Optional[int]) -> Optional[float]:
        """
        Calculate beneficiary growth rate
        
        Formula: (Current - Previous) / Previous
        
        Args:
            current_beneficiaries: Current beneficiary count
            previous_beneficiaries: Previous period beneficiary count
            
        Returns:
            Growth rate as decimal (0.15 = 15% growth), or None if no previous data
        """
        if previous_beneficiaries is None or previous_beneficiaries == 0:
            return None
        
        growth = (current_beneficiaries - previous_beneficiaries) / previous_beneficiaries
        logger.debug(f"Growth rate: ({current_beneficiaries} - {previous_beneficiaries}) / {previous_beneficiaries} = {growth}")
        return round(growth, 4)
    
    @staticmethod
    def normalize_value(value: float, min_val: float, max_val: float) -> float:
        """
        Normalize value to 0-100 scale
        
        Args:
            value: Value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            
        Returns:
            Normalized value (0-100)
        """
        if max_val == min_val:
            return 50.0
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0, min(100, normalized))  # Clamp to 0-100
    
    @staticmethod
    def calculate_composite_score(outcome_improvement: float, 
                                  cost_per_beneficiary: float,
                                  growth_rate: Optional[float]) -> float:
        """
        Calculate weighted composite impact score
        
        Combines multiple metrics into single score using weighted formula
        
        Args:
            outcome_improvement: Outcome improvement value
            cost_per_beneficiary: Cost efficiency metric
            growth_rate: Growth rate (optional)
            
        Returns:
            Composite impact score (0-100)
        """
        # Normalize each metric
        outcome_norm = MetricsCalculator.normalize_value(
            outcome_improvement,
            NORMALIZATION_RANGES["outcome_improvement"][0],
            NORMALIZATION_RANGES["outcome_improvement"][1]
        )
        
        # For cost, lower is better - invert the normalization
        cost_norm = 100 - MetricsCalculator.normalize_value(
            cost_per_beneficiary,
            NORMALIZATION_RANGES["cost_per_beneficiary"][0],
            NORMALIZATION_RANGES["cost_per_beneficiary"][1]
        )
        
        # Normalize growth rate if available
        if growth_rate is not None:
            growth_norm = MetricsCalculator.normalize_value(
                growth_rate,
                NORMALIZATION_RANGES["growth_rate"][0],
                NORMALIZATION_RANGES["growth_rate"][1]
            )
        else:
            growth_norm = 50.0  # Neutral score if no growth data
        
        # Calculate weighted composite
        composite = (
            outcome_norm * METRIC_WEIGHTS["outcome_improvement"] +
            cost_norm * METRIC_WEIGHTS["cost_efficiency"] +
            growth_norm * METRIC_WEIGHTS["growth_rate"]
        )
        
        logger.debug(f"Composite score: outcome={outcome_norm:.1f}, cost={cost_norm:.1f}, "
                    f"growth={growth_norm:.1f} -> {composite:.1f}")
        
        return round(composite, 2)
    
    @staticmethod
    def compute_program_metrics(program: ProgramDB, 
                               previous_beneficiaries: Optional[int] = None) -> ImpactMetrics:
        """
        Compute all metrics for a program
        
        Args:
            program: Program database object
            previous_beneficiaries: Previous period beneficiary count (optional)
            
        Returns:
            ImpactMetrics object with all computed metrics
        """
        outcome_improvement = MetricsCalculator.calculate_outcome_improvement(
            program.pre_outcome_score,
            program.post_outcome_score
        )
        
        cost_per_beneficiary = MetricsCalculator.calculate_cost_per_beneficiary(
            program.cost,
            program.beneficiaries
        )
        
        growth_rate = MetricsCalculator.calculate_growth_rate(
            program.beneficiaries,
            previous_beneficiaries
        )
        
        composite_score = MetricsCalculator.calculate_composite_score(
            outcome_improvement,
            cost_per_beneficiary,
            growth_rate
        )
        
        return ImpactMetrics(
            program_id=program.id,
            program_name=program.program_name,
            outcome_improvement=outcome_improvement,
            cost_per_beneficiary=cost_per_beneficiary,
            growth_rate=growth_rate,
            composite_impact_score=composite_score
        )


class AnalyticsEngine:
    """Generates analytics and insights from program data"""
    
    @staticmethod
    def get_analytics_summary(db: Session) -> AnalyticsSummary:
        """
        Generate summary analytics for dashboard
        
        Args:
            db: Database session
            
        Returns:
            AnalyticsSummary with aggregated metrics
        """
        programs = db.query(ProgramDB).all()
        
        if not programs:
            return AnalyticsSummary(
                total_programs=0,
                total_beneficiaries=0,
                average_impact_score=0.0,
                total_cost=0.0,
                average_outcome_improvement=0.0
            )
        
        total_beneficiaries = sum(p.beneficiaries for p in programs)
        total_cost = sum(p.cost for p in programs)
        
        # Calculate metrics for all programs
        metrics_list = []
        for program in programs:
            metrics = MetricsCalculator.compute_program_metrics(program)
            metrics_list.append(metrics)
        
        avg_impact_score = sum(m.composite_impact_score for m in metrics_list) / len(metrics_list)
        avg_outcome_improvement = sum(m.outcome_improvement for m in metrics_list) / len(metrics_list)
        
        return AnalyticsSummary(
            total_programs=len(programs),
            total_beneficiaries=total_beneficiaries,
            average_impact_score=round(avg_impact_score, 2),
            total_cost=round(total_cost, 2),
            average_outcome_improvement=round(avg_outcome_improvement, 2)
        )
    
    @staticmethod
    def get_program_trends(db: Session) -> List[ProgramTrend]:
        """
        Get trend data for visualization
        
        Args:
            db: Database session
            
        Returns:
            List of ProgramTrend objects
        """
        programs = db.query(ProgramDB).order_by(ProgramDB.created_at).all()
        
        trends = []
        for program in programs:
            outcome_improvement = program.post_outcome_score - program.pre_outcome_score
            trends.append(ProgramTrend(
                time_period=program.time_period,
                beneficiaries=program.beneficiaries,
                cost=program.cost,
                outcome_improvement=outcome_improvement
            ))
        
        return trends
    
    @staticmethod
    def get_ranked_programs(db: Session, limit: int = 10) -> List[ImpactMetrics]:
        """
        Get programs ranked by composite impact score
        
        Args:
            db: Database session
            limit: Maximum number of programs to return
            
        Returns:
            List of programs sorted by impact score (descending)
        """
        programs = db.query(ProgramDB).all()
        
        metrics_list = []
        for program in programs:
            metrics = MetricsCalculator.compute_program_metrics(program)
            metrics_list.append(metrics)
        
        # Sort by composite score (descending)
        ranked = sorted(metrics_list, 
                       key=lambda m: m.composite_impact_score, 
                       reverse=True)
        
        return ranked[:limit]
    
    @staticmethod
    def get_program_by_id_with_metrics(db: Session, program_id: int) -> Optional[ImpactMetrics]:
        """
        Get specific program with computed metrics
        
        Args:
            db: Database session
            program_id: Program ID
            
        Returns:
            ImpactMetrics for the program, or None if not found
        """
        program = db.query(ProgramDB).filter(ProgramDB.id == program_id).first()
        
        if not program:
            return None
        
        # Try to find previous beneficiary count for growth rate
        previous_programs = db.query(ProgramDB).filter(
            ProgramDB.program_name == program.program_name,
            ProgramDB.id < program.id
        ).order_by(ProgramDB.id.desc()).first()
        
        previous_beneficiaries = previous_programs.beneficiaries if previous_programs else None
        
        return MetricsCalculator.compute_program_metrics(program, previous_beneficiaries)

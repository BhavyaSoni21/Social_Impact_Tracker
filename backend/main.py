from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.models import (
    ProgramCreate, ProgramResponse, ImpactMetrics, 
    AnalyticsSummary, ProgramDB
)
from backend.database import get_db, init_database, get_database_stats
from backend.analytics import MetricsCalculator, AnalyticsEngine
from backend.compression import compress_program_data, get_compression_efficiency
from backend.config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, 
    CORS_ORIGINS, COMPRESSION_ENABLED
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Social Impact Tracker API...")
    init_database()
    logger.info("Database initialized successfully")


@app.get("/", tags=["Root"])
def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
def health_check():
    db_stats = get_database_stats()
    compression_stats = get_compression_efficiency()
    
    return {
        "status": "healthy",
        "database": db_stats,
        "compression": compression_stats
    }


@app.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED, tags=["Programs"])
def create_program(program: ProgramCreate, db: Session = Depends(get_db)):
    try:
        compressed_name = program.program_name
        delta_beneficiaries = None
        
        if COMPRESSION_ENABLED:
            compressed_name, delta_beneficiaries = compress_program_data(
                program.program_name, 
                program.beneficiaries
            )
        
        db_program = ProgramDB(
            program_name=program.program_name,
            time_period=program.time_period,
            beneficiaries=program.beneficiaries,
            cost=program.cost,
            pre_outcome_score=program.pre_outcome_score,
            post_outcome_score=program.post_outcome_score,
            compressed_name=compressed_name,
            delta_beneficiaries=delta_beneficiaries
        )
        
        db.add(db_program)
        db.commit()
        db.refresh(db_program)
        
        logger.info(f"Created program: {program.program_name} (ID: {db_program.id})")
        return db_program
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating program: {str(e)}"
        )


@app.get("/programs", response_model=List[ProgramResponse], tags=["Programs"])
def get_programs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    programs = db.query(ProgramDB).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(programs)} programs")
    return programs


@app.get("/programs/{program_id}", response_model=ProgramResponse, tags=["Programs"])
def get_program(program_id: int, db: Session = Depends(get_db)):
    program = db.query(ProgramDB).filter(ProgramDB.id == program_id).first()
    
    if not program:
        logger.warning(f"Program not found: {program_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    
    return program


@app.put("/programs/{program_id}", response_model=ProgramResponse, tags=["Programs"])
def update_program(program_id: int, program: ProgramCreate, db: Session = Depends(get_db)):
    try:
        db_program = db.query(ProgramDB).filter(ProgramDB.id == program_id).first()
        
        if not db_program:
            logger.warning(f"Program not found for update: {program_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
        
        compressed_name = program.program_name
        delta_beneficiaries = None
        
        if COMPRESSION_ENABLED:
            compressed_name, delta_beneficiaries = compress_program_data(
                program.program_name, 
                program.beneficiaries
            )
        
        db_program.program_name = program.program_name
        db_program.time_period = program.time_period
        db_program.beneficiaries = program.beneficiaries
        db_program.cost = program.cost
        db_program.pre_outcome_score = program.pre_outcome_score
        db_program.post_outcome_score = program.post_outcome_score
        db_program.compressed_name = compressed_name
        db_program.delta_beneficiaries = delta_beneficiaries
        
        db.commit()
        db.refresh(db_program)
        
        logger.info(f"Updated program: {program.program_name} (ID: {program_id})")
        return db_program
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating program: {str(e)}"
        )


@app.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Programs"])
def delete_program(program_id: int, db: Session = Depends(get_db)):
    program = db.query(ProgramDB).filter(ProgramDB.id == program_id).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    
    db.delete(program)
    db.commit()
    logger.info(f"Deleted program: {program_id}")
    return None


@app.get("/metrics/{program_id}", response_model=ImpactMetrics, tags=["Metrics"])
def get_program_metrics(program_id: int, db: Session = Depends(get_db)):
    metrics = AnalyticsEngine.get_program_by_id_with_metrics(db, program_id)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    
    logger.info(f"Calculated metrics for program {program_id}")
    return metrics


@app.get("/analytics/summary", response_model=AnalyticsSummary, tags=["Analytics"])
def get_analytics_summary(db: Session = Depends(get_db)):
    summary = AnalyticsEngine.get_analytics_summary(db)
    logger.info("Generated analytics summary")
    return summary


@app.get("/analytics/ranked", response_model=List[ImpactMetrics], tags=["Analytics"])
def get_ranked_programs(limit: int = 10, db: Session = Depends(get_db)):
    ranked = AnalyticsEngine.get_ranked_programs(db, limit)
    logger.info(f"Retrieved top {len(ranked)} ranked programs")
    return ranked


@app.get("/analytics/trends", tags=["Analytics"])
def get_trends(db: Session = Depends(get_db)):
    trends = AnalyticsEngine.get_program_trends(db)
    logger.info(f"Retrieved {len(trends)} trend data points")
    return trends


@app.get("/compression/stats", tags=["System"])
def get_compression_stats():
    stats = get_compression_efficiency()
    return stats


if __name__ == "__main__":
    import uvicorn
    from backend.config import API_HOST, API_PORT, API_RELOAD
    
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://crewuser:7997920068@localhost:5432/financial_analyzer")

try:
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("Database engine initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    raise

class AnalysisResult(Base):
    """Main analysis result storage."""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    status = Column(String(50), default="queued", nullable=False, index=True)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    company_name = Column(String(255), nullable=True, index=True)
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "filename": self.filename,
            "query": self.query,
            "status": self.status,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "company_name": self.company_name
        }

class FinancialMetrics(Base):
    """Structured financial metrics for analytics."""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=False, index=True)
    task_id = Column(String(36), nullable=False, index=True)
    company_name = Column(String(255), nullable=True, index=True)
    
    # Core metrics
    revenue = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    operating_cash_flow = Column(Float, nullable=True)
    profit_margin = Column(Float, nullable=True)
    
    reporting_period = Column(String(50), nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
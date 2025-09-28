from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    user_intent = Column(String, nullable=False)
    response_time = Column(Float, nullable=False)
    success = Column(Integer, nullable=False)  # 1 for success, 0 for failure

DATABASE_URL = "sqlite:///metrics.db"  # Change to your database URL (e.g., Postgres)

def get_database_engine():
    return create_engine(DATABASE_URL)

def create_tables():
    engine = get_database_engine()
    Base.metadata.create_all(engine)

def get_session():
    engine = get_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()
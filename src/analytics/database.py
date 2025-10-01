from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    user_intent = Column(String, nullable=False)
    response_time = Column(Float, nullable=False)
    success = Column(Integer, nullable=False)  # 1 for success, 0 for failure


class Database:
    """Database wrapper for metrics storage."""
    
    def __init__(self, database_url: str = "sqlite:///metrics.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        return self.Session()
    
    def close(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()


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
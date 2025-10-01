"""Cloud-native analytics system using Google Cloud SQL PostgreSQL."""

import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from google.cloud import pubsub_v1
from config.cloud_config import cloud_settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class UserInteraction(Base):
    """User interaction model for PostgreSQL."""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_role = Column(String(100), index=True)
    query = Column(Text)
    query_type = Column(String(50), index=True)
    response_time = Column(Float)
    response_length = Column(Integer)
    code_snippets_shown = Column(Integer, default=0)
    citations_provided = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    user_rating = Column(Integer, nullable=True)
    follow_up_query = Column(Boolean, default=False)
    conversation_turn = Column(Integer, default=1)


class ContentAnalytics(Base):
    """Content analytics model for PostgreSQL."""
    __tablename__ = 'content_analytics'
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(100), index=True)
    content_id = Column(String(255), index=True)
    access_count = Column(Integer, default=1)
    avg_relevance_score = Column(Float)
    user_roles_accessing = Column(Text)  # JSON array
    last_accessed = Column(DateTime, default=datetime.utcnow)


class BusinessMetrics(Base):
    """Business metrics model for PostgreSQL."""
    __tablename__ = 'business_metrics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, index=True)
    hiring_manager_sessions = Column(Integer, default=0)
    developer_sessions = Column(Integer, default=0)
    casual_visitor_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)
    conversion_to_detailed_queries = Column(Float, default=0.0)
    code_display_engagement = Column(Float, default=0.0)
    citation_click_through_rate = Column(Float, default=0.0)


@dataclass
class UserInteractionData:
    """Data transfer object for user interactions."""
    session_id: str
    timestamp: datetime
    user_role: str
    query: str
    query_type: str
    response_time: float
    response_length: int
    code_snippets_shown: int
    citations_provided: int
    success: bool
    user_rating: Optional[int] = None
    follow_up_query: bool = False
    conversation_turn: int = 1


class CloudAnalytics:
    """Cloud-native analytics system with PostgreSQL and Pub/Sub."""
    
    def __init__(self):
        # Database setup
        self.engine = create_engine(
            cloud_settings.database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Pub/Sub setup for event streaming
        if cloud_settings.is_cloud_environment:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(
                cloud_settings.project_id, 
                cloud_settings.cloud_config.analytics_topic
            )
        else:
            self.publisher = None
            self.topic_path = None
        
        self._lock = threading.Lock()
    
    def get_db_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def log_interaction(self, interaction_data: UserInteractionData):
        """Log a user interaction with PostgreSQL and Pub/Sub."""
        with self.get_db_session() as session:
            try:
                # Create database record
                interaction = UserInteraction(
                    session_id=interaction_data.session_id,
                    timestamp=interaction_data.timestamp,
                    user_role=interaction_data.user_role,
                    query=interaction_data.query,
                    query_type=interaction_data.query_type,
                    response_time=interaction_data.response_time,
                    response_length=interaction_data.response_length,
                    code_snippets_shown=interaction_data.code_snippets_shown,
                    citations_provided=interaction_data.citations_provided,
                    success=interaction_data.success,
                    user_rating=interaction_data.user_rating,
                    follow_up_query=interaction_data.follow_up_query,
                    conversation_turn=interaction_data.conversation_turn
                )
                
                session.add(interaction)
                session.commit()
                
                # Publish to Pub/Sub for real-time processing
                if self.publisher:
                    self._publish_analytics_event(interaction_data)
                
                logger.info(f"Logged interaction for session {interaction_data.session_id}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to log interaction: {e}")
                raise
    
    def _publish_analytics_event(self, interaction_data: UserInteractionData):
        """Publish analytics event to Pub/Sub."""
        try:
            event_data = {
                "event_type": "user_interaction",
                "timestamp": interaction_data.timestamp.isoformat(),
                "data": asdict(interaction_data)
            }
            
            # Convert datetime objects to strings for JSON serialization
            event_data["data"]["timestamp"] = interaction_data.timestamp.isoformat()
            
            message_data = json.dumps(event_data).encode("utf-8")
            
            # Publish message
            future = self.publisher.publish(self.topic_path, message_data)
            future.result()  # Wait for the publish to complete
            
            logger.debug(f"Published analytics event for session {interaction_data.session_id}")
            
        except Exception as e:
            logger.warning(f"Failed to publish analytics event: {e}")
            # Don't fail the main operation if Pub/Sub fails
    
    def update_content_analytics(self, content_type: str, content_id: str, 
                                relevance_score: float, user_role: str):
        """Update content utilization metrics."""
        with self.get_db_session() as session:
            try:
                # Get existing record
                content_analytics = session.query(ContentAnalytics).filter_by(
                    content_type=content_type,
                    content_id=content_id
                ).first()
                
                if content_analytics:
                    # Update existing record
                    content_analytics.access_count += 1
                    
                    # Update average relevance score
                    old_count = content_analytics.access_count - 1
                    old_avg = content_analytics.avg_relevance_score
                    content_analytics.avg_relevance_score = (
                        (old_avg * old_count + relevance_score) / content_analytics.access_count
                    )
                    
                    # Update user roles
                    roles = json.loads(content_analytics.user_roles_accessing or "[]")
                    if user_role not in roles:
                        roles.append(user_role)
                        content_analytics.user_roles_accessing = json.dumps(roles)
                    
                    content_analytics.last_accessed = datetime.utcnow()
                    
                else:
                    # Create new record
                    content_analytics = ContentAnalytics(
                        content_type=content_type,
                        content_id=content_id,
                        access_count=1,
                        avg_relevance_score=relevance_score,
                        user_roles_accessing=json.dumps([user_role]),
                        last_accessed=datetime.utcnow()
                    )
                    session.add(content_analytics)
                
                session.commit()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update content analytics: {e}")
                raise
    
    def calculate_daily_business_metrics(self, date: datetime):
        """Calculate and store daily business intelligence metrics."""
        with self.get_db_session() as session:
            try:
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date_start + timedelta(days=1)
                
                # Get sessions by role
                role_query = session.query(
                    UserInteraction.user_role,
                    UserInteraction.session_id
                ).filter(
                    UserInteraction.timestamp >= date_start,
                    UserInteraction.timestamp < date_end
                ).distinct()
                
                role_sessions = {}
                for role, session_id in role_query:
                    if role not in role_sessions:
                        role_sessions[role] = set()
                    role_sessions[role].add(session_id)
                
                # Calculate metrics
                session_durations = session.execute("""
                    SELECT AVG(duration_minutes) FROM (
                        SELECT session_id, 
                               EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) / 60 as duration_minutes
                        FROM user_interactions 
                        WHERE timestamp >= :start_date AND timestamp < :end_date
                        GROUP BY session_id
                    ) as session_durations
                """, {"start_date": date_start, "end_date": date_end}).scalar() or 0.0
                
                # Calculate conversion and engagement metrics
                metrics_query = session.execute("""
                    SELECT 
                        AVG(CASE WHEN query_type = 'technical' THEN 1.0 ELSE 0.0 END) as technical_queries,
                        AVG(CASE WHEN code_snippets_shown > 0 THEN 1.0 ELSE 0.0 END) as code_engagement,
                        AVG(CASE WHEN citations_provided > 0 THEN 1.0 ELSE 0.0 END) as citation_rate
                    FROM user_interactions 
                    WHERE timestamp >= :start_date AND timestamp < :end_date
                """, {"start_date": date_start, "end_date": date_end}).fetchone()
                
                # Create or update business metrics
                business_metrics = session.query(BusinessMetrics).filter_by(date=date_start).first()
                
                if not business_metrics:
                    business_metrics = BusinessMetrics(date=date_start)
                    session.add(business_metrics)
                
                business_metrics.hiring_manager_sessions = (
                    len(role_sessions.get('Hiring Manager (technical)', set())) +
                    len(role_sessions.get('Hiring Manager (nontechnical)', set()))
                )
                business_metrics.developer_sessions = len(role_sessions.get('Software Developer', set()))
                business_metrics.casual_visitor_sessions = len(role_sessions.get('Just looking around', set()))
                business_metrics.avg_session_duration = session_durations
                business_metrics.conversion_to_detailed_queries = metrics_query[0] or 0.0
                business_metrics.code_display_engagement = metrics_query[1] or 0.0
                business_metrics.citation_click_through_rate = metrics_query[2] or 0.0
                
                session.commit()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to calculate business metrics: {e}")
                raise
    
    def get_user_behavior_insights(self, days: int = 30) -> Dict[str, Any]:
        """Generate user behavior insights using PostgreSQL."""
        with self.get_db_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Use pandas for complex analytics queries
            query = """
            SELECT user_role, query_type, COUNT(*) as interactions,
                   AVG(response_time) as avg_response_time,
                   AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
            FROM user_interactions 
            WHERE timestamp >= %s
            GROUP BY user_role, query_type
            ORDER BY interactions DESC
            """
            
            df = pd.read_sql_query(query, self.engine, params=[cutoff_date])
            
            return {
                'period_days': days,
                'insights': df.to_dict('records'),
                'total_interactions': len(df)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the analytics system."""
        try:
            with self.get_db_session() as session:
                # Test database connection
                result = session.execute("SELECT 1").scalar()
                db_healthy = result == 1
                
                # Get basic stats
                total_interactions = session.query(UserInteraction).count()
                recent_interactions = session.query(UserInteraction).filter(
                    UserInteraction.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                return {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "database_connected": db_healthy,
                    "total_interactions": total_interactions,
                    "recent_interactions_24h": recent_interactions,
                    "pubsub_enabled": self.publisher is not None,
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global analytics instance
cloud_analytics = CloudAnalytics()
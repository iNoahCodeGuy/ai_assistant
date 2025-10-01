"""Comprehensive analytics system for Noah's AI Assistant.

This module provides enhanced analytics capabilities beyond basic performance monitoring,
focusing on user behavior, content effectiveness, and business intelligence.
"""
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserInteraction:
    """Detailed user interaction tracking."""
    session_id: str
    timestamp: datetime
    user_role: str
    query: str
    query_type: str  # technical, career, mma, fun, general
    response_time: float
    response_length: int
    code_snippets_shown: int
    citations_provided: int
    success: bool
    user_rating: Optional[int] = None  # 1-5 if provided
    follow_up_query: bool = False
    conversation_turn: int = 1


@dataclass
class ContentAnalytics:
    """Content utilization and effectiveness metrics."""
    content_type: str  # career_kb, code_snippet, mma_link
    content_id: str
    access_count: int
    avg_relevance_score: float
    user_roles_accessing: List[str]
    last_accessed: datetime


@dataclass
class BusinessMetrics:
    """Business intelligence metrics."""
    date: datetime
    hiring_manager_sessions: int
    developer_sessions: int
    casual_visitor_sessions: int
    avg_session_duration: float
    conversion_to_detailed_queries: float
    code_display_engagement: float
    citation_click_through_rate: float


class ComprehensiveAnalytics:
    """Enhanced analytics system for user behavior and business intelligence."""
    
    def __init__(self, db_path: str = "analytics/comprehensive_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Enable thread safety and WAL mode for better concurrent access
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._create_tables()
    
    def _create_tables(self):
        """Create analytics database tables."""
        with self.connection:
            # User interactions table
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    user_role TEXT,
                    query TEXT,
                    query_type TEXT,
                    response_time REAL,
                    response_length INTEGER,
                    code_snippets_shown INTEGER,
                    citations_provided INTEGER,
                    success INTEGER,
                    user_rating INTEGER,
                    follow_up_query INTEGER,
                    conversation_turn INTEGER
                )
            ''')
            
            # Content analytics table
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS content_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT,
                    content_id TEXT,
                    access_count INTEGER,
                    avg_relevance_score REAL,
                    user_roles_accessing TEXT,
                    last_accessed TEXT,
                    UNIQUE(content_type, content_id)
                )
            ''')
            
            # Business metrics table
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS business_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    hiring_manager_sessions INTEGER,
                    developer_sessions INTEGER,
                    casual_visitor_sessions INTEGER,
                    avg_session_duration REAL,
                    conversion_to_detailed_queries REAL,
                    code_display_engagement REAL,
                    citation_click_through_rate REAL,
                    UNIQUE(date)
                )
            ''')
    
    def log_interaction(self, interaction: UserInteraction):
        """Log a user interaction with detailed analytics."""
        with self.connection:
            self.connection.execute('''
                INSERT INTO user_interactions 
                (session_id, timestamp, user_role, query, query_type, response_time, 
                 response_length, code_snippets_shown, citations_provided, success, 
                 user_rating, follow_up_query, conversation_turn)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction.session_id,
                interaction.timestamp.isoformat(),
                interaction.user_role,
                interaction.query,
                interaction.query_type,
                interaction.response_time,
                interaction.response_length,
                interaction.code_snippets_shown,
                interaction.citations_provided,
                int(interaction.success),
                interaction.user_rating,
                int(interaction.follow_up_query),
                interaction.conversation_turn
            ))
    
    def update_content_analytics(self, content_type: str, content_id: str, 
                                relevance_score: float, user_role: str):
        """Update content utilization metrics."""
        with self.connection:
            # Get existing data
            cursor = self.connection.execute('''
                SELECT access_count, avg_relevance_score, user_roles_accessing 
                FROM content_analytics 
                WHERE content_type = ? AND content_id = ?
            ''', (content_type, content_id))
            
            result = cursor.fetchone()
            
            if result:
                access_count, avg_relevance, roles_json = result
                access_count += 1
                
                # Update average relevance score
                avg_relevance = ((avg_relevance * (access_count - 1)) + relevance_score) / access_count
                
                # Update user roles list
                roles = json.loads(roles_json) if roles_json else []
                if user_role not in roles:
                    roles.append(user_role)
                
                self.connection.execute('''
                    UPDATE content_analytics 
                    SET access_count = ?, avg_relevance_score = ?, 
                        user_roles_accessing = ?, last_accessed = ?
                    WHERE content_type = ? AND content_id = ?
                ''', (access_count, avg_relevance, json.dumps(roles), 
                      datetime.now().isoformat(), content_type, content_id))
            else:
                # Insert new record
                self.connection.execute('''
                    INSERT INTO content_analytics 
                    (content_type, content_id, access_count, avg_relevance_score, 
                     user_roles_accessing, last_accessed)
                    VALUES (?, ?, 1, ?, ?, ?)
                ''', (content_type, content_id, relevance_score, 
                      json.dumps([user_role]), datetime.now().isoformat()))
    
    def calculate_daily_business_metrics(self, date: datetime):
        """Calculate and store daily business intelligence metrics."""
        date_str = date.date().isoformat()
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        cursor = self.connection.cursor()
        
        # Get sessions by role
        cursor.execute('''
            SELECT user_role, COUNT(DISTINCT session_id) as sessions
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY user_role
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        role_sessions = dict(cursor.fetchall())
        
        # Calculate session durations
        cursor.execute('''
            SELECT AVG(duration) FROM (
                SELECT session_id, 
                       (julianday(MAX(timestamp)) - julianday(MIN(timestamp))) * 24 * 60 as duration
                FROM user_interactions 
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY session_id
            )
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        avg_duration = cursor.fetchone()[0] or 0.0
        
        # Calculate conversion rates and engagement metrics
        cursor.execute('''
            SELECT 
                AVG(CASE WHEN query_type = 'technical' THEN 1.0 ELSE 0.0 END) as technical_queries,
                AVG(CASE WHEN code_snippets_shown > 0 THEN 1.0 ELSE 0.0 END) as code_engagement,
                AVG(CASE WHEN citations_provided > 0 THEN 1.0 ELSE 0.0 END) as citation_rate
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp < ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        conversion_data = cursor.fetchone()
        
        business_metrics = BusinessMetrics(
            date=date,
            hiring_manager_sessions=role_sessions.get('Hiring Manager (technical)', 0) + 
                                   role_sessions.get('Hiring Manager (nontechnical)', 0),
            developer_sessions=role_sessions.get('Software Developer', 0),
            casual_visitor_sessions=role_sessions.get('Just looking around', 0),
            avg_session_duration=avg_duration,
            conversion_to_detailed_queries=conversion_data[0] or 0.0,
            code_display_engagement=conversion_data[1] or 0.0,
            citation_click_through_rate=conversion_data[2] or 0.0
        )
        
        # Store business metrics
        with self.connection:
            self.connection.execute('''
                INSERT OR REPLACE INTO business_metrics 
                (date, hiring_manager_sessions, developer_sessions, casual_visitor_sessions,
                 avg_session_duration, conversion_to_detailed_queries, 
                 code_display_engagement, citation_click_through_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date_str,
                business_metrics.hiring_manager_sessions,
                business_metrics.developer_sessions,
                business_metrics.casual_visitor_sessions,
                business_metrics.avg_session_duration,
                business_metrics.conversion_to_detailed_queries,
                business_metrics.code_display_engagement,
                business_metrics.citation_click_through_rate
            ))
    
    def get_user_behavior_insights(self, days: int = 30) -> Dict[str, Any]:
        """Generate user behavior insights for the last N days."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = self.connection.cursor()
        
        # Role distribution
        cursor.execute('''
            SELECT user_role, COUNT(*) as interactions
            FROM user_interactions 
            WHERE timestamp >= ?
            GROUP BY user_role
            ORDER BY interactions DESC
        ''', (cutoff_date,))
        
        role_distribution = dict(cursor.fetchall())
        
        # Query patterns by role
        cursor.execute('''
            SELECT user_role, query_type, COUNT(*) as count
            FROM user_interactions 
            WHERE timestamp >= ?
            GROUP BY user_role, query_type
        ''', (cutoff_date,))
        
        query_patterns = {}
        for role, query_type, count in cursor.fetchall():
            if role not in query_patterns:
                query_patterns[role] = {}
            query_patterns[role][query_type] = count
        
        # Success rates by role
        cursor.execute('''
            SELECT user_role, AVG(success) as success_rate, AVG(response_time) as avg_response_time
            FROM user_interactions 
            WHERE timestamp >= ?
            GROUP BY user_role
        ''', (cutoff_date,))
        
        performance_by_role = {
            role: {'success_rate': success_rate, 'avg_response_time': avg_time}
            for role, success_rate, avg_time in cursor.fetchall()
        }
        
        return {
            'period_days': days,
            'role_distribution': role_distribution,
            'query_patterns_by_role': query_patterns,
            'performance_by_role': performance_by_role,
            'total_interactions': sum(role_distribution.values())
        }
    
    def get_content_effectiveness_report(self) -> Dict[str, Any]:
        """Generate content effectiveness analysis."""
        cursor = self.connection.cursor()
        
        # Most accessed content
        cursor.execute('''
            SELECT content_type, content_id, access_count, avg_relevance_score
            FROM content_analytics 
            ORDER BY access_count DESC
            LIMIT 10
        ''')
        
        top_content = [
            {
                'type': content_type,
                'id': content_id,
                'access_count': access_count,
                'relevance_score': avg_relevance_score
            }
            for content_type, content_id, access_count, avg_relevance_score in cursor.fetchall()
        ]
        
        # Content performance by type
        cursor.execute('''
            SELECT content_type, 
                   COUNT(*) as unique_items,
                   SUM(access_count) as total_accesses,
                   AVG(avg_relevance_score) as avg_relevance
            FROM content_analytics 
            GROUP BY content_type
        ''')
        
        content_performance = {
            content_type: {
                'unique_items': unique_items,
                'total_accesses': total_accesses,
                'avg_relevance': avg_relevance
            }
            for content_type, unique_items, total_accesses, avg_relevance in cursor.fetchall()
        }
        
        return {
            'top_content': top_content,
            'performance_by_type': content_performance
        }
    
    def get_business_intelligence_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Generate business intelligence dashboard data."""
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        cursor = self.connection.cursor()
        
        # Get recent business metrics
        cursor.execute('''
            SELECT * FROM business_metrics 
            WHERE date >= ?
            ORDER BY date DESC
        ''', (cutoff_date,))
        
        metrics_data = cursor.fetchall()
        
        if not metrics_data:
            return {'error': 'No business metrics data available'}
        
        # Calculate trends
        df = pd.DataFrame(metrics_data, columns=[
            'id', 'date', 'hiring_manager_sessions', 'developer_sessions',
            'casual_visitor_sessions', 'avg_session_duration',
            'conversion_to_detailed_queries', 'code_display_engagement',
            'citation_click_through_rate'
        ])
        
        return {
            'period_days': days,
            'total_hiring_manager_sessions': df['hiring_manager_sessions'].sum(),
            'total_developer_sessions': df['developer_sessions'].sum(),
            'total_casual_sessions': df['casual_visitor_sessions'].sum(),
            'avg_session_duration': df['avg_session_duration'].mean(),
            'avg_conversion_rate': df['conversion_to_detailed_queries'].mean(),
            'avg_code_engagement': df['code_display_engagement'].mean(),
            'avg_citation_usage': df['citation_click_through_rate'].mean(),
            'daily_trends': df.to_dict('records')
        }
    
    def get_most_common_questions(self, role: Optional[str] = None, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common questions, optionally filtered by role."""
        with self._lock:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor = self.connection.cursor()
            
            if role:
                cursor.execute('''
                    SELECT query, COUNT(*) as frequency, 
                           AVG(success) as success_rate,
                           AVG(response_time) as avg_response_time,
                           query_type
                    FROM user_interactions 
                    WHERE timestamp >= ? AND user_role = ?
                    GROUP BY LOWER(TRIM(query))
                    ORDER BY frequency DESC
                    LIMIT ?
                ''', (cutoff_date, role, limit))
            else:
                cursor.execute('''
                    SELECT query, COUNT(*) as frequency, 
                           AVG(success) as success_rate,
                           AVG(response_time) as avg_response_time,
                           query_type,
                           GROUP_CONCAT(DISTINCT user_role) as roles
                    FROM user_interactions 
                    WHERE timestamp >= ?
                    GROUP BY LOWER(TRIM(query))
                    ORDER BY frequency DESC
                    LIMIT ?
                ''', (cutoff_date, limit))
            
            results = []
            for row in cursor.fetchall():
                if role:
                    query, frequency, success_rate, avg_response_time, query_type = row
                    roles = [role]
                else:
                    query, frequency, success_rate, avg_response_time, query_type, roles_str = row
                    roles = roles_str.split(',') if roles_str else []
                
                results.append({
                    'question': query,
                    'frequency': frequency,
                    'success_rate': success_rate,
                    'avg_response_time': avg_response_time,
                    'query_type': query_type,
                    'roles': roles
                })
            
            return results
    
    def get_common_questions_by_role(self, days: int = 30, limit_per_role: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Get most common questions grouped by role."""
        roles = [
            'Hiring Manager (technical)',
            'Hiring Manager (nontechnical)', 
            'Software Developer',
            'Just looking around'
        ]
        
        result = {}
        for role in roles:
            result[role] = self.get_most_common_questions(role=role, days=days, limit=limit_per_role)
        
        return result
    
    def get_suggested_questions_for_role(self, role: str, limit: int = 5) -> List[str]:
        """Get suggested questions for a specific role based on successful past queries."""
        cursor = self.connection.cursor()
        
        # Get successful questions for this role with high response quality
        cursor.execute('''
            SELECT query, COUNT(*) as frequency,
                   AVG(success) as success_rate,
                   AVG(CASE WHEN code_snippets_shown > 0 THEN 1.0 ELSE 0.0 END) as code_engagement
            FROM user_interactions 
            WHERE user_role = ? AND success = 1
            GROUP BY LOWER(TRIM(query))
            HAVING frequency >= 2 AND success_rate >= 0.8
            ORDER BY frequency DESC, code_engagement DESC
            LIMIT ?
        ''', (role, limit))
        
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close the database connection."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()


# Integration helper for existing systems
def create_interaction_from_rag_result(session_id: str, user_role: str, query: str, 
                                     query_type: str, response_time: float,
                                     rag_result: Dict[str, Any]) -> UserInteraction:
    """Create UserInteraction from RAG engine result."""
    return UserInteraction(
        session_id=session_id,
        timestamp=datetime.now(),
        user_role=user_role,
        query=query,
        query_type=query_type,
        response_time=response_time,
        response_length=len(str(rag_result.get('response', ''))),
        code_snippets_shown=len(rag_result.get('code_snippets', [])),
        citations_provided=sum(1 for snippet in rag_result.get('code_snippets', []) 
                              if snippet.get('citation')),
        success=bool(rag_result.get('response'))
    )

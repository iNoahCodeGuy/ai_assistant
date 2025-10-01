"""Core data management orchestration."""

import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .privacy import PrivacyManager
from .quality import DataQualityMonitor
from .backup import BackupManager
from .performance import PerformanceMonitor
from .models import SessionAnalytics, DataRetentionPolicy
from ..comprehensive_analytics import UserInteraction, ContentAnalytics, BusinessMetrics

logger = logging.getLogger(__name__)


class AnalyticsDataManager:
    """Enhanced data management system for Noah's AI Assistant analytics."""
    
    def __init__(self, db_path: str = "analytics.db", enable_privacy: bool = True):
        self.db_path = Path(db_path)
        self.connection_lock = threading.RLock()
        self.enable_privacy = enable_privacy
        
        # Initialize connection with optimizations
        self.connection = self._create_connection()
        
        # Initialize management components
        self.privacy_manager = PrivacyManager() if enable_privacy else None
        self.quality_monitor = DataQualityMonitor(self.connection)
        self.backup_manager = BackupManager(str(self.db_path))
        self.performance_monitor = PerformanceMonitor(self.connection)
        
        # Setup database schema
        self._create_tables()
        self._setup_indexes()
        self._setup_retention_policies()
        
        logger.info(f"AnalyticsDataManager initialized with database: {self.db_path}")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create optimized database connection."""
        connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,  # Allow multi-threaded access
            timeout=30.0
        )
        
        # Enable WAL mode for better concurrency
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA cache_size=10000")
        connection.execute("PRAGMA temp_store=MEMORY")
        
        return connection
    
    def _create_tables(self):
        """Create all necessary database tables."""
        with self.connection_lock:
            cursor = self.connection.cursor()
            
            # Enhanced user interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    user_role TEXT NOT NULL,
                    query TEXT NOT NULL,
                    query_type TEXT,
                    response_time REAL,
                    response_length INTEGER,
                    code_snippets_shown INTEGER DEFAULT 0,
                    citations_provided INTEGER DEFAULT 0,
                    success BOOLEAN DEFAULT 1,
                    user_rating REAL,
                    follow_up_query BOOLEAN DEFAULT 0,
                    conversation_turn INTEGER DEFAULT 1,
                    privacy_score REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Session analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_analytics (
                    session_id TEXT PRIMARY KEY,
                    user_role TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    last_activity DATETIME NOT NULL,
                    total_queries INTEGER DEFAULT 0,
                    successful_queries INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0.0,
                    total_code_snippets INTEGER DEFAULT 0,
                    total_citations INTEGER DEFAULT 0,
                    session_rating REAL,
                    conversion_achieved BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Content analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    engagement_score REAL DEFAULT 0.0,
                    effectiveness_score REAL DEFAULT 0.0,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Business metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Query performance tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    result_count INTEGER,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System performance metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Data retention policies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_retention_policy (
                    table_name TEXT PRIMARY KEY,
                    retention_days INTEGER NOT NULL,
                    archive_after_days INTEGER NOT NULL,
                    cleanup_enabled BOOLEAN DEFAULT 1,
                    last_cleanup DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
    
    def _setup_indexes(self):
        """Create performance indexes."""
        with self.connection_lock:
            cursor = self.connection.cursor()
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_interactions_session ON user_interactions(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON user_interactions(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_interactions_user_role ON user_interactions(user_role)",
                "CREATE INDEX IF NOT EXISTS idx_interactions_success ON user_interactions(success)",
                "CREATE INDEX IF NOT EXISTS idx_session_start_time ON session_analytics(start_time)",
                "CREATE INDEX IF NOT EXISTS idx_session_user_role ON session_analytics(user_role)",
                "CREATE INDEX IF NOT EXISTS idx_content_timestamp ON content_analytics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_business_timestamp ON business_metrics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_business_metric_name ON business_metrics(metric_name)",
                "CREATE INDEX IF NOT EXISTS idx_query_perf_timestamp ON query_performance(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_system_perf_timestamp ON system_performance(timestamp)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            self.connection.commit()
    
    def _setup_retention_policies(self):
        """Setup default data retention policies."""
        default_policies = [
            DataRetentionPolicy("user_interactions", 365, 90),
            DataRetentionPolicy("session_analytics", 365, 90),
            DataRetentionPolicy("content_analytics", 180, 60),
            DataRetentionPolicy("business_metrics", 365, 90),
            DataRetentionPolicy("query_performance", 30, 7),
            DataRetentionPolicy("system_performance", 90, 30)
        ]
        
        for policy in default_policies:
            self.set_retention_policy(policy)
    
    def record_interaction(self, interaction: UserInteraction) -> bool:
        """Record a user interaction with privacy controls."""
        try:
            with self.connection_lock:
                # Apply privacy controls if enabled
                if self.privacy_manager:
                    interaction = self.privacy_manager.anonymize_interaction(interaction)
                    privacy_score = 0.0 if self.privacy_manager.check_pii_presence(interaction.query) else 1.0
                else:
                    privacy_score = 1.0
                
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO user_interactions 
                    (session_id, timestamp, user_role, query, query_type, response_time, 
                     response_length, code_snippets_shown, citations_provided, success, 
                     user_rating, follow_up_query, conversation_turn, privacy_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.session_id,
                    interaction.timestamp,
                    interaction.user_role,
                    interaction.query,
                    interaction.query_type,
                    interaction.response_time,
                    interaction.response_length,
                    interaction.code_snippets_shown,
                    interaction.citations_provided,
                    interaction.success,
                    interaction.user_rating,
                    interaction.follow_up_query,
                    interaction.conversation_turn,
                    privacy_score
                ))
                
                self.connection.commit()
                
                # Update session analytics
                self._update_session_analytics(interaction)
                
                return True
                
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return False
    
    def _update_session_analytics(self, interaction: UserInteraction):
        """Update session-level analytics."""
        try:
            cursor = self.connection.cursor()
            
            # Check if session exists
            cursor.execute("""
                SELECT total_queries, successful_queries, avg_response_time, 
                       total_code_snippets, total_citations 
                FROM session_analytics 
                WHERE session_id = ?
            """, (interaction.session_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing session
                total_queries, successful_queries, avg_response_time, total_code_snippets, total_citations = result
                
                # Calculate new averages
                new_total = total_queries + 1
                new_successful = successful_queries + (1 if interaction.success else 0)
                new_avg_response = ((avg_response_time * total_queries) + interaction.response_time) / new_total
                new_code_snippets = total_code_snippets + interaction.code_snippets_shown
                new_citations = total_citations + interaction.citations_provided
                
                cursor.execute("""
                    UPDATE session_analytics 
                    SET total_queries = ?, successful_queries = ?, avg_response_time = ?,
                        total_code_snippets = ?, total_citations = ?, last_activity = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (new_total, new_successful, new_avg_response, new_code_snippets, 
                     new_citations, interaction.timestamp, interaction.session_id))
            else:
                # Create new session
                cursor.execute("""
                    INSERT INTO session_analytics 
                    (session_id, user_role, start_time, last_activity, total_queries,
                     successful_queries, avg_response_time, total_code_snippets, total_citations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.session_id,
                    interaction.user_role,
                    interaction.timestamp,
                    interaction.timestamp,
                    1,
                    1 if interaction.success else 0,
                    interaction.response_time,
                    interaction.code_snippets_shown,
                    interaction.citations_provided
                ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating session analytics: {e}")
    
    def record_content_analytics(self, analytics: ContentAnalytics) -> bool:
        """Record content analytics data."""
        try:
            with self.connection_lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO content_analytics 
                    (content_type, engagement_score, effectiveness_score, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    analytics.content_type,
                    analytics.engagement_score,
                    analytics.effectiveness_score,
                    analytics.timestamp,
                    analytics.metadata
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error recording content analytics: {e}")
            return False
    
    def record_business_metrics(self, metrics: BusinessMetrics) -> bool:
        """Record business metrics data."""
        try:
            with self.connection_lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO business_metrics 
                    (metric_name, metric_value, metric_type, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metrics.metric_name,
                    metrics.metric_value,
                    metrics.metric_type,
                    metrics.timestamp,
                    metrics.metadata
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error recording business metrics: {e}")
            return False
    
    def get_analytics_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            with self.connection_lock:
                cursor = self.connection.cursor()
                
                # User interaction metrics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_interactions,
                        COUNT(DISTINCT session_id) as unique_sessions,
                        AVG(response_time) as avg_response_time,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                        AVG(user_rating) as avg_rating,
                        SUM(code_snippets_shown) as total_code_snippets,
                        SUM(citations_provided) as total_citations
                    FROM user_interactions 
                    WHERE timestamp > ?
                """, (cutoff_date,))
                
                interaction_stats = cursor.fetchone()
                
                # Session metrics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        AVG(total_queries) as avg_queries_per_session,
                        AVG(avg_response_time) as avg_session_response_time,
                        COUNT(CASE WHEN conversion_achieved = 1 THEN 1 END) * 100.0 / COUNT(*) as conversion_rate
                    FROM session_analytics 
                    WHERE start_time > ?
                """, (cutoff_date,))
                
                session_stats = cursor.fetchone()
                
                # Performance metrics
                performance_metrics = self.performance_monitor.check_performance_metrics()
                
                # Quality metrics
                quality_score = self.quality_monitor.generate_quality_score()
                
                summary = {
                    'period_days': days_back,
                    'generated_at': datetime.now().isoformat(),
                    'interaction_metrics': {
                        'total_interactions': interaction_stats[0] or 0,
                        'unique_sessions': interaction_stats[1] or 0,
                        'avg_response_time': round(interaction_stats[2] or 0, 2),
                        'success_rate': round(interaction_stats[3] or 0, 2),
                        'avg_rating': round(interaction_stats[4] or 0, 2),
                        'total_code_snippets': interaction_stats[5] or 0,
                        'total_citations': interaction_stats[6] or 0
                    },
                    'session_metrics': {
                        'total_sessions': session_stats[0] or 0,
                        'avg_queries_per_session': round(session_stats[1] or 0, 2),
                        'avg_session_response_time': round(session_stats[2] or 0, 2),
                        'conversion_rate': round(session_stats[3] or 0, 2)
                    },
                    'performance_metrics': performance_metrics,
                    'data_quality_score': round(quality_score, 2),
                    'privacy_enabled': self.enable_privacy
                }
                
                return summary
                
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {'error': str(e)}
    
    def set_retention_policy(self, policy: DataRetentionPolicy) -> bool:
        """Set or update data retention policy for a table."""
        try:
            with self.connection_lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO data_retention_policy 
                    (table_name, retention_days, archive_after_days, cleanup_enabled, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (policy.table_name, policy.retention_days, policy.archive_after_days, policy.cleanup_enabled))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error setting retention policy: {e}")
            return False
    
    def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data based on retention policies."""
        cleanup_results = {}
        
        try:
            with self.connection_lock:
                cursor = self.connection.cursor()
                
                # Get all retention policies
                cursor.execute("SELECT * FROM data_retention_policy WHERE cleanup_enabled = 1")
                policies = cursor.fetchall()
                
                for policy in policies:
                    table_name, retention_days, archive_days, cleanup_enabled, last_cleanup, _, _ = policy
                    
                    if not cleanup_enabled:
                        continue
                    
                    # Calculate cutoff date
                    cutoff_date = datetime.now() - timedelta(days=retention_days)
                    
                    # Check table schema to find date columns
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # Determine which date column to use
                    date_column = None
                    if 'created_at' in columns:
                        date_column = 'created_at'
                    elif 'timestamp' in columns:
                        date_column = 'timestamp'
                    elif 'date' in columns:
                        date_column = 'date'
                    
                    if date_column:
                        # Delete old records
                        cursor.execute(f"""
                            DELETE FROM {table_name} 
                            WHERE {date_column} < ?
                        """, (cutoff_date,))
                        
                        deleted_count = cursor.rowcount
                        cleanup_results[table_name] = deleted_count
                    else:
                        cleanup_results[table_name] = 0
                    
                    # Update last cleanup time
                    cursor.execute("""
                        UPDATE data_retention_policy 
                        SET last_cleanup = CURRENT_TIMESTAMP 
                        WHERE table_name = ?
                    """, (table_name,))
                
                self.connection.commit()
                logger.info(f"Data cleanup completed: {cleanup_results}")
                
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            cleanup_results['error'] = str(e)
        
        return cleanup_results
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'status': 'healthy',
                    'size_mb': round(self.db_path.stat().st_size / (1024 * 1024), 2) if self.db_path.exists() else 0,
                    'connection_status': 'connected'
                },
                'components': {
                    'privacy_manager': 'enabled' if self.privacy_manager else 'disabled',
                    'quality_monitor': 'active',
                    'backup_manager': 'active',
                    'performance_monitor': 'active'
                },
                'data_quality': self.quality_monitor.generate_quality_score(),
                'performance': self.performance_monitor.check_performance_metrics(),
                'backup_status': self.backup_manager.get_backup_status(),
                'alerts': self.performance_monitor.get_recent_alerts(hours_back=24)
            }
            
            # Overall health score
            scores = [
                health_status['data_quality'],
                1.0 if health_status['performance']['success_rate'] > 0.8 else 0.5,
                1.0 if health_status['backup_status']['backup_count'] > 0 else 0.0
            ]
            health_status['overall_health_score'] = sum(scores) / len(scores)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'error': str(e)}
    
    def run_daily_maintenance(self):
        """Run daily maintenance tasks."""
        logger.info("Starting daily maintenance tasks...")
        
        # 1. Run data quality checks
        quality_report = self.quality_monitor.get_quality_report()
        logger.info(f"Data quality score: {quality_report.get('overall_score', 0):.2f}")
        
        # 2. Check performance metrics
        performance_report = self.performance_monitor.evaluate_alerts()
        if performance_report:
            logger.warning(f"Performance alerts: {len(performance_report)}")
        
        # 3. Create backup
        backup_path = self.backup_manager.create_backup()
        if backup_path:
            logger.info(f"Daily backup completed: {backup_path}")
        else:
            logger.error("Daily backup failed")
        
        # 4. Cleanup old backups
        removed_count = self.backup_manager.cleanup_old_backups()
        if removed_count > 0:
            logger.info(f"Removed {removed_count} old backups")
        
        # 5. Archive old data (if needed)
        cleanup_results = self.cleanup_old_data()
        if cleanup_results:
            # Sum only numeric values (ignore error strings)
            numeric_values = [v for v in cleanup_results.values() if isinstance(v, int)]
            total_cleaned = sum(numeric_values) if numeric_values else 0
            if total_cleaned > 0:
                logger.info(f"Archived {total_cleaned} old records")
        
        logger.info("Daily maintenance tasks completed")
    
    def close(self):
        """Close database connection."""
        try:
            with self.connection_lock:
                if self.connection:
                    self.connection.close()
                    logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

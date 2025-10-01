"""Data quality monitoring and validation."""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataQualityMonitor:
    """Monitor and ensure data quality."""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.quality_thresholds = {
            'completeness_threshold': 0.95,  # 95% completeness required
            'max_response_time': 300.0,  # 5 minutes max response time
            'min_success_rate': 0.8,  # 80% minimum success rate
        }
    
    def check_data_completeness(self, table_name: str, required_fields: List[str]) -> Dict[str, float]:
        """Check completeness of required fields in a table."""
        completeness_scores = {}
        
        try:
            cursor = self.connection.cursor()
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            
            if total_count == 0:
                return {field: 0.0 for field in required_fields}
            
            # Check each required field
            for field in required_fields:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE {field} IS NOT NULL AND {field} != ''
                """)
                non_null_count = cursor.fetchone()[0]
                completeness_scores[field] = non_null_count / total_count
                
        except sqlite3.Error as e:
            logger.error(f"Error checking completeness for {table_name}: {e}")
            completeness_scores = {field: 0.0 for field in required_fields}
        
        return completeness_scores
    
    def check_data_consistency(self, days_back: int = 7) -> Dict[str, List[str]]:
        """Check for data consistency issues."""
        issues = {
            'anomalies': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Check for impossible response times
            cursor.execute("""
                SELECT COUNT(*) FROM user_interactions 
                WHERE response_time > ? AND timestamp > ?
            """, (self.quality_thresholds['max_response_time'], cutoff_date))
            
            high_response_count = cursor.fetchone()[0]
            if high_response_count > 0:
                issues['anomalies'].append(f"{high_response_count} interactions with response time > {self.quality_thresholds['max_response_time']}s")
            
            # Check for negative response times
            cursor.execute("""
                SELECT COUNT(*) FROM user_interactions 
                WHERE response_time < 0 AND timestamp > ?
            """, (cutoff_date,))
            
            negative_response_count = cursor.fetchone()[0]
            if negative_response_count > 0:
                issues['errors'].append(f"{negative_response_count} interactions with negative response time")
            
            # Check success rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM user_interactions 
                WHERE timestamp > ?
            """, (cutoff_date,))
            
            result = cursor.fetchone()
            if result[0] > 0:
                success_rate = result[1] / result[0]
                if success_rate < self.quality_thresholds['min_success_rate']:
                    issues['warnings'].append(f"Success rate ({success_rate:.2%}) below threshold ({self.quality_thresholds['min_success_rate']:.2%})")
            
            # Check for duplicate sessions
            cursor.execute("""
                SELECT session_id, COUNT(*) as count 
                FROM user_interactions 
                WHERE timestamp > ?
                GROUP BY session_id 
                HAVING COUNT(*) > 50
            """, (cutoff_date,))
            
            high_activity_sessions = cursor.fetchall()
            if high_activity_sessions:
                issues['warnings'].extend([
                    f"Session {session_id} has {count} interactions (potential bot activity)"
                    for session_id, count in high_activity_sessions
                ])
                
        except sqlite3.Error as e:
            logger.error(f"Error checking data consistency: {e}")
            issues['errors'].append(f"Database error during consistency check: {e}")
        
        return issues
    
    def generate_quality_score(self, table_name: str = 'user_interactions') -> float:
        """Generate overall data quality score (0-1)."""
        try:
            # Check completeness for key fields
            required_fields = ['session_id', 'query', 'response_time', 'success']
            completeness_scores = self.check_data_completeness(table_name, required_fields)
            avg_completeness = sum(completeness_scores.values()) / len(completeness_scores) if completeness_scores else 0
            
            # Check consistency
            consistency_issues = self.check_data_consistency()
            total_issues = sum(len(issues) for issues in consistency_issues.values())
            
            # Weight completeness higher than consistency
            completeness_weight = 0.7
            consistency_weight = 0.3
            
            # Consistency score (fewer issues = higher score)
            consistency_score = max(0, 1 - (total_issues * 0.1))  # Each issue reduces score by 0.1
            
            overall_score = (avg_completeness * completeness_weight) + (consistency_score * consistency_weight)
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            logger.error(f"Error generating quality score: {e}")
            return 0.0
    
    def get_quality_report(self) -> Dict:
        """Generate comprehensive quality report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': self.generate_quality_score(),
            'completeness': {},
            'consistency': {},
            'recommendations': []
        }
        
        try:
            # Completeness analysis
            required_fields = ['session_id', 'query', 'response_time', 'success', 'user_role']
            report['completeness'] = self.check_data_completeness('user_interactions', required_fields)
            
            # Consistency analysis
            report['consistency'] = self.check_data_consistency()
            
            # Generate recommendations
            if report['overall_score'] < 0.8:
                report['recommendations'].append("Overall data quality is below recommended threshold")
            
            for field, score in report['completeness'].items():
                if score < self.quality_thresholds['completeness_threshold']:
                    report['recommendations'].append(f"Improve {field} completeness (currently {score:.1%})")
            
            if report['consistency']['errors']:
                report['recommendations'].append("Address data consistency errors immediately")
            
            if report['consistency']['anomalies']:
                report['recommendations'].append("Investigate data anomalies for potential issues")
                
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            report['error'] = str(e)
        
        return report
    
    def set_quality_threshold(self, threshold_name: str, value: float) -> bool:
        """Update quality threshold."""
        if threshold_name in self.quality_thresholds:
            self.quality_thresholds[threshold_name] = value
            logger.info(f"Updated {threshold_name} to {value}")
            return True
        return False

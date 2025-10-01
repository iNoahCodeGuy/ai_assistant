"""Performance monitoring and alerting."""

import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PerformanceAlert:
    """Performance alert configuration."""
    metric_name: str
    threshold: float
    operator: str  # 'gt', 'lt', 'eq'
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


class PerformanceMonitor:
    """Monitor system performance and generate alerts."""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Default alert configurations
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default performance alerts."""
        self.alerts = {
            'avg_response_time': PerformanceAlert(
                metric_name='avg_response_time',
                threshold=10.0,  # 10 seconds
                operator='gt'
            ),
            'success_rate': PerformanceAlert(
                metric_name='success_rate',
                threshold=0.8,  # 80%
                operator='lt'
            ),
            'query_volume': PerformanceAlert(
                metric_name='query_volume',
                threshold=1000,  # 1000 queries per hour
                operator='gt'
            ),
            'error_rate': PerformanceAlert(
                metric_name='error_rate',
                threshold=0.1,  # 10% error rate
                operator='gt'
            )
        }
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def check_performance_metrics(self, hours_back: int = 1) -> Dict[str, float]:
        """Check current performance metrics."""
        metrics = {}
        
        try:
            cursor = self.connection.cursor()
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Average response time
            cursor.execute("""
                SELECT AVG(response_time) 
                FROM user_interactions 
                WHERE timestamp > ? AND response_time IS NOT NULL
            """, (cutoff_time,))
            
            result = cursor.fetchone()
            metrics['avg_response_time'] = result[0] if result[0] is not None else 0.0
            
            # Success rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM user_interactions 
                WHERE timestamp > ?
            """, (cutoff_time,))
            
            result = cursor.fetchone()
            if result[0] > 0:
                metrics['success_rate'] = result[1] / result[0]
            else:
                metrics['success_rate'] = 1.0
            
            # Query volume per hour
            metrics['query_volume'] = result[0] if result[0] else 0
            
            # Error rate
            metrics['error_rate'] = 1.0 - metrics['success_rate']
            
            # Database size and performance
            cursor.execute("SELECT COUNT(*) FROM user_interactions")
            metrics['total_interactions'] = cursor.fetchone()[0]
            
            # Query execution time for a sample query
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM user_interactions WHERE timestamp > ?", (cutoff_time,))
            cursor.fetchone()
            metrics['db_query_time'] = time.time() - start_time
            
        except sqlite3.Error as e:
            logger.error(f"Error checking performance metrics: {e}")
            metrics = {
                'avg_response_time': 0.0,
                'success_rate': 0.0,
                'query_volume': 0,
                'error_rate': 1.0,
                'total_interactions': 0,
                'db_query_time': 0.0
            }
        
        return metrics
    
    def evaluate_alerts(self, metrics: Optional[Dict[str, float]] = None) -> List[Dict]:
        """Evaluate all alerts against current metrics."""
        if metrics is None:
            metrics = self.check_performance_metrics()
        
        triggered_alerts = []
        
        for alert_name, alert in self.alerts.items():
            if not alert.enabled:
                continue
            
            if alert_name not in metrics:
                continue
            
            current_value = metrics[alert_name]
            threshold_exceeded = False
            
            # Check threshold based on operator
            if alert.operator == 'gt' and current_value > alert.threshold:
                threshold_exceeded = True
            elif alert.operator == 'lt' and current_value < alert.threshold:
                threshold_exceeded = True
            elif alert.operator == 'eq' and abs(current_value - alert.threshold) < 0.001:
                threshold_exceeded = True
            
            if threshold_exceeded:
                alert_info = {
                    'alert_name': alert_name,
                    'metric_value': current_value,
                    'threshold': alert.threshold,
                    'operator': alert.operator,
                    'timestamp': datetime.now().isoformat(),
                    'severity': self._get_alert_severity(alert_name, current_value, alert.threshold)
                }
                
                triggered_alerts.append(alert_info)
                
                # Update alert metadata
                alert.last_triggered = datetime.now()
                alert.trigger_count += 1
                
                # Trigger callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert_info)
                    except Exception as e:
                        logger.error(f"Alert callback failed: {e}")
        
        return triggered_alerts
    
    def _get_alert_severity(self, alert_name: str, current_value: float, threshold: float) -> str:
        """Determine alert severity based on how far value exceeds threshold."""
        if alert_name == 'avg_response_time':
            if current_value > threshold * 2:
                return 'critical'
            elif current_value > threshold * 1.5:
                return 'high'
            else:
                return 'medium'
        
        elif alert_name == 'success_rate':
            if current_value < threshold * 0.5:
                return 'critical'
            elif current_value < threshold * 0.7:
                return 'high'
            else:
                return 'medium'
        
        elif alert_name == 'error_rate':
            if current_value > threshold * 3:
                return 'critical'
            elif current_value > threshold * 2:
                return 'high'
            else:
                return 'medium'
        
        return 'medium'
    
    def get_performance_summary(self, hours_back: int = 24) -> Dict:
        """Get comprehensive performance summary."""
        try:
            cursor = self.connection.cursor()
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Current metrics
            current_metrics = self.check_performance_metrics(hours_back=1)
            
            # Historical comparison
            cursor.execute("""
                SELECT 
                    AVG(response_time) as avg_response,
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_queries,
                    MIN(response_time) as min_response,
                    MAX(response_time) as max_response
                FROM user_interactions 
                WHERE timestamp > ?
            """, (cutoff_time,))
            
            historical_data = cursor.fetchone()
            
            # Trend analysis (compare last hour vs previous hour)
            prev_hour_cutoff = datetime.now() - timedelta(hours=2)
            cursor.execute("""
                SELECT AVG(response_time), COUNT(*) 
                FROM user_interactions 
                WHERE timestamp BETWEEN ? AND ?
            """, (prev_hour_cutoff, datetime.now() - timedelta(hours=1)))
            
            prev_hour_data = cursor.fetchone()
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'period_hours': hours_back,
                'current_metrics': current_metrics,
                'historical_summary': {
                    'avg_response_time': historical_data[0] if historical_data[0] else 0.0,
                    'total_queries': historical_data[1],
                    'success_rate': (historical_data[2] / historical_data[1]) if historical_data[1] > 0 else 0.0,
                    'min_response_time': historical_data[3] if historical_data[3] else 0.0,
                    'max_response_time': historical_data[4] if historical_data[4] else 0.0
                },
                'trends': {
                    'response_time_trend': 'stable',
                    'volume_trend': 'stable'
                },
                'active_alerts': len([a for a in self.alerts.values() if a.enabled]),
                'recent_alerts': self.get_recent_alerts(hours_back=hours_back)
            }
            
            # Calculate trends
            if prev_hour_data[0] and current_metrics['avg_response_time']:
                if current_metrics['avg_response_time'] > prev_hour_data[0] * 1.2:
                    summary['trends']['response_time_trend'] = 'increasing'
                elif current_metrics['avg_response_time'] < prev_hour_data[0] * 0.8:
                    summary['trends']['response_time_trend'] = 'decreasing'
            
            if prev_hour_data[1] and current_metrics['query_volume']:
                if current_metrics['query_volume'] > prev_hour_data[1] * 1.2:
                    summary['trends']['volume_trend'] = 'increasing'
                elif current_metrics['query_volume'] < prev_hour_data[1] * 0.8:
                    summary['trends']['volume_trend'] = 'decreasing'
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {'error': str(e)}
    
    def get_recent_alerts(self, hours_back: int = 24) -> List[Dict]:
        """Get recent alert history."""
        recent_alerts = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for alert_name, alert in self.alerts.items():
            if alert.last_triggered and alert.last_triggered > cutoff_time:
                recent_alerts.append({
                    'alert_name': alert_name,
                    'last_triggered': alert.last_triggered.isoformat(),
                    'trigger_count': alert.trigger_count,
                    'threshold': alert.threshold,
                    'enabled': alert.enabled
                })
        
        # Sort by last triggered time
        recent_alerts.sort(key=lambda x: x['last_triggered'], reverse=True)
        return recent_alerts
    
    def configure_alert(self, alert_name: str, threshold: float, operator: str = 'gt', enabled: bool = True) -> bool:
        """Configure or update an alert."""
        try:
            if alert_name in self.alerts:
                self.alerts[alert_name].threshold = threshold
                self.alerts[alert_name].operator = operator
                self.alerts[alert_name].enabled = enabled
            else:
                self.alerts[alert_name] = PerformanceAlert(
                    metric_name=alert_name,
                    threshold=threshold,
                    operator=operator,
                    enabled=enabled
                )
            
            logger.info(f"Configured alert '{alert_name}': {operator} {threshold}, enabled={enabled}")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring alert: {e}")
            return False
    
    def get_alert_status(self) -> Dict:
        """Get status of all configured alerts."""
        return {
            alert_name: {
                'threshold': alert.threshold,
                'operator': alert.operator,
                'enabled': alert.enabled,
                'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None,
                'trigger_count': alert.trigger_count
            }
            for alert_name, alert in self.alerts.items()
        }

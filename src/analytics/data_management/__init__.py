"""Data management package for Noah's AI Assistant analytics.

This package provides comprehensive data management capabilities including
privacy controls, quality monitoring, backup management, and performance monitoring.
"""

from .core import AnalyticsDataManager
from .privacy import PrivacyManager
from .quality import DataQualityMonitor
from .backup import BackupManager
from .performance import PerformanceMonitor
from .models import SessionAnalytics, DataRetentionPolicy

__all__ = [
    'AnalyticsDataManager',
    'PrivacyManager', 
    'DataQualityMonitor',
    'BackupManager',
    'PerformanceMonitor',
    'SessionAnalytics',
    'DataRetentionPolicy'
]

__version__ = "1.0.0"

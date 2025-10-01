#!/usr/bin/env python3
"""Daily maintenance script for Noah's AI Assistant analytics.

This script runs daily maintenance tasks including:
- Data quality checks
- Performance monitoring
- Backup creation
- Data archival
- Cleanup operations

Run this script daily via cron job or task scheduler.
"""

import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics.data_management import AnalyticsDataManager


def setup_logging():
    """Setup logging for maintenance script."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'maintenance.log'),
            logging.StreamHandler()
        ]
    )


def run_daily_maintenance():
    """Run daily maintenance tasks."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("Starting daily analytics maintenance")
        logger.info("=" * 60)
        
        # Initialize data manager
        data_manager = AnalyticsDataManager()
        
        # Get initial status
        initial_status = data_manager.get_system_health()
        logger.info(f"Initial system health: {initial_status['database']['status']}")
        logger.info(f"Total interactions: {initial_status.get('database_stats', {}).get('total_interactions', 0)}")
        logger.info(f"Recent interactions (24h): {initial_status.get('database_stats', {}).get('recent_interactions_24h', 0)}")
        
        # Run maintenance tasks
        data_manager.run_daily_maintenance()
        
        # Get final status
        final_status = data_manager.get_system_health()
        
        # Generate maintenance report
        maintenance_report = {
            'timestamp': datetime.now().isoformat(),
            'initial_status': initial_status,
            'final_status': final_status,
            'maintenance_tasks': [
                'data_quality_check',
                'performance_monitoring',
                'backup_creation',
                'backup_cleanup',
                'data_archival'
            ],
            'success': True
        }
        
        # Save report
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"maintenance_report_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(maintenance_report, f, indent=2)
        
        logger.info(f"Maintenance report saved: {report_file}")
        logger.info("Daily maintenance completed successfully")
        
        # Close data manager
        data_manager.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Daily maintenance failed: {e}")
        logger.exception("Full error details:")
        return False


def generate_health_summary():
    """Generate a quick health summary."""
    try:
        data_manager = AnalyticsDataManager()
        status = data_manager.get_system_health()
        data_manager.close()
        
        print("\n📊 ANALYTICS SYSTEM HEALTH SUMMARY")
        print("=" * 50)
        print(f"🔍 System Health: {status.get('overall_health_score', 0):.2f}")
        print(f"📈 Data Quality Score: {status.get('data_quality', 0):.2%}")
        print(f"⚡ Performance Status: HEALTHY" if status.get('performance', {}).get('success_rate', 0) > 0.8 else "⚡ Performance Status: DEGRADED")
        print(f"📊 Database Size: {status.get('database', {}).get('size_mb', 0):.1f} MB")
        
        if status.get('alerts', []):
            print(f"⚠️  Active Alerts: {len(status.get('alerts', []))}")
        
        if status.get('overall_health_score', 0) > 0.8:
            print("✅ All systems operational")
        else:
            print("⚠️  System needs attention")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error generating health summary: {e}")


def main():
    """Main entry point."""
    setup_logging()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--health':
        generate_health_summary()
        return
    
    success = run_daily_maintenance()
    
    if success:
        print("✅ Daily maintenance completed successfully")
        generate_health_summary()
        sys.exit(0)
    else:
        print("❌ Daily maintenance failed - check logs for details")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Demo script for the enhanced data management system.

This script demonstrates the capabilities of the new data management system
including data ingestion, quality monitoring, performance tracking, and export.
"""

import sys
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics.data_management import AnalyticsDataManager
from analytics.data_management.models import SessionAnalytics
from analytics.data_export import AnalyticsDataExporter
from analytics.comprehensive_analytics import UserInteraction


def create_sample_data(data_manager: AnalyticsDataManager, num_interactions: int = 50):
    """Create sample analytics data for demonstration."""
    
    print(f"📊 Creating {num_interactions} sample interactions...")
    
    roles = [
        "Software Developer",
        "Hiring Manager (technical)", 
        "Hiring Manager (nontechnical)",
        "Just looking around"
    ]
    
    query_templates = {
        "Software Developer": [
            "How does the RAG engine work?",
            "Show me the code architecture",
            "What's the memory system implementation?",
            "How is the vector store structured?",
            "Explain the role router logic"
        ],
        "Hiring Manager (technical)": [
            "What's Noah's technical background?",
            "Show me Noah's code examples", 
            "How does he approach system design?",
            "What technologies does he use?",
            "Tell me about his development process"
        ],
        "Hiring Manager (nontechnical)": [
            "What's Noah's professional background?",
            "Tell me about his achievements",
            "How does he work with teams?",
            "What's his career progression?",
            "Why should we hire Noah?"
        ],
        "Just looking around": [
            "Tell me about Noah",
            "What's interesting about him?",
            "Noah MMA fight",
            "Fun facts about Noah",
            "What does Noah do for fun?"
        ]
    }
    
    query_types = {
        "Software Developer": "technical",
        "Hiring Manager (technical)": "technical", 
        "Hiring Manager (nontechnical)": "career",
        "Just looking around": "general"
    }
    
    import random
    
    for i in range(num_interactions):
        role = random.choice(roles)
        query = random.choice(query_templates[role])
        
        # Create realistic interaction
        interaction = UserInteraction(
            session_id=f"demo_session_{random.randint(1, 10)}",
            timestamp=datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            ),
            user_role=role,
            query=query,
            query_type=query_types[role],
            response_time=random.uniform(0.5, 8.0),
            response_length=random.randint(200, 2000),
            code_snippets_shown=random.randint(0, 5) if "technical" in role.lower() else 0,
            citations_provided=random.randint(1, 8),
            success=random.choice([True, True, True, False]),  # 75% success rate
            user_rating=random.choice([None, None, 3, 4, 5]),  # Some ratings
            follow_up_query=random.choice([True, False, False]),  # 33% follow-up
            conversation_turn=random.randint(1, 5)
        )
        
        # Ingest the interaction
        success = data_manager.record_interaction(interaction)
        if not success:
            print(f"⚠️  Failed to ingest interaction {i+1}")
    
    print(f"✅ Created {num_interactions} sample interactions")


def demonstrate_data_management():
    """Demonstrate the data management system capabilities."""
    
    print("🚀 Data Management System Demo")
    print("=" * 60)
    
    # Use temporary database for demo
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Initialize data manager
        print("📦 Initializing data management system...")
        data_manager = AnalyticsDataManager(db_path=db_path)
        
        # Show initial status
        initial_status = data_manager.get_system_health()
        print(f"📊 Initial system health: {initial_status.get('overall_health_score', 0):.2f}")
        
        # Create sample data
        create_sample_data(data_manager, 100)
        
        # Show updated status
        print("\n📈 SYSTEM STATUS AFTER DATA INGESTION")
        print("-" * 50)
        status = data_manager.get_system_health()
        
        print(f"🔍 System Health Score: {status.get('overall_health_score', 0):.2f}")
        print(f"📊 Database Size: {status.get('database', {}).get('size_mb', 0):.1f} MB")
        print(f"📈 Data Quality Score: {status.get('data_quality', 0):.2f}")
        print(f"⚡ Performance: HEALTHY" if status.get('performance', {}).get('success_rate', 0) > 0.8 else "⚡ Performance: DEGRADED")
        
        # Demonstrate data quality monitoring
        print("\n🔍 DATA QUALITY MONITORING")
        print("-" * 50)
        
        quality_report = data_manager.quality_monitor.get_quality_report()
        print(f"✅ Overall Quality Score: {quality_report.get('overall_score', 0):.2%}")
        
        # Show completeness details if available
        print(f"📋 Data quality monitoring active")
        
        # Demonstrate performance monitoring
        print("\n⚡ PERFORMANCE MONITORING")
        print("-" * 50)
        
        perf_report = data_manager.performance_monitor.check_performance_metrics()
        print(f"🎯 Performance monitoring active")
        print(f"📊 Metrics collected: {len(perf_report)} metrics")
        
        # Check for any alerts
        alerts = data_manager.performance_monitor.evaluate_alerts()
        print(f"🚨 Active Alerts: {len(alerts)}")
        
        if alerts:
            for alert in alerts:
                print(f"⚠️  {alert['alert_name']}: {alert['metric_value']:.2f} (threshold: {alert['threshold']})")
        
        # Demonstrate backup system
        print("\n💾 BACKUP DEMONSTRATION")
        print("-" * 50)
        
        backup_path = data_manager.backup_manager.create_backup()
        if backup_path:
            print(f"✅ Backup created successfully: {backup_path}")
        else:
            print("❌ Backup failed")
        
        # Demonstrate data export
        print("\n📤 DATA EXPORT DEMONSTRATION")
        print("-" * 50)
        
        exporter = AnalyticsDataExporter(db_path=db_path)
        
        # Export analytics summary
        export_path = exporter.export_analytics_summary(
            days=30,
            format='json',
            output_path='demo_exports/analytics_summary.json'
        )
        print(f"📊 Analytics summary exported: {export_path}")
        
        # Export user interactions
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        interactions_path = exporter.export_user_interactions(
            start_date=start_date,
            end_date=end_date,
            format='csv',
            output_path='demo_exports/user_interactions_7d.csv'
        )
        print(f"📋 User interactions exported: {interactions_path}")
        
        exporter.close()
        
        # Run maintenance tasks
        print("\n🔧 MAINTENANCE TASKS DEMONSTRATION")
        print("-" * 50)
        
        print("🔄 Running daily maintenance tasks...")
        data_manager.run_daily_maintenance()
        print("✅ Maintenance tasks completed")
        
        # Final status
        print("\n📊 FINAL SYSTEM STATUS")
        print("-" * 50)
        
        final_status = data_manager.get_system_health()
        print(f"🔍 System Health Score: {final_status.get('overall_health_score', 0):.2f}")
        print(f"📈 Data Quality: {final_status.get('data_quality', 0):.2f}")
        print(f"📊 Database Size: {final_status.get('database', {}).get('size_mb', 0):.1f} MB")
        
        # Close data manager
        data_manager.close()
        
        print("\n" + "=" * 60)
        print("✅ DATA MANAGEMENT SYSTEM DEMO COMPLETED")
        print("=" * 60)
        
        print("\n🎯 KEY FEATURES DEMONSTRATED:")
        print("• ✅ Data ingestion with privacy controls")
        print("• ✅ Real-time quality monitoring")
        print("• ✅ Performance tracking and alerting")
        print("• ✅ Automated backup creation")
        print("• ✅ Data export in multiple formats")
        print("• ✅ Daily maintenance automation")
        print("• ✅ Comprehensive health reporting")
        
        print("\n📂 Generated Files:")
        print("• demo_exports/analytics_summary.json")
        print("• demo_exports/user_interactions_7d.csv")
        print("• backups/ (compressed database backups)")
        
    finally:
        # Cleanup temporary database
        try:
            os.unlink(db_path)
        except:
            pass


if __name__ == "__main__":
    demonstrate_data_management()

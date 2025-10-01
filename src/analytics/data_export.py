"""Data export and import utilities for analytics data.

This module provides tools for exporting analytics data for analysis,
compliance, migration, or backup purposes.
"""

import json
import csv
import sqlite3
import gzip
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class AnalyticsDataExporter:
    """Export analytics data in various formats."""
    
    def __init__(self, db_path: str = "analytics/comprehensive_metrics.db"):
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(str(self.db_path))
    
    def export_user_interactions(self, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                format: str = 'json',
                                output_path: Optional[str] = None) -> str:
        """Export user interactions data."""
        
        # Build query with date filters
        query = "SELECT * FROM user_interactions"
        params = []
        
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date.isoformat())
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp"
        
        # Execute query
        df = pd.read_sql_query(query, self.connection, params=params)
        
        # Generate output filename if not provided
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            date_suffix = ""
            if start_date:
                date_suffix = f"_{start_date.strftime('%Y%m%d')}"
            if end_date:
                date_suffix += f"_to_{end_date.strftime('%Y%m%d')}"
            
            output_path = f"exports/user_interactions{date_suffix}_{timestamp}.{format}"
        
        # Create exports directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Export in specified format
        if format.lower() == 'json':
            self._export_json(df, output_path)
        elif format.lower() == 'csv':
            self._export_csv(df, output_path)
        elif format.lower() == 'excel':
            self._export_excel(df, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported {len(df)} user interactions to {output_path}")
        return output_path
    
    def export_analytics_summary(self, 
                                days: int = 30,
                                format: str = 'json',
                                output_path: Optional[str] = None) -> str:
        """Export comprehensive analytics summary."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Gather analytics data
        summary = {
            'export_info': {
                'generated_at': end_date.isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'period_days': days
            },
            'user_interactions': self._get_interactions_summary(start_date, end_date),
            'role_distribution': self._get_role_distribution(start_date, end_date),
            'query_patterns': self._get_query_patterns(start_date, end_date),
            'performance_metrics': self._get_performance_metrics(start_date, end_date),
            'content_effectiveness': self._get_content_effectiveness(),
            'top_questions': self._get_top_questions(start_date, end_date)
        }
        
        # Generate output filename if not provided
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"exports/analytics_summary_{days}d_{timestamp}.{format}"
        
        # Create exports directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Export summary
        if format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        elif format.lower() == 'csv':
            # For CSV, export each section as separate files
            base_path = Path(output_path).stem
            base_dir = Path(output_path).parent
            
            for section, data in summary.items():
                if isinstance(data, list):
                    section_path = base_dir / f"{base_path}_{section}.csv"
                    pd.DataFrame(data).to_csv(section_path, index=False)
                elif isinstance(data, dict) and section != 'export_info':
                    section_path = base_dir / f"{base_path}_{section}.csv"
                    pd.DataFrame([data]).to_csv(section_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported analytics summary to {output_path}")
        return output_path
    
    def export_for_compliance(self, 
                             start_date: datetime,
                             end_date: datetime,
                             include_pii: bool = False) -> str:
        """Export data for compliance/audit purposes."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_dir = Path(f"exports/compliance_{timestamp}")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Export user interactions
        interactions_path = self.export_user_interactions(
            start_date=start_date,
            end_date=end_date,
            format='csv',
            output_path=str(export_dir / 'user_interactions.csv')
        )
        
        # Export session analytics
        session_query = '''
            SELECT * FROM session_analytics 
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time
        '''
        session_df = pd.read_sql_query(
            session_query, 
            self.connection, 
            params=[start_date.isoformat(), end_date.isoformat()]
        )
        session_path = export_dir / 'session_analytics.csv'
        session_df.to_csv(session_path, index=False)
        
        # Export system performance
        perf_query = '''
            SELECT * FROM system_performance 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        '''
        perf_df = pd.read_sql_query(
            perf_query, 
            self.connection, 
            params=[start_date.isoformat(), end_date.isoformat()]
        )
        perf_path = export_dir / 'system_performance.csv'
        perf_df.to_csv(perf_path, index=False)
        
        # Create compliance report
        compliance_report = {
            'export_info': {
                'purpose': 'compliance_audit',
                'generated_at': datetime.now().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'includes_pii': include_pii,
                'data_anonymized': not include_pii
            },
            'files_included': [
                'user_interactions.csv',
                'session_analytics.csv', 
                'system_performance.csv'
            ],
            'record_counts': {
                'user_interactions': len(session_df),
                'session_analytics': len(session_df),
                'system_performance': len(perf_df)
            }
        }
        
        # Save compliance report
        report_path = export_dir / 'compliance_report.json'
        with open(report_path, 'w') as f:
            json.dump(compliance_report, f, indent=2)
        
        # Create compressed archive
        archive_path = f"exports/compliance_export_{timestamp}.tar.gz"
        import tarfile
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(export_dir, arcname=f"compliance_export_{timestamp}")
        
        # Cleanup temporary directory
        import shutil
        shutil.rmtree(export_dir)
        
        logger.info(f"Compliance export created: {archive_path}")
        return archive_path
    
    def _export_json(self, df: pd.DataFrame, output_path: str):
        """Export DataFrame to JSON."""
        df.to_json(output_path, orient='records', date_format='iso', indent=2)
    
    def _export_csv(self, df: pd.DataFrame, output_path: str):
        """Export DataFrame to CSV."""
        df.to_csv(output_path, index=False)
    
    def _export_excel(self, df: pd.DataFrame, output_path: str):
        """Export DataFrame to Excel."""
        df.to_excel(output_path, index=False)
    
    def _get_interactions_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get summary of user interactions."""
        query = '''
            SELECT 
                COUNT(*) as total_interactions,
                COUNT(DISTINCT session_id) as unique_sessions,
                AVG(response_time) as avg_response_time,
                AVG(CAST(success AS FLOAT)) as success_rate,
                SUM(code_snippets_shown) as total_code_snippets,
                SUM(citations_provided) as total_citations
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp <= ?
        '''
        
        cursor = self.connection.cursor()
        cursor.execute(query, [start_date.isoformat(), end_date.isoformat()])
        result = cursor.fetchone()
        
        if result:
            return {
                'total_interactions': result[0],
                'unique_sessions': result[1],
                'avg_response_time': result[2],
                'success_rate': result[3],
                'total_code_snippets': result[4],
                'total_citations': result[5]
            }
        return {}
    
    def _get_role_distribution(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get distribution of interactions by role."""
        query = '''
            SELECT 
                user_role,
                COUNT(*) as interaction_count,
                COUNT(DISTINCT session_id) as session_count,
                AVG(response_time) as avg_response_time,
                AVG(CAST(success AS FLOAT)) as success_rate
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY user_role
            ORDER BY interaction_count DESC
        '''
        
        cursor = self.connection.cursor()
        cursor.execute(query, [start_date.isoformat(), end_date.isoformat()])
        
        return [
            {
                'user_role': row[0],
                'interaction_count': row[1],
                'session_count': row[2],
                'avg_response_time': row[3],
                'success_rate': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def _get_query_patterns(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get query patterns by type."""
        query = '''
            SELECT 
                query_type,
                COUNT(*) as count,
                AVG(response_time) as avg_response_time,
                AVG(CAST(success AS FLOAT)) as success_rate
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY query_type
            ORDER BY count DESC
        '''
        
        cursor = self.connection.cursor()
        cursor.execute(query, [start_date.isoformat(), end_date.isoformat()])
        
        return [
            {
                'query_type': row[0],
                'count': row[1],
                'avg_response_time': row[2],
                'success_rate': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def _get_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get performance metrics summary."""
        query = '''
            SELECT 
                MIN(response_time) as min_response_time,
                MAX(response_time) as max_response_time,
                AVG(response_time) as avg_response_time,
                AVG(response_length) as avg_response_length
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp <= ?
        '''
        
        cursor = self.connection.cursor()
        cursor.execute(query, [start_date.isoformat(), end_date.isoformat()])
        result = cursor.fetchone()
        
        if result:
            return {
                'min_response_time': result[0],
                'max_response_time': result[1],
                'avg_response_time': result[2],
                'avg_response_length': result[3]
            }
        return {}
    
    def _get_content_effectiveness(self) -> List[Dict[str, Any]]:
        """Get content effectiveness metrics."""
        query = '''
            SELECT 
                content_type,
                content_id,
                access_count,
                avg_relevance_score
            FROM content_analytics 
            ORDER BY access_count DESC
            LIMIT 20
        '''
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        return [
            {
                'content_type': row[0],
                'content_id': row[1],
                'access_count': row[2],
                'avg_relevance_score': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def _get_top_questions(self, start_date: datetime, end_date: datetime, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most frequently asked questions."""
        query = '''
            SELECT 
                query,
                COUNT(*) as frequency,
                AVG(CAST(success AS FLOAT)) as success_rate,
                AVG(response_time) as avg_response_time
            FROM user_interactions 
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY LOWER(TRIM(query))
            ORDER BY frequency DESC
            LIMIT ?
        '''
        
        cursor = self.connection.cursor()
        cursor.execute(query, [start_date.isoformat(), end_date.isoformat(), limit])
        
        return [
            {
                'question': row[0],
                'frequency': row[1],
                'success_rate': row[2],
                'avg_response_time': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()


class AnalyticsDataImporter:
    """Import analytics data from external sources."""
    
    def __init__(self, db_path: str = "analytics/comprehensive_metrics.db"):
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(str(self.db_path))
    
    def import_from_json(self, json_file: str, table_name: str = 'user_interactions') -> bool:
        """Import data from JSON file."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Import to database
            df.to_sql(table_name, self.connection, if_exists='append', index=False)
            
            logger.info(f"Imported {len(df)} records from {json_file} to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import from {json_file}: {e}")
            return False
    
    def import_from_csv(self, csv_file: str, table_name: str = 'user_interactions') -> bool:
        """Import data from CSV file."""
        try:
            df = pd.read_csv(csv_file)
            
            # Import to database
            df.to_sql(table_name, self.connection, if_exists='append', index=False)
            
            logger.info(f"Imported {len(df)} records from {csv_file} to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import from {csv_file}: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()


# CLI interface for data export
def main():
    """Command line interface for data export."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export analytics data')
    parser.add_argument('--format', choices=['json', 'csv', 'excel'], default='json',
                       help='Export format')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days to export')
    parser.add_argument('--summary', action='store_true',
                       help='Export analytics summary instead of raw data')
    parser.add_argument('--compliance', action='store_true',
                       help='Export for compliance/audit purposes')
    parser.add_argument('--output', type=str,
                       help='Output file path')
    
    args = parser.parse_args()
    
    exporter = AnalyticsDataExporter()
    
    try:
        if args.compliance:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=args.days)
            output_path = exporter.export_for_compliance(start_date, end_date)
        elif args.summary:
            output_path = exporter.export_analytics_summary(
                days=args.days,
                format=args.format,
                output_path=args.output
            )
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=args.days)
            output_path = exporter.export_user_interactions(
                start_date=start_date,
                end_date=end_date,
                format=args.format,
                output_path=args.output
            )
        
        print(f"✅ Export completed: {output_path}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
    finally:
        exporter.close()


if __name__ == "__main__":
    main()

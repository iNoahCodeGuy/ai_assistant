# 📊 Data Management Plan - Noah's AI Assistant Analytics

## Overview
This document outlines the comprehensive data management strategy for storing, processing, and maintaining analytics data collected by Noah's AI Assistant.

## 🎯 Data Management Objectives

1. **Data Integrity** - Ensure data accuracy and consistency
2. **Performance** - Optimize for fast reads and writes
3. **Scalability** - Handle growing data volumes
4. **Privacy** - Protect user information and comply with regulations
5. **Reliability** - Ensure data availability and backup/recovery
6. **Analytics** - Enable efficient querying and reporting

## 📂 Data Storage Architecture

### Current System
```
SQLite Database (analytics/comprehensive_metrics.db)
├── user_interactions (Primary analytics table)
├── content_analytics (Content effectiveness)
└── business_metrics (Daily aggregated metrics)
```

### Proposed Tiered Storage Strategy

#### Tier 1: Hot Data (Active Analytics)
**Technology**: SQLite with WAL mode
**Retention**: Last 90 days of detailed data
**Purpose**: Real-time analytics, dashboard queries, recent insights

```
Primary Database (analytics/comprehensive_metrics.db)
├── user_interactions_hot (90 days)
├── content_analytics_hot (90 days)
├── business_metrics_hot (90 days)
├── session_analytics (active sessions)
└── real_time_metrics (current day)
```

#### Tier 2: Warm Data (Historical Analytics)
**Technology**: SQLite + Compressed archives
**Retention**: 1-2 years of aggregated data
**Purpose**: Trend analysis, long-term insights

```
Historical Database (analytics/historical_metrics.db)
├── user_interactions_monthly (aggregated by month)
├── content_analytics_monthly (monthly summaries)
├── business_metrics_monthly (monthly trends)
└── performance_baselines (historical benchmarks)
```

#### Tier 3: Cold Data (Long-term Archive)
**Technology**: Compressed JSON files + Backup systems
**Retention**: 3+ years for compliance
**Purpose**: Audit trails, compliance, research

```
Archive Storage (analytics/archive/)
├── yearly_summaries/
├── compliance_exports/
├── data_dumps/
└── backup_snapshots/
```

## 🗄️ Database Schema Design

### Enhanced Schema Structure

#### 1. User Interactions Table (Enhanced)
```sql
CREATE TABLE user_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    user_role TEXT NOT NULL,
    query TEXT NOT NULL,
    query_hash TEXT,  -- For deduplication
    query_type TEXT NOT NULL,
    response_time REAL NOT NULL,
    response_length INTEGER,
    code_snippets_shown INTEGER DEFAULT 0,
    citations_provided INTEGER DEFAULT 0,
    success BOOLEAN NOT NULL,
    user_rating INTEGER CHECK(user_rating BETWEEN 1 AND 5),
    follow_up_query BOOLEAN DEFAULT FALSE,
    conversation_turn INTEGER DEFAULT 1,
    ip_hash TEXT,  -- Anonymized IP for abuse detection
    user_agent_hash TEXT,  -- Anonymized user agent
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_timestamp (timestamp),
    INDEX idx_session_id (session_id),
    INDEX idx_user_role (user_role),
    INDEX idx_query_type (query_type),
    INDEX idx_success (success),
    INDEX idx_query_hash (query_hash)
);
```

#### 2. Session Analytics Table (New)
```sql
CREATE TABLE session_analytics (
    session_id TEXT PRIMARY KEY,
    user_role TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    last_activity DATETIME NOT NULL,
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    avg_response_time REAL,
    total_code_snippets INTEGER DEFAULT 0,
    total_citations INTEGER DEFAULT 0,
    session_rating REAL,  -- Average of all ratings in session
    conversion_achieved BOOLEAN DEFAULT FALSE,  -- Did user engage deeply?
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_role (user_role),
    INDEX idx_start_time (start_time),
    INDEX idx_conversion (conversion_achieved)
);
```

#### 3. Content Performance Table (Enhanced)
```sql
CREATE TABLE content_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,  -- career_kb, code_snippet, mma_link
    content_id TEXT NOT NULL,
    content_hash TEXT,  -- For content versioning
    access_count INTEGER DEFAULT 1,
    avg_relevance_score REAL,
    success_rate REAL,  -- How often this content leads to successful responses
    user_roles_accessing TEXT,  -- JSON array
    first_accessed DATETIME,
    last_accessed DATETIME NOT NULL,
    performance_score REAL,  -- Calculated effectiveness metric
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(content_type, content_id),
    INDEX idx_content_type (content_type),
    INDEX idx_performance_score (performance_score),
    INDEX idx_last_accessed (last_accessed)
);
```

#### 4. Query Performance Table (New)
```sql
CREATE TABLE query_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_normalized TEXT NOT NULL,  -- Cleaned/normalized query
    query_category TEXT,  -- technical, career, mma, fun, general
    total_asks INTEGER DEFAULT 1,
    success_rate REAL,
    avg_response_time REAL,
    avg_user_rating REAL,
    popular_roles TEXT,  -- JSON array of roles that ask this
    trending_score REAL,  -- Recent popularity vs historical
    last_asked DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(query_normalized),
    INDEX idx_query_category (query_category),
    INDEX idx_success_rate (success_rate),
    INDEX idx_trending_score (trending_score),
    INDEX idx_last_asked (last_asked)
);
```

#### 5. System Performance Table (New)
```sql
CREATE TABLE system_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    metric_name TEXT NOT NULL,  -- response_time, memory_usage, concurrent_users, etc.
    metric_value REAL NOT NULL,
    metric_unit TEXT,  -- seconds, MB, count, etc.
    component TEXT,  -- rag_engine, code_index, database, etc.
    alert_threshold REAL,
    is_alert BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_metric_name (metric_name),
    INDEX idx_component (component),
    INDEX idx_is_alert (is_alert)
);
```

#### 6. Data Retention Policy Table (New)
```sql
CREATE TABLE data_retention_policy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    retention_days INTEGER NOT NULL,
    archive_after_days INTEGER,
    last_cleanup DATETIME,
    cleanup_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(table_name)
);
```

## 📈 Data Lifecycle Management

### 1. Data Ingestion Pipeline
```
User Interaction → Validation → Enrichment → Storage → Indexing
                     ↓              ↓           ↓          ↓
                 Schema Check → Add Metadata → Hot DB → Update Indexes
```

### 2. Data Processing Stages

#### Real-time Processing (< 1 second)
- Store raw interaction data
- Update session metrics
- Calculate immediate performance metrics
- Trigger alerts if thresholds exceeded

#### Near Real-time Processing (1-5 minutes)
- Aggregate session data
- Update content performance scores
- Calculate trending metrics
- Update query popularity rankings

#### Batch Processing (Hourly/Daily)
- Calculate business metrics
- Generate performance reports
- Archive old data
- Run data quality checks
- Generate insights and recommendations

### 3. Data Archival Strategy

#### Daily Archival Process
```python
def daily_archival_process():
    """Run daily data archival and cleanup."""
    
    # 1. Archive data older than 90 days to historical DB
    archive_old_interactions()
    
    # 2. Compress and backup data older than 1 year
    compress_historical_data()
    
    # 3. Clean up temporary data and logs
    cleanup_temporary_data()
    
    # 4. Update aggregated metrics
    update_monthly_summaries()
    
    # 5. Validate data integrity
    run_data_quality_checks()
    
    # 6. Generate archival report
    generate_archival_report()
```

## 🔒 Data Privacy & Security

### Privacy Protection Measures

#### 1. Data Anonymization
```python
def anonymize_user_data(interaction):
    """Anonymize sensitive user data."""
    return {
        'session_id': hash_session_id(interaction.session_id),
        'query': anonymize_query(interaction.query),  # Remove PII
        'ip_hash': hash_ip(interaction.ip_address),
        'user_agent_hash': hash_user_agent(interaction.user_agent),
        # ... other fields remain as-is
    }
```

#### 2. Data Retention Policies
- **User Interactions**: 90 days hot, 2 years warm, 3 years cold
- **Session Data**: 30 days detailed, 1 year aggregated
- **Performance Metrics**: 1 year detailed, 3 years summarized
- **Business Metrics**: Permanent (aggregated only)

#### 3. Access Controls
```python
class DataAccessControl:
    """Control access to analytics data based on user roles."""
    
    ROLE_PERMISSIONS = {
        'admin': ['read', 'write', 'delete', 'export'],
        'analyst': ['read', 'export'],
        'developer': ['read'],
        'viewer': ['read_summary']
    }
```

## 🔧 Data Management Tools

### 1. Data Manager Class
```python
class AnalyticsDataManager:
    """Comprehensive data management for analytics system."""
    
    def __init__(self):
        self.hot_db = sqlite3.connect('analytics/comprehensive_metrics.db')
        self.historical_db = sqlite3.connect('analytics/historical_metrics.db')
        self.retention_policy = DataRetentionPolicy()
        self.privacy_manager = PrivacyManager()
    
    def ingest_interaction(self, interaction: UserInteraction):
        """Ingest new user interaction with full pipeline."""
        # Validate data
        validated_data = self.validate_interaction(interaction)
        
        # Apply privacy controls
        anonymized_data = self.privacy_manager.anonymize(validated_data)
        
        # Store in hot database
        self.store_hot_data(anonymized_data)
        
        # Update real-time metrics
        self.update_realtime_metrics(anonymized_data)
        
        # Trigger alerts if needed
        self.check_alert_thresholds(anonymized_data)
    
    def archive_old_data(self, cutoff_date: datetime):
        """Archive data older than cutoff date."""
        # Move to historical database
        # Compress old files
        # Update retention tracking
    
    def generate_insights(self, timeframe: str = '30d'):
        """Generate actionable insights from data."""
        # Query patterns analysis
        # Performance trend analysis
        # User behavior insights
        # Content effectiveness report
```

### 2. Data Quality Monitor
```python
class DataQualityMonitor:
    """Monitor and ensure data quality."""
    
    def run_daily_checks(self):
        """Run comprehensive data quality checks."""
        checks = [
            self.check_data_completeness(),
            self.check_data_consistency(),
            self.check_performance_degradation(),
            self.check_anomaly_detection(),
            self.validate_business_rules()
        ]
        
        return self.generate_quality_report(checks)
```

### 3. Backup & Recovery System
```python
class BackupManager:
    """Handle backup and recovery operations."""
    
    def create_daily_backup(self):
        """Create incremental daily backup."""
        backup_path = f"backups/{datetime.now().strftime('%Y-%m-%d')}"
        
        # Backup databases
        self.backup_database('hot', backup_path)
        self.backup_database('historical', backup_path)
        
        # Backup configuration
        self.backup_configuration(backup_path)
        
        # Verify backup integrity
        self.verify_backup_integrity(backup_path)
```

## 📊 Performance Optimization

### 1. Database Optimization
- **Indexing Strategy**: Strategic indexes on frequently queried columns
- **Query Optimization**: Optimized queries for common analytics operations
- **Connection Pooling**: Efficient database connection management
- **WAL Mode**: Write-Ahead Logging for better concurrent access

### 2. Caching Strategy
```python
class AnalyticsCache:
    """Cache frequently accessed analytics data."""
    
    def __init__(self):
        self.redis_client = redis.Redis()  # Optional Redis for distributed caching
        self.memory_cache = {}
        self.cache_ttl = {
            'common_questions': 300,  # 5 minutes
            'user_behavior': 600,     # 10 minutes
            'content_performance': 900,  # 15 minutes
            'business_metrics': 3600     # 1 hour
        }
```

### 3. Query Performance
- **Prepared Statements**: Pre-compiled queries for better performance
- **Batch Operations**: Bulk inserts and updates
- **Async Processing**: Non-blocking data processing
- **Query Result Pagination**: Handle large result sets efficiently

## 🚨 Monitoring & Alerting

### 1. Performance Monitoring
```python
class PerformanceMonitor:
    """Monitor system performance and trigger alerts."""
    
    ALERT_THRESHOLDS = {
        'avg_response_time': 5.0,      # seconds
        'success_rate': 0.95,          # 95%
        'database_size': 1000,         # MB
        'concurrent_users': 100,       # simultaneous users
        'error_rate': 0.05             # 5%
    }
    
    def check_performance_metrics(self):
        """Check current performance against thresholds."""
        for metric, threshold in self.ALERT_THRESHOLDS.items():
            current_value = self.get_current_metric(metric)
            if self.exceeds_threshold(current_value, threshold, metric):
                self.trigger_alert(metric, current_value, threshold)
```

### 2. Data Health Monitoring
- **Data Freshness**: Ensure data is being updated regularly
- **Data Volume**: Monitor unexpected spikes or drops in data volume
- **Data Quality**: Track data completeness and consistency
- **System Resource**: Monitor database size, memory usage, CPU utilization

## 🔄 Data Migration & Versioning

### 1. Schema Migration
```python
class SchemaMigrator:
    """Handle database schema migrations."""
    
    def migrate_to_version(self, target_version: str):
        """Migrate database schema to target version."""
        current_version = self.get_current_schema_version()
        migration_path = self.get_migration_path(current_version, target_version)
        
        for migration in migration_path:
            self.apply_migration(migration)
            self.update_schema_version(migration.version)
```

### 2. Data Export/Import
```python
class DataPortability:
    """Handle data export and import operations."""
    
    def export_analytics_data(self, format: str = 'json', 
                             timeframe: str = 'all'):
        """Export analytics data for analysis or migration."""
        # Export to JSON, CSV, or other formats
        # Support filtering by timeframe, role, etc.
    
    def import_analytics_data(self, source_file: str, 
                             format: str = 'json'):
        """Import analytics data from external source."""
        # Validate format and schema
        # Import with data validation
        # Handle conflicts and duplicates
```

## 📋 Implementation Roadmap

### Phase 1: Enhanced Current System (Week 1-2)
- [ ] Implement enhanced database schema
- [ ] Add data retention policies
- [ ] Implement basic data quality checks
- [ ] Add performance monitoring

### Phase 2: Tiered Storage (Week 3-4)
- [ ] Implement historical database
- [ ] Create data archival process
- [ ] Add backup and recovery system
- [ ] Implement data migration tools

### Phase 3: Advanced Analytics (Week 5-6)
- [ ] Add caching layer
- [ ] Implement advanced data processing
- [ ] Create comprehensive monitoring
- [ ] Add alerting system

### Phase 4: Production Optimization (Week 7-8)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Compliance features
- [ ] Documentation and training

## 🎯 Success Metrics

### Data Management KPIs
- **Data Availability**: 99.9% uptime
- **Query Performance**: < 1 second for dashboard queries
- **Data Freshness**: < 5 minutes for real-time metrics
- **Storage Efficiency**: < 50% growth rate monthly
- **Backup Success**: 100% successful daily backups
- **Data Quality**: < 0.1% error rate in analytics data

### Business Impact Metrics
- **Insights Generation**: Daily automated insights
- **Decision Support**: Analytics-driven feature improvements
- **User Experience**: Data-driven UX optimizations
- **Performance Optimization**: 20% improvement in response times

---

This data management plan provides a comprehensive framework for storing, processing, and managing analytics data while ensuring privacy, performance, and scalability as the system grows.

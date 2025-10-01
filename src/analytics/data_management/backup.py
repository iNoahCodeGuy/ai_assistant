"""Backup and recovery management."""

import sqlite3
import gzip
import shutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """Handle database backup and recovery operations."""
    
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.max_backup_age_days = 30
        self.compression_enabled = True
        self.backup_retention_count = 10  # Keep last 10 backups
    
    def create_backup(self, backup_name: Optional[str] = None) -> Optional[str]:
        """Create a compressed backup of the database."""
        try:
            if not self.db_path.exists():
                logger.error(f"Database file not found: {self.db_path}")
                return None
            
            # Generate backup filename
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_name = f"analytics_backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.db"
            
            # Create backup using SQLite backup API
            source_conn = sqlite3.connect(str(self.db_path))
            backup_conn = sqlite3.connect(str(backup_path))
            
            source_conn.backup(backup_conn)
            source_conn.close()
            backup_conn.close()
            
            # Compress if enabled
            if self.compression_enabled:
                compressed_path = self.backup_dir / f"{backup_name}.db.gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed backup
                backup_path.unlink()
                backup_path = compressed_path
            
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_backup(self, backup_path: str, target_path: Optional[str] = None) -> bool:
        """Restore database from backup."""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            if target_path is None:
                target_path = self.db_path
            else:
                target_path = Path(target_path)
            
            # Handle compressed backups
            if backup_path.suffix == '.gz':
                # Decompress first
                temp_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path
            
            # Verify backup integrity
            if not self._verify_backup_integrity(str(backup_path)):
                logger.error("Backup integrity check failed")
                return False
            
            # Create backup of current database before restore
            if target_path.exists():
                current_backup = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                logger.info(f"Created backup of current database: {current_backup}")
            
            # Restore
            shutil.copy2(backup_path, target_path)
            
            # Clean up temporary decompressed file
            if backup_path.suffix != '.gz' and str(backup_path) != str(Path(backup_path).with_suffix('.gz')):
                backup_path.unlink()
            
            logger.info(f"Database restored from backup: {backup_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def _verify_backup_integrity(self, backup_path: str) -> bool:
        """Verify backup file integrity."""
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result and result[0] == "ok"
            
        except Exception as e:
            logger.error(f"Backup integrity check failed: {e}")
            return False
    
    def list_backups(self) -> List[dict]:
        """List available backups with metadata."""
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("*.db*"):
                stat = backup_file.stat()
                
                backup_info = {
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'compressed': backup_file.suffix == '.gz'
                }
                backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
        
        return backups
    
    def cleanup_old_backups(self) -> int:
        """Remove old backups based on retention policy."""
        removed_count = 0
        
        try:
            backups = self.list_backups()
            
            # Remove backups older than max_backup_age_days
            cutoff_date = datetime.now() - timedelta(days=self.max_backup_age_days)
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup['created'])
                if backup_date < cutoff_date:
                    Path(backup['path']).unlink()
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup['filename']}")
            
            # Keep only the most recent backups if we exceed retention count
            if len(backups) > self.backup_retention_count:
                excess_backups = backups[self.backup_retention_count:]
                for backup in excess_backups:
                    backup_path = Path(backup['path'])
                    if backup_path.exists():
                        backup_path.unlink()
                        removed_count += 1
                        logger.info(f"Removed excess backup: {backup['filename']}")
            
        except Exception as e:
            logger.error(f"Error during backup cleanup: {e}")
        
        return removed_count
    
    def get_backup_status(self) -> dict:
        """Get backup system status and statistics."""
        try:
            backups = self.list_backups()
            total_size = sum(backup['size_bytes'] for backup in backups)
            
            status = {
                'backup_count': len(backups),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'latest_backup': backups[0] if backups else None,
                'oldest_backup': backups[-1] if backups else None,
                'backup_directory': str(self.backup_dir),
                'compression_enabled': self.compression_enabled,
                'retention_days': self.max_backup_age_days,
                'retention_count': self.backup_retention_count
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting backup status: {e}")
            return {'error': str(e)}
    
    def configure_retention(self, max_age_days: int, max_count: int) -> bool:
        """Configure backup retention policy."""
        try:
            self.max_backup_age_days = max_age_days
            self.backup_retention_count = max_count
            logger.info(f"Updated backup retention: {max_age_days} days, {max_count} backups")
            return True
        except Exception as e:
            logger.error(f"Error configuring retention: {e}")
            return False

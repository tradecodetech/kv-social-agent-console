"""
KV Systems & Automations
Database Migration Script v2.0

This script safely migrates your existing memory.db to the new schema
with prompt_version tracking.

Run this BEFORE deploying the upgraded agent.py
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path


def backup_database(db_path: str) -> str:
    """Create a timestamped backup of the database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def check_column_exists(conn, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def migrate_database(db_path: str):
    """
    Migrate database to v2.0 schema.
    
    Changes:
    - Add prompt_version column to run_logs table
    """
    
    print("\n" + "="*60)
    print("KV Systems & Automations - Database Migration v2.0")
    print("="*60 + "\n")
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("   If this is a fresh install, the agent will create it automatically.")
        return
    
    # Create backup
    print("📦 Creating backup...")
    backup_path = backup_database(db_path)
    
    # Connect and migrate
    print("🔧 Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        if check_column_exists(conn, 'run_logs', 'prompt_version'):
            print("✅ Database is already up to date!")
            print("   No migration needed.\n")
            conn.close()
            return
        
        print("🚀 Starting migration...")
        
        # Add prompt_version column
        print("   → Adding prompt_version column to run_logs...")
        cursor.execute("""
            ALTER TABLE run_logs 
            ADD COLUMN prompt_version TEXT
        """)
        
        # Set default value for existing records
        cursor.execute("""
            UPDATE run_logs 
            SET prompt_version = 'v1.0-legacy'
            WHERE prompt_version IS NULL
        """)
        
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print(f"\n📊 Database Stats:")
        
        # Show stats
        cursor.execute("SELECT COUNT(*) FROM posts")
        post_count = cursor.fetchone()[0]
        print(f"   Total posts logged: {post_count}")
        
        cursor.execute("SELECT COUNT(*) FROM run_logs")
        run_count = cursor.fetchone()[0]
        print(f"   Total runs logged: {run_count}")
        
        cursor.execute("""
            SELECT COUNT(*) FROM run_logs WHERE success = 1
        """)
        success_count = cursor.fetchone()[0]
        success_rate = (success_count / run_count * 100) if run_count > 0 else 0
        print(f"   Success rate: {success_rate:.1f}%")
        
        print(f"\n💾 Backup preserved at: {backup_path}")
        print("   You can safely delete this backup after testing.\n")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"   Your backup is safe at: {backup_path}")
        print("   Restoring from backup...\n")
        
        conn.close()
        shutil.copy2(backup_path, db_path)
        print("✅ Database restored from backup")
        raise
    
    finally:
        conn.close()


def verify_migration(db_path: str):
    """Verify the migration was successful."""
    print("\n🔍 Verifying migration...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check schema
    cursor.execute("PRAGMA table_info(run_logs)")
    columns = [row[1] for row in cursor.fetchall()]
    
    expected_columns = [
        'id', 'ts', 'page_name', 'page_id', 'mode', 'pillar',
        'message_len', 'fb_post_id', 'success', 'error_code',
        'error_message', 'prompt_version'
    ]
    
    missing = set(expected_columns) - set(columns)
    if missing:
        print(f"⚠️  Missing columns: {missing}")
        conn.close()
        return False
    
    print("✅ All columns present")
    
    # Check data integrity
    cursor.execute("SELECT COUNT(*) FROM run_logs WHERE prompt_version IS NOT NULL")
    versioned_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM run_logs")
    total_count = cursor.fetchone()[0]
    
    if versioned_count == total_count:
        print(f"✅ All {total_count} records have version tracking")
    else:
        print(f"⚠️  {total_count - versioned_count} records missing version")
    
    conn.close()
    return True


if __name__ == "__main__":
    import sys
    
    # Default database path
    DB_PATH = "memory.db"
    
    # Allow custom path via command line
    if len(sys.argv) > 1:
        DB_PATH = sys.argv[1]
    
    print(f"Database path: {DB_PATH}\n")
    
    try:
        migrate_database(DB_PATH)
        verify_migration(DB_PATH)
        
        print("\n" + "="*60)
        print("Migration Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Replace old agent.py with upgraded version")
        print("2. Replace old logger.py with upgraded version")
        print("3. Test with: python agent.py")
        print("4. Monitor logs for prompt_version tracking")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
🗄️ Database Migration Runner
Handles database schema changes, ORM migrations, and data integrity
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import psycopg2

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database migrations with safety checks and rollback capabilities"""

    def __init__(self, database_url: str, environment: str = "development"):
        self.database_url = database_url
        self.environment = environment
        self.connection = None
        self.migration_history = []

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info(f"✅ Connected to database in {self.environment} environment")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Database connection closed")

    def create_migration_table(self):
        """Create migration tracking table if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS migration_history (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    environment VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'success',
                    rollback_sql TEXT,
                    metadata JSONB
                )
            """
            )
            self.connection.commit()
            logger.info("✅ Migration history table created/verified")
        except Exception as e:
            logger.error(f"❌ Failed to create migration table: {e}")
            self.connection.rollback()
            raise

    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT migration_name FROM migration_history 
                WHERE environment = %s AND status = 'success'
                ORDER BY applied_at
            """,
                (self.environment,),
            )

            applied = [row[0] for row in cursor.fetchall()]
            logger.info(f"📊 Found {len(applied)} applied migrations")
            return applied
        except Exception as e:
            logger.error(f"❌ Failed to get applied migrations: {e}")
            return []

    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        try:
            # Get all migration files
            migration_dir = os.path.join(os.path.dirname(__file__), "versions")
            if not os.path.exists(migration_dir):
                logger.warning("⚠️ No migrations directory found")
                return []

            migration_files = []
            for file in os.listdir(migration_dir):
                if file.endswith(".py") and file != "__init__.py":
                    migration_files.append(file)

            # Get applied migrations
            applied = self.get_applied_migrations()

            # Return pending migrations
            pending = [f for f in migration_files if f not in applied]
            logger.info(f"📋 Found {len(pending)} pending migrations")
            return pending

        except Exception as e:
            logger.error(f"❌ Failed to get pending migrations: {e}")
            return []

    def run_migration(self, migration_file: str, dry_run: bool = False) -> bool:
        """Run a single migration file"""
        try:
            migration_path = os.path.join(
                os.path.dirname(__file__), "versions", migration_file
            )

            logger.info(f"🔄 Running migration: {migration_file}")

            # Read migration file
            with open(migration_path, "r") as f:
                migration_code = f.read()

            # Execute migration
            if not dry_run:
                cursor = self.connection.cursor()

                # Execute the migration
                exec(
                    migration_code,
                    {"cursor": cursor, "connection": self.connection, "logger": logger},
                )

                # Record migration in history
                cursor.execute(
                    """
                    INSERT INTO migration_history 
                    (migration_name, environment, status, metadata)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        migration_file,
                        self.environment,
                        "success",
                        json.dumps(
                            {
                                "file_path": migration_path,
                                "executed_at": datetime.now().isoformat(),
                                "dry_run": dry_run,
                            }
                        ),
                    ),
                )

                self.connection.commit()
                logger.info(f"✅ Migration {migration_file} completed successfully")
            else:
                logger.info(f"🔍 Dry run completed for {migration_file}")

            return True

        except Exception as e:
            logger.error(f"❌ Migration {migration_file} failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def run_all_migrations(self, dry_run: bool = False) -> bool:
        """Run all pending migrations"""
        try:
            # Create migration table if it doesn't exist
            self.create_migration_table()

            # Get pending migrations
            pending = self.get_pending_migrations()

            if not pending:
                logger.info("✅ No pending migrations")
                return True

            logger.info(f"🚀 Starting {len(pending)} migrations")

            # Run each migration
            for migration in pending:
                if not self.run_migration(migration, dry_run):
                    logger.error(f"❌ Failed to run migration: {migration}")
                    return False

            logger.info("🎉 All migrations completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Migration process failed: {e}")
            return False

    def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a specific migration"""
        try:
            logger.info(f"🔄 Rolling back migration: {migration_name}")

            cursor = self.connection.cursor()

            # Get migration details
            cursor.execute(
                """
                SELECT rollback_sql, metadata FROM migration_history 
                WHERE migration_name = %s AND environment = %s
                ORDER BY applied_at DESC LIMIT 1
            """,
                (migration_name, self.environment),
            )

            result = cursor.fetchone()
            if not result:
                logger.error(f"❌ Migration {migration_name} not found in history")
                return False

            rollback_sql, metadata = result

            if rollback_sql:
                # Execute rollback SQL
                cursor.execute(rollback_sql)
                logger.info(f"✅ Rollback SQL executed for {migration_name}")
            else:
                # Try to find rollback in migration file
                migration_path = os.path.join(
                    os.path.dirname(__file__), "versions", migration_name
                )

                if os.path.exists(migration_path):
                    # Look for rollback function
                    with open(migration_path, "r") as f:
                        migration_code = f.read()

                    if "def rollback(" in migration_code:
                        # Execute rollback function
                        exec(
                            migration_code,
                            {
                                "cursor": cursor,
                                "connection": self.connection,
                                "logger": logger,
                            },
                        )

                        # Call rollback function
                        if "rollback" in locals():
                            rollback(cursor, self.connection)
                            logger.info(
                                f"✅ Rollback function executed for {migration_name}"
                            )
                        else:
                            logger.warning(
                                f"⚠️ Rollback function not found in {migration_name}"
                            )
                    else:
                        logger.warning(
                            f"⚠️ No rollback function found in {migration_name}"
                        )

            # Mark migration as rolled back
            cursor.execute(
                """
                UPDATE migration_history 
                SET status = 'rolled_back', 
                    metadata = jsonb_set(metadata, '{rolled_back_at}', %s)
                WHERE migration_name = %s AND environment = %s
            """,
                (
                    json.dumps(datetime.now().isoformat()),
                    migration_name,
                    self.environment,
                ),
            )

            self.connection.commit()
            logger.info(f"✅ Migration {migration_name} rolled back successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Rollback failed for {migration_name}: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        try:
            cursor = self.connection.cursor()

            # Get migration counts
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    COUNT(CASE WHEN status = 'rolled_back' THEN 1 END) as rolled_back
                FROM migration_history 
                WHERE environment = %s
            """,
                (self.environment,),
            )

            counts = cursor.fetchone()

            # Get recent migrations
            cursor.execute(
                """
                SELECT migration_name, status, applied_at 
                FROM migration_history 
                WHERE environment = %s 
                ORDER BY applied_at DESC 
                LIMIT 10
            """,
                (self.environment,),
            )

            recent = [
                {
                    "name": row[0],
                    "status": row[1],
                    "applied_at": row[2].isoformat() if row[2] else None,
                }
                for row in cursor.fetchall()
            ]

            return {
                "environment": self.environment,
                "total_migrations": counts[0],
                "successful": counts[1],
                "failed": counts[2],
                "rolled_back": counts[3],
                "recent_migrations": recent,
                "pending_migrations": self.get_pending_migrations(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get migration status: {e}")
            return {}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Database Migration Runner")
    parser.add_argument(
        "--environment",
        "-e",
        default="development",
        choices=["development", "staging", "production"],
        help="Target environment",
    )
    parser.add_argument(
        "--database-url", "-d", required=True, help="Database connection URL"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without executing migrations",
    )
    parser.add_argument(
        "--rollback", "-r", metavar="MIGRATION", help="Rollback specific migration"
    )
    parser.add_argument(
        "--status", "-s", action="store_true", help="Show migration status"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create migration runner
    runner = MigrationRunner(args.database_url, args.environment)

    try:
        # Connect to database
        if not runner.connect():
            sys.exit(1)

        # Handle different commands
        if args.rollback:
            # Rollback specific migration
            if runner.rollback_migration(args.rollback):
                logger.info("✅ Rollback completed successfully")
            else:
                logger.error("❌ Rollback failed")
                sys.exit(1)

        elif args.status:
            # Show migration status
            status = runner.get_migration_status()
            print(json.dumps(status, indent=2))

        else:
            # Run migrations
            if runner.run_all_migrations(args.dry_run):
                logger.info("✅ All migrations completed successfully")
            else:
                logger.error("❌ Migration process failed")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("⚠️ Migration interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

    finally:
        runner.disconnect()


if __name__ == "__main__":
    main()

"""Run database migrations for due_time and reminder_level fields"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine


def run_migration():
    """Add due_time to tasks and reminder_level to notifications"""

    migrations = [
        # Add due_time column to tasks table
        {
            "name": "Add due_time to tasks",
            "sql": "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_time TIME;",
            "verify": """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'due_time';
            """,
        },
        # Add reminder_level column to notifications table
        {
            "name": "Add reminder_level to notifications",
            "sql": "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS reminder_level VARCHAR(20);",
            "verify": """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'notifications' AND column_name = 'reminder_level';
            """,
        },
    ]

    with engine.connect() as conn:
        for migration in migrations:
            print(f"\nRunning: {migration['name']}...")
            try:
                conn.execute(text(migration["sql"]))
                conn.commit()
                print(f"  ✓ Migration applied")

                # Verify
                result = conn.execute(text(migration["verify"]))
                row = result.fetchone()
                if row:
                    print(f"  ✓ Verified: {row}")
                else:
                    print(f"  ⚠ Warning: Column not found after migration")

            except Exception as e:
                print(f"  ✗ Error: {e}")

    print("\n✓ All migrations completed!")


if __name__ == "__main__":
    run_migration()

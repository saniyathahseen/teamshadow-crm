#!/usr/bin/env python3
"""
Team Shadow Weddings CRM - Database Query Tool
==============================================
A simple CLI tool to query and inspect the SQLite database directly.

Usage:
    python3 query_db.py                    # Show all tables and row counts
    python3 query_db.py tables             # List all tables
    python3 query_db.py customers          # Show all customers
    python3 query_db.py inquiries          # Show all inquiries
    python3 query_db.py "SELECT * FROM users WHERE role='admin'"  # Raw SQL query
    python3 query_db.py --schema users     # Show table schema
"""
import os
import sys
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'teamshadow.db')

# Table display configuration
TABLE_COLUMNS = {
    'users': ['id', 'username', 'email', 'full_name', 'role', 'is_active', 'created_at'],
    'customers': ['id', 'name', 'phone', 'email', 'bride_name', 'groom_name', 'wedding_date', 'venue', 'created_at'],
    'inquiries': ['id', 'customer_id', 'source', 'status', 'event_type', 'guest_count', 'budget_estimate', 'assigned_to', 'created_at'],
    'quotations': ['id', 'quote_number', 'customer_id', 'package_name', 'base_amount', 'discount', 'gst', 'total_amount', 'status', 'created_at'],
    'bookings': ['id', 'booking_number', 'customer_id', 'status', 'total_amount', 'advance_amount', 'balance_amount', 'payment_status', 'event_date', 'created_at'],
    'payments': ['id', 'booking_id', 'amount', 'payment_type', 'payment_method', 'status', 'payment_date'],
    'staff': ['id', 'user_id', 'role', 'specialization', 'is_available', 'daily_rate'],
    'editing_projects': ['id', 'booking_id', 'editor_id', 'designer_id', 'status', 'created_at'],
    'tasks': ['id', 'title', 'status', 'priority', 'assigned_to', 'created_by', 'due_date', 'created_at'],
    'activity_logs': ['id', 'user_id', 'action', 'entity_type', 'entity_id', 'description', 'created_at'],
}


def connect():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Run 'python3 init_db.py' first to create the database.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def list_tables(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print("\n📋 Tables in database:\n")
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {'✅' if count > 0 else '➖'} {table:<20} ({count} rows)")
    return tables


def show_table(conn, table_name):
    if table_name not in TABLE_COLUMNS:
        # Check if it exists
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if table_name in tables:
            print(f"\n⚠️  Showing all columns for '{table_name}':\n")
            cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT 20")
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            print_table(cols, rows)
            print(f"\n({len(rows)} rows shown of {conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]} total)")
            return
        print(f"❌ Unknown table: '{table_name}'")
        print(f"   Available tables: {', '.join(tables)}")
        return

    cols = TABLE_COLUMNS[table_name]
    cursor = conn.execute(f"SELECT {', '.join(cols)} FROM {table_name} LIMIT 50")
    rows = cursor.fetchall()
    total = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

    print(f"\n📊 Table: {table_name} ({total} rows)\n")
    if not rows:
        print("  (empty table)")
        return
    print_table(cols, rows)
    if total > 50:
        print(f"\n  ⚠️  Showing first 50 of {total} rows. Use raw SQL for more.")


def print_table(cols, rows):
    # Calculate column widths
    widths = [len(str(c)) for c in cols]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    # Print header
    header = ' | '.join(str(c).ljust(widths[i]) for i, c in enumerate(cols))
    print('  ' + header)
    print('  ' + '-' * len(header))

    # Print rows
    for row in rows:
        line = ' | '.join(str(v)[:widths[i]].ljust(widths[i]) for i, v in enumerate(row))
        print('  ' + line)


def show_schema(conn, table_name):
    print(f"\n📐 Schema for table: {table_name}\n")
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()
    print_table(['cid', 'name', 'type', 'notnull', 'default', 'pk'], rows)


def run_sql(conn, query):
    print(f"\n🔍 Executing: {query}\n")
    try:
        cursor = conn.execute(query)
        cols = [d[0] for d in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
            print(f"✅ {cursor.rowcount} row(s) affected")
        elif cols:
            print_table(cols, rows)
            print(f"\n({len(rows)} rows returned)")
        else:
            print("✅ Query executed successfully")
    except sqlite3.Error as e:
        print(f"❌ SQL Error: {e}")


def summary(conn):
    print("\n" + "=" * 60)
    print("  📊 TEAM SHADOW CRM - DATABASE SUMMARY")
    print("=" * 60)

    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    for table in ['users', 'customers', 'inquiries', 'quotations', 'bookings', 'payments', 'tasks']:
        if table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<15} : {count} rows")

    # Special queries
    if 'users' in tables:
        admins = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
        staff = conn.execute("SELECT COUNT(*) FROM users WHERE role!='admin'").fetchone()[0]
        print(f"\n  👤 Users breakdown:")
        print(f"    - Admins: {admins}")
        print(f"    - Staff:  {staff}")

    if 'inquiries' in tables:
        print(f"\n  📨 Inquiries by source:")
        for row in conn.execute("SELECT source, COUNT(*) FROM inquiries GROUP BY source ORDER BY COUNT(*) DESC"):
            print(f"    - {row[0]:<12}: {row[1]}")

    if 'bookings' in tables:
        total_rev = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='completed'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM bookings WHERE payment_status IN ('pending','partial')").fetchone()[0]
        print(f"\n  💰 Payments:")
        print(f"    - Total collected: ₹{total_rev:,.0f}")
        print(f"    - Bookings with pending payments: {pending}")

    print("=" * 60)


def main():
    conn = connect()

    if len(sys.argv) < 2:
        summary(conn)
        print("\nUsage:")
        print("  python3 query_db.py tables              # Show all tables")
        print("  python3 query_db.py customers           # Show customers table")
        print("  python3 query_db.py 'SELECT * FROM users'  # Run raw SQL")
        print("  python3 query_db.py --schema users      # Show table schema")
        conn.close()
        return

    arg = sys.argv[1]

    if arg == 'tables':
        list_tables(conn)
    elif arg == '--schema' and len(sys.argv) > 2:
        show_schema(conn, sys.argv[2])
    elif arg in TABLE_COLUMNS:
        show_table(conn, arg)
    elif arg.lower() in ['summary', 'overview']:
        summary(conn)
    elif arg.startswith('--'):
        print(f"❌ Unknown option: {arg}")
    else:
        run_sql(conn, arg)

    conn.close()


if __name__ == '__main__':
    main()
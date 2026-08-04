# 🔐 Team Shadow CRM - Security & Deployment Guide

## Is the Current Database Enough for Deployment?

### ✅ Yes, for Small Business Use
The current **SQLite** database is sufficient for:
- **1-10 team members** using the system simultaneously
- **Up to 10,000+ records** (customers, inquiries, bookings)
- **Single server deployment** (one machine hosting the app)
- **Local/office use** or small VPS deployment

### ⚠️ When to Upgrade to PostgreSQL
Consider upgrading when:
- Multiple offices need to access the same data
- You expect **50+ concurrent users**
- You need advanced reporting/analytics
- You need automatic backups and replication
- Data grows beyond 100,000 records

**Upgrade path:** The code already uses SQLAlchemy ORM, so switching to PostgreSQL is just changing the database URL in `backend/app/database.py`.

---

## 🔒 Security Features Already Implemented

| Feature | Status | Details |
|---------|--------|---------|
| **Password Hashing** | ✅ | SHA-256 with salt (not plain text) |
| **JWT Authentication** | ✅ | 7-day tokens with role claims |
| **Role-Based Access** | ✅ | Admin vs Staff permissions |
| **CORS Protection** | ✅ | Configurable allowed origins |
| **Input Validation** | ✅ | Pydantic schemas validate all requests |
| **SQL Injection Protection** | ✅ | SQLAlchemy ORM parameterized queries |
| **Session Expiry** | ✅ | Tokens expire after 7 days |

---

## 🚀 Deployment Security Checklist

### 1. Change Default Passwords (CRITICAL)
```bash
# Login as admin and change password immediately
# Or update via API:
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Set a Strong JWT Secret
Edit `backend/app/auth.py`:
```python
# Change this to a long random string
SECRET_KEY = "your-very-long-random-secret-key-here"
```

### 3. Restrict CORS Origins
Edit `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Only your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Enable HTTPS
For production, always use HTTPS:
- **Option A:** Use a reverse proxy (Nginx/Caddy) with SSL
- **Option B:** Deploy on platforms with built-in SSL (Railway, Render, Fly.io)

### 5. Database Backup Strategy
```bash
# Manual backup
cp backend/teamshadow.db backups/teamshadow-$(date +%Y%m%d).db

# Automated daily backup (cron)
0 2 * * * cp /path/to/teamshadow.db /backups/teamshadow-$(date +\%Y\%m\%d).db
```

### 6. Environment Variables
Create a `.env` file (never commit to git):
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./teamshadow.db
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 📊 How to Check Database Data Directly

### Option 1: Use the Query Tool (Recommended)
```bash
# Show database summary
python3 query_db.py

# List all tables
python3 query_db.py tables

# Show customers table
python3 query_db.py customers

# Run raw SQL
python3 query_db.py "SELECT * FROM users WHERE role='admin'"

# Show table schema
python3 query_db.py --schema users
```

### Option 2: Use SQLite CLI
```bash
sqlite3 backend/teamshadow.db
# Then run SQL commands:
# .tables
# SELECT * FROM users;
# SELECT * FROM customers LIMIT 10;
```

### Option 3: Use DB Browser (GUI)
1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `backend/teamshadow.db`
3. Browse tables, run queries, export data

### Option 4: Use VS Code Extension
1. Install "SQLite Viewer" or "SQLite" extension in VS Code
2. Open `backend/teamshadow.db`
3. Browse and query data visually

---

## 🛡️ Recommended Production Stack

| Component | Free Option | Paid Option |
|-----------|------------|-------------|
| **Hosting** | Railway/Render free tier | AWS EC2, DigitalOcean |
| **Database** | SQLite (current) | PostgreSQL (RDS) |
| **HTTPS** | Caddy auto-SSL | Cloudflare |
| **Backups** | Cron + S3 | AWS Backup |
| **Monitoring** | UptimeRobot | Datadog |

---

## 🔑 User Roles & Permissions

### Admin Role
- ✅ Full access to all modules
- ✅ Create/manage staff accounts
- ✅ Assign tasks to staff
- ✅ View all customer data
- ✅ Manage quotations, bookings, payments
- ✅ Delete records

### Staff Role
- ✅ View Dashboard
- ✅ View and update their assigned tasks
- ✅ Add progress notes to tasks
- ✅ Update task status (pending → in_progress → completed)
- ❌ Cannot see other staff tasks
- ❌ Cannot create/delete tasks
- ❌ Cannot access customer management

---

## 📁 Database File Location
```
backend/teamshadow.db
```

### Important Notes
- The database file is **excluded from git** (in .gitignore)
- Each deployment has its own database
- To reset: delete the file and run `python3 init_db.py`
- Always backup before upgrading
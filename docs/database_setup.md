# Database Setup Script for PostgreSQL

## Step 1: Install PostgreSQL

### Windows
Download from: https://www.postgresql.org/download/windows/
- Choose PostgreSQL 13 or higher
- During installation, remember your postgres user password
- Default port: 5432

### Mac
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

---

## Step 2: Create Database

### Method 1: Using psql command line
```bash
# Connect as postgres user
psql -U postgres

# Inside psql:
CREATE DATABASE med_chatbot;
CREATE USER med_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE med_chatbot TO med_user;
\q
```

### Method 2: Using pgAdmin (GUI)
1. Open pgAdmin
2. Right-click on Databases → Create → Database
3. Name: `med_chatbot`
4. Save

---

## Step 3: Configure .env

Copy `.env.example` to `.env` and update:

```bash
# If using postgres user (development)
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/med_chatbot

# If using custom user
DATABASE_URL=postgresql://med_user:secure_password_here@localhost:5432/med_chatbot
```

---

## Step 4: Verify Connection

Run this Python script to test connection:

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:password@localhost:5432/med_chatbot"
engine = create_engine(DATABASE_URL)

try:
    connection = engine.connect()
    print("✅ Database connection successful!")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## Step 5: Run Backend (Tables Auto-Create)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tables will be created automatically on first run!

---

## Verify Tables Created

```sql
-- Connect to database
psql -U postgres -d med_chatbot

-- List all tables
\dt

-- Expected output:
-- users
-- doctors
-- nurses
-- patients

-- Check users table structure
\d users

-- Exit
\q
```

---

## Troubleshooting

### Error: "FATAL: password authentication failed"
1. Check your password in .env
2. Verify PostgreSQL is running: `pg_ctl status`
3. Reset postgres password:
   ```bash
   psql -U postgres
   ALTER USER postgres PASSWORD 'new_password';
   ```

### Error: "connection refused"
1. Check PostgreSQL is running:
   - Windows: Services → postgresql
   - Mac: `brew services list`
   - Linux: `sudo systemctl status postgresql`
2. Check port 5432 is not blocked

### Error: "database does not exist"
Run: `CREATE DATABASE med_chatbot;` in psql

---

## Optional: Sample Data for Testing

```sql
-- Connect to database
psql -U postgres -d med_chatbot

-- This is just for reference - use the API to create users!
-- The backend will hash passwords properly

-- Check if tables are empty
SELECT COUNT(*) FROM users;

-- Exit and use the /api/auth/register endpoint instead!
\q
```

---

## Database Schema Overview

```
users (base table)
  ├── doctors (1:1 with users, role='doctor')
  ├── nurses (1:1 with users, role='nurse')
  └── patients (1:1 with users, role='patient')
      └── assigned_doctor_id → doctors.id (many:1)

Future tables (STEP 2+):
- alerts
- vitals
- chat_history
- daily_checkins
```

---

## Backup & Restore (Optional)

### Backup
```bash
pg_dump -U postgres med_chatbot > backup.sql
```

### Restore
```bash
psql -U postgres med_chatbot < backup.sql
```

---

## Reset Database (If Needed)

```sql
-- Connect as postgres
psql -U postgres

-- Drop and recreate
DROP DATABASE med_chatbot;
CREATE DATABASE med_chatbot;
\q

-- Restart backend - tables will be recreated
```

---

## Production Considerations (Future)

For production deployment:
1. Use environment-specific .env files
2. Enable SSL for database connections
3. Use Alembic for database migrations
4. Set up regular backups
5. Use connection pooling
6. Monitor database performance

For now, simple setup is perfect for hackathon!

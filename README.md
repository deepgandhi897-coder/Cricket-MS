# 🏏 Cricket Management System

A full-stack **Cricket Management System** built with **Python Flask** and **Oracle Database** (hosted on FreeSQL.com / Oracle Cloud) designed to demonstrate relational database concepts, SQL constraints, joins, and aggregations.

---

## 📌 Features & Modules

- **Dashboard**:
  - Live counts for Teams, Players, and Matches using `COUNT()`
  - Recent matches list showing competing teams, match format, venue, and winner using SQL `JOIN`
- **Teams Module (CRUD)**:
  - Add, View, Edit, and Delete teams
  - Tracks Team Name, Coach, Home Ground, Founded Year, and total player count via `LEFT JOIN` + `GROUP BY`
- **Players Module (CRUD)**:
  - Add, View, Edit, and Delete players
  - Assign players to teams (Foreign Key relationship)
  - Filter players by team
  - Badges for player roles: *Batsman*, *Bowler*, *All-Rounder*, *Wicket-Keeper*
- **Matches Module (CRUD)**:
  - Record matches between Team 1 and Team 2 with Date, Venue, and Match Type (`T20`, `ODI`, `Test`)
  - Select Winner from participating teams
- **Player Statistics Module**:
  - Log player match performance (Runs, Wickets, Catches, Highest Score)
  - Leaderboard showing Total Matches, Runs, Highest Score, Wickets, and Catches using `SUM()`, `MAX()`, `COUNT()`, and `NVL()`

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, Font Awesome 6
- **Backend**: Python 3, Flask 3.0.3
- **Database**: Oracle Database 23ai / FreeSQL.com
- **Driver**: `python-oracledb` (Thin Mode — no Oracle Client installation required)

---

## 🗄️ Database Schema & Constraints

The project implements 4 relational tables:

1. **`TEAMS`**:
   - `TEAM_ID` (PK, Identity)
   - `TEAM_NAME` (VARCHAR2, NOT NULL, UNIQUE)
   - `COACH_NAME` (VARCHAR2, NOT NULL)
   - `HOME_GROUND` (VARCHAR2, NOT NULL)
   - `FOUNDED_YEAR` (NUMBER, CHECK between 1800 and 2100)

2. **`PLAYERS`**:
   - `PLAYER_ID` (PK, Identity)
   - `PLAYER_NAME` (VARCHAR2, NOT NULL)
   - `TEAM_ID` (FK → `TEAMS.TEAM_ID` ON DELETE SET NULL)
   - `ROLE` (VARCHAR2, CHECK IN 'Batsman', 'Bowler', 'All-Rounder', 'Wicket-Keeper')
   - `JERSEY_NO` (NUMBER, NOT NULL)
   - `NATIONALITY` (VARCHAR2, NOT NULL)

3. **`MATCHES`**:
   - `MATCH_ID` (PK, Identity)
   - `TEAM1_ID` (FK → `TEAMS.TEAM_ID`)
   - `TEAM2_ID` (FK → `TEAMS.TEAM_ID`)
   - `WINNER_ID` (FK → `TEAMS.TEAM_ID`, Nullable)
   - `MATCH_DATE` (DATE, NOT NULL)
   - `VENUE` (VARCHAR2, NOT NULL)
   - `MATCH_TYPE` (VARCHAR2, CHECK IN 'Test', 'ODI', 'T20')

4. **`PLAYER_STATISTICS`**:
   - `STAT_ID` (PK, Identity)
   - `PLAYER_ID` (FK → `PLAYERS.PLAYER_ID`)
   - `MATCH_ID` (FK → `MATCHES.MATCH_ID`)
   - `RUNS` (NUMBER, DEFAULT 0, CHECK >= 0)
   - `WICKETS` (NUMBER, DEFAULT 0, CHECK >= 0)
   - `CATCHES` (NUMBER, DEFAULT 0, CHECK >= 0)
   - `IS_HIGHEST_SCORE` (CHAR(1), CHECK IN 'Y', 'N')

---

## 📚 DBMS Concepts Demonstrated

- **DDL**: `CREATE TABLE`, constraints (`PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK`)
- **DML**: `INSERT`, `UPDATE`, `DELETE`, `SELECT`
- **Clauses**: `WHERE`, `ORDER BY`, `GROUP BY`
- **Aggregate Functions**: `COUNT()`, `SUM()`, `MAX()`
- **Null Handling**: `NVL()`
- **Joins**: Multi-table `JOIN`, `LEFT JOIN`
- **Referential Integrity**: Cascading deletes & foreign key constraints

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/deepgandhi897-coder/Cricket-MS.git
cd Cricket-MS
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database Credentials
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `.env` with your Oracle / FreeSQL credentials:
```ini
ORACLE_USER=your_oracle_username
ORACLE_PASSWORD=your_oracle_password
ORACLE_DSN=tcps://db.freesql.com:2484/your_service_name
```

### 4. Initialize Database
Run the database setup script to create tables and insert sample records:
```bash
python init_db.py
```
*(Alternatively, execute `sql/schema.sql` directly in Oracle SQL Developer or the FreeSQL SQL Web console).*

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## ⚡ Deploy to Vercel

1. **Push your code to GitHub**:
   ```bash
   git push
   ```
2. **Import Project into Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
   - Click **Add New...** → **Project**.
   - Select the `Cricket-MS` repository.
3. **Configure Environment Variables in Vercel**:
   Under the **Environment Variables** section in Vercel, add:
   - `ORACLE_USER` = `your_oracle_username`
   - `ORACLE_PASSWORD` = `your_oracle_password`
   - `ORACLE_DSN` = `tcps://db.freesql.com:2484/your_service_name`
4. **Deploy**:
   - Click **Deploy**. Vercel will build the serverless functions and provide your live production URL (e.g. `https://cricket-ms.vercel.app`).


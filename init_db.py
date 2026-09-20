"""
init_db.py — Initialize Oracle Database Schema and Sample Data
Executes schema.sql against the configured Oracle Database.
"""

import re
from db import get_connection

def run_init():
    print("Connecting to Oracle Database...")
    conn = get_connection()
    cur = conn.cursor()
    print("Connected successfully!")

    with open("sql/schema.sql", "r", encoding="utf-8") as f:
        content = f.read()

    # Step 1: Drop tables if they exist
    tables = ["PLAYER_STATISTICS", "MATCHES", "PLAYERS", "TEAMS"]
    for t in tables:
        try:
            cur.execute(f"DROP TABLE {t} CASCADE CONSTRAINTS")
            print(f"Dropped existing table: {t}")
        except Exception:
            pass  # Table didn't exist, ignore

    # Extract CREATE TABLE statements
    create_tables = [
        """CREATE TABLE TEAMS (
            TEAM_ID      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            TEAM_NAME    VARCHAR2(100) NOT NULL,
            COACH_NAME   VARCHAR2(100) NOT NULL,
            HOME_GROUND  VARCHAR2(150) NOT NULL,
            FOUNDED_YEAR NUMBER(4)     CHECK (FOUNDED_YEAR BETWEEN 1800 AND 2100),
            CONSTRAINT uq_team_name UNIQUE (TEAM_NAME)
        )""",
        """CREATE TABLE PLAYERS (
            PLAYER_ID   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            PLAYER_NAME VARCHAR2(100)  NOT NULL,
            TEAM_ID     NUMBER,
            ROLE        VARCHAR2(50)   NOT NULL
                            CHECK (ROLE IN ('Batsman','Bowler','All-Rounder','Wicket-Keeper')),
            JERSEY_NO   NUMBER(3)      NOT NULL,
            NATIONALITY VARCHAR2(50)   NOT NULL,
            CONSTRAINT fk_player_team
                FOREIGN KEY (TEAM_ID) REFERENCES TEAMS(TEAM_ID)
                ON DELETE SET NULL
        )""",
        """CREATE TABLE MATCHES (
            MATCH_ID   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            TEAM1_ID   NUMBER          NOT NULL,
            TEAM2_ID   NUMBER          NOT NULL,
            WINNER_ID  NUMBER,
            MATCH_DATE DATE            NOT NULL,
            VENUE      VARCHAR2(150)   NOT NULL,
            MATCH_TYPE VARCHAR2(10)    NOT NULL
                            CHECK (MATCH_TYPE IN ('Test','ODI','T20')),
            CONSTRAINT fk_match_team1  FOREIGN KEY (TEAM1_ID)  REFERENCES TEAMS(TEAM_ID),
            CONSTRAINT fk_match_team2  FOREIGN KEY (TEAM2_ID)  REFERENCES TEAMS(TEAM_ID),
            CONSTRAINT fk_match_winner FOREIGN KEY (WINNER_ID) REFERENCES TEAMS(TEAM_ID)
        )""",
        """CREATE TABLE PLAYER_STATISTICS (
            STAT_ID          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            PLAYER_ID        NUMBER NOT NULL,
            MATCH_ID         NUMBER NOT NULL,
            RUNS             NUMBER DEFAULT 0  CHECK (RUNS    >= 0),
            WICKETS          NUMBER DEFAULT 0  CHECK (WICKETS >= 0),
            CATCHES          NUMBER DEFAULT 0  CHECK (CATCHES >= 0),
            IS_HIGHEST_SCORE CHAR(1) DEFAULT 'N'
                                 CHECK (IS_HIGHEST_SCORE IN ('Y','N')),
            CONSTRAINT fk_stat_player FOREIGN KEY (PLAYER_ID) REFERENCES PLAYERS(PLAYER_ID),
            CONSTRAINT fk_stat_match  FOREIGN KEY (MATCH_ID)  REFERENCES MATCHES(MATCH_ID)
        )"""
    ]

    for stmt in create_tables:
        tbl_name = stmt.split()[2]
        print(f"Creating table {tbl_name}...")
        cur.execute(stmt)

    print("Tables created successfully!")

    # Parse and execute all INSERT statements from schema.sql
    inserts = re.findall(r"(INSERT INTO .*?;)", content, re.DOTALL | re.IGNORECASE)
    print(f"Executing {len(inserts)} sample data inserts...")
    for ins in inserts:
        # Strip trailing semicolon
        query = ins.strip().rstrip(";")
        cur.execute(query)

    conn.commit()
    print(f"Sample data inserted and committed successfully!")

    # Verify counts
    for tbl in ["TEAMS", "PLAYERS", "MATCHES", "PLAYER_STATISTICS"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        cnt = cur.fetchone()[0]
        print(f"  {tbl}: {cnt} rows")

    cur.close()
    conn.close()
    print("\nDatabase initialization complete! You can now run python app.py")

if __name__ == "__main__":
    run_init()

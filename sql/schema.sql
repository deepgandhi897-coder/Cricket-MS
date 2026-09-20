-- ============================================================
--  Cricket Management System — Oracle SQL Schema & Sample Data
--  Compatible with Oracle 12c+ / FreeSQL.com
--
--  SQL Concepts Demonstrated:
--    CREATE TABLE, PRIMARY KEY, FOREIGN KEY,
--    NOT NULL, CHECK, UNIQUE, IDENTITY,
--    INSERT, SELECT, UPDATE, DELETE,
--    WHERE, ORDER BY, GROUP BY,
--    COUNT(), SUM(), MAX(), JOIN, LEFT JOIN, NVL
-- ============================================================


-- ------------------------------------------------------------
--  STEP 1: Drop existing tables (safe re-run)
--  Reverse FK order: stats → matches → players → teams
-- ------------------------------------------------------------

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE PLAYER_STATISTICS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE MATCHES CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE PLAYERS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE TEAMS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/


-- ------------------------------------------------------------
--  STEP 2: CREATE TABLES
-- ------------------------------------------------------------

-- TEAMS Table
-- Constraints: PRIMARY KEY, NOT NULL, UNIQUE, CHECK
CREATE TABLE TEAMS (
    TEAM_ID      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    TEAM_NAME    VARCHAR2(100) NOT NULL,
    COACH_NAME   VARCHAR2(100) NOT NULL,
    HOME_GROUND  VARCHAR2(150) NOT NULL,
    FOUNDED_YEAR NUMBER(4)     CHECK (FOUNDED_YEAR BETWEEN 1800 AND 2100),
    CONSTRAINT uq_team_name UNIQUE (TEAM_NAME)
);

-- PLAYERS Table
-- Constraints: PRIMARY KEY, FOREIGN KEY, NOT NULL, CHECK
-- ON DELETE SET NULL → player remains but becomes "Unassigned" if team is deleted
CREATE TABLE PLAYERS (
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
);

-- MATCHES Table
-- Constraints: PRIMARY KEY, FOREIGN KEY × 3, NOT NULL, CHECK
CREATE TABLE MATCHES (
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
);

-- PLAYER_STATISTICS Table
-- Constraints: PRIMARY KEY, FOREIGN KEY × 2, NOT NULL, DEFAULT, CHECK
CREATE TABLE PLAYER_STATISTICS (
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
);


-- ------------------------------------------------------------
--  STEP 3: INSERT Sample Data — TEAMS (5 teams)
-- ------------------------------------------------------------

INSERT INTO TEAMS (TEAM_NAME, COACH_NAME, HOME_GROUND, FOUNDED_YEAR)
VALUES ('Mumbai Warriors',    'Sachin Tendulkar',    'Wankhede Stadium',              2008);

INSERT INTO TEAMS (TEAM_NAME, COACH_NAME, HOME_GROUND, FOUNDED_YEAR)
VALUES ('Chennai Kings',      'MS Dhoni',            'M.A. Chidambaram Stadium',      2008);

INSERT INTO TEAMS (TEAM_NAME, COACH_NAME, HOME_GROUND, FOUNDED_YEAR)
VALUES ('Delhi Dragons',      'Virat Kohli',         'Arun Jaitley Stadium',          2008);

INSERT INTO TEAMS (TEAM_NAME, COACH_NAME, HOME_GROUND, FOUNDED_YEAR)
VALUES ('Kolkata Tigers',     'Sourav Ganguly',      'Eden Gardens',                  2008);

INSERT INTO TEAMS (TEAM_NAME, COACH_NAME, HOME_GROUND, FOUNDED_YEAR)
VALUES ('Rajasthan Royals XI','Shane Warne',         'Sawai Mansingh Stadium',        2008);

COMMIT;


-- ------------------------------------------------------------
--  STEP 4: INSERT Sample Data — PLAYERS (15 players)
-- ------------------------------------------------------------

-- Mumbai Warriors (TEAM_ID = 1)
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Rohit Sharma',   1, 'Batsman',       45,  'Indian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Jasprit Bumrah', 1, 'Bowler',        93,  'Indian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Hardik Pandya',  1, 'All-Rounder',   228, 'Indian');

-- Chennai Kings (TEAM_ID = 2)
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('MS Dhoni',        2, 'Wicket-Keeper',  7,  'Indian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Ravindra Jadeja', 2, 'All-Rounder',    8,  'Indian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Deepak Chahar',   2, 'Bowler',         90, 'Indian');

-- Delhi Dragons (TEAM_ID = 3)
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Virat Kohli',  3, 'Batsman', 18, 'Indian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('David Warner', 3, 'Batsman', 31, 'Australian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Anrich Nortje', 3, 'Bowler',  17, 'South African');

-- Kolkata Tigers (TEAM_ID = 4)
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Andre Russell',  4, 'All-Rounder', 12, 'Jamaican');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Sunil Narine',   4, 'Bowler',      74, 'Trinidadian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Shreyas Iyer',   4, 'Batsman',     41, 'Indian');

-- Rajasthan Royals XI (TEAM_ID = 5)
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Sanju Samson',      5, 'Wicket-Keeper',  9,  'Indian');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Jos Buttler',       5, 'Batsman',        63, 'English');
INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE,           JERSEY_NO, NATIONALITY)
VALUES ('Yuzvendra Chahal',  5, 'Bowler',          3, 'Indian');

COMMIT;


-- ------------------------------------------------------------
--  STEP 5: INSERT Sample Data — MATCHES (5 matches)
-- ------------------------------------------------------------

-- Match 1: Mumbai vs Chennai  → Mumbai won
INSERT INTO MATCHES (TEAM1_ID, TEAM2_ID, WINNER_ID, MATCH_DATE, VENUE, MATCH_TYPE)
VALUES (1, 2, 1, TO_DATE('2024-03-15','YYYY-MM-DD'), 'Wankhede Stadium, Mumbai',             'T20');

-- Match 2: Delhi vs Kolkata   → Kolkata won
INSERT INTO MATCHES (TEAM1_ID, TEAM2_ID, WINNER_ID, MATCH_DATE, VENUE, MATCH_TYPE)
VALUES (3, 4, 4, TO_DATE('2024-03-20','YYYY-MM-DD'), 'Eden Gardens, Kolkata',                'T20');

-- Match 3: Chennai vs Rajasthan → Chennai won
INSERT INTO MATCHES (TEAM1_ID, TEAM2_ID, WINNER_ID, MATCH_DATE, VENUE, MATCH_TYPE)
VALUES (2, 5, 2, TO_DATE('2024-03-25','YYYY-MM-DD'), 'M.A. Chidambaram Stadium, Chennai',    'ODI');

-- Match 4: Mumbai vs Delhi    → Delhi won
INSERT INTO MATCHES (TEAM1_ID, TEAM2_ID, WINNER_ID, MATCH_DATE, VENUE, MATCH_TYPE)
VALUES (1, 3, 3, TO_DATE('2024-04-01','YYYY-MM-DD'), 'Arun Jaitley Stadium, Delhi',          'T20');

-- Match 5: Kolkata vs Rajasthan → Kolkata won
INSERT INTO MATCHES (TEAM1_ID, TEAM2_ID, WINNER_ID, MATCH_DATE, VENUE, MATCH_TYPE)
VALUES (4, 5, 4, TO_DATE('2024-04-05','YYYY-MM-DD'), 'Eden Gardens, Kolkata',                'ODI');

COMMIT;


-- ------------------------------------------------------------
--  STEP 6: INSERT Sample Data — PLAYER_STATISTICS
-- ------------------------------------------------------------

-- Match 1 (Mumbai vs Chennai)
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (1, 1, 89, 0, 1, 'Y');   -- Rohit Sharma
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (2, 1,  5, 3, 0, 'N');   -- Jasprit Bumrah
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (4, 1, 34, 0, 2, 'N');   -- MS Dhoni

-- Match 2 (Delhi vs Kolkata)
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (7,  2, 42, 0, 1, 'N');  -- Virat Kohli
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (10, 2, 67, 1, 0, 'Y');  -- Andre Russell
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (11, 2,  8, 4, 1, 'N');  -- Sunil Narine

-- Match 3 (Chennai vs Rajasthan)
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (5,  3, 51, 2, 2, 'Y');  -- Ravindra Jadeja
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (13, 3, 38, 0, 1, 'N');  -- Sanju Samson
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (14, 3, 45, 0, 0, 'N');  -- Jos Buttler

-- Match 4 (Mumbai vs Delhi)
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (3, 4, 72, 1, 0, 'Y');   -- Hardik Pandya
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (7, 4, 55, 0, 1, 'N');   -- Virat Kohli
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (9, 4, 15, 3, 0, 'N');   -- Anrich Nortje

-- Match 5 (Kolkata vs Rajasthan)
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (10, 5, 85, 0, 2, 'Y');  -- Andre Russell
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (12, 5, 23, 0, 1, 'N');  -- Shreyas Iyer
INSERT INTO PLAYER_STATISTICS (PLAYER_ID,MATCH_ID,RUNS,WICKETS,CATCHES,IS_HIGHEST_SCORE)
VALUES (15, 5, 11, 2, 0, 'N');  -- Yuzvendra Chahal

COMMIT;


-- ============================================================
--  STEP 7: Verification Queries (run these to confirm data)
-- ============================================================

-- Total counts
SELECT 'TEAMS'             AS tbl, COUNT(*) AS cnt FROM TEAMS UNION ALL
SELECT 'PLAYERS',                  COUNT(*)         FROM PLAYERS UNION ALL
SELECT 'MATCHES',                  COUNT(*)         FROM MATCHES UNION ALL
SELECT 'PLAYER_STATISTICS',        COUNT(*)         FROM PLAYER_STATISTICS;

-- JOIN: All matches with team names and winner
SELECT m.MATCH_ID,
       t1.TEAM_NAME AS Team1, t2.TEAM_NAME AS Team2,
       w.TEAM_NAME  AS Winner,
       TO_CHAR(m.MATCH_DATE,'DD-Mon-YYYY') AS MatchDate,
       m.MATCH_TYPE
FROM   MATCHES m
JOIN   TEAMS t1 ON m.TEAM1_ID  = t1.TEAM_ID
JOIN   TEAMS t2 ON m.TEAM2_ID  = t2.TEAM_ID
LEFT JOIN TEAMS w ON m.WINNER_ID = w.TEAM_ID
ORDER BY m.MATCH_DATE;

-- GROUP BY + SUM + MAX + COUNT: Player statistics summary
SELECT p.PLAYER_NAME,
       t.TEAM_NAME,
       COUNT(ps.MATCH_ID)       AS Matches_Played,
       NVL(SUM(ps.RUNS),    0)  AS Total_Runs,
       NVL(MAX(ps.RUNS),    0)  AS Highest_Score,
       NVL(SUM(ps.WICKETS), 0)  AS Total_Wickets,
       NVL(SUM(ps.CATCHES), 0)  AS Total_Catches
FROM   PLAYERS p
LEFT JOIN TEAMS t             ON p.TEAM_ID    = t.TEAM_ID
LEFT JOIN PLAYER_STATISTICS ps ON p.PLAYER_ID = ps.PLAYER_ID
GROUP BY p.PLAYER_NAME, t.TEAM_NAME
ORDER BY Total_Runs DESC NULLS LAST;

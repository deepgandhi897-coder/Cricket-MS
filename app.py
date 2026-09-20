"""
app.py — Cricket Management System
Flask Application with Oracle Database

Modules:
  - Dashboard  : Overview stats + recent matches
  - Teams      : Full CRUD (Create, Read, Update, Delete)
  - Players    : Full CRUD + team assignment
  - Matches    : Full CRUD + team1 / team2 / winner selection
  - Statistics : Player match stats (INSERT + aggregated GROUP BY view)

SQL Concepts Used:
  CREATE, INSERT, SELECT, UPDATE, DELETE,
  WHERE, ORDER BY, GROUP BY, COUNT, MAX, SUM, JOIN, LEFT JOIN
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection, fetch_all, fetch_one
import oracledb

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.getenv("SECRET_KEY", "cricket_mgmt_secret_2024")


# ==============================================================
#  DASHBOARD
# ==============================================================

@app.route("/")
@app.route("/api/index")
@app.route("/api/index.py")
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    # COUNT() — total rows in each table
    cur.execute("SELECT COUNT(*) FROM TEAMS")
    total_teams = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM PLAYERS")
    total_players = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM MATCHES")
    total_matches = cur.fetchone()[0]

    # JOIN — recent 5 matches with team names
    cur.execute("""
        SELECT m.MATCH_ID,
               t1.TEAM_NAME                         AS team1,
               t2.TEAM_NAME                         AS team2,
               w.TEAM_NAME                          AS winner,
               TO_CHAR(m.MATCH_DATE,'DD-Mon-YYYY')  AS match_date,
               m.VENUE,
               m.MATCH_TYPE
        FROM   MATCHES m
        JOIN   TEAMS t1 ON m.TEAM1_ID  = t1.TEAM_ID
        JOIN   TEAMS t2 ON m.TEAM2_ID  = t2.TEAM_ID
        LEFT JOIN TEAMS w ON m.WINNER_ID = w.TEAM_ID
        ORDER BY m.MATCH_DATE DESC
        FETCH FIRST 5 ROWS ONLY
    """)
    recent_matches = fetch_all(cur)

    cur.close()
    conn.close()

    return render_template("dashboard.html",
                           total_teams=total_teams,
                           total_players=total_players,
                           total_matches=total_matches,
                           recent_matches=recent_matches)


# ==============================================================
#  TEAMS — CRUD
# ==============================================================

@app.route("/teams/")
def teams_list():
    """SELECT + LEFT JOIN + GROUP BY + COUNT — list teams with player count."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.TEAM_ID,
               t.TEAM_NAME,
               t.COACH_NAME,
               t.HOME_GROUND,
               t.FOUNDED_YEAR,
               COUNT(p.PLAYER_ID) AS player_count
        FROM   TEAMS t
        LEFT JOIN PLAYERS p ON t.TEAM_ID = p.TEAM_ID
        GROUP BY t.TEAM_ID, t.TEAM_NAME, t.COACH_NAME, t.HOME_GROUND, t.FOUNDED_YEAR
        ORDER BY t.TEAM_NAME
    """)
    teams = fetch_all(cur)
    cur.close()
    conn.close()
    return render_template("teams/list.html", teams=teams)


@app.route("/teams/add", methods=["GET", "POST"])
def teams_add():
    """INSERT INTO TEAMS — add a new team."""
    if request.method == "POST":
        name   = request.form["team_name"].strip()
        coach  = request.form["coach_name"].strip()
        ground = request.form["home_ground"].strip()
        year   = request.form["founded_year"].strip()

        if not name or not coach or not ground:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("teams_add"))

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO TEAMS (TEAM_NAME, COACH_NAME, HOME_GROUND, FOUNDED_YEAR)
                VALUES (:1, :2, :3, :4)
            """, (name, coach, ground, int(year) if year else None))
            conn.commit()
            cur.close()
            conn.close()
            flash(f'Team "{name}" added successfully!', "success")
            return redirect(url_for("teams_list"))
        except oracledb.IntegrityError:
            flash("Team name already exists. Please use a unique name.", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("teams/form.html", team=None, action="Add")


@app.route("/teams/edit/<int:team_id>", methods=["GET", "POST"])
def teams_edit(team_id):
    """SELECT + UPDATE — edit existing team."""
    conn = get_connection()
    cur  = conn.cursor()

    if request.method == "POST":
        name   = request.form["team_name"].strip()
        coach  = request.form["coach_name"].strip()
        ground = request.form["home_ground"].strip()
        year   = request.form["founded_year"].strip()

        try:
            cur.execute("""
                UPDATE TEAMS
                SET    TEAM_NAME=:1, COACH_NAME=:2, HOME_GROUND=:3, FOUNDED_YEAR=:4
                WHERE  TEAM_ID=:5
            """, (name, coach, ground, int(year) if year else None, team_id))
            conn.commit()
            cur.close()
            conn.close()
            flash("Team updated successfully!", "success")
            return redirect(url_for("teams_list"))
        except oracledb.IntegrityError:
            flash("Team name already exists.", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")

    # SELECT for pre-populating the form
    cur.execute("SELECT * FROM TEAMS WHERE TEAM_ID = :1", (team_id,))
    team = fetch_one(cur)
    cur.close()
    conn.close()

    if not team:
        flash("Team not found.", "danger")
        return redirect(url_for("teams_list"))

    return render_template("teams/form.html", team=team, action="Edit")


@app.route("/teams/delete/<int:team_id>", methods=["POST"])
def teams_delete(team_id):
    """DELETE FROM TEAMS — remove a team."""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("SELECT TEAM_NAME FROM TEAMS WHERE TEAM_ID = :1", (team_id,))
        row  = cur.fetchone()
        name = row[0] if row else f"ID {team_id}"

        cur.execute("DELETE FROM TEAMS WHERE TEAM_ID = :1", (team_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash(f'Team "{name}" deleted successfully!', "success")
    except oracledb.IntegrityError:
        flash("Cannot delete: team has matches or players assigned. Remove them first.", "danger")
    except Exception as e:
        flash(f"Error: {e}", "danger")

    return redirect(url_for("teams_list"))


# ==============================================================
#  PLAYERS — CRUD + TEAM ASSIGNMENT
# ==============================================================

@app.route("/players/")
def players_list():
    """SELECT + LEFT JOIN — players with team name; optional WHERE filter."""
    conn     = get_connection()
    cur      = conn.cursor()
    team_filter = request.args.get("team_id", "")

    sql = """
        SELECT p.PLAYER_ID, p.PLAYER_NAME, p.ROLE, p.JERSEY_NO,
               p.NATIONALITY, p.TEAM_ID,
               t.TEAM_NAME
        FROM   PLAYERS p
        LEFT JOIN TEAMS t ON p.TEAM_ID = t.TEAM_ID
    """
    params = []
    if team_filter:
        sql    += " WHERE p.TEAM_ID = :1"
        params  = [int(team_filter)]
    sql += " ORDER BY p.PLAYER_NAME"

    cur.execute(sql, params)
    players = fetch_all(cur)

    cur.execute("SELECT TEAM_ID, TEAM_NAME FROM TEAMS ORDER BY TEAM_NAME")
    teams = fetch_all(cur)

    cur.close()
    conn.close()
    return render_template("players/list.html",
                           players=players,
                           teams=teams,
                           selected_team=team_filter)


@app.route("/players/add", methods=["GET", "POST"])
def players_add():
    """INSERT INTO PLAYERS — register a new player and optionally assign a team."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT TEAM_ID, TEAM_NAME FROM TEAMS ORDER BY TEAM_NAME")
    teams = fetch_all(cur)

    if request.method == "POST":
        pname       = request.form["player_name"].strip()
        role        = request.form["role"]
        jersey      = request.form["jersey_no"].strip()
        nationality = request.form["nationality"].strip()
        team_id     = request.form.get("team_id") or None

        if not pname or not jersey or not nationality:
            flash("Please fill in all required fields.", "danger")
            cur.close(); conn.close()
            return render_template("players/form.html", player=None, teams=teams, action="Add")

        try:
            cur.execute("""
                INSERT INTO PLAYERS (PLAYER_NAME, TEAM_ID, ROLE, JERSEY_NO, NATIONALITY)
                VALUES (:1, :2, :3, :4, :5)
            """, (pname, int(team_id) if team_id else None, role, int(jersey), nationality))
            conn.commit()
            flash(f'Player "{pname}" added successfully!', "success")
            cur.close(); conn.close()
            return redirect(url_for("players_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    cur.close()
    conn.close()
    return render_template("players/form.html", player=None, teams=teams, action="Add")


@app.route("/players/edit/<int:player_id>", methods=["GET", "POST"])
def players_edit(player_id):
    """SELECT + UPDATE — edit player details and team assignment."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT TEAM_ID, TEAM_NAME FROM TEAMS ORDER BY TEAM_NAME")
    teams = fetch_all(cur)

    if request.method == "POST":
        pname       = request.form["player_name"].strip()
        role        = request.form["role"]
        jersey      = request.form["jersey_no"].strip()
        nationality = request.form["nationality"].strip()
        team_id     = request.form.get("team_id") or None

        try:
            cur.execute("""
                UPDATE PLAYERS
                SET    PLAYER_NAME=:1, TEAM_ID=:2, ROLE=:3,
                       JERSEY_NO=:4, NATIONALITY=:5
                WHERE  PLAYER_ID=:6
            """, (pname, int(team_id) if team_id else None, role,
                  int(jersey), nationality, player_id))
            conn.commit()
            cur.close(); conn.close()
            flash("Player updated successfully!", "success")
            return redirect(url_for("players_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    cur.execute("SELECT * FROM PLAYERS WHERE PLAYER_ID = :1", (player_id,))
    player = fetch_one(cur)
    cur.close()
    conn.close()

    if not player:
        flash("Player not found.", "danger")
        return redirect(url_for("players_list"))

    return render_template("players/form.html", player=player, teams=teams, action="Edit")


@app.route("/players/delete/<int:player_id>", methods=["POST"])
def players_delete(player_id):
    """DELETE FROM PLAYERS — remove a player (cascades stats)."""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("SELECT PLAYER_NAME FROM PLAYERS WHERE PLAYER_ID = :1", (player_id,))
        row  = cur.fetchone()
        name = row[0] if row else f"ID {player_id}"

        # Delete stats first (child rows), then player
        cur.execute("DELETE FROM PLAYER_STATISTICS WHERE PLAYER_ID = :1", (player_id,))
        cur.execute("DELETE FROM PLAYERS WHERE PLAYER_ID = :1", (player_id,))
        conn.commit()
        cur.close(); conn.close()
        flash(f'Player "{name}" deleted successfully!', "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")

    return redirect(url_for("players_list"))


# ==============================================================
#  MATCHES — CRUD
# ==============================================================

@app.route("/matches/")
def matches_list():
    """SELECT + JOIN (3 JOINs to TEAMS) — list all matches."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT m.MATCH_ID,
               t1.TEAM_NAME                         AS team1_name,
               t2.TEAM_NAME                         AS team2_name,
               w.TEAM_NAME                          AS winner_name,
               TO_CHAR(m.MATCH_DATE,'DD-Mon-YYYY')  AS match_date,
               m.VENUE,
               m.MATCH_TYPE
        FROM   MATCHES m
        JOIN   TEAMS t1 ON m.TEAM1_ID  = t1.TEAM_ID
        JOIN   TEAMS t2 ON m.TEAM2_ID  = t2.TEAM_ID
        LEFT JOIN TEAMS w ON m.WINNER_ID = w.TEAM_ID
        ORDER BY m.MATCH_DATE DESC
    """)
    matches = fetch_all(cur)
    cur.close()
    conn.close()
    return render_template("matches/list.html", matches=matches)


@app.route("/matches/add", methods=["GET", "POST"])
def matches_add():
    """INSERT INTO MATCHES — record a new match."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT TEAM_ID, TEAM_NAME FROM TEAMS ORDER BY TEAM_NAME")
    teams = fetch_all(cur)

    if request.method == "POST":
        team1_id   = request.form["team1_id"]
        team2_id   = request.form["team2_id"]
        winner_id  = request.form.get("winner_id") or None
        match_date = request.form["match_date"]
        venue      = request.form["venue"].strip()
        match_type = request.form["match_type"]

        if team1_id == team2_id:
            flash("Team 1 and Team 2 cannot be the same!", "danger")
            cur.close(); conn.close()
            return render_template("matches/form.html", match=None, teams=teams, action="Add")

        try:
            cur.execute("""
                INSERT INTO MATCHES
                       (TEAM1_ID, TEAM2_ID, WINNER_ID, MATCH_DATE, VENUE, MATCH_TYPE)
                VALUES (:1, :2, :3, TO_DATE(:4,'YYYY-MM-DD'), :5, :6)
            """, (int(team1_id), int(team2_id),
                  int(winner_id) if winner_id else None,
                  match_date, venue, match_type))
            conn.commit()
            flash("Match added successfully!", "success")
            cur.close(); conn.close()
            return redirect(url_for("matches_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    cur.close()
    conn.close()
    return render_template("matches/form.html", match=None, teams=teams, action="Add")


@app.route("/matches/edit/<int:match_id>", methods=["GET", "POST"])
def matches_edit(match_id):
    """SELECT + UPDATE — edit match details."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT TEAM_ID, TEAM_NAME FROM TEAMS ORDER BY TEAM_NAME")
    teams = fetch_all(cur)

    if request.method == "POST":
        team1_id   = request.form["team1_id"]
        team2_id   = request.form["team2_id"]
        winner_id  = request.form.get("winner_id") or None
        match_date = request.form["match_date"]
        venue      = request.form["venue"].strip()
        match_type = request.form["match_type"]

        if team1_id == team2_id:
            flash("Team 1 and Team 2 cannot be the same!", "danger")
        else:
            try:
                cur.execute("""
                    UPDATE MATCHES
                    SET    TEAM1_ID=:1, TEAM2_ID=:2, WINNER_ID=:3,
                           MATCH_DATE=TO_DATE(:4,'YYYY-MM-DD'), VENUE=:5, MATCH_TYPE=:6
                    WHERE  MATCH_ID=:7
                """, (int(team1_id), int(team2_id),
                      int(winner_id) if winner_id else None,
                      match_date, venue, match_type, match_id))
                conn.commit()
                cur.close(); conn.close()
                flash("Match updated successfully!", "success")
                return redirect(url_for("matches_list"))
            except Exception as e:
                flash(f"Error: {e}", "danger")

    # SELECT with date formatted for HTML date input (YYYY-MM-DD)
    cur.execute("""
        SELECT MATCH_ID, TEAM1_ID, TEAM2_ID, WINNER_ID,
               TO_CHAR(MATCH_DATE,'YYYY-MM-DD') AS MATCH_DATE,
               VENUE, MATCH_TYPE
        FROM   MATCHES
        WHERE  MATCH_ID = :1
    """, (match_id,))
    match = fetch_one(cur)
    cur.close()
    conn.close()

    if not match:
        flash("Match not found.", "danger")
        return redirect(url_for("matches_list"))

    return render_template("matches/form.html", match=match, teams=teams, action="Edit")


@app.route("/matches/delete/<int:match_id>", methods=["POST"])
def matches_delete(match_id):
    """DELETE — remove match and its statistics."""
    try:
        conn = get_connection()
        cur  = conn.cursor()
        # Delete child rows first to maintain referential integrity
        cur.execute("DELETE FROM PLAYER_STATISTICS WHERE MATCH_ID = :1", (match_id,))
        cur.execute("DELETE FROM MATCHES WHERE MATCH_ID = :1", (match_id,))
        conn.commit()
        cur.close(); conn.close()
        flash("Match and its statistics deleted successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")

    return redirect(url_for("matches_list"))


# ==============================================================
#  STATISTICS — INSERT + AGGREGATED VIEW
# ==============================================================

@app.route("/statistics/")
def statistics_index():
    """
    SELECT with GROUP BY, SUM(), MAX(), COUNT(), LEFT JOIN
    — aggregated player performance across all matches.
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.PLAYER_ID,
               p.PLAYER_NAME,
               t.TEAM_NAME,
               p.ROLE,
               COUNT(ps.MATCH_ID)   AS matches_played,
               NVL(SUM(ps.RUNS), 0)     AS total_runs,
               NVL(SUM(ps.WICKETS), 0)  AS total_wickets,
               NVL(SUM(ps.CATCHES), 0)  AS total_catches,
               NVL(MAX(ps.RUNS), 0)     AS highest_score
        FROM   PLAYERS p
        LEFT JOIN TEAMS t            ON p.TEAM_ID = t.TEAM_ID
        LEFT JOIN PLAYER_STATISTICS ps ON p.PLAYER_ID = ps.PLAYER_ID
        GROUP BY p.PLAYER_ID, p.PLAYER_NAME, t.TEAM_NAME, p.ROLE
        ORDER BY total_runs DESC NULLS LAST, p.PLAYER_NAME
    """)
    stats = fetch_all(cur)
    cur.close()
    conn.close()
    return render_template("statistics/index.html", stats=stats)


@app.route("/statistics/add", methods=["GET", "POST"])
def statistics_add():
    """INSERT INTO PLAYER_STATISTICS — log player performance for a match."""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT PLAYER_ID, PLAYER_NAME FROM PLAYERS ORDER BY PLAYER_NAME")
    players = fetch_all(cur)

    cur.execute("""
        SELECT m.MATCH_ID,
               t1.TEAM_NAME || ' vs ' || t2.TEAM_NAME ||
               ' (' || TO_CHAR(m.MATCH_DATE,'DD-Mon-YYYY') || ')' AS match_label
        FROM   MATCHES m
        JOIN   TEAMS t1 ON m.TEAM1_ID = t1.TEAM_ID
        JOIN   TEAMS t2 ON m.TEAM2_ID = t2.TEAM_ID
        ORDER BY m.MATCH_DATE DESC
    """)
    matches = fetch_all(cur)

    if request.method == "POST":
        player_id        = request.form["player_id"]
        match_id         = request.form["match_id"]
        runs             = request.form.get("runs", 0)
        wickets          = request.form.get("wickets", 0)
        catches          = request.form.get("catches", 0)
        is_highest_score = "Y" if request.form.get("is_highest_score") else "N"

        try:
            cur.execute("""
                INSERT INTO PLAYER_STATISTICS
                       (PLAYER_ID, MATCH_ID, RUNS, WICKETS, CATCHES, IS_HIGHEST_SCORE)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (int(player_id), int(match_id),
                  int(runs), int(wickets), int(catches), is_highest_score))
            conn.commit()
            flash("Statistics saved successfully!", "success")
            cur.close(); conn.close()
            return redirect(url_for("statistics_index"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    cur.close()
    conn.close()
    return render_template("statistics/form.html", players=players, matches=matches)


# ==============================================================
#  ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True)

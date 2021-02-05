import sqlite3 as sq


db_core = "M:\\Programs\\workspace\\projects\\mbet_bs4_sqlite3\\db.sqlite3"


def save_to_db(collections):
    with sq.connect(db_core) as con:
        cur = con.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                date TEXT,
                result_1 REAL,
                draw_X REAL,
                result_2 REAL,
                double_chance_1X REAL,
                double_chance_12 REAL,
                double_chance_X2 REAL,
                total_under REAL,
                total_over REAL
            )
            """
        )

        cur.executemany("INSERT INTO matches VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", collections)


def select_all():
    with sq.connect(db_core) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM matches")
        for line in cur: print(line)

def delete_all():
    with sq.connect(db_core) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM matches")

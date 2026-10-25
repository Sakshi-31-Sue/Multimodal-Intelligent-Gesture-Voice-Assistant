import sqlite3, time
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent / "data" / "assistant.db"
DB_PATH.parent.mkdir(exist_ok=True)
class Database:
    def __init__(self):
        self.conn=sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, ts REAL, source TEXT, command TEXT, confidence REAL, result TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS calibration(username TEXT PRIMARY KEY, pinch REAL NOT NULL, sensitivity REAL NOT NULL, updated REAL NOT NULL)")
        self.conn.commit()
    def log(self, source, command, confidence, result):
        with self.conn: self.conn.execute("INSERT INTO history(ts,source,command,confidence,result) VALUES(?,?,?,?,?)", (time.time(),source,command,float(confidence),str(result)))
    def save_calibration(self, pinch, sensitivity, username="default"):
        with self.conn: self.conn.execute("INSERT INTO calibration VALUES(?,?,?,?) ON CONFLICT(username) DO UPDATE SET pinch=excluded.pinch,sensitivity=excluded.sensitivity,updated=excluded.updated", (username,float(pinch),float(sensitivity),time.time()))
    def calibration(self, username="default"):
        row=self.conn.execute("SELECT pinch,sensitivity FROM calibration WHERE username=?",(username,)).fetchone()
        return {"pinch":row[0],"sensitivity":row[1]} if row else {"pinch":0.045,"sensitivity":1.0}
    def recent(self, limit=25): return self.conn.execute("SELECT ts,source,command,confidence,result FROM history ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    def close(self): self.conn.close()

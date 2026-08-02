import sqlite3
import json
from contextlib import contextmanager
from typing import Dict, List, Optional


class HistoryManager:
    """Persists code review submissions (source code, findings, remediations, PR summary)
    to a local SQLite database so users can browse and revisit past reviews."""

    def __init__(self, db_path: str = "submission_history.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    submission_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    language TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    code TEXT NOT NULL,
                    total_issues INTEGER NOT NULL,
                    quality_count INTEGER NOT NULL,
                    security_count INTEGER NOT NULL,
                    results_json TEXT NOT NULL
                )
            """)

    def save_submission(self, submission_id: str, project_name: str, language: str,
                         code: str, results: Dict) -> None:
        """Stores one full review run. Overwrites any prior entry with the same submission_id."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO submissions
                    (submission_id, project_name, language, created_at, code,
                     total_issues, quality_count, security_count, results_json)
                VALUES (?, ?, ?, datetime('now', 'localtime'), ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    project_name or "Untitled Project",
                    language,
                    code,
                    results.get("total_issues", 0),
                    results.get("quality_count", 0),
                    results.get("security_count", 0),
                    json.dumps(results),
                ),
            )

    def list_submissions(self) -> List[Dict]:
        """Lightweight summaries (no code / full findings) for the history list, newest first."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT submission_id, project_name, language, created_at,
                       total_issues, quality_count, security_count
                FROM submissions
                ORDER BY created_at DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def get_submission(self, submission_id: str) -> Optional[Dict]:
        """Full record including original code and parsed results dict, or None if not found."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM submissions WHERE submission_id = ?",
                (submission_id,),
            ).fetchone()
            if not row:
                return None
            record = dict(row)
            record["results"] = json.loads(record.pop("results_json"))
            return record

    def delete_submission(self, submission_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM submissions WHERE submission_id = ?", (submission_id,))

"""
Database module for Study Dashboard - SQLite local storage
"""
import sqlite3
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import threading


@dataclass
class Subject:
    id: str
    name: str
    color: str
    weekly_target_minutes: int = 0
    created_at: str = ""
    notes: str = ""
    note_file_path: str = ""
    note_file_name: str = ""
    note_file_type: str = ""


@dataclass
class StudySession:
    id: str
    subject_id: str
    subject_name: str
    subject_color: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: int
    status: str  # ACTIVE, PAUSED, COMPLETED, INTERRUPTED
    created_at: str
    notes: str = ""
    note_file_path: str = ""
    note_file_name: str = ""
    note_file_type: str = ""


@dataclass
class StudyGoal:
    id: str
    daily_target_minutes: int
    weekly_target_minutes: int
    updated_at: str = ""


class StudyDatabase:
    def __init__(self, db_path: str = "study_data.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Subjects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#4338ca',
                    weekly_target_minutes INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    note_file_path TEXT DEFAULT '',
                    note_file_name TEXT DEFAULT '',
                    note_file_type TEXT DEFAULT ''
                )
            """)

            # Study sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    subject_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'INTERRUPTED')),
                    created_at TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    note_file_path TEXT DEFAULT '',
                    note_file_name TEXT DEFAULT '',
                    note_file_type TEXT DEFAULT '',
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT
                )
            """)

            # Study goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_goals (
                    id TEXT PRIMARY KEY,
                    daily_target_minutes INTEGER NOT NULL DEFAULT 120,
                    weekly_target_minutes INTEGER NOT NULL DEFAULT 600,
                    updated_at TEXT NOT NULL
                )
            """)

            # Insert default subjects if empty
            cursor.execute("SELECT COUNT(*) FROM subjects")
            if cursor.fetchone()[0] == 0:
                default_subjects = [
                    ("Mathematics", "#2a78d6"),
                    ("Physics", "#eb6834"),
                    ("Chemistry", "#1baf7a"),
                    ("Biology", "#eda100"),
                    ("Computer Science", "#e87ba4"),
                    ("English", "#008300"),
                ]
                now = datetime.now().isoformat()
                for name, color in default_subjects:
                    cursor.execute(
                        "INSERT INTO subjects (id, name, color, weekly_target_minutes, created_at, notes, note_file_path, note_file_name, note_file_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (str(uuid.uuid4()), name, color, 0, now, "", "", "", "")
                    )

            # Insert default goals if empty
            cursor.execute("SELECT COUNT(*) FROM study_goals")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO study_goals (id, daily_target_minutes, weekly_target_minutes, updated_at) VALUES (?, ?, ?, ?)",
                    (str(uuid.uuid4()), 120, 600, datetime.now().isoformat())
                )

            conn.commit()

    # ==================== Subject Methods ====================

    def get_all_subjects(self) -> List[Subject]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subjects ORDER BY name")
            rows = cursor.fetchall()
            subjects = []
            for row in rows:
                d = dict(row)
                # Set defaults for new fields if not present
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                subjects.append(Subject(**d))
            return subjects

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                return Subject(**d)
            return None

    def add_subject(self, name: str, color: str = "#4338ca", weekly_target: int = 0, notes: str = "", note_file_path: str = "", note_file_name: str = "", note_file_type: str = "") -> Subject:
        subject_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO subjects (id, name, color, weekly_target_minutes, created_at, notes, note_file_path, note_file_name, note_file_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (subject_id, name, color, weekly_target, now, notes, note_file_path, note_file_name, note_file_type)
            )
            conn.commit()
        return Subject(id=subject_id, name=name, color=color, weekly_target_minutes=weekly_target, created_at=now, notes=notes, note_file_path=note_file_path, note_file_name=note_file_name, note_file_type=note_file_type)

    def update_subject_target(self, subject_id: str, weekly_target_minutes: int):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subjects SET weekly_target_minutes = ? WHERE id = ?",
                (weekly_target_minutes, subject_id)
            )
            conn.commit()

    def update_subject_notes(self, subject_id: str, notes: str, note_file_path: str = "", note_file_name: str = "", note_file_type: str = ""):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subjects SET notes = ?, note_file_path = ?, note_file_name = ?, note_file_type = ? WHERE id = ?",
                (notes, note_file_path, note_file_name, note_file_type, subject_id)
            )
            conn.commit()

    def delete_subject(self, subject_id: str):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            conn.commit()

    # ==================== Session Methods ====================

    def create_session(self, subject_id: str, notes: str = "", note_file_path: str = "", note_file_name: str = "", note_file_type: str = "") -> StudySession:
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, color FROM subjects WHERE id = ?", (subject_id,))
            subject = cursor.fetchone()
            if not subject:
                raise ValueError("Subject not found")

            cursor.execute(
                """INSERT INTO study_sessions (id, subject_id, start_time, duration_seconds, status, created_at, notes, note_file_path, note_file_name, note_file_type)
                   VALUES (?, ?, ?, 0, 'ACTIVE', ?, ?, ?, ?, ?)""",
                (session_id, subject_id, now, now, notes, note_file_path, note_file_name, note_file_type)
            )
            conn.commit()

        return StudySession(
            id=session_id,
            subject_id=subject_id,
            subject_name=subject["name"],
            subject_color=subject["color"],
            start_time=now,
            end_time=None,
            duration_seconds=0,
            status="ACTIVE",
            created_at=now,
            notes=notes,
            note_file_path=note_file_path,
            note_file_name=note_file_name,
            note_file_type=note_file_type
        )

    def get_active_session(self) -> Optional[StudySession]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.status = 'ACTIVE'
                ORDER BY s.start_time DESC LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                return StudySession(**d)
            return None

    def get_paused_session(self) -> Optional[StudySession]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.status = 'PAUSED'
                ORDER BY s.start_time DESC LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                return StudySession(**d)
            return None

    def update_session_status(self, session_id: str, status: str, duration_seconds: int = None):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if duration_seconds is not None:
                cursor.execute(
                    "UPDATE study_sessions SET status = ?, duration_seconds = ? WHERE id = ?",
                    (status, duration_seconds, session_id)
                )
            else:
                cursor.execute(
                    "UPDATE study_sessions SET status = ? WHERE id = ?",
                    (status, session_id)
                )
            conn.commit()

    def complete_session(self, session_id: str, duration_seconds: int, notes: str = "", note_file_path: str = "", note_file_name: str = "", note_file_type: str = ""):
        end_time = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE study_sessions SET status = 'COMPLETED', end_time = ?, duration_seconds = ?, notes = ?, note_file_path = ?, note_file_name = ?, note_file_type = ? WHERE id = ?",
                (end_time, duration_seconds, notes, note_file_path, note_file_name, note_file_type, session_id)
            )
            conn.commit()

    def get_sessions_for_date(self, target_date: date) -> List[StudySession]:
        start_of_day = datetime.combine(target_date, datetime.min.time()).isoformat()
        end_of_day = datetime.combine(target_date, datetime.max.time()).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.start_time >= ? AND s.start_time <= ? AND s.status = 'COMPLETED'
                ORDER BY s.start_time DESC
            """, (start_of_day, end_of_day))
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                sessions.append(StudySession(**d))
            return sessions

    def get_sessions_for_week(self, week_start: date) -> List[StudySession]:
        week_end = week_start + timedelta(days=6)
        start_of_week = datetime.combine(week_start, datetime.min.time()).isoformat()
        end_of_week = datetime.combine(week_end, datetime.max.time()).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.start_time >= ? AND s.start_time <= ? AND s.status = 'COMPLETED'
                ORDER BY s.start_time DESC
            """, (start_of_week, end_of_week))
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                sessions.append(StudySession(**d))
            return sessions

    def get_sessions_for_month(self, year: int, month: int) -> List[StudySession]:
        start_of_month = datetime(year, month, 1).isoformat()
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1).isoformat()
        else:
            end_of_month = datetime(year, month + 1, 1).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.start_time >= ? AND s.start_time < ? AND s.status = 'COMPLETED'
                ORDER BY s.start_time DESC
            """, (start_of_month, end_of_month))
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                sessions.append(StudySession(**d))
            return sessions

    def get_all_completed_sessions(self) -> List[StudySession]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.status = 'COMPLETED'
                ORDER BY s.start_time DESC
            """)
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                sessions.append(StudySession(**d))
            return sessions

    def get_recent_sessions(self, limit: int = 10) -> List[StudySession]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, sub.name as subject_name, sub.color as subject_color
                FROM study_sessions s
                JOIN subjects sub ON s.subject_id = sub.id
                WHERE s.status = 'COMPLETED'
                ORDER BY s.start_time DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                d = dict(row)
                d.setdefault('notes', '')
                d.setdefault('note_file_path', '')
                d.setdefault('note_file_name', '')
                d.setdefault('note_file_type', '')
                sessions.append(StudySession(**d))
            return sessions

    # ==================== Goal Methods ====================

    def get_goals(self) -> StudyGoal:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM study_goals LIMIT 1")
            row = cursor.fetchone()
            if row:
                return StudyGoal(**dict(row))
            return StudyGoal(id=str(uuid.uuid4()), daily_target_minutes=120, weekly_target_minutes=600)

    def update_goals(self, daily_target_minutes: int, weekly_target_minutes: int):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE study_goals SET daily_target_minutes = ?, weekly_target_minutes = ?, updated_at = ?
            """, (daily_target_minutes, weekly_target_minutes, datetime.now().isoformat()))
            conn.commit()

    # ==================== Analytics Methods ====================

    def get_daily_stats(self, target_date: date) -> Dict:
        sessions = self.get_sessions_for_date(target_date)
        total_seconds = sum(s.duration_seconds for s in sessions)
        by_subject = {}
        for s in sessions:
            if s.subject_name not in by_subject:
                by_subject[s.subject_name] = {"seconds": 0, "color": s.subject_color}
            by_subject[s.subject_name]["seconds"] += s.duration_seconds
        return {
            "total_minutes": total_seconds // 60,
            "total_seconds": total_seconds,
            "session_count": len(sessions),
            "by_subject": by_subject
        }

    def get_weekly_stats(self, week_start: date) -> Dict:
        sessions = self.get_sessions_for_week(week_start)
        total_seconds = sum(s.duration_seconds for s in sessions)
        by_subject = {}
        by_day = {}
        for s in sessions:
            if s.subject_name not in by_subject:
                by_subject[s.subject_name] = {"seconds": 0, "color": s.subject_color}
            by_subject[s.subject_name]["seconds"] += s.duration_seconds

            day_key = datetime.fromisoformat(s.start_time).date().isoformat()
            if day_key not in by_day:
                by_day[day_key] = 0
            by_day[day_key] += s.duration_seconds

        return {
            "total_minutes": total_seconds // 60,
            "total_seconds": total_seconds,
            "session_count": len(sessions),
            "by_subject": by_subject,
            "by_day": by_day
        }

    def get_monthly_stats(self, year: int, month: int) -> Dict:
        sessions = self.get_sessions_for_month(year, month)
        total_seconds = sum(s.duration_seconds for s in sessions)
        by_subject = {}
        by_week = {}
        for s in sessions:
            if s.subject_name not in by_subject:
                by_subject[s.subject_name] = {"seconds": 0, "color": s.subject_color}
            by_subject[s.subject_name]["seconds"] += s.duration_seconds

            dt = datetime.fromisoformat(s.start_time)
            week_start = dt - timedelta(days=dt.weekday())
            week_key = week_start.date().isoformat()
            if week_key not in by_week:
                by_week[week_key] = 0
            by_week[week_key] += s.duration_seconds

        return {
            "total_minutes": total_seconds // 60,
            "total_seconds": total_seconds,
            "session_count": len(sessions),
            "by_subject": by_subject,
            "by_week": by_week
        }

    def get_streak_days(self) -> int:
        """Calculate current study streak in days"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT date(start_time) as study_date
                FROM study_sessions
                WHERE status = 'COMPLETED'
                ORDER BY study_date DESC
            """)
            dates = [datetime.fromisoformat(row[0]).date() for row in cursor.fetchall()]

        if not dates:
            return 0

        streak = 0
        today = date.today()
        expected_date = today

        for study_date in dates:
            if study_date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif study_date < expected_date:
                break

        return streak

    def get_subject_weekly_progress(self, subject_id: str, week_start: date) -> Tuple[int, int]:
        """Returns (actual_minutes, target_minutes) for a subject this week"""
        sessions = self.get_sessions_for_week(week_start)
        subject_sessions = [s for s in sessions if s.subject_id == subject_id]
        actual_minutes = sum(s.duration_seconds for s in subject_sessions) // 60

        subject = self.get_subject(subject_id)
        target_minutes = subject.weekly_target_minutes if subject else 0

        return actual_minutes, target_minutes
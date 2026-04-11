from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path


class SQLiteMemoryStore:
    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def add_turn(self, role: str, content: str) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                "INSERT INTO conversation_turns (role, content) VALUES (?, ?)",
                (role, content),
            )
            connection.commit()

    def get_recent_turns(self, limit: int = 10) -> list[tuple[str, str]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM conversation_turns
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        rows.reverse()
        return [(str(role), str(content)) for role, content in rows]

    def get_last_user_message(self) -> str | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT content
                FROM conversation_turns
                WHERE role = 'user'
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
        return None if row is None else str(row[0])

    def clear(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute("DELETE FROM conversation_turns")
            connection.commit()

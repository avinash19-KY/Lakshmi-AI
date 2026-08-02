from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
from uuid import uuid4

from src.models.asset import Asset
from src.models.financial_goal import FinancialGoal
from src.models.financial_profile import FinancialProfile
from src.models.investment import Investment
from src.models.liability import Liability
from src.repositories.base import Repository


class DatabaseError(Exception):
    pass


class SQLiteDB:
    """Simple SQLite helper for creating connections and initializing schema."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        try:
            conn = sqlite3.connect(str(self.path))
            conn.row_factory = sqlite3.Row
            # enable foreign keys if needed in future
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(str(exc)) from exc
        finally:
            try:
                conn.close()  # type: ignore
            except Exception:
                pass

    def initialize(self) -> None:
        """Create tables if they do not exist. Idempotent."""
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    monthly_income REAL NOT NULL,
                    monthly_expenses REAL NOT NULL,
                    monthly_essential_expenses REAL NOT NULL,
                    emergency_fund REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS liabilities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS investments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )


class SQLiteRepositoryBase(Repository):
    """Base for SQLite repositories implementing common helpers."""

    def __init__(self, db: SQLiteDB) -> None:
        self._db = db
        # ensure database initialized
        self._db.initialize()

    def _new_id(self) -> str:
        return str(uuid4())


class AssetSQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: Asset) -> str:
        item_id = self._new_id()
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO assets (id, name, category, value) VALUES (?, ?, ?, ?)",
                (item_id, item.name, item.category, float(item.value)),
            )
        return item_id

    def add_many(self, items: list[Asset]) -> list[str]:
        ids: list[str] = []
        with self._db.connect() as conn:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO assets (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
                ids.append(item_id)
        return ids

    def get_all(self) -> list[Asset]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM assets")
            rows = cur.fetchall()
            return [Asset(row["name"], row["category"], float(row["value"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[Asset]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM assets WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Asset(row["name"], row["category"], float(row["value"]))

    def update(self, item_id: str, item: Asset) -> None:
        with self._db.connect() as conn:
            cur = conn.execute(
                "UPDATE assets SET name = ?, category = ?, value = ? WHERE id = ?",
                (item.name, item.category, float(item.value), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str) -> None:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM assets WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM assets")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM assets")
            return int(cur.fetchone()["c"])


class LiabilitySQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: Liability) -> str:
        item_id = self._new_id()
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO liabilities (id, name, category, value) VALUES (?, ?, ?, ?)",
                (item_id, item.name, item.category, float(item.value)),
            )
        return item_id

    def add_many(self, items: list[Liability]) -> list[str]:
        ids: list[str] = []
        with self._db.connect() as conn:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO liabilities (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
                ids.append(item_id)
        return ids

    def get_all(self) -> list[Liability]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM liabilities")
            rows = cur.fetchall()
            return [Liability(row["name"], row["category"], float(row["value"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[Liability]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM liabilities WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Liability(row["name"], row["category"], float(row["value"]))

    def update(self, item_id: str, item: Liability) -> None:
        with self._db.connect() as conn:
            cur = conn.execute(
                "UPDATE liabilities SET name = ?, category = ?, value = ? WHERE id = ?",
                (item.name, item.category, float(item.value), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str) -> None:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM liabilities WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM liabilities")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM liabilities")
            return int(cur.fetchone()["c"])


class InvestmentSQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: Investment) -> str:
        item_id = self._new_id()
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO investments (id, name, category, value) VALUES (?, ?, ?, ?)",
                (item_id, item.name, item.category, float(item.value)),
            )
        return item_id

    def add_many(self, items: list[Investment]) -> list[str]:
        ids: list[str] = []
        with self._db.connect() as conn:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO investments (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
                ids.append(item_id)
        return ids

    def get_all(self) -> list[Investment]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM investments")
            rows = cur.fetchall()
            return [Investment(row["name"], row["category"], float(row["value"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[Investment]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM investments WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Investment(row["name"], row["category"], float(row["value"]))

    def update(self, item_id: str, item: Investment) -> None:
        with self._db.connect() as conn:
            cur = conn.execute(
                "UPDATE investments SET name = ?, category = ?, value = ? WHERE id = ?",
                (item.name, item.category, float(item.value), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str) -> None:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM investments WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM investments")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM investments")
            return int(cur.fetchone()["c"])


class GoalSQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: FinancialGoal) -> str:
        item_id = self._new_id()
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO goals (id, name, target_amount, current_amount) VALUES (?, ?, ?, ?)",
                (item_id, item.name, float(item.target_amount), float(item.current_amount)),
            )
        return item_id

    def add_many(self, items: list[FinancialGoal]) -> list[str]:
        ids: list[str] = []
        with self._db.connect() as conn:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO goals (id, name, target_amount, current_amount) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, float(item.target_amount), float(item.current_amount)),
                )
                ids.append(item_id)
        return ids

    def get_all(self) -> list[FinancialGoal]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, target_amount, current_amount FROM goals")
            rows = cur.fetchall()
            return [FinancialGoal(row["name"], float(row["target_amount"]), float(row["current_amount"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[FinancialGoal]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, target_amount, current_amount FROM goals WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return FinancialGoal(row["name"], float(row["target_amount"]), float(row["current_amount"]))

    def update(self, item_id: str, item: FinancialGoal) -> None:
        with self._db.connect() as conn:
            cur = conn.execute(
                "UPDATE goals SET name = ?, target_amount = ?, current_amount = ? WHERE id = ?",
                (item.name, float(item.target_amount), float(item.current_amount), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str) -> None:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM goals WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM goals")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM goals")
            return int(cur.fetchone()["c"])


class FinancialProfileSQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: FinancialProfile) -> str:
        # treat profiles as a single-row table; upsert by clearing and inserting
        with self._db.connect() as conn:
            conn.execute("DELETE FROM profiles")
            item_id = self._new_id()
            conn.execute(
                "INSERT INTO profiles (id, name, monthly_income, monthly_expenses, monthly_essential_expenses, emergency_fund) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item_id,
                    item.name,
                    float(item.monthly_income),
                    float(item.monthly_expenses),
                    float(item.monthly_essential_expenses),
                    float(item.emergency_fund),
                ),
            )
        return item_id

    def add_many(self, items: list[FinancialProfile]) -> list[str]:
        ids: list[str] = []
        for item in items:
            ids.append(self.add(item))
        return ids

    def get_all(self) -> list[FinancialProfile]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, monthly_income, monthly_expenses, monthly_essential_expenses, emergency_fund FROM profiles LIMIT 1")
            row = cur.fetchone()
            if not row:
                return []
            return [
                FinancialProfile(
                    name=row["name"],
                    monthly_income=float(row["monthly_income"]),
                    monthly_expenses=float(row["monthly_expenses"]),
                    monthly_essential_expenses=float(row["monthly_essential_expenses"]),
                    emergency_fund=float(row["emergency_fund"]),
                )
            ]

    def get_by_id(self, item_id: str) -> Optional[FinancialProfile]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, monthly_income, monthly_expenses, monthly_essential_expenses, emergency_fund FROM profiles WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return FinancialProfile(
                name=row["name"],
                monthly_income=float(row["monthly_income"]),
                monthly_expenses=float(row["monthly_expenses"]),
                monthly_essential_expenses=float(row["monthly_essential_expenses"]),
                emergency_fund=float(row["emergency_fund"]),
            )

    def update(self, item_id: str, item: FinancialProfile) -> None:
        with self._db.connect() as conn:
            cur = conn.execute(
                "UPDATE profiles SET name = ?, monthly_income = ?, monthly_expenses = ?, monthly_essential_expenses = ?, emergency_fund = ? WHERE id = ?",
                (
                    item.name,
                    float(item.monthly_income),
                    float(item.monthly_expenses),
                    float(item.monthly_essential_expenses),
                    float(item.emergency_fund),
                    item_id,
                ),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str) -> None:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM profiles WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM profiles")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM profiles")
            return int(cur.fetchone()["c"])

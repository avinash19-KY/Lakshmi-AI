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

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Provide a transactional connection -- commits on success, rolls back on failure.

        Usage:
            with db.transaction() as conn:
                conn.execute(...)
                repo.add(item, conn=conn)
        """
        try:
            conn = sqlite3.connect(str(self.path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            try:
                conn.rollback()
            except Exception:
                pass
            raise DatabaseError(str(exc)) from exc
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                conn.close()
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

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS connector_mappings (
                    connector_name TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    domain_id TEXT NOT NULL,
                    last_synced_at TEXT,
                    PRIMARY KEY (connector_name, external_id)
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
    def add(self, item: Asset, conn: sqlite3.Connection | None = None) -> str:
        item_id = self._new_id()
        if conn is not None:
            conn.execute(
                "INSERT INTO assets (id, name, category, value) VALUES (?, ?, ?, ?)",
                (item_id, item.name, item.category, float(item.value)),
            )
        else:
            with self._db.connect() as conn0:
                conn0.execute(
                    "INSERT INTO assets (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
        return item_id

    def add_many(self, items: list[Asset], conn: sqlite3.Connection | None = None) -> list[str]:
        ids: list[str] = []
        if conn is not None:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO assets (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
                ids.append(item_id)
        else:
            with self._db.connect() as conn0:
                for item in items:
                    item_id = self._new_id()
                    conn0.execute(
                        "INSERT INTO assets (id, name, category, value) VALUES (?, ?, ?, ?)",
                        (item_id, item.name, item.category, float(item.value)),
                    )
                    ids.append(item_id)
        return ids

    def get_all(self) -> list[Asset]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT id, name, category, value FROM assets")
            rows = cur.fetchall()
            return [Asset(row["name"], row["category"], float(row["value"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[Asset]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM assets WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Asset(row["name"], row["category"], float(row["value"]))

    def update(self, item_id: str, item: Asset, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute(
                "UPDATE assets SET name = ?, category = ?, value = ? WHERE id = ?",
                (item.name, item.category, float(item.value), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute(
                    "UPDATE assets SET name = ?, category = ?, value = ? WHERE id = ?",
                    (item.name, item.category, float(item.value), item_id),
                )
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute("DELETE FROM assets WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute("DELETE FROM assets WHERE id = ?", (item_id,))
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            conn.execute("DELETE FROM assets")
        else:
            with self._db.connect() as conn0:
                conn0.execute("DELETE FROM assets")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM assets")
            return int(cur.fetchone()["c"])

class LiabilitySQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: Liability, conn: sqlite3.Connection | None = None) -> str:
        item_id = self._new_id()
        if conn is not None:
            conn.execute(
                "INSERT INTO liabilities (id, name, category, value) VALUES (?, ?, ?, ?)",
                (item_id, item.name, item.category, float(item.value)),
            )
        else:
            with self._db.connect() as conn0:
                conn0.execute(
                    "INSERT INTO liabilities (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
        return item_id

    def add_many(self, items: list[Liability], conn: sqlite3.Connection | None = None) -> list[str]:
        ids: list[str] = []
        if conn is not None:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO liabilities (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
                ids.append(item_id)
        else:
            with self._db.connect() as conn0:
                for item in items:
                    item_id = self._new_id()
                    conn0.execute(
                        "INSERT INTO liabilities (id, name, category, value) VALUES (?, ?, ?, ?)",
                        (item_id, item.name, item.category, float(item.value)),
                    )
                    ids.append(item_id)
        return ids

    def get_all(self) -> list[Liability]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT id, name, category, value FROM liabilities")
            rows = cur.fetchall()
            return [Liability(row["name"], row["category"], float(row["value"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[Liability]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM liabilities WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Liability(row["name"], row["category"], float(row["value"]))

    def update(self, item_id: str, item: Liability, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute(
                "UPDATE liabilities SET name = ?, category = ?, value = ? WHERE id = ?",
                (item.name, item.category, float(item.value), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute(
                    "UPDATE liabilities SET name = ?, category = ?, value = ? WHERE id = ?",
                    (item.name, item.category, float(item.value), item_id),
                )
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute("DELETE FROM liabilities WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute("DELETE FROM liabilities WHERE id = ?", (item_id,))
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            conn.execute("DELETE FROM liabilities")
        else:
            with self._db.connect() as conn0:
                conn0.execute("DELETE FROM liabilities")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM liabilities")
            return int(cur.fetchone()["c"])


class InvestmentSQLiteRepository(SQLiteRepositoryBase):
    def add(self, item: Investment, conn: sqlite3.Connection | None = None) -> str:
        item_id = self._new_id()
        if conn is not None:
            conn.execute(
                "INSERT INTO investments (id, name, category, value) VALUES (?, ?, ?, ?)",
                (item_id, item.name, item.category, float(item.value)),
            )
        else:
            with self._db.connect() as conn0:
                conn0.execute(
                    "INSERT INTO investments (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
        return item_id

    def add_many(self, items: list[Investment], conn: sqlite3.Connection | None = None) -> list[str]:
        ids: list[str] = []
        if conn is not None:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO investments (id, name, category, value) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, item.category, float(item.value)),
                )
                ids.append(item_id)
        else:
            with self._db.connect() as conn0:
                for item in items:
                    item_id = self._new_id()
                    conn0.execute(
                        "INSERT INTO investments (id, name, category, value) VALUES (?, ?, ?, ?)",
                        (item_id, item.name, item.category, float(item.value)),
                    )
                    ids.append(item_id)
        return ids

    def get_all(self) -> list[Investment]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT id, name, category, value FROM investments")
            rows = cur.fetchall()
            return [Investment(row["name"], row["category"], float(row["value"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[Investment]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, category, value FROM investments WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Investment(row["name"], row["category"], float(row["value"]))

    def update(self, item_id: str, item: Investment, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute(
                "UPDATE investments SET name = ?, category = ?, value = ? WHERE id = ?",
                (item.name, item.category, float(item.value), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute(
                    "UPDATE investments SET name = ?, category = ?, value = ? WHERE id = ?",
                    (item.name, item.category, float(item.value), item_id),
                )
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute("DELETE FROM investments WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute("DELETE FROM investments WHERE id = ?", (item_id,))
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
    def add(self, item: FinancialGoal, conn: sqlite3.Connection | None = None) -> str:
        item_id = self._new_id()
        if conn is not None:
            conn.execute(
                "INSERT INTO goals (id, name, target_amount, current_amount) VALUES (?, ?, ?, ?)",
                (item_id, item.name, float(item.target_amount), float(item.current_amount)),
            )
        else:
            with self._db.connect() as conn0:
                conn0.execute(
                    "INSERT INTO goals (id, name, target_amount, current_amount) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, float(item.target_amount), float(item.current_amount)),
                )
        return item_id

    def add_many(self, items: list[FinancialGoal], conn: sqlite3.Connection | None = None) -> list[str]:
        ids: list[str] = []
        if conn is not None:
            for item in items:
                item_id = self._new_id()
                conn.execute(
                    "INSERT INTO goals (id, name, target_amount, current_amount) VALUES (?, ?, ?, ?)",
                    (item_id, item.name, float(item.target_amount), float(item.current_amount)),
                )
                ids.append(item_id)
        else:
            with self._db.connect() as conn0:
                for item in items:
                    item_id = self._new_id()
                    conn0.execute(
                        "INSERT INTO goals (id, name, target_amount, current_amount) VALUES (?, ?, ?, ?)",
                        (item_id, item.name, float(item.target_amount), float(item.current_amount)),
                    )
                    ids.append(item_id)
        return ids

    def get_all(self) -> list[FinancialGoal]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT id, name, target_amount, current_amount FROM goals")
            rows = cur.fetchall()
            return [FinancialGoal(row["name"], float(row["target_amount"]), float(row["current_amount"])) for row in rows]

    def get_by_id(self, item_id: str) -> Optional[FinancialGoal]:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT name, target_amount, current_amount FROM goals WHERE id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                return None
            return FinancialGoal(row["name"], float(row["target_amount"]), float(row["current_amount"]))

    def update(self, item_id: str, item: FinancialGoal, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute(
                "UPDATE goals SET name = ?, target_amount = ?, current_amount = ? WHERE id = ?",
                (item.name, float(item.target_amount), float(item.current_amount), item_id),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute(
                    "UPDATE goals SET name = ?, target_amount = ?, current_amount = ? WHERE id = ?",
                    (item.name, float(item.target_amount), float(item.current_amount), item_id),
                )
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def delete(self, item_id: str, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute("DELETE FROM goals WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute("DELETE FROM goals WHERE id = ?", (item_id,))
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
    def add(self, item: FinancialProfile, conn: sqlite3.Connection | None = None) -> str:
        # treat profiles as a single-row table; upsert by clearing and inserting
        if conn is not None:
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
        else:
            with self._db.connect() as conn0:
                conn0.execute("DELETE FROM profiles")
                item_id = self._new_id()
                conn0.execute(
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

    def add_many(self, items: list[FinancialProfile], conn: sqlite3.Connection | None = None) -> list[str]:
        ids: list[str] = []
        for item in items:
            ids.append(self.add(item, conn=conn))
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

    def update(self, item_id: str, item: FinancialProfile, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
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
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute(
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

    def delete(self, item_id: str, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            cur = conn.execute("DELETE FROM profiles WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise KeyError(f"Item with id '{item_id}' does not exist.")
        else:
            with self._db.connect() as conn0:
                cur = conn0.execute("DELETE FROM profiles WHERE id = ?", (item_id,))
                if cur.rowcount == 0:
                    raise KeyError(f"Item with id '{item_id}' does not exist.")

    def clear(self, conn: sqlite3.Connection | None = None) -> None:
        if conn is not None:
            conn.execute("DELETE FROM profiles")
        else:
            with self._db.connect() as conn0:
                conn0.execute("DELETE FROM profiles")

    def count(self) -> int:
        with self._db.connect() as conn:
            cur = conn.execute("SELECT COUNT(1) as c FROM profiles")
            return int(cur.fetchone()["c"])

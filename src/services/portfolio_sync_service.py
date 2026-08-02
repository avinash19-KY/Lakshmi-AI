from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.connectors.base import ConnectorHolding, PortfolioConnector
from src.models.asset import Asset
from src.models.investment import Investment
from src.repositories.sqlite_repository import SQLiteDB
from src.repositories.base import Repository


@dataclass
class SyncResult:
    connector: str
    status: str
    received: int
    added: int
    updated: int
    removed: int
    unchanged: int
    timestamp: str
    errors: Optional[List[str]] = None


class PortfolioSyncService:
    """Synchronize holdings from a PortfolioConnector into local repositories.

    This service is read-only toward providers and writes only to local repositories.
    It tracks connector ownership via the `connector_mappings` SQLite table.
    """

    def __init__(
        self,
        connector: PortfolioConnector,
        sqlite_db: SQLiteDB,
        asset_repo: Repository[Asset],
        investment_repo: Repository[Investment],
    ) -> None:
        self.connector = connector
        self._db = sqlite_db
        self.asset_repo = asset_repo
        self.investment_repo = investment_repo

    def _domain_repo(self, domain: str):
        if domain == "asset":
            return self.asset_repo
        return self.investment_repo

    def _to_domain_obj(self, holding: ConnectorHolding):
        if holding.domain == "asset":
            return Asset(holding.name, holding.category, holding.value)
        return Investment(holding.name, holding.category, holding.value)

    def _load_existing_mappings(self) -> Dict[str, Tuple[str, str]]:
        """Return mapping external_id -> (domain, domain_id) for this connector."""
        mappings: Dict[str, Tuple[str, str]] = {}
        with self._db.connect() as conn:
            cur = conn.execute(
                "SELECT external_id, domain, domain_id FROM connector_mappings WHERE connector_name = ?",
                (self.connector.name(),),
            )
            for row in cur.fetchall():
                mappings[row["external_id"]] = (row["domain"], row["domain_id"])
        return mappings

    def _upsert_mapping(self, external_id: str, domain: str, domain_id: str) -> None:
        now = datetime.now().isoformat()
        with self._db.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO connector_mappings (connector_name, external_id, domain, domain_id, last_synced_at) VALUES (?, ?, ?, ?, ?)",
                (self.connector.name(), external_id, domain, domain_id, now),
            )

    def _delete_mapping(self, external_id: str) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "DELETE FROM connector_mappings WHERE connector_name = ? AND external_id = ?",
                (self.connector.name(), external_id),
            )

    def sync(self) -> SyncResult:
        timestamp = datetime.now().isoformat()
        try:
            holdings = self.connector.fetch_holdings()
        except Exception as exc:
            # If connector provides a received count attach it to the result when possible
            received = 0
            if hasattr(exc, "received"):
                try:
                    received = int(getattr(exc, "received"))
                except Exception:
                    received = 0

            return SyncResult(
                connector=self.connector.name(),
                status="failed",
                received=received,
                added=0,
                updated=0,
                removed=0,
                unchanged=0,
                timestamp=timestamp,
                errors=[str(exc)],
            )

        # Validation
        errors: List[str] = []
        for h in holdings:
            if not h.external_id:
                errors.append("Missing external_id in holding")
            if h.value is None:
                errors.append(f"Missing value for external_id={h.external_id}")
        if errors:
            return SyncResult(
                connector=self.connector.name(),
                status="failed",
                received=len(holdings),
                added=0,
                updated=0,
                removed=0,
                unchanged=0,
                timestamp=timestamp,
                errors=errors,
            )

        incoming_by_id: Dict[str, ConnectorHolding] = {h.external_id: h for h in holdings}
        existing_mappings = self._load_existing_mappings()

        added = 0
        updated = 0
        unchanged = 0

        # Process incoming
        for external_id, holding in incoming_by_id.items():
            if external_id in existing_mappings:
                domain, domain_id = existing_mappings[external_id]
                repo = self._domain_repo(domain)
                domain_obj = self._to_domain_obj(holding)
                try:
                    repo.update(domain_id, domain_obj)
                    updated += 1
                except KeyError:
                    # mapped domain id missing — create new and update mapping
                    new_id = repo.add(domain_obj)
                    self._upsert_mapping(external_id, domain, new_id)
                    added += 1
            else:
                # new mapping — create domain record and mapping
                domain = holding.domain or "investment"
                repo = self._domain_repo(domain)
                domain_obj = self._to_domain_obj(holding)
                new_id = repo.add(domain_obj)
                self._upsert_mapping(external_id, domain, new_id)
                added += 1

        # Handle removals: any existing mapping not present in incoming should be removed (connector owns these records)
        removed = 0
        for external_id in list(existing_mappings.keys()):
            if external_id not in incoming_by_id:
                domain, domain_id = existing_mappings[external_id]
                repo = self._domain_repo(domain)
                try:
                    repo.delete(domain_id)
                except KeyError:
                    # already gone
                    pass
                self._delete_mapping(external_id)
                removed += 1

        # Unchanged is (received - added - updated)
        unchanged = len(holdings) - added - updated

        return SyncResult(
            connector=self.connector.name(),
            status="success",
            received=len(holdings),
            added=added,
            updated=updated,
            removed=removed,
            unchanged=unchanged,
            timestamp=timestamp,
            errors=None,
        )

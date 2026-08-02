import json
from pathlib import Path

from src.connectors.local_snapshot import LocalSnapshotConnector
from src.services.portfolio_sync_service import PortfolioSyncService
from src.repositories.sqlite_factory import create_sqlite_repositories
from src.models.investment import Investment


def test_mid_sync_failure_rolls_back(tmp_path):
    db_file = tmp_path / "lakshmi_tx.db"
    db_path = str(db_file)

    # initial snapshot with two holdings A and B
    snapshot = tmp_path / "snapshot_tx.json"
    snapshot.write_text(json.dumps([
        {"external_id": "A", "name": "Asset A", "category": "Equity", "value": 100.0, "domain": "investment"},
        {"external_id": "B", "name": "Asset B", "category": "Mutual Fund", "value": 200.0, "domain": "investment"},
    ]))

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)

    # First sync: add A and B
    res1 = service.sync()
    assert res1.status == "success"
    assert res1.added == 2

    # Add a manual investment (not connector-managed)
    manual = Investment("Manual Inv", "Equity", 10000.0)
    manual_id = investment_repo.add(manual)

    # Capture pre-sync state for later comparison
    with investment_repo._db.connect() as conn:
        cur = conn.execute("SELECT id, name, value FROM investments ORDER BY name")
        pre_rows = cur.fetchall()
        # get mapping for A and B
        cur2 = conn.execute("SELECT external_id, domain_id FROM connector_mappings WHERE connector_name = ?", (connector.name(),))
        mappings = {r["external_id"]: r["domain_id"] for r in cur2.fetchall()}

    a_id = mappings["A"]
    b_id = mappings["B"]

    # Prepare new snapshot: update A, create NEW, and remove B
    snapshot.write_text(json.dumps([
        {"external_id": "A", "name": "Asset A", "category": "Equity", "value": 150.0, "domain": "investment"},
        {"external_id": "NEW", "name": "New Asset", "category": "Equity", "value": 300.0, "domain": "investment"},
    ]))

    # Inject failure: make delete raise for B
    original_delete = investment_repo.delete

    def failing_delete(item_id: str, conn=None):
        if item_id == b_id:
            raise Exception("simulated failure during delete")
        return original_delete(item_id, conn=conn)

    investment_repo.delete = failing_delete

    # Run sync which should fail and rollback
    res2 = service.sync()
    assert res2.status == "failed"

    # Verify DB state unchanged compared to pre-sync
    with investment_repo._db.connect() as conn:
        cur = conn.execute("SELECT id, name, value FROM investments ORDER BY name")
        post_rows = cur.fetchall()
        assert pre_rows == post_rows

        # verify mappings unchanged
        cur2 = conn.execute("SELECT external_id, domain_id FROM connector_mappings WHERE connector_name = ?", (connector.name(),))
        post_mappings = {r["external_id"]: r["domain_id"] for r in cur2.fetchall()}
        assert mappings == post_mappings

    # verify manual record still exists
    all_invs = investment_repo.get_all()
    assert any(i.name == "Manual Inv" for i in all_invs)


def test_successful_atomic_sync(tmp_path):
    db_file = tmp_path / "lakshmi_tx2.db"
    db_path = str(db_file)

    snapshot = tmp_path / "snapshot_tx2.json"
    snapshot.write_text(json.dumps([
        {"external_id": "P1", "name": "Prod A", "category": "Equity", "value": 500.0, "domain": "investment"}
    ]))

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)

    res = service.sync()
    assert res.status == "success"
    assert res.added == 1

    # ensure mapping exists
    with investment_repo._db.connect() as conn:
        cur = conn.execute("SELECT COUNT(1) as c FROM connector_mappings WHERE connector_name = ?", (connector.name(),))
        assert cur.fetchone()["c"] == 1

import os
from tempfile import NamedTemporaryFile
from pathlib import Path

from src.connectors.local_snapshot import LocalSnapshotConnector
from src.services.portfolio_sync_service import PortfolioSyncService, SyncResult
from src.repositories.sqlite_factory import create_sqlite_repositories
from src.models.investment import Investment
from src.models.asset import Asset


def test_local_connector_sync_idempotent(tmp_path):
    db_file = tmp_path / "lakshmi_sync_test.db"
    db_path = str(db_file)

    # prepare a sample snapshot file
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text('[{"external_id":"TST-1","name":"Test Inv","category":"Equity","value":1000.0,"domain":"investment"}]')

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)

    # create sync service
    # asset_repo not used in this test but required by constructor
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)

    # first sync
    result1 = service.sync()
    assert result1.status == "success"
    assert result1.received == 1
    assert result1.added == 1
    assert result1.updated in (0,1)

    # second sync (idempotency)
    result2 = service.sync()
    assert result2.status == "success"
    assert result2.added == 0
    assert result2.updated in (0,1)


def test_local_connector_sync_update_and_removal(tmp_path):
    db_file = tmp_path / "lakshmi_sync_test2.db"
    db_path = str(db_file)

    # initial snapshot with two holdings
    snapshot = tmp_path / "snapshot2.json"
    snapshot.write_text('['
                        '{"external_id":"A","name":"Asset A","category":"Equity","value":100.0,"domain":"investment"},'
                        '{"external_id":"B","name":"Asset B","category":"Mutual Fund","value":200.0,"domain":"investment"}'
                        ']')

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)

    res1 = service.sync()
    assert res1.status == "success"
    assert res1.added == 2

    # update snapshot: change A value and remove B
    snapshot.write_text('[{"external_id":"A","name":"Asset A","category":"Equity","value":150.0,"domain":"investment"}]')
    res2 = service.sync()
    assert res2.status == "success"
    # one was updated, one removed
    assert res2.updated >= 1
    assert res2.removed >= 1


def test_manual_record_preservation(tmp_path):
    db_file = tmp_path / "lakshmi_sync_test3.db"
    db_path = str(db_file)

    # connector snapshot contains only connector-managed holding C
    snapshot = tmp_path / "snapshot3.json"
    snapshot.write_text('[{"external_id":"C","name":"Connector Holding","category":"Equity","value":500.0,"domain":"investment"}]')

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)

    # Add a manual investment directly to the repository (simulate user-added record)
    manual = Investment("Manual Inv","Equity", 10000.0)
    manual_id = investment_repo.add(manual)

    res1 = service.sync()
    assert res1.added == 1

    # Now connector snapshot omits the manual record (as expected). After sync, manual record must still exist.
    all_investments = investment_repo.get_all()
    # find manual by name
    assert any(i.name == "Manual Inv" for i in all_investments)


def test_sync_persists_across_restart(tmp_path):
    db_file = tmp_path / "lakshmi_sync_test4.db"
    db_path = str(db_file)

    snapshot = tmp_path / "snapshot4.json"
    snapshot.write_text('[{"external_id":"X1","name":"Persisted Inv","category":"Equity","value":700.0,"domain":"investment"}]')

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)
    res = service.sync()
    assert res.added == 1

    # recreate repositories pointing to same DB and verify persisted
    asset_repo2, liability_repo2, investment_repo2, goal_repo2, profile_repo2 = create_sqlite_repositories(db_path)
    investments = investment_repo2.get_all()
    assert any(inv.name == "Persisted Inv" for inv in investments)


def test_invalid_snapshot_fails_safely(tmp_path):
    db_file = tmp_path / "lakshmi_sync_test5.db"
    db_path = str(db_file)

    snapshot = tmp_path / "bad.json"
    snapshot.write_text('[{"external_id":"","name":"Bad","category":"Equity","value":null}]')

    connector = LocalSnapshotConnector(snapshot)
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)

    res = service.sync()
    assert res.status == "failed"
    assert res.received == 1
    # ensure no repository entries were created
    assert investment_repo.count() == 0
